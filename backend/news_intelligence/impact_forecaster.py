from dataclasses import dataclass, asdict
from typing import Dict, Any, List

from .volatility_predictor import VolatilityPredictor, VolatilityForecast

@dataclass
class MarketImpactForecast:
    symbol: str
    event_type: str
    impact_1h_pct: float
    impact_4h_pct: float
    impact_24h_pct: float
    direction: str  # BULLISH, BEARISH, NEUTRAL
    confidence: float
    volatility: VolatilityForecast

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["volatility"] = self.volatility.to_dict()
        return d

class ImpactForecaster:
    """Predicts Price Impact & Volatility Horizons (1h, 4h, 24h)."""

    def __init__(self):
        self.vol_predictor = VolatilityPredictor()

    def forecast_impact(
        self,
        symbol: str,
        event_type: str,
        expected_impact: str = "BULLISH",
        severity: str = "HIGH",
        confidence: float = 0.90
    ) -> MarketImpactForecast:
        vol = self.vol_predictor.predict_volatility(event_type, severity)

        mult = 1.0 if expected_impact == "BULLISH" else (-1.0 if expected_impact == "BEARISH" else 0.0)

        imp_1h = vol.expected_volatility_1h_pct * 0.80 * mult
        imp_4h = vol.expected_volatility_4h_pct * 0.70 * mult
        imp_24h = vol.expected_volatility_24h_pct * 0.60 * mult

        return MarketImpactForecast(
            symbol=symbol,
            event_type=event_type,
            impact_1h_pct=round(imp_1h, 2),
            impact_4h_pct=round(imp_4h, 2),
            impact_24h_pct=round(imp_24h, 2),
            direction=expected_impact,
            confidence=confidence,
            volatility=vol
        )
