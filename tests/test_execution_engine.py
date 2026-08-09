import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.ems.execution_engine import ems_engine

def test_ems_execution():
    exec_res = ems_engine.execute_parent_order("ord_101", "TWAP")
    assert exec_res["status"] == "ROUTED_AND_SLICED"
    assert exec_res["child_orders_count"] == 10
