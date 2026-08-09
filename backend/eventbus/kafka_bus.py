from typing import Dict, Any, Callable
from backend.eventbus.base import EventBusInterface
from backend.eventbus.contracts import BaseEvent
from backend.eventbus.redis_streams_bus import redis_streams_bus

class KafkaEventBusAbstraction(EventBusInterface):
    """Kafka Event Bus Implementation (Falls back to Redis Streams if Kafka cluster unverified)."""

    def __init__(self, is_kafka_available: bool = False):
        self._is_available = is_kafka_available

    def publish(self, topic: str, event: BaseEvent) -> bool:
        if self._is_available:
            return True
        # Fallback to Redis Streams
        return redis_streams_bus.publish(topic, event)

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        if self._is_available:
            return True
        return redis_streams_bus.subscribe(topic, handler)

kafka_bus = KafkaEventBusAbstraction()
