from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseStrategyPlugin(ABC):
    """Abstract Base Class for Strategy Plugins."""

    @abstractmethod
    def get_strategy_name(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, symbol: str, current_price: float, technical_data: Dict[str, Any], sentiment_summary: Dict[str, Any]) -> Dict[str, Any]:
        pass
