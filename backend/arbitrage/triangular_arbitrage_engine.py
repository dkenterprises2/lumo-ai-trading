from dataclasses import dataclass, asdict
from typing import Dict, List, Any

@dataclass
class TriangularOpportunity:
    exchange: str
    route: List[str]
    implied_multiplier: float
    profit_pct: float
    is_actionable: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class TriangularArbitrageEngine:
    """Intra-Exchange Triangular Arbitrage Calculator."""

    def evaluate_triangular_route(
        self,
        exchange: str = "BINANCE",
        pair_a_price: float = 118450.0,   # BTC/USDT
        pair_b_price: float = 0.035,      # ETH/BTC
        pair_c_price: float = 4200.0      # ETH/USDT
    ) -> TriangularOpportunity:
        # Route: USDT -> BTC -> ETH -> USDT
        # Step 1: Buy BTC with USDT -> 1 / pair_a
        # Step 2: Buy ETH with BTC -> (1 / pair_a) / pair_b
        # Step 3: Sell ETH for USDT -> ((1 / pair_a) / pair_b) * pair_c
        implied_usdt = ((1.0 / pair_a_price) / pair_b_price) * pair_c_price
        profit_pct = (implied_usdt - 1.0) * 100.0
        
        # Deduct 3 legs of taker fees (3 * 7.5 bps = 22.5 bps = 0.225%)
        net_profit_pct = profit_pct - 0.225
        is_actionable = net_profit_pct >= 0.15

        return TriangularOpportunity(
            exchange=exchange,
            route=["USDT->BTC", "BTC->ETH", "ETH->USDT"],
            implied_multiplier=round(implied_usdt, 6),
            profit_pct=round(net_profit_pct, 4),
            is_actionable=is_actionable
        )
