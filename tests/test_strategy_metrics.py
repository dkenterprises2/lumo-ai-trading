import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.analytics.performance_v2 import performance_engine_v2

def test_performance_metrics_engine():
    trades = [
        {"pnl_usd": 200.0},
        {"pnl_usd": -50.0},
        {"pnl_usd": 150.0},
        {"pnl_usd": -30.0},
        {"pnl_usd": 300.0}
    ]

    res = performance_engine_v2.calculate_performance_summary(trades)
    assert res["total_trades"] == 5
    assert res["win_rate"] == 60.0
    assert res["sharpe_ratio"] > 0
    assert res["sortino_ratio"] > 0
    assert res["profit_factor"] > 1.0
    assert res["total_pnl_usd"] == 570.0
