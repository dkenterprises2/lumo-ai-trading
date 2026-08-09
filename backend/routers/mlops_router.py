from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.mlops.experiment_tracker import experiment_tracker
from backend.mlops.feature_store import feature_store_manager
from backend.mlops.model_registry import model_registry_manager
from backend.mlops.retraining_scheduler import retraining_scheduler
from backend.mlops.drift_detector import drift_detector
from backend.mlops.data_quality import data_quality_pipeline
from backend.mlops.shadow_deployment import shadow_deployment_framework
from backend.mlops.canary_rollout import canary_rollout_engine
from backend.mlops.inference_monitor import inference_performance_monitor
from backend.mlops.governance import ai_governance_audit
from backend.mlops.gpu_inference import gpu_inference_pipeline
from backend.mlops.reinforcement_lab import reinforcement_lab

router = APIRouter(prefix="/api/mlops", tags=["ML Ops & Autonomous AI Operations"])

@router.post("/experiment/start")
async def start_experiment(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    name = body.get("name", "New Quantitative Model Experiment")
    description = body.get("description", "")
    return experiment_tracker.start_experiment(name, description)

@router.get("/experiments")
async def list_experiments(current_user: UserModel = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "experiments": experiment_tracker.list_experiments()
    }

@router.post("/feature-store/register")
async def register_feature_version(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    name = body.get("name", "Institutional Feature Set")
    features = body.get("features", ["rsi_14", "macd_diff"])
    version = body.get("version", "1.1.0")
    return feature_store_manager.register_feature_version(name, features, version)

@router.get("/feature-store/versions")
async def list_feature_versions(current_user: UserModel = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "versions": feature_store_manager.list_feature_versions()
    }

@router.post("/model/register")
async def register_model(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    name = body.get("name", "LSTM Trend Predictor")
    version = body.get("version", "1.0.0")
    stage = body.get("stage", "STAGING")
    return model_registry_manager.register_model(name, version, stage)

@router.post("/model/promote")
async def promote_model(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    model_id = body.get("model_id", "MOD-XGB-2026")
    new_stage = body.get("stage", "PRODUCTION")
    ai_governance_audit.log_event(model_id, f"PROMOTED_TO_{new_stage.upper()}", current_user.email)
    return model_registry_manager.promote_model(model_id, new_stage)

@router.get("/model/registry")
async def get_model_registry(current_user: UserModel = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "models": model_registry_manager.get_registry()
    }

@router.post("/retraining/trigger")
async def trigger_retraining_job(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    trigger_type = body.get("trigger_type", "MANUAL")
    model_id = body.get("model_id", "MOD-XGB-2026")
    return retraining_scheduler.trigger_retraining(trigger_type, model_id)

@router.get("/retraining/jobs")
async def list_retraining_jobs(current_user: UserModel = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "jobs": retraining_scheduler.list_jobs()
    }

@router.get("/drift/status")
async def get_drift_status(current_user: UserModel = Depends(get_current_user)):
    return drift_detector.evaluate_drift()

@router.get("/data-quality/reports")
async def get_data_quality_reports(current_user: UserModel = Depends(get_current_user)):
    return data_quality_pipeline.run_quality_check()

@router.post("/shadow/deploy")
async def deploy_shadow_model(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    candidate_id = body.get("candidate_model_id", "MOD-CANDIDATE-01")
    return shadow_deployment_framework.deploy_shadow_model(candidate_id)

@router.post("/canary/start")
async def start_canary_rollout(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    candidate_id = body.get("candidate_model_id", "MOD-CANDIDATE-01")
    traffic_pct = float(body.get("traffic_allocation_pct", 10.0))
    return canary_rollout_engine.start_canary(candidate_id, traffic_pct)

@router.get("/inference/performance")
async def get_inference_performance(current_user: UserModel = Depends(get_current_user)):
    perf = inference_performance_monitor.get_performance_metrics()
    gpu = gpu_inference_pipeline.get_gpu_status()
    return {
        "user_id": current_user.id,
        "inference_metrics": perf,
        "gpu_acceleration": gpu
    }

@router.get("/governance/audit")
async def get_governance_audit_trail(current_user: UserModel = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "audit_logs": ai_governance_audit.list_audit_trail()
    }
