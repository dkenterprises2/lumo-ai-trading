from typing import Dict, Any, List

class RBACPermissionManager:
    """Role-Based Access Control (RBAC) Permission Matrix."""

    ROLES = {
        "OWNER": ["*"],
        "ADMIN": ["org:read", "org:write", "members:manage", "billing:read", "trading:execute", "marketdata:view", "ai:manage", "ai:view", "multiasset:trade", "multiasset:view", "saas:manage", "saas:view", "platform:manage", "platform:view"],
        "TRADER": ["org:read", "trading:execute", "analytics:read", "marketdata:view", "ai:manage", "ai:view", "multiasset:trade", "multiasset:view", "saas:view", "platform:view"],
        "ANALYST": ["org:read", "analytics:read", "marketdata:view", "ai:view", "multiasset:view", "saas:view", "platform:view"],
        "VIEWER": ["org:read", "analytics:read", "marketdata:view", "ai:view", "multiasset:view", "saas:view", "platform:view"]




    }


    @staticmethod
    def check_permission(role: str, permission: str) -> bool:
        """Evaluate role permission against RBAC matrix."""
        role_upper = role.upper()
        if role_upper not in RBACPermissionManager.ROLES:
            return False

        allowed_perms = RBACPermissionManager.ROLES[role_upper]
        if "*" in allowed_perms or permission in allowed_perms:
            return True
        return False

rbac_manager = RBACPermissionManager()
