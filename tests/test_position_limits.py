import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.risk.pretrade_checks import pretrade_risk_controller

def test_position_limits():
    res = pretrade_risk_controller.validate_pretrade("BTCUSDT", 2.0, 64800.0)
    assert res["passed"] is True
