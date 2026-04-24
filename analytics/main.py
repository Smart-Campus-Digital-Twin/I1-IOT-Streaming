"""
Real-time analytics engine.

Consumes all sensors.* Kafka topics and applies:
  1. Z-score anomaly detection  (per-sensor sliding window, Redis-backed)
  2. Rule-based threshold checks

Detected events are deduplicated by AlertSuppressor (5-min cooldown per
sensor+alert_type) before being published to:
  - alerts.anomaly   — statistical outliers
  - alerts.threshold — rule violations
"""
import signal
import sys
import uuid

from confluent_kafka import Consumer, KafkaError, Producer

sys.path.insert(0, "/app")

from shared.logging_config import get_logger
from shared.models import SensorReading, AlertEvent
from analytics.config import config
from analytics.detectors.anomaly import ZScoreDetector
from analytics.detectors.threshold import ThresholdDetector
from analytics.suppressors.alert_suppressor import AlertSuppressor
from analytics.writers.alert_writer import AlertWriter

logger = get_logger("analytics.main", config.log_level)

SENSOR_TOPICS = [
    "sensors.temperature",
    "sensors.humidity",
    "sensors.pressure",
    "sensors.vibration",
    "sensors.occupancy",
]


def _build_consumer() -> Consumer:
    return Consumer({
        "bootstrap.servers":  config.kafka_bootstrap_servers,
        "group.id":           config.kafka_group_id,
        "auto.offset.reset":  config.kafka_auto_offset_reset,
        "enable.auto.commit": True,
        "auto.commit.interval.ms": 5000,
    })


def _build_producer() -> Producer:
    return Producer({
        "bootstrap.servers": config.kafka_bootstrap_servers,
        "acks": "1",
        "linger.ms": 10,
    })


def _make_alert(reading: SensorReading, alert_type: str, severity: str,
                threshold_val: float, message: str) -> AlertEvent:
    return AlertEvent(
        alert_id     = str(uuid.uuid4()),
        sensor_id    = reading.sensor_id,
        building_id  = reading.building_id,
        floor        = reading.floor,
        room_id      = reading.room_id,
        sensor_type  = reading.sensor_type,
        alert_type   = alert_type,
        severity     = severity,
        value        = reading.value,
        threshold    = threshold_val,
        message      = message,
        timestamp_ms = reading.timestamp_ms,
    )


def main() -> None:
    logger.info("Starting analytics engine", extra={"z_threshold": config.z_score_threshold})

    consumer     = _build_consumer()
    producer     = _build_producer()
    threshold    = ThresholdDetector()
    suppressor   = AlertSuppressor(cooldown_s=config.alert_cooldown_s)
    alert_writer = AlertWriter()
    alert_writer.connect()

    # ZScoreDetector wired to Redis if available
    try:
        import redis as redis_lib
        r = redis_lib.Redis(
            host=config.redis_host,
            port=config.redis_port,
            password=config.redis_password or None,
            db=0,
            socket_connect_timeout=3,
        )
        r.ping()
        anomaly = ZScoreDetector(z_threshold=config.z_score_threshold, redis_client=r)
        logger.info("Redis connected — window state will be checkpointed",
                    extra={"host": config.redis_host})
    except Exception as exc:
        anomaly = ZScoreDetector(z_threshold=config.z_score_threshold)
        logger.warning(f"Redis unavailable ({exc}) — window state is in-memory only")

    consumer.subscribe(SENSOR_TOPICS)

    stop = False

    def _handle_signal(sig, frame):
        nonlocal stop
        logger.info("Shutdown signal received")
        stop = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT,  _handle_signal)

    processed = anomalies = breaches = 0

    while not stop:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                logger.error(f"Kafka error: {msg.error()}")
            continue

        try:
            reading   = SensorReading.from_json(msg.value().decode("utf-8"))
            processed += 1

            # ── Z-score anomaly detection ───────────────────────────────
            z_score, is_anomaly = anomaly.detect(reading)
            if is_anomaly and not suppressor.is_suppressed(reading.sensor_id, "anomaly"):
                anomalies += 1
                alert = _make_alert(
                    reading,
                    alert_type    = "anomaly",
                    severity      = "warning",
                    threshold_val = z_score,
                    message       = (
                        f"Anomaly: {reading.sensor_type}={reading.value:.2f} "
                        f"(Z={z_score:.2f}) on {reading.sensor_id}"
                    ),
                )
                producer.produce(
                    "alerts.anomaly",
                    key=reading.sensor_id.encode(),
                    value=alert.to_json().encode(),
                )
                alert_writer.insert_alert(alert)
                logger.warning("Anomaly detected", extra={
                    "sensor_id":   reading.sensor_id,
                    "sensor_type": reading.sensor_type,
                    "value":       reading.value,
                    "z_score":     z_score,
                })

            # ── Threshold check ─────────────────────────────────────────
            breach = threshold.check(reading)
            if breach and not suppressor.is_suppressed(reading.sensor_id, "threshold_breach"):
                breaches += 1
                alert = _make_alert(
                    reading,
                    alert_type    = "threshold_breach",
                    severity      = breach.severity,
                    threshold_val = breach.limit,
                    message       = breach.message,
                )
                producer.produce(
                    "alerts.threshold",
                    key=reading.sensor_id.encode(),
                    value=alert.to_json().encode(),
                )
                alert_writer.insert_alert(alert)
                logger.warning("Threshold breach", extra={
                    "sensor_id":   reading.sensor_id,
                    "sensor_type": reading.sensor_type,
                    "value":       reading.value,
                    "limit":       breach.limit,
                    "direction":   breach.direction,
                    "severity":    breach.severity,
                })

            if processed % 5000 == 0:
                producer.flush(timeout=5)
                logger.info("Analytics heartbeat", extra={
                    "processed":  processed,
                    "anomalies":  anomalies,
                    "breaches":   breaches,
                    **suppressor.stats(),
                })

        except Exception as exc:
            logger.error(f"Analytics processing error: {exc}",
                         extra={"topic": msg.topic()})

    consumer.close()
    producer.flush(timeout=10)
    alert_writer.close()
    logger.info("Analytics engine stopped", extra={"processed": processed})


if __name__ == "__main__":
    main()
