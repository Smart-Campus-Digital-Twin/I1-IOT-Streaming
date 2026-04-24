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
    ('building-a', 'Academic Block A',              '1 University Ave', 3, NOW()),
    ('building-b', 'Administrative Block B',        '2 University Ave', 3, NOW()),
    ('building-c', 'Research & Facilities Block C', '3 University Ave', 2, NOW()),
    ('building-d', 'Student Canteen',               '4 University Ave', 1, NOW())
ON CONFLICT DO NOTHING;

-- Seed rooms (mirrors simulator/campus/topology.py — keep in sync)
INSERT INTO rooms (room_id, building_id, floor, room_type, capacity) VALUES
    -- Building A: Academic Block (3 floors × 6 rooms)
    ('building-a-f1-r01','building-a',1,'classroom',40),
    ('building-a-f1-r02','building-a',1,'classroom',40),
    ('building-a-f1-r03','building-a',1,'lab',20),
    ('building-a-f1-r04','building-a',1,'office',10),
    ('building-a-f1-r05','building-a',1,'office',10),
    ('building-a-f1-r06','building-a',1,'corridor',0),
    ('building-a-f2-r01','building-a',2,'classroom',40),
    ('building-a-f2-r02','building-a',2,'classroom',40),
    ('building-a-f2-r03','building-a',2,'lab',20),
    ('building-a-f2-r04','building-a',2,'office',10),
    ('building-a-f2-r05','building-a',2,'office',10),
    ('building-a-f2-r06','building-a',2,'corridor',0),
    ('building-a-f3-r01','building-a',3,'classroom',40),
    ('building-a-f3-r02','building-a',3,'classroom',40),
    ('building-a-f3-r03','building-a',3,'lab',20),
    ('building-a-f3-r04','building-a',3,'office',10),
    ('building-a-f3-r05','building-a',3,'office',10),
    ('building-a-f3-r06','building-a',3,'corridor',0),
    -- Building B: Administrative Block (3 floors × 4 rooms)
    ('building-b-f1-r01','building-b',1,'office',15),
    ('building-b-f1-r02','building-b',1,'office',15),
    ('building-b-f1-r03','building-b',1,'office',20),
    ('building-b-f1-r04','building-b',1,'corridor',0),
    ('building-b-f2-r01','building-b',2,'office',15),
    ('building-b-f2-r02','building-b',2,'office',15),
    ('building-b-f2-r03','building-b',2,'office',20),
    ('building-b-f2-r04','building-b',2,'corridor',0),
    ('building-b-f3-r01','building-b',3,'office',15),
    ('building-b-f3-r02','building-b',3,'office',15),
    ('building-b-f3-r03','building-b',3,'office',20),
    ('building-b-f3-r04','building-b',3,'corridor',0),
    -- Building C: Research & Facilities (2 floors × 5 rooms)
    ('building-c-f1-r01','building-c',1,'lab',15),
    ('building-c-f1-r02','building-c',1,'lab',15),
    ('building-c-f1-r03','building-c',1,'server_room',0),
    ('building-c-f1-r04','building-c',1,'office',10),
    ('building-c-f1-r05','building-c',1,'corridor',0),
    ('building-c-f2-r01','building-c',2,'lab',15),
    ('building-c-f2-r02','building-c',2,'lab',15),
    ('building-c-f2-r03','building-c',2,'server_room',0),
    ('building-c-f2-r04','building-c',2,'office',10),
    ('building-c-f2-r05','building-c',2,'corridor',0),
    -- Building D: Student Canteen (1 floor × 2 rooms)
    ('building-d-f1-r01','building-d',1,'canteen',150),
    ('building-d-f1-r02','building-d',1,'corridor',0)
ON CONFLICT DO NOTHING;
