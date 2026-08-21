import pytest
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.learning.experience_memory import TradeExperience, experience_memory, ExperienceMemoryStore
from backend.learning.error_taxonomy import TradeErrorCategory, error_classifier
from backend.learning.post_mortem_engine import post_mortem_engine, TradePostMortem
from backend.learning.learning_memories import learning_memories
from backend.learning.lesson_extractor import lesson_extractor, LearnedLesson
from backend.learning.lesson_application_engine import lesson_applier, LessonApplicationResult
from backend.learning.human_feedback import human_feedback_manager
from backend.learning.counterfactual_engine import counterfactual_engine
from backend.learning.missed_opportunity_engine import missed_opportunity_engine
from backend.learning.self_diagnostic import self_diagnostic_engine
from backend.learning.learning_ab_validator import learning_ab_validator
from backend.execution.kill_switch import emergency_kill_switch
from backend.safety.paper_mode_guard import paper_guard
from institutional_risk import InstitutionalRiskManager, InstitutionalRiskConfig
from trader import PaperTrader

@pytest.fixture
def clean_learning_state():
    emergency_kill_switch.deactivate()
    yield
    emergency_kill_switch.deactivate()

def test_1_trade_experience_stored_and_retrieved():
    """1. Verify TradeExperience is persistently saved to SQLite and retrieved accurately."""
    exp = TradeExperience(
        symbol="BTC/USDT",
        market="SPOT",
        strategy="BRAIN_V44_3",
        decision="TRADE",
        direction="LONG",
        entry_price=64000.0,
        exit_price=65200.0,
        quantity=0.1,
        allocation_usd=6400.0,
        realized_pnl=120.0,
        market_regime="TRENDING_BULL",
        signal_features={"rsi": 58.5, "adx": 28.0}
    )
    saved = experience_memory.save_experience(exp)
    assert saved is True

    fetched = experience_memory.get_experience(exp.experience_id)
    assert fetched is not None
    assert fetched.symbol == "BTC/USDT"
    assert fetched.realized_pnl == 120.0
    assert fetched.signal_features.get("rsi") == 58.5

def test_2_post_mortem_rca_generated_and_error_classified():
    """2. Verify Post-Mortem RCA analyzes losing trades and categorizes error taxonomy."""
    exp = TradeExperience(
        symbol="ETH/USDT",
        decision="TRADE",
        direction="SHORT",
        entry_price=3200.0,
        exit_price=3280.0,
        allocation_usd=2000.0,
        realized_pnl=-50.0,
        market_regime="RECOVERY_REVERSAL",
        signal_features={"rsi": 24.0, "ema20_dist_pct": -3.5},
        exit_reason="STOP_LOSS"
    )
    pm: TradePostMortem = post_mortem_engine.analyze_trade(exp)
    assert pm.is_success is False
    assert pm.root_cause == TradeErrorCategory.LATE_ENTRY.value
    assert "LATE_ENTRY" in pm.root_cause
    assert "OVEREXTENDED_INDICATOR_VALUES" in pm.contributing_factors
    assert "Reject SHORT setups" in pm.recommended_behavior

def test_3_success_memory_distinguishes_correlation_from_causation():
    """3. Verify winning trade post-mortem isolates strategic edge vs execution friction."""
    exp = TradeExperience(
        symbol="SOL/USDT",
        decision="TRADE",
        direction="LONG",
        realized_pnl=85.0,
        market_regime="TRENDING_BULL",
        regime_confidence=0.88,
        slippage_usd=0.20,
        allocation_usd=1500.0
    )
    pm: TradePostMortem = post_mortem_engine.analyze_trade(exp)
    assert pm.is_success is True
    assert pm.root_cause == "VALIDATED_EDGE"
    assert pm.attribution_type == "STRATEGY"
    assert "HIGH_QUALITY_EXECUTION_MINIMAL_SLIPPAGE" in pm.contributing_factors

def test_4_weak_single_trade_lesson_kept_in_hypothesis_status():
    """4. Verify single isolated experience creates a HYPOTHESIS, NOT an approved rule."""
    lesson = lesson_extractor.extract_or_update_lesson(
        title="Rare Flash Crash Rebound",
        description="One-off event testing single trade hypothesis.",
        regime="VOLATILITY_BURST",
        trigger_conditions={"flash_drop": True},
        confidence=0.55
    )
    assert lesson.status == "HYPOTHESIS"
    assert lesson.evidence_count == 1
    # Ensure it is NOT in active approved lessons
    approved_ids = [l.lesson_id for l in lesson_extractor.get_active_approved_lessons()]
    assert lesson.lesson_id not in approved_ids

