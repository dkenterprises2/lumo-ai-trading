import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.monte_carlo import monte_carlo_engine

def test_monte_carlo_simulation():
    res = monte_carlo_engine.run_simulation(100000.0, 50, 30, seed=42)
    assert res["num_simulations"] == 50
    assert "var_95" in res
    assert "cvar_95" in res
