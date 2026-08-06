import time
import uuid
from typing import Dict, Any, Optional, List
from backend.exchange.base import BaseExchangeAdapter

class PaperExchangeAdapter(BaseExchangeAdapter):
    """Paper Trading Exchange Adapter preserving paper simulation & double-entry accounting."""

    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.wallet_balance = initial_balance
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self.positions: Dict[str, Dict[str, Any]] = {}

    def get_exchange_name(self) -> str:
        return "PAPER"

    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "last": 65000.0,
            "bid": 64995.0,
            "ask": 65005.0,
            "high_24h": 65500.0,
            "low_24h": 64200.0,
            "volume": 50000.0,
            "exchange": "PAPER"
        }

    def fetch_balance(self) -> Dict[str, Any]:
        return {
            "total_wallet": round(self.wallet_balance, 2),
            "free_balance": round(self.wallet_balance, 2),
            "total_equity": round(self.wallet_balance, 2),
            "exchange": "PAPER"
        }

    def fetch_positions(self) -> Dict[str, Any]:
        return self.positions

    def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        if symbol:
            return [o for o in self.active_orders.values() if o["symbol"] == symbol and o["status"] == "OPEN"]
        return [o for o in self.active_orders.values() if o["status"] == "OPEN"]

    def create_order(
        self,
        symbol: str,
        side: str,
        amount_usd: float,
        order_type: str = "MARKET",
        leverage: int = 1,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        client_order_id: Optional[str] = None,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        c_id = client_order_id or f"PAPER_ORD_{int(time.time()*1000)}_{uuid.uuid4().hex[:4]}"

        if c_id in self.active_orders:
            return self.active_orders[c_id]

        exec_price = price or 65000.0
        order_res = {
            "status": "FILLED" if order_type == "MARKET" else "OPEN",
            "order_id": c_id,
            "client_order_id": c_id,
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "price": exec_price,
            "amount_usd": amount_usd,
            "leverage": leverage,
            "filled_amount": amount_usd if order_type == "MARKET" else 0.0,
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price,
            "exchange": "PAPER",
            "timestamp": time.time()
        }
        self.active_orders[c_id] = order_res
        return order_res

    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        if order_id in self.active_orders:
            self.active_orders[order_id]["status"] = "CANCELLED"
            return {"status": "success", "message": f"Order {order_id} cancelled.", "order_id": order_id}
        return {"status": "error", "message": f"Order {order_id} not found."}

    def replace_order(self, order_id: str, symbol: str, amount_usd: float, price: float) -> Dict[str, Any]:
        if order_id in self.active_orders:
            self.active_orders[order_id]["amount_usd"] = amount_usd
            self.active_orders[order_id]["price"] = price
            return {"status": "success", "message": f"Order {order_id} updated.", "order": self.active_orders[order_id]}
        return {"status": "error", "message": f"Order {order_id} not found."}

    def reconcile_orders(self) -> List[Dict[str, Any]]:
        return list(self.active_orders.values())
