# Pillar 1 Glossary (Phase 0)

This glossary defines the core terms used in the Smart Campus Digital Twin Pillar 1 (IoT/Edge) scope.

## IoT (Internet of Things)
A system where physical devices (sensors, controllers, meters, etc.) collect data from the real world and exchange it over networks so software can monitor, analyze, and act on it.

## Digital Twin
A digital representation of a physical environment that stays useful by continuously receiving real-world telemetry. In this project, the campus twin is fed by live sensor streams.

## Sensor
A hardware component that measures a physical quantity (for example temperature, humidity, vibration, or occupancy) and outputs a value that firmware can read.

## Microcontroller
A small embedded computer (CPU, memory, and peripherals on one chip) designed for control tasks. It runs firmware and interacts directly with sensors and network modules.

## Firmware
The software programmed into a microcontroller. It handles sensor reads, time sync, network reconnect logic, payload creation, and MQTT publish behavior.

## Edge
The device-side or near-device compute layer where data is produced and first processed. In Pillar 1, ESP32 devices and local broker-side handling are edge concerns.

## Cloud / Platform Side
The central services that consume and process telemetry at scale (Kafka, analytics, storage, dashboards). In this project, Pillars 2-4 are primarily platform-side.

## MQTT
A lightweight publish/subscribe messaging protocol designed for low-bandwidth or unstable networks. Devices send messages to topics via a broker instead of direct client-to-client calls.

## Broker (MQTT Broker)
The MQTT server that receives published messages and forwards them to all matching subscribers. In this project, Mosquitto is the broker.

## Topic
A hierarchical routing key in MQTT (for example `campus/building-a/floor1/building-a-f1-r01/temperature`) used by the broker to decide who receives each message.

## Publisher
A client that sends messages to MQTT topics (for example an ESP32 or simulator publishing telemetry).

## Subscriber
A client that receives messages by subscribing to one or more topic filters (for example ingestion bridge, analytics service, or observability tools).

## Payload
The message body carried by MQTT. Here it is JSON containing telemetry fields such as sensor identity, value, unit, timestamp, and quality.

## Pub/Sub (Publish/Subscribe)
A messaging pattern where producers and consumers are decoupled through a broker and topic filters. Producers do not need to know who consumes their messages.

## QoS 0 (At Most Once)
Best-effort delivery. Message may be lost if the network fails; no retry/ack guarantee.

## QoS 1 (At Least Once)
Broker acknowledges receipt; sender retries until acknowledged. Message can be delivered more than once, so consumers should tolerate duplicates.

## QoS 2 (Exactly Once)
Strongest MQTT delivery guarantee using a multi-step handshake. Highest overhead; usually unnecessary for high-frequency telemetry.

## Last Will and Testament (LWT)
A message registered at connect time that the broker publishes automatically if a client disconnects unexpectedly. Used for offline status signaling.

## Retained Message
A broker-stored last message for a topic. New subscribers immediately receive the retained value (for example current online/offline status).

## TCP
A reliable transport protocol that provides ordered, retransmitted byte streams. MQTT commonly runs over TCP.

## Port
A numeric endpoint on a host that identifies a network service (for example MQTT on 1883, MQTT over TLS on 8883).

## TLS
A cryptographic protocol that encrypts traffic and authenticates peers using certificates. Used to secure MQTT sessions and prevent interception/spoofing.

## JSON Schema
A machine-readable contract for JSON data shape and rules (required fields, data types, enum values, ranges, formats). Used to validate telemetry payloads.

## C4 Model
A diagramming approach that describes software architecture in levels (Context, Container, Component, Code). Phase 0 starts with a level-1 context view.

## ADR (Architecture Decision Record)
A short, versioned document that captures one architecture decision, alternatives considered, rationale, and consequences.

## UTC Timestamp
A time value normalized to Coordinated Universal Time. Using UTC avoids timezone drift and keeps analytics consistent across systems.

## Device ID
A stable, unique identifier assigned to a device independent of MAC address or friendly label. It allows reliable tracking across hardware/network changes.
