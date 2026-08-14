from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class VolatilityRegimeAnalysis:
    volatility_regime: str # LOW, NORMAL, HIGH, EXTREME
    realized_volatility_pct: float
    atr_pct: float
    position_size_multiplier: float # 1.0, 1.0, 0.60, 0.30
    leverage_multiplier: float
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class VolatilityEngine:
    """Computes asset & portfolio volatility regimes and position scaling multipliers."""

    def __init__(self, high_vol_threshold_pct: float = 3.5, extreme_vol_threshold_pct: float = 6.0):
        self.high_vol_threshold = high_vol_threshold_pct
        self.extreme_vol_threshold = extreme_vol_threshold_pct

    def analyze_volatility(
        self,
        atr_pct: float = 2.0,
        realized_vol_pct: float = 25.0
    ) -> VolatilityRegimeAnalysis:
        """Analyze current volatility regime and compute risk multipliers."""

        if atr_pct >= self.extreme_vol_threshold or realized_vol_pct >= 60.0:
            regime = "EXTREME"
            size_mult = 0.30
            lev_mult = 0.50
            reason = f"Extreme volatility detected (ATR {atr_pct:.2f}% >= {self.extreme_vol_threshold}%). Position size scaled to 30%."
        elif atr_pct >= self.high_vol_threshold or realized_vol_pct >= 40.0:
            regime = "HIGH"
            size_mult = 0.60
            lev_mult = 0.75
            reason = f"High volatility detected (ATR {atr_pct:.2f}% >= {self.high_vol_threshold}%). Position size scaled to 60%."
        elif atr_pct < 1.0 and realized_vol_pct < 15.0:
            regime = "LOW"
            size_mult = 1.0
            lev_mult = 1.0
            reason = "Low volatility regime. Normal risk sizing permitted."
        else:
            regime = "NORMAL"
            size_mult = 1.0
            lev_mult = 1.0
            reason = "Normal volatility regime. Standard risk sizing applied."

        return VolatilityRegimeAnalysis(
            volatility_regime=regime,
            realized_volatility_pct=round(realized_vol_pct, 2),
            atr_pct=round(atr_pct, 2),
            position_size_multiplier=round(size_mult, 2),
            leverage_multiplier=round(lev_mult, 2),
            reason=reason
        )
