"""
Writes SensorReading objects to InfluxDB 2.x using the line protocol.

One measurement per sensor type. Tags carry location metadata; value is
the only field. Writes are batched for throughput with explicit retry and
an error callback so failures are never silently dropped.
"""
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions, WriteType

import sys
sys.path.insert(0, "/app")

from shared.models import SensorReading
from shared.logging_config import get_logger
from processor.config import config

logger = get_logger("processor.influx_writer", config.log_level)

# Flush every 200 points or 1 second, whichever comes first.
# Retry up to 5 times with exponential back-off before giving up.
_WRITE_OPTIONS = WriteOptions(
    write_type=WriteType.batching,
    batch_size=200,
    flush_interval=1_000,       # ms
    retry_interval=2_000,       # ms between first and second attempt
    max_retries=5,
    max_retry_delay=30_000,     # ms cap on back-off
    max_close_wait=10_000,      # ms to wait for in-flight writes on close
)


class InfluxWriter:
    def __init__(self) -> None:
        self._client = InfluxDBClient(
            url=config.influxdb_url,
            token=config.influxdb_token,
            org=config.influxdb_org,
        )
        self._failed_batches = 0
        self._write_api = self._client.write_api(
            write_options=_WRITE_OPTIONS,
            error_callback=self._on_write_error,
        )
        logger.info("InfluxDB writer initialised", extra={"url": config.influxdb_url})

    # ------------------------------------------------------------------

    def write(self, reading: SensorReading) -> None:
        point = (
            Point(reading.influx_measurement)
            .tag("building_id", reading.building_id)
            .tag("floor",       str(reading.floor))
            .tag("room_id",     reading.room_id)
            .tag("sensor_id",   reading.sensor_id)
            .tag("unit",        reading.unit)
            .field("value",     reading.value)
            .field("quality",   reading.quality)
            .time(reading.timestamp_ms, WritePrecision.MS)
        )
        self._write_api.write(
            bucket=config.influxdb_bucket,
            org=config.influxdb_org,
            record=point,
        )

    def close(self) -> None:
        self._write_api.close()   # flushes remaining buffer before closing
        self._client.close()
        logger.info(
            "InfluxDB writer closed",
            extra={"total_failed_batches": self._failed_batches},
        )

    # ------------------------------------------------------------------

    def _on_write_error(self, conf, data, exception) -> None:
        """
        Called by the influxdb-client background thread after all retries
        are exhausted. At this point the batch is permanently lost from
        InfluxDB's perspective — log it as CRITICAL so it is visible in
        any log aggregation system and can be replayed from the Kafka DLQ.
        """
        self._failed_batches += 1
        logger.error(
            "InfluxDB batch permanently failed after retries — data loss occurred",
            extra={
                "error":                str(exception),
                "total_failed_batches": self._failed_batches,
                "hint":                 "Replay from Kafka topic offset to recover",
            },
        )
