import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.algorithms.adaptive_execution import algo_suite

def test_pov_execution():
    res = algo_suite.execute_pov("BTCUSDT", 0.15)
    assert res["algo"] == "POV"
    assert res["participation_rate"] == 0.15
