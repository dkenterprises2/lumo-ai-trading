import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Union

from backend.execution.execution_orchestrator import execution_orchestrator
from backend.portfolio_risk.portfolio_risk_engine import InstitutionalPortfolioRiskEngine

@dataclass
class ExitEvaluationResult:
    should_exit: bool
    trigger_reason: str
    exit_price: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ArbitrageExitEngine:
    """Automated Exit Condition Evaluator for Active Shadow Arbitrage Positions."""

    MAX_HOLDING_TIME_SECONDS = 600.0
    MIN_NET_EDGE_PCT = 0.15
    MAX_QUOTE_AGE_MS = 2000.0

    def evaluate_position_exit(
        self,
        position: Dict[str, Any],
        current_buy_quote: Optional[Any] = None,
        current_sell_quote: Optional[Any] = None,
        kill_switch_halted: bool = False,
        news_hack_detected: bool = False
    ) -> ExitEvaluationResult:
        now = time.time()
        entry_time = position.get("entry_timestamp", now)
        holding_seconds = now - entry_time

        # 1. Kill Switch Trigger
        if kill_switch_halted:
            return ExitEvaluationResult(should_exit=True, trigger_reason="KILL_SWITCH_ACTIVATED")

        # 2. News Hack / Outage Alert
        if news_hack_detected:
            return ExitEvaluationResult(should_exit=True, trigger_reason="NEWS_SECURITY_ALERT")

        # 3. Max Holding Time Expired
        if holding_seconds >= self.MAX_HOLDING_TIME_SECONDS:
            return ExitEvaluationResult(should_exit=True, trigger_reason="MAX_HOLDING_TIME_EXPIRED")

        # Quote validations if live market quotes passed
        if current_buy_quote and current_sell_quote:
            # 4. Stale Quote Check
            max_age = max(getattr(current_buy_quote, 'data_age_ms', 0.0), getattr(current_sell_quote, 'data_age_ms', 0.0))
            if max_age > self.MAX_QUOTE_AGE_MS or getattr(current_buy_quote, 'status', 'FRESH') == 'DATA_STALE':
                return ExitEvaluationResult(should_exit=True, trigger_reason="QUOTE_STALE")

            # 5. Liquidity Deteriorated
            if getattr(current_buy_quote, 'ask_price', 0.0) <= 0.0 or getattr(current_sell_quote, 'bid_price', 0.0) <= 0.0:
                return ExitEvaluationResult(should_exit=True, trigger_reason="LIQUIDITY_DETERIORATED")

            buy_ask = current_buy_quote.ask_price
            sell_bid = current_sell_quote.bid_price
            gross_spread_pct = ((sell_bid - buy_ask) / buy_ask) * 100.0 if buy_ask > 0 else 0.0

            # 6. Spread Convergence
            if gross_spread_pct <= 0.0:
                return ExitEvaluationResult(should_exit=True, trigger_reason="SPREAD_CONVERGED", exit_price=sell_bid)

            # 7. Net Edge Decay
            total_fees_bps = 15.0  # 7.5 bps + 7.5 bps
            net_edge = gross_spread_pct - (total_fees_bps / 100.0)
            if net_edge < self.MIN_NET_EDGE_PCT:
                return ExitEvaluationResult(should_exit=True, trigger_reason="NET_EDGE_DECAYED", exit_price=sell_bid)

        return ExitEvaluationResult(should_exit=False, trigger_reason="NONE")

    def execute_shadow_exit(self, position: Any, reason: str) -> Dict[str, Any]:
        """Route position closing order through OMS/EMS ExecutionOrchestrator."""
        if hasattr(position, "to_dict"):
            pos_dict = position.to_dict()
            position.status = "CLOSED"
            position.exit_timestamp = time.time()
            position.exit_reason = reason
        else:
            pos_dict = position
            position["status"] = "CLOSED"
            position["exit_timestamp"] = time.time()
            position["exit_reason"] = reason

        user_id = pos_dict.get("user_id", "user-p41")
        symbol = pos_dict.get("symbol", "BTC/USDT")
        quantity = pos_dict.get("quantity", 0.1)

        # Unwind buy leg (SELL) & sell leg (BUY) via OMS
        close_buy_leg = execution_orchestrator.submit_order(
            user_id=user_id,
            symbol=symbol,
            side="SELL",
            quantity=quantity,
            exchange=pos_dict.get("buy_exchange", "BINANCE")
        )

        close_sell_leg = execution_orchestrator.submit_order(
            user_id=user_id,
            symbol=symbol,
            side="BUY",
            quantity=quantity,
            exchange=pos_dict.get("sell_exchange", "BYBIT")
        )

        return {
            "status": "success",
            "position_id": pos_dict.get("position_id"),
            "exit_reason": reason,
            "close_buy_leg": close_buy_leg,
            "close_sell_leg": close_sell_leg
        }
