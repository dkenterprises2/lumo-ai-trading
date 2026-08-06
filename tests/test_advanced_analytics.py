import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.analytics.performance import AdvancedPerformanceAnalytics

def test_calmar_omega_heatmap():
    calmar = AdvancedPerformanceAnalytics.calculate_calmar_ratio(25.0, 10.0)
    assert calmar == 2.5

    omega = AdvancedPerformanceAnalytics.calculate_omega_ratio([100.0, 200.0, -50.0])
    assert omega > 1.0

    trades = [{"entry_time": "2026-08-06 10:00:00", "pnl_usd": 150.0}]
    heatmap = AdvancedPerformanceAnalytics.generate_monthly_heatmap(trades)
    assert "2026" in heatmap
    assert "08" in heatmap["2026"]
