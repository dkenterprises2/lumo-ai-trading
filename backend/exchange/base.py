from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseExchangeAdapter(ABC):
    """Abstract interface for all broker and exchange adapters."""

    @abstractmethod
    def get_exchange_name(self) -> str:
        pass

    @abstractmethod
    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def fetch_balance(self) -> Dict[str, Any]:
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
        take_profit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def close_position(self, symbol: str, price: Optional[float] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_positions() -> Dict[str, Any]:
        pass
