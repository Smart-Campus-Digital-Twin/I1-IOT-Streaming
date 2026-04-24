import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ProcessorConfig:
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_group_id:          str = os.getenv("KAFKA_PROCESSOR_GROUP_ID", "campus-processor")
    kafka_auto_offset_reset: str = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")

    influxdb_url:    str = os.getenv("INFLUXDB_URL",    "http://localhost:8086")
    influxdb_token:  str = os.getenv("INFLUXDB_TOKEN",  "my-super-secret-token")
    influxdb_org:    str = os.getenv("INFLUXDB_ORG",    "smart-campus")
    influxdb_bucket: str = os.getenv("INFLUXDB_BUCKET", "sensors")
    influxdb_batch_size: int = int(os.getenv("INFLUXDB_BATCH_SIZE", "200"))
    influxdb_flush_interval_ms: int = int(os.getenv("INFLUXDB_FLUSH_INTERVAL_MS", "1000"))

    postgres_host:     str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port:     int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db:       str = os.getenv("POSTGRES_DB",   "campus_metadata")
    postgres_user:     str = os.getenv("POSTGRES_USER", "campus_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "campus_password")

    log_level: str = os.getenv("LOG_LEVEL", "INFO")


config = ProcessorConfig()
