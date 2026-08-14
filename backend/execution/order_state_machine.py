import time
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

class OrderState(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    ROUTING = "ROUTING"
    SUBMITTED = "SUBMITTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"

class InvalidStateTransitionError(Exception):
    """Raised when an illegal order state transition is attempted."""
    pass

@dataclass
class StateAuditEvent:
    order_id: str
    old_state: str
    new_state: str
    actor: str
    reason: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class OrderStateMachine:
    """Deterministic Order Lifecycle State Machine."""

    VALID_TRANSITIONS = {
        OrderState.DRAFT: [OrderState.VALIDATED, OrderState.REJECTED, OrderState.CANCELLED],
        OrderState.VALIDATED: [OrderState.ROUTING, OrderState.REJECTED, OrderState.CANCELLED],
        OrderState.ROUTING: [OrderState.SUBMITTED, OrderState.FAILED, OrderState.REJECTED, OrderState.CANCELLED],
        OrderState.SUBMITTED: [OrderState.PARTIALLY_FILLED, OrderState.FILLED, OrderState.FAILED, OrderState.CANCELLED, OrderState.EXPIRED],
        OrderState.PARTIALLY_FILLED: [OrderState.PARTIALLY_FILLED, OrderState.FILLED, OrderState.CANCELLED, OrderState.FAILED, OrderState.EXPIRED],
        OrderState.FILLED: [],      # Terminal
        OrderState.REJECTED: [],    # Terminal
        OrderState.CANCELLED: [],   # Terminal
        OrderState.EXPIRED: [],     # Terminal
        OrderState.FAILED: []       # Terminal
    }

    def __init__(self, order_id: str, initial_state: OrderState = OrderState.DRAFT):
        self.order_id = order_id
        self.current_state = initial_state
        self.audit_log: List[StateAuditEvent] = []

    def transition_to(self, new_state: OrderState, actor: str = "OMS_ENGINE", reason: str = "State Transition", metadata: Optional[Dict[str, Any]] = None) -> OrderState:
        """Execute state transition with strict validation and audit logging."""
        if new_state not in self.VALID_TRANSITIONS.get(self.current_state, []):
            raise InvalidStateTransitionError(
                f"Illegal state transition for order {self.order_id}: cannot transition from {self.current_state.value} to {new_state.value}"
            )

        old_state = self.current_state
        self.current_state = new_state
        event = StateAuditEvent(
            order_id=self.order_id,
            old_state=old_state.value,
            new_state=new_state.value,
            actor=actor,
            reason=reason,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.audit_log.append(event)
        return self.current_state
