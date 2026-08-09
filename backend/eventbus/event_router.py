from typing import Dict, Any
from backend.eventbus.contracts import BaseEvent
from backend.eventbus.kafka_bus import kafka_bus
from backend.eventbus.redis_streams_bus import redis_streams_bus

class DistributedEventRouter:
    """Event Router dispatching typed events across Kafka and Redis Streams."""

    @staticmethod
    def dispatch_event(topic: str, event: BaseEvent) -> bool:
        """Route event to active event bus."""
        return kafka_bus.publish(topic, event)

event_router = DistributedEventRouter()
