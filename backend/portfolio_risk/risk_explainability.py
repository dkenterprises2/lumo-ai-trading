from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class RiskDecisionExplanation:
    decision: str # ALLOWED, SCALED, BLOCKED
    symbol: str
    side: str
    requested_allocation_usd: float
    approved_allocation_usd: float
    effective_max_positions: int
    currently_open_positions: int
    remaining_risk_budget_pct: float
    primary_factor: str
    detailed_reasons: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RiskExplainabilityEngine:
    """Formats mandatory explainability reports for every trade execution decision."""

    def format_explanation(
        self,
        decision: str,
        symbol: str,
        side: str,
        requested_alloc: float,
        approved_alloc: float,
        effective_limit: int,
        open_positions: int,
        rem_budget_pct: float,
        primary_factor: str,
        reasons: List[str]
    ) -> RiskDecisionExplanation:
        """Create structured decision explanation."""
        return RiskDecisionExplanation(
            decision=decision,
            symbol=symbol,
            side=side,
            requested_allocation_usd=round(requested_alloc, 2),
            approved_allocation_usd=round(approved_alloc, 2),
            effective_max_positions=effective_limit,
            currently_open_positions=open_positions,
            remaining_risk_budget_pct=round(rem_budget_pct, 2),
            primary_factor=primary_factor,
            detailed_reasons=reasons
        )
