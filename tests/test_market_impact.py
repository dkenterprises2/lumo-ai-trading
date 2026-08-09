import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.market_impact import market_impact_engine

def test_market_impact_estimation():
    imp = market_impact_engine.estimate_impact("BTC/USDT", 10.0)
    assert imp["estimated_impact_bps"] > 0
    assert imp["swept_levels"] == 3
