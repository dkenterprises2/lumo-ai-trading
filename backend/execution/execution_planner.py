import time
import uuid
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

logger = logging.getLogger("execution_planner")

SUPPORTED_ALGORITHMS = {"DIRECT", "TWAP", "VWAP", "ICEBERG"}
SUPPORTED_SIDES = {"BUY", "SELL", "LONG", "SHORT"}
MAX_CONCURRENT_POSITIONS_LIMIT = 50
MAX_SPOT_THROUGHPUT_PER_SEC = 15
MIN_ARBITRAGE_SCAN_INTERVAL_SEC = 1.0

@dataclass
class ExecutionPlan:
    plan_id: str = field(default_factory=lambda: f"PLAN-{uuid.uuid4().hex[:8].upper()}")
    order_id: str = ""
    symbol: str = "BTC/USDT"
    side: str = "BUY"
    quantity: float = 0.0
    selected_algorithm: str = "DIRECT"  # DIRECT, TWAP, VWAP, ICEBERG
    reason: str = ""
    confidence: float = 1.0
    expected_slippage_bps: float = 2.5
    max_allowed_slippage_bps: float = 50.0
    participation_rate_pct: float = 10.0
    duration_seconds: int = 0
    slice_count: int = 1
    slice_interval_seconds: int = 0
    urgency: str = "NORMAL"  # LOW, NORMAL, HIGH, CRITICAL
    risk_constraints: Dict[str, Any] = field(default_factory=dict)
    execution_mode: str = "PAPER"  # PAPER or SHADOW ONLY. LIVE = BLOCKED.
    status: str = "ACTIVE"  # ACTIVE, EXECUTING, COMPLETED, REJECTED
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AutonomousExecutionPlanner:
    """Master Deterministic Execution Planner & Algorithm Selector for Phase 44.2."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutonomousExecutionPlanner, cls).__new__(cls)
            cls._instance._init_planner()
        return cls._instance

    def _init_planner(self):
        self.active_plans: Dict[str, ExecutionPlan] = {}
        self.plan_history: List[ExecutionPlan] = []
        self.order_plan_map: Dict[str, str] = {}  # order_id -> plan_id (Idempotency)
        self.user_spot_timestamps: Dict[str, List[float]] = {}  # user_id -> rolling 1s timestamps

    def select_algorithm(
        self,
        symbol: str,
        side: str,
        quantity: float,
        current_price: float = 50000.0,
        book_depth_usd: Optional[float] = 50000.0,
        volatility_pct: Optional[float] = 2.0,
        urgency: str = "NORMAL",
        is_arbitrage: bool = False
    ) -> tuple[str, str, int, int]:
        """
        Deterministic selection logic:
        - Arbitrage -> DIRECT (preserves multi-leg quote atomicity)
        - Small orders / High Urgency -> DIRECT
        - Large orders (>20% depth) -> ICEBERG
        - Medium orders (10-20% depth): Volatility > 4% -> VWAP, else -> TWAP
        - Insufficient Market Data -> DIRECT ("INSUFFICIENT MARKET DATA")
        """
        order_value_usd = quantity * current_price

        # 1. Arbitrage latency priority
        if is_arbitrage:
            return (
                "DIRECT",
                "DIRECT selected for arbitrage order to preserve multi-leg execution latency & quote atomicity.",
                0,
                1
            )

        # 2. Insufficient Market Data Fallback
        if book_depth_usd is None or book_depth_usd <= 0:
            return (
                "DIRECT",
                "INSUFFICIENT MARKET DATA: Defaulting to DIRECT execution mode with safety slippage cap.",
                0,
                1
            )

        depth_utilization_pct = (order_value_usd / max(1.0, book_depth_usd)) * 100.0

        # 3. Small order or High Urgency -> DIRECT
        if order_value_usd < 5000.0 or depth_utilization_pct < 5.0 or urgency.upper() in ["HIGH", "CRITICAL"]:
            return (
                "DIRECT",
                f"DIRECT selected for low impact order (${order_value_usd:,.2f} USD, {depth_utilization_pct:.1f}% depth utilization).",
                0,
                1
            )

        # 4. Large order (>20% depth) -> ICEBERG
        if depth_utilization_pct > 20.0:
            slices = max(5, int(depth_utilization_pct / 4.0))
            return (
                "ICEBERG",
                f"ICEBERG selected because order size is {depth_utilization_pct:.1f}% of displayed depth (>20% impact threshold).",
                300,
                slices
            )

        # 5. Medium order (10-20% depth) -> VWAP or TWAP
        vol = volatility_pct if volatility_pct is not None else 2.0
        if vol > 4.0:
            slices = max(4, int(depth_utilization_pct / 3.0))
            return (
                "VWAP",
                f"VWAP selected due to elevated market volatility ({vol:.1f}%) and {depth_utilization_pct:.1f}% depth utilization.",
                300,
                slices
            )
        else:
            slices = max(3, int(depth_utilization_pct / 3.0))
            return (
                "TWAP",
                f"TWAP selected for time-sliced execution ({depth_utilization_pct:.1f}% depth utilization, normal volatility {vol:.1f}%).",
                300,
                slices
            )

    def validate_plan(
        self,
        plan: ExecutionPlan,
        user_id: str = "default",
        is_arbitrage: bool = False,
        active_positions_count: int = 0
    ) -> Dict[str, Any]:
        """Strict schema & safety validation before execution plan is accepted."""
        # 1. LIVE execution hard block
        if plan.execution_mode.upper() == "LIVE":
            return {"valid": False, "reason": "LIVE DEPLOYMENT DISABLED. System operates in PAPER/SHADOW mode only."}

        if plan.execution_mode.upper() not in ["PAPER", "SHADOW"]:
            return {"valid": False, "reason": f"Invalid execution mode '{plan.execution_mode}'. Must be PAPER or SHADOW."}

        # 2. Schema validation
        if plan.quantity <= 0:
            return {"valid": False, "reason": "Quantity must be strictly positive (> 0)."}

        if plan.side.upper() not in SUPPORTED_SIDES:
            return {"valid": False, "reason": f"Unsupported order side '{plan.side}'."}

        if plan.selected_algorithm.upper() not in SUPPORTED_ALGORITHMS:
            return {"valid": False, "reason": f"Unsupported algorithm '{plan.selected_algorithm}'."}

        if plan.max_allowed_slippage_bps > 500.0:
            return {"valid": False, "reason": "Max allowed slippage exceeds 500 bps safety ceiling."}

        # 3. Position limit hard ceiling
        if active_positions_count >= MAX_CONCURRENT_POSITIONS_LIMIT:
            return {"valid": False, "reason": f"Active positions count ({active_positions_count}) reached hard limit ({MAX_CONCURRENT_POSITIONS_LIMIT})."}

        # 4. Spot order throughput limit (<= 15 orders/sec per user instance)
        if not is_arbitrage:
            now = time.time()
            if user_id not in self.user_spot_timestamps:
                self.user_spot_timestamps[user_id] = []
            # Prune timestamps older than 1.0 second
            self.user_spot_timestamps[user_id] = [t for t in self.user_spot_timestamps[user_id] if (now - t) <= 1.0]
            if len(self.user_spot_timestamps[user_id]) >= MAX_SPOT_THROUGHPUT_PER_SEC:
                return {
                    "valid": False,
                    "reason": f"Spot order throughput limit ({MAX_SPOT_THROUGHPUT_PER_SEC} orders/sec) exceeded for user '{user_id}'."
                }
            self.user_spot_timestamps[user_id].append(now)

        return {"valid": True, "reason": "Plan validation passed."}

    def plan_order_execution(
        self,
        order_id: str,
        user_id: str = "default",
        symbol: str = "BTC/USDT",
        side: str = "BUY",
        quantity: float = 0.0,
        current_price: float = 50000.0,
        book_depth_usd: Optional[float] = 50000.0,
        volatility_pct: Optional[float] = 2.0,
        urgency: str = "NORMAL",
        is_arbitrage: bool = False,
        execution_mode: str = "PAPER",
        active_positions_count: int = 0
    ) -> ExecutionPlan:
        """Single entrypoint for generating & validating an execution plan."""
        # Idempotency check: Return existing plan if order_id already planned
        if order_id in self.order_plan_map:
            plan_id = self.order_plan_map[order_id]
            if plan_id in self.active_plans:
                logger.info(f"[PLANNER_IDEMPOTENCY] Order ID {order_id} already planned (PlanID: {plan_id})")
                return self.active_plans[plan_id]

        algo, reason, duration, slices = self.select_algorithm(
            symbol=symbol,
            side=side,
            quantity=quantity,
            current_price=current_price,
            book_depth_usd=book_depth_usd,
            volatility_pct=volatility_pct,
            urgency=urgency,
            is_arbitrage=is_arbitrage
        )

        interval = duration // slices if slices > 0 else 0

        plan = ExecutionPlan(
            order_id=order_id,
            symbol=symbol,
            side=side.upper(),
            quantity=quantity,
            selected_algorithm=algo,
            reason=reason,
            confidence=0.98 if algo != "DIRECT" else 1.0,
            expected_slippage_bps=2.5 if algo == "DIRECT" else 1.2,
            max_allowed_slippage_bps=50.0,
            participation_rate_pct=15.0 if algo in ["TWAP", "VWAP"] else 100.0,
            duration_seconds=duration,
            slice_count=slices,
            slice_interval_seconds=interval,
            urgency=urgency.upper(),
            risk_constraints={
                "max_positions": MAX_CONCURRENT_POSITIONS_LIMIT,
                "spot_max_throughput_per_sec": MAX_SPOT_THROUGHPUT_PER_SEC,
                "arbitrage_min_interval_sec": MIN_ARBITRAGE_SCAN_INTERVAL_SEC
            },
            execution_mode=execution_mode.upper(),
            status="ACTIVE"
        )

        # Validate plan
        validation = self.validate_plan(
            plan,
            user_id=user_id,
            is_arbitrage=is_arbitrage,
            active_positions_count=active_positions_count
        )
        if not validation["valid"]:
            plan.status = "REJECTED"
            plan.reason = f"REJECTED: {validation['reason']} (Original: {reason})"
            logger.warning(f"[PLANNER_REJECTED] Plan {plan.plan_id} for Order {order_id} rejected: {validation['reason']}")

        # Register plan & idempotency map
        self.active_plans[plan.plan_id] = plan
        self.order_plan_map[order_id] = plan.plan_id
        self.plan_history.append(plan)

        logger.info(f"[PLANNER_CREATED] Execution Plan {plan.plan_id} created for Order {order_id} ({algo} | Slices={slices} | Mode={execution_mode})")
        return plan

    def get_active_plans(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.active_plans.values()]

execution_planner = AutonomousExecutionPlanner()
