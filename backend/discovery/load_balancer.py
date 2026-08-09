from typing import Dict, Any, Optional
from backend.discovery.service_registry import service_registry

class RoundRobinLoadBalancer:
    """Health-Aware Round-Robin Load Balancer for Microservice Routing."""

    def __init__(self):
        self._indices: Dict[str, int] = {}

    def select_instance(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Select next healthy instance in round-robin order."""
        services = service_registry.list_services()
        if service_name not in services or not services[service_name]:
            return None

        healthy_instances = [inst for inst in services[service_name] if inst["status"] == "UP"]
        if not healthy_instances:
            return None

        if service_name not in self._indices:
            self._indices[service_name] = 0

        idx = self._indices[service_name] % len(healthy_instances)
        self._indices[service_name] += 1
        return healthy_instances[idx]

load_balancer = RoundRobinLoadBalancer()
