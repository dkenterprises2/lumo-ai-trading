import time
import logging
from typing import Dict, List, Any, Optional
from .runtime_health import runtime_watchdog
from .runtime_supervisor import runtime_supervisor

logger = logging.getLogger("recovery_manager")

class RecoveryManager:
    """Subsystem Failure Isolation, Degradation & Self-Healing Recovery Manager."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RecoveryManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self.failed_exchanges: Dict[str, float] = {}
        self.db_status: str = "HEALTHY"
        self.ws_status: str = "CONNECTED"
        self.ws_reconnect_count: int = 0
        self.recovery_events: List[Dict[str, Any]] = []

    def handle_database_failure(self, exc: Exception) -> Dict[str, Any]:
        """Temporarily isolate database operations and move to DEGRADED state."""
        self.db_status = "DEGRADED"
        runtime_watchdog.record_error("database")
        event = {
            "type": "DATABASE_DEGRADED",
            "reason": str(exc),
            "timestamp": time.time()
        }
        self.recovery_events.append(event)
        return {"status": "degraded", "db_status": "DEGRADED", "new_executions_blocked": True}

    def handle_database_recovery(self) -> Dict[str, Any]:
        """Restore database status to HEALTHY."""
        self.db_status = "HEALTHY"
        runtime_watchdog.heartbeat("database", "HEALTHY")
        event = {
            "type": "DATABASE_RECOVERED",
            "timestamp": time.time()
        }
        self.recovery_events.append(event)
        return {"status": "success", "db_status": "HEALTHY"}

    def handle_ws_disconnect(self, reason: str = "Network Drop") -> Dict[str, Any]:
        """Handle WebSocket drop and trigger safe reconnect / polling fallback."""
        self.ws_status = "DISCONNECTED"
        self.ws_reconnect_count += 1
        runtime_watchdog.record_error("websocket")
        event = {
            "type": "WS_DISCONNECTED",
            "reason": reason,
            "reconnect_attempt": self.ws_reconnect_count,
            "timestamp": time.time()
        }
        self.recovery_events.append(event)
        return {"status": "disconnected", "ws_status": "DISCONNECTED", "fallback": "POLLING_ACTIVE"}

    def handle_ws_reconnect(self) -> Dict[str, Any]:
        """Restore WebSocket status to CONNECTED."""
        self.ws_status = "CONNECTED"
        runtime_watchdog.heartbeat("websocket", "CONNECTED")
        event = {
            "type": "WS_RECONNECTED",
            "timestamp": time.time()
        }
        self.recovery_events.append(event)
        return {"status": "success", "ws_status": "CONNECTED", "reconnect_count": self.ws_reconnect_count}

    def handle_exchange_failure(self, exchange: str, reason: str = "Exchange API Unresponsive") -> Dict[str, Any]:
        """Isolate failed exchange venue."""
        self.failed_exchanges[exchange] = time.time()
        runtime_watchdog.record_error("arbitrage_engine")
        event = {
            "type": "EXCHANGE_FAILED",
            "exchange": exchange,
            "reason": reason,
            "timestamp": time.time()
        }
        self.recovery_events.append(event)
        return {"status": "isolated", "exchange": exchange, "action": "REJECT_NEW_TRADES"}

    def handle_exchange_recovery(self, exchange: str) -> Dict[str, Any]:
        """Restore exchange venue health."""
        if exchange in self.failed_exchanges:
            del self.failed_exchanges[exchange]
        runtime_watchdog.heartbeat("arbitrage_engine", "HEALTHY")
        event = {
            "type": "EXCHANGE_RECOVERED",
            "exchange": exchange,
            "timestamp": time.time()
        }
        self.recovery_events.append(event)
        return {"status": "restored", "exchange": exchange}

    def is_exchange_healthy(self, exchange: str) -> bool:
        return exchange not in self.failed_exchanges

recovery_manager = RecoveryManager()
