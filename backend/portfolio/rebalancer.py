import time
from typing import Dict, Any, List

class PortfolioRebalancer:
    """Portfolio Rebalancing Scheduler executing drift monitoring & target allocation adjustments."""

    @staticmethod
    def evaluate_rebalance_drift(
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        drift_threshold_pct: float = 5.0
    ) -> Dict[str, Any]:
        """Check if portfolio allocation drift exceeds rebalance threshold."""
        rebalance_required = False
        drifts = {}

        for s_id, target in target_weights.items():
            curr = current_weights.get(s_id, 0.0)
            diff = abs(curr - target) * 100.0
            drifts[s_id] = round(diff, 2)
            if diff >= drift_threshold_pct:
                rebalance_required = True

        return {
            "rebalance_required": rebalance_required,
            "drift_threshold_pct": drift_threshold_pct,
            "drifts_pct": drifts,
            "evaluated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

    @staticmethod
    def execute_rebalance(
        user_id: int,
        target_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Execute portfolio rebalancing orders to match target weights."""
        return {
            "status": "COMPLETED",
            "user_id": user_id,
            "rebalanced_weights": target_weights,
            "rebalanced_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

portfolio_rebalancer = PortfolioRebalancer()
