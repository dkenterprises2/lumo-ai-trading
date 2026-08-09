import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.portfolio_assistant.portfolio_explainer import portfolio_explainer

def test_portfolio_explainer():
    res = portfolio_explainer.explain_portfolio()
    assert "summary" in res
    assert "risk_impact" in res
