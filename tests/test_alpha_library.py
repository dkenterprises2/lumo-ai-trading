import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.alpha_library import alpha_library

def test_alpha_library():
    alphas = alpha_library.get_alpha_factors()
    assert len(alphas) >= 4
    assert alphas[0]["id"] == "ALPHA-001"
