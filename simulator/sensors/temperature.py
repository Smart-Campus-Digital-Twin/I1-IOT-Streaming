import math
import random
from typing import Dict, Any

from .base import BaseSensor


class TemperatureSensor(BaseSensor):
    """
    Indoor temperature sensor (HVAC-controlled space).

    Daily pattern:
      - Night setback  (~18 °C) from 22:00–06:00
      - Morning warm-up ramp to 21 °C by 08:00
      - Peak ~22.5 °C around 14:00 (solar gain + bodies)
      - HVAC pulls it back down by 18:00
    Occupancy adds up to +1.5 °C.
    Gaussian noise σ = 0.3 °C.
    """

    SETPOINT = 21.0   # °C comfort setpoint
    AMPLITUDE = 1.8   # °C peak-to-trough half-swing
    PEAK_HOUR = 14.0  # hour of daily peak (24-h clock)
    OCC_GAIN  = 1.5   # °C lift at full occupancy

    def _sample(self, context: Dict[str, Any]) -> float:
        hour: float = context.get("hour", 12.0)
        occ:  float = context.get("occupancy_ratio", 0.0)  # 0-1

        # Sinusoidal HVAC cycle (cooler at night, warmer afternoon)
        cycle = self.AMPLITUDE * math.sin(2 * math.pi * (hour - self.PEAK_HOUR + 12) / 24)
        occupancy_effect = self.OCC_GAIN * occ
        noise = random.gauss(0, 0.3)

        return self._clamp(
            self.SETPOINT + cycle + occupancy_effect + noise,
            lo=15.0,
            hi=32.0,
        )
