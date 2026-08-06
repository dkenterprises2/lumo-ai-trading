import asyncio
import inspect
import time
from typing import Dict, List, Callable, Any, Awaitable
from backend.core.logger import logger
from backend.core.monitoring import metrics_collector


class EventTypes:
    MARKET_TICK = "MARKET_TICK"
    SCAN_COMPLETE = "SCAN_COMPLETE"
    AI_SIGNAL = "AI_SIGNAL"
    RISK_APPROVED = "RISK_APPROVED"
    ORDER_OPENED = "ORDER_OPENED"
    ORDER_CLOSED = "ORDER_CLOSED"
    POSITION_UPDATED = "POSITION_UPDATED"
    PORTFOLIO_UPDATED = "PORTFOLIO_UPDATED"
    WS_BROADCAST = "WS_BROADCAST"

class EventBus:
    """Asynchronous Pub/Sub Event Bus for decoupled module communication."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._init_bus()
        return cls._instance

    def _init_bus(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker_task = None

    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    async def publish(self, event_type: str, data: Dict[str, Any]):
        event = {
            "type": event_type,
            "timestamp": time.time(),
            "data": data
        }
        metrics_collector.increment_events()
        
        # Direct async notification to subscribers
        subscribers = self._subscribers.get(event_type, [])
        for callback in subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)

            except Exception as e:
                logger.error(f"[EVENT_BUS_ERROR] Error handling subscriber callback for {event_type}: {e}")

event_bus = EventBus()
