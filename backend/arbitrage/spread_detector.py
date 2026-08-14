from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class ArbitrageSpread:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    gross_spread_usd: float
    gross_spread_pct: float
    total_fees_bps: float
    transfer_cost_usd: float
    latency_penalty_bps: float
    net_spread_pct: float
    is_executable: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SpreadDetector:
    """Calculates Net Executable Arbitrage Spread with Fee & Latency Deductions."""

    def compute_spread(
        self,
        symbol: str,
        buy_exchange: str,
        sell_exchange: str,
        buy_ask_price: float,
        sell_bid_price: float,
        buy_fee_bps: float = 7.5,
        sell_fee_bps: float = 7.5,
        latency_ms: float = 25.0
    ) -> ArbitrageSpread:
        gross_usd = sell_bid_price - buy_ask_price
        gross_pct = (gross_usd / buy_ask_price) * 100.0 if buy_ask_price > 0 else 0.0

        total_fees = buy_fee_bps + sell_fee_bps
        latency_penalty = (latency_ms / 100.0) * 1.5  # 1.5 bps per 100ms
        transfer_cost_usd = 1.0  # Fixed transfer cost estimate

        net_pct = gross_pct - (total_fees / 100.0) - (latency_penalty / 100.0)
        is_exec = net_pct >= 0.15  # Minimum 0.15% net edge requirement

        return ArbitrageSpread(
            symbol=symbol,
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            buy_price=round(buy_ask_price, 2),
            sell_price=round(sell_bid_price, 2),
            gross_spread_usd=round(gross_usd, 2),
            gross_spread_pct=round(gross_pct, 4),
            total_fees_bps=total_fees,
            transfer_cost_usd=transfer_cost_usd,
            latency_penalty_bps=round(latency_penalty, 2),
            net_spread_pct=round(net_pct, 4),
            is_executable=is_exec
        )
