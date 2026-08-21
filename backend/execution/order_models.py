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

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        avg_f = self.average_fill_price or (self.price or 100.0)
        mark_p = self.metadata.get("mark_price", avg_f)
        qty = self.filled_quantity or self.quantity
        tot_val = round(qty * avg_f, 2)
        fee = round(tot_val * 0.00075, 2)  # Standard 0.075% taker fee

        # Authentic Mark-to-Market PnL Calculation
        if self.side.upper() in ["BUY", "LONG"]:
            pnl_usd = round((mark_p - avg_f) * qty - fee, 2)
        else:
            pnl_usd = round((avg_f - mark_p) * qty - fee, 2)

        pnl_pct = round((pnl_usd / max(1.0, tot_val)) * 100.0, 2)

        d["mark_price"] = mark_p
        d["total_value_usd"] = tot_val
        d["fee_usd"] = fee
        d["pnl_usd"] = pnl_usd
        d["pnl_pct"] = pnl_pct
        return d

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
