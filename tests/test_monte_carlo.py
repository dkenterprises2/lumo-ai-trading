import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backtest_engine import QuantitativeBacktestEngine

def test_monte_carlo_and_walk_forward():
    engine = QuantitativeBacktestEngine(initial_balance=10000.0)

    trades = [{"pnl_usd": 200.0}, {"pnl_usd": -100.0}, {"pnl_usd": 300.0}, {"pnl_usd": -50.0}]
    mc_res = engine.run_monte_carlo_simulation(trades, simulations_count=50)

    assert mc_res["simulations_count"] == 50
    assert "percentile_5th_balance" in mc_res
    assert "percentile_95th_balance" in mc_res
