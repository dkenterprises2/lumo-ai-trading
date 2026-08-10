import pytest
import asyncio
from backend.learning.weight_optimizer import weight_optimizer
from backend.database.session import init_db

@pytest.mark.asyncio
async def test_weight_optimizer_trials():
    await init_db()
    res = await weight_optimizer.run_optimization(strategy_name="AI_HYBRID", market_regime="NEUTRAL", n_trials=20)
    assert res["status"] == "success"
    assert "experiment_id" in res
    assert "best_score" in res
    assert "weights" in res
    weights = res["weights"]
    assert "ema_weight" in weights
    assert "rsi_weight" in weights
    assert "macd_weight" in weights
    assert len(weights) == 7

    exps = await weight_optimizer.get_experiments(limit=5)
    assert len(exps) > 0
