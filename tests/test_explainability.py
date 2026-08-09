import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.explainability import explainability_engine

def test_explainability_attribution():
    exp = explainability_engine.explain_decision("DEC-101")
    assert "top_features" in exp
    assert exp["confidence"] > 0.80
