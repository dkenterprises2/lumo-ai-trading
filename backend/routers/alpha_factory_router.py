from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.alpha_factory.marketplace.strategy_catalog import strategy_catalog
from backend.alpha_factory.automl.strategy_generator import strategy_generator
from backend.alpha_factory.evolution.genetic_engine import genetic_engine
from backend.alpha_factory.optimization.bayesian_optimizer import bayesian_optimizer
from backend.alpha_factory.validation.walk_forward import walk_forward_engine
from backend.alpha_factory.ensemble.ensemble_composer import ensemble_composer
from backend.alpha_factory.meta_learning.strategy_selector import strategy_selector
from backend.alpha_factory.governance.promotion_pipeline import promotion_pipeline
from backend.alpha_factory.monitoring.drift_detector import drift_detector
from backend.alpha_factory.lineage.alpha_lineage import alpha_lineage_tracker

router = APIRouter(tags=["Institutional Strategy Marketplace & Autonomous Alpha Factory"])

@router.get("/api/marketplace/strategies")
async def list_marketplace_strategies(current_user: UserModel = Depends(get_current_user)):
    return {"strategies": strategy_catalog.list_strategies()}

@router.post("/api/marketplace/strategies")
async def create_marketplace_strategy(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    title = body.get("title", "New Alpha Strategy")
    return {"strategy_id": f"alpha_{title.lower().replace(' ', '_')}", "title": title, "status": "DRAFT"}

@router.get("/api/marketplace/strategies/{strategy_id}")
async def get_marketplace_strategy(strategy_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"strategy_id": strategy_id, "title": "Institutional Momentum Alpha", "sharpe": 2.14}

@router.post("/api/marketplace/strategies/{strategy_id}/publish")
async def publish_marketplace_strategy(strategy_id: str, current_user: UserModel = Depends(get_current_user)):
    return strategy_catalog.publish_strategy(strategy_id)

@router.post("/api/automl/search-spaces")
async def create_automl_search_space(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"space_id": "space_default", "status": "CREATED", "indicators": ["SMA", "EMA", "RSI", "MACD"]}

@router.post("/api/automl/runs")
async def start_automl_run(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    space_id = body.get("search_space_id", "default_space")
    return strategy_generator.generate_candidate(space_id)

@router.get("/api/automl/runs/{run_id}")
async def get_automl_run(run_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"run_id": run_id, "status": "COMPLETED", "best_sharpe": 2.25}

@router.post("/api/evolution/populations")
async def create_genetic_population(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"population_id": "pop_001", "size": 100, "status": "INITIALIZED"}

@router.post("/api/evolution/populations/{population_id}/evolve")
async def evolve_population(population_id: str, current_user: UserModel = Depends(get_current_user)):
    return genetic_engine.evolve_population(population_id)

@router.post("/api/optimization/bayesian/runs")
async def run_bayesian_optimization(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    strategy_id = body.get("strategy_id", "alpha_momentum_v12")
    return bayesian_optimizer.run_optimization(strategy_id)

@router.get("/api/optimization/bayesian/runs/{run_id}")
async def get_bayesian_run(run_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"run_id": run_id, "status": "CONVERGED", "best_sharpe": 2.52}

@router.post("/api/validation/walk-forward")
async def run_walk_forward(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    strategy_id = body.get("strategy_id", "alpha_momentum_v12")
    return walk_forward_engine.run_walk_forward(strategy_id)

@router.post("/api/validation/robustness")
async def run_robustness_test(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"robustness_score": 0.88, "status": "ROBUST"}

@router.post("/api/ensemble/compose")
async def compose_ensemble(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    sids = body.get("strategy_ids", ["alpha_momentum_v12", "stat_arb_pairs"])
    return ensemble_composer.compose_ensemble(sids)

@router.get("/api/ensemble/{ensemble_id}")
async def get_ensemble(ensemble_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"ensemble_id": ensemble_id, "sharpe": 2.78, "components": 2}

@router.post("/api/meta-learning/select")
async def select_meta_learning_strategy(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    regime = body.get("regime", "HIGH_VOLATILITY_BULL")
    return strategy_selector.select_strategies(regime)

@router.post("/api/governance/promote/{strategy_id}")
async def promote_strategy(strategy_id: str, body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    stage = body.get("target_stage", "SHADOW_DEPLOYED")
    return promotion_pipeline.promote_strategy(strategy_id, stage)

@router.post("/api/governance/certify/{strategy_id}")
async def certify_strategy(strategy_id: str, current_user: UserModel = Depends(get_current_user)):
    return promotion_pipeline.certify_strategy(strategy_id)

@router.get("/api/monitoring/drift-alerts")
async def get_drift_alerts(current_user: UserModel = Depends(get_current_user)):
    return {"drift_alerts": drift_detector.get_drift_alerts()}

@router.post("/api/monitoring/retrain/{strategy_id}")
async def retrain_strategy(strategy_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"strategy_id": strategy_id, "status": "RETRAINING_SCHEDULED"}

@router.post("/api/monitoring/retire/{strategy_id}")
async def retire_strategy(strategy_id: str, current_user: UserModel = Depends(get_current_user)):
    return drift_detector.retire_strategy(strategy_id)

@router.get("/api/lineage/{strategy_id}")
async def get_strategy_lineage(strategy_id: str, current_user: UserModel = Depends(get_current_user)):
    return alpha_lineage_tracker.get_lineage(strategy_id)
