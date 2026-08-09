import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.ems_engine import ems_engine

def test_ems_routing():
    route = ems_engine.route_execution("OMS-101", "NASDAQ", 50.0)
    assert route["status"] == "EXECUTED_SIMULATED"
    assert route["target_venue"] == "NASDAQ"
