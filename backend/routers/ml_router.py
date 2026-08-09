from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.ai.model_registry import ml_model_registry
from backend.ai.feature_store_v2 import feature_store_v2
from backend.ai.training_pipeline import automl_pipeline

router = APIRouter(prefix="/api/ml", tags=["AI Intelligence & Autonomous Optimization"])

@router.get("/models")
async def list_registered_ml_models(current_user: UserModel = Depends(get_current_user)):
    """Return all registered ML models with accuracy and Champion flag."""
    return {"models": ml_model_registry.list_models()}

@router.post("/train")
async def trigger_model_training(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Trigger automated AutoML model training experiment."""
    algo = body.get("algorithm", "XGBOOST")
    params = body.get("parameters")
    return automl_pipeline.run_training_experiment(algorithm=algo, parameters=params)

@router.post("/optimize")
async def trigger_hyperparameter_optimization(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Trigger Grid/Random search hyperparameter optimization."""
    algo = body.get("algorithm", "XGBOOST")
    return automl_pipeline.run_hyperparameter_optimization(algorithm=algo)

@router.get("/rankings")
async def get_model_leaderboard(current_user: UserModel = Depends(get_current_user)):
    """Return strategy & ML model leaderboard rankings."""
    return {"rankings": automl_pipeline.get_model_rankings()}

@router.post("/promote")
async def promote_champion_model(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Promote specified model to CHAMPION."""
    model_id = body.get("model_id", "")
    return ml_model_registry.promote_champion(model_id)

@router.post("/rollback")
async def rollback_champion_model(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Rollback champion to previous model."""
    prev_id = body.get("previous_model_id", "xgb_prod_v2")
    return ml_model_registry.rollback_champion(prev_id)

@router.get("/features")
async def get_feature_store_metadata(symbol: str = Query("BTC/USDT"), current_user: UserModel = Depends(get_current_user)):
    """Fetch latest feature vector for symbol from Feature Store."""
    feat_data = feature_store_v2.get_latest_features(symbol)
    meta = feature_store_v2.list_feature_metadata()
    return {
        "symbol": symbol,
        "feature_vector": feat_data,
        "metadata": meta
    }
