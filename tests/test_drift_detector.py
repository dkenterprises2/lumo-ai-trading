import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.drift_detector import drift_detector

def test_drift_detector_evaluation():
    drift = drift_detector.evaluate_drift()
    assert drift["psi_score"] >= 0.0
    assert "drift_status" in drift
    assert len(drift["detectors"]) == 4
