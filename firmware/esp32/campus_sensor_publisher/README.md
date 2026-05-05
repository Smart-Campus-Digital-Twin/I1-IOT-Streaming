# Campus Sensor Publisher

Put the final ESP32 MQTT publisher sketch in this folder.

Recommended Arduino sketch path:

```text
firmware/esp32/campus_sensor_publisher/campus_sensor_publisher.ino
```

That sketch should:

- connect to Wi-Fi,
- connect to the Mosquitto broker,
- read SHT30 temperature and humidity,
- calculate occupancy from the two IR beams,
- publish JSON payloads that match `contracts/payload.schema.json`,
- publish to topics shaped like `campus/{building_id}/floor{floor}/{room_id}/{sensor_type}`.
