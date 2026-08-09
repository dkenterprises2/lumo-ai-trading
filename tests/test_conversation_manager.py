import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.copilot.copilot_service import copilot_service

def test_copilot_chat():
    res = copilot_service.process_chat("ws_quant_team", "user_01", "Explain risk")
    assert res["status"] == "COMPLETED"
    assert "response" in res
    assert len(res["citations"]) >= 1
