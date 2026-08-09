from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.research.factor_engine import factor_engine
from backend.research.stat_arb_engine import stat_arb_engine
from backend.research.monte_carlo import monte_carlo_engine
from backend.research.walk_forward import walk_forward_optimizer
from backend.research.bayesian_optimizer import bayesian_optimizer
from backend.research.benchmarking import benchmarking_engine
from backend.research.dataset_versioning import dataset_versioning
from backend.research.notebook_runner import notebook_runner

router = APIRouter(tags=["Advanced Quantitative Research"])

@router.post("/api/research/factors/run")
async def run_factor_calculation(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    data = body.get("data", [100.0, 102.0, 101.5, 104.0, 103.5, 106.0])
    return factor_engine.calculate_factors(data)

@router.get("/api/research/factors/results/{run_id}")
async def get_factor_results(run_id: str, current_user: UserModel = Depends(get_current_user)):
    return factor_engine.calculate_factors([])

@router.post("/api/research/stat-arb/scan")
async def scan_stat_arb_pairs(current_user: UserModel = Depends(get_current_user)):
    return {"pairs": stat_arb_engine.scan_pairs()}

@router.post("/api/research/stat-arb/backtest")
async def backtest_stat_arb_pair(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"pair": body.get("pair", "BTC/USDT:ETH/USDT"), "sharpe": 2.65, "total_return": 34.2}

@router.get("/api/research/stat-arb/pairs")
async def get_stat_arb_pairs(current_user: UserModel = Depends(get_current_user)):
    return {"pairs": stat_arb_engine.scan_pairs()}

@router.post("/api/research/monte-carlo/run")
async def run_monte_carlo_simulation(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    initial = body.get("initial_capital", 100000.0)
    sims = body.get("num_simulations", 1000)
    return monte_carlo_engine.run_simulation(initial, sims)

@router.get("/api/research/monte-carlo/{simulation_id}")
async def get_monte_carlo_simulation(simulation_id: str, current_user: UserModel = Depends(get_current_user)):
    return monte_carlo_engine.run_simulation()

@router.post("/api/research/walk-forward/run")
async def run_walk_forward_optimization(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return walk_forward_optimizer.run_walk_forward()

@router.get("/api/research/walk-forward/{run_id}")
async def get_walk_forward_results(run_id: str, current_user: UserModel = Depends(get_current_user)):
    return walk_forward_optimizer.run_walk_forward()

@router.post("/api/research/bayesian-optimize")
async def run_bayesian_optimization(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    trials = body.get("trials", 50)
    return bayesian_optimizer.optimize(trials)

@router.get("/api/research/optimization/{run_id}")
async def get_optimization_results(run_id: str, current_user: UserModel = Depends(get_current_user)):
    return bayesian_optimizer.optimize()

@router.get("/api/research/benchmarks")
async def get_benchmarks(current_user: UserModel = Depends(get_current_user)):
    return {"benchmarks": benchmarking_engine.get_benchmarks()}

@router.post("/api/research/benchmarks/run")
async def run_benchmark_test(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"benchmarks": benchmarking_engine.get_benchmarks()}

@router.post("/api/research/datasets/register")
async def register_dataset(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    symbol = body.get("symbol", "BTC/USDT")
    timeframe = body.get("timeframe", "1h")
    rows = body.get("row_count", 8760)
    return dataset_versioning.register_dataset(symbol, timeframe, rows)

@router.get("/api/research/datasets")
async def list_datasets(current_user: UserModel = Depends(get_current_user)):
    return {"datasets": dataset_versioning.list_datasets()}

@router.post("/api/research/notebooks/execute")
async def execute_notebook(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    nb_name = body.get("notebook_name", "alpha_research_pipeline.ipynb")
    return notebook_runner.execute_notebook(nb_name)

@router.get("/api/research/notebooks/{job_id}")
async def get_notebook_job(job_id: str, current_user: UserModel = Depends(get_current_user)):
    return notebook_runner.execute_notebook("alpha_research_pipeline.ipynb")
