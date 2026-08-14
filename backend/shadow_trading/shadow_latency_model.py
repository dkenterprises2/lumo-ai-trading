import random
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class ShadowLatencyMetrics:
    network_latency_ms: float
    exchange_matching_latency_ms: float
    routing_latency_ms: float
    decision_latency_ms: float
    total_latency_ms: float
    rating: str  # EXCELLENT, GOOD, ACCEPTABLE, DEGRADED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ShadowLatencyModel:
    """Stochastic Latency Simulation & Execution Quality Evaluator."""

    def simulate_latency(
        self,
        base_network_ms: float = 12.0,
        base_matching_ms: float = 5.0,
        base_routing_ms: float = 4.0,
        base_decision_ms: float = 3.0
    ) -> ShadowLatencyMetrics:
        # Add slight stochastic jitter (0.8 - 1.3x)
        net_ms = base_network_ms * random.uniform(0.9, 1.2)
        match_ms = base_matching_ms * random.uniform(0.9, 1.2)
        route_ms = base_routing_ms * random.uniform(0.9, 1.2)
        dec_ms = base_decision_ms * random.uniform(0.9, 1.2)

        total_ms = net_ms + match_ms + route_ms + dec_ms

        if total_ms < 20.0:
            rating = "EXCELLENT"
        elif total_ms <= 50.0:
            rating = "GOOD"
        elif total_ms <= 100.0:
            rating = "ACCEPTABLE"
        else:
            rating = "DEGRADED"

        return ShadowLatencyMetrics(
            network_latency_ms=round(net_ms, 2),
            exchange_matching_latency_ms=round(match_ms, 2),
            routing_latency_ms=round(route_ms, 2),
            decision_latency_ms=round(dec_ms, 2),
            total_latency_ms=round(total_ms, 2),
            rating=rating
        )
