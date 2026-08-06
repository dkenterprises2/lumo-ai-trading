import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.analytics.equity_curve import equity_curve_gen

def test_equity_curve_generator():
    series = equity_curve_gen.generate_equity_series(initial_equity=10000.0, num_points=20)
    assert len(series) == 20
    assert series[0]["equity_usd"] > 0
    assert "drawdown_pct" in series[0]

    comparison = equity_curve_gen.generate_strategy_comparison()
    assert len(comparison) >= 5
    assert comparison[0]["sharpe"] > 0
