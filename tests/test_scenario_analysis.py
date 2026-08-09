import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.portfolio.scenario_analysis import scenario_analysis_engine

def test_scenario_analysis_correlation_matrix():
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    res = scenario_analysis_engine.generate_correlation_matrix(symbols)
    assert res["is_symmetric"] is True
    assert len(res["correlation_matrix"]) == 3
    assert res["correlation_matrix"][0][0] == 1.0
