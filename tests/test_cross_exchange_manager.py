import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.cross_exchange_manager import cross_exchange_manager

def test_cross_exchange_execution():
    res = cross_exchange_manager.execute_multi_venue("BTC/USDT", 10.0, "BUY")
    assert res["status"] == "DISPATCHED"
    assert len(res["allocations"]) == 2
