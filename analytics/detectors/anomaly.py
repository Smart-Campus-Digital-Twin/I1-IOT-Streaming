"""
Z-score anomaly detector using a per-sensor sliding window.

Window state (n, mean, M2) is optionally persisted to Redis so that the
30-reading warmup period survives container restarts.  Without Redis the
detector falls back to pure in-memory state with no persistence.

State is written to Redis every CHECKPOINT_EVERY updates per sensor to
keep write load low while still recovering quickly after a restart.
"""
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Optional, TYPE_CHECKING

import sys
sys.path.insert(0, "/app")

from shared.models import SensorReading

if TYPE_CHECKING:
    import redis

_WARMUP             = 30    # samples before detection activates
_DEFAULT_Z_THRESHOLD = 3.5
_CHECKPOINT_EVERY   = 50    # persist state to Redis every N updates per sensor
_REDIS_KEY_PREFIX   = "campus:anomaly:"


@dataclass
class _WindowState:
    n:    int   = 0
    mean: float = 0.0
    M2:   float = 0.0      # Welford's sum of squared deviations
    _updates_since_checkpoint: int = field(default=0, repr=False)

    def update(self, value: float) -> None:
        self.n += 1
        delta = value - self.mean
        self.mean += delta / self.n
        self.M2 += delta * (value - self.mean)
        self._updates_since_checkpoint += 1

    @property
    def variance(self) -> float:
        return self.M2 / (self.n - 1) if self.n > 1 else 0.0

    @property
    def std(self) -> float:
        return math.sqrt(self.variance)

    def z_score(self, value: float) -> Optional[float]:
        if self.n < _WARMUP or self.std == 0:
            return None
        return (value - self.mean) / self.std

    def to_dict(self) -> dict:
        return {"n": self.n, "mean": self.mean, "M2": self.M2}

    @classmethod
    def from_dict(cls, d: dict) -> "_WindowState":
        obj = cls()
        obj.n    = int(d.get("n",    0))
        obj.mean = float(d.get("mean", 0.0))
        obj.M2   = float(d.get("M2",   0.0))
        return obj


class ZScoreDetector:
    """
    Stateful, per-sensor anomaly detector.

    Pass a connected redis.Redis instance to enable window checkpointing.
    The detector loads all existing states from Redis on init so it resumes
    immediately after a restart without re-warming up.
    """

    def __init__(
        self,
        z_threshold: float = _DEFAULT_Z_THRESHOLD,
        redis_client: Optional["redis.Redis"] = None,
    ) -> None:
        self._threshold = z_threshold
        self._redis     = redis_client
        self._windows: Dict[str, _WindowState] = defaultdict(_WindowState)

        if self._redis:
            self._load_all()

    # ------------------------------------------------------------------

    def detect(self, reading: SensorReading) -> tuple:
        state = self._windows[reading.sensor_id]
        z = state.z_score(reading.value)
        state.update(reading.value)

        if self._redis and state._updates_since_checkpoint >= _CHECKPOINT_EVERY:
            self._checkpoint(reading.sensor_id, state)
            state._updates_since_checkpoint = 0

        if z is None:
            return None, False
        return round(z, 4), abs(z) > self._threshold

    # ------------------------------------------------------------------

    def _redis_key(self, sensor_id: str) -> str:
        return f"{_REDIS_KEY_PREFIX}{sensor_id}"

    def _checkpoint(self, sensor_id: str, state: _WindowState) -> None:
        try:
            self._redis.hset(self._redis_key(sensor_id), mapping=state.to_dict())
        except Exception as exc:
            # Non-fatal — detection continues in-memory
            pass

    def _load_all(self) -> None:
        """Load every persisted window state from Redis on startup."""
        try:
            keys = self._redis.keys(f"{_REDIS_KEY_PREFIX}*")
            for key in keys:
                data = self._redis.hgetall(key)
                if data:
                    sensor_id = key.decode().replace(_REDIS_KEY_PREFIX, "", 1)
                    self._windows[sensor_id] = _WindowState.from_dict(
                        {k.decode(): v.decode() for k, v in data.items()}
                    )
        except Exception as exc:
            pass   # Redis read failure is non-fatal; start with empty windows
