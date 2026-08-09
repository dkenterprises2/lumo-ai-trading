import uuid
from typing import Dict, Any

class DistributedTracePropagator:
    """OpenTelemetry Context & Trace Correlation ID Propagator."""

    @staticmethod
    def get_or_create_trace_id(headers: Dict[str, str]) -> str:
        return headers.get("X-Trace-Id", f"trace-{uuid.uuid4().hex[:16]}")

trace_propagator = DistributedTracePropagator()
