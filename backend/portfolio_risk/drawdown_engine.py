from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class DrawdownRiskAdjustment:
    current_drawdown_pct: float
    risk_multiplier: float  # 1.0, 0.80, 0.50, 0.25, 0.0
    trading_status: str     # NORMAL, SCALED_80, SCALED_50, SCALED_25, HALTED
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class DrawdownEngine:
    """Calculates drawdown-aware risk scaling multipliers."""

    def __init__(
        self,
        tier1_pct: float = 2.0,
        tier2_pct: float = 5.0,
        tier3_pct: float = 8.0,
        halt_pct: float = 10.0
    ):
        self.tier1 = tier1_pct
        self.tier2 = tier2_pct
        self.tier3 = tier3_pct
        self.halt_threshold = halt_pct

    def compute_drawdown_adjustment(
        self,
        current_drawdown_pct: float
    ) -> DrawdownRiskAdjustment:
        """Compute drawdown risk multiplier and trading status."""
        dd = max(0.0, current_drawdown_pct)

        if dd >= self.halt_threshold:
            mult = 0.0
            status = "HALTED"
            reason = f"Critical drawdown limit reached ({dd:.2f}% >= {self.halt_threshold}%). New trade entries HALTED."
        elif dd >= self.tier3:
            mult = 0.25
            status = "SCALED_25"
            reason = f"Severe drawdown detected ({dd:.2f}% >= {self.tier3}%). Risk budget scaled to 25%."
        elif dd >= self.tier2:
            mult = 0.50
            status = "SCALED_50"
            reason = f"Moderate drawdown detected ({dd:.2f}% >= {self.tier2}%). Risk budget scaled to 50%."
        elif dd >= self.tier1:
            mult = 0.80
            status = "SCALED_80"
            reason = f"Minor drawdown detected ({dd:.2f}% >= {self.tier1}%). Risk budget scaled to 80%."
        else:
            mult = 1.0
            status = "NORMAL"
            reason = f"Drawdown normal ({dd:.2f}% < {self.tier1}%). Full risk budget permitted."

        return DrawdownRiskAdjustment(
            current_drawdown_pct=round(dd, 2),
            risk_multiplier=round(mult, 2),
            trading_status=status,
            reason=reason
        )
