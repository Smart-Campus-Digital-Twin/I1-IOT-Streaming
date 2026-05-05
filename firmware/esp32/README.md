# ESP32 Firmware Workspace

This folder contains ESP32-side code for the Smart Campus MQTT pipeline.

## Structure

- `tests/`: small hardware and logic sketches used while wiring and validating sensors.
- `prototypes/`: combined sketches that behave like early firmware but do not yet publish MQTT.
- `campus_sensor_publisher/`: intended home for the final production sketch that connects to Wi-Fi and publishes MQTT messages matching `contracts/payload.schema.json`.

## Current Sketches

- `tests/i2c_scanner`: scans both normal and swapped ESP32 I2C pin pairings.
- `tests/sht30_sensor_test`: verifies SHT30 temperature and humidity readings.
- `tests/ir_single_beam_test`: verifies one IR break-beam sensor on GPIO 32.
- `tests/ir_dual_beam_test`: verifies two IR break-beam sensors on GPIO 32 and GPIO 33.
- `tests/occupancy_counter_test`: validates entry/exit counting from two IR beams.
- `prototypes/sht30_ir_serial_telemetry`: combines SHT30 readings, IR beam status, and occupancy counting over Serial.

## MQTT Contract

Final ESP32 firmware should publish JSON payloads to:

```text
campus/{building_id}/floor{floor}/{room_id}/{sensor_type}
```

The payload shape must match `contracts/payload.schema.json`.
