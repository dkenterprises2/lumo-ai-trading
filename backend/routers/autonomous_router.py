from fastapi import APIRouter, Depends, Query
from typing import Dict, List, Any, Optional

from backend.auth.security import get_optional_current_user
from backend.models.domain import UserModel
from backend.autonomous.autonomous_engine import autonomous_engine

router = APIRouter(prefix="/api/autonomous", tags=["Phase 41 — Autonomous Shadow Trading Engine"])

@router.get("/status")
async def get_autonomous_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch current autonomous engine status for the current user."""
    from trader import trader_manager
    user_id = getattr(current_user, "id", 1) if (current_user and hasattr(current_user, "id")) else 1
    trader_inst = await trader_manager.get_trader_for_user(user_id)
    user_auto_enabled = getattr(trader_inst, "autonomous_engine_enabled", True)
    
    engine_status = autonomous_engine.get_status()
    engine_status["status"] = "RUNNING" if user_auto_enabled else "STOPPED"
    return {"status": "success", "engine": engine_status}

@router.post("/start")
async def start_autonomous_engine(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Start autonomous shadow trading scan and execution engine for current user."""
    from trader import trader_manager
    user_id = getattr(current_user, "id", 1) if (current_user and hasattr(current_user, "id")) else 1
    trader_inst = await trader_manager.get_trader_for_user(user_id)
    trader_inst.autonomous_engine_enabled = True
    await trader_inst.save_portfolio_async()
    return {"status": "success", "engine_state": "RUNNING", "message": "Autonomous Engine ACTIVATED for your account"}

@router.post("/pause")
async def pause_autonomous_engine(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Pause autonomous shadow trading engine for current user."""
    from trader import trader_manager
    user_id = getattr(current_user, "id", 1) if (current_user and hasattr(current_user, "id")) else 1
    trader_inst = await trader_manager.get_trader_for_user(user_id)
    trader_inst.autonomous_engine_enabled = False
    await trader_inst.save_portfolio_async()
    return {"status": "success", "engine_state": "PAUSED", "message": "Autonomous Engine PAUSED for your account"}

@router.post("/resume")
async def resume_autonomous_engine(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Resume autonomous shadow trading engine for current user."""
    from trader import trader_manager
    user_id = getattr(current_user, "id", 1) if (current_user and hasattr(current_user, "id")) else 1
    trader_inst = await trader_manager.get_trader_for_user(user_id)
    trader_inst.autonomous_engine_enabled = True
    await trader_inst.save_portfolio_async()
    return {"status": "success", "engine_state": "RUNNING", "message": "Autonomous Engine RESUMED for your account"}

@router.post("/stop")
async def stop_autonomous_engine(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Stop autonomous shadow trading engine for current user."""
    from trader import trader_manager
    user_id = getattr(current_user, "id", 1) if (current_user and hasattr(current_user, "id")) else 1
    trader_inst = await trader_manager.get_trader_for_user(user_id)
    trader_inst.autonomous_engine_enabled = False
    await trader_inst.save_portfolio_async()
    return {"status": "success", "engine_state": "STOPPED", "message": "Autonomous Engine STOPPED for your account"}

@router.get("/metrics")
async def get_autonomous_metrics(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch autonomous shadow trading performance metrics."""
    return {"status": "success", "metrics": autonomous_engine.get_metrics()}

@router.get("/executions")
async def get_autonomous_executions(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch blotter of all autonomous shadow executions and state transition timelines."""
    execs = list(autonomous_engine.get_executions())
    try:
        from backend.autonomous_validation.validation_router import _run_history
        for r in _run_history:
            execs.append({
                "execution_id": r.get("execution_id", "EXEC-VAL"),
                "symbol": r.get("symbol", "BTC/USDT"),
                "buy_exchange": r.get("buy_exchange", "Binance"),
                "sell_exchange": r.get("sell_exchange", "Coinbase"),
                "selected_algorithm": "DETERMINISTIC_REPLAY",
                "status": r.get("actual_terminal_state", "COMPLETED"),
                "fees": r.get("fees", 0.0),
                "net_pnl": r.get("realized_pnl", 0.0),
                "state_history": r.get("state_history", []),
                "timeline": r.get("state_history", [])
            })
    except Exception:
        pass
    return {"status": "success", "executions": execs}

@router.get("/runtime-health")
async def get_runtime_health(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch 24x7 runtime supervisor and subsystem watchdog health telemetry."""
    from backend.autonomous.runtime_health import runtime_watchdog
    from backend.autonomous.runtime_supervisor import runtime_supervisor
    return {
        "status": "success",
        "supervisor": runtime_supervisor.get_status(),
        "health": runtime_watchdog.get_runtime_health()
    }

@router.get("/session")
async def get_current_session(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch active autonomous session details."""
    from backend.autonomous.runtime_checkpoint import checkpoint_manager
    return {
        "status": "success",
        "session": checkpoint_manager.current_session.to_dict()
    }

@router.get("/sessions")
async def get_all_sessions(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch history of all autonomous sessions."""
    from backend.autonomous.runtime_checkpoint import checkpoint_manager
    return {
        "status": "success",
        "sessions": [s.to_dict() for s in checkpoint_manager.sessions_history]
    }

@router.get("/reconciliation")
async def get_pnl_reconciliation(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Perform periodic PnL and cash/equity reconciliation audit."""
    m = autonomous_engine.execution_manager
    positions = list(m.positions.values())
    closed_pos = [p for p in positions if p.status == "CLOSED"]
    
    total_net_pnl = sum(p.net_pnl for p in closed_pos)
    total_fees = sum(p.entry_fees for p in closed_pos)
    total_gross = sum(p.gross_pnl for p in closed_pos)
    
    reconciled = round(total_gross - total_fees, 2) == round(total_net_pnl, 2) or len(closed_pos) == 0

    return {
        "status": "success" if reconciled else "RECONCILIATION_FAILED",
        "reconciled": reconciled,
        "closed_positions_count": len(closed_pos),
        "total_gross_pnl": round(total_gross, 2),
        "total_fees": round(total_fees, 2),
        "total_net_pnl": round(total_net_pnl, 2)
    }

@router.get("/system-resources")
async def get_system_resources(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch live CPU, memory, task count, DB connections, and WS client telemetry."""
    from backend.telemetry.resource_monitor import resource_monitor
    return resource_monitor.get_current_resources()
