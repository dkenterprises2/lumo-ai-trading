from typing import Dict, Any, List

class PermissionRegistry:
    """Declarative Permissions Catalog."""

    @staticmethod
    def list_permissions() -> List[Dict[str, str]]:
        return [
            {"resource": "execution.orders", "action": "create"},
            {"resource": "execution.orders", "action": "read"},
            {"resource": "marketdata.view", "action": "read"},
            {"resource": "ai.manage", "action": "execute"},
            {"resource": "billing.invoices", "action": "read"},
            {"resource": "admin.tenants", "action": "manage"}
        ]

permission_registry = PermissionRegistry()
