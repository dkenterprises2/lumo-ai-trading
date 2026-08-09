import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.ems.execution_engine import ems_engine

def test_child_order_slicing():
    exec_res = ems_engine.execute_parent_order("ord_102", "VWAP")
    assert exec_res["algorithm"] == "VWAP"
