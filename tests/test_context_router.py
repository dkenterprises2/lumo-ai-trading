import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.copilot.copilot_service import copilot_service

def test_context_routing():
    res = copilot_service.process_chat("ws_quant_team", "user_01", "Execution costs")
    assert res["workspace_id"] == "ws_quant_team"
