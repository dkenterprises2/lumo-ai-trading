import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.algorithms.adaptive_execution import algo_suite

def test_twap_execution():
    res = algo_suite.execute_twap("BTCUSDT", 10.0, 30)
    assert res["algo"] == "TWAP"
    assert res["slices"] == 6
