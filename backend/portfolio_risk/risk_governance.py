from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class RiskGovernanceEvaluation:
    candidate_id: str
    approved: bool
    status: str # APPROVED, REJECTED, PENDING_REVIEW
    safety_violations: List[str]
    audit_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RiskGovernanceEngine:
    """Governance gate enforcing deterministic safety limits on self-learning loop parameter candidates."""

    def evaluate_candidate_parameters(
        self,
        candidate_id: str,
        learned_parameters: Dict[str, Any],
        user_hard_limits: Dict[str, Any]
    ) -> RiskGovernanceEvaluation:
        """Evaluate Phase 25 candidate risk parameters against hard governance rules."""
        violations = []

        # Rule 1: Dynamic trade limit multiplier cannot exceed 1.0
        if learned_parameters.get("dynamic_trade_limit_multiplier", 1.0) > 1.0:
            violations.append("Candidate attempts to expand trade limit beyond safe 1.0x ceiling.")

        # Rule 2: Cannot disable kill-switch or risk budget checks
        if learned_parameters.get("disable_kill_switch", False):
            violations.append("Candidate attempts to disable system kill-switch.")

        # Rule 3: Cannot exceed user's configured hard leverage ceiling
        cand_lev = learned_parameters.get("max_leverage", 1)
        user_lev = user_hard_limits.get("max_leverage", 10)
        if cand_lev > user_lev:
            violations.append(f"Candidate leverage ({cand_lev}x) exceeds user hard limit ({user_lev}x).")

        approved = len(violations) == 0
        status = "APPROVED" if approved else "REJECTED"
        notes = "Passed governance validation." if approved else f"Rejected due to {len(violations)} safety violations."

        return RiskGovernanceEvaluation(
            candidate_id=candidate_id,
            approved=approved,
            status=status,
            safety_violations=violations,
            audit_notes=notes
        )
