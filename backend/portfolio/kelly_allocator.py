from typing import Dict, Any, List

class KellyPositionAllocator:
    """Kelly Criterion Fractional Position Sizing & Cash Reserve Allocator."""

    @staticmethod
    def calculate_fractional_kelly(
        win_rate: float,
        profit_loss_ratio: float,
        fraction: float = 0.50,
        max_position_pct: float = 25.0,
        min_cash_reserve_pct: float = 10.0
    ) -> Dict[str, Any]:
        """Compute fractional Kelly position size with cash reserve constraints."""
        w = win_rate / 100.0 if win_rate > 1.0 else win_rate
        r = max(0.1, profit_loss_ratio)

        full_kelly = (w * r - (1.0 - w)) / r if r > 0 else 0.0
        frac_kelly = full_kelly * fraction

        capped_kelly_pct = min(max_position_pct, max(0.0, frac_kelly * 100.0))
        available_cap_pct = 100.0 - min_cash_reserve_pct
        final_position_pct = min(capped_kelly_pct, available_cap_pct)

        return {
            "full_kelly_pct": round(full_kelly * 100.0, 2),
            "fractional_kelly_pct": round(frac_kelly * 100.0, 2),
            "recommended_position_pct": round(final_position_pct, 2),
            "cash_reserve_pct": round(min_cash_reserve_pct, 2)
        }

kelly_allocator = KellyPositionAllocator()
