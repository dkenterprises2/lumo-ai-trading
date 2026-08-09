from typing import Dict, Any

class MarketRegimeSpecialistRouter:
    """Dynamic Market Regime Specialist Agent Router."""

    @staticmethod
    def route_to_specialist(volatility: float, trend_score: float) -> str:
        if volatility > 0.04:
            return "VOLATILITY_BREAKOUT"
        elif trend_score > 0.65:
            return "TREND_FOLLOWING"
        elif trend_score < -0.65:
            return "BEAR_DEFENSIVE"
        else:
            return "MEAN_REVERSION"

regime_specialist = MarketRegimeSpecialistRouter()
