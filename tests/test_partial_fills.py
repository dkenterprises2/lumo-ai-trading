import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution.reconciliation import reconciliation_engine

def test_partial_fills_detection():
    local_orders = [{"order_id": "ORD_PARTIAL", "amount": 1.0, "status": "OPEN"}]
    exchange_orders = [{"order_id": "ORD_PARTIAL", "filled_amount": 0.4, "amount": 1.0, "status": "OPEN"}]

    res = reconciliation_engine.audit_orders(local_orders, exchange_orders)
    assert len(res["partial_fills"]) == 1
    assert res["partial_fills"][0]["filled"] == 0.4
