import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AnalyticsConfig:
    kafka_bootstrap_servers: str   = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_group_id:          str   = os.getenv("KAFKA_ANALYTICS_GROUP_ID", "campus-analytics")
    kafka_auto_offset_reset: str   = os.getenv("KAFKA_AUTO_OFFSET_RESET", "latest")

    z_score_threshold:  float = float(os.getenv("Z_SCORE_THRESHOLD", "3.5"))
    alert_cooldown_s:   int   = int(os.getenv("ALERT_COOLDOWN_S", "300"))

    redis_host:     str = os.getenv("REDIS_HOST", "redis")
    redis_port:     int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")

    postgres_host:     str = os.getenv("POSTGRES_HOST",     "postgres")
    postgres_port:     int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db:       str = os.getenv("POSTGRES_DB",       "campus_metadata")
    postgres_user:     str = os.getenv("POSTGRES_USER",     "campus_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "campus_password")

    log_level: str = os.getenv("LOG_LEVEL", "INFO")


config = AnalyticsConfig()
