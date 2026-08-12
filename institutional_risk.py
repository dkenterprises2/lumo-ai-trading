from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import math
import time

@dataclass
class InstitutionalRiskConfig:
    """Configurable parameters for Institutional Risk Engine 2.0."""
    max_daily_loss_pct: float = 5.0             # Max allowed daily loss % of initial balance (e.g. 5.0%)
    max_daily_loss_usd: float = 500.0           # Max allowed daily loss USD
    max_drawdown_pct: float = 10.0              # Max allowed peak-to-trough drawdown % (e.g. 10.0%)
    max_concurrent_trades: int = 50            # Max allowed concurrent open positions (e.g. 50)

    max_exposure_ratio: float = 50.0            # Max total notional exposure / portfolio value (e.g. 50.0x)
    max_volatility_atr_pct: float = 5.0         # Max ATR % of price allowed for new entry (e.g. 5.0%)
    correlation_filter_enabled: bool = True     # Block opening correlated assets exceeding group limit
    correlation_group_limit: int = 50

    news_blackout_enabled: bool = True          # Pause auto-bot during extreme market panic/greed
    news_blackout_fg_min: float = 15.0          # Fear & Greed < 15 triggers blackout
    news_blackout_fg_max: float = 85.0          # Fear & Greed > 85 triggers blackout
    position_scaling_enabled: bool = True       # Scale allocation down based on drawdown level
    risk_per_trade_pct: float = 2.0             # Default risk per trade % on stop-loss distance
    sl_atr_multiplier: float = 2.0              # ATR multiplier for dynamic Stop Loss
    tp_atr_multiplier: float = 4.0              # ATR multiplier for dynamic Take Profit

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstitutionalRiskConfig":
        valid_keys = {k: v for k, v in data.items() if hasattr(cls, k)}
        return cls(**valid_keys)



