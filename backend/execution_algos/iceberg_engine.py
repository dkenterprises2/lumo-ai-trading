from typing import Dict, Any

class IcebergOrderEngine:
    """Iceberg Hidden Reserve & Anti-Detection Order Engine."""

    @staticmethod
    def initialize_iceberg(
        total_quantity: float,
        display_quantity: float
    ) -> Dict[str, Any]:
        hidden_reserve = max(0.0, total_quantity - display_quantity)
        return {
            "algo": "ICEBERG",
            "total_quantity": total_quantity,
            "visible_display_quantity": min(display_quantity, total_quantity),
            "hidden_reserve_quantity": round(hidden_reserve, 6),
            "replenishment_count": 0,
            "status": "ACTIVE"
        }

iceberg_engine = IcebergOrderEngine()
