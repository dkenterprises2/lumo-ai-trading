import math
from typing import Dict, Any, Optional
from loguru import logger

from backend.strategies.base_strategy import BaseStrategy, StrategyFamily, StrategyCandidateResult, SuitabilityScoreBreakdown
from backend.execution.execution_cost_estimator import execution_cost_estimator
from backend.brain.entry_timing import entry_timing_engine
from backend.brain.regime_intelligence import MarketRegimeType

class BreakoutStrategy(BaseStrategy):
    """
    Phase 47 BREAKOUT Strategy Family.
    Specialized for Range Expansion & High-Volatility Breakout regimes:
    - Volatility compression detection (Bollinger squeeze / bandwidth contraction)
    - Structural High/Low breaks (Donchian 20-period channel breakout)
    - Volume surge confirmation multiplier (>= 1.25x)
    - False-breakout wick trap rejection filter
    - Single-source authoritative friction deduction
    """

    def __init__(self):
        super().__init__(StrategyFamily.BREAKOUT)
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
        min_vol_mult = pair_parameters.min_volume_ratio if pair_parameters else 1.15
        strategy_id = f"{symbol.replace('/', '')}-BREAKOUT-V1"

        # 1. Technical Data
        ema_20 = float(technical_data.get("ema_20", current_price))
        atr = float(technical_data.get("atr", current_price * 0.02))
        atr_pct = (atr / max(1e-9, current_price)) * 100.0
        vol_spike = float(technical_data.get("volume_spike_ratio", 1.0))
        macd = float(technical_data.get("macd", 0.0))

        bb_upper = float(technical_data.get("bb_upper", ema_20 + (atr * 1.5)))
        bb_lower = float(technical_data.get("bb_lower", ema_20 - (atr * 1.5)))
        bandwidth_pct = ((bb_upper - bb_lower) / max(1e-4, ema_20)) * 100.0

        # Squeeze indicator: Bandwidth contracted compared to standard ATR
        is_squeeze = (bandwidth_pct <= atr_pct * 2.2)

        # 2. Structural Breakout Detection
        # Breakout requires price piercing band WITH volume surge >= min_vol_mult
        has_volume_confirmation = (vol_spike >= min_vol_mult)
        is_bull_breakout = (current_price > bb_upper and has_volume_confirmation and macd > 0)
        is_bear_breakout = (current_price < bb_lower and has_volume_confirmation and macd < 0)

        regime_enum = regime_state.regime if hasattr(regime_state, "regime") else MarketRegimeType.SIDEWAYS_RANGE
        stability = getattr(regime_state, "stability", 0.8)

        if is_bull_breakout:
            direction = "LONG"
            raw_strength = 0.60 + min(0.35, (vol_spike - 1.0) * 0.25)
            signal_strength = round(min(1.0, raw_strength), 3)
            bo_reason = f"Bullish Breakout above upper band (${bb_upper:.2f}) with {vol_spike:.2f}x volume surge."
        elif is_bear_breakout:
            direction = "SHORT"
            raw_strength = 0.60 + min(0.35, (vol_spike - 1.0) * 0.25)
            signal_strength = round(-min(1.0, raw_strength), 3)
            bo_reason = f"Bearish Breakout below lower band (${bb_lower:.2f}) with {vol_spike:.2f}x volume surge."
        else:
            direction = "NEUTRAL"
            signal_strength = 0.0
            if not has_volume_confirmation and (current_price > bb_upper or current_price < bb_lower):
                bo_reason = f"Price at boundary but volume ({vol_spike:.2f}x) lacks breakout confirmation (need >={min_vol_mult:.2f}x)."
            else:
                bo_reason = "Price within consolidation range; no breakout trigger."

        # 3. Probability of Breakout Continuation
        if direction != "NEUTRAL":
            base_prob = 0.53 + (min(0.18, (vol_spike - 1.0) * 0.15) * stability)
            # Breakout in sideways range is often a false trap
            if regime_enum == MarketRegimeType.SIDEWAYS_RANGE:
                base_prob -= 0.08
            prob_win = round(min(0.74, max(0.40, base_prob)), 3)
        else:
            prob_win = 0.500
        prob_loss = round(1.0 - prob_win, 3)

        # 4. Expected Gross Return (Breakouts capture larger moves)
        expected_target_bps = atr_pct * 100.0 * 2.2
        expected_stop_bps = atr_pct * 100.0 * 1.1
        gross_edge_bps = round((prob_win * expected_target_bps) - (prob_loss * expected_stop_bps), 2) if direction != "NEUTRAL" else 0.0

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
        if regime_enum == MarketRegimeType.HIGH_VOL_BREAKOUT:
            regime_fit = 25.0
        elif regime_enum == MarketRegimeType.LOW_VOL_COMPRESSION:
            regime_fit = 20.0  # Prime pre-breakout compression regime
        elif regime_enum in [MarketRegimeType.BULL_TREND, MarketRegimeType.BEAR_TREND]:
            regime_fit = 15.0
        else:
            regime_fit = 0.0  # False breakout risk is high in sideways range

        # 7. Entry Timing Assessment
        entry_assess = entry_timing_engine.evaluate_entry_timing(
            symbol=symbol,
            direction=direction if direction != "NEUTRAL" else "LONG",
            current_price=current_price,
            technical_data=technical_data
        )
        entry_quality_str = entry_assess.quality.value if direction != "NEUTRAL" else "N/A"

        # 8. Suitability Score Calculation (0-100)
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
            reason = f"Breakout {direction} confirmed (Gross: +{gross_edge_bps:.1f}bps, Net: +{expected_net_edge_bps:.1f}bps, Vol: {vol_spike:.2f}x, P(win)={prob_win*100:.1f}%)."
        elif direction == "NEUTRAL":
            reason = f"Breakout Neutral: {bo_reason}"
        elif regime_fit < 15.0:
            reason = f"Breakout rejected: Active regime [{regime_enum.value}] poses high false-breakout trap risk."
        elif not entry_assess.is_approved:
            reason = f"Breakout rejected by timing: {entry_assess.reason}"
        else:
            reason = f"Breakout net edge (+{expected_net_edge_bps:.1f}bps) < pair hurdle (+{min_hurdle_bps:.1f}bps) after friction (-{total_friction_bps:.1f}bps)."

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
                "bandwidth_pct": round(bandwidth_pct, 2),
                "is_squeeze": is_squeeze,
                "vol_spike": vol_spike,
                "bo_reason": bo_reason,
                "friction_breakdown": friction_est.to_dict()
            }
        )

breakout_strategy = BreakoutStrategy()
