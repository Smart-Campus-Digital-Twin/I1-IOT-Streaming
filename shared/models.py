from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
import json

SENSOR_UNITS: Dict[str, str] = {
    "temperature": "celsius",
    "humidity": "percent",
    "pressure": "hPa",
    "vibration": "mm/s",
    "occupancy": "persons",
}

SENSOR_RANGES: Dict[str, tuple] = {
    "temperature": (15.0, 35.0),
    "humidity": (10.0, 100.0),
    "pressure": (980.0, 1050.0),
    "vibration": (0.0, 20.0),
    "occupancy": (0.0, 500.0),
}

KAFKA_TOPICS = [
    "sensors.temperature",
    "sensors.humidity",
    "sensors.pressure",
    "sensors.vibration",
    "sensors.occupancy",
    "alerts.threshold",
    "alerts.anomaly",
]


@dataclass
class SensorReading:
    sensor_id: str
    building_id: str
    floor: int
    room_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp_ms: int
    quality: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SensorReading":
        return cls(**data)

    @classmethod
    def from_json(cls, payload: str) -> "SensorReading":
        return cls.from_dict(json.loads(payload))

    @property
    def mqtt_topic(self) -> str:
        return f"campus/{self.building_id}/floor{self.floor}/{self.room_id}/{self.sensor_type}"

    @property
    def kafka_topic(self) -> str:
        return f"sensors.{self.sensor_type}"

    @property
    def influx_measurement(self) -> str:
        return self.sensor_type


@dataclass
class AlertEvent:
    alert_id: str
    sensor_id: str
    building_id: str
    floor: int
    room_id: str
    sensor_type: str
    alert_type: str   # threshold_breach | anomaly | sensor_failure
    severity: str     # info | warning | critical
    value: float
    threshold: Optional[float]
    message: str
    timestamp_ms: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, payload: str) -> "AlertEvent":
        return cls(**json.loads(payload))
