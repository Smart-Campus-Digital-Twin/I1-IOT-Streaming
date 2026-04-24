import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class IngestionConfig:
    mqtt_host:            str = os.getenv("MQTT_HOST", "localhost")
    mqtt_port:            int = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_keepalive:       int = int(os.getenv("MQTT_KEEPALIVE", "60"))
    mqtt_subscribe_topic: str = os.getenv("MQTT_SUBSCRIBE_TOPIC", "campus/#")
    mqtt_username:        str = os.getenv("MQTT_USERNAME", "")
    mqtt_password:        str = os.getenv("MQTT_PASSWORD", "")

    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_acks:              str = os.getenv("KAFKA_ACKS", "1")

    log_level: str = os.getenv("LOG_LEVEL", "INFO")


config = IngestionConfig()
