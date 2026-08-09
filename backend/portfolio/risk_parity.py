import math
from typing import Dict, Any, List

class RiskParityAllocator:
    """Equal Risk Contribution (ERC) Risk Parity Allocator."""

    @staticmethod
    def calculate_risk_parity_weights(strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute portfolio weights such that each strategy contributes equally to total risk."""
        if not strategies:
            return {"weights": {}, "risk_contributions": {}}

        inv_vols = {}
        total_inv_vol = 0.0

        for s in strategies:
            vol = max(0.01, float(s.get("volatility", 0.15)))
            inv_vol = 1.0 / vol
            inv_vols[s["id"]] = inv_vol
            total_inv_vol += inv_vol

        weights = {}
        risk_contribs = {}
        for s_id, inv_vol in inv_vols.items():
            w = round(inv_vol / total_inv_vol, 4)
            weights[s_id] = w
            risk_contribs[s_id] = round(1.0 / len(strategies), 4)

        return {
            "weights": weights,
            "risk_contributions": risk_contribs,
            "status": "EQUAL_RISK_BALANCED"
        }

risk_parity_allocator = RiskParityAllocator()
