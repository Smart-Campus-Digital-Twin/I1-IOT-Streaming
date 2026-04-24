-- Smart Campus Digital Twin — PostgreSQL schema

CREATE TABLE IF NOT EXISTS buildings (
    building_id   TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    address       TEXT,
    floors        INT  NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id      TEXT PRIMARY KEY,
    building_id  TEXT NOT NULL REFERENCES buildings(building_id),
    floor        INT  NOT NULL,
    room_type    TEXT NOT NULL,  -- classroom | office | lab | server_room | corridor | canteen
    capacity     INT  NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id    TEXT PRIMARY KEY,
    room_id      TEXT NOT NULL,
    building_id  TEXT NOT NULL,
    floor        INT  NOT NULL,
    sensor_type  TEXT NOT NULL,
    unit         TEXT NOT NULL,
    is_active    BOOLEAN DEFAULT TRUE,
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS alert_events (
    id           BIGSERIAL PRIMARY KEY,
    alert_id     TEXT UNIQUE NOT NULL,
    sensor_id    TEXT NOT NULL,
    building_id  TEXT NOT NULL,
    floor        INT  NOT NULL,
    room_id      TEXT NOT NULL,
    sensor_type  TEXT NOT NULL,
    alert_type   TEXT NOT NULL,
    severity     TEXT NOT NULL,
    value        DOUBLE PRECISION NOT NULL,
    threshold    DOUBLE PRECISION,
    message      TEXT NOT NULL,
    timestamp_ms BIGINT NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensor_hourly_stats (
    id           BIGSERIAL PRIMARY KEY,
    sensor_id    TEXT NOT NULL,
    building_id  TEXT NOT NULL,
    floor        INT  NOT NULL,
    room_id      TEXT NOT NULL,
    sensor_type  TEXT NOT NULL,
    hour_bucket  TIMESTAMPTZ NOT NULL,
    avg_value    DOUBLE PRECISION,
    min_value    DOUBLE PRECISION,
    max_value    DOUBLE PRECISION,
    stddev_value DOUBLE PRECISION,
    sample_count INT,
    UNIQUE (sensor_id, hour_bucket)
);

CREATE INDEX IF NOT EXISTS idx_alerts_sensor_id       ON alert_events(sensor_id);
CREATE INDEX IF NOT EXISTS idx_alerts_building_id     ON alert_events(building_id);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp_ms    ON alert_events(timestamp_ms DESC);
CREATE INDEX IF NOT EXISTS idx_stats_sensor_hour      ON sensor_hourly_stats(sensor_id, hour_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_sensors_building       ON sensors(building_id);

-- Seed campus topology
INSERT INTO buildings VALUES
    ('building-a', 'Academic Block A', '1 University Ave', 3, NOW()),
    ('building-b', 'Administrative Block B', '2 University Ave', 3, NOW()),
    ('building-c', 'Research & Facilities Block C', '3 University Ave', 2, NOW()),
    ('building-d', 'Student Canteen', '4 University Ave', 1, NOW())
ON CONFLICT DO NOTHING;
