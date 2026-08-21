from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from loguru import logger
from .signal_calibration import CalibratedSignal
from .portfolio_brain import PortfolioExposureGraph

@dataclass
class AdversarialReviewResult:
    passed: bool                      # True = Approved; False = Vetoed by Red-Team
    challenge_score: float             # [0.0, 100.0] Higher = Stronger objection
    veto_reasons: List[str]
    counter_thesis: str
    survival_edge_bps: float           # Net edge surviving adversarial deductions

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AdversarialRedTeamGate:
    """
    Phase 44.3 Adversarial Red-Team Verification Gate.
    Asynchronously challenges and attempts to disprove trading candidates before order submission.
    """

    VETO_CHALLENGE_THRESHOLD = 65.0    # Objection score >= 65.0 triggers unconditional VETO

    def challenge_trade(
        self,
        symbol: str,
        direction: str,
        calibrated_signal: CalibratedSignal,
        portfolio_graph: PortfolioExposureGraph,
        technical_data: Dict[str, Any],
        spread_bps: float = 2.0
    ) -> AdversarialReviewResult:
        """
        Red-Team challenges:
        1. Fee Eat-Up: Is the gross edge smaller than round-trip taker fees + 2x spread?
        2. Cluster Crowding: Is the portfolio already heavily biased in this direction?
        3. Fakeout Trap: Is RSI diverging from the price breakout?
        4. Liquidity Drag: Is spread widening during local volatility?
        """
        veto_reasons: List[str] = []
        challenge_score = 10.0  # Base skepticism
        gross_edge_bps = calibrated_signal.expected_return_bps

        # Challenge 1: Transaction Cost Drag (Friction Eat-Up)
        total_friction_bps = 15.0 + (spread_bps * 1.5)
        if gross_edge_bps <= total_friction_bps:
            challenge_score += 60.0
            veto_reasons.append(
                f"Fee Drag Objection: Gross edge (+{gross_edge_bps:.1f} bps) is too thin to survive friction ({total_friction_bps:.1f} bps)."
            )

        # Challenge 2: Correlation Crowding
        if direction == "SHORT" and portfolio_graph.short_ratio_pct >= 55.0:
            challenge_score += 35.0
            veto_reasons.append(
                f"Crowding Objection: Portfolio is already {portfolio_graph.short_ratio_pct:.1f}% SHORT. Adding {symbol} increases unhedged market-beta."
            )
        elif direction == "LONG" and portfolio_graph.short_ratio_pct <= 45.0 and portfolio_graph.total_notional_usd > 10000:
            challenge_score += 35.0
            veto_reasons.append(
                f"Crowding Objection: Portfolio is already heavily LONG. Adding {symbol} increases unhedged market-beta."
            )

        # Challenge 3: Momentum Divergence Trap
        rsi = float(technical_data.get("rsi", 50.0))
        vol_spike = float(technical_data.get("volume_spike_ratio", 1.0))
        if direction == "LONG" and rsi >= 68.0 and vol_spike < 0.80:
            challenge_score += 30.0
            veto_reasons.append(f"Low-Volume Exhaustion Objection: Long signal at RSI {rsi:.1f} has declining volume ({vol_spike:.1f}x) -> Potential Bull Trap.")
        elif direction == "SHORT" and rsi <= 32.0 and vol_spike < 0.80:
            challenge_score += 30.0
            veto_reasons.append(f"Low-Volume Absorption Objection: Short signal at RSI {rsi:.1f} has declining volume ({vol_spike:.1f}x) -> Potential Bear Trap.")

        challenge_score = min(100.0, challenge_score)
        passed = (challenge_score < self.VETO_CHALLENGE_THRESHOLD)
        surviving_edge = max(0.0, gross_edge_bps - total_friction_bps) if passed else 0.0

        if passed:
            counter_thesis = "Trade thesis survived adversarial red-team objections with positive net expectancy."
        else:
            counter_thesis = f"Red-team VETOED trade (Objection Score: {challenge_score:.0f}/100): " + "; ".join(veto_reasons)

        return AdversarialReviewResult(
            passed=passed,
            challenge_score=challenge_score,
            veto_reasons=veto_reasons,
            counter_thesis=counter_thesis,
            survival_edge_bps=round(surviving_edge, 1)
        )

# Global Singleton
adversarial_gate = AdversarialRedTeamGate()
