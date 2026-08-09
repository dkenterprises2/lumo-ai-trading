from typing import Dict, Any
from backend.marketdata.dom_processor import dom_processor

class OrderBookImbalanceAnalytics:
    """Order Book Depth & Flow Imbalance Analytics."""

    @staticmethod
    def get_imbalance(symbol: str = "BTC/USDT") -> Dict[str, Any]:
        dom = dom_processor.process_dom(symbol)
        imb = dom["depth_imbalance"]
        signal = "BULLISH_PRESSURE" if imb > 0.60 else ("BEARISH_PRESSURE" if imb < 0.40 else "NEUTRAL")
        return {
            "symbol": symbol,
            "imbalance_ratio": imb,
            "pressure_signal": signal
        }

orderbook_imbalance = OrderBookImbalanceAnalytics()
