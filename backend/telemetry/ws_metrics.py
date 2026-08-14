import time
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class WSConnectionMetrics:
    connected_clients: int
    heartbeat_ok: bool
    last_broadcast_ms: float
    stream_uptime_seconds: float
    total_messages_broadcast: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class WSMetricsManager:
    """Tracks WebSocket connection health and broadcast metrics."""

    def __init__(self):
        self.start_time = time.time()
        self.connected_clients = 0
        self.last_broadcast_timestamp = time.time()
        self.total_messages_broadcast = 0
        self.heartbeat_interval_seconds = 15.0
        self.last_heartbeat_timestamp = time.time()

    def register_client(self):
        self.connected_clients += 1

    def unregister_client(self):
        self.connected_clients = max(0, self.connected_clients - 1)

    def record_broadcast(self, broadcast_duration_ms: float = 5.0):
        self.last_broadcast_timestamp = time.time()
        self.total_messages_broadcast += 1

    def record_heartbeat(self):
        self.last_heartbeat_timestamp = time.time()

    def get_metrics(self) -> WSConnectionMetrics:
        now = time.time()
        uptime = now - self.start_time
        since_heartbeat = now - self.last_heartbeat_timestamp
        last_b_ms = round((now - self.last_broadcast_timestamp) * 1000.0, 2)

        return WSConnectionMetrics(
            connected_clients=self.connected_clients,
            heartbeat_ok=since_heartbeat <= (self.heartbeat_interval_seconds * 2.5),
            last_broadcast_ms=last_b_ms,
            stream_uptime_seconds=round(uptime, 2),
            total_messages_broadcast=self.total_messages_broadcast
        )

# Global Singleton
ws_metrics = WSMetricsManager()
