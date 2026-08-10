import time
from typing import Dict, Any, List, Optional
from backend.saas.organization_manager import organization_manager

class TenantAdminConsole:
    """Tenant & Organization Administration Console."""

    def suspend_tenant(self, tenant_id: str) -> Dict[str, Any]:
        org = organization_manager.get_organization(tenant_id)
        if org:
            org["status"] = "SUSPENDED"
        return {"status": "SUSPENDED", "tenant_id": tenant_id, "updated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}

    def activate_tenant(self, tenant_id: str) -> Dict[str, Any]:
        org = organization_manager.get_organization(tenant_id)
        if org:
            org["status"] = "ACTIVE"
        return {"status": "ACTIVE", "tenant_id": tenant_id, "updated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}

    def list_users(self) -> List[Dict[str, Any]]:
        return [
            {"user_id": 1, "email": "jiodkd@gmail.com", "role": "SUPER_ADMIN", "tenant_id": "ORG-101", "plan": "ENTERPRISE", "status": "ACTIVE"},
            {"user_id": 2, "email": "trader@alphaquant.com", "role": "TRADER", "tenant_id": "ORG-101", "plan": "PRO", "status": "ACTIVE"},
            {"user_id": 3, "email": "kumardharma7889@gmail.com", "role": "TRADER", "tenant_id": "ORG-ENTERPRISE", "plan": "ENTERPRISE", "status": "ACTIVE"}
        ]


tenant_admin_console = TenantAdminConsole()
