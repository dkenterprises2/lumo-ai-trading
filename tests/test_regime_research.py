import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.regime_research import regime_research

def test_regime_research():
    reg = regime_research.detect_regime([100, 105, 110])
    assert "current_regime" in reg
    assert reg["transition_probability"] > 0
