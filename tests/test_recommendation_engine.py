import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.recommendation_engine import ai_recommendation_engine

def test_ai_recommendation_engine_full_workflow():
    res = ai_recommendation_engine.run_full_research_workflow(symbol="BTC/USDT", hypothesis="Trend Reversal Alpha")
    assert "experiment_id" in res
    assert res["recommendation"]["recommendation"] in ["PROMOTE_TO_PAPER", "PROMOTE_TO_LIVE", "REJECT"]
    assert res["recommendation"]["composite_score"] > 0
