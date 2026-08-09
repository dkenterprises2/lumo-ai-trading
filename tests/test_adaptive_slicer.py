import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.adaptive_slicer import adaptive_slicer

def test_adaptive_slicer():
    high_urg = adaptive_slicer.slice_order(10.0, "HIGH")
    assert high_urg["recommended_slices"] == 5

    med_urg = adaptive_slicer.slice_order(10.0, "MEDIUM")
    assert med_urg["recommended_slices"] == 10
