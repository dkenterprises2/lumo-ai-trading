from typing import Dict, Any, Set

class DistributedWebSocketConnectionRegistry:
    """Registry tracking active WebSocket connections per tenant channel across gateway nodes."""

    def __init__(self):
        self._channels: Dict[str, Set[str]] = {}

    def register_connection(self, tenant_id: str, connection_id: str):
        channel = f"tenant:{tenant_id}"
        if channel not in self._channels:
            self._channels[channel] = set()
        self._channels[channel].add(connection_id)

    def unregister_connection(self, tenant_id: str, connection_id: str):
        channel = f"tenant:{tenant_id}"
        if channel in self._channels and connection_id in self._channels[channel]:
            self._channels[channel].remove(connection_id)

    def get_channel_connections(self, tenant_id: str) -> Set[str]:
        return self._channels.get(f"tenant:{tenant_id}", set())

connection_registry = DistributedWebSocketConnectionRegistry()
