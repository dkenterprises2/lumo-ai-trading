import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.portfolio.kelly_allocator import kelly_allocator

def test_fractional_kelly_allocator():
    res = kelly_allocator.calculate_fractional_kelly(win_rate=60.0, profit_loss_ratio=1.5, fraction=0.5)
    assert res["recommended_position_pct"] > 0
    assert res["cash_reserve_pct"] == 10.0
    assert res["recommended_position_pct"] <= 90.0
