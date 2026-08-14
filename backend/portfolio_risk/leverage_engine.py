from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class LeverageRecommendation:
    requested: float
    recommended: float
    maximum_allowed: float
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class LeverageEngine:
    """Calculates safe dynamic leverage recommendations based on risk metrics."""

    def evaluate_leverage(
        self,
        requested_leverage: int,
        user_max_leverage: int = 10,
        volatility_multiplier: float = 1.0,
        drawdown_pct: float = 0.0,
        portfolio_heat_status: str = "NORMAL",
        confidence: float = 75.0
    ) -> LeverageRecommendation:
        """Compute recommended and maximum allowed leverage."""
        req = float(max(1, requested_leverage))
        u_max = float(max(1, user_max_leverage))

        # Base maximum allowed is capped at user's max leverage selection
        max_cap = u_max

        reasons = []

        # Volatility reduction
        if volatility_multiplier < 1.0:
            max_cap *= volatility_multiplier
            reasons.append(f"Volatility reduction ({volatility_multiplier:.2f}x)")

        # Drawdown reduction
        if drawdown_pct >= 5.0:
            max_cap *= 0.50
            reasons.append(f"Drawdown cap ({drawdown_pct:.1f}%)")

        # Portfolio Heat reduction
        if portfolio_heat_status in ["HIGH", "CRITICAL"]:
            max_cap *= 0.50
            reasons.append(f"Portfolio Heat Status ({portfolio_heat_status})")

        # Low confidence reduction
        if confidence < 60.0:
            max_cap *= 0.75
            reasons.append(f"Low Signal Confidence ({confidence:.1f}%)")

        max_allowed = max(1.0, round(max_cap, 1))

        # NEVER increase requested leverage automatically!
        recommended = min(req, max_allowed)
        reason_str = ", ".join(reasons) if reasons else "Risk metrics normal."

        return LeverageRecommendation(
            requested=req,
            recommended=recommended,
            maximum_allowed=max_allowed,
            reason=reason_str
        )
