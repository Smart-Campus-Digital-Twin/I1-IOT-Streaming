# ADR 0001: MQTT Topic Taxonomy

**Status**: Accepted  
**Date**: May 3, 2026  
**Decider**: Buwaneka (Pillar 1 Lead)  
**Consulted**: None (internal design decision)  

---

## Context

Pillar 1 will publish sensor data from ~160 devices across 4 buildings via MQTT. Without a well-designed topic hierarchy, the downstream system (Pillar 2, Pillar 3) will struggle to subscribe to the right data, and device firmware will be hard to scale or modify.

**Constraints:**
- MQTT brokers match subscriptions via hierarchical topic strings with wildcards (`+`, `#`).
- Topic structure must be intuitive for humans and unambiguous for machines.
- Room and building IDs must be stable over time (no renumbering).
- Device hardware may change (new sensors, new devices in same room), but topic structure should remain unchanged.

---

## Options Considered

### Option 1: Device-Centric Topics
**Topic structure**: `device/{device_id}/sensors/{sensor_type}`

**Pros:**
- Simple per-device subscription: `device/esp32-001/#`

**Cons:**
- Device IDs are hardware-specific; if a device fails, its topics become orphaned.
- Hard to answer "what are all temperatures in building A?" — would require subscribing to every device in building A.
- Scales poorly: 5,000 devices = 5,000 device subtrees to manage.

### Option 2: Sensor-Centric Topics (Chosen)
**Topic structure**: `campus/{building}/{floor}/{room}/{sensor_type}`

**Pros:**
- Logical grouping by physical location (building → floor → room).
- Wildcards are natural: `campus/building-a/#` = all sensors in building A.
- Easy to subscribe to all measurements of one type: `campus/+/+/+/temperature`.
- Room/building structure is stable; if a device fails, another can take its place.
- Scales well: new buildings/devices only add leaves to the tree, never restructure branches.

**Cons:**
- Multiple devices in the same room publishing the same sensor type will overwrite each other in a naive MQTT client.
- (Mitigation: device ID is in the payload; the bridge/ingestion layer handles disambiguation.)

### Option 3: Hybrid (Device ID in Topic)
**Topic structure**: `campus/{building}/{floor}/{room}/{sensor_type}/{device_id}`

**Pros:**
- No ambiguity; every message is attributed to a specific device.
- Allows subscribing to a specific device: `campus/+/+/+/+/esp32-001/#`.

**Cons:**
- Topic names become very long (8+ levels).
- Overkill for most use cases (analytics doesn't care which device, only the value and timestamp).
- Harder for simple MQTT clients to use (longer patterns to remember).

---

## Decision

**Chosen: Option 2 (Sensor-Centric, Location-Based)**

**Topic structure:**
```
campus/{building_id}/floor{floor}/{room_id}/{sensor_type}
```

**Examples:**
- `campus/building-a/floor1/building-a-f1-r01/temperature`
- `campus/building-d/floor1/building-d-f1-r01/occupancy`

---

## Rationale

1. **Location-first aligns with the campus model.** Analytics naturally groups data by building and room; topic hierarchy should match.
2. **Stable room IDs prevent orphaned data.** If device A fails, device B can publish to the same topic. The room stays meaningful.
3. **Wildcards are intuitive.** "All sensors in building A" is `campus/building-a/#`, not a complex filter.
4. **Scalability.** The topology grows by adding rooms and buildings (tree extension), not by managing per-device namespaces.
5. **Payload contains device_id.** Downstream systems that care about device-level traceability read the `device_id` field in the JSON; topic alone is not the authority.

---

## Consequences

### Positive
- Clear, predictable topic names for firmware developers.
- Easy to set up firewall rules, ACLs, and monitoring by building/room/sensor.
- Aligns with the Smart Campus domain (students/staff think in terms of "Room 204", not "Device ABC").

### Negative
- Multiple devices in the same room publishing the same sensor type will collide at the topic level.
  - **Mitigation**: Ingestion layer subscribes to all rooms/sensors; bridges to Kafka with device_id as a key for deduplication.
- Devices cannot subscribe to only their own topic for bidirectional control (e.g., downlink commands).
  - **Mitigation**: If downlink is needed (Phase X), introduce a separate `commands/{device_id}` topic tree.

---

## Related Decisions

- ADR 0002: Payload schema format (JSON vs Protobuf).
- Topic taxonomy specification: [contracts/topic-taxonomy.md](../../contracts/topic-taxonomy.md)

---

## Revision History

| Date | Status | Notes |
| --- | --- | --- |
| May 3, 2026 | Accepted | Initial design for v1 |
