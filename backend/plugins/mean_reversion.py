from typing import Dict, Any
from backend.plugins.base import BaseStrategyPlugin

class MeanReversionStrategyPlugin(BaseStrategyPlugin):
    """RSI Mean Reversion Strategy Plugin."""

    def get_strategy_name(self) -> str:
        return "Mean Reversion"

    def evaluate(self, symbol: str, current_price: float, technical_data: Dict[str, Any], sentiment_summary: Dict[str, Any]) -> Dict[str, Any]:
        rsi = float(technical_data.get("rsi", 50.0))

        if rsi <= 30.0:
            action = "BUY"
            direction = "LONG"
            confidence = 88.0
        elif rsi >= 70.0:
            action = "SELL"
            direction = "SHORT"
            confidence = 88.0
        else:
            action = "HOLD"
            direction = "NEUTRAL"
            confidence = 50.0

        return {
            "symbol": symbol,
            "strategy": "Mean Reversion",
            "action": action,
            "direction": direction,
            "confidence": confidence
        }
