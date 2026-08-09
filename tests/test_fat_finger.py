import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_network.risk.pretrade_checks import pretrade_risk_controller

def test_fat_finger_prevention():
    res = pretrade_risk_controller.validate_pretrade("BTCUSDT", 100.0, 64800.0) # $6.48M > $5M
    assert res["passed"] is False
    assert res["reason"] == "FAT_FINGER_NOTIONAL_EXCEEDED"
