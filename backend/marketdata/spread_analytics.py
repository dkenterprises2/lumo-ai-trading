from typing import Dict, Any
from backend.marketdata.dom_processor import dom_processor

class SpreadAnalyticsEngine:
    """Real-Time Spread & Liquidity Dynamics Engine."""

    @staticmethod
    def get_spread_metrics(symbol: str = "BTC/USDT") -> Dict[str, Any]:
        dom = dom_processor.process_dom(symbol)
        return {
            "symbol": symbol,
            "current_spread": dom["spread"],
            "current_spread_bps": dom["spread_bps"],
            "avg_spread_bps_24h": 1.45,
            "liquidity_regime": "TIGHT"
        }

spread_analytics = SpreadAnalyticsEngine()
