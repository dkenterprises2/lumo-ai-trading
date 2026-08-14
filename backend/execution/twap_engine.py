import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class TWAPSlice:
    slice_index: int
    scheduled_time: float
    quantity: float
    status: str  # PENDING, EXECUTED, SKIPPED
    fill_price: Optional[float] = None
    executed_at: Optional[float] = None

@dataclass
class TWAPJob:
    job_id: str
    symbol: str
    side: str
    total_quantity: float
    duration_seconds: int
    slice_interval_seconds: int
    num_slices: int
    slices: List[TWAPSlice] = field(default_factory=list)
    status: str = "RUNNING"  # RUNNING, PAUSED, COMPLETED, CANCELLED
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["slices"] = [asdict(s) for s in self.slices]
        return d

class TWAPEngine:
    """Time-Weighted Average Price (TWAP) Execution Slice Generator."""

    def create_twap_job(
        self,
        job_id: str,
        symbol: str,
        side: str,
        total_quantity: float,
        duration_seconds: int = 300,
        slice_interval_seconds: int = 30
    ) -> TWAPJob:
        """Generate TWAP slices over target duration."""
        dur = max(10, duration_seconds)
        interval = max(5, slice_interval_seconds)
        num_slices = max(1, dur // interval)
        slice_qty = total_quantity / num_slices

        now = time.time()
        slices = []
        for i in range(num_slices):
            slices.append(TWAPSlice(
                slice_index=i + 1,
                scheduled_time=now + (i * interval),
                quantity=round(slice_qty, 6),
                status="PENDING"
            ))

        return TWAPJob(
            job_id=job_id,
            symbol=symbol,
            side=side,
            total_quantity=total_quantity,
            duration_seconds=dur,
            slice_interval_seconds=interval,
            num_slices=num_slices,
            slices=slices,
            status="RUNNING",
            created_at=now
        )
