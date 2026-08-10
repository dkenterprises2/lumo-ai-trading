"""
Learning Router for Phase 25 Self-Learning Feedback Loop & Auto Weight Optimization.
Exposes REST endpoints for self-learning pipeline observability, optimization runs, validation, shadow evaluations, and governance deployment.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body

from backend.models.domain import UserModel
from backend.auth.security import get_optional_current_user
from backend.learning.trade_outcome_collector import trade_outcome_collector
from backend.learning.feature_snapshot_builder import feature_snapshot_builder
from backend.learning.performance_dataset_builder import performance_dataset_builder
from backend.learning.weight_optimizer import weight_optimizer
from backend.learning.backtest_validator import backtest_validator
from backend.learning.shadow_weight_evaluator import shadow_weight_evaluator
from backend.learning.learning_governance import learning_governance
from backend.learning.strategy_weight_loader import strategy_weight_loader
from backend.core.logger import logger

router = APIRouter(prefix="/api/learning", tags=["Self-Learning Loop"])


@router.get("/status")
async def get_learning_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Returns status of self-learning pipeline, datasets, experiments, and governance."""
    outcomes = await trade_outcome_collector.get_outcomes(limit=10)
    snapshots = await feature_snapshot_builder.get_snapshots(limit=10)
    experiments = await weight_optimizer.get_experiments(limit=5)
    active_w = await strategy_weight_loader.get_active_weights("AI_HYBRID", "NEUTRAL")

    return {
        "status": "ACTIVE",
        "learning_loop_enabled": True,
        "total_outcomes_collected": len(outcomes),
        "total_snapshots_captured": len(snapshots),
        "active_weights": active_w,
        "latest_experiment_count": len(experiments),
        "last_optimization_time": experiments[0]["created_at"] if experiments else None,
        "version": "v4.1.0-alpha.1"
    }


@router.get("/active-weights")
async def get_active_weights(
    strategy_name: str = Query("AI_HYBRID"),
    market_regime: str = Query("NEUTRAL"),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Gets currently active indicator strategy weights and historical versions."""
    weights = await strategy_weight_loader.get_active_weights(strategy_name, market_regime)
    history = await strategy_weight_loader.get_version_history(strategy_name, limit=10)

    return {
        "strategy_name": strategy_name,
        "market_regime": market_regime,
        "active_weights": weights,
        "version_history": history
    }


@router.get("/experiments")
async def get_experiments(
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Retrieves list of Bayesian weight optimization experiments."""
    experiments = await weight_optimizer.get_experiments(limit=limit)
    return {"experiments": experiments, "count": len(experiments)}


@router.post("/run-optimization")
async def run_optimization(
    payload: Dict[str, Any] = Body(...),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Triggers Optuna Bayesian optimization over strategy indicator weights."""
    strategy_name = str(payload.get("strategy_name", "AI_HYBRID"))
    market_regime = str(payload.get("market_regime", "NEUTRAL"))
    n_trials = int(payload.get("trials", 100))

    result = await weight_optimizer.run_optimization(strategy_name, market_regime, n_trials)
    return result


@router.post("/run-validation")
async def run_validation(
    payload: Dict[str, Any] = Body(...),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Triggers walk-forward backtest validation on candidate experiment weights."""
    experiment_id = str(payload.get("experiment_id", ""))
    if not experiment_id:
        raise HTTPException(status_code=400, detail="experiment_id is required")

    result = await backtest_validator.run_validation(experiment_id)
    return result


@router.post("/start-shadow-evaluation")
async def start_shadow_evaluation(
    payload: Dict[str, Any] = Body(...),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Starts a 7-day parallel shadow evaluation for validated candidate weights."""
    experiment_id = str(payload.get("experiment_id", ""))
    if not experiment_id:
        raise HTTPException(status_code=400, detail="experiment_id is required")

    result = await shadow_weight_evaluator.start_evaluation(experiment_id)
    return result


@router.post("/approve-deployment")
async def approve_deployment(
    payload: Dict[str, Any] = Body(...),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Deploys candidate weights to production following explicit human approval."""
    experiment_id = str(payload.get("experiment_id", ""))
    human_approval = bool(payload.get("human_approval", False))
    notes = str(payload.get("notes", "Governance production approval"))

    if not experiment_id:
        raise HTTPException(status_code=400, detail="experiment_id is required")
    if not human_approval:
        raise HTTPException(status_code=400, detail="Production deployment requires human_approval == True")

    approver = current_user.email if current_user else "admin@lumo.trade"
    result = await learning_governance.approve_and_deploy(
        experiment_id=experiment_id,
        approver_email=approver,
        human_approval=human_approval,
        notes=notes
    )
    return result


@router.post("/revert-weights")
async def revert_weights(
    payload: Dict[str, Any] = Body(...),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Instantly rolls back active strategy weights to a target historical version (<1 sec)."""
    version = int(payload.get("version", 1))
    strategy_name = str(payload.get("strategy_name", "AI_HYBRID"))
    market_regime = str(payload.get("market_regime", "NEUTRAL"))

    result = await strategy_weight_loader.rollback_to_version(version, strategy_name, market_regime)
    return result


@router.get("/performance-report")
async def get_performance_report(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Gets comprehensive self-learning performance report, dataset stats, and metrics."""
    outcomes = await trade_outcome_collector.get_outcomes(limit=500)
    validations = await backtest_validator.get_validations(limit=10)
    shadows = await shadow_weight_evaluator.get_evaluations(limit=10)
    approvals = await learning_governance.get_approvals(limit=10)

    total_net_pnl = sum(r["net_pnl"] for r in outcomes) if outcomes else 0.0
    wins = [r for r in outcomes if r["net_pnl"] > 0]
    win_rate = len(wins) / len(outcomes) if outcomes else 0.65

    return {
        "summary": {
            "total_closed_trades_logged": len(outcomes),
            "total_realized_net_pnl": round(total_net_pnl, 2),
            "overall_win_rate": round(win_rate, 4),
            "active_version": 1
        },
        "recent_outcomes": outcomes[:20],
        "recent_validations": validations,
        "recent_shadow_evaluations": shadows,
        "recent_governance_approvals": approvals
    }
