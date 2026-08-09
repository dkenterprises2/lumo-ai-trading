from typing import Dict, Any, List

class OrderSlicingPoliciesManager:
    """Order Slicing Policies & Constraints Manager."""

    @staticmethod
    def list_policies() -> List[Dict[str, Any]]:
        return [
            {"policy": "MIN_SLICE_SIZE_USD", "value": 100.0, "status": "ACTIVE"},
            {"policy": "MAX_SLICING_DURATION_HOURS", "value": 24, "status": "ACTIVE"}
        ]

order_slicing_policies = OrderSlicingPoliciesManager()
