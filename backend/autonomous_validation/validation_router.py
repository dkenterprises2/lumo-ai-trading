from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional

from backend.auth.security import get_optional_current_user
from backend.models.domain import UserModel
from .scenario_factory import ScenarioFactory
from .opportunity_injector import OpportunityInjector
from .validation_report import ValidationReportGenerator

router = APIRouter(prefix="/api/autonomous-validation", tags=["Phase 42 — Autonomous Shadow Validation & Market Replay"])

# Shared memory run history
_run_history: List[Dict[str, Any]] = []

@router.get("/status")
async def get_validation_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch status of autonomous validation framework."""
    return {
        "status": "success",
        "mode": "REPLAY_VALIDATION",
        "live_execution": False,
        "scenarios_available": len(ScenarioFactory.get_all_scenarios()),
        "total_runs_executed": len(_run_history)
    }

@router.get("/scenarios")
async def get_validation_scenarios(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """List all available deterministic market replay validation scenarios (A through J)."""
    scenarios = ScenarioFactory.get_all_scenarios()
    return {
        "status": "success",
        "scenarios": [s.to_dict() for s in scenarios]
    }

@router.post("/run/{scenario_id}")
async def run_validation_scenario(scenario_id: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Run a single deterministic market replay scenario and return state transition audit trail."""
    sc = ScenarioFactory.get_scenario_by_code(scenario_id)
    if not sc:
        raise HTTPException(status_code=404, detail=f"Validation scenario {scenario_id} not found")

    injector = OpportunityInjector()
    result = injector.run_scenario(sc)
    res_dict = result.to_dict()
    _run_history.append(res_dict)

    return {
        "status": "success",
        "scenario_result": res_dict
    }

@router.post("/run-all")
async def run_all_scenarios(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Run all 10 deterministic market replay scenarios (A through J) and compile validation report."""
    scenarios = ScenarioFactory.get_all_scenarios()
    injector = OpportunityInjector()
    results = []
    for sc in scenarios:
        res = injector.run_scenario(sc)
        results.append(res)
        _run_history.append(res.to_dict())

    rep = ValidationReportGenerator.generate_report(results)
    return {
        "status": "success",
        "report": rep
    }

@router.get("/runs")
async def get_validation_runs(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch history of all executed scenario validation runs."""
    return {
        "status": "success",
        "runs": _run_history[-50:]
    }

@router.get("/report")
async def get_validation_report(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Compile and return master autonomous shadow validation report."""
    scenarios = ScenarioFactory.get_all_scenarios()
    injector = OpportunityInjector()
    results = [injector.run_scenario(sc) for sc in scenarios]
    rep = ValidationReportGenerator.generate_report(results)
    return {
        "status": "success",
        "report": rep
    }

@router.get("/lifecycle/{execution_id}")
async def get_lifecycle_audit(execution_id: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch complete microsecond state machine transition timeline for a specific execution ID."""
    matching = [r for r in _run_history if r.get("execution_id") == execution_id]
    if not matching:
        # Fallback to scanning all run histories
        for r in _run_history:
            if r.get("execution_id") == execution_id:
                matching = [r]
                break

    if not matching:
        raise HTTPException(status_code=404, detail=f"Execution audit log {execution_id} not found")

    return {
        "status": "success",
        "execution_id": execution_id,
        "state_history": matching[0].get("state_history", [])
    }
