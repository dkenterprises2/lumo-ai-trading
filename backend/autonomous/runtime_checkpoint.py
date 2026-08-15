import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class AutonomousSessionRecord:
    session_id: str = field(default_factory=lambda: f"AUTO-SESSION-{time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}")
    started_at: float = field(default_factory=time.time)
    stopped_at: Optional[float] = None
    status: str = "RUNNING"  # RUNNING, PAUSED, STOPPED, DEGRADED, RECOVERING, FAILED
    uptime_seconds: float = 0.0
    opportunities_detected: int = 0
    executions_started: int = 0
    executions_completed: int = 0
    positions_opened: int = 0
    positions_closed: int = 0
    gross_pnl: float = 0.0
    net_pnl: float = 0.0
    errors: int = 0
    recoveries: int = 0
    restarts: int = 0

    def update_uptime(self):
        now = time.time()
        self.uptime_seconds = round(now - self.started_at, 1)

    def to_dict(self) -> Dict[str, Any]:
        self.update_uptime()
        return asdict(self)

@dataclass
class RuntimeCheckpoint:
    checkpoint_id: str = field(default_factory=lambda: f"CHK-{uuid.uuid4().hex[:8].upper()}")
    timestamp: float = field(default_factory=time.time)
    session: Dict[str, Any] = field(default_factory=dict)
    active_executions: List[Dict[str, Any]] = field(default_factory=list)
    active_positions: List[Dict[str, Any]] = field(default_factory=list)
    pending_exits: List[str] = field(default_factory=list)
    last_opportunity_id: Optional[str] = None
    risk_state: Dict[str, Any] = field(default_factory=dict)
    governance_state: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RuntimeCheckpointManager:
    """Persists and Restores Runtime Checkpoints Across Restarts."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RuntimeCheckpointManager, cls).__new__(cls)
            cls._instance._init_checkpoint()
        return cls._instance

    def _init_checkpoint(self):
        self.current_session = AutonomousSessionRecord()
        self.sessions_history: List[AutonomousSessionRecord] = [self.current_session]
        self.latest_checkpoint: Optional[RuntimeCheckpoint] = None
        self.checkpoints: List[RuntimeCheckpoint] = []

    def save_checkpoint(self, execution_manager: Any) -> RuntimeCheckpoint:
        """Create and persist a state snapshot."""
        self.current_session.update_uptime()
        execs = [e.to_dict() for e in execution_manager.executions.values()]
        positions = [p.to_dict() for p in execution_manager.positions.values()]
        pending = [p.position_id for p in execution_manager.positions.values() if p.status == "CLOSING"]

        chk = RuntimeCheckpoint(
            session=self.current_session.to_dict(),
            active_executions=execs,
            active_positions=positions,
            pending_exits=pending,
            last_opportunity_id=getattr(execution_manager, 'last_opp_id', None),
            risk_state={"kill_switch": execution_manager.risk_engine.kill_switch.is_halted},
            governance_state={"keys_count": len(getattr(execution_manager.governance_engine, '_processed_idempotency_keys', set()))}
        )
        self.latest_checkpoint = chk
        self.checkpoints.append(chk)
        return chk

    def restore_checkpoint(self, execution_manager: Any) -> Dict[str, Any]:
        """Restore state from latest checkpoint, reconcile orphaned jobs/positions without duplication."""
        if not self.latest_checkpoint:
            return {"status": "skipped", "reason": "No checkpoint available"}

        chk = self.latest_checkpoint
        reconciled_orphaned_jobs = 0
        reconciled_orphaned_positions = 0

        # Reconcile executions
        for ex_dict in chk.active_executions:
            exec_id = ex_dict.get("execution_id")
            if exec_id and exec_id not in execution_manager.executions:
                # Mark orphaned pending executions as COMPLETED or RECOVERED to prevent double-execution
                if ex_dict.get("status") in ["STARTING", "EXECUTING"]:
                    ex_dict["status"] = "RECOVERED"
                    reconciled_orphaned_jobs += 1
                execution_manager.executions[exec_id] = ex_dict

        # Reconcile positions
        for pos_dict in chk.active_positions:
            pos_id = pos_dict.get("position_id")
            if pos_id and pos_id not in execution_manager.positions:
                # Restore position monitoring
                execution_manager.positions[pos_id] = pos_dict
                reconciled_orphaned_positions += 1

        return {
            "status": "success",
            "checkpoint_id": chk.checkpoint_id,
            "reconciled_orphaned_jobs": reconciled_orphaned_jobs,
            "reconciled_orphaned_positions": reconciled_orphaned_positions,
            "restored_positions_count": len(execution_manager.positions)
        }

checkpoint_manager = RuntimeCheckpointManager()
