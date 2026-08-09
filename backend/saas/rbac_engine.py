from typing import Dict, Any, List

class DeclarativeRBACEngine:
    """Declarative Role-Based & Action Permission Evaluator."""

    DEFAULT_ROLES = [
        "SUPER_ADMIN", "ORG_OWNER", "ORG_ADMIN", "TRADER",
        "QUANT_RESEARCHER", "RISK_MANAGER", "COMPLIANCE_OFFICER", "VIEWER", "API_CLIENT"
    ]

    @staticmethod
    def evaluate_permission(role: str, resource: str, action: str) -> bool:
        if role in ["SUPER_ADMIN", "ORG_OWNER"]:
            return True
        if role == "ORG_ADMIN" and resource != "system.super_admin":
            return True
        if role == "TRADER" and resource in ["execution.orders", "marketdata.view", "ai.manage"]:
            return True
        if role == "VIEWER" and action == "read":
            return True
        return False

rbac_engine = DeclarativeRBACEngine()
