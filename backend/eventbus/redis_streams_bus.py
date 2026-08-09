from typing import Dict, Any, Callable, List
from backend.eventbus.base import EventBusInterface
from backend.eventbus.contracts import BaseEvent

class RedisStreamsEventBus(EventBusInterface):
    """Redis Streams Message Bus Fallback Implementation."""

    def __init__(self):
        self._streams: Dict[str, List[Dict[str, Any]]] = {}
        self._handlers: Dict[str, List[Callable]] = {}

    def publish(self, topic: str, event: BaseEvent) -> bool:
        if topic not in self._streams:
            self._streams[topic] = []
        payload = event.model_dump()
        self._streams[topic].append(payload)
        
        if topic in self._handlers:
            for handler in self._handlers[topic]:
                handler(payload)
        return True

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        if topic not in self._handlers:
            self._handlers[topic] = []
        self._handlers[topic].append(handler)
        return True

redis_streams_bus = RedisStreamsEventBus()
