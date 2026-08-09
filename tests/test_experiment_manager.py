import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai.research_agents import BacktestAgent, RiskEvaluationAgent, PerformanceEvaluationAgent

def test_experiment_agent_pipeline():
    bt_agent = BacktestAgent()
    bt_res = bt_agent.run("BTC/USDT")
    assert bt_res["total_trades"] > 0

    risk_agent = RiskEvaluationAgent()
    risk_res = risk_agent.run(bt_res)
    assert risk_res["risk_status"] == "APPROVED"

    perf_agent = PerformanceEvaluationAgent()
    perf_res = perf_agent.run(bt_res)
    assert perf_res["sharpe_ratio"] > 0
