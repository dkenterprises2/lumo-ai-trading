from typing import Dict, Any

class AdaptiveOrderSlicer:
    """Adaptive Dynamic Order Slicing Engine."""

    @staticmethod
    def slice_order(quantity: float, urgency: str = "MEDIUM") -> Dict[str, Any]:
        num_slices = 5 if urgency == "HIGH" else 10
        return {
            "urgency": urgency,
            "quantity": quantity,
            "recommended_slices": num_slices,
            "slice_size": round(quantity / num_slices, 6)
        }

adaptive_slicer = AdaptiveOrderSlicer()
