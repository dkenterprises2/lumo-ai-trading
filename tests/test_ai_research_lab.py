import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.research_lab import ai_research_lab

def test_ai_research_lab_experiments_and_registry():
    exp = ai_research_lab.run_experiment("XGBoost Volatility Test", framework="XGBoost")
    assert exp["experiment_name"] == "XGBoost Volatility Test"
    assert "metrics" in exp
    assert "feature_importance" in exp

    registry = ai_research_lab.get_model_registry()
    assert len(registry) >= 1
