import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.automl.strategy_generator import strategy_generator

def test_search_space_candidate():
    cand = strategy_generator.generate_candidate("space_01")
    assert cand["sharpe_estimated"] > 0
