import time
import uuid
from typing import Dict, Any, Optional, List
from backend.exchange.base import BaseExchangeAdapter

class OKXAdapter(BaseExchangeAdapter):
    """OKX Spot & Swap Contract Exchange Adapter."""

    def __init__(self, api_key: str = "", secret_key: str = "", testnet: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.testnet = testnet
        self.active_orders: Dict[str, Dict[str, Any]] = {}

    def get_exchange_name(self) -> str:
        return "OKX_DEMO" if self.testnet else "OKX_LIVE"

    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "last": 64990.0,
            "bid": 64985.0,
            "ask": 64995.0,
            "volume": 38000.0,
            "exchange": self.get_exchange_name()
        }

    def fetch_balance(self) -> Dict[str, Any]:
        return {
            "total_wallet": 10000.0,
            "free_balance": 10000.0,
            "total_equity": 10000.0,
            "exchange": self.get_exchange_name()
        }

    def fetch_positions(self) -> Dict[str, Any]:
        return {}

    def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        return list(self.active_orders.values())

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
        c_id = client_order_id or f"OKX_{int(time.time()*1000)}_{uuid.uuid4().hex[:4]}"
        if c_id in self.active_orders:
            return self.active_orders[c_id]

        res = {
            "status": "FILLED" if order_type == "MARKET" else "OPEN",
            "order_id": c_id,
            "client_order_id": c_id,
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "price": price or 64990.0,
            "amount_usd": amount_usd,
            "leverage": leverage,
            "exchange": self.get_exchange_name(),
            "timestamp": time.time()
        }
        self.active_orders[c_id] = res
        return res

    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        if order_id in self.active_orders:
            self.active_orders[order_id]["status"] = "CANCELLED"
            return {"status": "success", "order_id": order_id}
        return {"status": "error", "message": "Order not found"}

    def replace_order(self, order_id: str, symbol: str, amount_usd: float, price: float) -> Dict[str, Any]:
        if order_id in self.active_orders:
            self.active_orders[order_id]["price"] = price
            return {"status": "success", "order": self.active_orders[order_id]}
        return {"status": "error", "message": "Order not found"}

    def reconcile_orders(self) -> List[Dict[str, Any]]:
        return list(self.active_orders.values())
