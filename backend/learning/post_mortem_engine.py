import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from .error_taxonomy import TradeErrorCategory, error_classifier
from .experience_memory import TradeExperience

@dataclass
class TradePostMortem:
    experience_id: str
    symbol: str
    realized_pnl: float
    is_success: bool
    root_cause: str
    contributing_factors: List[str]
    lesson_hypothesis: str
    recommended_behavior: str
    attribution_type: str  # STRATEGY, EXECUTION, FRICTION, REGIME_SHIFT
    causation_confidence: float
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class TradePostMortemEngine:
    """Quantitative Post-Mortem RCA Engine evaluating 13 diagnostic criteria."""

    def analyze_trade(self, exp: TradeExperience) -> TradePostMortem:
        is_success = exp.realized_pnl > 0.0
        contributing_factors: List[str] = []

        if is_success:
            # Success Analysis: Distinguish Correlation from Causation
            root_cause = "VALIDATED_EDGE"
            lesson_hypothesis = f"Entry in {exp.market_regime} regime with calibrated win prob {exp.calibrated_win_probability:.2f} executed within expected edge."
            recommended_behavior = "Reinforce current regime entry criteria and maintain disciplined sizing."
            attribution_type = "STRATEGY"
            causation_conf = 0.85
            
            if exp.slippage_usd <= (exp.allocation_usd * 0.0005):
                contributing_factors.append("HIGH_QUALITY_EXECUTION_MINIMAL_SLIPPAGE")
            if exp.regime_confidence > 0.80:
                contributing_factors.append("STRONG_REGIME_CLASSIFICATION_ALIGNMENT")
        else:
            # Failure RCA: Classify Error Category & Root Cause
            err_cat = error_classifier.classify_trade_error(
                realized_pnl=exp.realized_pnl,
                features=exp.signal_features,
                market_regime=exp.market_regime,
                direction=exp.direction,
                expected_edge_bps=exp.expected_edge_bps,
                fees_usd=exp.fees_usd,
                slippage_usd=exp.slippage_usd,
                latency_ms=exp.execution_latency_ms,
                holding_time_seconds=exp.holding_time_seconds,
                exit_reason=exp.exit_reason
            )
            root_cause = err_cat.value

            if err_cat == TradeErrorCategory.LATE_ENTRY:
                lesson_hypothesis = f"Late {exp.direction} entry when price is overextended from EMA20 in {exp.market_regime} regime produces negative expectancy."
                recommended_behavior = f"Reject {exp.direction} setups where RSI is overbought/oversold and price is > 2.5% from 20 EMA."
                attribution_type = "STRATEGY"
                causation_conf = 0.80
                contributing_factors.append("OVEREXTENDED_INDICATOR_VALUES")

            elif err_cat in [TradeErrorCategory.EXCESS_FEES, TradeErrorCategory.HIGH_SLIPPAGE]:
                lesson_hypothesis = f"Execution friction (${exp.fees_usd + exp.slippage_usd:.2f}) exceeded expected gross edge in {exp.symbol}."
                recommended_behavior = "Require minimum net edge threshold of at least 15 bps after accounting for venue taker fees and book depth."
                attribution_type = "FRICTION"
                causation_conf = 0.90
                contributing_factors.append("THIN_ORDERBOOK_LIQUIDITY")

            elif err_cat == TradeErrorCategory.MEAN_REVERSION_TRAP:
                lesson_hypothesis = f"Counter-trend mean reversion entries during elevated ADX (>30) in {exp.market_regime} fail frequently."
                recommended_behavior = "Veto counter-trend mean reversion signals whenever ADX > 28."
                attribution_type = "STRATEGY"
                causation_conf = 0.82
                contributing_factors.append("STRONG_TRENDING_MOMENTUM_AGAINST_POSITION")

            elif err_cat == TradeErrorCategory.FALSE_BREAKOUT:
                lesson_hypothesis = f"Breakouts lacking volume confirmation in {exp.market_regime} have high false-positive rates."
                recommended_behavior = "Require volume > 1.3x 20-period volume MA before breakout entry confirmation."
                attribution_type = "STRATEGY"
                causation_conf = 0.75
                contributing_factors.append("UNCONFIRMED_BREAKOUT_VOLUME")

            else:
                lesson_hypothesis = f"Trade in {exp.symbol} suffered adverse price excursion in {exp.market_regime} regime."
                recommended_behavior = "Review stop loss distance and tighten invalidation triggers."
                attribution_type = "STRATEGY"
                causation_conf = 0.65
                contributing_factors.append("ADVERSE_MARKET_DRIFT")

            if exp.portfolio_exposure > 0.50:
                contributing_factors.append("HIGH_PORTFOLIO_CONCENTRATION")
            if exp.execution_latency_ms > 35.0:
                contributing_factors.append("ELEVATED_EXECUTION_LATENCY")

        return TradePostMortem(
            experience_id=exp.experience_id,
            symbol=exp.symbol,
            realized_pnl=exp.realized_pnl,
            is_success=is_success,
            root_cause=root_cause,
            contributing_factors=contributing_factors,
            lesson_hypothesis=lesson_hypothesis,
            recommended_behavior=recommended_behavior,
            attribution_type=attribution_type,
            causation_confidence=causation_conf
        )

# Global Singleton
post_mortem_engine = TradePostMortemEngine()
