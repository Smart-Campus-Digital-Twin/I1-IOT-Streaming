"""
Populates sensor_hourly_stats in PostgreSQL from InfluxDB data.

Runs once per hour from the processor main loop.  For each sensor it queries
the last hour of readings from InfluxDB, computes avg/min/max/stddev/count in
Python, and upserts a single row into sensor_hourly_stats.

Uses its own InfluxDB query client and PostgreSQL connection so it does not
interfere with the write paths in InfluxWriter or PostgresWriter.
"""
import math
import time
from datetime import datetime, timezone
from typing import Optional

import psycopg2
from influxdb_client import InfluxDBClient
from psycopg2.extensions import connection as PgConnection

import sys
sys.path.insert(0, "/app")

from shared.logging_config import get_logger
from processor.config import config

logger = get_logger("processor.hourly_aggregator", config.log_level)

_FLUX = """
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._field == "value")
  |> group(columns: ["_measurement", "sensor_id", "building_id", "floor", "room_id"])
"""

_UPSERT_STATS = """
INSERT INTO sensor_hourly_stats
  (sensor_id, building_id, floor, room_id, sensor_type, hour_bucket,
   avg_value, min_value, max_value, stddev_value, sample_count)
VALUES
  (%(sensor_id)s, %(building_id)s, %(floor)s, %(room_id)s, %(sensor_type)s,
   %(hour_bucket)s, %(avg_value)s, %(min_value)s, %(max_value)s,
   %(stddev_value)s, %(sample_count)s)
ON CONFLICT (sensor_id, hour_bucket) DO UPDATE
  SET avg_value    = EXCLUDED.avg_value,
      min_value    = EXCLUDED.min_value,
      max_value    = EXCLUDED.max_value,
      stddev_value = EXCLUDED.stddev_value,
      sample_count = EXCLUDED.sample_count;
"""


def _pg_connect(retries: int = 5, delay: float = 3.0) -> PgConnection:
    dsn = dict(
        host=config.postgres_host,
        port=config.postgres_port,
        dbname=config.postgres_db,
        user=config.postgres_user,
        password=config.postgres_password,
    )
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(**dsn)
            conn.autocommit = True
            return conn
        except psycopg2.OperationalError as exc:
            logger.warning(f"Aggregator: PG connect attempt {attempt}/{retries}: {exc}")
            if attempt < retries:
                time.sleep(delay)
    raise RuntimeError("Aggregator: exhausted PostgreSQL connection retries")


class HourlyAggregator:
    """
    Call run() once per hour.  Queries InfluxDB for the past hour of readings,
    computes per-sensor statistics, and upserts them into sensor_hourly_stats.
    """

    def __init__(self) -> None:
        self._influx = InfluxDBClient(
            url=config.influxdb_url,
            token=config.influxdb_token,
            org=config.influxdb_org,
        )
        self._query_api = self._influx.query_api()
        self._pg: Optional[PgConnection] = None

    def connect(self) -> None:
        self._pg = _pg_connect()

    def run(self) -> int:
        """Query InfluxDB and upsert stats. Returns number of rows written."""
        now = datetime.now(timezone.utc)
        hour_bucket = now.replace(minute=0, second=0, microsecond=0)

        flux = _FLUX.format(bucket=config.influxdb_bucket)
        try:
            tables = self._query_api.query(flux)
        except Exception as exc:
            logger.error(f"Aggregator: InfluxDB query failed: {exc}")
            return 0

        rows_written = 0
        for table in tables:
            records = table.records
            if not records:
                continue

            meta = records[0].values
            sensor_id   = meta.get("sensor_id",   "")
            building_id = meta.get("building_id", "")
            room_id     = meta.get("room_id",     "")
            sensor_type = meta.get("_measurement", "")
            floor_val   = meta.get("floor",        0)

            try:
                floor_int = int(floor_val)
            except (TypeError, ValueError):
                floor_int = 0

            values = [r.get_value() for r in records if r.get_value() is not None]
            if not values:
                continue

            n     = len(values)
            mean  = sum(values) / n
            mn    = min(values)
            mx    = max(values)
            # Sample standard deviation (0 when n == 1)
            if n > 1:
                variance = sum((v - mean) ** 2 for v in values) / (n - 1)
                stddev   = math.sqrt(variance)
            else:
                stddev = 0.0

            row = dict(
                sensor_id    = sensor_id,
                building_id  = building_id,
                floor        = floor_int,
                room_id      = room_id,
                sensor_type  = sensor_type,
                hour_bucket  = hour_bucket,
                avg_value    = round(mean,   4),
                min_value    = round(mn,     4),
                max_value    = round(mx,     4),
                stddev_value = round(stddev, 4),
                sample_count = n,
            )

            try:
                if self._pg is None or self._pg.closed:
                    self.connect()
                with self._pg.cursor() as cur:
                    cur.execute(_UPSERT_STATS, row)
                rows_written += 1
            except Exception as exc:
                logger.error(f"Aggregator: PG upsert failed for {sensor_id}: {exc}")

        logger.info("Hourly aggregation complete", extra={
            "hour_bucket": hour_bucket.isoformat(),
            "rows_written": rows_written,
        })
        return rows_written

    def close(self) -> None:
        self._influx.close()
        if self._pg and not self._pg.closed:
            self._pg.close()
        logger.info("HourlyAggregator closed")
