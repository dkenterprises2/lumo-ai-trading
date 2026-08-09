import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.guardrails.policy_engine import guardrail_policy_engine

def test_validation_guardrails():
    eval_res = guardrail_policy_engine.evaluate_action("LIVE_DEPLOYMENT", "VIEWER")
    assert eval_res["decision"] == "BLOCK"
