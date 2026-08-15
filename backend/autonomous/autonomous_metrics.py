import time
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class AutonomousMetricsSummary:
    opportunities_detected: int = 0
    approved_count: int = 0
    risk_blocked_count: int = 0
    governance_blocked_count: int = 0
    executions_started: int = 0
    active_executions: int = 0
    positions_open: int = 0
    positions_closed: int = 0
    net_shadow_pnl: float = 0.0
    average_execution_cost: float = 0.0
    last_updated: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["net_shadow_pnl"] = round(d["net_shadow_pnl"], 2)
        d["average_execution_cost"] = round(d["average_execution_cost"], 4)
        return d

class AutonomousMetricsTracker:
    """Collector for Autonomous Shadow Engine Metrics."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutonomousMetricsTracker, cls).__new__(cls)
            cls._instance._reset()
        return cls._instance

    def _reset(self):
        self.opportunities_detected = 0
        self.approved_count = 0
        self.risk_blocked_count = 0
        self.governance_blocked_count = 0
        self.executions_started = 0
        self.active_executions = 0
        self.positions_open = 0
        self.positions_closed = 0
        self.net_shadow_pnl = 0.0
        self.total_cost_usd = 0.0
        self.cost_sample_count = 0
        self.last_updated = time.time()

    def record_opportunity(self, is_approved: bool, blocked_by: str = None):
        self.opportunities_detected += 1
        if is_approved:
            self.approved_count += 1
        elif blocked_by == "RISK":
            self.risk_blocked_count += 1
        elif blocked_by == "GOVERNANCE":
            self.governance_blocked_count += 1
        self.last_updated = time.time()

    def record_execution_started(self):
        self.executions_started += 1
        self.active_executions += 1
        self.last_updated = time.time()

    def record_position_opened(self):
        self.positions_open += 1
        self.last_updated = time.time()

    def record_position_closed(self, net_pnl: float, cost_usd: float = 0.0):
        if self.active_executions > 0:
            self.active_executions -= 1
        if self.positions_open > 0:
            self.positions_open -= 1
        self.positions_closed += 1
        self.net_shadow_pnl += net_pnl
        if cost_usd > 0:
            self.total_cost_usd += cost_usd
            self.cost_sample_count += 1
        self.last_updated = time.time()

    def get_summary(self) -> AutonomousMetricsSummary:
        avg_cost = (self.total_cost_usd / self.cost_sample_count) if self.cost_sample_count > 0 else 0.0
        return AutonomousMetricsSummary(
            opportunities_detected=self.opportunities_detected,
            approved_count=self.approved_count,
            risk_blocked_count=self.risk_blocked_count,
            governance_blocked_count=self.governance_blocked_count,
            executions_started=self.executions_started,
            active_executions=self.active_executions,
            positions_open=self.positions_open,
            positions_closed=self.positions_closed,
            net_shadow_pnl=self.net_shadow_pnl,
            average_execution_cost=avg_cost,
            last_updated=self.last_updated
        )
