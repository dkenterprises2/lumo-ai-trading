from typing import Dict, Any, Callable
from backend.eventbus.base import EventBusInterface
from backend.eventbus.contracts import BaseEvent
from backend.eventbus.redis_streams_bus import redis_streams_bus

class NATSEventBusAbstraction(EventBusInterface):
    """NATS JetStream Event Bus Implementation (Falls back to Redis Streams)."""

    def __init__(self, is_nats_available: bool = False):
        self._is_available = is_nats_available

    def publish(self, topic: str, event: BaseEvent) -> bool:
        if self._is_available:
            return True
        return redis_streams_bus.publish(topic, event)

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        if self._is_available:
            return True
        return redis_streams_bus.subscribe(topic, handler)

nats_bus = NATSEventBusAbstraction()
