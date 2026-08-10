import pytest
import asyncio
from backend.learning.weight_optimizer import weight_optimizer
from backend.learning.shadow_weight_evaluator import shadow_weight_evaluator
from backend.database.session import init_db

@pytest.mark.asyncio
async def test_shadow_weight_evaluator():
    await init_db()
    exp = await weight_optimizer.run_optimization(strategy_name="AI_HYBRID", market_regime="NEUTRAL", n_trials=20)
    exp_id = exp["experiment_id"]

    eval_res = await shadow_weight_evaluator.start_evaluation(exp_id)
    assert eval_res["status"] == "success"
    assert "shadow_id" in eval_res
    assert eval_res["days_evaluated"] == 7
    assert eval_res["consecutive_passing_windows"] == 3

    evals = await shadow_weight_evaluator.get_evaluations(limit=5)
    assert len(evals) > 0
