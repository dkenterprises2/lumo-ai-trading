import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.execution_rl_agent import execution_rl_agent

def test_execution_optimization():
    opt = execution_rl_agent.optimize_execution_params("TWAP")
    assert opt["recommended_algo"] == "TWAP"
    assert opt["optimal_slice_interval_sec"] == 240
