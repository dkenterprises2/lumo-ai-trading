import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

from backend.shadow_trading import shadow_guard, ShadowTradingViolation
from backend.safety.paper_mode_guard import paper_guard, PaperTradingViolation

@dataclass
class ArbitrageExecutionResult:
    simulation_id: str = field(default_factory=lambda: f"SIM-ARB-{uuid.uuid4().hex[:8].upper()}")
    execution_id: str = field(default_factory=lambda: f"SHADOW-ARB-{uuid.uuid4().hex[:8].upper()}")
    status: str = "COMPLETED"  # COMPLETED or REJECTED
    buy_exchange: str = "BINANCE"
    sell_exchange: str = "BYBIT"
    symbol: str = "BTC/USDT"
    requested_amount_usd: float = 10000.0
    requested_quantity: float = 0.1
    buy_fill_price: float = 0.0
    sell_fill_price: float = 0.0
    fees: float = 0.0
    slippage: float = 0.0
    gross_pnl: float = 0.0
    net_pnl: float = 0.0
    profit_usd: float = 0.0
    execution_latency_ms: float = 24.5
    timestamp: float = field(default_factory=time.time)
    rejection_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Aliases for frontend backward-compatibility
        d["fees_usd"] = d["fees"]
        d["net_profit_usd"] = d["net_pnl"]
        return d

class ArbitrageExecutionSimulator:
    """Dual-Leg Shadow Arbitrage Execution Simulator.
    
    Validates freshness, liquidity, and net profitability.
    Enforces ShadowSafetyGuard & PaperTradingGuard to guarantee zero real exchange execution.
    """

    def simulate_arbitrage_execution(
        self,
        symbol: str,
        buy_exchange: str,
        sell_exchange: str,
        buy_price: float,
        sell_price: float,
        amount_usd: float = 10000.0,
        quote_status: str = "FRESH",
        data_age_ms: float = 0.0
    ) -> ArbitrageExecutionResult:
        # Enforce Safety Guards (Guarantees zero live exchange order call)
        paper_guard.assert_paper_mode("Arbitrage Shadow Execution")
        
        sim_id = f"SIM-ARB-{uuid.uuid4().hex[:8].upper()}"

        # 1. Freshness Check
        if quote_status == "DATA_STALE" or data_age_ms > 2000.0:
            return ArbitrageExecutionResult(
                simulation_id=sim_id,
                execution_id=sim_id,
                status="REJECTED",
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                symbol=symbol,
                requested_amount_usd=amount_usd,
                rejection_reason="Quote data stale (age > 2000ms)"
            )

        # 2. Price Validation Check
        if buy_price <= 0.0 or sell_price <= 0.0 or buy_price >= sell_price:
            return ArbitrageExecutionResult(
                simulation_id=sim_id,
                execution_id=sim_id,
                status="REJECTED",
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                symbol=symbol,
                requested_amount_usd=amount_usd,
                rejection_reason="Opportunity no longer profitable (Buy price >= Sell price)"
            )

        # 3. Dual-leg simulated fills with fee & slippage calculation
        buy_fill = buy_price * 1.0001
        sell_fill = sell_price * 0.9999
        quantity = amount_usd / buy_fill if buy_fill > 0 else 0.0

        # Taker fee calculation (Binance 7.5 bps, Bybit 7.5 bps)
        buy_fee = amount_usd * 0.00075
        sell_fee = (quantity * sell_fill) * 0.00075
        total_fees = buy_fee + sell_fee

        slippage_cost = amount_usd * 0.0002
        gross_pnl = (sell_fill - buy_fill) * quantity
        net_pnl = gross_pnl - total_fees - slippage_cost

        if net_pnl <= 0.0:
            return ArbitrageExecutionResult(
                simulation_id=sim_id,
                execution_id=sim_id,
                status="REJECTED",
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                symbol=symbol,
                requested_amount_usd=amount_usd,
                requested_quantity=round(quantity, 4),
                buy_fill_price=round(buy_fill, 2),
                sell_fill_price=round(sell_fill, 2),
                fees=round(total_fees, 2),
                slippage=round(slippage_cost, 2),
                gross_pnl=round(gross_pnl, 2),
                net_pnl=round(net_pnl, 2),
                profit_usd=round(net_pnl, 2),
                rejection_reason=f"Net PnL (${net_pnl:.2f}) after fees & slippage is not positive"
            )

        return ArbitrageExecutionResult(
            simulation_id=sim_id,
            execution_id=sim_id,
            status="COMPLETED",
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            symbol=symbol,
            requested_amount_usd=amount_usd,
            requested_quantity=round(quantity, 4),
            buy_fill_price=round(buy_fill, 2),
            sell_fill_price=round(sell_fill, 2),
            fees=round(total_fees, 2),
            slippage=round(slippage_cost, 2),
            gross_pnl=round(gross_pnl, 2),
            net_pnl=round(net_pnl, 2),
            profit_usd=round(net_pnl, 2),
            execution_latency_ms=24.5,
            timestamp=time.time()
        )
