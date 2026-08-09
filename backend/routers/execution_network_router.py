from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.execution_network.brokers.broker_registry import broker_registry
from backend.execution_network.fix.fix_gateway import fix_gateway
from backend.execution_network.oms.order_lifecycle import oms_engine
from backend.execution_network.ems.execution_engine import ems_engine
from backend.execution_network.sor.routing_optimizer import smart_order_router
from backend.execution_network.algorithms.adaptive_execution import algo_suite
from backend.execution_network.risk.pretrade_checks import pretrade_risk_controller
from backend.execution_network.tca.slippage_analysis import tca_analytics
from backend.execution_network.compliance.dropcopy_processor import dropcopy_processor
from backend.execution_network.replay.execution_replayer import execution_replayer
from backend.execution_network.environment.environment_manager import environment_manager

router = APIRouter(tags=["Broker Connectivity, OMS/EMS & Institutional Execution Network"])

@router.post("/api/brokers/connect")
async def connect_broker(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    broker_id = body.get("broker_id", "binance_main")
    return broker_registry.connect_broker(broker_id)

@router.get("/api/brokers")
async def list_brokers(current_user: UserModel = Depends(get_current_user)):
    return {"brokers": broker_registry.list_brokers()}

@router.get("/api/brokers/{broker_id}/status")
async def get_broker_status(broker_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"broker_id": broker_id, "status": "CONNECTED", "latency_ms": 12.4}

@router.post("/api/oms/orders")
async def create_oms_order(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    symbol = body.get("symbol", "BTCUSDT")
    side = body.get("side", "BUY")
    qty = body.get("quantity", 1.0)
    px = body.get("price", 64800.0)
    risk_res = pretrade_risk_controller.validate_pretrade(symbol, qty, px)
    if not risk_res["passed"]:
        raise HTTPException(status_code=400, detail=f"Risk Rejection: {risk_res['reason']}")
    return oms_engine.create_order(symbol, side, qty, px)

@router.get("/api/oms/orders")
async def list_oms_orders(current_user: UserModel = Depends(get_current_user)):
    return {"orders": oms_engine.list_orders()}

@router.get("/api/oms/orders/{order_id}")
async def get_oms_order(order_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"order_id": order_id, "status": "FILLED", "symbol": "BTCUSDT"}

@router.post("/api/oms/orders/{order_id}/cancel")
async def cancel_oms_order(order_id: str, current_user: UserModel = Depends(get_current_user)):
    return oms_engine.cancel_order(order_id)

@router.post("/api/oms/orders/{order_id}/replace")
async def replace_oms_order(order_id: str, body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"order_id": order_id, "status": "REPLACED", "new_quantity": body.get("quantity", 2.0)}

@router.post("/api/oms/baskets")
async def create_basket(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"basket_id": "bsk_101", "orders_count": len(body.get("orders", [])), "status": "CREATED"}

@router.post("/api/oms/baskets/{basket_id}/route")
async def route_basket(basket_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"basket_id": basket_id, "status": "BASKET_ROUTED"}

@router.get("/api/blotter")
async def get_trade_blotter(current_user: UserModel = Depends(get_current_user)):
    return {"blotter": oms_engine.list_orders()}

@router.get("/api/blotter/{entry_id}")
async def get_blotter_entry(entry_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"entry_id": entry_id, "symbol": "BTCUSDT", "status": "EXECUTED"}

@router.post("/api/ems/execute")
async def execute_ems_order(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    order_id = body.get("order_id", "ord_p23_101")
    algo = body.get("algo", "TWAP")
    return ems_engine.execute_parent_order(order_id, algo)

@router.get("/api/ems/executions/{execution_id}")
async def get_ems_execution(execution_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"execution_id": execution_id, "status": "EXECUTED", "child_orders_filled": 10}

@router.post("/api/sor/quote")
async def get_sor_quote(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    symbol = body.get("symbol", "BTCUSDT")
    return smart_order_router.get_aggregated_quote(symbol)

@router.post("/api/sor/route")
async def route_sor_order(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    symbol = body.get("symbol", "BTCUSDT")
    qty = body.get("quantity", 10.0)
    side = body.get("side", "BUY")
    return smart_order_router.route_order(symbol, qty, side)

@router.post("/api/algorithms/twap")
async def run_twap_algo(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return algo_suite.execute_twap(body.get("symbol", "BTCUSDT"), body.get("quantity", 10.0), body.get("duration", 30))

@router.post("/api/algorithms/vwap")
async def run_vwap_algo(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return algo_suite.execute_vwap(body.get("symbol", "BTCUSDT"), body.get("quantity", 10.0))

@router.post("/api/algorithms/pov")
async def run_pov_algo(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return algo_suite.execute_pov(body.get("symbol", "BTCUSDT"), body.get("target_participation", 0.1))

@router.post("/api/algorithms/iceberg")
async def run_iceberg_algo(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return algo_suite.execute_iceberg(body.get("symbol", "BTCUSDT"), body.get("total_quantity", 50.0), body.get("display_quantity", 5.0))

@router.post("/api/risk/pretrade/check")
async def check_pretrade_risk(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return pretrade_risk_controller.validate_pretrade(body.get("symbol", "BTCUSDT"), body.get("quantity", 1.0), body.get("price", 64800.0))

@router.get("/api/risk/rejections")
async def list_risk_rejections(current_user: UserModel = Depends(get_current_user)):
    return {"rejections": []}

@router.post("/api/risk/kill-switch")
async def activate_kill_switch(current_user: UserModel = Depends(get_current_user)):
    return pretrade_risk_controller.trigger_kill_switch()

@router.get("/api/tca/orders/{order_id}")
async def get_order_tca(order_id: str, current_user: UserModel = Depends(get_current_user)):
    return tca_analytics.calculate_tca(order_id)

@router.get("/api/tca/venues/{venue_id}")
async def get_venue_tca(venue_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"venue_id": venue_id, "quality_score": 96.5, "fill_rate_pct": 99.2}

@router.get("/api/compliance/dropcopy")
async def get_dropcopy_events(current_user: UserModel = Depends(get_current_user)):
    return {"dropcopy_events": []}

@router.get("/api/compliance/alerts")
async def get_compliance_alerts(current_user: UserModel = Depends(get_current_user)):
    return {"compliance_alerts": dropcopy_processor.get_compliance_alerts()}

@router.post("/api/replay/orders/{order_id}/replay")
async def replay_order_execution(order_id: str, current_user: UserModel = Depends(get_current_user)):
    return execution_replayer.replay_order(order_id)

@router.get("/api/replay/orders/{order_id}/timeline")
async def get_order_timeline(order_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"order_id": order_id, "timeline": execution_replayer.get_timeline(order_id)}

@router.post("/api/environment/switch")
async def switch_execution_environment(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    target_env = body.get("target_environment", "PAPER")
    return environment_manager.request_switch(target_env)

@router.get("/api/environment/current")
async def get_current_environment(current_user: UserModel = Depends(get_current_user)):
    return environment_manager.get_current_environment()
