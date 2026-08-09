import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.tca_engine import tca_engine

def test_tca_metrics_reconciliation():
    tca = tca_engine.analyze_execution(64800.0, 64812.0, 64810.0, 10.0)
    assert "implementation_shortfall_bps" in tca
    assert "execution_efficiency_score" in tca
    assert tca["execution_efficiency_score"] > 90.0
