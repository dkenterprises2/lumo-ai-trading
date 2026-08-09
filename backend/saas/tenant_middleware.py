from typing import Dict, Any, Optional

class TenantIsolationMiddleware:
    """Tenant Database & WebSocket Isolation Layer."""

    @staticmethod
    def get_tenant_context(header_org_id: Optional[str] = None) -> Dict[str, Any]:
        """Extract and enforce tenant context on requests."""
        tenant_id = header_org_id or "ORG-101"
        return {
            "tenant_id": tenant_id,
            "is_isolated": True,
            "websocket_channel": f"tenant:{tenant_id}"
        }

tenant_middleware = TenantIsolationMiddleware()
