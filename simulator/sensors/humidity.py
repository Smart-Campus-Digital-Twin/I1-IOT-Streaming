import math
import random
from typing import Dict, Any

from .base import BaseSensor


class HumiditySensor(BaseSensor):
    """
    Relative humidity sensor.

    Humidity is inversely correlated with temperature:
      - Drier in the warm afternoon, more humid early morning.
    Occupancy adds moisture (breathing, bodies).
    Gaussian noise σ = 2 %.
    """

    BASE      = 45.0   # % RH mid-point
    AMPLITUDE =  6.0   # % RH half-swing
    PEAK_HOUR =  7.0   # early morning peak
    OCC_GAIN  =  5.0   # % RH lift at full occupancy

    def _sample(self, context: Dict[str, Any]) -> float:
        hour: float = context.get("hour", 12.0)
        occ:  float = context.get("occupancy_ratio", 0.0)

        # Inverse to temperature: peaks early morning, dips mid-afternoon
        cycle = self.AMPLITUDE * math.sin(2 * math.pi * (hour - self.PEAK_HOUR) / 24)
        occupancy_effect = self.OCC_GAIN * occ
        noise = random.gauss(0, 2.0)

        return self._clamp(
            self.BASE + cycle + occupancy_effect + noise,
            lo=20.0,
            hi=90.0,
        )
