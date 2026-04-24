"""
Stream processor: Kafka → InfluxDB + PostgreSQL.

Consumes from all sensors.* topics.  For each reading:
  1. Writes the time-series point to InfluxDB  (immediately — visible in
     dashboards in real time).
  2. Upserts the sensor's device registration in PostgreSQL  (time-gated
     cache so only ~16 SQL calls/min instead of 32/sec).

Kafka offsets are committed in batches of COMMIT_EVERY messages rather
than after every single message.  InfluxDB and PostgreSQL writes still
happen per message — batching only reduces Kafka broker round-trips.
If the processor crashes mid-batch the worst case is replaying the last
COMMIT_EVERY messages; InfluxDB upserts are idempotent so no duplicates.
"""
import signal
import sys
import time

from confluent_kafka import Consumer, KafkaError, KafkaException

sys.path.insert(0, "/app")

from shared.logging_config import get_logger
from shared.models import SensorReading
from processor.config import config
from processor.writers.influx_writer import InfluxWriter
from processor.writers.postgres_writer import PostgresWriter

logger = get_logger("processor.main", config.log_level)

SENSOR_TOPICS = [
    "sensors.temperature",
    "sensors.humidity",
    "sensors.pressure",
    "sensors.vibration",
    "sensors.occupancy",
]

# Commit Kafka offset every N successfully processed messages.
# InfluxDB/Postgres writes still happen on every message.
COMMIT_EVERY = 100


def _build_consumer() -> Consumer:
    return Consumer({
        "bootstrap.servers":  config.kafka_bootstrap_servers,
        "group.id":           config.kafka_group_id,
        "auto.offset.reset":  config.kafka_auto_offset_reset,
        "enable.auto.commit": False,
    })


def main() -> None:
    logger.info("Starting stream processor")

    influx   = InfluxWriter()
    postgres = PostgresWriter()
    postgres.connect()

    consumer = _build_consumer()
    consumer.subscribe(SENSOR_TOPICS)

    stop = False

    def _handle_signal(sig, frame):
        nonlocal stop
        logger.info("Shutdown signal received")
        stop = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT,  _handle_signal)

    processed = 0
    errors    = 0
    uncommitted = 0

    while not stop:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            logger.error(f"Kafka consumer error: {msg.error()}")
            errors += 1
            continue

        try:
            reading = SensorReading.from_json(msg.value().decode("utf-8"))

            # ── Write to stores immediately (real-time visibility) ──────
            influx.write(reading)
            postgres.upsert_sensor(reading)

            processed   += 1
            uncommitted += 1

            # ── Commit Kafka offset in batches ──────────────────────────
            if uncommitted >= COMMIT_EVERY:
                consumer.commit(asynchronous=True)
                uncommitted = 0

            if processed % 1000 == 0:
                logger.info(
                    "Processor heartbeat",
                    extra={"processed": processed, "errors": errors},
                )

        except Exception as exc:
            errors += 1
            logger.error(
                f"Processing error: {exc}",
                extra={"topic": msg.topic(), "offset": msg.offset()},
            )

    # Flush final uncommitted offset before exit
    if uncommitted > 0:
        consumer.commit(asynchronous=False)

    consumer.close()
    influx.close()
    postgres.close()
    logger.info("Processor stopped", extra={"processed": processed, "errors": errors})


if __name__ == "__main__":
    main()
