import time
from typing import Dict, Any, List

class SubscriptionManager:
    """Subscription Plans & Seat-Based Billing Manager."""

    PLANS = [
        {"id": "plan_free", "name": "Free Simulator", "price_usd": 0, "api_limit": 10000, "seats": 1},
        {"id": "plan_pro", "name": "Pro Trader", "price_usd": 199, "api_limit": 100000, "seats": 5},
        {"id": "plan_enterprise", "name": "Institutional Enterprise", "price_usd": 999, "api_limit": 1000000, "seats": 25}
    ]

    def list_plans(self) -> List[Dict[str, Any]]:
        return SubscriptionManager.PLANS

    def subscribe_org(self, org_id: str, plan_id: str) -> Dict[str, Any]:
        """Subscribe organization to selected billing plan."""
        return {
            "status": "ACTIVE",
            "org_id": org_id,
            "plan_id": plan_id,
            "subscribed_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

subscription_manager = SubscriptionManager()
