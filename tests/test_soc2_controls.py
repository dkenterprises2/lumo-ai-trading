import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.security.soc2_controls import soc2_controls

def test_soc2_readiness_scorecard():
    scorecard = soc2_controls.get_readiness_scorecard()
    assert scorecard["overall_score"] > 95.0
