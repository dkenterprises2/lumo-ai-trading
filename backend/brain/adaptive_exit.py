import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from .regime_intelligence import MarketRegimeType, RegimeState

@dataclass
class TradeThesis:
    trade_id: str
    symbol: str
    direction: str                     # LONG, SHORT
    entry_price: float
    entry_time: float
    max_holding_seconds: int           # Default e.g. 3600 (60 mins)
    invalidation_condition: str        # e.g. "Price closes above 20 EMA"
    expected_target_price: float
    stop_loss_price: float
    thesis_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ExitDecision:
    should_exit: bool
    exit_price: float
    exit_reason: str
    is_urgent: bool = False

class AdaptiveExitEngine:
    """
    Phase 44.3 Multi-Factor Dynamic Exit Engine.
    Evaluates Thesis Invalidation, Max Holding Time Decay, Trailing Stops, and Regime Flips.
    """

    def evaluate_position_exit(
        self,
        position: Dict[str, Any],
        current_price: float,
        technical_data: Dict[str, Any],
        current_regime: MarketRegimeType,
        now_ts: Optional[float] = None
    ) -> ExitDecision:
        now = now_ts or time.time()
        sym = position.get("symbol", "")
        side = position.get("side", "BUY").upper()
        entry_price = float(position.get("entry_price", current_price))
        sl_price = float(position.get("stop_loss_price", 0.0))
        tp_price = float(position.get("take_profit_price", 0.0))
        entry_time_str = position.get("entry_time", "")

        # 1. Parse Entry Timestamp
        try:
            entry_ts = position.get("entry_time_ts")
            if not entry_ts and entry_time_str:
                entry_ts = time.mktime(time.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S"))
            else:
                entry_ts = float(entry_ts or (now - 300.0))
        except Exception:
            entry_ts = now - 300.0

        holding_duration_secs = max(0.0, now - entry_ts)
        max_holding_secs = int(position.get("max_holding_seconds", 5400))  # Default 90 mins

        # 2. RULE A: Traditional Hard Stop Loss & Take Profit
        if side in ["BUY", "LONG"]:
            if sl_price > 0 and current_price <= sl_price:
                return ExitDecision(True, current_price, f"Hard Stop-Loss Triggered (${sl_price:,.2f})", True)
            if tp_price > 0 and current_price >= tp_price:
                return ExitDecision(True, current_price, f"Take-Profit Target Achieved (${tp_price:,.2f})", False)
        else:
            if sl_price > 0 and current_price >= sl_price:
                return ExitDecision(True, current_price, f"Hard Stop-Loss Triggered (${sl_price:,.2f})", True)
            if tp_price > 0 and current_price <= tp_price:
                return ExitDecision(True, current_price, f"Take-Profit Target Achieved (${tp_price:,.2f})", False)

        # 3. RULE B: Time-Decay Window / Max Holding Horizon
        # If position has been held longer than max_holding_seconds without achieving target -> Close
        if holding_duration_secs >= max_holding_secs:
            return ExitDecision(
                True,
                current_price,
                f"Time Decay Limit ({holding_duration_secs/60:.0f} mins >= {max_holding_secs/60:.0f} mins max) reached -> Clean Exit.",
                False
            )

        # 4. RULE C: Dynamic Thesis Invalidation Exit
        ema_20 = float(technical_data.get("ema_20", current_price))
        macd_hist = float(technical_data.get("macd_hist", 0.0))
        rsi = float(technical_data.get("rsi", 50.0))

        if side in ["BUY", "LONG"]:
            # Long thesis invalidated if price breaks below 20 EMA with accelerating negative momentum
            if current_price < ema_20 * 0.985 and macd_hist < -2.0 and rsi < 42.0:
                return ExitDecision(
                    True,
                    current_price,
                    f"Thesis Invalidation: Bullish momentum collapsed below EMA20 (${ema_20:,.2f}) -> Early Risk Cut.",
                    True
                )
        else:
            # Short thesis invalidated if price reclaims 20 EMA with accelerating positive momentum
            if current_price > ema_20 * 1.015 and macd_hist > 2.0 and rsi > 58.0:
                return ExitDecision(
                    True,
                    current_price,
                    f"Thesis Invalidation: Bearish thesis violated, price reclaimed EMA20 (${ema_20:,.2f}) -> Early Risk Cut.",
                    True
                )

        # 5. RULE D: Macro Regime Flip Invalidation
        if current_regime in [MarketRegimeType.LIQUIDITY_SHOCK, MarketRegimeType.PANIC_LIQUIDATION] and side in ["BUY", "LONG"]:
            return ExitDecision(
                True,
                current_price,
                f"Emergency Regime Flip Exit: Market entered [{current_regime.value}] -> Preserving capital.",
                True
            )

        return ExitDecision(False, current_price, "Hold position; active thesis remains valid.", False)

# Global Singleton
adaptive_exit_engine = AdaptiveExitEngine()
