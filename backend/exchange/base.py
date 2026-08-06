from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseExchangeAdapter(ABC):
    """Abstract Base Class for all Exchange Adapters (Binance, Bybit, OKX, Paper)."""

    @abstractmethod
    def get_exchange_name(self) -> str:
        """Return unique exchange identifier."""
        pass

    @abstractmethod
    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch current ticker price and 24h stats."""
        pass

    @abstractmethod
    def fetch_balance(self) -> Dict[str, Any]:
        """Fetch account wallet balance and equity."""
        pass

    @abstractmethod
    def fetch_positions(self) -> Dict[str, Any]:
        """Fetch active open positions."""
        pass

    @abstractmethod
    def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch open active orders."""
        pass

    @abstractmethod
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
        """Place new order with idempotency check."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an open order."""
        pass

    @abstractmethod
    def replace_order(self, order_id: str, symbol: str, amount_usd: float, price: float) -> Dict[str, Any]:
        """Replace an existing order."""
        pass

    @abstractmethod
    def reconcile_orders(self) -> List[Dict[str, Any]]:
        """Reconcile local open order states with exchange order book."""
        pass

    def get_capabilities(self) -> Dict[str, Any]:
        """Return supported features and rate limit specs."""
        return {
            "spot_trading": True,
            "futures_trading": True,
            "margin_trading": False,
            "stop_market_orders": True,
            "trailing_stop_orders": True,
            "rate_limit_requests_per_min": 1200
        }

    def normalize_symbol(self, symbol: str) -> str:
        """Standardize internal symbol to exchange format (e.g. BTC/USDT -> BTCUSDT)."""
        return symbol.replace("/", "").replace("-", "").upper()

    def denormalize_symbol(self, exchange_symbol: str) -> str:
        """Standardize exchange symbol back to internal format (e.g. BTCUSDT -> BTC/USDT)."""
        if "USDT" in exchange_symbol and "/" not in exchange_symbol:
            base = exchange_symbol.replace("USDT", "")
            return f"{base}/USDT"
        return exchange_symbol