class InstitutionalRiskManager:
    """Institutional Risk Management & Circuit Breaker Engine."""

    # High Correlation Asset Groups in Crypto Market (>0.80 correlation)
    CORRELATED_GROUPS = {
        "MAJOR_ALT_LONG": ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT", "LINK/USDT", "DOT/USDT", "MATIC/USDT", "ADA/USDT"],
        "STABLE_COINS": ["USDT/USD", "USDC/USDT"]
    }

    def __init__(self, config: Optional[InstitutionalRiskConfig] = None):
        self.config = config or InstitutionalRiskConfig()

    def evaluate_order_risk(
        self,
        user_trader,
        symbol: str,
        side: str,
        price: float,
        allocation_usd: float,
        leverage: int = 1,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        ta_data: Optional[Dict[str, Any]] = None,
        sentiment_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive Institutional Risk Assessment pipeline evaluating all 10 risk rules."""

        ta_data = ta_data or {}
        sentiment_data = sentiment_data or {}
        summary = user_trader.get_portfolio_summary({symbol: price})


        usdt_bal = user_trader.usdt_balance
        init_bal = user_trader.initial_balance if user_trader.initial_balance > 0 else 10000.0
        portfolio_val = summary.get("total_portfolio_value", usdt_bal)
        daily_pnl_usd = summary.get("daily_pnl_usd", 0.0)
        daily_pnl_pct = (daily_pnl_usd / init_bal) * 100.0

        # Peak Equity & Lifetime Drawdown Calculation
        if not hasattr(user_trader, 'peak_equity') or user_trader.peak_equity < portfolio_val:
            user_trader.peak_equity = max(portfolio_val, init_bal)

        peak_eq = getattr(user_trader, 'peak_equity', portfolio_val)
        drawdown_usd = max(0.0, peak_eq - portfolio_val)
        drawdown_pct = (drawdown_usd / (peak_eq + 1e-9)) * 100.0

        # RULE 1: Maximum Daily Loss Circuit Breaker
        if daily_pnl_pct <= -self.config.max_daily_loss_pct or daily_pnl_usd <= -self.config.max_daily_loss_usd:
            msg = f"[RISK_REJECTION] [DAILY_LOSS_BREACH] Daily PnL ({daily_pnl_pct:.2f}% / ${daily_pnl_usd:.2f}) breached Max Daily Loss Limit (-{self.config.max_daily_loss_pct}% / -${self.config.max_daily_loss_usd}). All trading locked."
            logger.error(msg)
            return {"passed": False, "status": "error", "rule": "MAX_DAILY_LOSS", "message": msg}

        # RULE 2: Maximum Peak-to-Trough Drawdown Limit
        if drawdown_pct >= self.config.max_drawdown_pct:
            msg = f"[RISK_REJECTION] [MAX_DRAWDOWN_BREACH] Current Drawdown ({drawdown_pct:.2f}%) breached Max Drawdown Limit ({self.config.max_drawdown_pct}%). Trading halted."
            logger.error(msg)
            return {"passed": False, "status": "error", "rule": "MAX_DRAWDOWN", "message": msg}

        # RULE 3: Maximum Concurrent Trades Limit
        active_positions = user_trader.positions
        if len(active_positions) >= self.config.max_concurrent_trades and symbol not in active_positions:
            msg = f"[RISK_REJECTION] [CONCURRENT_TRADES_EXCEEDED] Active positions ({len(active_positions)}) reached max concurrent trade limit ({self.config.max_concurrent_trades})."
            logger.warning(msg)
            return {"passed": False, "status": "error", "rule": "MAX_CONCURRENT_TRADES", "message": msg}

        # RULE 4: Maximum Exposure Cap (Notional Ratio)
        current_notional = sum(p.get("notional_val_usd", p.get("amount", 0) * p.get("entry_price", 0)) for p in active_positions.values())
        new_notional = allocation_usd
        total_notional_after = current_notional + new_notional
        exposure_ratio = total_notional_after / (portfolio_val + 1e-9)

        if exposure_ratio > self.config.max_exposure_ratio:
            msg = f"[RISK_REJECTION] [MAX_EXPOSURE_EXCEEDED] Proposed total notional exposure ratio ({exposure_ratio:.2f}x) exceeds max allowed exposure ({self.config.max_exposure_ratio:.2f}x)."
            logger.warning(msg)
            return {"passed": False, "status": "error", "rule": "MAX_EXPOSURE", "message": msg}

        # RULE 5: Correlation Filter
        if self.config.correlation_filter_enabled:
            group1_active = [sym for sym in active_positions if sym in self.CORRELATED_GROUPS["MAJOR_ALT_LONG"]]
            if len(group1_active) >= self.config.correlation_group_limit and symbol in self.CORRELATED_GROUPS["MAJOR_ALT_LONG"]:
                msg = f"[RISK_REJECTION] [CORRELATION_FILTER] Already holding {len(group1_active)} correlated assets ({', '.join(group1_active)}). Blocked {symbol} to prevent correlated risk stacking."
                logger.warning(msg)
                return {"passed": False, "status": "error", "rule": "CORRELATION_FILTER", "message": msg}

        # RULE 6: Volatility Filter (ATR Spike Detection)
        atr = float(ta_data.get("atr", price * 0.02))
        vol_atr_pct = (atr / (price + 1e-9)) * 100.0
        if vol_atr_pct > self.config.max_volatility_atr_pct:
            msg = f"[RISK_REJECTION] [VOLATILITY_FILTER] Market ATR volatility ({vol_atr_pct:.2f}%) exceeds max safe volatility threshold ({self.config.max_volatility_atr_pct:.2f}%)."
            logger.warning(msg)
            return {"passed": False, "status": "error", "rule": "VOLATILITY_FILTER", "message": msg}

        # RULE 7: News Blackout Protection
        if self.config.news_blackout_enabled and sentiment_data:
            fg_val = float(sentiment_data.get("fear_greed", {}).get("value", 50))
            if fg_val <= self.config.news_blackout_fg_min or fg_val >= self.config.news_blackout_fg_max:
                msg = f"[RISK_REJECTION] [NEWS_BLACKOUT] Fear & Greed index ({fg_val}) triggered News Blackout Protection (Min {self.config.news_blackout_fg_min} / Max {self.config.news_blackout_fg_max})."
                logger.warning(msg)
                return {"passed": False, "status": "error", "rule": "NEWS_BLACKOUT", "message": msg}

        # RULE 8 & 10: Position Scaling & Risk Per Trade Sizing
        adjusted_alloc = allocation_usd
        if self.config.position_scaling_enabled:
            if drawdown_pct >= 8.0:
                adjusted_alloc *= 0.50
                logger.info(f"[POSITION_SCALING] High Drawdown ({drawdown_pct:.1f}%). Scaled allocation down 50% to ${adjusted_alloc:.2f}.")
            elif drawdown_pct >= 5.0:
                adjusted_alloc *= 0.75
                logger.info(f"[POSITION_SCALING] Moderate Drawdown ({drawdown_pct:.1f}%). Scaled allocation down 25% to ${adjusted_alloc:.2f}.")

        # RULE 9: Dynamic ATR Stop Loss & Take Profit Computation
        computed_sl = stop_loss_price
        computed_tp = take_profit_price
        if not computed_sl or computed_sl == 0.0 or not computed_tp or computed_tp == 0.0:
            sl_dist = atr * self.config.sl_atr_multiplier
            tp_dist = atr * self.config.tp_atr_multiplier
            if side.upper() == "LONG":
                computed_sl = round(price - sl_dist, 4)
                computed_tp = round(price + tp_dist, 4)
            else:
                computed_sl = round(price + sl_dist, 4)
                computed_tp = round(price - tp_dist, 4)

        # Ensure Risk Per Trade Cap (% of portfolio)
        max_risk_usd = portfolio_val * (self.config.risk_per_trade_pct / 100.0)
        sl_dist_abs = abs(price - computed_sl)
        pos_amount = adjusted_alloc / price
        potential_loss_usd = pos_amount * sl_dist_abs

        if potential_loss_usd > max_risk_usd and sl_dist_abs > 0:
            capped_amount = max_risk_usd / sl_dist_abs
            adjusted_alloc = capped_amount * price
            logger.info(f"[RISK_PER_TRADE_CAP] Potential SL loss ${potential_loss_usd:.2f} > max allowed risk ${max_risk_usd:.2f} ({self.config.risk_per_trade_pct}%). Capped allocation to ${adjusted_alloc:.2f}.")

        return {
            "passed": True,
            "status": "success",
            "adjusted_allocation_usd": round(adjusted_alloc, 2),
            "stop_loss_price": computed_sl,
            "take_profit_price": computed_tp,
            "drawdown_pct": round(drawdown_pct, 2),
            "daily_pnl_pct": round(daily_pnl_pct, 2),
            "exposure_ratio": round(exposure_ratio, 2)
        }

    def get_risk_health_metrics(self, user_trader) -> Dict[str, Any]:
        """Expose institutional risk health dashboard metrics."""
        summary = user_trader.get_portfolio_summary()
        usdt_bal = user_trader.usdt_balance
        init_bal = user_trader.initial_balance if user_trader.initial_balance > 0 else 10000.0
        portfolio_val = summary.get("total_portfolio_value", usdt_bal)

        if not hasattr(user_trader, 'peak_equity') or user_trader.peak_equity < portfolio_val:
            user_trader.peak_equity = max(portfolio_val, init_bal)

        peak_eq = getattr(user_trader, 'peak_equity', portfolio_val)
        drawdown_usd = max(0.0, peak_eq - portfolio_val)
        drawdown_pct = (drawdown_usd / (peak_eq + 1e-9)) * 100.0

        daily_pnl_usd = summary.get("daily_pnl_usd", 0.0)
        daily_pnl_pct = (daily_pnl_usd / init_bal) * 100.0

        active_positions = user_trader.positions
        current_notional = sum(p.get("notional_val_usd", p.get("amount", 0) * p.get("entry_price", 0)) for p in active_positions.values())
        exposure_ratio = current_notional / (portfolio_val + 1e-9)

        daily_loss_breached = daily_pnl_pct <= -self.config.max_daily_loss_pct or daily_pnl_usd <= -self.config.max_daily_loss_usd
        drawdown_breached = drawdown_pct >= self.config.max_drawdown_pct

        return {
            "status": "HEALTHY" if not (daily_loss_breached or drawdown_breached) else "BREACHED",
            "daily_pnl_usd": round(daily_pnl_usd, 2),
            "daily_pnl_pct": round(daily_pnl_pct, 2),
            "max_daily_loss_limit_pct": self.config.max_daily_loss_pct,
            "daily_loss_breached": daily_loss_breached,
            "peak_equity_usd": round(peak_eq, 2),
            "current_drawdown_usd": round(drawdown_usd, 2),
            "current_drawdown_pct": round(drawdown_pct, 2),
            "max_drawdown_limit_pct": self.config.max_drawdown_pct,
            "drawdown_breached": drawdown_breached,
            "active_concurrent_trades": len(active_positions),
            "max_concurrent_trades_limit": self.config.max_concurrent_trades,
            "current_exposure_ratio": round(exposure_ratio, 2),
            "max_exposure_ratio_limit": self.config.max_exposure_ratio,
            "news_blackout_active": False,
            "config": self.config.to_dict()
        }
