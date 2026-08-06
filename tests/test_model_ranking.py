import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.training_pipeline import automl_pipeline

def test_model_ranking_leaderboard():
    rankings = automl_pipeline.get_model_rankings()
    assert len(rankings) >= 5
    assert rankings[0]["rank"] == 1
    assert rankings[0]["accuracy"] >= rankings[1]["accuracy"]
