from backend.discovery.service_registry import service_registry

class HeartbeatManager:
    """Heartbeat Renewal & Stale Instance Eviction Manager."""

    @staticmethod
    def send_heartbeat(service_name: str, instance_id: str) -> bool:
        return service_registry.renew_heartbeat(service_name, instance_id)

    @staticmethod
    def run_eviction_pass() -> int:
        return service_registry.evict_stale_services(max_stale_seconds=30)

heartbeat_manager = HeartbeatManager()
