import pytest
import time
from backend.brain.regime_intelligence import regime_engine, MarketRegimeType, RegimeState
from backend.brain.signal_calibration import signal_calibrator, CalibratedSignal
from backend.brain.signal_ensemble import alpha_ensemble, EnsembleSignal
from backend.brain.portfolio_brain import portfolio_brain, PortfolioExposureGraph
from backend.brain.smart_sizing import smart_sizing_engine
from backend.brain.entry_timing import entry_timing_engine, EntryQuality, EntryAssessment
from backend.brain.adaptive_exit import adaptive_exit_engine, ExitDecision
from backend.brain.adversarial_gate import adversarial_gate, AdversarialReviewResult
from backend.brain.latency_router import latency_router
from backend.brain.trading_brain import lumo_trading_brain, PreTradeDecision
from backend.brain.shadow_ab_engine import shadow_ab_engine
from backend.execution.order_models import OMSOrder

def test_10_market_regimes_detection():
    """Verify that RegimeIntelligenceEngine detects all distinct market regimes accurately."""
    # 1. Bull Trend
    bull_ta = {"atr": 1000.0, "adx": 30.0, "plus_di": 32.0, "minus_di": 12.0, "ema_20": 59000.0, "ema_50": 58000.0, "ema_200": 55000.0, "rsi": 62.0}
    bull_res = regime_engine.detect_regime(60000.0, bull_ta, {"fear_greed": {"value": 65}})
    assert bull_res.regime == MarketRegimeType.BULL_TREND
    assert bull_res.confidence >= 0.70
    assert "TrendFollowing" in bull_res.recommended_alphas

    # 2. Bear Trend
    bear_ta = {"atr": 1000.0, "adx": 30.0, "plus_di": 12.0, "minus_di": 32.0, "ema_20": 61000.0, "ema_50": 62000.0, "ema_200": 65000.0, "rsi": 38.0}
    bear_res = regime_engine.detect_regime(60000.0, bear_ta, {"fear_greed": {"value": 35}})
    assert bear_res.regime == MarketRegimeType.BEAR_TREND
    assert bear_res.confidence >= 0.70

    # 3. Panic Liquidation
    panic_ta = {"atr": 3000.0, "adx": 35.0, "plus_di": 10.0, "minus_di": 40.0, "volume_spike_ratio": 3.2, "rsi": 18.0, "ema_20": 65000.0, "ema_200": 70000.0}
    panic_res = regime_engine.detect_regime(60000.0, panic_ta, {"fear_greed": {"value": 15}})
    assert panic_res.regime == MarketRegimeType.PANIC_LIQUIDATION

    # 4. Low Volatility Compression (Squeeze)
    squeeze_ta = {"atr": 300.0, "adx": 14.0, "bb_width_pct": 1.5, "volume_spike_ratio": 0.45, "rsi": 50.0, "ema_20": 60000.0}
    squeeze_res = regime_engine.detect_regime(60000.0, squeeze_ta, {"fear_greed": {"value": 50}})
    assert squeeze_res.regime == MarketRegimeType.LOW_VOL_COMPRESSION

    # 5. Liquidity Shock
    liq_shock_ob = {"spread_bps": 22.0, "depth_liquidity_usd": 5000.0}
    shock_res = regime_engine.detect_regime(60000.0, {"atr": 1000.0}, {}, liq_shock_ob)
    assert shock_res.regime == MarketRegimeType.LIQUIDITY_SHOCK

def test_calibrated_win_probability():
    """Verify that SignalProbabilityCalibrator generates realistic P(win) and expected return."""
    # Strong Long Signal
    cal_long = signal_calibrator.calibrate("BTC/USDT", raw_score=85.0, atr_pct=2.0)
    assert cal_long.direction == "LONG"
    assert 0.52 <= cal_long.prob_profit <= 0.65  # Realistic out-of-sample win rate range
    assert cal_long.expected_return_bps > 0
    assert cal_long.is_tradeable is True

    # Neutral Weak Signal
    cal_neutral = signal_calibrator.calibrate("BTC/USDT", raw_score=52.0, atr_pct=2.0)
    assert cal_neutral.direction == "NEUTRAL"
    assert cal_neutral.is_tradeable is False
    assert "Neutral" in cal_neutral.decision_reason

def test_late_entry_rejection():
    """Verify that EntryTimingEngine strictly rejects overextended late-cycle entries."""
    # Price is 2.5x ATR above EMA20 -> Overextended late entry
    ta_late = {
        "atr": 1000.0,
        "ema_20": 57000.0,  # Current price 60000 is $3000 away (3.0x ATR)
        "rsi": 68.0,
        "volume_spike_ratio": 1.0
    }
    assessment = entry_timing_engine.evaluate_entry_timing("BTC/USDT", "LONG", 60000.0, ta_late)
    assert assessment.quality == EntryQuality.LATE
    assert assessment.is_approved is False
    assert "Late-Cycle Entry" in assessment.reason

def test_reversal_trap_rejection():
    """Verify that EntryTimingEngine rejects extreme reversal traps."""
    # Short signal at extreme oversold RSI 22 with volume climax
    ta_trap = {
        "atr": 1000.0,
        "ema_20": 60500.0,
        "rsi": 22.0,
        "volume_spike_ratio": 3.0
    }
    assessment = entry_timing_engine.evaluate_entry_timing("BTC/USDT", "SHORT", 60000.0, ta_trap)
    assert assessment.quality == EntryQuality.REJECT
    assert assessment.is_approved is False
    assert "Reversal Trap Risk" in assessment.reason

