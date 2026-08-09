from typing import Dict, Any, List

class ShadowLearningAgent:
    """Shadow-Learning / Counterfactual Paper-Trading Agent."""

    def __init__(self):
        self._shadow_trades: List[Dict[str, Any]] = [
            {
                "trade_id": "SHADOW-101",
                "symbol": "BTC/USDT",
                "hypothetical_action": "BUY_SMALL",
                "hypothetical_price": 64810.0,
                "real_market_outcome_pnl": 125.40,
                "status": "RECORDED"
            }
        ]

    def record_shadow_decision(self, symbol: str, action: str, price: float) -> Dict[str, Any]:
        trade = {
            "trade_id": f"SHADOW-{len(self._shadow_trades)+101}",
            "symbol": symbol,
            "hypothetical_action": action,
            "hypothetical_price": price,
            "real_market_outcome_pnl": 0.0,
            "status": "RECORDED"
        }
        self._shadow_trades.append(trade)
        return trade

    def list_shadow_trades(self) -> List[Dict[str, Any]]:
        return self._shadow_trades

shadow_learning_agent = ShadowLearningAgent()
