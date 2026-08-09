from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.research.data_lake.parquet_store import parquet_store
from backend.research.feature_store.feature_registry import feature_registry
from backend.research.factors.factor_registry import factor_registry
from backend.research.experiments.experiment_tracker import experiment_tracker
from backend.research.datasets.snapshot_manager import snapshot_manager
from backend.research.notebooks.workspace_manager import workspace_manager
from backend.research.compute.distributed_scheduler import distributed_scheduler
from backend.research.governance.research_approval import research_approval
from backend.research.alpha.alpha_pipeline import alpha_pipeline

router = APIRouter(tags=["Enterprise Data Lake & Quant Research Platform"])

@router.get("/api/research/datasets")
async def list_datasets(current_user: UserModel = Depends(get_current_user)):
    return {
        "datasets": [
            {"dataset_id": "market_data_ohlcv", "name": "Global Multi-Exchange OHLCV", "partitions": 1420},
            {"dataset_id": "orderbook_l2_ticks", "name": "Level-2 Orderbook Snapshots", "partitions": 5800}
        ]
    }

@router.get("/api/research/datasets/{dataset_id}")
async def get_dataset(dataset_id: str, current_user: UserModel = Depends(get_current_user)):
    return {
        "dataset_id": dataset_id,
        "partitions": parquet_store.list_partitions(dataset_id),
        "stats": parquet_store.get_stats()
    }

@router.post("/api/research/datasets/{dataset_id}/snapshot")
async def create_snapshot(dataset_id: str, current_user: UserModel = Depends(get_current_user)):
    return snapshot_manager.create_snapshot(dataset_id)

@router.get("/api/research/features")
async def list_features(current_user: UserModel = Depends(get_current_user)):
    return {"features": feature_registry.list_features()}

@router.get("/api/research/features/{feature_name}")
async def get_feature(feature_name: str, current_user: UserModel = Depends(get_current_user)):
    return feature_registry.get_feature(feature_name)

@router.post("/api/research/features/{feature_name}/materialize")
async def materialize_feature(feature_name: str, current_user: UserModel = Depends(get_current_user)):
    return feature_registry.materialize(feature_name)

@router.get("/api/research/factors")
async def list_factors(current_user: UserModel = Depends(get_current_user)):
    return {"factors": factor_registry.list_factors()}

@router.post("/api/research/factors/run")
async def run_factor(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    factor_id = body.get("factor_id", "momentum_20d")
    return factor_registry.run_factor(factor_id)

@router.get("/api/research/experiments")
async def list_experiments(current_user: UserModel = Depends(get_current_user)):
    return {"experiments": experiment_tracker.list_experiments()}

@router.post("/api/research/experiments")
async def create_experiment(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    name = body.get("name", "New Alpha Search")
    return experiment_tracker.create_experiment(name)

@router.get("/api/research/experiments/{experiment_id}/leaderboard")
async def get_experiment_leaderboard(experiment_id: str, current_user: UserModel = Depends(get_current_user)):
    return {
        "experiment_id": experiment_id,
        "leaderboard": [
            {"rank": 1, "run_id": "run_001", "sharpe": 2.45, "ic": 0.092},
            {"rank": 2, "run_id": "run_002", "sharpe": 2.12, "ic": 0.078}
        ]
    }

@router.get("/api/research/notebooks/workspaces")
async def list_workspaces(current_user: UserModel = Depends(get_current_user)):
    return {"workspaces": workspace_manager.list_workspaces()}

@router.post("/api/research/compute/jobs")
async def submit_compute_job(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    job_type = body.get("job_type", "parameter_sweep")
    return distributed_scheduler.submit_job(job_type)

@router.get("/api/research/data-quality/alerts")
async def get_data_quality_alerts(current_user: UserModel = Depends(get_current_user)):
    return {
        "quality_alerts": [
            {"alert_id": "DQ-101", "dataset": "orderbook_l2", "anomaly": "Timestamp gap detected", "severity": "MEDIUM"}
        ]
    }

@router.post("/api/research/approvals/{approval_id}/review")
async def review_research_approval(approval_id: str, body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    decision = body.get("decision", "APPROVED_FOR_SHADOW")
    return research_approval.review_approval(approval_id, decision)

@router.get("/api/research/alpha/candidates")
async def list_alpha_candidates(current_user: UserModel = Depends(get_current_user)):
    return {"candidates": alpha_pipeline.get_candidates()}

@router.post("/api/research/alpha/validate")
async def validate_alpha_candidate(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    alpha_id = body.get("alpha_id", "alpha_micro_depth")
    return alpha_pipeline.validate_alpha(alpha_id)
