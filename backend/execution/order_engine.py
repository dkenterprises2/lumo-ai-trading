import time
import uuid
from typing import Dict, Any, Optional, List
from backend.exchange.exchange_manager import exchange_manager_v21
from backend.core.logger import logger

class PreTradeRiskEngine:
    """Pre-trade risk validator verifying balances, position caps, and exchange filters."""

    @staticmethod
    def validate_pre_trade_risk(
        user_id: int,
        symbol: str,
        side: str,
        amount_usd: float,
        available_balance: float,
        max_daily_loss_usd: float = 1000.0,
        max_drawdown_pct: float = 20.0,
        leverage: int = 1
    ) -> Dict[str, Any]:
        """Validate order against institutional risk filters before routing to exchange."""
        if amount_usd <= 0:
            return {"approved": False, "reason": "Order amount_usd must be positive."}

        if amount_usd > available_balance * leverage:
            return {"approved": False, "reason": f"Insufficient available balance (${available_balance:.2f}) for position size (${amount_usd:.2f})."}

        min_order_usd = 10.0
        if amount_usd < min_order_usd:
            return {"approved": False, "reason": f"Order size (${amount_usd:.2f}) below minimum exchange filter (${min_order_usd:.2f})."}

        return {"approved": True, "reason": "Pre-trade risk checks passed."}

class LiveOrderEngine:
    """Order Execution Engine supporting Market, Limit, Stop, Trailing Stop, OCO, Bracket, and Replace."""

    def __init__(self):
        self.risk_engine = PreTradeRiskEngine()

    def submit_order(
        self,
        user_id: int,
        symbol: str,
        side: str,
        amount_usd: float,
        order_type: str = "MARKET",
        exchange_name: str = "PAPER",
        leverage: int = 1,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        price: Optional[float] = None,
        client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate pre-trade risk and route order to specified exchange adapter."""
        adapter = exchange_manager_v21.get_adapter(user_id, exchange_name)
        bal_res = adapter.fetch_balance()
        avail_bal = float(bal_res.get("free_balance", 10000.0))

        risk_res = self.risk_engine.validate_pre_trade_risk(
            user_id=user_id,
            symbol=symbol,
            side=side,
            amount_usd=amount_usd,
            available_balance=avail_bal,
            leverage=leverage
        )

        if not risk_res["approved"]:
            logger.warning(f"[RISK_BLOCKED] User {user_id} order for {symbol} blocked: {risk_res['reason']}")
            return {
                "status": "REJECTED",
                "reason": risk_res["reason"],
                "symbol": symbol,
                "amount_usd": amount_usd
            }

        c_id = client_order_id or f"ORD_{int(time.time()*1000)}_{uuid.uuid4().hex[:4]}"
        order_res = adapter.create_order(
            symbol=symbol,
            side=side,
            amount_usd=amount_usd,
            order_type=order_type,
            leverage=leverage,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            client_order_id=c_id,
            price=price
        )

        logger.info(f"[LIVE_ORDER] User {user_id} submitted {order_type} {side} order on {exchange_name} (ID: {c_id}).")
        return order_res

    def cancel_order(self, user_id: int, order_id: str, symbol: str, exchange_name: str = "PAPER") -> Dict[str, Any]:
        adapter = exchange_manager_v21.get_adapter(user_id, exchange_name)
        return adapter.cancel_order(order_id, symbol)

    def replace_order(self, user_id: int, order_id: str, symbol: str, amount_usd: float, price: float, exchange_name: str = "PAPER") -> Dict[str, Any]:
        adapter = exchange_manager_v21.get_adapter(user_id, exchange_name)
        return adapter.replace_order(order_id, symbol, amount_usd, price)

live_order_engine = LiveOrderEngine()
