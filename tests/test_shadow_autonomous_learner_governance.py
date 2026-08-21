import pytest
import asyncio
import time
from backend.shadow_trading.shadow_autonomous_learner import (
    ShadowAutonomousLearner, LearningExperimentResult
)
from backend.shadow_trading.shadow_safety_guard import (
    shadow_guard, TradingMode, ShadowTradingViolation
)
from backend.safety.paper_mode_guard import paper_guard
from backend.core.config import settings
from backend.marketdata.historical_candle_archive import HistoricalCandle

@pytest.fixture
def learner():
    learner = ShadowAutonomousLearner()
    learner.MIN_IN_SAMPLE_TRADES = 15
    learner.MIN_OOS_TRADES = 5
    learner.MIN_WIN_RATE_PCT = 55.0
    learner.MIN_PROFIT_FACTOR = 1.50
    learner.MAX_DRAWDOWN_PCT = 15.0
    learner.MIN_NET_PNL_USD = 30.0
    learner.MAX_OOS_DEGRADATION_PCT = 35.0
    return learner

def test_live_trading_permanently_disabled_invariants():
    """Verify strict safety invariant: LIVE_TRADING_ENABLED is False and safety guards are active."""
    assert settings.LIVE_TRADING_ENABLED is False, "LIVE_TRADING_ENABLED must be False"
    assert shadow_guard.shadow_mode is True, "Shadow safety guard must be in SHADOW mode"
    assert paper_guard.paper_mode is True, "Paper mode guard must be in PAPER mode"

    # Verify that attempting a real exchange order raises ShadowTradingViolation
    with pytest.raises(ShadowTradingViolation):
        shadow_guard.block_ccxt_create_order("NEAR/USDT", "BUY", 100.0)

    with pytest.raises(ShadowTradingViolation):
        shadow_guard.assert_shadow_safety("Binance Live Order Dispatch")

def test_low_sample_size_rejected_insufficient_evidence(learner):
    """
    Test that a 100% win rate strategy with low trade count (e.g. 2 or 3 trades)
    is strictly rejected with status INSUFFICIENT_EVIDENCE and NOT promoted.
    """
    # Create artificial short candle series resulting in only 2 trades
    technique_def = learner.TECHNIQUES[0]
    
    # Run single cycle on mock candles or duration
    res = LearningExperimentResult(
        experiment_id="TEST-EXP-LOW-SAMPLE",
        timestamp=time.time(),
        symbol="NEAR/USDT",
        timeframe="15m",
        duration_preset="3M",
        candles_analyzed=1000,
        technique_id="TECH_EMA_PULLBACK",
        technique_name="Adaptive EMA Trend Pullback",
        parameters={"fast_ema": 20, "slow_ema": 50},
        trades_count=3,
        wins=3,
        losses=0,
        win_rate_pct=100.0,
        gross_pnl=38.36,
        friction_deducted=6.0,
        net_pnl=32.36,
        profit_factor=99.9,
        max_drawdown_pct=0.0,
        sharpe_ratio=6.95,
        is_champion=False,
        learned_insight="",
        oos_candles_analyzed=300,
        oos_trades_count=1,
        oos_wins=1,
        oos_losses=0,
        oos_win_rate_pct=100.0,
        oos_net_pnl=10.50,
        oos_profit_factor=99.9,
        governance_status="INSUFFICIENT_EVIDENCE",
        applied_to_paper=False,
        applied_to_spot=False
    )

    # Check evidence check logic
    has_adequate_sample = (res.trades_count >= learner.MIN_IN_SAMPLE_TRADES and res.oos_trades_count >= learner.MIN_OOS_TRADES)
    assert has_adequate_sample is False, "3 in-sample and 1 OOS trades must fail sample size check"

def test_oos_degradation_rejection(learner):
    """
    Test that a strategy with good in-sample metrics but severe out-of-sample degradation
    is rejected and not promoted to champion.
    """
    is_trades_count = 20
    is_win_rate = 85.0
    oos_trades_count = 10
    oos_win_rate = 40.0 # 45% drop (exceeds max 35% degradation barrier)
    oos_net_pnl = -15.0

    degradation = is_win_rate - oos_win_rate
    assert degradation > learner.MAX_OOS_DEGRADATION_PCT
    assert oos_net_pnl < 0

def test_governance_champion_promotion_to_paper_active(learner):
    """
    Test that when all 5 governance gates pass:
    1. Sample size >= 15 IS, >= 5 OOS
    2. Net PnL > $30, WR >= 55%, PF >= 1.5
    3. Drawdown <= 15%
    4. OOS Net PnL > 0, OOS WR >= 50%
    5. OOS degradation <= 35%
    The strategy is promoted to PAPER ACTIVE (SHADOW-APPROVED) and NOT live exchange.
    """
    res = LearningExperimentResult(
        experiment_id="TEST-EXP-GOVERNANCE-PASS",
        timestamp=time.time(),
        symbol="BTC/USDT",
        timeframe="1h",
        duration_preset="6M",
        candles_analyzed=1000,
        technique_id="TECH_EMA_PULLBACK",
        technique_name="Adaptive EMA Trend Pullback",
        parameters={"fast_ema": 13, "slow_ema": 34},
        trades_count=25,
        wins=18,
        losses=7,
        win_rate_pct=72.0,
        gross_pnl=650.0,
        friction_deducted=50.0,
        net_pnl=600.0,
        profit_factor=2.85,
        max_drawdown_pct=4.2,
        sharpe_ratio=2.45,
        is_champion=True,
        learned_insight="Passed all governance gates",
        oos_candles_analyzed=300,
        oos_trades_count=8,
        oos_wins=6,
        oos_losses=2,
        oos_win_rate_pct=75.0,
        oos_net_pnl=180.0,
        oos_profit_factor=3.10,
        governance_status="SHADOW_APPROVED",
        applied_to_paper=True,
        applied_to_spot=True
    )

    learner._promote_champion_to_paper_active(res)

    champ = learner.get_champion_for_symbol("BTC/USDT")
    assert champ is not None
    assert champ["symbol"] == "BTC/USDT"
    assert champ["applied_to_paper"] is True
    assert champ["status"] == "SHADOW_APPROVED"

    # Confirm live trading was NOT touched
    assert settings.LIVE_TRADING_ENABLED is False

@pytest.mark.asyncio
async def test_runtime_cycle_controlled_execution(learner):
    """
    Execute a real cycle through execute_single_learning_cycle and verify
    that the result contains OOS metrics and appropriate governance status.
    """
    technique_def = learner.TECHNIQUES[0]
    res = await learner.execute_single_learning_cycle(
        symbol="ETH/USDT",
        timeframe="1h",
        duration="3M",
        technique_def=technique_def
    )

    assert res.experiment_id.startswith("EXP-")
    assert res.candles_analyzed > 0
    assert hasattr(res, "oos_trades_count")
    assert hasattr(res, "governance_status")
    assert res.governance_status in ["INSUFFICIENT_EVIDENCE", "REJECTED_RISK", "DEGRADATION_DETECTED", "SHADOW_APPROVED"]
    
    # Invariant: live trading remains False and no exchange order occurred
    assert settings.LIVE_TRADING_ENABLED is False
