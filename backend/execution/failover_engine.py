import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class FailoverEvent:
    order_id: str
    client_order_id: str
    primary_exchange: str
    failover_exchange: str
    reason: str
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class FailoverEngine:
    """Venue Failover & Rerouting Engine."""

    def evaluate_failover(
        self,
        order_id: str,
        client_order_id: str,
        primary_exchange: str,
        available_venues: List[str],
        reason: str = "Primary exchange connection degraded"
    ) -> Optional[FailoverEvent]:
        """Select fallback exchange preserving order intent."""
        primary_upper = primary_exchange.upper()
        candidates = [v for v in available_venues if v.upper() != primary_upper]

        if not candidates:
            return None

        failover_venue = candidates[0]
        return FailoverEvent(
            order_id=order_id,
            client_order_id=client_order_id,
            primary_exchange=primary_upper,
            failover_exchange=failover_venue,
            reason=reason,
            timestamp=time.time()
        )
