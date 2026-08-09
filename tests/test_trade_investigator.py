import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.investigation.trade_investigator import trade_investigator

def test_trade_investigation():
    rca = trade_investigator.investigate_order("ord_p23_101")
    assert rca["confidence_score"] > 0.9
    assert len(rca["evidence_items"]) >= 3
