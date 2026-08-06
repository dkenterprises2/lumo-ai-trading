import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.analytics.risk_quant import AdvancedQuantRiskEngine

def test_var_cvar_kelly_calculations():
    pnls = [-200.0, -100.0, 50.0, 150.0, 300.0, 400.0, -50.0]

    var_95 = AdvancedQuantRiskEngine.calculate_var(pnls, 0.95)
    cvar_95 = AdvancedQuantRiskEngine.calculate_cvar(pnls, 0.95)
    kelly = AdvancedQuantRiskEngine.calculate_kelly_fraction(65.0, 200.0, 100.0)

    assert var_95 >= 0.0
    assert cvar_95 >= 0.0
    assert 0.01 <= kelly <= 0.25
