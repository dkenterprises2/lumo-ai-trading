import os

class SharedServiceConfig:
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "shared-service")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

shared_config = SharedServiceConfig()
