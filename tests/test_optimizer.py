import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.training_pipeline import automl_pipeline

def test_hyperparameter_optimization():
    opt_res = automl_pipeline.run_hyperparameter_optimization(algorithm="CATBOOST")
    assert opt_res["status"] == "COMPLETED"
    assert opt_res["best_score"] > 0
    assert "best_parameters" in opt_res
