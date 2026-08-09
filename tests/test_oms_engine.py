import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.oms_engine import oms_engine

def test_oms_order_creation():
    ord = oms_engine.create_order("AAPL", "EQUITY", 100.0, "BUY")
    assert ord["order_id"].startswith("OMS-PARENT-")
    assert ord["allocated_quantity"] == 100.0
