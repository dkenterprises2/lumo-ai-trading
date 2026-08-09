import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.governance.promotion_pipeline import promotion_pipeline

def test_certification():
    cert = promotion_pipeline.certify_strategy("alpha_test")
    assert cert["status"] == "ROBUSTNESS_CERTIFIED"
