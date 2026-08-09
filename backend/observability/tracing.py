import uuid
import time
from typing import Dict, Any, Optional

class OpenTelemetryTracer:
    """OpenTelemetry Distributed Tracing Manager."""

    def __init__(self):
        self.service_name = "lumo-trading-backend"

    def start_span(self, name: str, parent_trace_id: Optional[str] = None) -> Dict[str, Any]:
        """Start OpenTelemetry trace span."""
        trace_id = parent_trace_id or str(uuid.uuid4())
        span_id = str(uuid.uuid4())[:8]
        return {
            "service_name": self.service_name,
            "span_name": name,
            "trace_id": trace_id,
            "span_id": span_id,
            "start_time": time.time(),
            "status": "OK"
        }

opentelemetry_tracer = OpenTelemetryTracer()
