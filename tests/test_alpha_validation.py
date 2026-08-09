import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.alpha.alpha_pipeline import alpha_pipeline

def test_alpha_pipeline():
    candidates = alpha_pipeline.get_candidates()
    assert len(candidates) >= 1
    val = alpha_pipeline.validate_alpha("alpha_micro_depth")
    assert val["status"] == "VALIDATED"
