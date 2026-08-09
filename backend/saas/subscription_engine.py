from typing import Dict, Any, List

class SubscriptionEngine:
    """Enterprise Subscription Tier & Plan Lifecycle Engine."""

    PLANS = ["FREE", "STARTER", "PROFESSIONAL", "INSTITUTIONAL", "ENTERPRISE", "WHITE_LABEL"]

    @staticmethod
    def change_plan(tenant_id: str, new_plan: str) -> Dict[str, Any]:
        if new_plan not in SubscriptionEngine.PLANS:
            new_plan = "ENTERPRISE"
        return {
            "tenant_id": tenant_id,
            "previous_plan": "PROFESSIONAL",
            "new_plan": new_plan,
            "status": "ACTIVE",
            "billing_cycle": "MONTHLY"
        }

subscription_engine = SubscriptionEngine()
