import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.evolution.genetic_engine import genetic_engine

def test_genetic_engine():
    res = genetic_engine.evolve_population("pop_001")
    assert res["status"] == "EVOLVED"
    assert res["generation"] == 42
