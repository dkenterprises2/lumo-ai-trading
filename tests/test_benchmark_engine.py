import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.benchmark_engine import benchmark_engine

def test_benchmark_engine():
    b = benchmark_engine.compare_algos(10.0)
    assert b["winner"] == "VWAP"
    assert len(b["results"]) == 4
