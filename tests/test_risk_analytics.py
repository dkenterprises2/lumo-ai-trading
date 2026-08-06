import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.analytics.risk_quant import quant_risk_engine

def test_risk_analytics_var_cvar():
    returns = [0.02, -0.01, 0.015, -0.025, 0.01, -0.005, 0.03, -0.015]
    var_95 = quant_risk_engine.calculate_var_historical(returns, 0.95)
    cvar_95 = quant_risk_engine.calculate_cvar_historical(returns, 0.95)

    assert var_95 >= 0
    assert cvar_95 >= var_95
