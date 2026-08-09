from typing import Dict, Any
from backend.marketdata.orderbook_engine import orderbook_engine

class DepthOfMarketProcessor:
    """Depth-of-Market (DOM) Real-Time Metrics Processor."""

    @staticmethod
    def process_dom(symbol: str = "BTC/USDT") -> Dict[str, Any]:
        book = orderbook_engine.get_orderbook(symbol, 10)
        best_bid = book["bids"][0][0] if book["bids"] else 64810.0
        best_ask = book["asks"][0][0] if book["asks"] else 64810.5
        spread = round(best_ask - best_bid, 2)
        spread_bps = round((spread / best_bid) * 10000.0, 2)
        
        bid_depth = sum(qty for _, qty in book["bids"])
        ask_depth = sum(qty for _, qty in book["asks"])
        imbalance = round(bid_depth / (bid_depth + ask_depth + 1e-8), 4)

        return {
            "symbol": symbol,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "mid_price": round((best_bid + best_ask) / 2.0, 2),
            "spread": spread,
            "spread_bps": spread_bps,
            "cumulative_bid_depth": round(bid_depth, 2),
            "cumulative_ask_depth": round(ask_depth, 2),
            "depth_imbalance": imbalance
        }

dom_processor = DepthOfMarketProcessor()
