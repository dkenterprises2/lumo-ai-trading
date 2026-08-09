import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.spread_analytics import spread_analytics

def test_spread_analytics():
    sp = spread_analytics.get_spread_metrics("BTC/USDT")
    assert "current_spread" in sp
    assert sp["liquidity_regime"] == "TIGHT"
