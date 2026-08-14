from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class ArbitrageGovernanceResult:
    is_approved: bool
    status: str
    reasons: list

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ArbitrageGovernance:
    """Approval Workflow & Lifecycle Governance for Arbitrage Sessions."""

    def validate_session(
        self,
        portfolio_heat_pct: float = 20.0,
        kill_switch_state: str = "NORMAL"
    ) -> ArbitrageGovernanceResult:
        reasons = []
        is_ok = True

        if kill_switch_state != "NORMAL":
            is_ok = False
            reasons.append(f"Kill switch is in {kill_switch_state} state")

        if portfolio_heat_pct >= 70.0:
            is_ok = False
            reasons.append(f"Portfolio heat utilization ({portfolio_heat_pct}%) >= 70%")

        return ArbitrageGovernanceResult(
            is_approved=is_ok,
            status="ARBITRAGE_APPROVED" if is_ok else "ARBITRAGE_HALTED",
            reasons=reasons
        )
