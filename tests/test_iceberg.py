import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.algorithms.adaptive_execution import algo_suite

def test_iceberg_execution():
    res = algo_suite.execute_iceberg("BTCUSDT", 50.0, 5.0)
    assert res["algo"] == "ICEBERG"
    assert res["hidden_quantity"] == 45.0
