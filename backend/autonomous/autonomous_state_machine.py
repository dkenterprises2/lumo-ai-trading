import time
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

class EngineState(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    ERROR = "ERROR"

class ExecutionState(str, Enum):
    # Operational States
    DETECTED = "DETECTED"
    VALIDATING = "VALIDATING"
    RISK_CHECK = "RISK_CHECK"
    GOVERNANCE_CHECK = "GOVERNANCE_CHECK"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    PARTIAL_FILL = "PARTIAL_FILL"
    FILLED = "FILLED"
    POSITION_OPEN = "POSITION_OPEN"
    MONITORING = "MONITORING"
    EXIT_TRIGGERED = "EXIT_TRIGGERED"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"
    COMPLETED = "COMPLETED"

    # Rejection / Failure States
    REJECTED = "REJECTED"
    STALE = "STALE"
    RISK_BLOCKED = "RISK_BLOCKED"
    GOVERNANCE_BLOCKED = "GOVERNANCE_BLOCKED"
    LIQUIDITY_BLOCKED = "LIQUIDITY_BLOCKED"
    EXCHANGE_UNHEALTHY = "EXCHANGE_UNHEALTHY"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class ExecutionStateTransition:
    execution_id: str
    previous_state: str
    new_state: str
    reason: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ExecutionStateMachine:
    """State machine governing autonomous execution transitions and recording full audit logs."""

    def __init__(self, execution_id: str, initial_state: ExecutionState = ExecutionState.DETECTED):
        self.execution_id = execution_id
        self.current_state = initial_state
        self.history: List[ExecutionStateTransition] = [
            ExecutionStateTransition(
                execution_id=execution_id,
                previous_state="NONE",
                new_state=initial_state.value,
                reason="Execution initialized"
            )
        ]

    def transition_to(self, target_state: ExecutionState, reason: str) -> ExecutionStateTransition:
        prev = self.current_state.value
        self.current_state = target_state
        transition = ExecutionStateTransition(
            execution_id=self.execution_id,
            previous_state=prev,
            new_state=target_state.value,
            reason=reason
        )
        self.history.append(transition)
        return transition

    def is_terminal(self) -> bool:
        return self.current_state in [
            ExecutionState.COMPLETED,
            ExecutionState.CLOSED,
            ExecutionState.REJECTED,
            ExecutionState.STALE,
            ExecutionState.RISK_BLOCKED,
            ExecutionState.GOVERNANCE_BLOCKED,
            ExecutionState.LIQUIDITY_BLOCKED,
            ExecutionState.EXCHANGE_UNHEALTHY,
            ExecutionState.EXECUTION_FAILED,
            ExecutionState.CANCELLED
        ]

    def get_history_dicts(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.history]
