import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strategy_sandbox import StrategySandboxEngine

def test_strategy_sandbox():
    sandbox = StrategySandboxEngine(initial_balance_per_strategy=10000.0)

    candles = [
        {"close": 60000.0, "rsi": 28.0, "macd_hist": 8.0},
        {"close": 61000.0, "rsi": 32.0, "macd_hist": 10.0},
        {"close": 62000.0, "rsi": 45.0, "macd_hist": 12.0}
    ]

    res = sandbox.run_sandbox_simulation("BTC/USDT", candles)

    assert "comparison_metrics" in res
    metrics = res["comparison_metrics"]
    assert "AI Hybrid" in metrics
    assert "Momentum" in metrics
    assert "Mean Reversion" in metrics
    assert metrics["AI Hybrid"]["final_balance"] >= 10000.0
