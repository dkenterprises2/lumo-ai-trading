import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.portfolio.stress_testing import stress_testing_engine

def test_stress_testing_scenarios():
    res = stress_testing_engine.run_stress_test_scenarios(portfolio_equity=100000.0)
    assert res["scenarios_evaluated"] == 7
    assert res["status"] == "STRESS_TEST_COMPLETED"
    assert res["resilience_score"] > 0
