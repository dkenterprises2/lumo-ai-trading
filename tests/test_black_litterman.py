import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.portfolio.black_litterman import black_litterman_model

def test_black_litterman_model():
    market_w = {"strat_a": 0.50, "strat_b": 0.50}
    ai_views = [{"strategy_id": "strat_a", "expected_return": 0.10}]

    res = black_litterman_model.calculate_bl_weights(market_w, ai_views)
    adj_w = res["adjusted_weights"]
    assert adj_w["strat_a"] > adj_w["strat_b"]
    assert sum(adj_w.values()) == pytest.approx(1.0, abs=1e-3)
