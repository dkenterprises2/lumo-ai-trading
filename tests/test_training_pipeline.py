import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.training_pipeline import automl_pipeline

def test_automl_training_pipeline():
    res = automl_pipeline.run_training_experiment(algorithm="LIGHTGBM")
    assert res["status"] == "COMPLETED"
    assert res["metrics"]["accuracy"] > 0
    assert len(res["feature_importance"]) >= 3
    assert res["walk_forward_validation"]["status"] == "PASSED"
