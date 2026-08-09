import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.model_registry import ml_model_registry

def test_ml_model_registry_list_and_promote():
    models = ml_model_registry.list_models()
    assert len(models) >= 6

    champ = ml_model_registry.get_champion_model()
    assert champ is not None
    assert champ.is_champion is True

    # Test promote challenger
    prom_res = ml_model_registry.promote_champion("lgb_challenger_v1")
    assert prom_res["status"] == "success"
    assert ml_model_registry.get_champion_model().model_id == "lgb_challenger_v1"

    # Test rollback
    roll_res = ml_model_registry.rollback_champion("xgb_prod_v2")
    assert roll_res["status"] == "success"
    assert ml_model_registry.get_champion_model().model_id == "xgb_prod_v2"
