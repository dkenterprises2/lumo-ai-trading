import sys
import os
import pytest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backtest_engine import QuantitativeBacktestEngine

def test_quantitative_backtest_engine():
    backtester = QuantitativeBacktestEngine(initial_balance=10000.0)

    # Generate synthetic 30 candle dataset
    now = time.time()
    candles = []
    price = 60000.0
    for i in range(30):
        price += (i % 3 - 1) * 200.0
        candles.append({
            "timestamp": now - (30 - i) * 3600,
            "open": price - 100.0,
            "high": price + 300.0,
            "low": price - 300.0,
            "close": price,
            "volume": 1000.0
        })

    res = backtester.run_backtest(
        symbol="BTC/USDT",
        ohlcv_candles=candles,
        strategy_name="AI Hybrid",
        risk_mode="Moderate"
    )

    assert "metrics" in res
    metrics = res["metrics"]
    assert "net_profit_usd" in metrics
    assert "win_rate_pct" in metrics
    assert "sharpe_ratio" in metrics
    assert "sortino_ratio" in metrics
    assert "max_drawdown_pct" in metrics
    assert len(res["equity_curve"]) > 0
