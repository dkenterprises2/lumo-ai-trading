import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.footprint_engine import footprint_engine

def test_footprint_engine():
    fp = footprint_engine.get_footprint("BTC/USDT")
    assert fp["cumulative_delta"] > 0
    assert len(fp["footprint_bars"]) >= 2
