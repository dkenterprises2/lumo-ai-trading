import math
from typing import Dict, Any, Optional
from loguru import logger
from .signal_calibration import CalibratedSignal

class SmartPositionSizingEngine:
    """
    Phase 44.3 Institutional Volatility-Targeted Fractional Kelly Position Sizing.
    Replaces static 'divide balance by remaining slots' with rigorous risk-budgeted sizing.
    """

    def __init__(
        self,
        target_volatility_pct: float = 2.0,     # Annualized or per-trade target vol
        max_capital_per_trade_pct: float = 8.0, # Hard cap per trade: 8% of equity
        fractional_kelly: float = 0.25,         # 1/4 Fractional Kelly (conservative)
        min_trade_usd: float = 10.0
    ):
        self.target_volatility_pct = target_volatility_pct
        self.max_capital_per_trade_pct = max_capital_per_trade_pct
        self.fractional_kelly = fractional_kelly
        self.min_trade_usd = min_trade_usd

    def calculate_position_size(
        self,
        portfolio_equity_usd: float,
        calibrated_signal: CalibratedSignal,
        current_drawdown_pct: float = 0.0,
        correlation_penalty: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates volatility-scaled and Kelly-capped allocation USD.
        """
        if portfolio_equity_usd <= 0 or not calibrated_signal.is_tradeable:
            return {
                "allocation_usd": 0.0,
                "margin_usd": 0.0,
                "leverage": 1,
                "reason": "Signal not tradeable or zero equity."
            }

        p = calibrated_signal.prob_profit
        q = 1.0 - p
        # Win/Loss payoff ratio b = (Avg TP / Avg SL) ~ 1.5
        b = 1.5

        # 1. Full Kelly Criterion: f* = (p * b - q) / b
        raw_kelly = (p * b - q) / max(1e-4, b)
        safe_kelly = max(0.0, raw_kelly * self.fractional_kelly)

        # 2. Volatility Scaling Factor: TargetVol / AssetVol
        asset_vol = max(0.5, calibrated_signal.expected_volatility_pct)
        vol_scalar = min(2.0, max(0.4, self.target_volatility_pct / asset_vol))

        # 3. Drawdown Dampener (De-leverage during drawdown)
        # If drawdown > 4%, reduce sizing linearly: 1.0 - (dd / 20)
        dd_scalar = max(0.25, 1.0 - (current_drawdown_pct / 20.0))

        # 4. Correlation Penalty (0.0 to 0.50 scale down)
        corr_scalar = max(0.50, 1.0 - correlation_penalty)

        # 5. Combined Sizing Fraction
        target_fraction = min(
            self.max_capital_per_trade_pct / 100.0,
            safe_kelly * vol_scalar * dd_scalar * corr_scalar
        )

        allocation_usd = round(portfolio_equity_usd * target_fraction, 2)
        allocation_usd = max(self.min_trade_usd, min(portfolio_equity_usd * (self.max_capital_per_trade_pct / 100.0), allocation_usd))

        # Leverage determination (1x for standard spot; max 2x-3x only if high confidence and low vol)
        if calibrated_signal.expected_volatility_pct <= 1.5 and calibrated_signal.prob_profit >= 0.58:
            leverage = 2
        else:
            leverage = 1

        margin_usd = round(allocation_usd / leverage, 2)

        return {
            "allocation_usd": allocation_usd,
            "margin_usd": margin_usd,
            "leverage": leverage,
            "target_fraction_pct": round(target_fraction * 100.0, 2),
            "vol_scalar": round(vol_scalar, 2),
            "kelly_fraction": round(safe_kelly, 4),
            "reason": f"Sizing: {target_fraction*100:.1f}% equity (Kelly={safe_kelly:.3f}, VolScalar={vol_scalar:.2f}, DDScalar={dd_scalar:.2f})"
        }

# Global Singleton
smart_sizing_engine = SmartPositionSizingEngine()
