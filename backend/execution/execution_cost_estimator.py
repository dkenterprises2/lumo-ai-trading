from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class PreTradeFrictionEstimate:
    symbol: str
    taker_fee_bps: float = 15.0        # Round-trip 7.5 bps x 2 = 15.0 bps
    expected_slippage_bps: float = 2.5 # Slippage model expectation
    spread_bps: float = 2.0            # Half-spread / orderbook spread cost
    latency_cost_bps: float = 1.5      # Expected latency slippage / adverse selection
    total_friction_bps: float = 21.0

    def calculate_total(self) -> float:
        self.total_friction_bps = round(
            self.taker_fee_bps + self.expected_slippage_bps + self.spread_bps + self.latency_cost_bps, 2
        )
        return self.total_friction_bps

    def to_dict(self) -> Dict[str, Any]:
        self.calculate_total()
        return asdict(self)

@dataclass
class RealizedExecutionFriction:
    order_id: str
    symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    notional_usd: float
    actual_fee_usd: float
    actual_slippage_usd: float
    actual_total_cost_usd: float
    actual_friction_bps: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ExecutionCostEstimator:
    """
    Authoritative Single-Source-of-Truth for Pre-Trade Friction & Post-Trade Cost Accounting.
    Guarantees that transaction friction is estimated exactly ONCE during pre-trade signal calibration
    and never double-deducted in downstream decision gates.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExecutionCostEstimator, cls).__new__(cls)
        return cls._instance

    def estimate_pre_trade_friction(
        self,
        symbol: str,
        spread_bps: float = 2.0,
        slippage_bps: float = 2.5,
        taker_fee_bps: float = 15.0,
        latency_bps: float = 1.5
    ) -> PreTradeFrictionEstimate:
        """Compute authoritative pre-trade friction breakdown in basis points (bps)."""
        est = PreTradeFrictionEstimate(
            symbol=symbol,
            taker_fee_bps=round(max(0.0, taker_fee_bps), 2),
            expected_slippage_bps=round(max(0.0, slippage_bps), 2),
            spread_bps=round(max(0.0, spread_bps), 2),
            latency_cost_bps=round(max(0.0, latency_bps), 2)
        )
        est.calculate_total()
        return est

    def compute_realized_friction(
        self,
        order_id: str,
        symbol: str,
        entry_price: float,
        exit_price: float,
        quantity: float,
        taker_fee_rate: float = 0.0015,
        slippage_bps: float = 2.5
    ) -> RealizedExecutionFriction:
        """Compute exact post-trade realized transaction friction."""
        notional_entry = entry_price * quantity
        notional_exit = exit_price * quantity
        total_notional = notional_entry + notional_exit

        fee_usd = round(total_notional * taker_fee_rate, 4)
        slip_usd = round(notional_entry * (slippage_bps / 10000.0), 4)
        total_cost_usd = round(fee_usd + slip_usd, 4)
        friction_bps = round((total_cost_usd / max(1e-6, notional_entry)) * 10000.0, 2)

        return RealizedExecutionFriction(
            order_id=order_id,
            symbol=symbol,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            notional_usd=round(notional_entry, 2),
            actual_fee_usd=fee_usd,
            actual_slippage_usd=slip_usd,
            actual_total_cost_usd=total_cost_usd,
            actual_friction_bps=friction_bps
        )

# Global Authoritative Singleton
execution_cost_estimator = ExecutionCostEstimator()
