from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Room:
    room_id: str
    building_id: str
    floor: int
    room_type: str   # classroom | office | lab | server_room | corridor
    capacity: int
    sensors: List[str] = field(default_factory=list)


@dataclass
class Building:
    building_id: str
    name: str
    rooms: List[Room] = field(default_factory=list)


def _make_room(
    building_id: str,
    floor: int,
    number: int,
    room_type: str,
    capacity: int,
    sensors: List[str],
) -> Room:
    room_id = f"{building_id}-f{floor}-r{number:02d}"
    return Room(room_id, building_id, floor, room_type, capacity, sensors)


ALL_SENSORS     = ["temperature", "humidity", "pressure", "vibration", "occupancy"]
ENV_SENSORS     = ["temperature", "humidity", "pressure", "occupancy"]
BASIC_SENSORS   = ["temperature", "occupancy"]
CANTEEN_SENSORS = ["temperature", "humidity", "occupancy"]


class CampusTopology:
    """Static description of all campus buildings, floors, and rooms."""

    def __init__(self) -> None:
        self._buildings: Dict[str, Building] = {}
        self._build()

    def _build(self) -> None:
        # Building A — Academic Block (classrooms, labs)
        bld_a = Building("building-a", "Academic Block A")
        for floor in range(1, 4):
            bld_a.rooms.extend([
                _make_room("building-a", floor, 1, "classroom", 40, ALL_SENSORS),
                _make_room("building-a", floor, 2, "classroom", 40, ALL_SENSORS),
                _make_room("building-a", floor, 3, "lab",       20, ALL_SENSORS),
                _make_room("building-a", floor, 4, "office",    10, ENV_SENSORS),
                _make_room("building-a", floor, 5, "office",    10, ENV_SENSORS),
                _make_room("building-a", floor, 6, "corridor",   0, BASIC_SENSORS),
            ])

        # Building B — Administrative Block (offices)
        bld_b = Building("building-b", "Administrative Block B")
        for floor in range(1, 4):
            bld_b.rooms.extend([
                _make_room("building-b", floor, 1, "office",    15, ENV_SENSORS),
                _make_room("building-b", floor, 2, "office",    15, ENV_SENSORS),
                _make_room("building-b", floor, 3, "office",    20, ENV_SENSORS),
                _make_room("building-b", floor, 4, "corridor",   0, BASIC_SENSORS),
            ])

        # Building C — Research & Facilities (labs, server rooms)
        bld_c = Building("building-c", "Research & Facilities Block C")
        for floor in range(1, 3):
            bld_c.rooms.extend([
                _make_room("building-c", floor, 1, "lab",         15, ALL_SENSORS),
                _make_room("building-c", floor, 2, "lab",         15, ALL_SENSORS),
                _make_room("building-c", floor, 3, "server_room",  0, ["temperature", "humidity", "vibration"]),
                _make_room("building-c", floor, 4, "office",      10, ENV_SENSORS),
                _make_room("building-c", floor, 5, "corridor",     0, BASIC_SENSORS),
            ])

        # Building D — Student Canteen
        bld_d = Building("building-d", "Student Canteen")
        bld_d.rooms.extend([
            _make_room("building-d", 1, 1, "canteen",  150, CANTEEN_SENSORS),
            _make_room("building-d", 1, 2, "corridor",   0, BASIC_SENSORS),
        ])

        for bld in (bld_a, bld_b, bld_c, bld_d):
            self._buildings[bld.building_id] = bld

    @property
    def buildings(self) -> Dict[str, Building]:
        return self._buildings

    def all_rooms(self) -> List[Room]:
        return [r for bld in self._buildings.values() for r in bld.rooms]

    def rooms_with_sensor(self, sensor_type: str) -> List[Room]:
        return [r for r in self.all_rooms() if sensor_type in r.sensors]
