import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.portfolio.scenario_analysis import scenario_analysis_engine

def test_exposure_constraints_summary():
    exp = scenario_analysis_engine.generate_exposure_summary()
    assert "strategy_exposure" in exp
    assert "sector_exposure" in exp
    assert exp["cash_reserve_pct"] >= 10.0
    assert exp["max_leverage_used"] <= 2.0
