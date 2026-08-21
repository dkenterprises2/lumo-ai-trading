from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from loguru import logger

from backend.strategies.base_strategy import StrategyFamily, StrategyCandidateResult, BaseStrategy
from backend.strategies.trend_strategy import trend_strategy
from backend.strategies.mean_reversion_strategy import mean_reversion_strategy
from backend.strategies.breakout_strategy import breakout_strategy
from backend.strategies.reversal_strategy import reversal_strategy

@dataclass
class MetaSelectorDecision:
    action: str                                    # SELECT_STRATEGY or NO_TRADE
    pair: str
    regime: str
    regime_confidence: float
    selected_strategy: Optional[StrategyCandidateResult]
    candidate_results: Dict[str, StrategyCandidateResult]
    selection_thesis: str
    rejection_reasons_by_family: Dict[str, str]
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "pair": self.pair,
            "regime": self.regime,
            "regime_confidence": self.regime_confidence,
            "selected_strategy": self.selected_strategy.to_dict() if self.selected_strategy else None,
            "candidate_results": {k: v.to_dict() for k, v in self.candidate_results.items()},
            "selection_thesis": self.selection_thesis,
            "rejection_reasons_by_family": self.rejection_reasons_by_family,
            "timestamp": self.timestamp
        }

class MetaStrategySelector:
    """
    Phase 47 Deterministic & Transparent Meta Strategy Selector.
    Evaluates all 4 strategy families (TREND, MEAN_REVERSION, BREAKOUT, REVERSAL)
    against the detected market regime, expected net edge, single-source friction,
    and multi-factor suitability scoring.
    """

    def __init__(self):
        self.strategies: Dict[StrategyFamily, BaseStrategy] = {
            StrategyFamily.TREND: trend_strategy,
            StrategyFamily.MEAN_REVERSION: mean_reversion_strategy,
            StrategyFamily.BREAKOUT: breakout_strategy,
            StrategyFamily.REVERSAL: reversal_strategy
        }
        self.min_suitability_threshold: float = 55.0

    def evaluate_all_strategies(
        self,
        symbol: str,
        current_price: float,
        technical_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        regime_state: Any,
        orderbook_data: Optional[Dict[str, Any]] = None,
        pair_parameters: Optional[Any] = None,
        timestamp: float = 0.0
    ) -> MetaSelectorDecision:
        regime_name = regime_state.regime.value if hasattr(regime_state, "regime") else str(regime_state)
        regime_conf = getattr(regime_state, "confidence", 0.85)

        candidates: Dict[str, StrategyCandidateResult] = {}
        rejection_reasons: Dict[str, str] = {}

        # 1. Evaluate each strategy family independently
        for family, strat in self.strategies.items():
            res = strat.evaluate_candidate(
                symbol=symbol,
                current_price=current_price,
                technical_data=technical_data,
                sentiment_data=sentiment_data,
                regime_state=regime_state,
                orderbook_data=orderbook_data,
                pair_parameters=pair_parameters
            )
            candidates[family.value] = res
            rejection_reasons[family.value] = res.decision_reason

        # 2. Filter for qualified tradeable candidates
        qualified_candidates = [
            res for res in candidates.values()
            if res.is_tradeable and res.suitability_score >= self.min_suitability_threshold
        ]

        # 3. Select optimal strategy or emit NO_TRADE
        if qualified_candidates:
            # Rank candidates by: 1) Suitability Score, 2) Expected Net Edge
            qualified_candidates.sort(
                key=lambda x: (x.suitability_score, x.expected_net_edge_bps),
                reverse=True
            )
            winner = qualified_candidates[0]
            action = "SELECT_STRATEGY"
            thesis = (
                f"Selected {winner.family.value} ({winner.direction}) for {symbol} in [{regime_name}] "
                f"with Suitability {winner.suitability_score:.1f}/100 and Net Edge +{winner.expected_net_edge_bps:.1f}bps."
            )
            # Update rejection reasons for unselected families
            for family_str, res in candidates.items():
                if family_str != winner.family.value and not res.is_tradeable:
                    pass  # Keep original rejection reason
                elif family_str != winner.family.value:
                    rejection_reasons[family_str] = (
                        f"Outranked by {winner.family.value} (Suitability {res.suitability_score:.1f} vs {winner.suitability_score:.1f})."
                    )

            return MetaSelectorDecision(
                action=action,
                pair=symbol,
                regime=regime_name,
                regime_confidence=regime_conf,
                selected_strategy=winner,
                candidate_results=candidates,
                selection_thesis=thesis,
                rejection_reasons_by_family=rejection_reasons,
                timestamp=timestamp
            )
        else:
            action = "NO_TRADE"
            thesis = (
                f"NO_TRADE for {symbol} in [{regime_name}]: No strategy family qualified. "
                f"All 4 candidates failed net edge hurdle or regime suitability criteria."
            )
            return MetaSelectorDecision(
                action=action,
                pair=symbol,
                regime=regime_name,
                regime_confidence=regime_conf,
                selected_strategy=None,
                candidate_results=candidates,
                selection_thesis=thesis,
                rejection_reasons_by_family=rejection_reasons,
                timestamp=timestamp
            )

meta_strategy_selector = MetaStrategySelector()
