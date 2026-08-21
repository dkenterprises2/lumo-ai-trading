import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

from backend.execution.execution_intent import ExecutionIntent

@dataclass
class ExecutionReceipt:
    """Standardized Result Receipt emitted by all Execution Adapters."""
    receipt_id: str = field(default_factory=lambda: f"RCPT-{uuid.uuid4().hex[:8].upper()}")
    execution_intent_id: str = ""
    status: str = "FILLED"  # FILLED, PARTIALLY_FILLED, REJECTED, DRY_RUN_VALIDATED
    symbol: str = "BTC/USDT"
    side: str = "BUY"
    executed_quantity: float = 0.0
    average_fill_price: float = 0.0
    executed_notional_usd: float = 0.0
    fees_usd: float = 0.0
    slippage_usd: float = 0.0
    execution_latency_ms: float = 0.0
    execution_mode: str = "PAPER"  # PAPER, SHADOW, LIVE, DRY_RUN
    exchange: str = "BINANCE"
    exchange_order_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    raw_exchange_response: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ExecutionAdapter(ABC):
    """Abstract Base Class for all Execution Adapters (Paper, Shadow, Live).
    
    Guarantees that Paper and Live modes consume the EXACT SAME ExecutionIntent object
    and return a standardized ExecutionReceipt.
    """

    @abstractmethod
    def get_adapter_type(self) -> str:
        """Return adapter name (PAPER, SHADOW, LIVE)."""
        pass

    @abstractmethod
    def validate_intent(self, intent: ExecutionIntent) -> Dict[str, Any]:
        """Pre-execution validation (precision, lot size, min notional)."""
        pass

    @abstractmethod
    def execute(self, intent: ExecutionIntent) -> ExecutionReceipt:
        """Execute the order intent."""
        pass

    @abstractmethod
    def dry_run(self, intent: ExecutionIntent) -> ExecutionReceipt:
        """Validate and simulate live order creation without submitting network request."""
        pass
