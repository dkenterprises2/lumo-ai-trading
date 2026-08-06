import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.smart_allocation import smart_allocator

def test_smart_capital_allocation():
    perfs = [
        {"strategy_id": "ai_hybrid", "sharpe_ratio": 2.5, "win_rate": 70.0},
        {"strategy_id": "trend_following", "sharpe_ratio": 1.8, "win_rate": 60.0},
        {"strategy_id": "scalping", "sharpe_ratio": 1.2, "win_rate": 55.0}
    ]

    allocs = smart_allocator.calculate_allocations(100000.0, perfs)
    assert len(allocs) == 3
    for a in allocs:
        assert a["allocation_pct"] <= 30.0
        assert a["allocated_usd"] > 0
