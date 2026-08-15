import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Set

from backend.safety.paper_mode_guard import paper_guard
from backend.shadow_trading.shadow_safety_guard import shadow_guard

@dataclass
class AutonomousGovernanceCheckResult:
    is_allowed: bool
    status: str
    reason: str
    idempotency_key: str
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AutonomousGovernanceEngine:
    """Governance & Idempotency Protection for Autonomous Trading Engine."""

    def __init__(self):
        self._processed_idempotency_keys: Set[str] = set()

    def generate_idempotency_key(self, symbol: str, buy_ex: str, sell_ex: str, buy_price: float, sell_price: float) -> str:
        # Minute-window rounded price bucket to guarantee idempotency across scanner ticks
        time_bucket = int(time.time() // 30)
        return f"OPP-{symbol.upper()}-{buy_ex.upper()}-{sell_ex.upper()}-{round(buy_price, 1)}-{round(sell_price, 1)}-{time_bucket}"

    def validate_opportunity_governance(
        self,
        symbol: str,
        buy_exchange: str,
        sell_exchange: str,
        buy_price: float,
        sell_price: float,
        kill_switch_halted: bool = False
    ) -> AutonomousGovernanceCheckResult:
        now = time.time()
        key = self.generate_idempotency_key(symbol, buy_exchange, sell_exchange, buy_price, sell_price)

        # 1. Paper & Shadow Mode Enforcement
        if not paper_guard.paper_mode or not shadow_guard.shadow_mode:
            return AutonomousGovernanceCheckResult(
                is_allowed=False,
                status="GOVERNANCE_BLOCKED",
                reason="System must be in PAPER and SHADOW trading mode for autonomous execution",
                idempotency_key=key,
                timestamp=now
            )

        # 2. Kill Switch Check
        if kill_switch_halted:
            return AutonomousGovernanceCheckResult(
                is_allowed=False,
                status="GOVERNANCE_BLOCKED",
                reason="Portfolio Kill-Switch is HALTED. Autonomous execution blocked.",
                idempotency_key=key,
                timestamp=now
            )

        # 3. Idempotency Key & Duplicate Check
        if key in self._processed_idempotency_keys:
            return AutonomousGovernanceCheckResult(
                is_allowed=False,
                status="GOVERNANCE_BLOCKED",
                reason=f"Duplicate execution blocked by idempotency key: {key}",
                idempotency_key=key,
                timestamp=now
            )

        # Mark key as processed
        self._processed_idempotency_keys.add(key)

        return AutonomousGovernanceCheckResult(
            is_allowed=True,
            status="APPROVED",
            reason="Autonomous governance & idempotency checks passed",
            idempotency_key=key,
            timestamp=now
        )

    def clear_keys(self):
        self._processed_idempotency_keys.clear()
