from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from backend.auth.security import get_optional_current_user
from backend.models.domain import UserModel
from backend.execution import execution_orchestrator

router = APIRouter(prefix="/api/execution", tags=["Institutional OMS / EMS Execution Phase 35"])

class CreateOrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: Optional[str] = "MARKET"
    price: Optional[float] = None
    exchange: Optional[str] = None

class TWAPAlgorithmRequest(BaseModel):
    symbol: str
    side: str
    total_quantity: float
    duration_seconds: Optional[int] = 300
    slice_interval_seconds: Optional[int] = 30

class VWAPAlgorithmRequest(BaseModel):
    symbol: str
    side: str
    total_quantity: float
    num_bins: Optional[int] = 10

class IcebergAlgorithmRequest(BaseModel):
    symbol: str
    side: str
    total_quantity: float
    display_quantity_pct: Optional[float] = 10.0

@router.get("/orders")
async def get_execution_orders(status: Optional[str] = None, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch order blotter for current authenticated user."""
    user_id = str(current_user.id) if current_user else "demo_user"
    orders = execution_orchestrator.repository.list_orders(user_id=user_id, status=status)
    return [o.to_dict() for o in orders]

@router.get("/orders/{order_id}")
async def get_execution_order_by_id(order_id: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch order details by order_id."""
    order = execution_orchestrator.repository.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")
    return order.to_dict()

@router.post("/orders")
async def create_execution_order(body: CreateOrderRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Submit new order through Phase 35 OMS/EMS Single Gateway."""
    user_id = str(current_user.id) if current_user else "demo_user"
    res = execution_orchestrator.submit_order(
        user_id=user_id,
        symbol=body.symbol,
        side=body.side,
        quantity=body.quantity,
        order_type=body.order_type or "MARKET",
        price=body.price,
        exchange=body.exchange
    )
    return res

@router.post("/orders/{order_id}/cancel")
async def cancel_execution_order(order_id: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Cancel order by order_id."""
    res = execution_orchestrator.cancel_order(order_id, reason="User API cancellation")
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.get("/fills")
async def get_execution_fills(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch fill history."""
    fills = execution_orchestrator.repository.get_all_fills()
    return [f.to_dict() for f in fills]

@router.get("/telemetry")
async def get_execution_telemetry(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch current execution telemetry snapshot."""
    user_id = str(current_user.id) if current_user else "demo_user"
    orders = execution_orchestrator.repository.list_orders(user_id=user_id)
    active_count = sum(1 for o in orders if o.status not in ["FILLED", "CANCELLED", "REJECTED"])
    filled_today = sum(1 for o in orders if o.status == "FILLED")
    return {
        "active_orders_count": active_count,
        "filled_today_count": filled_today,
        "primary_venue": "BINANCE",
        "average_slippage_pct": 0.02,
        "status": "OPERATIONAL"
    }

@router.get("/costs")
async def get_execution_costs(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch execution cost analytics."""
    user_id = str(current_user.id) if current_user else "demo_user"
    orders = execution_orchestrator.repository.list_orders(user_id=user_id, status="FILLED")
    total_cost = 0.0
    for o in orders:
        analysis = execution_orchestrator.cost_engine.compute_cost_analysis(
            order_id=o.order_id,
            expected_price=o.price or o.average_fill_price,
            actual_average_fill=o.average_fill_price,
            quantity=o.filled_quantity,
            side=o.side
        )
        total_cost += analysis.total_execution_cost_usd

    return {
        "total_execution_cost_usd": round(total_cost, 4),
        "average_implementation_shortfall_bps": 2.5,
        "filled_orders_analyzed": len(orders)
    }

@router.post("/simulate")
async def simulate_execution_routing(body: CreateOrderRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Simulate Smart Order Routing & Slippage Estimate before placing order."""
    venue_score = execution_orchestrator.sor.route_order(
        symbol=body.symbol,
        side=body.side,
        quantity=body.quantity,
        order_type=body.order_type or "MARKET",
        requested_exchange=body.exchange,
        price=body.price
    )
    slippage = execution_orchestrator.slippage_engine.estimate_slippage(
        symbol=body.symbol,
        side=body.side,
        quantity=body.quantity,
        price=body.price or 50000.0
    )
    return {
        "recommended_venue": venue_score.to_dict(),
        "slippage_estimate": slippage.to_dict()
    }

@router.get("/exchanges/health")
async def get_exchanges_health(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch health status across connected exchanges."""
    health_dict = execution_orchestrator.health_monitor.get_all_health()
    return {ex: v.to_dict() for ex, v in health_dict.items()}

class CreateExecutionJobRequest(BaseModel):
    symbol: str
    side: str
    algo_type: Optional[str] = "TWAP"  # TWAP, VWAP, ICEBERG, SOR, POV
    total_quantity: float
    num_slices: Optional[int] = 5

@router.post("/jobs")
async def create_execution_job(body: CreateExecutionJobRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Submit new algorithmic execution job through Phase 35 OMS/EMS Gateway."""
    from backend.execution import execution_job_manager
    user_id = str(current_user.id) if current_user else "demo_user"
    job = execution_job_manager.create_job(
        user_id=user_id,
        symbol=body.symbol,
        side=body.side,
        algo_type=body.algo_type or "TWAP",
        total_quantity=body.total_quantity,
        num_slices=body.num_slices or 5
    )
    return job.to_dict()

@router.get("/jobs")
async def list_execution_jobs(status: Optional[str] = None, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch algorithmic execution jobs for current user."""
    from backend.execution import execution_job_manager
    user_id = str(current_user.id) if current_user else None
    jobs = execution_job_manager.list_jobs(user_id=user_id, status=status)
    return [j.to_dict() for j in jobs]

@router.get("/jobs/{job_id}")
async def get_execution_job(job_id: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch execution job state & child slices by job_id."""
    from backend.execution import execution_job_manager
    job = execution_job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Execution job {job_id} not found.")
    return job.to_dict()

@router.post("/jobs/{job_id}/cancel")
async def cancel_execution_job(job_id: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Cancel execution job by job_id."""
    from backend.execution import execution_job_manager
    try:
        job = execution_job_manager.cancel_job(job_id, reason="User manual API cancellation")
        return job.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/algorithms/twap")
async def create_twap_algorithm(body: TWAPAlgorithmRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Initialize TWAP Slicing Job."""
    uid = current_user.id if current_user else 1
    job = execution_orchestrator.twap_engine.create_twap_job(
        job_id=f"TWAP-{uid}-1",
        symbol=body.symbol,
        side=body.side,
        total_quantity=body.total_quantity,
        duration_seconds=body.duration_seconds or 300,
        slice_interval_seconds=body.slice_interval_seconds or 30
    )
    return job.to_dict()

@router.post("/algorithms/vwap")
async def create_vwap_algorithm(body: VWAPAlgorithmRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Initialize VWAP Intraday Allocation Job."""
    uid = current_user.id if current_user else 1
    job = execution_orchestrator.vwap_engine.create_vwap_job(
        job_id=f"VWAP-{uid}-1",
        symbol=body.symbol,
        side=body.side,
        total_quantity=body.total_quantity,
        num_bins=body.num_bins or 10
    )
    return job.to_dict()

@router.post("/algorithms/iceberg")
async def create_iceberg_algorithm(body: IcebergAlgorithmRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Initialize Iceberg Hidden Reserve Job."""
    uid = current_user.id if current_user else 1
    job = execution_orchestrator.iceberg_engine.create_iceberg(
        iceberg_id=f"ICE-{uid}-1",
        symbol=body.symbol,
        side=body.side,
        total_quantity=body.total_quantity,
        display_quantity_pct=body.display_quantity_pct or 10.0
    )
    return job.to_dict()
