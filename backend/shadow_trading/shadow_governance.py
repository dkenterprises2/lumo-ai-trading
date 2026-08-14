from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class ShadowGovernanceValidationResult:
    is_approved: bool
    status: str  # DRAFT, UNDER_REVIEW, SHADOW_APPROVED, SHADOW_RUNNING, SHADOW_HALTED, SHADOW_COMPLETED
    reasons: list

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ShadowGovernance:
    """Approval Workflow Governance for Shadow Trading Sessions."""

    def validate_shadow_approval(
        self,
        portfolio_heat_utilization_pct: float = 20.0,
        kill_switch_state: str = "NORMAL",
        paper_readiness_score: float = 97.4
    ) -> ShadowGovernanceValidationResult:
        reasons = []
        is_ok = True

        if portfolio_heat_utilization_pct >= 70.0:
            is_ok = False
            reasons.append(f"Portfolio heat utilization ({portfolio_heat_utilization_pct}%) >= 70% threshold")

        if kill_switch_state != "NORMAL":
            is_ok = False
            reasons.append(f"Kill switch is in {kill_switch_state} state (must be NORMAL)")

        if paper_readiness_score <= 95.0:
            is_ok = False
            reasons.append(f"Paper trading readiness score ({paper_readiness_score}) <= 95.0 minimum requirement")

        status = "SHADOW_APPROVED" if is_ok else "SHADOW_HALTED"
        return ShadowGovernanceValidationResult(
            is_approved=is_ok,
            status=status,
            reasons=reasons
        )
