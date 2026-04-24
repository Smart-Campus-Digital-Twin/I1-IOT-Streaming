"""
Simulator entry point.

Builds one sensor object per (room, sensor_type) pair, then publishes
readings at a fixed interval.  An occupancy_ratio derived from OccupancySensor
readings is passed as context to correlated sensors (temperature, humidity,
vibration) so they react realistically to people being in the space.
"""
import signal
import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo

sys.path.insert(0, "/app")

from shared.logging_config import get_logger
from simulator.campus.topology import CampusTopology, Room
from simulator.config import config
from simulator.publisher import MQTTPublisher
from simulator.sensors.base import BaseSensor
from simulator.sensors.humidity import HumiditySensor
from simulator.sensors.occupancy import OccupancySensor
from simulator.sensors.pressure import PressureSensor
from simulator.sensors.temperature import TemperatureSensor
from simulator.sensors.vibration import VibrationSensor

logger = get_logger("simulator.main", config.log_level)

_SENSOR_CLASSES = {
    "temperature": TemperatureSensor,
    "humidity":    HumiditySensor,
    "pressure":    PressureSensor,
    "vibration":   VibrationSensor,
    "occupancy":   OccupancySensor,
}


def _build_sensors(topology: CampusTopology) -> List[Tuple[Room, BaseSensor]]:
    sensors: List[Tuple[Room, BaseSensor]] = []
    for room in topology.all_rooms():
        for s_type in room.sensors:
            sensor_id = f"{room.room_id}-{s_type}"
            cls = _SENSOR_CLASSES[s_type]
            kwargs = dict(
                sensor_id=sensor_id,
                room_id=room.room_id,
                building_id=room.building_id,
                floor=room.floor,
                sensor_type=s_type,
            )
            if s_type == "occupancy":
                kwargs["capacity"]  = room.capacity
                kwargs["room_type"] = room.room_type
            sensors.append((room, cls(**kwargs)))
    return sensors


def _context_now() -> Dict:
    now = datetime.now(ZoneInfo(config.campus_timezone))
    return {
        "hour":        now.hour + now.minute / 60.0,
        "day_of_week": now.weekday(),   # 0=Mon, 6=Sun
    }


def main() -> None:
    logger.info("Starting Smart Campus Simulator")
    topology  = CampusTopology()
    publisher = MQTTPublisher()
    publisher.connect()

    all_sensors  = _build_sensors(topology)
    reading_count = 0

    # Group occupancy sensors by room for context injection
    occ_sensors: Dict[str, OccupancySensor] = {
        room.room_id: sensor
        for room, sensor in all_sensors
        if isinstance(sensor, OccupancySensor)
    }

    stop = False

    def _handle_signal(sig, frame):
        nonlocal stop
        logger.info("Shutdown signal received")
        stop = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT,  _handle_signal)

    logger.info(
        "Simulator ready",
        extra={
            "sensor_count":   len(all_sensors),
            "building_count": len(topology.buildings),
            "room_count":     len(topology.all_rooms()),
            "interval_s":     config.publish_interval_s,
        },
    )

    while not stop:
        ctx = _context_now()

        # First pass: sample occupancy to build room-level context
        occ_readings: Dict[str, float] = {}
        for room_id, occ_sensor in occ_sensors.items():
            room_obj = next(r for r, s in all_sensors if r.room_id == room_id and isinstance(s, OccupancySensor))
            r = occ_sensor.read(ctx)
            occ_readings[room_id] = r.value / max(1, room_obj.capacity)

        # Second pass: sample all sensors with occupancy context
        for room, sensor in all_sensors:
            room_ctx = {**ctx, "occupancy_ratio": occ_readings.get(room.room_id, 0.0)}
            reading = sensor.read(room_ctx)

            # Inject occasional artificial anomaly for analytics testing
            if config.anomaly_every_n > 0 and reading_count % config.anomaly_every_n == 0:
                reading.metadata["injected_anomaly"] = True

            publisher.publish(reading)
            reading_count += 1

        if reading_count % (len(all_sensors) * 10) == 0:
            logger.info("Heartbeat", extra={"total_readings": reading_count})

        time.sleep(config.publish_interval_s)

    publisher.disconnect()
    logger.info("Simulator stopped", extra={"total_readings": reading_count})


if __name__ == "__main__":
    main()
