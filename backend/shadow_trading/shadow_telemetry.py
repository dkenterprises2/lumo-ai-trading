import time
from typing import Dict, Any

class ShadowTelemetry:
    """Formats WebSocket real-time telemetry payloads for Shadow Trading."""

    def format_shadow_update(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": f"shadow_{event_type}",
            "data": payload,
            "timestamp": time.time()
        }
