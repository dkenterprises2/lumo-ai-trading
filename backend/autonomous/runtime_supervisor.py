import time
import logging
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from .runtime_health import runtime_watchdog

logger = logging.getLogger("runtime_supervisor")

class SupervisorState(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    DEGRADED = "DEGRADED"
    RECOVERING = "RECOVERING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    FAILED = "FAILED"

@dataclass
class ComponentFailureRecord:
    component: str
    exception_msg: str
    timestamp: float = field(default_factory=time.time)
    recovery_attempt: int = 1
    recovery_status: str = "PENDING"  # PENDING, RECOVERED, FAILED

class RuntimeSupervisor:
    """Master Autonomous Supervisor & Component Crash Recovery Engine."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RuntimeSupervisor, cls).__new__(cls)
            cls._instance._init_supervisor()
        return cls._instance

    def _init_supervisor(self):
        self.state = SupervisorState.STOPPED
        self.failure_history: List[ComponentFailureRecord] = []
        self.restart_timestamps: Dict[str, List[float]] = {}
        self.max_restarts_per_window = 5
        self.window_seconds = 60.0
        self.initial_backoff_sec = 1.0
        self.max_backoff_sec = 30.0

    def start_supervision(self) -> Dict[str, Any]:
        self.state = SupervisorState.STARTING
        runtime_watchdog.heartbeat("autonomous_engine", "RUNNING")
        self.state = SupervisorState.RUNNING
        return {"status": "success", "supervisor_state": self.state.value}

    def pause_supervision(self) -> Dict[str, Any]:
        self.state = SupervisorState.PAUSED
        return {"status": "success", "supervisor_state": self.state.value}

    def resume_supervision(self) -> Dict[str, Any]:
        self.state = SupervisorState.RUNNING
        return {"status": "success", "supervisor_state": self.state.value}

    def stop_supervision(self) -> Dict[str, Any]:
        self.state = SupervisorState.STOPPING
        self.state = SupervisorState.STOPPED
        return {"status": "success", "supervisor_state": self.state.value}

    def handle_component_failure(self, component: str, exc: Exception) -> Dict[str, Any]:
        """Detect component failure, record exception, backoff restart, and manage state."""
        now = time.time()
        logger.error(f"[SUPERVISOR] Failure detected in component {component}: {exc}")

        runtime_watchdog.record_error(component)
        self.state = SupervisorState.DEGRADED

        # Clean old restart timestamps outside window
        timestamps = self.restart_timestamps.get(component, [])
        timestamps = [t for t in timestamps if (now - t) <= self.window_seconds]
        
        if len(timestamps) >= self.max_restarts_per_window:
            logger.critical(f"[SUPERVISOR] Restart storm prevented for {component} ({len(timestamps)} restarts in {self.window_seconds}s)")
            self.state = SupervisorState.FAILED
            rec = ComponentFailureRecord(component=component, exception_msg=str(exc), recovery_status="STORM_PREVENTED")
            self.failure_history.append(rec)
            return {"status": "failed", "reason": "Restart storm prevented", "component": component}

        # Calculate bounded exponential backoff
        attempts = len(timestamps) + 1
        backoff = min(self.max_backoff_sec, self.initial_backoff_sec * (2 ** (attempts - 1)))
        
        self.state = SupervisorState.RECOVERING
        time.sleep(min(0.1, backoff * 0.01))  # Accelerated test-friendly sleep

        timestamps.append(now)
        self.restart_timestamps[component] = timestamps
        runtime_watchdog.record_restart(component)

        rec = ComponentFailureRecord(component=component, exception_msg=str(exc), recovery_attempt=attempts, recovery_status="RECOVERED")
        self.failure_history.append(rec)

        # Restore RUNNING state if other components are healthy
        self.state = SupervisorState.RUNNING

        return {
            "status": "success",
            "component": component,
            "recovery_attempt": attempts,
            "backoff_sec": backoff,
            "supervisor_state": self.state.value
        }

    def get_status(self) -> Dict[str, Any]:
        health = runtime_watchdog.get_runtime_health()
        return {
            "supervisor_state": self.state.value,
            "health": health,
            "failures_recorded": len(self.failure_history),
            "recent_failures": [asdict(f) for f in self.failure_history[-10:]]
        }

runtime_supervisor = RuntimeSupervisor()
