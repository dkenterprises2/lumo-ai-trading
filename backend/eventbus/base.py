from abc import ABC, abstractmethod
from typing import Dict, Any, Callable
from backend.eventbus.contracts import BaseEvent

class EventBusInterface(ABC):
    """Abstract Base Class for Event Bus Implementations (Kafka / NATS / Redis Streams)."""

    @abstractmethod
    def publish(self, topic: str, event: BaseEvent) -> bool:
        pass

    @abstractmethod
    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> bool:
        pass
