import math
import random
from typing import Dict, Any

from .base import BaseSensor


class VibrationSensor(BaseSensor):
    """
    Vibration sensor mounted on HVAC / mechanical equipment (mm/s RMS).

    Normal operating baseline: ~1.5 mm/s.
    Higher during morning HVAC ramp-up (6–9 h) and afternoon peak (13–15 h).
    Occasional spike events (compressor start / door slam) with low probability.
    Gaussian noise σ = 0.25 mm/s.
    """

    BASELINE     = 1.5    # mm/s at rest / normal operation
    RAMP_GAIN    = 0.8    # extra vibration during HVAC startup cycles
    SPIKE_PROB   = 0.005  # 0.5 % chance of transient spike per reading
    SPIKE_RANGE  = (3.0, 8.0)

    def _sample(self, context: Dict[str, Any]) -> float:
        hour: float = context.get("hour", 12.0)

        # HVAC ramp-up peaks ~08:00 and 14:00
        hvac_cycle = self.RAMP_GAIN * abs(math.sin(2 * math.pi * (hour - 8) / 24))
        noise = random.gauss(0, 0.25)
        value = self.BASELINE + hvac_cycle + noise

        # Rare transient spike
        if random.random() < self.SPIKE_PROB:
            value += random.uniform(*self.SPIKE_RANGE)

        return self._clamp(value, lo=0.0, hi=20.0)
