import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.feature_store_v2 import feature_store_v2

def test_feature_store_v2():
    feature_store_v2.store_feature_vector("ETH/USDT", {"rsi_14": 62.1, "ema_20": 1950.0})
    eth_feats = feature_store_v2.get_latest_features("ETH/USDT")
    assert eth_feats["symbol"] == "ETH/USDT"
    assert eth_feats["features"]["rsi_14"] == 62.1

    meta = feature_store_v2.list_feature_metadata()
    assert len(meta) >= 5
