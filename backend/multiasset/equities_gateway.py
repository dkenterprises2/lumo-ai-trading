from typing import Dict, Any

class EquitiesGateway:
    """Equities Execution Gateway Abstraction."""

    @staticmethod
    def get_status() -> Dict[str, Any]:
        return {"gateway": "EQUITIES", "status": "CONNECTED_SIMULATED", "venues": ["NASDAQ", "NYSE"]}

equities_gateway = EquitiesGateway()
