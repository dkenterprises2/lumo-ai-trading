import time
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class VWAPSlice:
    slice_index: int
    expected_volume_pct: float
    allocated_quantity: float
    status: str  # PENDING, EXECUTED
    executed_at: Optional[float] = None
    fill_price: Optional[float] = None

@dataclass
class VWAPJob:
    job_id: str
    symbol: str
    side: str
    total_quantity: float
    num_bins: int
    slices: List[VWAPSlice] = field(default_factory=list)
    status: str = "RUNNING"
    target_vwap: float = 0.0
    actual_vwap: float = 0.0
    vwap_deviation_bps: float = 0.0
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["slices"] = [asdict(s) for s in self.slices]
        return d

class VWAPEngine:
    """Volume-Weighted Average Price (VWAP) Intraday Volume Profile Execution Engine."""

    def create_vwap_job(
        self,
        job_id: str,
        symbol: str,
        side: str,
        total_quantity: float,
        num_bins: int = 10
    ) -> VWAPJob:
        """Create VWAP job with U-shaped intra-day volume curve profile."""
        bins = max(2, num_bins)
        x = np.linspace(-2, 2, bins)
        u_curve = (x ** 2) + 0.5
        u_weights = u_curve / np.sum(u_curve)

        slices = []
        for i, weight in enumerate(u_weights):
            alloc_qty = total_quantity * float(weight)
            slices.append(VWAPSlice(
                slice_index=i + 1,
                expected_volume_pct=round(float(weight) * 100.0, 2),
                allocated_quantity=round(alloc_qty, 6),
                status="PENDING"
            ))

        return VWAPJob(
            job_id=job_id,
            symbol=symbol,
            side=side,
            total_quantity=total_quantity,
            num_bins=bins,
            slices=slices,
            status="RUNNING"
        )
