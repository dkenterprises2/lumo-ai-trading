from fastapi import APIRouter, Depends, Query
from typing import Dict, List, Any, Optional

from backend.auth.security import get_current_user
from backend.models.domain import UserModel
from backend.autonomous.autonomous_engine import autonomous_engine

router = APIRouter(prefix="/api/autonomous", tags=["Phase 41 — Autonomous Shadow Trading Engine"])

@router.get("/status")
async def get_autonomous_status(current_user: UserModel = Depends(get_current_user)):
    """Fetch current autonomous engine status, mode, and paper/shadow safety flags."""
    return {"status": "success", "engine": autonomous_engine.get_status()}

@router.post("/start")
async def start_autonomous_engine(current_user: UserModel = Depends(get_current_user)):
    """Start autonomous shadow trading scan and execution engine."""
    res = autonomous_engine.start()
    return res

@router.post("/pause")
async def pause_autonomous_engine(current_user: UserModel = Depends(get_current_user)):
    """Pause autonomous shadow trading engine (prevents new execution jobs)."""
    res = autonomous_engine.pause()
    return res

@router.post("/resume")
async def resume_autonomous_engine(current_user: UserModel = Depends(get_current_user)):
    """Resume autonomous shadow trading engine."""
    res = autonomous_engine.resume()
    return res

@router.post("/stop")
async def stop_autonomous_engine(current_user: UserModel = Depends(get_current_user)):
    """Stop autonomous shadow trading engine and close open shadow positions."""
    res = autonomous_engine.stop()
    return res

@router.get("/metrics")
async def get_autonomous_metrics(current_user: UserModel = Depends(get_current_user)):
    """Fetch autonomous shadow trading performance metrics."""
    return {"status": "success", "metrics": autonomous_engine.get_metrics()}

@router.get("/executions")
async def get_autonomous_executions(current_user: UserModel = Depends(get_current_user)):
    """Fetch blotter of all autonomous shadow executions and state transition timelines."""
    return {"status": "success", "executions": autonomous_engine.get_executions()}