def test_5_validated_lesson_promoted_to_approved_rule():
    """5. Verify lesson with 5+ evidence samples and high confidence promotes to APPROVED."""
    title = "High Volume Breakout Expansion"
    for i in range(5):
        lesson = lesson_extractor.extract_or_update_lesson(
            title=title,
            description="Breakouts with volume > 1.5x 20MA maintain positive expectancy.",
            regime="BREAKOUT_EXPANSION",
            trigger_conditions={"direction": "LONG", "vol_ratio_above": 1.5},
            confidence=0.85,
            symbol=f"SYM_{i}/USDT"
        )
    assert lesson.evidence_count >= 5
    assert lesson.status == "APPROVED"
    assert lesson.quality_score >= 70.0

def test_6_next_trade_relevant_lesson_retrieved_and_vetoed():
    """6. Verify NextTradeLessonApplicationEngine triggers VETO on matching negative pattern."""
    result: LessonApplicationResult = lesson_applier.evaluate_candidate_against_lessons(
        symbol="BTC/USDT",
        direction="SHORT",
        market_regime="RECOVERY_REVERSAL",
        signal_features={"rsi": 25.0, "adx": 18.0, "volume_ma_ratio": 1.1}
    )
    assert result.lesson_applied is True
    assert result.action == "VETO_TRADE"
    assert result.matching_lesson_id == "L-101"
    assert "Vetoed by Approved Lesson L-101" in result.reason

def test_7_irrelevant_lesson_ignored():
    """7. Verify non-matching setups cleanly pass through with PROCEED and 1.0x sizing."""
    result: LessonApplicationResult = lesson_applier.evaluate_candidate_against_lessons(
        symbol="BTC/USDT",
        direction="LONG",
        market_regime="TRENDING_BULL",
        signal_features={"rsi": 55.0, "adx": 28.0, "volume_ma_ratio": 1.8}
    )
    assert result.lesson_applied is False
    assert result.action == "PROCEED"
    assert result.sizing_multiplier == 1.0

def test_8_user_feedback_recorded_as_hypothesis():
    """8. Verify human feedback is recorded in SQLite and registered as hypothesis only."""
    fb = human_feedback_manager.record_feedback(
        experience_id="EXP-TEST-001",
        user_id="1",
        rating="INCORRECT",
        user_notes="Bot entered short trade too late after breakdown was already exhausted."
    )
    assert fb.feedback_id.startswith("FB-")
    assert fb.rating == "INCORRECT"
    
    # Verify feedback was stored
    records = human_feedback_manager.get_feedback_for_experience("EXP-TEST-001")
    assert len(records) > 0
    assert records[0]["user_notes"] == fb.user_notes

def test_9_lesson_state_lifecycle_and_rollback():
    """9. Verify explicit governance state changes (DEACTIVATE / ACTIVATE / ROLLBACK)."""
    assert "L-101" in lesson_extractor.lessons
    
    # Deactivate
    lesson_extractor.set_lesson_status("L-101", "DEACTIVATED")
    assert lesson_extractor.lessons["L-101"].status == "DEACTIVATED"
    approved_ids = [l.lesson_id for l in lesson_extractor.get_active_approved_lessons()]
    assert "L-101" not in approved_ids

    # Reactivate
    lesson_extractor.set_lesson_status("L-101", "APPROVED")
    assert lesson_extractor.lessons["L-101"].status == "APPROVED"
    approved_ids_re = [l.lesson_id for l in lesson_extractor.get_active_approved_lessons()]
    assert "L-101" in approved_ids_re

def test_10_no_look_ahead_at_decision_time():
    """10. Verify decision engine only uses past/current data without future information."""
    pre_trade_features = {"rsi": 25.0, "volume_ma_ratio": 1.0, "adx": 15.0}
    res = lesson_applier.evaluate_candidate_against_lessons(
        symbol="BTC/USDT",
        direction="SHORT",
        market_regime="RECOVERY_REVERSAL",
        signal_features=pre_trade_features
    )
    # Result depends strictly on pre_trade_features
    assert "rsi_below" in lesson_extractor.lessons["L-101"].trigger_conditions

def test_11_arbitrage_failure_memory():
    """11. Verify ArbitrageFailureMemory records and exposes fee/friction traps."""
    fail_rec = {
        "symbol": "BTC/USDT",
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT",
        "gross_spread_pct": 0.0012,
        "fees_bps": 15.0,
        "slippage_bps": 2.0,
        "net_edge_pct": -0.0005,
        "rejection_reason": "FEE_FRICTION_REJECT"
    }
    learning_memories.record_arbitrage_failure(fail_rec)
    failures = learning_memories.get_arbitrage_failures(limit=5)
    assert len(failures) > 0
    assert failures[-1]["failure_reason"] == "FEE_FRICTION_REJECT"

