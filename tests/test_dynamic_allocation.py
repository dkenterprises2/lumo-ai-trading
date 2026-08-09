import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.alpha_factory.ensemble.ensemble_composer import ensemble_composer

def test_equal_weight_allocation():
    ens = ensemble_composer.compose_ensemble(["s1", "s2"])
    assert ens["weights"]["s1"] == 0.5
