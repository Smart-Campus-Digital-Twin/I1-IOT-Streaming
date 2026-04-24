# Smart Campus Digital Twin

A real-time IoT data pipeline simulating a university campus — 160 sensors across 4 buildings streaming through MQTT → Kafka → InfluxDB + PostgreSQL, with live anomaly detection, alert suppression, and Redis-backed analytics.

---

## Architecture

```
[Simulator]  160 sensors, 5s interval, local timezone schedule
     │  MQTT (authenticated, QoS-1)
     ▼
[Mosquitto]  broker, username/password auth
     │  campus/#
     ▼
[Bridge]  schema validation (pydantic) → forward
     │  sensors.{type}  Kafka topics
     ▼
[Kafka]  3 partitions per topic, 7-day retention
     │
     ├──────────────────────────┐
     ▼                          ▼
[Processor]               [Analytics]
 batch Kafka commits        Z-score + threshold detection
 InfluxDB (time-series)     alert suppression (5-min cooldown)
 PostgreSQL (registry)      Redis window checkpointing
     │                          │
     ▼                          ▼
[InfluxDB]              [alerts.anomaly / alerts.threshold]
[PostgreSQL]
[Redis]

[Prometheus]  scrape-ready (targets in infra/prometheus/prometheus.yml)
[Grafana]     InfluxDB + Prometheus datasources pre-provisioned
```

**Buildings:** Academic A · Administrative B · Research C · Canteen D
**Sensors per room:** temperature, humidity, pressure, vibration, occupancy (subset by room type)

---

## Quick Start

```bash
# 1. Copy environment config
cp .env.example .env          # edit passwords if needed

# 2. Start everything (builds images on first run)
make up

# 3. Check all containers are healthy
make ps

# 4. Watch live logs
make logs                     # all services
make logs-sim                 # simulator only
make logs-bridge              # bridge only
make logs-processor           # processor only
make logs-analytics           # analytics only
```

---

## Container Commands

| Action | Command |
|---|---|
| Start all | `make up` |
| Stop (keep data) | `make down` |
| Stop + wipe all data | `make clean` |
| Restart all | `make restart` |
| Restart one service | `docker compose restart simulator` |
| Rebuild one service | `docker compose up -d --build simulator` |
| Full no-cache rebuild | `make build && make up` |
| Stop one service | `docker compose stop analytics` |

---

## UI Access

### Grafana — Dashboards
```
http://localhost:3000
Username: admin
Password: admin2026   (set via GRAFANA_PASSWORD in .env)
```
Pre-provisioned datasources: **InfluxDB** (default) and **Prometheus**.

**Create your first panel:**
1. `+` → New Dashboard → Add visualization → select **InfluxDB**
2. Switch to **Code** mode, paste a Flux query (examples below)
3. Set viz type to **Time series** → Save

```flux
// Occupancy across all classrooms — last 1 hour
from(bucket: "sensors")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "occupancy")
  |> filter(fn: (r) => r._field == "value")
  |> filter(fn: (r) => r.building_id == "building-a")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
```

```flux
// Average temperature per building — last 30 min
from(bucket: "sensors")
  |> range(start: -30m)
  |> filter(fn: (r) => r._measurement == "temperature")
  |> filter(fn: (r) => r._field == "value")
  |> group(columns: ["building_id"])
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```

---

### InfluxDB — Data Explorer
```
http://localhost:8086
Username: admin
Password: adminpassword123   (set via INFLUXDB_PASSWORD in .env)
Org:      smart-campus
Bucket:   sensors
```
Go to **Data Explorer** → select `_measurement` (e.g. `occupancy`) → select `_field` = `value` → Submit.

Add optional tag filters: `building_id`, `floor`, `room_id`, `sensor_id`.

---

### Prometheus — Metrics
```
http://localhost:9090
```
- **Status → Targets** — shows all configured scrape targets
- Currently scraping itself; Python service metrics are ready to enable — uncomment targets in [infra/prometheus/prometheus.yml](infra/prometheus/prometheus.yml) and add `prometheus-client` to service requirements

---

### PostgreSQL — Metadata & Registry
```
Host:     localhost
Port:     5433
Database: campus_metadata
Username: campus_user
Password: campus_password
```

```bash
# Open psql shell
make psql

# Live sensor registry (last seen)
make pg-sensors

# Recent alerts
make pg-alerts
```

---

### Redis — Analytics Window State
```
Host: localhost   Port: 6379
Password: redis-secret-2026   (set via REDIS_PASSWORD in .env)
```

```bash
# Open redis-cli
docker exec -it campus-redis redis-cli -a redis-secret-2026

# Count checkpointed sensor windows
DBSIZE

# Inspect one sensor's Z-score window
HGETALL campus:anomaly:building-a-f1-r01-temperature
# Returns: n (samples), mean, M2 (variance accumulator)
```

---

### Kafka — Message Inspection
```
Bootstrap: localhost:9092
```

```bash
# List all topics
make kafka-topics

# Stream live temperature readings
make kafka-tail-temp

# Stream threshold alerts
make kafka-tail-alerts

# Check consumer group lag (how far behind is the processor?)
docker exec campus-kafka /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group campus-processor
```

**Topics:**

| Topic | Description |
|---|---|
| `sensors.temperature` | Raw temperature readings |
| `sensors.humidity` | Raw humidity readings |
| `sensors.pressure` | Raw pressure readings |
| `sensors.vibration` | Raw vibration readings |
| `sensors.occupancy` | Raw occupancy counts |
| `alerts.anomaly` | Z-score anomaly events |
| `alerts.threshold` | Rule-based threshold breaches |

---

## Project Structure

```
smart-campus-digital-twin/
├── shared/                   # Models, logging — imported by all services
├── simulator/
│   ├── campus/               # Building + room topology (4 buildings, 42 rooms, 160 sensors)
│   └── sensors/              # temperature, humidity, pressure, vibration, occupancy
├── ingestion/                # MQTT → Kafka bridge + pydantic schema validation
├── processor/
│   └── writers/              # InfluxDB writer (batched retry) + PostgreSQL writer (cached upserts)
├── analytics/
│   ├── detectors/            # Z-score anomaly + threshold rule detectors
│   └── suppressors/          # Alert deduplication (5-min cooldown)
├── infra/
│   ├── mosquitto/            # mosquitto.conf + passwd (hashed credentials)
│   ├── postgres/             # init.sql schema + seed data
│   ├── prometheus/           # prometheus.yml scrape config
│   └── grafana/              # Datasource provisioning (InfluxDB + Prometheus)
├── docker-compose.yml
├── Makefile
└── .env
```


