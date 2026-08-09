import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.data_quality import data_quality_pipeline

def test_data_quality_pipeline():
    report = data_quality_pipeline.run_quality_check()
    assert report["overall_quality"] == "PASSED"
    assert report["null_value_pct"] == 0.0
