import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution.order_engine import live_order_engine

def test_live_order_execution_and_pre_trade_risk():
    user_id = 702
    # Submit valid order
    res = live_order_engine.submit_order(
        user_id=user_id,
        symbol="BTC/USDT",
        side="BUY",
        amount_usd=1000.0,
        order_type="MARKET",
        exchange_name="PAPER"
    )
    assert res.get("status") in ["FILLED", "OPEN", "success"]

    # Submit invalid order exceeding balance
    bad_res = live_order_engine.submit_order(
        user_id=user_id,
        symbol="BTC/USDT",
        side="BUY",
        amount_usd=500000.0,
        order_type="MARKET",
        exchange_name="PAPER"
    )
    assert bad_res["status"] == "REJECTED"
    assert "Insufficient available balance" in bad_res["reason"]
