import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.portfolio_manager_v2 import multi_portfolio_manager

def test_multi_portfolio_creation_and_aggregation():
    user_id = 999
    summary = multi_portfolio_manager.get_aggregate_summary(user_id)
    assert summary["total_portfolios"] >= 1

    new_p = multi_portfolio_manager.create_portfolio(
        user_id=user_id,
        name="Futures Alpha Portfolio",
        portfolio_type="FUTURES",
        exchange_id="BINANCE_FUTURES",
        initial_capital=25000.0
    )

    assert new_p.type == "FUTURES"
    summary_updated = multi_portfolio_manager.get_aggregate_summary(user_id)
    assert summary_updated["total_portfolios"] >= 2
