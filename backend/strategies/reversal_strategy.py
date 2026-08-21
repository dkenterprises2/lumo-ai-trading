import math
from typing import Dict, Any, Optional
from loguru import logger

from backend.strategies.base_strategy import BaseStrategy, StrategyFamily, StrategyCandidateResult, SuitabilityScoreBreakdown
from backend.execution.execution_cost_estimator import execution_cost_estimator
from backend.brain.entry_timing import entry_timing_engine
from backend.brain.regime_intelligence import MarketRegimeType

class ReversalStrategy(BaseStrategy):
    """
    Phase 47 REVERSAL Strategy Family.
    Specialized for Trend Exhaustion, Panic Liquidation, and Recovery Reversal regimes:
    - Momentum Divergence (RSI & MACD divergence vs price swings)
    - Volatility & Volume Climax (Exhaustion volume spike >= 1.30x with price rejection)
    - Failed Breakout & Liquidity Sweep fade
    - Single-source authoritative friction deduction
    """

    def __init__(self):
        super().__init__(StrategyFamily.REVERSAL)
        self.version = "1.0.0"

    def evaluate_candidate(
        self,
        symbol: str,
        current_price: float,
        technical_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        regime_state: Any,
        orderbook_data: Optional[Dict[str, Any]] = None,
        pair_parameters: Optional[Any] = None
    ) -> StrategyCandidateResult:
        orderbook_data = orderbook_data or {}
        spread_bps = float(orderbook_data.get("spread_bps", 2.0))
        slippage_bps = float(technical_data.get("slippage_bps", 2.5))
        min_hurdle_bps = pair_parameters.min_edge_hurdle_bps if pair_parameters else 4.0
        strategy_id = f"{symbol.replace('/', '')}-REVERSAL-V1"

        # 1. Technical Factors Extraction
        ema_20 = float(technical_data.get("ema_20", current_price))
        rsi = float(technical_data.get("rsi", 50.0))
        macd = float(technical_data.get("macd", 0.0))
        macd_signal = float(technical_data.get("macd_signal", 0.0))
        macd_hist = macd - macd_signal
        atr = float(technical_data.get("atr", current_price * 0.02))
        atr_pct = (atr / max(1e-9, current_price)) * 100.0
        vol_spike = float(technical_data.get("volume_spike_ratio", 1.0))

        # Check for divergence clues or extreme extension
        is_bull_divergence = bool(technical_data.get("bullish_divergence", False)) or (rsi < 28.0 and macd_hist > -0.05 and vol_spike >= 1.25)
        is_bear_divergence = bool(technical_data.get("bearish_divergence", False)) or (rsi > 72.0 and macd_hist < 0.05 and vol_spike >= 1.25)

        regime_enum = regime_state.regime if hasattr(regime_state, "regime") else MarketRegimeType.SIDEWAYS_RANGE
        stability = getattr(regime_state, "stability", 0.8)

        if is_bull_divergence:
            direction = "LONG"
            raw_strength = 0.60 + (0.15 if rsi < 25.0 else 0.0) + min(0.20, (vol_spike - 1.0) * 0.20)
            signal_strength = round(min(1.0, raw_strength), 3)
            rev_reason = f"Bullish Reversal / Divergence trigger (RSI={rsi:.1f}, Climax Vol={vol_spike:.2f}x)."
        elif is_bear_divergence:
            direction = "SHORT"
            raw_strength = 0.60 + (0.15 if rsi > 75.0 else 0.0) + min(0.20, (vol_spike - 1.0) * 0.20)
            signal_strength = round(-min(1.0, raw_strength), 3)
            rev_reason = f"Bearish Reversal / Divergence trigger (RSI={rsi:.1f}, Climax Vol={vol_spike:.2f}x)."
        else:
            direction = "NEUTRAL"
            signal_strength = 0.0
            rev_reason = f"No momentum exhaustion or divergence detected (RSI={rsi:.1f}, Vol={vol_spike:.2f}x)."

        # 2. Probability of Reversal
        if direction != "NEUTRAL":
            base_prob = 0.53 + (min(0.18, abs(signal_strength) * 0.15) * stability)
            # In persistent trends without climax volume, reversal probability drops
            if regime_enum in [MarketRegimeType.BULL_TREND, MarketRegimeType.BEAR_TREND] and vol_spike < 1.30:
                base_prob -= 0.12
            prob_win = round(min(0.72, max(0.38, base_prob)), 3)
        else:
            prob_win = 0.500
        prob_loss = round(1.0 - prob_win, 3)

        # 3. Expected Gross Return
        expected_target_bps = atr_pct * 100.0 * 2.0
        expected_stop_bps = atr_pct * 100.0 * 1.0
        gross_edge_bps = round((prob_win * expected_target_bps) - (prob_loss * expected_stop_bps), 2) if direction != "NEUTRAL" else 0.0

        # 4. Authoritative Single Friction Deduction
        friction_est = execution_cost_estimator.estimate_pre_trade_friction(
            symbol=symbol,
            spread_bps=spread_bps,
            slippage_bps=slippage_bps,
            taker_fee_bps=15.0,
            latency_bps=1.5
        )
        total_friction_bps = friction_est.total_friction_bps
        expected_net_edge_bps = round(gross_edge_bps - total_friction_bps, 2)

        # 5. Regime Fit Scoring (0-25)
        if regime_enum in [MarketRegimeType.RECOVERY_REVERSAL, MarketRegimeType.PANIC_LIQUIDATION]:
            regime_fit = 25.0
        elif regime_enum == MarketRegimeType.HIGH_VOL_BREAKOUT:
            regime_fit = 15.0  # Fade potential climax top/bottom
        elif regime_enum == MarketRegimeType.SIDEWAYS_RANGE:
            regime_fit = 10.0
        else:
            regime_fit = 0.0  # Fighting strong ongoing trends without climax is high risk

        # 6. Entry Timing Assessment
        entry_assess = entry_timing_engine.evaluate_entry_timing(
            symbol=symbol,
            direction=direction if direction != "NEUTRAL" else "LONG",
            current_price=current_price,
            technical_data=technical_data
        )
        entry_quality_str = entry_assess.quality.value if direction != "NEUTRAL" else "N/A"

        # 7. Suitability Score Calculation (0-100)
        net_edge_pts = min(25.0, max(0.0, (expected_net_edge_bps / max(1.0, min_hurdle_bps * 2.0)) * 25.0))
        calib_pts = min(20.0, max(0.0, ((prob_win - 0.50) / 0.20) * 20.0))
        fee_res_pts = min(15.0, max(0.0, (gross_edge_bps / max(1.0, total_friction_bps)) * 7.5))
        sample_pts = 15.0

        suitability = SuitabilityScoreBreakdown(
            regime_fit=regime_fit,
            net_edge_score=round(net_edge_pts, 1),
            calibration_score=round(calib_pts, 1),
            fee_slippage_resistance=round(fee_res_pts, 1),
            sample_degradation_score=sample_pts
        )
        total_suitability = suitability.calculate_total()

        is_tradeable = (
            direction != "NEUTRAL" and
            expected_net_edge_bps >= min_hurdle_bps and
            prob_win >= 0.510 and
            regime_fit >= 15.0 and
            entry_assess.is_approved
        )

        if is_tradeable:
            reason = f"Reversal {direction} confirmed (Gross: +{gross_edge_bps:.1f}bps, Net: +{expected_net_edge_bps:.1f}bps, P(win)={prob_win*100:.1f}%)."
        elif direction == "NEUTRAL":
            reason = f"Reversal Neutral: {rev_reason}"
        elif regime_fit < 15.0:
            reason = f"Reversal rejected: Active regime [{regime_enum.value}] is unfavorable (high adverse trend continuation risk)."
        elif not entry_assess.is_approved:
            reason = f"Reversal rejected by timing: {entry_assess.reason}"
        else:
            reason = f"Reversal net edge (+{expected_net_edge_bps:.1f}bps) < pair hurdle (+{min_hurdle_bps:.1f}bps) after friction (-{total_friction_bps:.1f}bps)."

        return StrategyCandidateResult(
            strategy_id=strategy_id,
            family=self.family,
            pair=symbol,
            version=self.version,
            direction=direction,
            signal_strength=signal_strength,
            calibrated_probability=prob_win,
            expected_gross_edge_bps=gross_edge_bps,
            estimated_friction_bps=total_friction_bps,
            expected_net_edge_bps=expected_net_edge_bps,
            entry_quality=entry_quality_str,
            risk_state="NORMAL" if is_tradeable else "FILTERED",
            regime_fit_score=regime_fit,
            suitability_score=total_suitability,
            suitability_breakdown=suitability,
            decision_reason=reason,
            is_tradeable=is_tradeable,
            diagnostics={
                "rsi": rsi,
                "is_bull_divergence": is_bull_divergence,
                "is_bear_divergence": is_bear_divergence,
                "rev_reason": rev_reason,
                "friction_breakdown": friction_est.to_dict()
            }
        )

reversal_strategy = ReversalStrategy()
