import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.portfolio.optimizer import portfolio_optimizer

def test_mean_variance_portfolio_optimizer():
    strategies = [
        {"id": "strat_a", "expected_return": 0.25, "volatility": 0.14},
        {"id": "strat_b", "expected_return": 0.18, "volatility": 0.12}
    ]
    res = portfolio_optimizer.optimize_portfolio(strategies)
    assert "weights" in res
    assert res["sharpe_ratio"] > 0
    assert sum(res["weights"].values()) == pytest.approx(1.0, abs=1e-3)
