import time
from typing import Dict, Any

def get_service_health(service_name: str) -> Dict[str, Any]:
    return {
        "service": service_name,
        "status": "HEALTHY",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }
