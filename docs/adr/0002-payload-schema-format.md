# ADR 0002: Payload Schema Format (JSON vs Protobuf)

**Status**: Accepted  
**Date**: May 3, 2026  
**Decider**: Buwaneka (Pillar 1 Lead)  
**Consulted**: None (internal design decision)  

---

## Context

Pillar 1 publishes sensor readings over MQTT. The payload format must be:
- **Parseable by ESP32 firmware** (limited RAM, no heavy libraries).
- **Validatable by ingestion bridge** (Pillar 2 entry point).
- **Language-agnostic** (future: mobile apps, third-party integrations).
- **Versionable** (schema changes without breaking existing devices).
- **Debuggable** (human-readable for troubleshooting).

The two leading candidates are **JSON** and **Protocol Buffers (Protobuf)**.

---

## Options Considered

### Option 1: JSON (Chosen)

**Schema language**: JSON Schema (Draft 2020-12)  
**Example payload**:
```json
{
  "sensor_id": "building-a-f1-r01-temperature",
  "building_id": "building-a",
  "floor": 1,
  "room_id": "building-a-f1-r01",
  "sensor_type": "temperature",
  "value": 22.5,
  "unit": "celsius",
  "timestamp_ms": 1746360000000,
  "quality": 1.0
}
```

**Pros:**
- **Human-readable**: Easy to debug, log, and understand.
- **Language-agnostic**: JSON parsers exist in every language (Python, C++, JavaScript, Arduino libraries).
- **Schema is text, not compiled**: JSON Schema is committed to git; no build step needed.
- **Widely supported on ESP32**: `ArduinoJson` library is popular, lightweight (< 50 KB).
- **Additive evolution**: New optional fields don't break old firmware (forward-compatible).
- **No code generation**: Field names are strings; no need to regenerate code on schema change.

**Cons:**
- **Larger payload size** than Protobuf (~200 bytes per reading vs ~80 bytes).
- **No strict type enforcement** in transit (validation must happen in code).
- **No built-in compression** (though MQTT itself can compress).

### Option 2: Protocol Buffers (Protobuf)

**Schema language**: `.proto` definition files  
**Example** (simplified):
```protobuf
message SensorReading {
  string sensor_id = 1;
  string building_id = 2;
  int32 floor = 3;
  string room_id = 4;
  string sensor_type = 5;
  float value = 6;
  string unit = 7;
  int64 timestamp_ms = 8;
  float quality = 9;
}
```

**Pros:**
- **Compact binary encoding**: ~80 bytes per reading (60% smaller than JSON).
- **Type safety**: Field types are enforced at schema level.
- **Fast parsing**: Binary format is faster to serialize/deserialize.
- **Mature tooling**: Code generation for many languages.

**Cons:**
- **Requires code generation**: `.proto` → generated code in every language.
- **Not human-readable**: Binary payloads are opaque (hard to debug in MQTT explorer).
- **Steeper learning curve**: Protobuf versioning rules are complex.
- **Extra build step**: Must regenerate code when schema changes, then rebuild firmware.
- **Limited ESP32 adoption**: `nanopb` is the main library, less widely used than ArduinoJson.
- **Breaking changes are easy**: If field semantics change, old clients silently misparsed data.

### Option 3: MessagePack

**Pros**: Compact, faster than JSON.  
**Cons**: Less widely supported on constrained devices; less human-readable than JSON.  
**Verdict**: Rejected (middle ground with downsides of both).

---

## Decision

**Chosen: Option 1 (JSON)**

**Rationale:**

1. **Firmware development velocity**: Developers can use `ArduinoJson`, serialize a struct, and publish in ~10 lines of code. No code generation.
2. **Debugging**: MQTT Explorer, Grafana, and logs show human-readable payloads immediately. A firmware crash can be diagnosed by looking at the last message.
3. **Evolution without fragility**: Adding `metadata: { firmware_version: "1.2.3" }` to payloads is trivial; old ingestion code ignores it.
4. **This is a campus system, not a high-frequency system**: 160 devices × 5-second interval = 32 messages/sec. Bandwidth is not a constraint; JSON's ~200-byte payloads are negligible.
5. **Protobuf's gains are premature optimization**: Even if payloads were 60% larger, the campus LAN bandwidth is orders of magnitude higher than needed.

---

## Consequences

### Positive
- **Rapid iteration**: Firmware can be updated without rebuilding the entire schema pipeline.
- **Transparent operation**: All data in the system is human-readable until final storage (InfluxDB).
- **Easier debugging**: Payload validation errors are clear (e.g., "value out of range").

### Negative
- **Larger messages** (but negligible at this scale).
- **Validation must happen in code** (Pydantic on the bridge, not schema-enforced by transport).

---

## Migration Path (If Needed)

If bandwidth or latency becomes a bottleneck:

1. **Phase X: Add Protobuf alongside JSON**
   - Introduce new topics: `v2/campus/...` with Protobuf payloads.
   - Devices gradually publish to v2 topics.
   - Ingestion bridge deserializes both v1 (JSON) and v2 (Protobuf).

2. **Phase Y: Deprecate JSON**
   - Stop accepting v1 topics (6-month notice).
   - All devices must publish to v2.

3. **Phase Z: Remove v1 support**
   - Sunset the old code path.

---

## Validation

All JSON payloads MUST validate against [contracts/payload.schema.json](../../contracts/payload.schema.json).

Tools:
- **Python**: `jsonschema` library
- **Node.js**: `ajv` library
- **Online**: [json-schema.org validator](https://www.jsonschemavalidator.net/)

---

## Related Decisions

- ADR 0001: Topic taxonomy (location-based MQTT topics).
- Schema: [contracts/payload.schema.json](../../contracts/payload.schema.json)

---

## Revision History

| Date | Status | Notes |
| --- | --- | --- |
| May 3, 2026 | Accepted | Initial decision for v1 |
