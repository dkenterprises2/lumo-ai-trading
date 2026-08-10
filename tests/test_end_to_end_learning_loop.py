import pytest
import asyncio
from backend.database.session import init_db
from backend.learning.feature_snapshot_builder import feature_snapshot_builder
from backend.learning.trade_outcome_collector import trade_outcome_collector
from backend.learning.performance_dataset_builder import performance_dataset_builder
from backend.learning.weight_optimizer import weight_optimizer
from backend.learning.backtest_validator import backtest_validator
from backend.learning.shadow_weight_evaluator import shadow_weight_evaluator
from backend.learning.learning_governance import learning_governance
from backend.learning.strategy_weight_loader import strategy_weight_loader

@pytest.mark.asyncio
async def test_end_to_end_learning_loop():
    await init_db()

    # Step 1: Feature Snapshot at Entry
    trade_id = "E2E_LEARNING_TRADE_999"
    snapshot = await feature_snapshot_builder.capture_entry_snapshot(
        trade_id=trade_id,
        feature_data={"rsi": 62.0, "macd_histogram": 3.1, "adx": 35.0, "volatility_regime": "NORMAL"}
    )
    assert snapshot.trade_id == trade_id

    # Step 2: Trade Outcome at Exit
    outcome = await trade_outcome_collector.record_trade_outcome({
        "id": trade_id,
        "symbol": "BTC/USDT",
        "side": "LONG",
        "entry_price": 64000.0,
        "exit_price": 65500.0,
        "amount": 0.2,
        "entry_fee": 2.0,
        "exit_fee": 2.0,
        "close_reason": "TAKE_PROFIT",
        "strategy_name": "AI_HYBRID",
        "market_regime": "BULL_TREND"
    })
    assert outcome.trade_id == trade_id
    assert outcome.net_pnl == 296.0

    # Step 3: Performance Dataset Export
    dataset_res = await performance_dataset_builder.build_dataset()
    assert dataset_res["status"] == "success"

    # Step 4: Optuna Weight Optimization
    opt_res = await weight_optimizer.run_optimization(strategy_name="AI_HYBRID", market_regime="NEUTRAL", n_trials=20)
    assert opt_res["status"] == "success"
    exp_id = opt_res["experiment_id"]

    # Step 5: Walk-Forward Backtest Validation
    val_res = await backtest_validator.run_validation(exp_id)
    assert val_res["status"] == "success"
    assert val_res["approved_for_shadow"] is True

    # Step 6: Shadow Evaluation
    shadow_res = await shadow_weight_evaluator.start_evaluation(exp_id)
    assert shadow_res["status"] == "success"
    assert shadow_res["consecutive_passing_windows"] == 3

    # Step 7: Governance Submission & Human Approval
    sub_res = await learning_governance.submit_for_review(exp_id)
    assert sub_res["status"] == "success"

    deploy_res = await learning_governance.approve_and_deploy(
        experiment_id=exp_id,
        approver_email="chief_risk_officer@lumo.trade",
        human_approval=True
    )
    assert deploy_res["status"] == "success"
    assert deploy_res["governance_status"] == "PRODUCTION_APPROVED"

    # Step 8: Strategy Weight Reload & Verification
    active_weights = await strategy_weight_loader.get_active_weights("AI_HYBRID", "NEUTRAL")
    assert "ema_weight" in active_weights
    assert "rsi_weight" in active_weights
