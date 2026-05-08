# Edge Hardware: Energy Telemetry Topology & Data Acquisition Architecture

## 1. Executive Summary

The Device & Edge Systems layer (I-1) is responsible for the physical cyber-link of the Smart Campus Digital Twin. To feed the Data & Intelligence (I-2) XGBoost predictive models, standard building-level energy aggregations are insufficient. We have architected a highly granular, micro-monitoring topology designed to capture room-specific telemetry safely, accurately, and with sub-100ms transmission latency.

## 2. Hardware Selection & Sensor Deployment

- **Microcontroller Unit (MCU):** ESP32 NodeMCU (Dual-Core 240MHz, built-in 802.11 b/g/n Wi-Fi).
- **Energy Transducer:** PZEM-004T V3.0 AC Digital Power/Energy Meter.
- **Measurement Mechanism:** Non-invasive Current Transformer (CT) Clamps (100A rating).
- **Deployment Topology:** The ESP32 edge nodes are physically decoupled from the environmental room sensors to optimize hardware costs. A single ESP32 node is positioned inside the floor's electrical Distribution Board (DB). Using UART multi-addressing, a single ESP32 queries multiple PZEM-004T modules simultaneously. The CT clamps are safely attached exclusively to the Live (L) wires of individual Miniature Circuit Breakers (MCBs) corresponding to specific academic rooms.

## 3. Edge Processing & Data Serialization

Raw electrical signals are not blindly forwarded. The ESP32 performs edge-level calculations before network transmission to conserve bandwidth:

1. **True Power Calculation:** The PZEM module calculates True Active Power ($P = V \times I \times \cos \theta$). The ESP32 polls this data via UART.
2. **Payload Serialization:** The C++ firmware serializes the float values into a strict JSON contract (`SensorReading`) mandated by the upstream ingestion bridge.
3. **Transmission Protocol:** Data is published over MQTT to the Eclipse Mosquitto broker using **QoS 1 (At least once)** to guarantee message delivery even during transient campus Wi-Fi drops.

### 3.1. Standardized JSON Telemetry Contract

```json
{
  "sensor_id": "energy_node_DB_floor1_roomA",
  "building_id": "EF",
  "room_id": "EF101",
  "sensor_type": "energy_watts",
  "metrics": {
    "voltage_v": 231.2,
    "current_a": 12.4,
    "active_power_w": 2721.5,
    "power_factor": 0.95,
    "frequency_hz": 50.0
  },
  "timestamp_ms": 1714980240000
}
```

## 4. Hardware Limitations & Constraints

To ensure architectural transparency, the following physical constraints govern the system:

- **Faraday Cage Effect:** Electrical DBs act as localized Faraday cages, heavily attenuating the 2.4GHz Wi-Fi signal of the ESP32 PCB antenna.
- _Mitigation Strategy:_ Nodes must utilize external SMA antennas routed outside the DB chassis, or edge nodes must be housed in IP65-rated PVC enclosures adjacent to the DB.

- **Noise Floor (Low-Load Inaccuracy):** The 100A CT clamps exhibit a minimum detection threshold (~0.2A). Parasitic or standby loads (e.g., a single 5W LED indicator) will fall below the noise floor and register as 0 Watts.
- _Acceptance Criteria:_ This is acceptable for the MVP scope, as the predictive AI models are correlating massive loads (HVAC arrays, servers) with room occupancy, making negligible parasitic loads statistically insignificant.
