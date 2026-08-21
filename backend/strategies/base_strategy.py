import abc
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

class StrategyFamily(str, Enum):
    TREND = "TREND"
    MEAN_REVERSION = "MEAN_REVERSION"
    BREAKOUT = "BREAKOUT"
    REVERSAL = "REVERSAL"

@dataclass
class SuitabilityScoreBreakdown:
    regime_fit: float = 0.0              # Max 25.0 pts
    net_edge_score: float = 0.0          # Max 25.0 pts
    calibration_score: float = 0.0       # Max 20.0 pts
    fee_slippage_resistance: float = 0.0 # Max 15.0 pts
    sample_degradation_score: float = 0.0# Max 15.0 pts
    total_score: float = 0.0             # Max 100.0 pts

    def calculate_total(self) -> float:
        self.total_score = round(
            self.regime_fit + self.net_edge_score + self.calibration_score +
            self.fee_slippage_resistance + self.sample_degradation_score, 1
        )
        return self.total_score

    def to_dict(self) -> Dict[str, Any]:
        self.calculate_total()
        return asdict(self)

@dataclass
class StrategyCandidateResult:
    strategy_id: str
    family: StrategyFamily
    pair: str
    version: str
    direction: str                     # LONG, SHORT, NEUTRAL
    signal_strength: float             # [-1.0, +1.0]
    calibrated_probability: float      # [0.0, 1.0]
    expected_gross_edge_bps: float
    estimated_friction_bps: float
    expected_net_edge_bps: float
    entry_quality: str                 # EXCELLENT, GOOD, MARGINAL, LATE, REJECT, N/A
    risk_state: str                    # NORMAL, ELEVATED, BLOCKED
    regime_fit_score: float            # [0.0, 25.0]
    suitability_score: float           # [0.0, 100.0]
    suitability_breakdown: SuitabilityScoreBreakdown = field(default_factory=SuitabilityScoreBreakdown)
    decision_reason: str = ""
    is_tradeable: bool = False
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["family"] = self.family.value if isinstance(self.family, StrategyFamily) else self.family
        d["suitability_breakdown"] = self.suitability_breakdown.to_dict()
        return d

class BaseStrategy(abc.ABC):
    """
    Phase 47 Abstract Base Strategy Family Interface.
    Every strategy family implements independent signal generation, expected gross edge,
    authoritative single friction deduction, and entry quality assessment.
    """

    def __init__(self, family: StrategyFamily):
        self.family = family

    @abc.abstractmethod
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
        """Evaluates market opportunity for this strategy family."""
        pass
