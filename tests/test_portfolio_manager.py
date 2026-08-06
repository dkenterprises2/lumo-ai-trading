import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.portfolio_manager_v2 import multi_portfolio_manager

def test_multi_portfolio_manager_v21():
    user_id = 902
    p1 = multi_portfolio_manager.create_portfolio(user_id, "Scalping Desk", "SCALPING", 10000.0)
    assert p1["type"] == "SCALPING"
    assert p1["equity"] == 10000.0

    summary = multi_portfolio_manager.get_aggregate_summary(user_id)
    assert summary["total_net_worth"] >= 10000.0
