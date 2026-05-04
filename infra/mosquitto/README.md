# Mosquitto MQTT Broker Setup

## Overview

This directory contains the configuration and documentation for the Eclipse Mosquitto MQTT broker used in the Smart Campus Digital Twin project. Mosquitto is the central message broker for all IoT sensor telemetry and system events.

## Quick Start

### Starting Mosquitto

Mosquitto runs as a Docker container managed by the root `docker-compose.yml`:

```bash
# From the project root
docker-compose up -d mosquitto
```

Verify it's running:
```bash
docker-compose ps mosquitto
```

### Stopping Mosquitto

```bash
docker-compose down mosquitto
```

Or stop the entire stack:
```bash
docker-compose down
```

## Configuration

### `mosquitto.conf`
- **Port 1883:** Standard MQTT port (unencrypted)
- **Port 9001:** WebSocket port (for browser-based clients)
- **Authentication:** Username/password required (see `passwd` below)
- **Persistence:** Enabled (data stored in Docker volume `mosquitto-data`)
- **Log Level:** Informational

### `passwd`
Plain-text password file with format: `username:hashed_password`

To add or modify credentials:
```bash
# From project root, enter the mosquitto container
docker-compose exec mosquitto mosquitto_passwd -c /mosquitto/config/passwd username

# Reload broker to apply changes (no restart needed)
docker-compose exec mosquitto kill -HUP 1
```

## Logs

View real-time broker logs:
```bash
docker-compose logs -f mosquitto
```

Check container status and health:
```bash
docker-compose ps mosquitto
```

Health checks run every 10 seconds (timeout: 5s).

## Resetting State

To completely reset the Mosquitto broker and its data:

```bash
# Remove container and volume
docker-compose down -v mosquitto

# Recreate from scratch
docker-compose up -d mosquitto
```

**Warning:** This removes all persisted messages and subscriptions.

## Testing Connectivity

Use `mosquitto_sub` and `mosquitto_pub` (included in container):

```bash
# Subscribe to all messages
docker-compose exec mosquitto mosquitto_sub -h localhost -p 1883 -u admin -P password -t '#'

# Publish a test message (from another terminal)
docker-compose exec mosquitto mosquitto_pub -h localhost -p 1883 -u admin -P password \
  -t 'campus/test/smoke' -m '{"timestamp":"2026-05-04T00:00:00Z","value":42}'
```

Or run the automated smoke test (see below).

## Smoke Test

The project includes an automated smoke test (`scripts/smoke-test.sh`) that verifies broker connectivity:

```bash
# From project root
bash scripts/smoke-test.sh
```

The script:
1. Starts a subscriber listening to `campus/test/smoke` with a 3-second timeout
2. Publishes a test message
3. Verifies the message was received
4. Returns exit code 0 on success, 1 on failure

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Docker Compose Network (campus-net)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐            ┌─────────────────────┐   │
│  │   Simulator      │   MQTT     │    Mosquitto        │   │
│  │  (publisher)     ├──────────→ │  Port 1883/9001     │   │
│  └──────────────────┘            │  Auth: admin:pwd    │   │
│                                   │  Vol: mosquitto-data│   │
│  ┌──────────────────┐            └─────────┬───────────┘   │
│  │  Ingestion       │   MQTT                │               │
│  │  (subscriber &   ├──────────────────────┘               │
│  │   publisher)     │                                        │
│  └──────────────────┘  ┌─────────────────────┐              │
│                        │  Kafka Bridge       │              │
│  ┌──────────────────┐  │  (reads MQTT,       │              │
│  │  Analytics       │  │   publishes Kafka)  │              │
│  │  (subscriber)    ├──┤                     │              │
│  └──────────────────┘  └──────────┬──────────┘              │
│                                    │                         │
│                          ┌─────────▼──────────┐             │
│                          │  Kafka (KRaft)     │             │
│                          │  Port 9092         │             │
│                          └────────────────────┘             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Environment Variables

Required in `.env`:
- `MQTT_USERNAME=admin`
- `MQTT_PASSWORD=password`

These are referenced in the healthcheck and used by all services.

## Troubleshooting

### Broker won't start
- Check logs: `docker-compose logs mosquitto`
- Verify port 1883 is not already in use: `netstat -an | grep 1883`
- Ensure `mosquitto.conf` syntax is valid

### Authentication fails
- Verify credentials in `passwd` file
- Check `.env` has correct `MQTT_USERNAME` and `MQTT_PASSWORD`
- Reload broker: `docker-compose exec mosquitto kill -HUP 1`

### Smoke test fails
- Ensure Mosquitto is running: `docker-compose ps mosquitto`
- Check network connectivity: `docker-compose exec mosquitto ping kafka`
- Review logs for errors: `docker-compose logs mosquitto`

## Further Reading

- [Eclipse Mosquitto Documentation](https://mosquitto.org/)
- [MQTT Specification](https://mqtt.org/)
- [Project Topic Taxonomy](../../contracts/topic-taxonomy.md)
- [Payload Schema](../../contracts/payload.schema.json)
