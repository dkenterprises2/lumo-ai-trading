import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution.slippage_tracker import slippage_tracker

def test_slippage_tracker_calculation():
    # Buy order executed higher than expected -> adverse slippage
    res = slippage_tracker.calculate_slippage(expected_price=64800.0, filled_price=64815.0, side="BUY")
    assert res["slippage_bps"] == 2.31
    assert res["is_adverse"] is True
