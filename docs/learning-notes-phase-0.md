# Phase 0 Learning Notes (Foundations)

## Summary (3-5 Sentences)
I learned that Pillar 1 is the edge layer responsible for turning physical sensor readings into a reliable message stream the rest of the system can consume. MQTT is a better fit than request/response APIs for this use case because it decouples publishers and subscribers, reduces overhead, and supports unreliable links through QoS and session features. I now understand that topic structure and payload schema are architectural contracts, not implementation details, and they must be stable before firmware work begins. I also learned why UTC timestamps and stable device IDs are mandatory for downstream analytics quality. Finally, I understand that ADRs and C4 diagrams are not paperwork; they are technical controls that prevent accidental architecture drift.

## Concepts Reviewed

### OSI/TCP-IP Basics
- TCP provides ordered, reliable delivery over sockets.
- Ports identify services on a host (MQTT typically 1883, TLS MQTT 8883).
- TLS adds confidentiality/integrity/authentication above TCP.

### Publish/Subscribe Pattern
- Producers publish events without knowing consumers.
- Consumers subscribe to filters, not specific producers.
- A broker enables fan-out and loose coupling.

### MQTT 3.1.1 vs MQTT 5.0
- MQTT 5.0 adds richer metadata (properties), reason codes, and better diagnostics.
- MQTT 3.1.1 is simpler and still widely interoperable.
- For this semester scope, 3.1.1-compatible design remains practical while keeping migration options open.

### JSON Schema
- Encodes payload contracts as machine-verifiable rules.
- Supports required fields, types, enums, ranges, and pattern constraints.
- Enables early validation in simulators, firmware tests, and ingestion boundaries.

### C4 Model
- Context view (C1) defines system boundary and external actors/systems.
- Prevents mixing implementation detail into high-level architecture discussions.
- Provides a shared mental model across all pillars.

### ADRs
- Record decisions at the time they are made.
- Capture alternatives and tradeoffs, not just outcomes.
- Improve review quality and future maintainability.

## Self-Check Answers

### Why is MQTT pub/sub a better fit than REST for streaming sensor data to multiple consumers?
MQTT pub/sub lets devices send once to a broker while multiple downstream systems consume independently, so producers and consumers stay decoupled and can evolve separately. It also reduces message overhead compared to repeated REST calls, which matters for constrained or unstable edge networks. QoS and retained/LWT features provide delivery and state semantics that REST does not offer natively for continuous telemetry.

### What do + and # mean in MQTT topics?
`+` matches exactly one topic level, while `#` matches the rest of the hierarchy from that point onward.

### What does LWT give us operationally?
It lets the broker publish an offline status if a device drops unexpectedly, which enables accurate device health monitoring without polling.
