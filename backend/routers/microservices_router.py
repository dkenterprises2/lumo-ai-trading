from fastapi import APIRouter
from backend.discovery.service_registry import service_registry
from backend.discovery.load_balancer import load_balancer
from backend.eventbus.contracts import OrderCreatedEvent, SignalGeneratedEvent

router = APIRouter(tags=["Microservices Architecture & Event Bus"])

@router.get("/api/platform/services")
async def list_microservices():
    return {
        "services": service_registry.list_services()
    }

@router.get("/api/platform/eventbus/status")
async def get_eventbus_status():
    return {
        "event_bus": "KAFKA",
        "fallback_bus": "REDIS_STREAMS",
        "status": "OPERATIONAL",
        "registered_events": [
            "OrderCreatedEvent", "OrderFilledEvent", "PositionOpenedEvent",
            "SignalGeneratedEvent", "RiskAlertEvent", "DriftDetectedEvent"
        ]
    }

@router.get("/api/platform/clusters")
async def get_clusters_status():
    return {
        "kubernetes_namespace": "lumo-microservices",
        "active_deployments": 7,
        "hpa_active": True,
        "hpa_replicas": {"trading-service": 2, "websocket-gateway": 3}
    }
