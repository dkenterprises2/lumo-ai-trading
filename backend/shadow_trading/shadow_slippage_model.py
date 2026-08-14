from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class ShadowSlippageResult:
    order_size_usd: float
    orderbook_depth_usd: float
    slippage_bps: float
    slippage_usd: float
    expected_price: float
    simulated_execution_price: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ShadowSlippageModel:
    """Orderbook-Based Market Impact & Slippage Calculator for Shadow Simulation."""

    def calculate_slippage(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        depth_usd: float = 250000.0,
        spread_bps: float = 1.5
    ) -> ShadowSlippageResult:
        p_base = max(0.00000001, price)
        order_val = quantity * p_base
        d_usd = max(1000.0, depth_usd)

        # Impact function: (order_size / depth)^1.2 * 25 bps
        ratio = order_val / d_usd
        impact_bps = (ratio ** 1.2) * 25.0
        total_slippage_bps = (spread_bps / 2.0) + impact_bps
        slippage_usd = order_val * (total_slippage_bps / 10000.0)

        if side.upper() in ["BUY", "LONG"]:
            exec_price = p_base * (1.0 + (total_slippage_bps / 10000.0))
        else:
            exec_price = p_base * (1.0 - (total_slippage_bps / 10000.0))

        return ShadowSlippageResult(
            order_size_usd=round(order_val, 2),
            orderbook_depth_usd=round(d_usd, 2),
            slippage_bps=round(total_slippage_bps, 2),
            slippage_usd=round(slippage_usd, 4),
            expected_price=round(p_base, 4),
            simulated_execution_price=round(exec_price, 4)
        )
