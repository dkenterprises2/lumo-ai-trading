from typing import Dict, Any
from services.websocket-gateway.connection_registry import connection_registry
from services.websocket-gateway.pubsub_bridge import pubsub_bridge

class DistributedWebSocketGateway:
    """Horizontally Scalable Distributed WebSocket Gateway Service."""

    def handle_connect(self, tenant_id: str, conn_id: str):
        connection_registry.register_connection(tenant_id, conn_id)

    def handle_disconnect(self, tenant_id: str, conn_id: str):
        connection_registry.unregister_connection(tenant_id, conn_id)

    def broadcast_event(self, tenant_id: str, event_data: Dict[str, Any]):
        pubsub_bridge.broadcast_to_tenant(tenant_id, event_data)

websocket_gateway = DistributedWebSocketGateway()
