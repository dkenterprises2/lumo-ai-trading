import time
from typing import Dict, Any, List, Optional

class ServiceRegistry:
    """Lightweight Microservice Discovery & Instance Registry."""

    def __init__(self):
        self._services: Dict[str, List[Dict[str, Any]]] = {
            "api-gateway": [{"id": "api-gw-1", "host": "10.0.1.10", "port": 8000, "last_heartbeat": time.time(), "status": "UP"}],
            "trading-service": [{"id": "trade-svc-1", "host": "10.0.1.11", "port": 8001, "last_heartbeat": time.time(), "status": "UP"}],
            "execution-service": [{"id": "exec-svc-1", "host": "10.0.1.12", "port": 8002, "last_heartbeat": time.time(), "status": "UP"}],
            "ai-inference-service": [{"id": "ai-svc-1", "host": "10.0.1.13", "port": 8003, "last_heartbeat": time.time(), "status": "UP"}],
            "websocket-gateway": [{"id": "ws-gw-1", "host": "10.0.1.14", "port": 8004, "last_heartbeat": time.time(), "status": "UP"}]
        }

    def register_service(self, service_name: str, instance_id: str, host: str, port: int) -> Dict[str, Any]:
        """Register service instance."""
        if service_name not in self._services:
            self._services[service_name] = []
        inst = {
            "id": instance_id,
            "host": host,
            "port": port,
            "last_heartbeat": time.time(),
            "status": "UP"
        }
        self._services[service_name].append(inst)
        return inst

    def renew_heartbeat(self, service_name: str, instance_id: str) -> bool:
        """Renew instance heartbeat."""
        if service_name in self._services:
            for inst in self._services[service_name]:
                if inst["id"] == instance_id:
                    inst["last_heartbeat"] = time.time()
                    inst["status"] = "UP"
                    return True
        return False

    def evict_stale_services(self, max_stale_seconds: int = 30) -> int:
        """Evict instances with stale heartbeats."""
        evicted = 0
        now = time.time()
        for name in list(self._services.keys()):
            valid = []
            for inst in self._services[name]:
                if now - inst["last_heartbeat"] <= max_stale_seconds:
                    valid.append(inst)
                else:
                    evicted += 1
            self._services[name] = valid
        return evicted

    def list_services(self) -> Dict[str, List[Dict[str, Any]]]:
        return self._services

service_registry = ServiceRegistry()
