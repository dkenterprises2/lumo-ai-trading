import time
import random
from typing import Dict, Any, List

class TWAPExecutionEngine:
    """Time-Weighted Average Price (TWAP) Order Execution Engine."""

    @staticmethod
    def slice_twap_order(
        total_quantity: float,
        duration_minutes: int = 60,
        interval_seconds: int = 300,
        randomize_slices: bool = True,
        max_deviation_pct: float = 5.0
    ) -> Dict[str, Any]:
        num_slices = max(1, (duration_minutes * 60) // interval_seconds)
        base_qty = total_quantity / num_slices
        slices = []
        accumulated_qty = 0.0

        for i in range(num_slices):
            if i == num_slices - 1:
                slice_qty = round(total_quantity - accumulated_qty, 6)
            else:
                if randomize_slices:
                    dev = random.uniform(-max_deviation_pct, max_deviation_pct) / 100.0
                    slice_qty = round(base_qty * (1.0 + dev), 6)
                else:
                    slice_qty = round(base_qty, 6)
                accumulated_qty += slice_qty

            slices.append({
                "slice_number": i + 1,
                "quantity": slice_qty,
                "scheduled_time_offset_sec": i * interval_seconds
            })

        return {
            "algo": "TWAP",
            "total_quantity": total_quantity,
            "num_slices": len(slices),
            "duration_minutes": duration_minutes,
            "slices": slices
        }

twap_engine = TWAPExecutionEngine()
