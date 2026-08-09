from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.ai_agents.trend_following_agent import trend_following_agent
from backend.ai_agents.mean_reversion_agent import mean_reversion_agent
from backend.ai_agents.momentum_agent import momentum_agent
from backend.ai_agents.volatility_breakout_agent import volatility_breakout_agent
from backend.ai_agents.offline_trainer import offline_trainer
from backend.ai_agents.shadow_learning_agent import shadow_learning_agent
from backend.ai_agents.explainability import explainability_engine
from backend.ai_agents.agent_governance import agent_governance
from backend.ai_agents.model_registry import model_registry
from backend.ai_agents.safety_guardrails import safety_guardrails
from backend.ai_agents.kill_switch import ai_kill_switch

router = APIRouter(tags=["Autonomous Multi-Agent AI Trading Platform"])

@router.get("/api/ai/agents")
async def list_agents(current_user: UserModel = Depends(get_current_user)):
    return {
        "agents": [
            trend_following_agent.get_info(),
            mean_reversion_agent.get_info(),
            momentum_agent.get_info(),
            volatility_breakout_agent.get_info()
        ]
    }

@router.post("/api/ai/agents")
async def create_agent(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    name = body.get("name", "Custom RL Agent")
    return {"agent_id": f"AGENT-{name.upper().replace(' ', '-')}", "name": name, "status": "ACTIVE"}

@router.get("/api/ai/agents/{agent_id}")
async def get_agent_detail(agent_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"agent_id": agent_id, "name": "Specialist Agent", "status": "ACTIVE", "reward": 14.85}

@router.post("/api/ai/training/start")
async def start_training_job(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    agent_id = body.get("agent_id", "AGENT-TREND-01")
    dataset_version = body.get("dataset_version", "DS-BTC-1H-V1")
    return offline_trainer.run_training_job(agent_id, dataset_version)

@router.get("/api/ai/training/{run_id}")
async def get_training_run(run_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"run_id": run_id, "status": "COMPLETED", "sharpe_ratio": 2.45, "final_reward": 14.85}

@router.post("/api/ai/training/{run_id}/stop")
async def stop_training_run(run_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"run_id": run_id, "status": "STOPPED"}

@router.post("/api/ai/shadow/start")
async def start_shadow_learning(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    symbol = body.get("symbol", "BTC/USDT")
    action = body.get("action", "BUY_SMALL")
    price = body.get("price", 64810.0)
    return shadow_learning_agent.record_shadow_decision(symbol, action, price)

@router.get("/api/ai/shadow/runs")
async def get_shadow_runs(current_user: UserModel = Depends(get_current_user)):
    return {"runs": shadow_learning_agent.list_shadow_trades()}

@router.get("/api/ai/decisions/recent")
async def get_recent_decisions(current_user: UserModel = Depends(get_current_user)):
    return {
        "decisions": [
            explainability_engine.explain_decision("DEC-101"),
            explainability_engine.explain_decision("DEC-102")
        ]
    }

@router.get("/api/ai/explainability/{decision_id}")
async def get_explainability_detail(decision_id: str, current_user: UserModel = Depends(get_current_user)):
    return explainability_engine.explain_decision(decision_id)

@router.post("/api/ai/governance/{version_id}/approve")
async def approve_agent_version(version_id: str, current_user: UserModel = Depends(get_current_user)):
    return agent_governance.approve_version(version_id, current_user.email)

@router.post("/api/ai/governance/{version_id}/reject")
async def reject_agent_version(version_id: str, current_user: UserModel = Depends(get_current_user)):
    return agent_governance.reject_version(version_id, current_user.email)

@router.get("/api/ai/model-registry")
async def get_model_registry(current_user: UserModel = Depends(get_current_user)):
    return {"entries": model_registry.list_entries()}

@router.post("/api/ai/model-registry/promote")
async def promote_model_registry(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    version_id = body.get("version_id", "ppo_bull_v1")
    return model_registry.promote_entry(version_id)

@router.get("/api/ai/safety/events")
async def get_safety_events(current_user: UserModel = Depends(get_current_user)):
    return {"events": safety_guardrails.list_safety_events()}

@router.post("/api/ai/kill-switch/activate")
async def activate_ai_kill_switch(current_user: UserModel = Depends(get_current_user)):
    return ai_kill_switch.activate()

@router.post("/api/ai/kill-switch/deactivate")
async def deactivate_ai_kill_switch(current_user: UserModel = Depends(get_current_user)):
    return ai_kill_switch.deactivate()
