import time
from typing import Dict, Any, List, Optional

class FeatureStoreManager:
    """Centralized Feature Storage, Caching, and Versioning for ML & Technical Features."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FeatureStoreManager, cls).__new__(cls)
            cls._instance._init_store()
        return cls._instance

    def _init_store(self):
        # symbol -> timeframe -> feature_set
        self.feature_cache: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.version: str = "2.0.0"

    def update_symbol_features(
        self,
        symbol: str,
        technical_data: Dict[str, Any],
        sentiment_summary: Dict[str, Any],
        market_regime: str = "BULL_TRENDING",
        timeframe: str = "1h"
    ) -> Dict[str, Any]:
        """Ingest, index, and store features for symbol/timeframe."""
        if symbol not in self.feature_cache:
            self.feature_cache[symbol] = {}

        feature_record = {
            "symbol": symbol,
            "timeframe": timeframe,
            "version": self.version,
            "timestamp": time.time(),
            "indicators": {
                "ema_20": technical_data.get("ema_20", 0.0),
                "ema_50": technical_data.get("ema_50", 0.0),
                "ema_200": technical_data.get("ema_200", 0.0),
                "rsi": technical_data.get("rsi", 50.0),
                "macd": technical_data.get("macd", 0.0),
                "macd_signal": technical_data.get("macd_signal", 0.0),
                "vwap": technical_data.get("vwap", 0.0),
                "atr": technical_data.get("atr", 0.0),
                "adx": technical_data.get("adx", 0.0),
                "obv": technical_data.get("obv", 0.0)
            },
            "sentiment": {
                "combined_score": sentiment_summary.get("combined_score", 50.0),
                "fear_greed_index": sentiment_summary.get("fear_greed", {}).get("value", 50)
            },
            "market_regime": market_regime
        }

        self.feature_cache[symbol][timeframe] = feature_record
        return feature_record

    def get_latest_features(self, symbol: str = "BTC/USDT", timeframe: str = "1h") -> Dict[str, Any]:
        """Fetch cached feature vector for symbol."""
        if symbol in self.feature_cache and timeframe in self.feature_cache[symbol]:
            return self.feature_cache[symbol][timeframe]

        # Return default feature set if missing
        return self.update_symbol_features(
            symbol=symbol,
            technical_data={"rsi": 55.0, "ema_20": 64800.0, "ema_50": 64000.0, "vwap": 64750.0, "atr": 500.0},
            sentiment_summary={"combined_score": 62.0, "fear_greed": {"value": 60}},
            market_regime="BULL_TRENDING",
            timeframe=timeframe
        )

feature_store_manager = FeatureStoreManager()
