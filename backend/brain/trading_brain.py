import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

from .regime_intelligence import regime_engine, RegimeState, MarketRegimeType
from .signal_calibration import signal_calibrator, CalibratedSignal
from .signal_ensemble import alpha_ensemble, EnsembleSignal
from .portfolio_brain import portfolio_brain, PortfolioExposureGraph
from .smart_sizing import smart_sizing_engine
from .entry_timing import entry_timing_engine, EntryAssessment, EntryQuality
from .adaptive_exit import adaptive_exit_engine, ExitDecision, TradeThesis
from .adversarial_gate import adversarial_gate, AdversarialReviewResult
from .latency_router import latency_router, LatencyProfile

try:
    from backend.news_intelligence.sentiment_engine import NewsSentimentEngine
    from backend.news_intelligence.event_signal_engine import EventSignalEngine
    news_sentiment_engine = NewsSentimentEngine()
    event_signal_engine = EventSignalEngine()
except Exception:
    news_sentiment_engine = None
    event_signal_engine = None

try:
    from backend.learning.experience_memory import experience_memory
except Exception:
    experience_memory = None

try:
    from backend.shadow_trading.pair_strategy_profile import pair_strategy_store, PairStrategyProfile, get_default_pair_parameters
except Exception:
    pair_strategy_store = None
    get_default_pair_parameters = None

try:
    from backend.strategies.meta_strategy_selector import meta_strategy_selector, MetaSelectorDecision
except Exception:
    meta_strategy_selector = None
    MetaSelectorDecision = None

