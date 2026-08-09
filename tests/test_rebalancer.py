import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.portfolio.rebalancer import portfolio_rebalancer

def test_portfolio_rebalancer_drift_and_execute():
    curr_w = {"strat_a": 0.40, "strat_b": 0.60}
    target_w = {"strat_a": 0.50, "strat_b": 0.50}

    drift_res = portfolio_rebalancer.evaluate_rebalance_drift(curr_w, target_w, drift_threshold_pct=5.0)
    assert drift_res["rebalance_required"] is True

    exec_res = portfolio_rebalancer.execute_rebalance(user_id=1, target_weights=target_w)
    assert exec_res["status"] == "COMPLETED"
    assert exec_res["rebalanced_weights"] == target_w
