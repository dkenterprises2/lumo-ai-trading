import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class SubsystemHeartbeat:
    component: str
    status: str = "RUNNING"  # RUNNING, HEALTHY, DEGRADED, DISCONNECTED, STOPPED, FAILED
    last_heartbeat: float = field(default_factory=time.time)
    age_ms: float = 0.0
    restart_count: int = 0
    error_count: int = 0

    def update(self, status: Optional[str] = None):
        self.last_heartbeat = time.time()
        self.age_ms = 0.0
        if status:
            self.status = status

    def record_error(self):
        self.error_count += 1
        self.status = "DEGRADED"

    def record_restart(self):
        self.restart_count += 1
        self.status = "RUNNING"
        self.last_heartbeat = time.time()
        self.age_ms = 0.0

    def to_dict(self) -> Dict[str, Any]:
        now = time.time()
        self.age_ms = round((now - self.last_heartbeat) * 1000.0, 1)
        return asdict(self)

class RuntimeHealthWatchdog:
    """Master Watchdog & Subsystem Heartbeat Aggregator."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RuntimeHealthWatchdog, cls).__new__(cls)
            cls._instance._init_watchdog()
        return cls._instance

    def _init_watchdog(self):
        self.subsystems: Dict[str, SubsystemHeartbeat] = {
            "autonomous_engine": SubsystemHeartbeat(component="autonomous_engine", status="RUNNING"),
            "scanner_loop": SubsystemHeartbeat(component="scanner_loop", status="RUNNING"),
            "market_data_loop": SubsystemHeartbeat(component="market_data_loop", status="RUNNING"),
            "execution_loop": SubsystemHeartbeat(component="execution_loop", status="RUNNING"),
            "position_monitor": SubsystemHeartbeat(component="position_monitor", status="RUNNING"),
            "exit_monitor": SubsystemHeartbeat(component="exit_monitor", status="RUNNING"),
            "websocket": SubsystemHeartbeat(component="websocket", status="CONNECTED"),
            "database": SubsystemHeartbeat(component="database", status="HEALTHY"),
            "risk_engine": SubsystemHeartbeat(component="risk_engine", status="HEALTHY"),
            "governance_engine": SubsystemHeartbeat(component="governance_engine", status="HEALTHY"),
            "news_intelligence": SubsystemHeartbeat(component="news_intelligence", status="HEALTHY"),
            "arbitrage_engine": SubsystemHeartbeat(component="arbitrage_engine", status="HEALTHY"),
        }

    def heartbeat(self, component: str, status: Optional[str] = None):
        if component not in self.subsystems:
            self.subsystems[component] = SubsystemHeartbeat(component=component)
        self.subsystems[component].update(status)

    def record_error(self, component: str):
        if component in self.subsystems:
            self.subsystems[component].record_error()

    def record_restart(self, component: str):
        if component in self.subsystems:
            self.subsystems[component].record_restart()

    def heartbeat_all(self, status: Optional[str] = None):
        """Touch and refresh heartbeats for all registered subsystems."""
        for comp in list(self.subsystems.keys()):
            st = status if status else ("CONNECTED" if comp == "websocket" else ("HEALTHY" if comp in ["database", "risk_engine", "governance_engine", "news_intelligence", "arbitrage_engine"] else "RUNNING"))
            self.subsystems[comp].update(st)

    def get_runtime_health(self) -> Dict[str, Any]:
        now = time.time()
        health_map = {}
        for comp, hb in self.subsystems.items():
            h_dict = hb.to_dict()
            # If heartbeat age > 10000ms, mark DEGRADED
            if h_dict["age_ms"] > 10000.0 and h_dict["status"] in ["RUNNING", "HEALTHY", "CONNECTED"]:
                h_dict["status"] = "DEGRADED"
            health_map[comp] = h_dict["status"]

        is_all_healthy = all(s in ["RUNNING", "HEALTHY", "CONNECTED"] for s in health_map.values())

        return {
            "status": "healthy" if is_all_healthy else "degraded",
            "overall": "RUNNING" if is_all_healthy else "DEGRADED",
            "components": health_map,
            "subsystems_detail": {c: hb.to_dict() for c, hb in self.subsystems.items()},
            "timestamp": now
        }

runtime_watchdog = RuntimeHealthWatchdog()
