import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class TransitionRecord:
    transition_id: str = field(default_factory=lambda: f"TR-{uuid.uuid4().hex[:8].upper()}")
    execution_id: str = ""
    opportunity_id: str = ""
    state_from: str = ""
    state_to: str = ""
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    formatted_time: str = ""
    quote_age_ms: float = 0.0
    net_edge_pct: float = 0.0
    risk_decision: Optional[Dict[str, Any]] = None
    governance_decision: Optional[Dict[str, Any]] = None
    selected_algorithm: Optional[str] = None
    fill_quantity: float = 0.0
    fill_price: float = 0.0
    fees: float = 0.0
    slippage: float = 0.0
    realized_pnl: float = 0.0

    def __post_init__(self):
        if not self.formatted_time:
            self.formatted_time = time.strftime("%H:%M:%S", time.localtime(self.timestamp)) + f".{int((self.timestamp % 1) * 1000):03d}"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class LifecycleValidator:
    """Microsecond State Machine Transition Validator & Audit Trail Recorder."""

    def __init__(self):
        self.transitions: List[TransitionRecord] = []

    def record_transition(
        self,
        execution_id: str,
        opportunity_id: str,
        state_from: str,
        state_to: str,
        reason: str,
        quote_age_ms: float = 0.0,
        net_edge_pct: float = 0.0,
        risk_decision: Optional[Dict[str, Any]] = None,
        governance_decision: Optional[Dict[str, Any]] = None,
        selected_algorithm: Optional[str] = None,
        fill_quantity: float = 0.0,
        fill_price: float = 0.0,
        fees: float = 0.0,
        slippage: float = 0.0,
        realized_pnl: float = 0.0
    ) -> TransitionRecord:
        rec = TransitionRecord(
            execution_id=execution_id,
            opportunity_id=opportunity_id,
            state_from=state_from,
            state_to=state_to,
            reason=reason,
            timestamp=time.time(),
            quote_age_ms=quote_age_ms,
            net_edge_pct=net_edge_pct,
            risk_decision=risk_decision,
            governance_decision=governance_decision,
            selected_algorithm=selected_algorithm,
            fill_quantity=fill_quantity,
            fill_price=fill_price,
            fees=fees,
            slippage=slippage,
            realized_pnl=realized_pnl
        )
        self.transitions.append(rec)
        return rec

    def get_audit_trail(self, execution_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if execution_id:
            return [t.to_dict() for t in self.transitions if t.execution_id == execution_id]
        return [t.to_dict() for t in self.transitions]

    def verify_lifecycle_sequence(self, expected_states: List[str], execution_id: Optional[str] = None) -> bool:
        recorded = [t.state_to for t in self.transitions if not execution_id or t.execution_id == execution_id]
        for expected in expected_states:
            if expected not in recorded:
                return False
        return True
