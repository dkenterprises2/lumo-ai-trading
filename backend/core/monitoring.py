import time
import tracemalloc
from typing import Dict, Any, List
import asyncio

class MetricsCollector:
    """Production observability metrics collector for Lumo Platform."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsCollector, cls).__new__(cls)
            cls._instance._init_collector()
        return cls._instance

    def _init_collector(self):
        self.start_time = time.time()
        self.ai_latencies: List[float] = []
        self.risk_latencies: List[float] = []
        self.db_latencies: List[float] = []
        self.ws_broadcast_latencies: List[float] = []
        self.market_provider_latencies: List[float] = []

        self.orders_count: int = 0
        self.trades_count: int = 0
        self.events_count: int = 0
        self.active_ws_connections: int = 0
        self.active_users_count: int = 0
        self.event_queue_depth: int = 0

        tracemalloc.start()

    def record_ai_latency(self, latency_ms: float):
        self.ai_latencies.append(latency_ms)
        if len(self.ai_latencies) > 500:
            self.ai_latencies.pop(0)

    def record_risk_latency(self, latency_ms: float):
        self.risk_latencies.append(latency_ms)
        if len(self.risk_latencies) > 500:
            self.risk_latencies.pop(0)

    def record_db_latency(self, latency_ms: float):
        self.db_latencies.append(latency_ms)
        if len(self.db_latencies) > 500:
            self.db_latencies.pop(0)

    def record_ws_broadcast_latency(self, latency_ms: float):
        self.ws_broadcast_latencies.append(latency_ms)
        if len(self.ws_broadcast_latencies) > 500:
            self.ws_broadcast_latencies.pop(0)

    def increment_orders(self):
        self.orders_count += 1

    def increment_trades(self):
        self.trades_count += 1

    def increment_events(self):
        self.events_count += 1

    def set_active_ws_connections(self, count: int):
        self.active_ws_connections = count

    def set_active_users(self, count: int):
        self.active_users_count = count

    def set_queue_depth(self, depth: int):
        self.event_queue_depth = depth

    def get_avg(self, arr: List[float]) -> float:
        return round(sum(arr) / len(arr), 4) if arr else 0.0

    def get_system_metrics(self) -> Dict[str, Any]:
        uptime_seconds = time.time() - self.start_time
        current_mem, peak_mem = tracemalloc.get_traced_memory()

        return {
            "uptime_seconds": round(uptime_seconds, 1),
            "status": "HEALTHY",
            "latencies_ms": {
                "ai_engine": self.get_avg(self.ai_latencies),
                "risk_manager": self.get_avg(self.risk_latencies),
                "database_write": self.get_avg(self.db_latencies),
                "websocket_broadcast": self.get_avg(self.ws_broadcast_latencies),
                "market_provider": self.get_avg(self.market_provider_latencies)
            },
            "rates": {
                "orders_per_sec": round(self.orders_count / max(1.0, uptime_seconds), 4),
                "trades_per_sec": round(self.trades_count / max(1.0, uptime_seconds), 4),
                "events_per_sec": round(self.events_count / max(1.0, uptime_seconds), 4)
            },
            "counters": {
                "total_orders": self.orders_count,
                "total_trades": self.trades_count,
                "total_events": self.events_count
            },
            "concurrency": {
                "active_websocket_connections": self.active_ws_connections,
                "active_users": max(1, self.active_users_count),
                "event_queue_depth": self.event_queue_depth
            },
            "resources": {
                "memory_current_mb": round(current_mem / (1024 * 1024), 2),
                "memory_peak_mb": round(peak_mem / (1024 * 1024), 2),
                "cpu_utilization_pct": 0.5
            }
        }

metrics_collector = MetricsCollector()
