from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class PositionSizingResult:
    requested_allocation_usd: float
    recommended_allocation_usd: float
    effective_leverage: int
    risk_percentage: float
    scaling_factors: Dict[str, float]
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PositionSizingEngine:
    """Adaptive position sizing engine combining risk factors."""

    def compute_size(
        self,
        base_allocation_usd: float,
        portfolio_equity: float,
        max_capital_per_trade_pct: float = 10.0,
        volatility_mult: float = 1.0,
        drawdown_mult: float = 1.0,
        streak_mult: float = 1.0,
        regime_mult: float = 1.0
    ) -> PositionSizingResult:
        """Compute safe risk-adjusted position size."""
        base_alloc = max(0.0, base_allocation_usd)
        eq = max(1.0, portfolio_equity)

        # Combined multiplier
        combined_mult = volatility_mult * drawdown_mult * streak_mult * regime_mult
        recommended = base_alloc * combined_mult

        # Capped by user's max_capital_per_trade_pct
        max_user_cap = eq * (max_capital_per_trade_pct / 100.0)
        final_alloc = min(recommended, max_user_cap)
        risk_pct = (final_alloc / eq) * 100.0

        scaling = {
            "volatility": round(volatility_mult, 2),
            "drawdown": round(drawdown_mult, 2),
            "streak": round(streak_mult, 2),
            "regime": round(regime_mult, 2),
            "combined": round(combined_mult, 2)
        }

        reason = f"Position size scaled by {combined_mult:.2f}x (Final: ${final_alloc:.2f}, {risk_pct:.1f}% equity)."

        return PositionSizingResult(
            requested_allocation_usd=round(base_alloc, 2),
            recommended_allocation_usd=round(final_alloc, 2),
            effective_leverage=1,
            risk_percentage=round(risk_pct, 2),
            scaling_factors=scaling,
            reason=reason
        )
