# Campus Sensor Publisher

This folder contains the ESP32 demo MQTT publisher sketch used to publish
Smart Classroom telemetry from the SHT30 temperature sensor and IR occupancy
counter.

Arduino sketch path:

```text
firmware/esp32/campus_sensor_publisher/campus_sensor_publisher.ino
```

The current demo publisher:

- connect to Wi-Fi,
- connect to the public HiveMQ broker,
- read SHT30 temperature,
- calculate occupancy from the two IR beams,
- publish JSON telemetry to `smartclassroom/classroom001/telemetry`.

## Viewing Published Data

Use the HiveMQ WebSocket Client:

```text
https://www.hivemq.com/demos/websocket-client/
```

Connection settings:

```text
Host: broker.hivemq.com
Port: 8884
SSL: checked / on
Username: empty
Password: empty
Clean Session: checked
```

After connecting, subscribe to:

```text
smartclassroom/classroom001/telemetry
```

When the ESP32 is running, published payloads should appear on that topic.

## Production Note

This is a demo publisher. A production version for this repo should be adapted
to publish payloads matching `contracts/payload.schema.json` on topics shaped
like `campus/{building_id}/floor{floor}/{room_id}/{sensor_type}`.
