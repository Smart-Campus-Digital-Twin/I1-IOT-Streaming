"""
Writes device-registry upserts and alert events to PostgreSQL.

Sensor upserts are time-gated: each sensor_id is only re-upserted every
UPSERT_INTERVAL seconds. This cuts PostgreSQL load from ~32 writes/sec
(one per reading) down to ~16 writes/min (one per sensor per 10 min).
"""
import time
from typing import Dict, Optional

import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection as PgConnection

import sys
sys.path.insert(0, "/app")

from shared.models import SensorReading, AlertEvent
from shared.logging_config import get_logger
from processor.config import config

logger = get_logger("processor.postgres_writer", config.log_level)

_UPSERT_SENSOR = """
INSERT INTO sensors (sensor_id, room_id, building_id, floor, sensor_type, unit, last_seen_at)
VALUES (%(sensor_id)s, %(room_id)s, %(building_id)s, %(floor)s, %(sensor_type)s, %(unit)s, NOW())
ON CONFLICT (sensor_id) DO UPDATE
  SET last_seen_at = NOW(),
      is_active    = TRUE;
"""

_INSERT_ALERT = """
INSERT INTO alert_events
  (alert_id, sensor_id, building_id, floor, room_id, sensor_type,
   alert_type, severity, value, threshold, message, timestamp_ms)
VALUES
  (%(alert_id)s, %(sensor_id)s, %(building_id)s, %(floor)s, %(room_id)s,
   %(sensor_type)s, %(alert_type)s, %(severity)s, %(value)s, %(threshold)s,
   %(message)s, %(timestamp_ms)s)
ON CONFLICT (alert_id) DO NOTHING;
"""

# Re-upsert each sensor at most once per this many seconds.
# Keeps last_seen_at reasonably fresh without hammering Postgres.
_UPSERT_INTERVAL: float = 600.0   # 10 minutes


def _connect(retries: int = 10, delay: float = 3.0) -> PgConnection:
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
            logger.info("PostgreSQL connected")
            return conn
        except psycopg2.OperationalError as exc:
            logger.warning(f"PostgreSQL connect attempt {attempt}/{retries} failed: {exc}")
            if attempt < retries:
                time.sleep(delay)
    raise RuntimeError("PostgreSQL: exhausted connection retries")


class PostgresWriter:
    def __init__(self) -> None:
        self._conn: Optional[PgConnection] = None
        # sensor_id -> monotonic time of last successful upsert
        self._last_upserted: Dict[str, float] = {}

    def connect(self) -> None:
        self._conn = _connect()

    def upsert_sensor(self, reading: SensorReading) -> None:
        now = time.monotonic()
        # Default to -_UPSERT_INTERVAL so the very first message always upserts
        last = self._last_upserted.get(reading.sensor_id, -_UPSERT_INTERVAL)
        if now - last < _UPSERT_INTERVAL:
            return   # still fresh — skip the SQL round-trip
        self._execute(_UPSERT_SENSOR, reading.to_dict())
        self._last_upserted[reading.sensor_id] = now

    def insert_alert(self, alert: AlertEvent) -> None:
        self._execute(_INSERT_ALERT, alert.to_dict())

    def _execute(self, sql: str, params: dict) -> None:
        try:
            with self._conn.cursor() as cur:
                cur.execute(sql, params)
        except psycopg2.InterfaceError:
            logger.warning("PostgreSQL connection lost — reconnecting")
            self.connect()
            with self._conn.cursor() as cur:
                cur.execute(sql, params)
        except Exception as exc:
            logger.error(f"PostgreSQL write error: {exc}", extra={"sql": sql[:80]})

    def close(self) -> None:
        if self._conn and not self._conn.closed:
            self._conn.close()
        logger.info("PostgreSQL writer closed")