def test_anti_correlation_portfolio_brain_skew_cap():
    """Verify that AntiCorrelationPortfolioBrain blocks stacking same-direction shorts beyond 60%."""
    # Existing portfolio holding 4 large SHORT positions
    current_pos = {
        "BTC/USDT": {"symbol": "BTC/USDT", "side": "SHORT", "amount": 1.0, "entry_price": 60000.0, "margin_usd": 20000.0, "leverage": 3},
        "ETH/USDT": {"symbol": "ETH/USDT", "side": "SHORT", "amount": 10.0, "entry_price": 2000.0, "margin_usd": 6666.0, "leverage": 3},
        "SOL/USDT": {"symbol": "SOL/USDT", "side": "SHORT", "amount": 100.0, "entry_price": 140.0, "margin_usd": 4666.0, "leverage": 3},
        "BNB/USDT": {"symbol": "BNB/USDT", "side": "SHORT", "amount": 20.0, "entry_price": 600.0, "margin_usd": 4000.0, "leverage": 3}
    }
    # Attempt to open another SHORT on AVAX
    fit = portfolio_brain.evaluate_order_portfolio_fit("AVAX/USDT", "SHORT", proposed_notional_usd=10000.0, current_positions=current_pos)
    assert fit["passed"] is False
    assert "ANTI_CORRELATION_BLOCKED" in fit["reason"]

    # Attempt to open a LONG on AVAX (hedging) -> Should be permitted
    fit_long = portfolio_brain.evaluate_order_portfolio_fit("AVAX/USDT", "LONG", proposed_notional_usd=10000.0, current_positions=current_pos)
    assert fit_long["passed"] is True

def test_smart_volatility_and_kelly_sizing():
    """Verify that SmartPositionSizingEngine sizes positions with fractional Kelly & volatility dampener."""
    cal_signal = CalibratedSignal(
        symbol="BTC/USDT",
        direction="LONG",
        signal_strength=0.8,
        prob_profit=0.58,
        expected_return_bps=45.0,
        expected_volatility_pct=2.5,
        expected_holding_seconds=3600,
        prob_stop_loss=0.35,
        prob_take_profit=0.50,
        calibration_reliability=0.85,
        is_tradeable=True,
        decision_reason="Tradeable Edge"
    )
    sizing = smart_sizing_engine.calculate_position_size(
        portfolio_equity_usd=10000.0,
        calibrated_signal=cal_signal,
        current_drawdown_pct=0.0
    )
    assert 200.0 <= sizing["allocation_usd"] <= 800.0  # Safe 2% - 8% equity allocation
    assert sizing["margin_usd"] > 0
    assert sizing["leverage"] in [1, 2]

def test_adaptive_exit_thesis_invalidation_and_time_decay():
    """Verify that AdaptiveExitEngine triggers thesis invalidation and max holding time decay."""
    # 1. Thesis Invalidation: Short trade where price reclaimed EMA20 with positive MACD
    pos_short = {
        "symbol": "BTC/USDT",
        "side": "SHORT",
        "entry_price": 59000.0,
        "entry_time_ts": time.time() - 600,  # 10 mins ago
        "max_holding_seconds": 3600
    }
    ta_bullish = {"ema_20": 59500.0, "macd_hist": 4.5, "rsi": 62.0}
    exit_inv = adaptive_exit_engine.evaluate_position_exit(pos_short, 61000.0, ta_bullish, MarketRegimeType.BULL_TREND)
    assert exit_inv.should_exit is True
    assert "Thesis Invalidation" in exit_inv.exit_reason

    # 2. Time Decay Exit: Trade open for 100 mins (exceeding 90 min max)
    pos_old = {
        "symbol": "BTC/USDT",
        "side": "LONG",
        "entry_price": 60000.0,
        "entry_time_ts": time.time() - 6000,  # 100 mins ago
        "max_holding_seconds": 5400  # 90 mins max
    }
    exit_time = adaptive_exit_engine.evaluate_position_exit(pos_old, 60100.0, {"ema_20": 60000.0}, MarketRegimeType.SIDEWAYS_RANGE)
    assert exit_time.should_exit is True
    assert "Time Decay Limit" in exit_time.exit_reason

def test_adversarial_red_team_gate():
    """Verify that AdversarialRedTeamGate challenges and vetoes low-expectancy trades."""
    # Trade with weak edge where transaction friction eats the entire profit
    weak_signal = CalibratedSignal(
        symbol="BTC/USDT",
        direction="LONG",
        signal_strength=0.3,
        prob_profit=0.51,
        expected_return_bps=12.0,  # Less than round-trip taker fees (15 bps)
        expected_volatility_pct=2.0,
        expected_holding_seconds=3600,
        prob_stop_loss=0.45,
        prob_take_profit=0.45,
        calibration_reliability=0.70,
        is_tradeable=True,
        decision_reason="Marginal"
    )
    graph = PortfolioExposureGraph(0, 0, 0, 50.0, 0.0, 0.0, {}, True, [])
    review = adversarial_gate.challenge_trade("BTC/USDT", "LONG", weak_signal, graph, {"rsi": 50.0}, spread_bps=2.5)
    assert review.passed is False
    assert review.challenge_score >= 65.0
    assert "Fee Drag" in review.veto_reasons[0]

def test_order_models_zero_residual_booster():
    """Verify that OMSOrder.to_dict() has ZERO residual 0.0035 artificial profit booster."""
    order = OMSOrder(
        symbol="BTC/USDT",
        side="BUY",
        quantity=1.0,
        filled_quantity=1.0,
        average_fill_price=60000.0,
        metadata={"mark_price": 60000.0}
    )
    d = order.to_dict()
    # At exact fill price with 0.075% taker fee ($45.00), PnL should be -$45.00, NOT +$210.00 booster!
    assert d["pnl_usd"] == -45.0
    assert d["fee_usd"] == 45.0
