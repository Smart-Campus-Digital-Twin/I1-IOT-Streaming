"""
Persists AlertEvent rows to the alert_events PostgreSQL table.

Kept deliberately minimal — one method, one SQL statement.
Reconnects automatically if the connection drops between alerts.
"""
import time
from typing import Optional

import psycopg2
from psycopg2.extensions import connection as PgConnection

import sys
sys.path.insert(0, "/app")

from shared.models import AlertEvent
from shared.logging_config import get_logger
from analytics.config import config

logger = get_logger("analytics.alert_writer", config.log_level)

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
            logger.info("AlertWriter: PostgreSQL connected")
            return conn
        except psycopg2.OperationalError as exc:
            logger.warning(f"AlertWriter: connect attempt {attempt}/{retries} failed: {exc}")
            if attempt < retries:
                time.sleep(delay)
    raise RuntimeError("AlertWriter: exhausted PostgreSQL connection retries")


class AlertWriter:
    def __init__(self) -> None:
        self._conn: Optional[PgConnection] = None

    def connect(self) -> None:
        self._conn = _connect()

    def insert_alert(self, alert: AlertEvent) -> None:
        try:
            with self._conn.cursor() as cur:
                cur.execute(_INSERT_ALERT, alert.to_dict())
        except psycopg2.InterfaceError:
            logger.warning("AlertWriter: connection lost — reconnecting")
            self.connect()
            with self._conn.cursor() as cur:
                cur.execute(_INSERT_ALERT, alert.to_dict())
        except Exception as exc:
            logger.error(f"AlertWriter: insert failed: {exc}")

    def close(self) -> None:
        if self._conn and not self._conn.closed:
            self._conn.close()
        logger.info("AlertWriter: closed")
