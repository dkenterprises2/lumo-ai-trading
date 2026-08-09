import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.mean_reversion import mean_reversion_toolkit

def test_mean_reversion_ou():
    ou = mean_reversion_toolkit.calculate_ou_params([100, 101, 102])
    assert "theta_speed" in ou
    assert "half_life" in ou
