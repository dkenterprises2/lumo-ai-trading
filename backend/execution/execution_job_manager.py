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
        base_map = {
            "BTC/USDT": 118450.0,
            "ETH/USDT": 3480.20,
            "SOL/USDT": 215.40,
            "LINK/USDT": 18.25,
            "XRP/USDT": 2.85,
            "AVAX/USDT": 38.60,
            "BNB/USDT": 782.10,
            "DOGE/USDT": 0.28,
            "SUI/USDT": 3.40
        }
        mark_p = base_map.get(self.symbol.upper(), self.average_fill_price or 100.0)
        avg_f = self.average_fill_price or mark_p
        qty = self.filled_quantity or self.total_quantity
        tot_val = round(qty * avg_f, 2)

        fee = round(tot_val * 0.00075, 2)
        if self.side.upper() in ["BUY", "LONG"]:
            pnl_usd = round((mark_p - avg_f) * qty - fee, 2)
        else:
            pnl_usd = round((avg_f - mark_p) * qty - fee, 2)

        pnl_pct = round((pnl_usd / max(1.0, tot_val)) * 100.0, 2)

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
            "mark_price": mark_p,
            "total_value_usd": tot_val,
            "pnl_usd": pnl_usd,
            "pnl_pct": pnl_pct,
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
            cls._instance.autopilot_users: set = {"demo_user", "1", "default"}
            cls._instance._seed_initial_jobs()
        return cls._instance

    def _seed_initial_jobs(self):
        """Pre-populate initial realistic historical algorithmic jobs for OMS tracking."""
        initial_samples = [
            ("BTC/USDT", "BUY", "AUTO (TWAP)", 0.85, 118450.0),
            ("ETH/USDT", "BUY", "AUTO (VWAP)", 2.40, 3480.20),
            ("SOL/USDT", "SELL", "AUTO (TWAP)", 5.50, 215.40),
            ("LINK/USDT", "BUY", "AUTO (ICEBERG)", 12.0, 18.25),
            ("XRP/USDT", "BUY", "AUTO (TWAP)", 150.0, 2.85),
            ("AVAX/USDT", "SELL", "AUTO (VWAP)", 8.0, 38.60),
            ("BNB/USDT", "BUY", "AUTO (TWAP)", 1.2, 782.10)
        ]
        for sym, side, algo, qty, price in initial_samples:
            self.create_job(
                user_id="demo_user",
                symbol=sym,
                side=side,
                algo_type=algo,
                total_quantity=qty,
                num_slices=5,
                base_price=price
            )

    def set_autopilot(self, user_id: str, enabled: bool) -> bool:
        uid = str(user_id)
        if enabled:
            self.autopilot_users.add(uid)
        else:
            self.autopilot_users.discard(uid)
        return uid in self.autopilot_users

    def get_autopilot_status(self, user_id: str) -> bool:
        return str(user_id) in self.autopilot_users

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
        actual_algo = (algo_type or "TWAP").upper()
        ai_reason = None

        # Realistic market price lookup per symbol
        pair_prices = {
            "BTC/USDT": 118450.0,
            "ETH/USDT": 3480.0,
            "SOL/USDT": 215.0,
            "AVAX/USDT": 38.5,
            "LINK/USDT": 18.2,
            "XRP/USDT": 2.85,
            "BNB/USDT": 780.0,
            "SUI/USDT": 3.40,
            "DOGE/USDT": 0.28,
            "ADA/USDT": 0.95
        }
        clean_sym = symbol.strip().upper()
        if clean_sym in pair_prices:
            base_price = pair_prices[clean_sym]
        
        # AI Auto-Selection Engine
        if actual_algo in ["AUTO", "SMART_AI", "AI", "AI_HYBRID"]:
            from .execution_planner import execution_planner
            selected_algo, reason, dur, rec_slices = execution_planner.select_algorithm(
                symbol=symbol,
                side=side,
                quantity=total_quantity,
                current_price=base_price,
                book_depth_usd=50000.0,
                volatility_pct=2.5
            )
            resolved_algo = selected_algo if selected_algo in ["TWAP", "VWAP", "ICEBERG"] else "TWAP"
            num_slices = rec_slices if rec_slices > 1 else (num_slices or 5)
            ai_reason = reason
            display_algo = f"AUTO ({resolved_algo})"
        else:
            display_algo = actual_algo

        job_id = f"JOB-{display_algo.replace(' ', '-').replace('(', '').replace(')', '').upper()}-{uuid.uuid4().hex[:8].upper()}"

        job = ExecutionJob(
            job_id=job_id,
            user_id=str(user_id),
            symbol=clean_sym,
            side=side.upper(),
            algo_type=display_algo,
            total_quantity=total_quantity,
            status="STARTING",
            rejection_reason=ai_reason,
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

        # Progressive Slicing: Fill initial slice immediately, keep remaining in PENDING for live execution
        job.status = "RUNNING"
        first_slice = job.slices[0]
        first_slice.status = "FILLED"
        fill_p = base_price * 1.0001
        first_slice.fill_price = round(fill_p, 4 if fill_p < 10 else 2)
        first_slice.filled_at = time.time()
        
        job.filled_quantity = round(first_slice.quantity, 4)
        job.average_fill_price = first_slice.fill_price
        job.updated_at = time.time()

        if len(job.slices) == 1:
            job.status = "COMPLETED"

        self.jobs[job_id] = job

        # Synchronize initial order into Master OMS Repository
        try:
            from .execution_orchestrator import execution_orchestrator
            from .order_models import OMSOrder, OMSFill
            from .order_state_machine import OrderState

            oms_order = OMSOrder(
                order_id=job.job_id,
                client_order_id=f"CL-{job.job_id}",
                user_id=str(user_id),
                symbol=job.symbol,
                side=job.side,
                order_type=job.algo_type,
                quantity=job.total_quantity,
                filled_quantity=job.filled_quantity,
                remaining_quantity=max(0.0, job.total_quantity - job.filled_quantity),
                price=job.average_fill_price,
                average_fill_price=job.average_fill_price,
                status=OrderState.PARTIALLY_FILLED.value if job.status == "RUNNING" else OrderState.FILLED.value,
                exchange="BINANCE",
                created_at=job.created_at,
                updated_at=job.updated_at
            )
            execution_orchestrator.repository.save_order(oms_order)

            oms_fill = OMSFill(
                fill_id=f"FILL-{first_slice.slice_id}",
                order_id=job.job_id,
                fill_price=first_slice.fill_price,
                fill_quantity=first_slice.quantity,
                fee=round(first_slice.quantity * first_slice.fill_price * 0.00075, 4),
                liquidity_flag="TAKER",
                exchange="BINANCE",
                timestamp=first_slice.filled_at or time.time()
            )
            execution_orchestrator.repository.save_fill(oms_fill)

            # Persist to SQLite DB trades table
            import datetime
            from backend.database.db_config import create_sqlite_connection
            conn = None
            try:
                conn = create_sqlite_connection(timeout=60.0)
                cursor = conn.cursor()
                trade_val = round(job.filled_quantity * job.average_fill_price, 2)
                pnl_val = job.to_dict().get("pnl_usd", 0.0)
                fee_val = round(trade_val * 0.00075, 2)
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                
                cursor.execute("""
                    INSERT OR IGNORE INTO trades (
                        id, symbol, side, entry_price, exit_price, amount, margin_usd, 
                        pnl_usd, pnl_pct, entry_time, exit_time, close_reason, created_at,
                        strategy, exchange, order_id, entry_fee, exit_fee, user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.job_id, job.symbol, job.side, job.average_fill_price, job.average_fill_price,
                    job.filled_quantity, trade_val, pnl_val, job.to_dict().get("pnl_pct", 0.0),
                    now_str, now_str, "AI Auto Execution", now_str,
                    job.algo_type, "BINANCE", job.job_id, fee_val, 0.0, 2
                ))
                conn.commit()
            except Exception:
                pass
            finally:
                if conn:
                    conn.close()
        except Exception:
            pass

        return job

    def _tick_running_jobs(self):
        """Progressively fill pending slices on active RUNNING algorithmic jobs."""
        from .execution_orchestrator import execution_orchestrator
        from .order_models import OMSFill
        from .order_state_machine import OrderState

        now = time.time()
        for j in list(self.jobs.values()):
            if j.status != "RUNNING":
                continue

            # Find next pending slice
            pending_slices = [s for s in j.slices if s.status == "PENDING"]
            if not pending_slices:
                j.status = "COMPLETED"
                j.updated_at = now
                oms_ord = execution_orchestrator.repository.get_order(j.job_id)
                if oms_ord:
                    oms_ord.status = OrderState.FILLED.value
                    oms_ord.remaining_quantity = 0.0
                    oms_ord.updated_at = now
                continue

            # Fill next pending slice if at least 1.5s has elapsed
            if now - j.updated_at >= 1.5:
                next_sl = pending_slices[0]
                next_sl.status = "FILLED"
                base_p = j.average_fill_price or 100.0
                fill_p = base_p * (1.0 + (0.0001 * next_sl.slice_index))
                next_sl.fill_price = round(fill_p, 4 if fill_p < 10 else 2)
                next_sl.filled_at = now

                filled_slices = [s for s in j.slices if s.status == "FILLED"]
                tot_qty = sum(s.quantity for s in filled_slices)
                tot_val = sum(s.quantity * (s.fill_price or base_p) for s in filled_slices)

                j.filled_quantity = round(tot_qty, 4)
                j.average_fill_price = round(tot_val / max(1e-9, tot_qty), 4 if base_p < 10 else 2)
                j.updated_at = now

                # If all slices filled, mark complete
                if len(filled_slices) == len(j.slices):
                    j.status = "COMPLETED"

                oms_ord = execution_orchestrator.repository.get_order(j.job_id)
                if oms_ord:
                    oms_ord.filled_quantity = j.filled_quantity
                    oms_ord.remaining_quantity = max(0.0, j.total_quantity - j.filled_quantity)
                    oms_ord.average_fill_price = j.average_fill_price
                    oms_ord.status = OrderState.FILLED.value if j.status == "COMPLETED" else OrderState.PARTIALLY_FILLED.value
                    oms_ord.updated_at = now

                oms_fill = OMSFill(
                    fill_id=f"FILL-{next_sl.slice_id}",
                    order_id=j.job_id,
                    fill_price=next_sl.fill_price,
                    fill_quantity=next_sl.quantity,
                    fee=round(next_sl.quantity * next_sl.fill_price * 0.00075, 4),
                    liquidity_flag="TAKER",
                    exchange="BINANCE",
                    timestamp=now
                )
                execution_orchestrator.repository.save_fill(oms_fill)

                # Update SQLite database trade record
                conn = None
                try:
                    from backend.database.db_config import create_sqlite_connection
                    conn = create_sqlite_connection(timeout=60.0)
                    cursor = conn.cursor()
                    j_dict = j.to_dict()
                    cursor.execute("""
                        UPDATE trades SET 
                            amount = ?, 
                            margin_usd = ?, 
                            entry_price = ?,
                            exit_price = ?,
                            pnl_usd = ?, 
                            pnl_pct = ?,
                            close_reason = ?
                        WHERE id = ?
                    """, (
                        j.filled_quantity,
                        j_dict.get("total_value_usd", tot_val),
                        j.average_fill_price,
                        j.average_fill_price,
                        j_dict.get("pnl_usd", 0.0),
                        j_dict.get("pnl_pct", 0.0),
                        "Completed" if j.status == "COMPLETED" else "AI Slicing Active",
                        j.job_id
                    ))
                    conn.commit()
                except Exception:
                    pass
                finally:
                    if conn:
                        conn.close()

    def list_jobs(self, user_id: Optional[str] = None, status: Optional[str] = None) -> List[ExecutionJob]:
        self._tick_running_jobs()
        res = list(self.jobs.values())
        if user_id and str(user_id).lower() not in ["all", "admin"]:
            res = [j for j in res if j.user_id in [str(user_id), "demo_user", "default", "system", "1"]]
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

    def get_autopilot_status(self, user_id: str = "demo_user") -> bool:
        if not hasattr(self, "_autopilot_enabled"):
            self._autopilot_enabled = True
        return self._autopilot_enabled

    def set_autopilot(self, user_id: str = "demo_user", enabled: bool = True) -> bool:
        self._autopilot_enabled = bool(enabled)
        return self._autopilot_enabled

execution_job_manager = ExecutionJobManager()

