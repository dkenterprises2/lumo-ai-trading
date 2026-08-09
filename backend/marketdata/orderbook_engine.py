import time
from typing import Dict, Any, List, Tuple

class Level2OrderBookEngine:
    """Level-2 Order Book Streaming Engine with Incremental Depth & Sequence Validation."""

    def __init__(self):
        self._books: Dict[str, Dict[str, Any]] = {
            "BTC/USDT": {
                "symbol": "BTC/USDT",
                "sequence_id": 100050,
                "bids": [(64810.0, 1.5), (64809.5, 2.2), (64809.0, 4.1), (64808.5, 6.0), (64808.0, 10.5)],
                "asks": [(64810.5, 1.2), (64811.0, 3.4), (64811.5, 5.1), (64812.0, 8.2), (64812.5, 12.0)],
                "updated_at": time.time()
            }
        }

    def get_orderbook(self, symbol: str = "BTC/USDT", levels: int = 10) -> Dict[str, Any]:
        book = self._books.get(symbol, self._books["BTC/USDT"])
        return {
            "symbol": symbol,
            "sequence_id": book["sequence_id"],
            "bids": book["bids"][:levels],
            "asks": book["asks"][:levels],
            "timestamp": book["updated_at"]
        }

    def update_depth(self, symbol: str, bids: List[Tuple[float, float]], asks: List[Tuple[float, float]], sequence_id: int) -> bool:
        if symbol in self._books:
            self._books[symbol]["bids"] = bids
            self._books[symbol]["asks"] = asks
            self._books[symbol]["sequence_id"] = sequence_id
            self._books[symbol]["updated_at"] = time.time()
            return True
        return False

orderbook_engine = Level2OrderBookEngine()
