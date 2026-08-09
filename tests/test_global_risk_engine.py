import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.multiasset.global_risk_engine import global_risk_engine

def test_global_risk():
    risk = global_risk_engine.get_global_risk()
    assert "gross_exposure_usd" in risk
    assert risk["leverage_ratio"] > 0
