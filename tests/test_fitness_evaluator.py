import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.evolution.genetic_engine import genetic_engine

def test_fitness_sharpe():
    res = genetic_engine.evolve_population("pop_001")
    assert res["best_fitness_sharpe"] > 2.0
