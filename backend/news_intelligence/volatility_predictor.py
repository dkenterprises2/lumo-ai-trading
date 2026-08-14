from dataclasses import dataclass, asdict
from typing import Dict, Any

from .event_taxonomy import CryptoEventType, EventImpactSeverity

@dataclass
class VolatilityForecast:
    event_type: str
    expected_volatility_1h_pct: float
    expected_volatility_4h_pct: float
    expected_volatility_24h_pct: float
    volatility_regime: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class VolatilityPredictor:
    """Predicts Horizon Volatility Spikes (1h, 4h, 24h)."""

    def predict_volatility(self, event_type: str, severity: str = "HIGH") -> VolatilityForecast:
        base_1h = 1.5
        base_4h = 3.2
        base_24h = 6.5

        if severity == "CRITICAL":
            base_1h *= 3.0
            base_4h *= 2.5
            base_24h *= 2.0
        elif severity == "HIGH":
            base_1h *= 1.8
            base_4h *= 1.5
            base_24h *= 1.3

        regime = "NORMAL"
        if base_1h >= 4.0:
            regime = "EXTREME_VOLATILITY"
        elif base_1h >= 2.0:
            regime = "HIGH_VOLATILITY"

        return VolatilityForecast(
            event_type=event_type,
            expected_volatility_1h_pct=round(base_1h, 2),
            expected_volatility_4h_pct=round(base_4h, 2),
            expected_volatility_24h_pct=round(base_24h, 2),
            volatility_regime=regime
        )
