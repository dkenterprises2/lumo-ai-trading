import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.execution_quality import execution_quality

def test_execution_quality():
    q = execution_quality.score_execution({})
    assert q["quality_grade"] == "A+"
    assert q["score"] > 90.0
