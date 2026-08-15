import time
import uuid
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

logger = logging.getLogger("execution_job_manager")

@dataclass
class ExecutionJobSlice:
    slice_id: str
    job_id: str
    slice_index: int
    quantity: float
    status: str  # PENDING, FILLED, REJECTED, CANCELLED
    fill_price: Optional[float] = None
    filled_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ExecutionJob:
    job_id: str
    user_id: str
    symbol: str
    side: str
    algo_type: str  # TWAP, VWAP, ICEBERG, SOR, POV
    total_quantity: float
    filled_quantity: float = 0.0
    status: str = "STARTING"  # STARTING, RUNNING, COMPLETED, REJECTED, FAILED, CANCELLED
    average_fill_price: float = 0.0
    rejection_reason: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    slices: List[ExecutionJobSlice] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "side": self.side,
            "algo_type": self.algo_type,
            "total_quantity": self.total_quantity,
            "filled_quantity": self.filled_quantity,
            "status": self.status,
            "average_fill_price": self.average_fill_price,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "slices": [s.to_dict() for s in self.slices]
        }

class ExecutionJobManager:
    """Institutional OMS / EMS Algorithmic Execution Job Lifecycle Engine."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExecutionJobManager, cls).__new__(cls)
            cls._instance.jobs: Dict[str, ExecutionJob] = {}
        return cls._instance

    def create_job(
        self,
        user_id: str,
        symbol: str,
        side: str,
        algo_type: str,
        total_quantity: float,
        num_slices: int = 5,
        base_price: float = 118450.0
    ) -> ExecutionJob:
        job_id = f"JOB-{algo_type.upper()}-{uuid.uuid4().hex[:8].upper()}"

        job = ExecutionJob(
            job_id=job_id,
            user_id=str(user_id),
            symbol=symbol.upper(),
            side=side.upper(),
            algo_type=algo_type.upper(),
            total_quantity=total_quantity,
            status="STARTING",
            created_at=time.time(),
            updated_at=time.time()
        )

        # Build Slices
        slice_qty = round(total_quantity / num_slices, 4)
        for i in range(num_slices):
            s_id = f"{job_id}-S{i+1}"
            job.slices.append(ExecutionJobSlice(
                slice_id=s_id,
                job_id=job_id,
                slice_index=i + 1,
                quantity=slice_qty,
                status="PENDING"
            ))

        # Risk & Governance Validation Check
        if total_quantity <= 0:
            job.status = "REJECTED"
            job.rejection_reason = "Invalid quantity specified (must be > 0)."
            self.jobs[job_id] = job
            return job

        # Set job to RUNNING and simulate initial shadow execution slices
        job.status = "RUNNING"
        filled_qty = 0.0
        total_value = 0.0

        for idx, sl in enumerate(job.slices):
            sl.status = "FILLED"
            # Introduce realistic 0.01% fill price deviation per slice
            fill_p = base_price * (1.0 + (0.0001 * (idx - 1)))
            sl.fill_price = round(fill_p, 2)
            sl.filled_at = time.time()
            filled_qty += sl.quantity
            total_value += sl.quantity * sl.fill_price

        job.filled_quantity = round(filled_qty, 4)
        job.average_fill_price = round(total_value / max(1e-9, filled_qty), 2)
        job.status = "COMPLETED"
        job.updated_at = time.time()

        self.jobs[job_id] = job
        return job

    def list_jobs(self, user_id: Optional[str] = None, status: Optional[str] = None) -> List[ExecutionJob]:
        res = list(self.jobs.values())
        if user_id:
            res = [j for j in res if j.user_id == str(user_id)]
        if status:
            res = [j for j in res if j.status.upper() == status.upper()]
        return sorted(res, key=lambda j: j.created_at, reverse=True)

    def get_job(self, job_id: str) -> Optional[ExecutionJob]:
        return self.jobs.get(job_id)

    def cancel_job(self, job_id: str, reason: str = "User manual cancellation") -> ExecutionJob:
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Execution job {job_id} not found.")
        if job.status in ["COMPLETED", "REJECTED", "FAILED", "CANCELLED"]:
            return job

        job.status = "CANCELLED"
        job.rejection_reason = reason
        job.updated_at = time.time()
        for sl in job.slices:
            if sl.status == "PENDING":
                sl.status = "CANCELLED"
        return job

execution_job_manager = ExecutionJobManager()
