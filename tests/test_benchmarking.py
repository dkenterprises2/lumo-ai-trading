import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.benchmarking import benchmarking_engine

def test_benchmarking():
    benches = benchmarking_engine.get_benchmarks()
    assert len(benches) >= 3
    assert benches[2]["benchmark"] == "Lumo Quant Multi-Factor"
