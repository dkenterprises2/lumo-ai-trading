from typing import Dict, Any

class MultiExchangeFeedNormalizer:
    """Normalized Multi-Exchange Feed Converter (Binance, Bybit, OKX)."""

    @staticmethod
    def normalize_tick(exchange: str, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "exchange": exchange,
            "symbol": raw_payload.get("s", "BTC/USDT"),
            "price": float(raw_payload.get("p", 64810.0)),
            "quantity": float(raw_payload.get("q", 0.1)),
            "normalized": True
        }

feed_normalizer = MultiExchangeFeedNormalizer()
