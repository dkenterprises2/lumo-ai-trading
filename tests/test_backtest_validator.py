import pytest
import asyncio
from backend.learning.weight_optimizer import weight_optimizer
from backend.learning.backtest_validator import backtest_validator
from backend.database.session import init_db

@pytest.mark.asyncio
async def test_backtest_validator_checks():
    await init_db()
    exp = await weight_optimizer.run_optimization(strategy_name="AI_HYBRID", market_regime="NEUTRAL", n_trials=20)
    exp_id = exp["experiment_id"]

    val = await backtest_validator.run_validation(exp_id)
    assert val["status"] == "success"
    assert val["experiment_id"] == exp_id
    assert "approved_for_shadow" in val
    assert val["candidate_sharpe"] >= val["current_sharpe"]
    assert "validation_report" in val

    validations = await backtest_validator.get_validations(limit=5)
    assert len(validations) > 0
