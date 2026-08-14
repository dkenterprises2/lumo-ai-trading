import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class KillSwitchStatus:
    state: str # NORMAL, WARNING, RESTRICTED, HALTED
    is_active: bool
    trigger_reason: Optional[str] = None
    triggered_at: Optional[str] = None
    audit_events: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PortfolioKillSwitch:
    """Portfolio-Level Emergency Kill Switch."""

    def __init__(self):
        self.state = "NORMAL"
        self.trigger_reason = None
        self.triggered_at = None
        self.audit_events: List[Dict[str, Any]] = []

    @property
    def is_halted(self) -> bool:
        return self.state == "HALTED"

    def activate(self, reason: str, triggered_by: str = "SYSTEM_RISK_ENGINE") -> KillSwitchStatus:
        """Activate Kill Switch to HALTED state. Blocks all new entries."""
        self.state = "HALTED"
        self.trigger_reason = reason
        self.triggered_at = time.strftime("%Y-%m-%d %H:%M:%S")

        event = {
            "event_type": "KILL_SWITCH_ACTIVATED",
            "state": "HALTED",
            "reason": reason,
            "triggered_by": triggered_by,
            "timestamp": self.triggered_at
        }
        self.audit_events.insert(0, event)

        return self.get_status()

    def recover(self, authorized_by: str = "ADMIN_USER", notes: str = "Manual Recovery Authorized") -> KillSwitchStatus:
        """Recover Kill Switch back to NORMAL state upon explicit authorization."""
        self.state = "NORMAL"
        rec_time = time.strftime("%Y-%m-%d %H:%M:%S")

        event = {
            "event_type": "KILL_SWITCH_RECOVERED",
            "state": "NORMAL",
            "reason": notes,
            "authorized_by": authorized_by,
            "timestamp": rec_time
        }
        self.audit_events.insert(0, event)
        self.trigger_reason = None
        self.triggered_at = None

        return self.get_status()

    def evaluate_triggers(
        self,
        daily_loss_breached: bool = False,
        drawdown_breached: bool = False,
        portfolio_heat_critical: bool = False,
        calculation_error: bool = False
    ) -> KillSwitchStatus:
        """Evaluate automated circuit breaker triggers."""
        if self.state == "HALTED":
            return self.get_status()

        if calculation_error:
            self.activate("FAIL_SAFE: Risk calculation failure encountered.", triggered_by="RISK_ENGINE_FAILSAFE")
        elif daily_loss_breached:
            self.activate("CIRCUIT_BREAKER: Daily loss limit breached.", triggered_by="DAILY_LOSS_LIMIT")
        elif drawdown_breached:
            self.activate("CIRCUIT_BREAKER: Maximum drawdown threshold breached.", triggered_by="MAX_DRAWDOWN_LIMIT")
        elif portfolio_heat_critical:
            self.state = "RESTRICTED"

        return self.get_status()

    def get_status(self) -> KillSwitchStatus:
        return KillSwitchStatus(
            state=self.state,
            is_active=self.is_halted,
            trigger_reason=self.trigger_reason,
            triggered_at=self.triggered_at,
            audit_events=list(self.audit_events[:20])
        )
