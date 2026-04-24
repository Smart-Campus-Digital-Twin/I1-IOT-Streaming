import random
from typing import Any, Dict, List, Tuple

from .base import BaseSensor


# Lecture timetable (24-hour): (start, end)
_LECTURE_SLOTS: List[Tuple[float, float]] = [
    (8  + 15/60, 10 + 15/60),   # 08:15–10:15
    (10 + 30/60, 12 + 15/60),   # 10:30–12:15
    (13 + 15/60, 15 + 15/60),   # 13:15–15:15
    (15 + 15/60, 17 + 15/60),   # 15:15–17:15
]

_PRE_WINDOW  = 15 / 60   # 15-min student arrival window before lecture
_POST_WINDOW = 10 / 60   # 10-min drain window after lecture ends

# Canteen busy periods: (start, end, peak_ratio_of_capacity)
_CANTEEN_PERIODS: List[Tuple[float, float, float]] = [
    (7.5,            9.0,            0.50),  # Breakfast
    (10 + 15/60,     10 + 30/60,     0.75),  # Morning break spike
    (12.0,           13.5,           0.95),  # Lunch peak
    (15 + 15/60,     15 + 30/60,     0.60),  # Tea break
    (17.0,           19.0,           0.35),  # Evening / dinner
]


def _lecture_target_ratio(hour: float) -> float:
    """Target occupancy ratio for a classroom/lab at the given hour (weekday)."""
    for start, end in _LECTURE_SLOTS:
        pre_start = start - _PRE_WINDOW
        post_end  = end   + _POST_WINDOW

        if pre_start <= hour < start:
            return 0.88 * (hour - pre_start) / _PRE_WINDOW   # ramp up

        if start <= hour <= end:
            return 0.88

        if end < hour < post_end:
            return 0.88 * (1.0 - (hour - end) / _POST_WINDOW)  # drain

    if hour < 6.5 or hour >= 20.0:         # night
        return 0.0
    return 0.0   # between lectures, before first slot, lunch break — rooms empty


def _canteen_target_ratio(hour: float) -> float:
    """Target occupancy ratio for the canteen at the given hour (weekday)."""
    for start, end, peak in _CANTEEN_PERIODS:
        if start <= hour < end:
            # Trapezoid shape: ramp-up / flat / ramp-down, each 1/3 of the window
            ramp = (end - start) / 3.0
            if hour < start + ramp:
                return peak * (hour - start) / ramp
            if hour > end - ramp:
                return peak * (end - hour) / ramp
            return peak
    if hour < 6.5 or hour >= 20.0:
        return 0.0
    return 0.05   # light background traffic


class OccupancySensor(BaseSensor):
    """
    Stateful bi-directional door counter.

    Maintains a running person count updated each tick via probabilistic
    entry/exit events. The target count is driven by a lecture timetable
    (classrooms/labs) or a meal-time schedule (canteen). Reports the
    current integer headcount — identical to how real people-counter
    hardware (IR beam or thermal) pushes periodic snapshots upstream.
    """

    def __init__(
        self,
        *args,
        capacity: int = 30,
        room_type: str = "classroom",
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.capacity  = capacity
        self.room_type = room_type
        self._count: int = 0
        self._evening_active: bool  = False
        self._evening_ratio:  float = 0.0

    # ------------------------------------------------------------------
    def _target_ratio(self, hour: float, day_of_week: int) -> float:
        is_weekend = day_of_week >= 5

        if self.room_type == "canteen":
            base = _canteen_target_ratio(hour)
            return base * 0.35 if is_weekend else base

        if is_weekend:
            return 0.05 if 9.0 <= hour <= 17.0 else 0.0

        ratio = _lecture_target_ratio(hour)

        if self.room_type in ("classroom", "lab") and 17 + 15/60 < hour < 21.0:
            ratio = self._apply_evening_event(hour, ratio)

        return ratio

    def _apply_evening_event(self, hour: float, base: float) -> float:
        """Randomly trigger/hold/end an evening gathering (lecture rooms only)."""
        if not self._evening_active:
            # ~0.15 % chance per 5-second tick → roughly one event per 2–3 evenings per room
            if random.random() < 0.0015:
                self._evening_active = True
                self._evening_ratio  = random.uniform(0.25, 0.55)
        else:
            if hour >= 21.0 or random.random() < 0.0008:
                self._evening_active = False
        return self._evening_ratio if self._evening_active else base

    # ------------------------------------------------------------------
    def _sample(self, context: Dict[str, Any]) -> float:
        hour:        float = context.get("hour", 12.0)
        day_of_week: int   = context.get("day_of_week", 0)

        target = self._target_ratio(hour, day_of_week) * self.capacity
        # Per-sensor jitter prevents all rooms filling/draining in perfect sync
        target += random.gauss(0, max(1, self.capacity * 0.04))
        target  = int(max(0, min(self.capacity, round(target))))

        diff = target - self._count

        if diff > 0:
            # Entry: fast burst when count is far below target (lecture start),
            # trickles to near-zero as target is approached
            prob = min(0.92, diff / max(1, self.capacity * 1.5))
            if random.random() < prob:
                self._count += 1
        elif diff < 0:
            # Exit: slightly faster than entry (students leave in groups)
            prob = min(0.92, -diff / max(1, self.capacity * 1.0))
            if random.random() < prob:
                self._count -= 1

        self._count = max(0, min(self.capacity, self._count))
        return self._count  # int — keeps field type consistent with existing InfluxDB schema