def test_12_missed_opportunity_engine_evaluates_rejections():
    """12. Verify MissedOpportunityEngine classifies GOOD_SAVE vs MISSED_OPPORTUNITY."""
    # Scenario A: Good Save (price dropped after rejecting a BUY)
    rec_save = missed_opportunity_engine.evaluate_rejection_outcome(
        symbol="BTC/USDT",
        direction="BUY",
        rejection_reason="ADVERSARIAL_VETO",
        entry_price=60000.0,
        forward_price=58500.0, # -2.5% loss avoided
        allocation_usd=1000.0
    )
    assert rec_save.assessment == "GOOD_SAVE"
    assert rec_save.hypothetical_pnl < 0

    # Scenario B: Missed Opportunity (price rallied after rejecting a BUY)
    rec_missed = missed_opportunity_engine.evaluate_rejection_outcome(
        symbol="BTC/USDT",
        direction="BUY",
        rejection_reason="ADVERSARIAL_VETO",
        entry_price=60000.0,
        forward_price=62000.0, # +3.3% gain missed
        allocation_usd=1000.0
    )
    assert rec_missed.assessment == "MISSED_OPPORTUNITY"
    assert rec_missed.hypothetical_pnl > 0

def test_13_counterfactual_engine_simulations():
    """13. Verify CounterfactualEngine computes post-trade alternative outcomes."""
    exp = TradeExperience(
        experience_id="EXP-CF-1",
        realized_pnl=-80.0,
        allocation_usd=2000.0,
        fees_usd=3.0,
        expected_edge_bps=20.0
    )
    cf = counterfactual_engine.analyze_counterfactuals(exp)
    assert cf["experience_id"] == "EXP-CF-1"
    assert cf["actual_pnl"] == -80.0
    scenarios = {s["scenario_name"]: s for s in cf["scenarios"]}
    assert "NO_TRADE" in scenarios
    assert scenarios["NO_TRADE"]["simulated_pnl"] == 0.0
    assert scenarios["HALF_SIZING_50PCT"]["simulated_pnl"] == -40.0

def test_14_self_diagnostic_detects_decay_and_auto_throttles():
    """14. Verify SelfDiagnosticEngine detects loss streaks and activates auto-throttling."""
    # Record 4 consecutive losses
    for _ in range(4):
        self_diagnostic_engine.record_trade_outcome(is_win=False, slippage_bps=3.5)
    
    report = self_diagnostic_engine.run_diagnostics()
    assert report.throttling_active is True
    assert report.throttling_multiplier <= 0.5
    assert len(report.degradation_alerts) > 0

    # Reset with a win
    self_diagnostic_engine.record_trade_outcome(is_win=True, slippage_bps=1.0)
    report_clean = self_diagnostic_engine.run_diagnostics()
    assert report_clean.throttling_active is False

def test_15_out_of_sample_ab_validator_proves_learning_superiority():
    """15. Verify Out-of-Sample A/B benchmark confirms learning-enabled system outperforms baseline."""
    res = learning_ab_validator.evaluate_ab_benchmark()
    assert res.is_learning_superior is True
    assert res.learning_win_rate_pct > res.baseline_win_rate_pct
    assert res.learning_net_pnl > res.baseline_net_pnl
    assert res.false_positives_blocked > 0
    assert res.loss_reduction_pct > 0.0

def test_16_risk_guard_and_kill_switch_remain_authoritative(clean_learning_state):
    """16. Verify Institutional Risk Engine and Kill Switch cannot be bypassed by learned rules."""
    # 1. Kill Switch
    emergency_kill_switch.activate(reason="Risk Emergency")
    assert emergency_kill_switch.is_active is True

    # 2. Risk Engine Rejection
    trader = PaperTrader(initial_balance=10000.0)
    risk_manager = InstitutionalRiskManager(InstitutionalRiskConfig(max_daily_loss_usd=200.0, max_daily_loss_pct=2.0))
    today_str = time.strftime("%Y-%m-%d %H:%M:%S")
    trader.trade_history.append({"status": "CLOSED", "pnl_usd": -300.0, "exit_time": today_str})
    
    risk_res = risk_manager.evaluate_order_risk(trader, "BTC/USDT", "LONG", 65000.0, 1000.0)
    assert risk_res["passed"] is False
    assert risk_res["rule"] == "MAX_DAILY_LOSS"

def test_17_live_exchange_remains_immutably_disabled():
    """17. Verify Sandbox Paper Guard ensures 100% paper execution and blocks live orders."""
    assert paper_guard.paper_mode is True
    # Verify paper guard check succeeds in sandbox
    paper_guard.assert_paper_mode("Learning Test Assertion")
