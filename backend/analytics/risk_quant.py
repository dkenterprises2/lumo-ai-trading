import math
from typing import List, Dict, Any

class AdvancedQuantRiskEngine:
    """Institutional Advanced Quantitative Risk Metrics (VaR, CVaR, Kelly Criterion)."""

    @staticmethod
    def calculate_var(pnls_or_returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Value-at-Risk (VaR) at specified confidence level (e.g., 95% or 99%)."""
        if not pnls_or_returns:
            return 0.0
        sorted_returns = sorted(pnls_or_returns)
        index = int((1.0 - confidence) * len(sorted_returns))
        index = max(0, min(len(sorted_returns) - 1, index))
        return abs(round(sorted_returns[index], 2))

    @staticmethod
    def calculate_cvar(pnls_or_returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Expected Shortfall (Conditional VaR / CVaR)."""
        if not pnls_or_returns:
            return 0.0
        sorted_returns = sorted(pnls_or_returns)
        cutoff_index = int((1.0 - confidence) * len(sorted_returns))
        cutoff_index = max(1, min(len(sorted_returns), cutoff_index))
        tail_losses = sorted_returns[:cutoff_index]
        return abs(round(sum(tail_losses) / len(tail_losses), 2))

    @staticmethod
    def calculate_kelly_fraction(win_rate_pct: float, avg_win_usd: float, avg_loss_usd: float) -> float:
        """Calculate Kelly Criterion Optimal Sizing Fraction: Kelly % = W - (1-W)/R."""
        if avg_loss_usd <= 0 or avg_win_usd <= 0:
            return 0.10  # Fallback to 10% default sizing
        win_prob = win_rate_pct / 100.0
        loss_prob = 1.0 - win_prob
        payoff_ratio = avg_win_usd / avg_loss_usd
        kelly = win_prob - (loss_prob / payoff_ratio)
        return round(max(0.01, min(0.25, kelly * 0.5)), 4)  # Half-Kelly for risk preservation

    @staticmethod
    def estimate_slippage_and_spread(price: float, volume_usd: float) -> Dict[str, float]:
        """Estimate expected slippage and bid-ask spread based on order size."""
        spread_pct = 0.02
        slippage_pct = min(0.5, 0.01 + (volume_usd / 50000.0) * 0.05)
        return {
            "expected_spread_pct": spread_pct,
            "expected_slippage_pct": round(slippage_pct, 4),
            "estimated_impact_usd": round(volume_usd * (slippage_pct / 100.0), 2)
        }
