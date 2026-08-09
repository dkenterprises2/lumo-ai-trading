from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.multiasset.security_master import security_master
from backend.multiasset.unified_portfolio import unified_portfolio
from backend.multiasset.prime_brokerage import prime_brokerage
from backend.multiasset.oms_engine import oms_engine
from backend.multiasset.ems_engine import ems_engine
from backend.multiasset.cross_chain_wallets import cross_chain_wallets
from backend.multiasset.onchain_analytics import onchain_analytics
from backend.multiasset.whale_monitor import whale_monitor
from backend.multiasset.arbitrage_graph import arbitrage_graph
from backend.multiasset.collateral_optimizer import collateral_optimizer
from backend.multiasset.treasury_manager import treasury_manager
from backend.multiasset.yield_router import yield_router
from backend.multiasset.global_risk_engine import global_risk_engine
from backend.multiasset.settlement_engine import settlement_engine
from backend.multiasset.custody_layer import custody_layer

router = APIRouter(tags=["Global Multi-Asset & Prime Brokerage Platform"])

@router.get("/api/multiasset/securities")
async def list_securities(current_user: UserModel = Depends(get_current_user)):
    return {"securities": security_master.list_securities()}

@router.post("/api/multiasset/securities")
async def register_security(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return security_master.register_security(body)

@router.get("/api/multiasset/portfolio/unified")
async def get_unified_portfolio(current_user: UserModel = Depends(get_current_user)):
    return unified_portfolio.calculate_global_nav("USD")

@router.get("/api/multiasset/portfolio/nav")
async def get_global_nav(current_user: UserModel = Depends(get_current_user)):
    return unified_portfolio.calculate_global_nav("USD")

@router.get("/api/multiasset/brokers")
async def list_prime_brokers(current_user: UserModel = Depends(get_current_user)):
    return {"brokers": prime_brokerage.list_brokers()}

@router.post("/api/multiasset/brokers/accounts")
async def register_broker_account(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return prime_brokerage.register_account(body)

@router.post("/api/multiasset/oms/orders")
async def create_oms_order(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    symbol = body.get("symbol", "BTCUSDT")
    asset_class = body.get("asset_class", "CRYPTO")
    qty = body.get("quantity", 10.0)
    side = body.get("side", "BUY")
    return oms_engine.create_order(symbol, asset_class, qty, side)

@router.get("/api/multiasset/oms/orders/{order_id}")
async def get_oms_order(order_id: str, current_user: UserModel = Depends(get_current_user)):
    return oms_engine.get_order(order_id)

@router.post("/api/multiasset/ems/routes")
async def route_ems_execution(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    order_id = body.get("order_id", "OMS-PARENT-101")
    venue = body.get("venue", "Binance")
    qty = body.get("quantity", 10.0)
    return ems_engine.route_execution(order_id, venue, qty)

@router.get("/api/multiasset/ems/routes/{route_id}")
async def get_ems_route(route_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"route_id": route_id, "status": "EXECUTED_SIMULATED"}

@router.get("/api/multiasset/wallets")
async def list_cross_chain_wallets(current_user: UserModel = Depends(get_current_user)):
    return {"wallets": cross_chain_wallets.list_wallets()}

@router.post("/api/multiasset/wallets/register")
async def register_wallet(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return cross_chain_wallets.register_wallet(body)

@router.get("/api/multiasset/onchain/analytics")
async def get_onchain_analytics(current_user: UserModel = Depends(get_current_user)):
    return onchain_analytics.get_analytics()

@router.get("/api/multiasset/onchain/whales")
async def get_whale_alerts(current_user: UserModel = Depends(get_current_user)):
    return {"alerts": whale_monitor.list_alerts()}

@router.get("/api/multiasset/arbitrage/opportunities")
async def get_arbitrage_opportunities(current_user: UserModel = Depends(get_current_user)):
    return {"opportunities": arbitrage_graph.find_opportunities()}

@router.get("/api/multiasset/collateral/status")
async def get_collateral_status(current_user: UserModel = Depends(get_current_user)):
    return collateral_optimizer.optimize_collateral()

@router.post("/api/multiasset/collateral/optimize")
async def optimize_collateral(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    total = body.get("total_collateral", 1000000.0)
    margin = body.get("margin_used", 400000.0)
    return collateral_optimizer.optimize_collateral(total, margin)

@router.get("/api/multiasset/treasury/status")
async def get_treasury_status(current_user: UserModel = Depends(get_current_user)):
    return treasury_manager.get_treasury_status()

@router.get("/api/multiasset/treasury/yield-opportunities")
async def get_yield_opportunities(current_user: UserModel = Depends(get_current_user)):
    return {"opportunities": yield_router.get_yield_opportunities()}

@router.get("/api/multiasset/risk/global")
async def get_global_risk(current_user: UserModel = Depends(get_current_user)):
    return global_risk_engine.get_global_risk()

@router.get("/api/multiasset/risk/stress-tests")
async def get_global_stress_tests(current_user: UserModel = Depends(get_current_user)):
    return {
        "scenarios": [
            {"scenario": "Crypto Liquidity Shock (-30%)", "estimated_loss_usd": 630000.0},
            {"scenario": "USD Rate Hike + Vol Spike", "estimated_loss_usd": 210000.0}
        ]
    }

@router.post("/api/multiasset/settlement/instructions")
async def create_settlement_instruction(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    asset = body.get("asset", "USDT")
    amount = body.get("amount", 100000.0)
    recipient = body.get("recipient", "Binance Custody")
    return settlement_engine.create_instruction(asset, amount, recipient)

@router.get("/api/multiasset/custody/accounts")
async def list_custody_accounts(current_user: UserModel = Depends(get_current_user)):
    return {"accounts": custody_layer.get_custody_accounts()}
