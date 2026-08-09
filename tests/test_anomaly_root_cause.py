import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.investigation.trade_investigator import trade_investigator

def test_root_cause_analysis():
    rca = trade_investigator.investigate_order("ord_p23_103")
    assert "root_cause" in rca
