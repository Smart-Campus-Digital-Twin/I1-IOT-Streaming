"""
Rule-based threshold detector.

Each sensor type has a configurable (low, high) range.  Readings outside that
range generate a ThresholdBreach with a severity mapped to how far the value
deviates from the boundary.
"""
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import sys
sys.path.insert(0, "/app")

from shared.models import SensorReading


@dataclass(frozen=True)
class _Rule:
    lo:       float
    hi:       float
    warn_pct: float = 0.10  # within 10 % of limit → warning; beyond → critical


_DEFAULT_RULES: Dict[str, _Rule] = {
    "temperature": _Rule(lo=16.0,  hi=30.0),
    "humidity":    _Rule(lo=20.0,  hi=80.0),
    "pressure":    _Rule(lo=990.0, hi=1040.0),
    "vibration":   _Rule(lo=0.0,   hi=7.0),
    "occupancy":   _Rule(lo=0.0,   hi=float("inf"), warn_pct=0.0),
}


@dataclass
class ThresholdBreach:
    sensor_type: str
    value:       float
    limit:       float
    direction:   str    # "high" | "low"
    severity:    str    # "warning" | "critical"
    message:     str


class ThresholdDetector:
    def __init__(self, rules: Optional[Dict[str, _Rule]] = None) -> None:
        self._rules: Dict[str, _Rule] = rules or _DEFAULT_RULES

    def check(self, reading: SensorReading) -> Optional[ThresholdBreach]:
        rule = self._rules.get(reading.sensor_type)
        if rule is None:
            return None

        value = reading.value

        if value > rule.hi:
            span     = rule.hi - rule.lo if rule.lo != float("-inf") else rule.hi
            overshoot = (value - rule.hi) / (span * rule.warn_pct + 1e-9)
            severity = "critical" if overshoot > 1.0 else "warning"
            return ThresholdBreach(
                sensor_type=reading.sensor_type,
                value=value,
                limit=rule.hi,
                direction="high",
                severity=severity,
                message=f"{reading.sensor_type} {value:.2f} exceeds upper limit {rule.hi}",
            )

        if value < rule.lo:
            span     = rule.hi - rule.lo if rule.hi != float("inf") else rule.lo
            undershoot = (rule.lo - value) / (span * rule.warn_pct + 1e-9)
            severity = "critical" if undershoot > 1.0 else "warning"
            return ThresholdBreach(
                sensor_type=reading.sensor_type,
                value=value,
                limit=rule.lo,
                direction="low",
                severity=severity,
                message=f"{reading.sensor_type} {value:.2f} below lower limit {rule.lo}",
            )

        return None
