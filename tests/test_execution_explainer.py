import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.investigation.trade_investigator import trade_investigator

def test_execution_explainer():
    rca = trade_investigator.investigate_order("ord_p23_102")
    assert rca["primary_slippage_venue"] == "BINANCE"
