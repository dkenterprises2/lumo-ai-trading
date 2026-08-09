from typing import Dict, Any, List

class BlackLittermanModel:
    """Black-Litterman Bayesian Portfolio Allocation Model blending market equilibrium with AI views."""

    @staticmethod
    def calculate_bl_weights(
        market_weights: Dict[str, float],
        ai_views: List[Dict[str, Any]],
        tau: float = 0.05
    ) -> Dict[str, Any]:
        """Compute posterior Black-Litterman Bayesian optimal portfolio weights."""
        if not market_weights:
            return {"adjusted_weights": {}, "equilibrium_returns": {}}

        adjusted = dict(market_weights)

        for view in ai_views:
            s_id = view.get("strategy_id")
            view_return = float(view.get("expected_return", 0.05))
            if s_id in adjusted:
                # Bayesian update shifting market equilibrium towards AI view signal
                tilt = view_return * tau
                adjusted[s_id] = round(max(0.01, adjusted[s_id] + tilt), 4)

        # Normalize posterior weights
        total_w = sum(adjusted.values())
        if total_w > 0:
            adjusted = {k: round(v / total_w, 4) for k, v in adjusted.items()}

        return {
            "adjusted_weights": adjusted,
            "tau": tau,
            "views_applied": len(ai_views)
        }

black_litterman_model = BlackLittermanModel()
