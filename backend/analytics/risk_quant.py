import math
from typing import List, Dict, Any

class AdvancedQuantRiskEngine:
    """Quantitative Risk Engine computing Value-at-Risk (VaR), CVaR, and Kelly Criterion."""

    @staticmethod
    def calculate_var_historical(returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Historical Value-at-Risk (VaR)."""
        if not returns:
            return 0.0
        sorted_returns = sorted(returns)
        idx = int((1.0 - confidence_level) * len(sorted_returns))
        var_val = abs(sorted_returns[max(0, idx)])
        return round(var_val, 4)

    @staticmethod
    def calculate_cvar_historical(returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value-at-Risk (CVaR / Expected Shortfall)."""
        if not returns:
            return 0.0
        sorted_returns = sorted(returns)
        cutoff_idx = int((1.0 - confidence_level) * len(sorted_returns))
        tail_losses = sorted_returns[:max(1, cutoff_idx)]
        cvar_val = abs(sum(tail_losses) / len(tail_losses))
        return round(cvar_val, 4)

    @staticmethod
    def calculate_kelly_fraction(win_rate: float, win_loss_ratio: float) -> float:
        """Calculate optimal Kelly Criterion fraction."""
        w = win_rate / 100.0 if win_rate > 1.0 else win_rate
        r = win_loss_ratio
        if r <= 0:
            return 0.0
        kelly = (w * r - (1.0 - w)) / r
        return round(max(0.0, min(0.25, kelly)), 4)  # Half/Quarter Kelly cap

quant_risk_engine = AdvancedQuantRiskEngine()