@dataclass
class PreTradeDecision:
    action: str                        # TRADE, NO_TRADE
    symbol: str
    direction: str                     # LONG, SHORT, NEUTRAL
    regime: str
    calibrated_win_prob: float         # [0.0, 1.0] True calibrated probability
    expected_net_return_bps: float
    approved_allocation_usd: float
    approved_margin_usd: float
    approved_leverage: int
    entry_quality: str
    adversarial_passed: bool
    latency_profile_ms: float
    decision_reason: str
    trade_thesis: Optional[Dict[str, Any]] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class LumoTradingBrain:
    """
    Phase 46.2.2 Superintelligent Master Trading Brain.
    Unifies Market Regime Intelligence, Calibrated Alpha Ensemble, News/Sentiment,
    Pair-Specific Parameters, Authoritative Single-Friction Gate, Anti-Correlation Risk,
    Entry Quality Timing, Smart Kelly Sizing, Adversarial Red-Team, and Adaptive Exits.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LumoTradingBrain, cls).__new__(cls)
        return cls._instance

    def evaluate_opportunity(
        self,
        symbol: str,
        current_price: float,
        technical_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        portfolio_positions: Dict[str, Dict[str, Any]],
        portfolio_equity_usd: float = 10000.0,
        orderbook_data: Optional[Dict[str, Any]] = None,
        pair_profile: Optional[Any] = None
    ) -> PreTradeDecision:
        t0 = time.time()
        orderbook_data = orderbook_data or {}
        spread_bps = float(orderbook_data.get("spread_bps", 2.0))
        slippage_bps = float(technical_data.get("slippage_bps", 2.5))

        # ---------------------------------------------------------------------
        # 0. PAIR-SPECIFIC RUNTIME PARAMETERS & THRESHOLDS
        # ---------------------------------------------------------------------
        if pair_profile is None and pair_strategy_store:
            try:
                pair_profile = pair_strategy_store.get_profile(symbol)
            except Exception:
                pair_profile = None

        if pair_profile and hasattr(pair_profile, "parameters") and pair_profile.parameters:
            pair_params = pair_profile.parameters
        elif get_default_pair_parameters:
            pair_params = get_default_pair_parameters(symbol)
        else:
            pair_params = None

        min_hurdle_bps = pair_params.min_edge_hurdle_bps if pair_params else 4.0

        # ---------------------------------------------------------------------
        # 0.1 NEWS & SENTIMENT INTELLIGENCE EVALUATION
        # ---------------------------------------------------------------------
        news_label = sentiment_data.get("news_label", "NEUTRAL")
        news_score = float(sentiment_data.get("sentiment_score", 0.0))
        news_event_type = sentiment_data.get("event_type", "MARKET_UPDATE")
        
        event_action = "NORMAL"
        if event_signal_engine and news_event_type != "MARKET_UPDATE":
            try:
                sig = event_signal_engine.generate_signal(news_event_type, symbol)
                event_action = sig.action
            except Exception:
                pass

        # ---------------------------------------------------------------------
        # 1. MARKET REGIME INTELLIGENCE
        # ---------------------------------------------------------------------
        regime_state: RegimeState = regime_engine.detect_regime(
            current_price=current_price,
            technical_data=technical_data,
            sentiment_summary=sentiment_data,
            orderbook_data=orderbook_data
        )

        # ---------------------------------------------------------------------
        # 2. MULTI-MODEL ALPHA ENSEMBLE
        # ---------------------------------------------------------------------
        ensemble_signal: EnsembleSignal = alpha_ensemble.evaluate_ensemble(
            symbol=symbol,
            current_price=current_price,
            technical_data=technical_data,
            sentiment_data=sentiment_data,
            regime_state=regime_state,
            orderbook_data=orderbook_data
        )

        # ---------------------------------------------------------------------
        # 3. SIGNAL PROBABILITY CALIBRATION & SINGLE-SOURCE FRICTION
        # ---------------------------------------------------------------------
        atr = float(technical_data.get("atr", current_price * 0.02))
        atr_pct = (atr / max(1e-9, current_price)) * 100.0
        calibrated: CalibratedSignal = signal_calibrator.calibrate(
            symbol=symbol,
            raw_score=ensemble_signal.composite_score,
            atr_pct=atr_pct,
            regime_stability=regime_state.stability,
            spread_bps=spread_bps,
            slippage_bps=slippage_bps,
            taker_fee_bps=15.0,
            min_net_edge_bps=min_hurdle_bps
        )

        # ---------------------------------------------------------------------
        # 3.1 NEWS CONFLICT RISK GATE
        # ---------------------------------------------------------------------
        if calibrated.direction == "LONG" and (news_score < -0.40 or event_action in ["BLOCK_NEW_LONGS", "CLOSE_POSITION", "REDUCE_RISK"]):
            latency = latency_router.profile_and_route(symbol, "NORMAL", t0)
            return PreTradeDecision(
                action="NO_TRADE",
                symbol=symbol,
                direction=calibrated.direction,
                regime=regime_state.regime.value,
                calibrated_win_prob=calibrated.prob_profit,
                expected_net_return_bps=calibrated.expected_net_return_bps,
                approved_allocation_usd=0.0,
                approved_margin_usd=0.0,
                approved_leverage=1,
                entry_quality="NEWS_REJECTED",
                adversarial_passed=False,
                latency_profile_ms=latency.total_roundtrip_ms,
                decision_reason=f"REJECTED BY NEWS GATE: Technical signal is LONG but fresh news sentiment is negative ({news_score:.2f}, event={news_event_type}). Risk policy mandates WAIT.",
                diagnostics={
                    "regime": regime_state.to_dict(),
                    "ensemble": ensemble_signal.to_dict(),
                    "news_sentiment": sentiment_data
                }
            )

        # ---------------------------------------------------------------------
        # 3.2 EXPECTED NET EDGE FRICTION GATE (Single Authoritative Friction)
        # ---------------------------------------------------------------------
        net_edge_bps = calibrated.expected_net_return_bps
        total_friction_bps = calibrated.expected_friction_bps
        gross_edge_bps = calibrated.expected_gross_return_bps

        if net_edge_bps < min_hurdle_bps:
            latency = latency_router.profile_and_route(symbol, "NORMAL", t0)
            return PreTradeDecision(
                action="NO_TRADE",
                symbol=symbol,
                direction=calibrated.direction,
                regime=regime_state.regime.value,
                calibrated_win_prob=calibrated.prob_profit,
                expected_net_return_bps=round(net_edge_bps, 2),
                approved_allocation_usd=0.0,
                approved_margin_usd=0.0,
                approved_leverage=1,
                entry_quality="LOW_EDGE",
                adversarial_passed=False,
                latency_profile_ms=latency.total_roundtrip_ms,
                decision_reason=f"REJECTED BY FRICTION GATE: Expected net edge (+{net_edge_bps:.1f}bps) < pair hurdle (+{min_hurdle_bps:.1f}bps) after total single friction (-{total_friction_bps:.1f}bps).",
                diagnostics={
                    "gross_edge_bps": gross_edge_bps,
                    "net_edge_bps": round(net_edge_bps, 2),
                    "total_friction_bps": total_friction_bps,
                    "min_hurdle_bps": min_hurdle_bps,
                    "pair_parameters": pair_params.to_dict() if pair_params else {}
                }
            )

        # ---------------------------------------------------------------------
        # 3.3 PAIR LEARNING MEMORY EXPERIENCE LOOKUP
        # ---------------------------------------------------------------------
        learning_summary = {"similar_trades_count": 0, "win_rate_pct": 50.0, "expectancy_usd": 0.0}
        if experience_memory:
            try:
                exp_list = experience_memory.query_experiences(symbol=symbol, limit=50)
                if exp_list:
                    wins = sum(1 for e in exp_list if e.realized_pnl > 0)
                    total_pnl = sum(e.realized_pnl for e in exp_list)
                    wr = (wins / len(exp_list)) * 100.0
                    learning_summary = {
                        "similar_trades_count": len(exp_list),
                        "win_rate_pct": round(wr, 1),
                        "expectancy_usd": round(total_pnl / len(exp_list), 2)
                    }
                    if len(exp_list) >= 5 and wr < 30.0:
                        latency = latency_router.profile_and_route(symbol, "NORMAL", t0)
                        return PreTradeDecision(
                            action="NO_TRADE",
                            symbol=symbol,
                            direction=calibrated.direction,
                            regime=regime_state.regime.value,
                            calibrated_win_prob=calibrated.prob_profit,
                            expected_net_return_bps=round(net_edge_bps, 2),
                            approved_allocation_usd=0.0,
                            approved_margin_usd=0.0,
                            approved_leverage=1,
                            entry_quality="LEARNING_VETO",
                            adversarial_passed=False,
                            latency_profile_ms=latency.total_roundtrip_ms,
                            decision_reason=f"REJECTED BY LEARNING MEMORY: Historical setups in {symbol} show low win rate ({wr:.1f}%, {len(exp_list)} trades). Expectancy is negative.",
                            diagnostics={"learning_summary": learning_summary}
                        )
            except Exception as l_err:
                logger.warning(f"[LEARNING_LOOKUP_WARN] {l_err}")

        # Early Exit Gate: If signal is not tradeable -> NO_TRADE
        if not calibrated.is_tradeable:
            latency = latency_router.profile_and_route(symbol, "NORMAL", t0)
            return PreTradeDecision(
                action="NO_TRADE",
                symbol=symbol,
                direction=calibrated.direction,
                regime=regime_state.regime.value,
                calibrated_win_prob=calibrated.prob_profit,
                expected_net_return_bps=calibrated.expected_return_bps,
                approved_allocation_usd=0.0,
                approved_margin_usd=0.0,
                approved_leverage=1,
                entry_quality="N/A",
                adversarial_passed=False,
                latency_profile_ms=latency.total_roundtrip_ms,
                decision_reason=calibrated.decision_reason,
                diagnostics={
                    "regime": regime_state.to_dict(),
                    "ensemble": ensemble_signal.to_dict(),
                    "calibration": calibrated.to_dict()
                }
            )

        # ---------------------------------------------------------------------
        # 4. ENTRY TIMING INTELLIGENCE (LATE ENTRY FILTER)
        # ---------------------------------------------------------------------
        entry_assessment: EntryAssessment = entry_timing_engine.evaluate_entry_timing(
            symbol=symbol,
            direction=calibrated.direction,
            current_price=current_price,
            technical_data=technical_data
        )

        if not entry_assessment.is_approved:
            latency = latency_router.profile_and_route(symbol, "NORMAL", t0)
            return PreTradeDecision(
                action="NO_TRADE",
                symbol=symbol,
                direction=calibrated.direction,
                regime=regime_state.regime.value,
                calibrated_win_prob=calibrated.prob_profit,
                expected_net_return_bps=calibrated.expected_return_bps,
                approved_allocation_usd=0.0,
                approved_margin_usd=0.0,
                approved_leverage=1,
                entry_quality=entry_assessment.quality.value,
                adversarial_passed=False,
                latency_profile_ms=latency.total_roundtrip_ms,
                decision_reason=entry_assessment.reason,
                diagnostics={
                    "regime": regime_state.to_dict(),
                    "entry_timing": entry_assessment.to_dict()
                }
            )

        # ---------------------------------------------------------------------
        # 5. SMART VOLATILITY & KELLY POSITION SIZING
        # ---------------------------------------------------------------------
        sizing_res = smart_sizing_engine.calculate_position_size(
            portfolio_equity_usd=portfolio_equity_usd,
            calibrated_signal=calibrated,
            current_drawdown_pct=0.0
        )
        proposed_notional = sizing_res["allocation_usd"]

        # ---------------------------------------------------------------------
        # 6. ANTI-CORRELATION PORTFOLIO BRAIN
        # ---------------------------------------------------------------------
        portfolio_fit = portfolio_brain.evaluate_order_portfolio_fit(
            symbol=symbol,
            side=calibrated.direction,
            proposed_notional_usd=proposed_notional,
            current_positions=portfolio_positions
        )

        if not portfolio_fit["passed"]:
            latency = latency_router.profile_and_route(symbol, "NORMAL", t0)
            return PreTradeDecision(
                action="NO_TRADE",
                symbol=symbol,
                direction=calibrated.direction,
                regime=regime_state.regime.value,
                calibrated_win_prob=calibrated.prob_profit,
                expected_net_return_bps=calibrated.expected_return_bps,
                approved_allocation_usd=0.0,
                approved_margin_usd=0.0,
                approved_leverage=1,
                entry_quality=entry_assessment.quality.value,
                adversarial_passed=False,
                latency_profile_ms=latency.total_roundtrip_ms,
                decision_reason=portfolio_fit["reason"],
                diagnostics={
                    "portfolio_fit": portfolio_fit
                }
            )

        final_notional = portfolio_fit.get("adjusted_notional_usd", proposed_notional)
        final_leverage = sizing_res["leverage"]
        final_margin = round(final_notional / final_leverage, 2)

        # ---------------------------------------------------------------------
        # 6.5 LEARNED LESSONS PRE-TRADE EVALUATION GATE (Phase 44.4)
        # ---------------------------------------------------------------------
        try:
            from backend.learning.lesson_application_engine import lesson_applier
            lesson_res = lesson_applier.evaluate_candidate_against_lessons(
                symbol=symbol,
                direction=calibrated.direction,
                market_regime=regime_state.regime.value,
                signal_features=technical_data
            )
            if lesson_res.action == "VETO_TRADE":
                latency = latency_router.profile_and_route(symbol, "NORMAL", t0)
                return PreTradeDecision(
                    action="NO_TRADE",
                    symbol=symbol,
                    direction=calibrated.direction,
                    regime=regime_state.regime.value,
                    calibrated_win_prob=calibrated.prob_profit,
                    expected_net_return_bps=calibrated.expected_return_bps,
                    approved_allocation_usd=0.0,
                    approved_margin_usd=0.0,
                    approved_leverage=1,
                    entry_quality=entry_assessment.quality.value,
                    adversarial_passed=False,
                    latency_profile_ms=latency.total_roundtrip_ms,
                    decision_reason=lesson_res.reason,
                    diagnostics={
                        "learned_lesson_veto": lesson_res.to_dict()
                    }
                )
            elif lesson_res.action == "REDUCE_SIZE_50":
                final_notional = round(final_notional * 0.5, 2)
                final_margin = round(final_margin * 0.5, 2)
        except Exception as l_ex:
            logger.error(f"[LESSON_EVAL_ERROR] Error in lesson application gate: {l_ex}")

        # ---------------------------------------------------------------------
        # 7. ADVERSARIAL RED-TEAM VERIFICATION GATE
        # ---------------------------------------------------------------------
        portfolio_graph = portfolio_brain.analyze_portfolio(portfolio_positions)
        red_team_res: AdversarialReviewResult = adversarial_gate.challenge_trade(
            symbol=symbol,
            direction=calibrated.direction,
            calibrated_signal=calibrated,
            portfolio_graph=portfolio_graph,
            technical_data=technical_data,
            spread_bps=spread_bps
        )

        if not red_team_res.passed:
            latency = latency_router.profile_and_route(symbol, "NORMAL", t0)
            return PreTradeDecision(
                action="NO_TRADE",
                symbol=symbol,
                direction=calibrated.direction,
                regime=regime_state.regime.value,
                calibrated_win_prob=calibrated.prob_profit,
                expected_net_return_bps=calibrated.expected_return_bps,
                approved_allocation_usd=0.0,
                approved_margin_usd=0.0,
                approved_leverage=1,
                entry_quality=entry_assessment.quality.value,
                adversarial_passed=False,
                latency_profile_ms=latency.total_roundtrip_ms,
                decision_reason=red_team_res.counter_thesis,
                diagnostics={
                    "red_team": red_team_res.to_dict()
                }
            )

        # ---------------------------------------------------------------------
        # 8. BUILD TRADE THESIS & LATENCY PROFILE
        # ---------------------------------------------------------------------
        latency = latency_router.profile_and_route(symbol, "NORMAL", t0)

        if calibrated.direction == "LONG":
            target_p = round(current_price * (1.0 + (calibrated.expected_volatility_pct * 0.015)), 2)
            sl_p = round(current_price * (1.0 - (calibrated.expected_volatility_pct * 0.009)), 2)
            invalidation = "Price drops below 20 EMA with negative momentum."
        else:
            target_p = round(current_price * (1.0 - (calibrated.expected_volatility_pct * 0.015)), 2)
            sl_p = round(current_price * (1.0 + (calibrated.expected_volatility_pct * 0.009)), 2)
            invalidation = "Price rises above 20 EMA with positive momentum."

        thesis = TradeThesis(
            trade_id=f"THESIS-{symbol.replace('/', '')}-{int(time.time())}",
            symbol=symbol,
            direction=calibrated.direction,
            entry_price=current_price,
            entry_time=time.time(),
            max_holding_seconds=calibrated.expected_holding_seconds,
            invalidation_condition=invalidation,
            expected_target_price=target_p,
            stop_loss_price=sl_p,
            thesis_summary=f"{calibrated.direction} in [{regime_state.regime.value}] supported by {ensemble_signal.dominant_factor}. P(win)={calibrated.prob_profit*100:.1f}%, Expected Return=+{calibrated.expected_return_bps:.1f}bps."
        )

        return PreTradeDecision(
            action="TRADE",
            symbol=symbol,
            direction=calibrated.direction,
            regime=regime_state.regime.value,
            calibrated_win_prob=calibrated.prob_profit,
            expected_net_return_bps=calibrated.expected_return_bps,
            approved_allocation_usd=final_notional,
            approved_margin_usd=final_margin,
            approved_leverage=final_leverage,
            entry_quality=entry_assessment.quality.value,
            adversarial_passed=True,
            latency_profile_ms=latency.total_roundtrip_ms,
            decision_reason=f"Approved: Calibrated edge +{calibrated.expected_return_bps:.1f}bps, Entry Quality={entry_assessment.quality.value}, Red-Team Score={red_team_res.challenge_score:.0f}/100.",
            trade_thesis=thesis.to_dict(),
            diagnostics={
                "regime": regime_state.to_dict(),
                "ensemble": ensemble_signal.to_dict(),
                "calibration": calibrated.to_dict(),
                "entry_timing": entry_assessment.to_dict(),
                "portfolio_fit": portfolio_fit,
                "red_team": red_team_res.to_dict(),
                "latency": latency.to_dict()
            }
        )

# Global Singleton Master Brain
lumo_trading_brain = LumoTradingBrain()
