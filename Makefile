.PHONY: up down build logs restart clean ps influx-query

# ── Lifecycle ──────────────────────────────────────────────────────────────────

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build --no-cache

restart:
	docker compose restart

ps:
	docker compose ps

# ── Logs ───────────────────────────────────────────────────────────────────────

logs:
	docker compose logs -f

logs-sim:
	docker compose logs -f simulator

logs-bridge:
	docker compose logs -f bridge

logs-processor:
	docker compose logs -f processor

logs-analytics:
	docker compose logs -f analytics

# ── InfluxDB ───────────────────────────────────────────────────────────────────

influx-shell:
	docker exec -it campus-influxdb influx

influx-query:
	@docker exec campus-influxdb influx query \
	  --org smart-campus \
	  --token my-super-secret-admin-token \
	  'from(bucket:"sensors") |> range(start:-1h) |> filter(fn:(r)=>r._measurement=="temperature") |> last()'

# ── PostgreSQL ─────────────────────────────────────────────────────────────────

psql:
	docker exec -it campus-postgres psql -U campus_user -d campus_metadata

pg-sensors:
	docker exec -it campus-postgres psql -U campus_user -d campus_metadata \
	  -c "SELECT sensor_id, sensor_type, last_seen_at FROM sensors ORDER BY last_seen_at DESC LIMIT 20;"

pg-alerts:
	docker exec -it campus-postgres psql -U campus_user -d campus_metadata \
	  -c "SELECT alert_type, severity, sensor_type, value, message FROM alert_events ORDER BY timestamp_ms DESC LIMIT 10;"

# ── Kafka ──────────────────────────────────────────────────────────────────────

kafka-topics:
	docker exec campus-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

kafka-tail-temp:
	docker exec campus-kafka /opt/kafka/bin/kafka-console-consumer.sh \
	  --bootstrap-server localhost:9092 \
	  --topic sensors.temperature \
	  --from-beginning --max-messages 5

kafka-tail-alerts:
	docker exec campus-kafka /opt/kafka/bin/kafka-console-consumer.sh \
	  --bootstrap-server localhost:9092 \
	  --topic alerts.threshold \
	  --from-beginning --max-messages 10

# ── Cleanup ────────────────────────────────────────────────────────────────────

clean:
	docker compose down -v --remove-orphans
	docker system prune -f
