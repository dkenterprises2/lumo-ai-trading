import math
from typing import Dict, Any, Optional
from loguru import logger

from backend.strategies.base_strategy import BaseStrategy, StrategyFamily, StrategyCandidateResult, SuitabilityScoreBreakdown
from backend.execution.execution_cost_estimator import execution_cost_estimator
from backend.brain.entry_timing import entry_timing_engine
from backend.brain.regime_intelligence import MarketRegimeType

class MeanReversionStrategy(BaseStrategy):
    """
    Phase 47 MEAN_REVERSION Strategy Family.
    Specialized for Range-Bound and Low-Volatility Consolidation regimes:
    - Volatility-normalized deviation (Z-score distance from 20 EMA)
    - Bollinger Band (2.0 std dev) boundary penetration and mean snap-back
    - RSI extreme boundaries with volume absorption (selling exhaustion / buying climax)
    - Single-source authoritative friction deduction
    """

    def __init__(self):
        super().__init__(StrategyFamily.MEAN_REVERSION)
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
        rsi_os = pair_parameters.rsi_oversold if pair_parameters else 30.0
        rsi_ob = pair_parameters.rsi_overbought if pair_parameters else 70.0
        strategy_id = f"{symbol.replace('/', '')}-MEANREV-V1"

        # 1. Technical Metrics Extraction
        ema_20 = float(technical_data.get("ema_20", current_price))
        rsi = float(technical_data.get("rsi", 50.0))
        atr = float(technical_data.get("atr", current_price * 0.02))
        atr_pct = (atr / max(1e-9, current_price)) * 100.0
        vol_spike = float(technical_data.get("volume_spike_ratio", 1.0))

        # Approximate Bollinger Bands (2.0 ATR equivalent if std not provided)
        bb_upper = float(technical_data.get("bb_upper", ema_20 + (atr * 1.5)))
        bb_lower = float(technical_data.get("bb_lower", ema_20 - (atr * 1.5)))

        # 2. Normalized Mean Deviation (Z-score)
        dist_from_mean = current_price - ema_20
        z_score = round(dist_from_mean / max(1e-4, atr), 2)

        # 3. Mean Reversion Signal Generation
        # Long Reversion: Price depressed below lower band / oversold RSI with absorption
        # Short Reversion: Price extended above upper band / overbought RSI with exhaustion
        is_oversold = (rsi <= rsi_os or current_price <= bb_lower or z_score <= -1.2)
        is_overbought = (rsi >= rsi_ob or current_price >= bb_upper or z_score >= 1.2)

        regime_enum = regime_state.regime if hasattr(regime_state, "regime") else MarketRegimeType.SIDEWAYS_RANGE
        stability = getattr(regime_state, "stability", 0.8)

        if is_oversold and not is_overbought:
            direction = "LONG"
            raw_strength = min(1.0, 0.55 + (abs(z_score) * 0.15) + (0.10 if rsi <= rsi_os else 0.0))
            signal_strength = round(raw_strength, 3)
            mr_reason = f"Oversold deviation (Z={z_score:.2f}, RSI={rsi:.1f}) below lower band -> Long Mean Snapback."
        elif is_overbought and not is_oversold:
            direction = "SHORT"
            raw_strength = min(1.0, 0.55 + (abs(z_score) * 0.15) + (0.10 if rsi >= rsi_ob else 0.0))
            signal_strength = round(-raw_strength, 3)
            mr_reason = f"Overbought deviation (Z=+{z_score:.2f}, RSI={rsi:.1f}) above upper band -> Short Mean Snapback."
        else:
            direction = "NEUTRAL"
            signal_strength = 0.0
            mr_reason = f"Price near local mean (Z={z_score:.2f}, RSI={rsi:.1f}); no boundary overshoot."

        # 4. Probability of Mean Reversion
        if direction != "NEUTRAL":
            base_prob = 0.54 + (min(0.16, abs(z_score) * 0.08) * stability)
            # In strong trends, mean reversion has lower success (trend drift hazard)
            if regime_enum in [MarketRegimeType.BULL_TREND, MarketRegimeType.BEAR_TREND]:
                base_prob -= 0.10
            prob_win = round(min(0.72, max(0.40, base_prob)), 3)
        else:
            prob_win = 0.500
        prob_loss = round(1.0 - prob_win, 3)

        # 5. Expected Gross Return
        expected_target_bps = min(atr_pct * 100.0 * 1.8, max(atr_pct * 100.0 * 0.8, abs(dist_from_mean / current_price) * 10000.0))
        expected_stop_bps = atr_pct * 100.0 * 1.0
        gross_edge_bps = round((prob_win * expected_target_bps) - (prob_loss * expected_stop_bps), 2) if direction != "NEUTRAL" else 0.0

        # 6. Single Authoritative Friction Deduction
        friction_est = execution_cost_estimator.estimate_pre_trade_friction(
            symbol=symbol,
            spread_bps=spread_bps,
            slippage_bps=slippage_bps,
            taker_fee_bps=15.0,
            latency_bps=1.5
        )
        total_friction_bps = friction_est.total_friction_bps
        expected_net_edge_bps = round(gross_edge_bps - total_friction_bps, 2)

        # 7. Regime Fit Scoring (0-25)
        if regime_enum in [MarketRegimeType.SIDEWAYS_RANGE, MarketRegimeType.LOW_VOL_COMPRESSION, MarketRegimeType.MEAN_REVERSION]:
            regime_fit = 25.0
        elif regime_enum == MarketRegimeType.RECOVERY_REVERSAL:
            regime_fit = 15.0
        elif regime_enum in [MarketRegimeType.BULL_TREND, MarketRegimeType.BEAR_TREND]:
            regime_fit = 0.0  # Mean reversion is high risk against strong trends
        else:
            regime_fit = 5.0

        # 8. Entry Timing Assessment
        entry_assess = entry_timing_engine.evaluate_entry_timing(
            symbol=symbol,
            direction=direction if direction != "NEUTRAL" else "LONG",
            current_price=current_price,
            technical_data=technical_data
        )
        entry_quality_str = entry_assess.quality.value if direction != "NEUTRAL" else "N/A"

        # 9. Suitability Score Calculation (0-100)
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
            reason = f"Mean Reversion {direction} qualified in [{regime_enum.value}] (Gross: +{gross_edge_bps:.1f}bps, Net: +{expected_net_edge_bps:.1f}bps, P(win)={prob_win*100:.1f}%)."
        elif direction == "NEUTRAL":
            reason = f"Mean Reversion Neutral: {mr_reason}"
        elif regime_fit < 15.0:
            reason = f"Mean Reversion rejected: Active regime [{regime_enum.value}] is unfavorable for range fading."
        elif not entry_assess.is_approved:
            reason = f"Mean Reversion rejected by timing: {entry_assess.reason}"
        else:
            reason = f"Mean Reversion net edge (+{expected_net_edge_bps:.1f}bps) < pair hurdle (+{min_hurdle_bps:.1f}bps) after friction (-{total_friction_bps:.1f}bps)."

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
                "z_score": z_score,
                "rsi": rsi,
                "bb_upper": bb_upper,
                "bb_lower": bb_lower,
                "mr_reason": mr_reason,
                "friction_breakdown": friction_est.to_dict()
            }
        )

mean_reversion_strategy = MeanReversionStrategy()
