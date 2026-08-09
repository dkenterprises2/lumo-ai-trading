import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.model_registry import model_registry

def test_model_registry_promotions():
    ent = model_registry.promote_entry("ppo_bull_v2", "APPROVED")
    assert ent["version_id"] == "ppo_bull_v2"
    assert ent["status"] == "APPROVED"
