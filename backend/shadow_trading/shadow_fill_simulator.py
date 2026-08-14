import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from .shadow_orderbook import ShadowOrderBook, ShadowOrderBookSnapshot
from .shadow_slippage_model import ShadowSlippageModel, ShadowSlippageResult
from .shadow_latency_model import ShadowLatencyModel, ShadowLatencyMetrics

@dataclass
class ShadowFillEvent:
    fill_id: str = field(default_factory=lambda: f"SHADOW-FILL-{uuid.uuid4().hex[:8].upper()}")
    order_id: str = ""
    symbol: str = "BTC/USDT"
    side: str = "BUY"
    requested_qty: float = 0.0
    filled_qty: float = 0.0
    remaining_qty: float = 0.0
    expected_price: float = 0.0
    execution_price: float = 0.0
    fee_usd: float = 0.0
    slippage_cost_usd: float = 0.0
    latency_ms: float = 0.0
    latency_rating: str = "GOOD"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ShadowFillSimulator:
    """Orderbook-Based Execution Fill Simulator for Shadow Trading."""

    def __init__(self):
        self.orderbook_feed = ShadowOrderBook()
        self.slippage_model = ShadowSlippageModel()
        self.latency_model = ShadowLatencyModel()

    def simulate_fill(
        self,
        order_id: str,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: Optional[float] = None
    ) -> ShadowFillEvent:
        curr_p = price if (price and price > 0) else 50000.0
        snapshot = self.orderbook_feed.get_orderbook(symbol, current_price=curr_p)

        # 1. Latency simulation
        latency_res = self.latency_model.simulate_latency()

        # 2. Slippage simulation
        best_p = snapshot.best_ask if side.upper() in ["BUY", "LONG"] else snapshot.best_bid
        slip_res = self.slippage_model.calculate_slippage(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=best_p,
            depth_usd=snapshot.depth_usd,
            spread_bps=snapshot.spread_bps
        )

        # 3. Available Depth Fill logic
        avail_depth_qty = snapshot.asks[0].quantity if side.upper() in ["BUY", "LONG"] else snapshot.bids[0].quantity
        # Allow realistic fill up to requested quantity
        filled_qty = min(quantity, avail_depth_qty * 10.0)
        remaining_qty = max(0.0, quantity - filled_qty)

        fee = filled_qty * slip_res.simulated_execution_price * 0.00075  # 7.5 bps fee

        return ShadowFillEvent(
            order_id=order_id,
            symbol=symbol,
            side=side.upper(),
            requested_qty=round(quantity, 6),
            filled_qty=round(filled_qty, 6),
            remaining_qty=round(remaining_qty, 6),
            expected_price=round(best_p, 4),
            execution_price=round(slip_res.simulated_execution_price, 4),
            fee_usd=round(fee, 4),
            slippage_cost_usd=round(slip_res.slippage_usd, 4),
            latency_ms=latency_res.total_latency_ms,
            latency_rating=latency_res.rating,
            timestamp=time.time()
        )
