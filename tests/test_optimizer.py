import sys
import os
import pytest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strategy_optimizer import StrategyParameterOptimizer

def test_strategy_parameter_optimizer():
    optimizer = StrategyParameterOptimizer(initial_balance=10000.0)

    now = time.time()
    candles = []
    price = 60000.0
    for i in range(25):
        price += (i % 2 - 0.5) * 300.0
        candles.append({
            "timestamp": now - (25 - i) * 3600,
            "open": price - 100.0,
            "high": price + 200.0,
            "low": price - 200.0,
            "close": price,
            "volume": 1000.0
        })

    grid = {
        "strategy_name": ["AI Hybrid", "Trend Following"],
        "risk_mode": ["Moderate", "Aggressive"],
        "leverage": [1, 2]
    }

    res = optimizer.optimize_parameters("BTC/USDT", candles, grid)

    assert res["total_combinations_evaluated"] == 8
    assert "best_configuration" in res
    assert "sharpe_ratio" in res["best_configuration"]
