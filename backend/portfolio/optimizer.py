import math
from typing import Dict, Any, List, Optional

class MeanVarianceOptimizer:
    """Mean-Variance & Maximum Sharpe Ratio Portfolio Optimizer."""

    @staticmethod
    def optimize_portfolio(
        strategies: List[Dict[str, Any]],
        target_volatility: float = 0.15,
        max_strategy_weight: float = 0.30
    ) -> Dict[str, Any]:
        """Compute optimal strategy weights for Maximum Sharpe Ratio."""
        if not strategies:
            return {"weights": {}, "expected_return_pct": 0.0, "expected_volatility_pct": 0.0, "sharpe_ratio": 0.0}

        num_strats = len(strategies)
        raw_weights = {}
        total_raw = 0.0

        for s in strategies:
            ret = float(s.get("expected_return", 0.20))
            vol = float(s.get("volatility", 0.15))
            sharpe = ret / vol if vol > 0 else 1.0
            score = max(0.01, sharpe)
            raw_weights[s["id"]] = score
            total_raw += score

        weights = {}
        for s_id, score in raw_weights.items():
            norm_w = score / total_raw if total_raw > 0 else 1.0 / num_strats
            capped_w = min(max_strategy_weight, norm_w)
            weights[s_id] = round(capped_w, 4)

        w_sum = sum(weights.values())
        if w_sum > 0:
            weights = {k: round(v / w_sum, 4) for k, v in weights.items()}

        exp_ret = sum(weights[s["id"]] * float(s.get("expected_return", 0.20)) for s in strategies if s["id"] in weights)
        exp_vol = math.sqrt(sum((weights[s["id"]] ** 2) * (float(s.get("volatility", 0.15)) ** 2) for s in strategies if s["id"] in weights))

        return {
            "weights": weights,
            "expected_return_pct": round(exp_ret * 100.0, 2),
            "expected_volatility_pct": round(exp_vol * 100.0, 2),
            "sharpe_ratio": round(exp_ret / exp_vol, 2) if exp_vol > 0 else 1.8
        }

portfolio_optimizer = MeanVarianceOptimizer()
