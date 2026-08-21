import math
from typing import Dict, Any, Optional
from loguru import logger

from backend.strategies.base_strategy import BaseStrategy, StrategyFamily, StrategyCandidateResult, SuitabilityScoreBreakdown
from backend.execution.execution_cost_estimator import execution_cost_estimator
from backend.brain.entry_timing import entry_timing_engine
from backend.brain.regime_intelligence import MarketRegimeType

class TrendStrategy(BaseStrategy):
    """
    Phase 47 TREND Strategy Family.
    Preserves the established Trend-following architecture:
    - Triple EMA alignment (EMA20 vs EMA50 vs EMA200)
    - MACD histogram momentum and directional slope
    - ADX trend strength filtering (ADX >= 20)
    - Single-source authoritative friction deduction
    """

    def __init__(self):
        super().__init__(StrategyFamily.TREND)
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
        strategy_id = f"{symbol.replace('/', '')}-TREND-V1"

        # 1. Technical Factors Extraction
        ema_20 = float(technical_data.get("ema_20", current_price))
        ema_50 = float(technical_data.get("ema_50", current_price))
        ema_200 = float(technical_data.get("ema_200", current_price))
        macd = float(technical_data.get("macd", 0.0))
        macd_signal = float(technical_data.get("macd_signal", 0.0))
        macd_hist = macd - macd_signal
        adx = float(technical_data.get("adx", 25.0))
        atr = float(technical_data.get("atr", current_price * 0.02))
        atr_pct = (atr / max(1e-9, current_price)) * 100.0
        vol_spike = float(technical_data.get("volume_spike_ratio", 1.0))

        # 2. Trend Signal Direction & Strength
        is_bull_align = (current_price > ema_20 > ema_50 > ema_200)
        is_bear_align = (current_price < ema_20 < ema_50 < ema_200)

        if is_bull_align and macd_hist > 0 and adx >= 20.0:
            direction = "LONG"
            raw_strength = 0.65 + min(0.30, (adx - 20.0) / 40.0) + (0.05 if vol_spike >= 1.10 else 0.0)
            signal_strength = round(min(1.0, raw_strength), 3)
            trend_reason = f"Bullish Triple EMA alignment with positive MACD (+{macd_hist:.2f}) and ADX ({adx:.1f})"
        elif is_bear_align and macd_hist < 0 and adx >= 20.0:
            direction = "SHORT"
            raw_strength = 0.65 + min(0.30, (adx - 20.0) / 40.0) + (0.05 if vol_spike >= 1.10 else 0.0)
            signal_strength = round(-min(1.0, raw_strength), 3)
            trend_reason = f"Bearish Triple EMA alignment with negative MACD ({macd_hist:.2f}) and ADX ({adx:.1f})"
        else:
            direction = "NEUTRAL"
            signal_strength = 0.0
            trend_reason = "No confirmed triple EMA trend alignment or ADX < 20"

        # 3. Probability of Trend Continuation
        regime_enum = regime_state.regime if hasattr(regime_state, "regime") else MarketRegimeType.SIDEWAYS_RANGE
        stability = getattr(regime_state, "stability", 0.8)

        if direction != "NEUTRAL":
            base_prob = 0.52 + (abs(signal_strength) * 0.12 * stability)
            prob_win = round(min(0.75, max(0.45, base_prob)), 3)
        else:
            prob_win = 0.500
        prob_loss = round(1.0 - prob_win, 3)

        # 4. Expected Gross Return
        expected_win_bps = atr_pct * 100.0 * 1.5
        expected_loss_bps = atr_pct * 100.0 * 0.9
        gross_edge_bps = round((prob_win * expected_win_bps) - (prob_loss * expected_loss_bps), 2) if direction != "NEUTRAL" else 0.0

        # 5. Authoritative Single Friction Deduction
        friction_est = execution_cost_estimator.estimate_pre_trade_friction(
            symbol=symbol,
            spread_bps=spread_bps,
            slippage_bps=slippage_bps,
            taker_fee_bps=15.0,
            latency_bps=1.5
        )
        total_friction_bps = friction_est.total_friction_bps
        expected_net_edge_bps = round(gross_edge_bps - total_friction_bps, 2)

        # 6. Regime Fit Scoring (0-25)
        if regime_enum in [MarketRegimeType.BULL_TREND, MarketRegimeType.BEAR_TREND]:
            regime_fit = 25.0
        elif regime_enum == MarketRegimeType.HIGH_VOL_BREAKOUT:
            regime_fit = 15.0
        elif regime_enum == MarketRegimeType.SIDEWAYS_RANGE:
            regime_fit = 5.0
        else:
            regime_fit = 0.0

        # 7. Entry Timing Assessment
        entry_assess = entry_timing_engine.evaluate_entry_timing(
            symbol=symbol,
            direction=direction if direction != "NEUTRAL" else "LONG",
            current_price=current_price,
            technical_data=technical_data
        )
        entry_quality_str = entry_assess.quality.value if direction != "NEUTRAL" else "N/A"

        # 8. Suitability Breakdown Calculation (0-100)
        net_edge_pts = min(25.0, max(0.0, (expected_net_edge_bps / max(1.0, min_hurdle_bps * 2.0)) * 25.0))
        calib_pts = min(20.0, max(0.0, ((prob_win - 0.50) / 0.20) * 20.0))
        fee_res_pts = min(15.0, max(0.0, (gross_edge_bps / max(1.0, total_friction_bps)) * 7.5))
        sample_pts = 15.0  # Established base strategy

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
            entry_assess.is_approved and
            regime_fit >= 10.0
        )

        if is_tradeable:
            reason = f"Trend {direction} confirmed (+{gross_edge_bps:.1f}bps gross - {total_friction_bps:.1f}bps friction = +{expected_net_edge_bps:.1f}bps net). P(win)={prob_win*100:.1f}%."
        elif direction == "NEUTRAL":
            reason = f"Trend Neutral: {trend_reason}"
        elif regime_fit < 10.0:
            reason = f"Trend strategy rejected: Active regime [{regime_enum.value}] is unfavorable (Regime Fit {regime_fit}/25)."
        elif not entry_assess.is_approved:
            reason = f"Trend strategy rejected by timing: {entry_assess.reason}"
        else:
            reason = f"Trend strategy net edge (+{expected_net_edge_bps:.1f}bps) < pair hurdle (+{min_hurdle_bps:.1f}bps) after friction (-{total_friction_bps:.1f}bps)."

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
                "adx": adx,
                "macd_hist": macd_hist,
                "ema_alignment": "BULLISH" if is_bull_align else ("BEARISH" if is_bear_align else "MIXED"),
                "trend_reason": trend_reason,
                "friction_breakdown": friction_est.to_dict()
            }
        )

trend_strategy = TrendStrategy()
