import random
from typing import Dict, Any

from .base import BaseSensor


class PressureSensor(BaseSensor):
    """
    Barometric pressure sensor.

    Pressure is driven by weather fronts — very slow drift (< 3 hPa/h),
    not a daily cycle.  We simulate a continuous random walk with
    mean-reversion toward the standard ISA sea-level value (1013.25 hPa).
    Gaussian noise σ = 0.5 hPa.
    """

    ISA_BASE      = 1013.25  # hPa (standard atmosphere)
    DRIFT_SIGMA   =    0.8   # hPa random-walk step per reading
    REVERT_COEFF  =    0.02  # pulls drift back toward 0 each step

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._drift: float = 0.0  # accumulated departure from ISA base

    def _sample(self, context: Dict[str, Any]) -> float:
        # Mean-reverting random walk
        self._drift = (
            self._drift * (1 - self.REVERT_COEFF)
            + random.gauss(0, self.DRIFT_SIGMA)
        )
        noise = random.gauss(0, 0.5)
        return self._clamp(
            self.ISA_BASE + self._drift + noise,
            lo=980.0,
            hi=1050.0,
        )
