from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.platform.health_service import health_service
from backend.platform.deployment_service import deployment_service
from backend.platform.canary_controller import canary_controller
from backend.platform.metrics_collector import metrics_collector
from backend.platform.sre_control import sre_control
from backend.platform.chaos_engine import chaos_engine
from backend.platform.dr_runbooks import dr_runbooks

router = APIRouter(tags=["Cloud-Native Platform, DevSecOps & SRE"])

@router.get("/api/platform/health")
async def get_health():
    return health_service.get_health()

@router.get("/api/platform/health/deep")
async def get_deep_health(current_user: UserModel = Depends(get_current_user)):
    return health_service.get_deep_health()

@router.get("/api/platform/readiness")
async def get_readiness():
    return {"status": "READY"}

@router.get("/api/platform/liveness")
async def get_liveness():
    return {"status": "ALIVE"}

@router.get("/api/platform/deployments")
async def list_deployments(current_user: UserModel = Depends(get_current_user)):
    return {"deployments": deployment_service.list_deployments()}

@router.post("/api/platform/deployments/canary")
async def start_canary_deployment(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    app_name = body.get("app", "lumo-api")
    split = body.get("traffic_split_pct", 5)
    return canary_controller.start_canary(app_name, split)

@router.post("/api/platform/deployments/rollback")
async def rollback_deployment(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    deploy_id = body.get("deploy_id", "dep-v3.6.0-101")
    return deployment_service.rollback(deploy_id)

@router.get("/api/platform/observability/metrics")
async def get_metrics(current_user: UserModel = Depends(get_current_user)):
    return metrics_collector.get_metrics_summary()

@router.get("/api/platform/observability/alerts")
async def get_alerts(current_user: UserModel = Depends(get_current_user)):
    return {
        "active_alerts": [
            {"alert_id": "ALT-101", "name": "MemoryUsageWarning", "severity": "WARNING", "service": "lumo-workers"}
        ]
    }

@router.get("/api/platform/sre/error-budgets")
async def get_error_budgets(current_user: UserModel = Depends(get_current_user)):
    return {"error_budgets": sre_control.get_error_budgets()}

@router.get("/api/platform/sre/incidents")
async def get_sre_incidents(current_user: UserModel = Depends(get_current_user)):
    return {"incidents": sre_control.get_incidents()}

@router.post("/api/platform/chaos/experiments")
async def run_chaos_experiment(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    exp_type = body.get("experiment_type", "pod_termination_test")
    ns = body.get("namespace", "staging")
    return chaos_engine.run_experiment(exp_type, ns)

@router.get("/api/platform/chaos/history")
async def get_chaos_history(current_user: UserModel = Depends(get_current_user)):
    return {"history": chaos_engine.list_experiments()}

@router.get("/api/platform/dr/status")
async def get_dr_status(current_user: UserModel = Depends(get_current_user)):
    return {
        "dr_status": "READY",
        "primary_region": "us-east-1",
        "dr_region": "us-west-2",
        "rpo_target_sec": 15,
        "rto_target_min": 5
    }

@router.post("/api/platform/dr/runbooks/{runbook_id}/execute-dry-run")
async def execute_runbook_dry_run(runbook_id: str, current_user: UserModel = Depends(get_current_user)):
    return dr_runbooks.execute_dry_run(runbook_id)
