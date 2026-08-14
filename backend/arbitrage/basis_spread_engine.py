from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class BasisOpportunity:
    symbol: str
    exchange: str
    spot_price: float
    perpetual_mark_price: float
    basis_usd: float
    annualized_basis_pct: float
    is_actionable: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BasisSpreadEngine:
    """Spot-Perpetual Basis Arbitrage Engine."""

    def evaluate_basis(
        self,
        symbol: str,
        exchange: str,
        spot_price: float,
        perp_mark_price: float,
        days_to_expiry: float = 30.0
    ) -> BasisOpportunity:
        basis_usd = perp_mark_price - spot_price
        basis_pct = (basis_usd / spot_price) * 100.0 if spot_price > 0 else 0.0
        annualized_pct = basis_pct * (365.0 / max(1.0, days_to_expiry))

        is_actionable = annualized_pct >= 8.0
        reason = "Annualized basis > 8.0% threshold" if is_actionable else "Annualized basis below 8.0% minimum"

        return BasisOpportunity(
            symbol=symbol,
            exchange=exchange,
            spot_price=round(spot_price, 2),
            perpetual_mark_price=round(perp_mark_price, 2),
            basis_usd=round(basis_usd, 2),
            annualized_basis_pct=round(annualized_pct, 2),
            is_actionable=is_actionable,
            reason=reason
        )
