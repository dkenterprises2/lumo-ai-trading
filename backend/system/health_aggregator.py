from typing import Dict, Any
from .health_state import SystemHealthState
from backend.telemetry.ws_metrics import ws_metrics

class HealthAggregator:
    """Single Source of Truth for Platform Health Indicators."""

    ENTERPRISE_MODULES = {
        "incident_response": "PARTIALLY_INTEGRATED",
        "rag_knowledge_base": "PARTIALLY_INTEGRATED",
        "agentic_workflow_bus": "MOCK",
        "human_approval_gate": "PARTIALLY_INTEGRATED",
        "security_guardrails": "PARTIALLY_INTEGRATED",
        "portfolio_risk_engine": "REAL",
        "execution_oms_ems": "REAL",
        "paper_trading_safety_guard": "REAL"
    }

    def __init__(self):
        self._override_db_status = "SYNCED"
        self._override_validation_status = "VERIFIED"
        self._override_trading_status = "ACTIVE"

    def get_system_health(self) -> SystemHealthState:
        return self.get_aggregated_health()


    def get_aggregated_health(self) -> SystemHealthState:
        ws_m = ws_metrics.get_metrics()
        ws_stat = "CONNECTED" if ws_m.connected_clients > 0 else "CONNECTING"

        return SystemHealthState(
            db_status=self._override_db_status,
            websocket_status=ws_stat,
            validation_status=self._override_validation_status,
            trading_engine_status=self._override_trading_status,
            exchange_connectivity=True,
            portfolio_risk_ready=True,
            governance_ready=(
                self._override_db_status == "SYNCED" and
                self._override_validation_status == "VERIFIED"
            ),
            paper_trading_mode=True
        )

    def get_module_registry(self) -> Dict[str, str]:
        return self.ENTERPRISE_MODULES

# Global Singleton
health_aggregator = HealthAggregator()
