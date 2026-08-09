import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.monitoring.drift_detector import drift_detector

def test_retire_strategy():
    res = drift_detector.retire_strategy("alpha_decayed")
    assert res["status"] == "RETIRED_FROM_LIVE"
    assert res["allocation"] == 0.0
