import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.marketdata.volume_profile import volume_profile_engine

def test_volume_profile_poc():
    vp = volume_profile_engine.get_volume_profile("BTC/USDT")
    assert vp["poc_price"] == 64810.0
    assert len(vp["profile_bins"]) == 3
