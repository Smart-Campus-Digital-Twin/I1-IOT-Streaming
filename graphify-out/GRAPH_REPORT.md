# Graph Report - .  (2026-05-05)

## Corpus Check
- Corpus is ~14,642 words - fits in a single context window. You may not need a graph.

## Summary
- 241 nodes · 310 edges · 26 communities (20 shown, 6 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 24|Community 24]]

## God Nodes (most connected - your core abstractions)
1. `SensorReading` - 15 edges
2. `BaseSensor` - 13 edges
3. `MQTTKafkaBridge` - 10 edges
4. `PostgresWriter` - 10 edges
5. `MQTTPublisher` - 10 edges
6. `ZScoreDetector` - 9 edges
7. `main()` - 8 edges
8. `OccupancySensor` - 8 edges
9. `AlertWriter` - 7 edges
10. `HourlyAggregator` - 7 edges

## Surprising Connections (you probably didn't know these)
- `_Rule` --uses--> `SensorReading`  [INFERRED]
  analytics/detectors/threshold.py → shared/models.py
- `_make_alert()` --calls--> `AlertEvent`  [INFERRED]
  analytics/main.py → shared/models.py
- `_WindowState` --uses--> `SensorReading`  [INFERRED]
  analytics/detectors/anomaly.py → shared/models.py
- `ZScoreDetector` --uses--> `SensorReading`  [INFERRED]
  analytics/detectors/anomaly.py → shared/models.py
- `ThresholdBreach` --uses--> `SensorReading`  [INFERRED]
  analytics/detectors/threshold.py → shared/models.py

## Communities (26 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.0
Nodes (27): campus-analytics scrape job, campus-bridge scrape job, campus-processor scrape job, confluent-kafka, datasources.yaml, InfluxDB, influxdb-client, ingestion requirements (+19 more)

### Community 1 - "Community 1"
Cohesion: 0.0
Nodes (16): ABC, BaseSensor, BaseSensor, Abstract base for all simulated sensors., Public API: generate a SensorReading with the current timestamp., Override to simulate sensor degradation / data-quality flags., _sample(), HumiditySensor (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.0
Nodes (30): ADR, Broker (MQTT Broker), C4 Model, Device ID, Digital Twin, Edge, Firmware, glossary.md (+22 more)

### Community 3 - "Community 3"
Cohesion: 0.0
Nodes (7): BaseModel, _ensure_topics(), main(), MQTTKafkaBridge, MQTT → Kafka bridge.  Subscribes to campus/# on the MQTT broker and forwards e, Lightweight schema guard at the bridge entry point., _SensorPayload

### Community 4 - "Community 4"
Cohesion: 0.0
Nodes (6): from_dict(), Z-score anomaly detector using a per-sensor sliding window.  Window state (n,, Load every persisted window state from Redis on startup., Stateful, per-sensor anomaly detector.      Pass a connected redis.Redis insta, _WindowState, ZScoreDetector

### Community 5 - "Community 5"
Cohesion: 0.0
Nodes (9): _build_consumer(), _build_producer(), main(), _make_alert(), Real-time analytics engine.  Consumes all sensors.* Kafka topics and applies:, AlertSuppressor, Alert suppressor — prevents the analytics engine from flooding downstream consu, In-memory cooldown tracker.      Thread-safe for single-threaded consumers (on (+1 more)

### Community 6 - "Community 6"
Cohesion: 0.0
Nodes (6): _build_sensors(), _context_now(), main(), Simulator entry point.  Builds one sensor object per (room, sensor_type) pair,, MQTTPublisher, Thread-safe MQTT publisher with automatic reconnection.

### Community 7 - "Community 7"
Cohesion: 0.0
Nodes (7): _canteen_target_ratio(), _lecture_target_ratio(), OccupancySensor, Randomly trigger/hold/end an evening gathering (lecture rooms only)., Target occupancy ratio for a classroom/lab at the given hour (weekday)., Target occupancy ratio for the canteen at the given hour (weekday)., Stateful bi-directional door counter.      Maintains a running person count up

### Community 8 - "Community 8"
Cohesion: 0.0
Nodes (5): Building, CampusTopology, _make_room(), Static description of all campus buildings, floors, and rooms., Room

### Community 9 - "Community 9"
Cohesion: 0.0
Nodes (3): _connect(), PostgresWriter, Writes device-registry upserts and alert events to PostgreSQL.  Sensor upserts

### Community 10 - "Community 10"
Cohesion: 0.0
Nodes (3): AlertEvent, from_dict(), from_json()

### Community 11 - "Community 11"
Cohesion: 0.0
Nodes (3): AlertWriter, _connect(), Persists AlertEvent rows to the alert_events PostgreSQL table.  Kept deliberat

### Community 12 - "Community 12"
Cohesion: 0.0
Nodes (4): Rule-based threshold detector.  Each sensor type has a configurable (low, high, _Rule, ThresholdBreach, ThresholdDetector

## Knowledge Gaps
- **37 isolated node(s):** `AnalyticsConfig`, `Real-time analytics engine.  Consumes all sensors.* Kafka topics and applies:`, `Z-score anomaly detector using a per-sensor sliding window.  Window state (n,`, `Stateful, per-sensor anomaly detector.      Pass a connected redis.Redis insta`, `Load every persisted window state from Redis on startup.` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.