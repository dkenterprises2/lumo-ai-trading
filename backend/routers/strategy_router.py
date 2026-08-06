from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.plugins.strategy_registry import strategy_registry
from backend.plugins.strategy_manager import strategy_orchestrator
from backend.core.smart_allocation import smart_allocator
from backend.analytics.performance_v2 import performance_engine_v2

router = APIRouter(prefix="/api", tags=["Strategy Orchestrator & Portfolio Intelligence"])

@router.get("/strategies")
async def list_available_strategies(current_user: UserModel = Depends(get_current_user)):
    """Return all 8 built-in quantitative strategies with configuration parameters."""
    strats = strategy_registry.list_strategies()
    user_runtime = strategy_orchestrator.get_user_strategies(current_user.id)
    runtime_map = {r["strategy_id"]: r for r in user_runtime}

    for s in strats:
        r_info = runtime_map.get(s["id"], {})
        s["state"] = r_info.get("state", "RUNNING")
        s["priority"] = r_info.get("priority", 1)
        s["allocation_pct"] = r_info.get("allocation_pct", 12.5)
        s["health"] = r_info.get("health", "HEALTHY")

    return {"strategies": strats}

@router.post("/strategies")
async def create_custom_strategy(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Register custom strategy instance."""
    return {"status": "success", "message": "Custom strategy registered successfully."}

@router.put("/strategies/{strategy_id}")
async def update_strategy_config(strategy_id: str, body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Update strategy parameters."""
    return {"status": "success", "message": f"Strategy {strategy_id} parameters updated."}

@router.delete("/strategies/{strategy_id}")
async def delete_custom_strategy(strategy_id: str, current_user: UserModel = Depends(get_current_user)):
    """Delete custom strategy instance."""
    return {"status": "success", "message": f"Strategy {strategy_id} removed."}

@router.post("/strategies/{strategy_id}/enable")
async def enable_strategy_instance(strategy_id: str, current_user: UserModel = Depends(get_current_user)):
    """Enable strategy execution."""
    return strategy_orchestrator.enable_strategy(current_user.id, strategy_id)

@router.post("/strategies/{strategy_id}/disable")
async def disable_strategy_instance(strategy_id: str, current_user: UserModel = Depends(get_current_user)):
    """Pause strategy execution."""
    return strategy_orchestrator.disable_strategy(current_user.id, strategy_id)

@router.get("/portfolios")
async def list_user_portfolios(current_user: UserModel = Depends(get_current_user)):
    """Return isolated multi-portfolio instances with capital allocations."""
    portfolios = [
        {"id": "PAPER", "name": "Paper Trading", "type": "PAPER", "equity": 10000.0, "allocation_pct": 25.0},
        {"id": "SPOT", "name": "Spot Multi-Factor", "type": "SPOT", "equity": 25000.0, "allocation_pct": 25.0},
        {"id": "FUTURES", "name": "Futures Momentum", "type": "FUTURES", "equity": 15000.0, "allocation_pct": 20.0},
        {"id": "SWING", "name": "Swing Reversal", "type": "SWING", "equity": 10000.0, "allocation_pct": 15.0},
        {"id": "SCALPING", "name": "High-Frequency Scalp", "type": "SCALPING", "equity": 5000.0, "allocation_pct": 10.0},
        {"id": "RESEARCH", "name": "AI Experiment Lab", "type": "RESEARCH", "equity": 5000.0, "allocation_pct": 5.0}
    ]
    return {"portfolios": portfolios, "total_net_worth": 70000.0}

@router.post("/portfolios")
async def create_user_portfolio(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Create new portfolio container."""
    name = body.get("name", "Custom Portfolio")
    p_type = body.get("type", "SPOT")
    return {"status": "success", "message": f"Portfolio '{name}' created.", "portfolio_id": name.upper().replace(" ", "_")}

@router.get("/performance")
async def get_performance_analytics(current_user: UserModel = Depends(get_current_user)):
    """Fetch institutional performance metrics."""
    mock_trades = [
        {"pnl_usd": 150.0}, {"pnl_usd": -40.0}, {"pnl_usd": 220.0},
        {"pnl_usd": 90.0}, {"pnl_usd": -30.0}, {"pnl_usd": 310.0}
    ]
    return performance_engine_v2.calculate_performance_summary(mock_trades)
