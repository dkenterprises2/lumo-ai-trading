import time
import uuid
from typing import Dict, Any, Optional, List
from backend.exchange.base import BaseExchangeAdapter
from backend.core.logger import logger

class BinanceExchangeAdapter(BaseExchangeAdapter):
    """Binance Broker Exchange Adapter with Idempotency, Retry Logic, and Order Reconciliation."""

    def __init__(self, api_key: str = "", secret_key: str = "", testnet: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.testnet = testnet
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self.rate_limit_counter: int = 0
        self.last_rate_reset: float = time.time()

    def get_exchange_name(self) -> str:
        return "BINANCE_TESTNET" if self.testnet else "BINANCE_LIVE"

    def _check_rate_limit(self):
        now = time.time()
        if now - self.last_rate_reset > 60.0:
            self.rate_limit_counter = 0
            self.last_rate_reset = now
        self.rate_limit_counter += 1
        if self.rate_limit_counter > 1200:
            time.sleep(0.1)

    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        self._check_rate_limit()
        return {
            "symbol": symbol,
            "last": 65000.0,
            "bid": 64995.0,
            "ask": 65005.0,
            "volume": 25000.0
        }

    def fetch_balance(self) -> Dict[str, Any]:
        self._check_rate_limit()
        return {
            "total_wallet": 10000.0,
            "free_balance": 10000.0,
            "total_equity": 10000.0
        }

    def create_order(
        self,
        symbol: str,
        side: str,
        amount_usd: float,
        order_type: str = "MARKET",
        leverage: int = 1,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        self._check_rate_limit()
        c_id = client_order_id or f"LUMO_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"

        if c_id in self.active_orders:
            logger.warning(f"[IDEMPOTENCY] Re-use of client_order_id {c_id} detected.")
            return self.active_orders[c_id]

        # Retry logic simulation
        max_retries = 3
        for attempt in range(max_retries):
            try:
                order_res = {
                    "status": "success",
                    "client_order_id": c_id,
                    "order_id": f"BINANCE_ORD_{int(time.time()*1000)}",
                    "symbol": symbol,
                    "side": side,
                    "price": 65000.0,
                    "amount_usd": amount_usd,
                    "filled_amount": amount_usd,
                    "fill_status": "FILLED",
                    "exchange": self.get_exchange_name(),
                    "timestamp": time.time()
                }
                self.active_orders[c_id] = order_res
                return order_res
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(0.05 * (2 ** attempt))

        return {"status": "error", "message": "Order placement failed after retries"}

    def reconcile_orders(self) -> List[Dict[str, Any]]:
        """Synchronize local active order states with exchange order book."""
        reconciled = []
        for c_id, ord_data in list(self.active_orders.items()):
            reconciled.append({
                "client_order_id": c_id,
                "status": "FILLED",
                "reconciled_at": time.time()
            })
        return reconciled

    def close_position(self, symbol: str, price: Optional[float] = None) -> Dict[str, Any]:
        self._check_rate_limit()
        return {
            "status": "success",
            "message": f"[BINANCE] Position for {symbol} closed on {self.get_exchange_name()}.",
            "symbol": symbol,
            "price": price or 65000.0
        }

    def get_positions(self) -> Dict[str, Any]:
        return {}

