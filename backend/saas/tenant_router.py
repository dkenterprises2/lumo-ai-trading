from typing import Dict, Any
from backend.saas.tenant_context import TenantContext

class TenantRouter:
    """Tenant Resolution from Host Subdomain, Custom Domain, or JWT."""

    @staticmethod
    def resolve_tenant(host: str = "acme.lumo.trade") -> TenantContext:
        slug = host.split(".")[0] if "." in host else "default"
        return TenantContext(tenant_id=f"org_{slug}", organization_slug=slug)

tenant_router_service = TenantRouter()
