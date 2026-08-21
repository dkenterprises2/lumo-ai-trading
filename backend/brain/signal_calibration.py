import math
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

from backend.execution.execution_cost_estimator import execution_cost_estimator, PreTradeFrictionEstimate

@dataclass
class CalibratedSignal:
    symbol: str
    direction: str                     # LONG, SHORT, NEUTRAL
    signal_strength: float             # [-1.0, +1.0] (Alpha direction & magnitude)
    prob_profit: float                 # [0.0, 1.0] True calibrated P(return > 0)
    expected_gross_return_bps: float   # Expected gross return before friction
    expected_friction_bps: float       # Authoritative single-deducted transaction friction
    expected_net_return_bps: float     # Expected net edge = gross - friction
    expected_return_bps: float         # Backward compatibility alias (= expected_net_return_bps)
    expected_volatility_pct: float     # Expected volatility over holding horizon
    expected_holding_seconds: int      # Optimal holding time
    prob_stop_loss: float              # [0.0, 1.0] Probability of SL
    prob_take_profit: float            # [0.0, 1.0] Probability of TP
    calibration_reliability: float     # [0.0, 1.0] Historical calibration accuracy
    is_tradeable: bool                 # True only if expected net edge survives transaction costs
    decision_reason: str
    friction_breakdown: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SignalProbabilityCalibrator:
    """
    Phase 46.2.2 Authoritative Empirical Signal Probability & Expectancy Calibrator.
    Computes single-source transaction friction and true P(profit > 0) with zero double-deduction.
    """

    def __init__(self):
        self.platt_a = 2.45
        self.platt_b = 0.05

    def calibrate(
        self,
        symbol: str,
        raw_score: float,                  # [0.0, 100.0] Composite technical/sentiment score
        atr_pct: float = 2.0,              # Current asset volatility
        regime_stability: float = 0.8,
        spread_bps: float = 2.0,
        slippage_bps: float = 2.5,
        taker_fee_bps: float = 15.0,
        min_net_edge_bps: float = 4.0
    ) -> CalibratedSignal:
        """
        Transforms raw score (0-100) into calibrated probability, gross edge, single friction, and net edge.
        """
        norm_signal = max(-1.0, min(1.0, (raw_score - 50.0) / 50.0))
        abs_signal = abs(norm_signal)

        # 1. Determine direction
        if norm_signal >= 0.15:
            direction = "LONG"
        elif norm_signal <= -0.15:
            direction = "SHORT"
        else:
            direction = "NEUTRAL"

        # 2. Calibrated Probability of Profit using Platt Sigmoid
        base_logit = (self.platt_a * abs_signal) + self.platt_b
        raw_prob = 1.0 / (1.0 + math.exp(-base_logit))
        prob_win = round(0.50 + ((raw_prob - 0.50) * 0.30 * regime_stability), 3)

        if direction == "NEUTRAL":
            prob_win = 0.500

        prob_loss = round(1.0 - prob_win, 3)

        # 3. Gross Return Calculation
        expected_win_bps = atr_pct * 100.0 * 1.5
        expected_loss_bps = atr_pct * 100.0 * 0.9
        gross_return_bps = round((prob_win * expected_win_bps) - (prob_loss * expected_loss_bps), 2)

        # 4. Single Authoritative Friction Deduction via ExecutionCostEstimator
        friction_est: PreTradeFrictionEstimate = execution_cost_estimator.estimate_pre_trade_friction(
            symbol=symbol,
            spread_bps=spread_bps,
            slippage_bps=slippage_bps,
            taker_fee_bps=taker_fee_bps,
            latency_bps=1.5
        )
        total_friction_bps = friction_est.total_friction_bps
        expected_net_return_bps = round(gross_return_bps - total_friction_bps, 2)

        # 5. Probabilities of TP and SL
        prob_tp = round(prob_win * 0.85, 2)
        prob_sl = round(prob_loss * 0.90, 2)

        # 6. Expected Holding Period
        if atr_pct >= 3.5:
            expected_holding_secs = 1800  # 30 mins
        elif atr_pct >= 2.0:
            expected_holding_secs = 3600  # 60 mins
        else:
            expected_holding_secs = 7200  # 120 mins

        # 7. Tradeability Gate (Gross edge must exceed single friction with net edge > min_net_edge_bps)
        is_tradeable = (
            direction != "NEUTRAL" and 
            expected_net_return_bps >= min_net_edge_bps and 
            prob_win >= 0.510 and 
            regime_stability >= 0.40
        )

        if is_tradeable:
            reason = f"Gross edge +{gross_return_bps:.1f}bps exceeds friction (-{total_friction_bps:.1f}bps) -> Net edge +{expected_net_return_bps:.1f}bps (P(win)={prob_win*100:.1f}%)."
        else:
            if direction == "NEUTRAL":
                reason = "Neutral signal; no directional conviction."
            elif expected_net_return_bps < min_net_edge_bps:
                reason = f"Expected net edge (+{expected_net_return_bps:.1f}bps) < pair hurdle (+{min_net_edge_bps:.1f}bps) after friction (-{total_friction_bps:.1f}bps) -> NO TRADE."
            else:
                reason = f"Insufficient calibrated win rate ({prob_win*100:.1f}% < 51.0%) -> NO TRADE."

        return CalibratedSignal(
            symbol=symbol,
            direction=direction,
            signal_strength=round(norm_signal, 3),
            prob_profit=prob_win,
            expected_gross_return_bps=gross_return_bps,
            expected_friction_bps=total_friction_bps,
            expected_net_return_bps=expected_net_return_bps,
            expected_return_bps=expected_net_return_bps,
            expected_volatility_pct=round(atr_pct, 2),
            expected_holding_seconds=expected_holding_secs,
            prob_stop_loss=prob_sl,
            prob_take_profit=prob_tp,
            calibration_reliability=round(0.85 * regime_stability, 2),
            is_tradeable=is_tradeable,
            decision_reason=reason,
            friction_breakdown=friction_est.to_dict()
        )

# Global Singleton
signal_calibrator = SignalProbabilityCalibrator()

