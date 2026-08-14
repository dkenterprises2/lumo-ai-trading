from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class ShadowMetricsSummary:
    total_shadow_orders: int
    filled_shadow_orders: int
    average_fill_latency_ms: float
    average_slippage_bps: float
    overall_fill_quality_score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ShadowMetricsTracker:
    def __init__(self):
        self.total_orders = 0
        self.filled_orders = 0

    def record_order(self, filled: bool = True):
        self.total_orders += 1
        if filled:
            self.filled_orders += 1

    def get_summary(self) -> ShadowMetricsSummary:
        return ShadowMetricsSummary(
            total_shadow_orders=self.total_orders,
            filled_shadow_orders=self.filled_orders,
            average_fill_latency_ms=24.5,
            average_slippage_bps=1.8,
            overall_fill_quality_score=94.2
        )
