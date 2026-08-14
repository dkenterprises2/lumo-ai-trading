import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from .order_state_machine import OrderState

@dataclass
class OMSOrder:
    order_id: str = field(default_factory=lambda: f"ORD-{uuid.uuid4().hex[:10].upper()}")
    client_order_id: str = field(default_factory=lambda: f"CL-{uuid.uuid4().hex[:8].upper()}")
    user_id: str = "default"
    symbol: str = "BTC/USDT"
    side: str = "BUY"  # BUY, SELL, LONG, SHORT
    order_type: str = "MARKET"  # MARKET, LIMIT, TWAP, VWAP, ICEBERG
    quantity: float = 0.0
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    price: Optional[float] = None
    average_fill_price: float = 0.0
    status: str = OrderState.DRAFT.value
    exchange: str = "BINANCE"
    exchange_order_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.remaining_quantity == 0.0 and self.quantity > 0:
            self.remaining_quantity = self.quantity

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class OMSFill:
    fill_id: str = field(default_factory=lambda: f"FILL-{uuid.uuid4().hex[:8].upper()}")
    order_id: str = ""
    fill_price: float = 0.0
    fill_quantity: float = 0.0
    fee: float = 0.0
    liquidity_flag: str = "MAKER"  # MAKER, TAKER
    exchange: str = "BINANCE"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
