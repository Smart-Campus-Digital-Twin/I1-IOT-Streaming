# MQTT Topic Taxonomy — Smart Campus Digital Twin

## Overview

This document defines the complete MQTT topic structure for all sensor data published by Pillar 1 (Edge/IoT).  
**Version**: 1.0  
**Last Updated**: May 3, 2026  
**Owner**: Pillar 1 Lead (Buwaneka)

---

## Topic Hierarchy

### Root Topic: `campus`

All device-published sensor readings use this prefix. Topics follow a strict hierarchical structure:

```
campus/
  ├── {building_id}/
  │   ├── floor{floor}/
  │   │   ├── {room_id}/
  │   │   │   ├── temperature
  │   │   │   ├── humidity
  │   │   │   ├── pressure
  │   │   │   ├── vibration
  │   │   │   └── occupancy
  │   │   └── ...
  │   └── ...
  └── ...
```

---

## Field Definitions

### `{building_id}`

A stable, unique identifier for each campus building.

**Format**: lowercase alphanumeric with hyphens  
**Pattern**: `building-[a-d]`  
**Examples**:
- `building-a` — Academic Block A (classrooms, labs)
- `building-b` — Administrative Block B (offices)
- `building-c` — Research & Facilities Block C (labs, server rooms)
- `building-d` — Student Canteen (cafeteria)

**Cardinality**: Fixed set of 4 buildings (no wildcards in practice).

---

### `floor`

The physical floor number within a building.

**Format**: Literal string `floor` followed by integer  
**Pattern**: `floor[0-9]+`  
**Examples**: `floor1`, `floor2`, `floor3`

**Note**: Floors are 1-indexed. `floor0` is not used in this campus.

---

### `{room_id}`

A stable, globally unique identifier for a room or space.

**Format**: Compound ID combining building, floor, and room number  
**Pattern**: `{building_id}-f{floor}-r{room_number:02d}`  
**Examples**:
- `building-a-f1-r01` — Building A, Floor 1, Room 01 (classroom)
- `building-a-f2-r06` — Building A, Floor 2, Room 06 (corridor)
- `building-c-f1-r03` — Building C, Floor 1, Room 03 (server room)
- `building-d-f1-r01` — Building D, Floor 1, Room 01 (canteen)

**Note**: Room IDs are static. They do not change over the device's lifetime. Rooms are not renumbered.

---

### `{sensor_type}`

The type of physical sensor being read.

**Format**: lowercase, single word  
**Enum**: `temperature`, `humidity`, `pressure`, `vibration`, `occupancy`  

**Description per type**:

| Type | Unit | Physical Meaning | Typical Range | Device Count |
|---|---|---|---|---|
| `temperature` | celsius | Ambient air temperature | 15–35°C | ~160 |
| `humidity` | percent | Relative humidity | 10–100% | ~100 |
| `pressure` | hPa | Atmospheric pressure | 980–1050 hPa | ~50 |
| `vibration` | mm/s | Vibration amplitude | 0–20 mm/s | ~60 |
| `occupancy` | persons | Number of people in space | 0–500 | ~80 |

---

## Full Examples

### Example 1: Classroom Temperature
```
campus/building-a/floor1/building-a-f1-r01/temperature
```
- Building: Academic Block A
- Floor: 1
- Room: 01 (classroom, capacity 40)
- Sensor: temperature reading

### Example 2: Server Room Vibration
```
campus/building-c/floor1/building-c-f1-r03/vibration
```
- Building: Research & Facilities (server rooms)
- Floor: 1
- Room: 03 (server room, no occupancy sensor)
- Sensor: vibration detection for equipment health

### Example 3: Canteen Occupancy
```
campus/building-d/floor1/building-d-f1-r01/occupancy
```
- Building: Student Canteen
- Floor: 1
- Room: 01 (main dining area)
- Sensor: occupancy count

---

## Wildcard Subscriptions

MQTT wildcards (`+` for single level, `#` for multi-level) are supported:

### Subscribe to all sensors in a building
```
campus/building-a/+/+/+
```
Matches: `campus/building-a/floor1/building-a-f1-r01/temperature`, etc.

### Subscribe to all temperature sensors
```
campus/+/+/+/temperature
```
Matches: `campus/building-a/floor1/building-a-f1-r01/temperature`, `campus/building-b/floor2/building-b-f2-r01/temperature`, etc.

### Subscribe to all sensors everywhere
```
campus/#
```
Matches: all sensor topics under `campus/`

---

## Quality of Service (QoS)

All published readings use **QoS 1** (at-least-once delivery).

**Rationale**:
- QoS 0 (at-most-once) risks silent data loss if network hiccup occurs during transmission.
- QoS 1 ensures the broker acknowledges receipt; device retries if no ACK within timeout.
- QoS 2 (exactly-once) is too expensive for 160 sensors publishing every 5 seconds.

---

## Topic Naming Constraints

1. **No spaces, tabs, or special characters** (except `-` for clarity).
2. **No uppercase letters** (topics are lowercase).
3. **No leading/trailing slashes** on segments.
4. **No duplicate level names** (e.g., no `floor/building/floor`).
5. **Immutable room IDs**: Once a room is assigned `building-a-f1-r01`, it keeps that ID forever. Rooms are not renumbered.
6. **No device-level topics at the edge**: Topics are based on room + sensor type, not device hardware. Multiple devices in the same room publishing the same sensor type will overwrite each other; disambiguation happens in the payload (device_id field).

---

## Schema Validation

Every payload published to these topics **must** conform to the JSON Schema defined in [contracts/payload.schema.json](payload.schema.json).

See [contracts/payload-examples/](payload-examples/) for valid and invalid examples.

---

## Backward Compatibility & Versioning

**Current version**: 1.0 (no schema prefix in topic).

If schema changes are incompatible, future versions may use prefixed topics:
- `v2/campus/...` — hypothetical version 2 (not deployed yet)

**Deprecation path** (if needed):
1. Introduce `v2/campus/...` topics alongside `campus/...`
2. Devices gradually migrate to v2
3. Once all devices are v2, stop publishing to `campus/...`
4. Give 6-month notice before deleting v1 topics

---

## Related Documents

- [payload.schema.json](payload.schema.json) — JSON Schema for payloads on these topics
- [payload-examples/](payload-examples/) — Valid and invalid example payloads
- [../docs/adr/0001-mqtt-topic-taxonomy.md](../docs/adr/0001-mqtt-topic-taxonomy.md) — Design rationale
- [../README.md](../README.md) — Architecture overview
