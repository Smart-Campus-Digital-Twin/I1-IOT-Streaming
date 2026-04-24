"""
Alert suppressor — prevents the analytics engine from flooding downstream
consumers and the alert_events table with thousands of identical alerts
when a sensor gets stuck in a bad state.

Logic: once an alert fires for a (sensor_id, alert_type) pair, that same
combination is suppressed for COOLDOWN_S seconds.  A suppressed alert is
counted but not published to Kafka or PostgreSQL.
"""
import time
from typing import Dict, Tuple


class AlertSuppressor:
    """
    In-memory cooldown tracker.

    Thread-safe for single-threaded consumers (one analytics main loop).
    If you scale to multiple analytics instances, move state to Redis.
    """

    def __init__(self, cooldown_s: int = 300) -> None:
        self._cooldown = cooldown_s
        # (sensor_id, alert_type) -> monotonic time of last fired alert
        self._last_fired: Dict[Tuple[str, str], float] = {}
        self.suppressed_count = 0

    def is_suppressed(self, sensor_id: str, alert_type: str) -> bool:
        """
        Returns True if this alert should be suppressed (duplicate within
        the cooldown window).  Updates the last-fired timestamp when the
        alert is allowed through.
        """
        key = (sensor_id, alert_type)
        now = time.monotonic()
        last = self._last_fired.get(key, 0.0)

        if now - last < self._cooldown:
            self.suppressed_count += 1
            return True

        self._last_fired[key] = now
        return False

    def stats(self) -> Dict[str, int]:
        return {
            "active_cooldowns": len(self._last_fired),
            "suppressed_total": self.suppressed_count,
        }
