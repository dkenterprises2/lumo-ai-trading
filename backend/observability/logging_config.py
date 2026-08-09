import json
import time
import uuid
from typing import Dict, Any

class StructuredJsonLogger:
    """Structured JSON Logger with Correlation IDs."""

    @staticmethod
    def format_log(level: str, message: str, correlation_id: str = None, extra: Dict[str, Any] = None) -> str:
        """Format structured log JSON payload."""
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": level.upper(),
            "service": "lumo-trading-backend",
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "message": message,
            "extra": extra or {}
        }
        return json.dumps(payload)

structured_logger = StructuredJsonLogger()
