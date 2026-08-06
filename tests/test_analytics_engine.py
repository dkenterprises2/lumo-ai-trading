import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.analytics.institutional_engine import institutional_analytics

def test_institutional_analytics_engine():
    returns = [0.012, 0.008, -0.004, 0.015, 0.021]
    metrics = institutional_analytics.calculate_rolling_metrics(returns)
    assert metrics["rolling_sharpe"] > 0
    assert metrics["rolling_sortino"] > 0
    assert metrics["rolling_volatility"] > 0

    trades = [{"pnl_usd": 100.0, "side": "BUY"}, {"pnl_usd": -50.0, "side": "SELL"}]
    streaks = institutional_analytics.calculate_streaks_and_distribution(trades)
    assert streaks["max_winning_streak"] >= 1
    assert streaks["max_losing_streak"] >= 1

    heatmap = institutional_analytics.generate_monthly_heatmap()
    assert len(heatmap) == 12
