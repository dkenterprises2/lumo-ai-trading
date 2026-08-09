import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.sre_control import sre_control

def test_error_budgets():
    ebs = sre_control.get_error_budgets()
    assert len(ebs) >= 2
    assert ebs[0]["budget_remaining_pct"] > 0
