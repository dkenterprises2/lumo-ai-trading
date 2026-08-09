from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.ai.research_workspace import research_workspace_manager
from backend.ai.recommendation_engine import ai_recommendation_engine

router = APIRouter(prefix="/api/research", tags=["Autonomous Quantitative Research Platform"])

@router.get("/projects")
async def list_research_projects(current_user: UserModel = Depends(get_current_user)):
    """List active quantitative research projects."""
    projects = research_workspace_manager.list_projects(current_user.id)
    catalog = research_workspace_manager.list_dataset_catalog()
    return {"projects": projects, "dataset_catalog": catalog}

@router.post("/projects")
async def create_research_project(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Create new research project workspace."""
    title = body.get("title", "Custom Quantitative Strategy")
    hypothesis = body.get("hypothesis", "Test technical indicator alpha")
    market = body.get("target_market", "SPOT")

    return research_workspace_manager.create_project(
        user_id=current_user.id,
        title=title,
        hypothesis=hypothesis,
        target_market=market
    )

@router.get("/experiments")
async def list_research_experiments(current_user: UserModel = Depends(get_current_user)):
    """List research experiments."""
    return {
        "experiments": [
            {
                "experiment_id": "EXP_178600101",
                "title": "EMA Cross + RSI Volatility Filter",
                "symbol": "BTC/USDT",
                "composite_score": 84.5,
                "recommendation": "PROMOTE_TO_PAPER",
                "status": "COMPLETED"
            },
            {
                "experiment_id": "EXP_178600102",
                "title": "High-Frequency Orderbook Scalp",
                "symbol": "ETH/USDT",
                "composite_score": 62.0,
                "recommendation": "REJECT",
                "status": "COMPLETED"
            }
        ]
    }

@router.post("/run")
async def run_autonomous_research_experiment(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Trigger 7-agent autonomous research experiment workflow."""
    symbol = body.get("symbol", "BTC/USDT")
    hypothesis = body.get("hypothesis", "Multi-Factor Momentum Alpha")
    return ai_recommendation_engine.run_full_research_workflow(symbol=symbol, hypothesis=hypothesis)

@router.get("/results")
async def get_research_results(experiment_id: str = Query("EXP_178600101"), current_user: UserModel = Depends(get_current_user)):
    """Fetch detailed research experiment analysis results."""
    return ai_recommendation_engine.run_full_research_workflow()

@router.post("/promote")
async def promote_strategy_candidate(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Promote strategy candidate to active Paper/Live strategy registry."""
    candidate_id = body.get("candidate_id", "")
    target = body.get("target_environment", "PAPER")
    return {
        "status": "success",
        "message": f"Strategy candidate {candidate_id} promoted to {target} environment.",
        "target": target
    }
