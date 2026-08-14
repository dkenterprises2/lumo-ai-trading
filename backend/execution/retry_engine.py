import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Callable

@dataclass
class RetryAttempt:
    attempt: int
    delay_seconds: float
    is_transient: bool
    error_message: str
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RetryEngine:
    """Exponential Backoff Execution Retry Engine."""

    TRANSIENT_ERRORS = [
        "network_timeout", "rate_limit_exceeded", "429",
        "exchange_unavailable", "503", "websocket_disconnect",
        "connection_reset", "econnreset", "etimedout"
    ]

    def is_transient_error(self, error: Exception) -> bool:
        err_str = str(error).lower()
        return any(t in err_str for t in self.TRANSIENT_ERRORS)

    def calculate_backoff(self, attempt: int, base_delay: float = 1.0, max_attempts: int = 5) -> float:
        """Compute exponential backoff delay (1s, 2s, 4s, 8s...)."""
        if attempt >= max_attempts:
            return -1.0  # Max attempts exhausted
        return base_delay * (2 ** (attempt - 1))
