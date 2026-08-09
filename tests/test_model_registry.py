import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.model_registry import model_registry_manager

def test_model_registry_lifecycle():
    mod = model_registry_manager.register_model("Ensemble Predictor", "1.0.0", "STAGING")
    assert mod["stage"] == "STAGING"

    prom = model_registry_manager.promote_model(mod["model_id"], "PRODUCTION")
    assert prom["stage"] == "PRODUCTION"
