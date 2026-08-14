from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class KellySizingResult:
    raw_kelly: float
    fractional_kelly: float
    capped_allocation_usd: float
    effective_risk_pct: float
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class KellySizingEngine:
    """Safe Fractional Kelly Criterion sizing engine with strict risk caps."""

    def compute_kelly_size(
        self,
        win_probability: float = 0.55,
        win_loss_ratio: float = 1.5,
        portfolio_equity: float = 10000.0,
        kelly_fraction: float = 0.25,
        max_cap_pct: float = 10.0,
        drawdown_mult: float = 1.0,
        volatility_mult: float = 1.0
    ) -> KellySizingResult:
        """Compute fractional Kelly size in USD."""
        p = max(0.01, min(0.99, win_probability))
        b = max(0.1, win_loss_ratio)
        q = 1.0 - p

        # Full Kelly = (b * p - q) / b
        raw_k = (b * p - q) / b
        if raw_k <= 0:
            return KellySizingResult(
                raw_kelly=round(raw_k, 4),
                fractional_kelly=0.0,
                capped_allocation_usd=0.0,
                effective_risk_pct=0.0,
                reason="Negative Kelly expectancy. Trade sizing set to 0."
            )

        # Apply fraction (e.g. 0.25 = Quarter Kelly)
        f_k = raw_k * kelly_fraction

        # Apply drawdown & volatility multipliers
        adjusted_f_k = f_k * drawdown_mult * volatility_mult

        # Hard upper cap (e.g. max 10% of portfolio per trade)
        capped_f_k = min(adjusted_f_k, max_cap_pct / 100.0)
        alloc_usd = portfolio_equity * capped_f_k

        return KellySizingResult(
            raw_kelly=round(raw_k, 4),
            fractional_kelly=round(f_k, 4),
            capped_allocation_usd=round(alloc_usd, 2),
            effective_risk_pct=round(capped_f_k * 100.0, 2),
            reason=f"Fractional ({kelly_fraction}x) Kelly calculated. Allocation capped to ${alloc_usd:.2f} ({capped_f_k * 100.0:.1f}%)."
        )
