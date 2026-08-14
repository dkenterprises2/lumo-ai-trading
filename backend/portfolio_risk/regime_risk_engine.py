from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class RegimeRiskParameters:
    market_regime: str # BULL, BEAR, SIDEWAYS, HIGH_VOLATILITY, LOW_VOLATILITY, UNKNOWN
    permitted_exposure_pct: float
    max_concurrent_positions: int
    position_size_multiplier: float
    leverage_multiplier: float
    risk_budget_multiplier: float
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RegimeRiskEngine:
    """Adapts risk parameters based on market regime detection."""

    def __init__(self, base_max_positions: int = 10):
        self.base_max_positions = base_max_positions

    def evaluate_regime_risk(
        self,
        market_regime: str = "BULL"
    ) -> RegimeRiskParameters:
        """Map market regime to risk parameters."""
        regime = market_regime.upper() if market_regime else "UNKNOWN"

        if regime == "HIGH_VOLATILITY":
            return RegimeRiskParameters(
                market_regime=regime,
                permitted_exposure_pct=40.0,
                max_concurrent_positions=max(3, int(self.base_max_positions * 0.5)),
                position_size_multiplier=0.50,
                leverage_multiplier=0.50,
                risk_budget_multiplier=0.60,
                description="High Volatility Regime: Defensive exposure, reduced position count, capped leverage."
            )
        elif regime == "BEAR":
            return RegimeRiskParameters(
                market_regime=regime,
                permitted_exposure_pct=60.0,
                max_concurrent_positions=max(5, int(self.base_max_positions * 0.7)),
                position_size_multiplier=0.75,
                leverage_multiplier=0.75,
                risk_budget_multiplier=0.75,
                description="Bear Market Regime: Moderate exposure cap, selective short/hedged strategies."
            )
        elif regime == "SIDEWAYS":
            return RegimeRiskParameters(
                market_regime=regime,
                permitted_exposure_pct=75.0,
                max_concurrent_positions=self.base_max_positions,
                position_size_multiplier=0.90,
                leverage_multiplier=1.0,
                risk_budget_multiplier=0.90,
                description="Sideways Ranging Regime: Mean-reversion and scalping parameters enabled."
            )
        elif regime == "LOW_VOLATILITY":
            return RegimeRiskParameters(
                market_regime=regime,
                permitted_exposure_pct=90.0,
                max_concurrent_positions=self.base_max_positions,
                position_size_multiplier=1.0,
                leverage_multiplier=1.0,
                risk_budget_multiplier=1.0,
                description="Low Volatility Regime: Favorable conditions for breakout strategies."
            )
        else: # BULL or UNKNOWN
            return RegimeRiskParameters(
                market_regime=regime,
                permitted_exposure_pct=100.0,
                max_concurrent_positions=self.base_max_positions,
                position_size_multiplier=1.0,
                leverage_multiplier=1.0,
                risk_budget_multiplier=1.0,
                description="Bullish / Standard Market Regime: Standard risk parameters active."
            )
