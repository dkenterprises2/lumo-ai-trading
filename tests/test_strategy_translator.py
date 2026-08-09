import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.nlp_trading.intent_parser import strategy_translator

def test_strategy_translator():
    intent = strategy_translator.parse_intent("Create momentum strategy")
    assert intent["intent"] == "CREATE_STRATEGY"
    assert "generated_dsl" in intent
    assert intent["requires_confirmation"] is True
