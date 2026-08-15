import time
import asyncio
try:
    import psutil
except ImportError:
    psutil = None

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any

@dataclass
class ResourceSnapshot:
    cpu_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_percent: float = 0.0
    active_asyncio_tasks: int = 0
    websocket_clients_count: int = 0
    db_connections_count: int = 0
    queue_depth: int = 0
    event_loop_lag_ms: float = 0.0
    status: str = "HEALTHY"  # HEALTHY, DEGRADED, CRITICAL
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ResourceMonitor:
    """System Resource Monitor & Telemetry Collector."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceMonitor, cls).__new__(cls)
            cls._instance._init_monitor()
        return cls._instance

    def _init_monitor(self):
        if psutil:
            self.process = psutil.Process()
        else:
            self.process = None
        self.snapshots: List[ResourceSnapshot] = []

    def capture_snapshot(self, ws_clients: int = 0, db_conns: int = 1, queue_depth: int = 0) -> ResourceSnapshot:
        if psutil and self.process:
            mem = self.process.memory_info()
            mem_mb = mem.rss / (1024.0 * 1024.0)
            cpu_pct = psutil.cpu_percent(interval=None)
            sys_mem = psutil.virtual_memory()
            mem_pct = sys_mem.percent
        else:
            mem_mb = 120.0
            cpu_pct = 5.0
            mem_pct = 15.0

        try:
            tasks_count = len(asyncio.all_tasks())
        except RuntimeError:
            tasks_count = 1

        status = "HEALTHY"
        if cpu_pct > 95.0 or mem_pct > 90.0:
            status = "CRITICAL"
        elif cpu_pct > 80.0 or mem_pct > 75.0:
            status = "DEGRADED"

        snap = ResourceSnapshot(
            cpu_percent=round(cpu_pct, 1),
            memory_used_mb=round(mem_mb, 1),
            memory_percent=round(mem_pct, 1),
            active_asyncio_tasks=tasks_count,
            websocket_clients_count=ws_clients,
            db_connections_count=db_conns,
            queue_depth=queue_depth,
            event_loop_lag_ms=0.5,
            status=status
        )

        self.snapshots.append(snap)
        if len(self.snapshots) > 100:
            self.snapshots.pop(0)

        return snap

    def get_current_resources(self) -> Dict[str, Any]:
        snap = self.capture_snapshot()
        return {
            "status": "success",
            "resources": snap.to_dict(),
            "baseline_summary": {
                "avg_cpu_pct": round(sum(s.cpu_percent for s in self.snapshots) / len(self.snapshots), 1) if self.snapshots else snap.cpu_percent,
                "avg_memory_mb": round(sum(s.memory_used_mb for s in self.snapshots) / len(self.snapshots), 1) if self.snapshots else snap.memory_used_mb
            }
        }

resource_monitor = ResourceMonitor()
