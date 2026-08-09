import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.governance.promotion_pipeline import promotion_pipeline

def test_promotion_pipeline():
    res = promotion_pipeline.promote_strategy("alpha_momentum_v12", "SHADOW_DEPLOYED")
    assert res["status"] == "PROMOTED_SUCCESSFULLY"
    assert res["stage"] == "SHADOW_DEPLOYED"
