"""
MQTT → Kafka bridge.

Subscribes to campus/# on the MQTT broker and forwards every message to the
matching Kafka topic (sensors.<sensor_type>).  Uses QoS-1 on MQTT and
synchronous acks on Kafka to avoid silent message loss.

Schema validation (Fix 9): every inbound payload is validated against the
SensorReading schema using pydantic before being forwarded.  Malformed
messages are logged and dropped rather than poisoning Kafka topics.
"""
import signal
import sys
import time

import paho.mqtt.client as mqtt
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from pydantic import BaseModel, ValidationError, field_validator

sys.path.insert(0, "/app")

from shared.logging_config import get_logger
from shared.models import SensorReading, KAFKA_TOPICS
from ingestion.config import config

logger = get_logger("ingestion.bridge", config.log_level)

_RECONNECT_DELAY_MAX = 30

# ── Pydantic schema (Fix 9) ────────────────────────────────────────────────────

_VALID_SENSOR_TYPES = {
    "temperature", "humidity", "pressure", "vibration", "occupancy"
}


class _SensorPayload(BaseModel):
    """Lightweight schema guard at the bridge entry point."""
    sensor_id:   str
    building_id: str
    floor:       int
    room_id:     str
    sensor_type: str
    value:       float
    unit:        str
    timestamp_ms: int
    quality:     float = 1.0

    @field_validator("sensor_type")
    @classmethod
    def _check_sensor_type(cls, v: str) -> str:
        if v not in _VALID_SENSOR_TYPES:
            raise ValueError(f"unknown sensor_type: {v!r}")
        return v

    @field_validator("quality")
    @classmethod
    def _check_quality(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"quality {v} out of range [0, 1]")
        return v


# ──────────────────────────────────────────────────────────────────────────────

def _ensure_topics(bootstrap_servers: str) -> None:
    admin = AdminClient({"bootstrap.servers": bootstrap_servers})
    existing = set(admin.list_topics(timeout=10).topics.keys())
    new_topics = [
        NewTopic(t, num_partitions=3, replication_factor=1)
        for t in KAFKA_TOPICS
        if t not in existing
    ]
    if new_topics:
        futures = admin.create_topics(new_topics)
        for topic, future in futures.items():
            try:
                future.result()
                logger.info(f"Created Kafka topic: {topic}")
            except Exception as exc:
                if "already exists" not in str(exc):
                    logger.warning(f"Topic creation warning ({topic}): {exc}")


def _delivery_report(err, msg) -> None:
    if err:
        logger.error(
            "Kafka delivery failed",
            extra={"topic": msg.topic(), "error": str(err)},
        )


class MQTTKafkaBridge:
    def __init__(self) -> None:
        self._producer = Producer({
            "bootstrap.servers": config.kafka_bootstrap_servers,
            "acks": config.kafka_acks,
            "compression.type": "lz4",
            "linger.ms": 5,
        })
        self._mqtt = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="campus-bridge",
        )
        if config.mqtt_username:
            self._mqtt.username_pw_set(config.mqtt_username, config.mqtt_password)

        self._mqtt.on_connect    = self._on_connect
        self._mqtt.on_message    = self._on_message
        self._mqtt.on_disconnect = self._on_disconnect
        self._connected = False
        self._stop      = False
        self._invalid   = 0

    # ------------------------------------------------------------------

    def start(self) -> None:
        _ensure_topics(config.kafka_bootstrap_servers)
        self._mqtt.loop_start()
        self._mqtt_connect()
        logger.info("Bridge running — waiting for messages")

        while not self._stop:
            self._producer.poll(0)
            time.sleep(0.1)

        self._mqtt.loop_stop()
        self._mqtt.disconnect()
        self._producer.flush(timeout=10)
        logger.info("Bridge stopped", extra={"invalid_dropped": self._invalid})

    def stop(self) -> None:
        self._stop = True

    # ------------------------------------------------------------------

    def _mqtt_connect(self) -> None:
        delay = 1
        while True:
            try:
                self._mqtt.connect(config.mqtt_host, config.mqtt_port, config.mqtt_keepalive)
                deadline = time.time() + 5
                while not self._connected and time.time() < deadline:
                    time.sleep(0.1)
                if self._connected:
                    return
            except Exception as exc:
                logger.warning(f"MQTT connect failed ({exc}), retrying in {delay}s")
            time.sleep(delay)
            delay = min(delay * 2, _RECONNECT_DELAY_MAX)

    def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        if reason_code == 0:
            self._connected = True
            client.subscribe(config.mqtt_subscribe_topic, qos=1)
            logger.info("MQTT connected and subscribed",
                        extra={"topic": config.mqtt_subscribe_topic})
        else:
            logger.error(f"MQTT connect refused rc={reason_code}")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties) -> None:
        self._connected = False
        logger.warning("MQTT disconnected", extra={"reason_code": reason_code})

    def _on_message(self, client, userdata, msg: mqtt.MQTTMessage) -> None:
        raw = msg.payload.decode("utf-8")

        # ── Schema validation (Fix 9) ───────────────────────────────────
        try:
            import json
            _SensorPayload.model_validate(json.loads(raw))
        except (ValidationError, Exception) as exc:
            self._invalid += 1
            logger.warning(
                "Invalid payload dropped — schema validation failed",
                extra={"topic": msg.topic, "error": str(exc)},
            )
            return
        # ───────────────────────────────────────────────────────────────

        try:
            reading = SensorReading.from_json(raw)
            self._producer.produce(
                topic    = reading.kafka_topic,
                key      = reading.sensor_id.encode(),
                value    = reading.to_json().encode(),
                callback = _delivery_report,
            )
        except Exception as exc:
            logger.error(
                "Failed to forward MQTT message",
                extra={"topic": msg.topic, "error": str(exc)},
            )


def main() -> None:
    logger.info("Starting MQTT-Kafka bridge")
    bridge = MQTTKafkaBridge()

    def _handle_signal(sig, frame):
        logger.info("Shutdown signal received")
        bridge.stop()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT,  _handle_signal)

    bridge.start()


if __name__ == "__main__":
    main()
