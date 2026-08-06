from typing import Dict, Any
from backend.plugins.base import BaseStrategyPlugin

class MomentumStrategyPlugin(BaseStrategyPlugin):
    """Trend & Momentum Strategy Plugin."""

    def get_strategy_name(self) -> str:
        return "Momentum"

    def evaluate(self, symbol: str, current_price: float, technical_data: Dict[str, Any], sentiment_summary: Dict[str, Any]) -> Dict[str, Any]:
        macd_hist = float(technical_data.get("macd_hist", 0.0))
        adx = float(technical_data.get("adx", 20.0))

        if macd_hist > 5.0 and adx > 25.0:
            action = "BUY"
            direction = "LONG"
            confidence = 82.0
        elif macd_hist < -5.0 and adx > 25.0:
            action = "SELL"
            direction = "SHORT"
            confidence = 82.0
        else:
            action = "HOLD"
            direction = "NEUTRAL"
            confidence = 50.0

        return {
            "symbol": symbol,
            "strategy": "Momentum",
            "action": action,
            "direction": direction,
            "confidence": confidence
        }
