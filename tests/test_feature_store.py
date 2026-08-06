import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.analytics.feature_store import feature_store_manager

def test_feature_store_caching_and_retrieval():
    symbol = "ETH/USDT"
    rec = feature_store_manager.update_symbol_features(
        symbol=symbol,
        technical_data={"rsi": 62.0, "ema_20": 2000.0, "ema_50": 1950.0, "vwap": 1990.0},
        sentiment_summary={"combined_score": 70.0, "fear_greed": {"value": 65}},
        market_regime="BULL_TREND"
    )

    assert rec["symbol"] == symbol
    assert rec["indicators"]["rsi"] == 62.0

    latest = feature_store_manager.get_latest_features(symbol=symbol)
    assert latest["indicators"]["rsi"] == 62.0
