import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.security.iso27001_controls import iso27001_controls

def test_iso27001_readiness_scorecard():
    scorecard = iso27001_controls.get_readiness_scorecard()
    assert scorecard["overall_score"] > 95.0
    assert scorecard["status"] == "READY_FOR_AUDIT"
