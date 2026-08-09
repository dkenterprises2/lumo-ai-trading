import time
from typing import Dict, Any, List

class OrderReconciliationEngine:
    """Order Reconciliation Engine auditing local orders against exchange orderbooks."""

    @staticmethod
    def audit_orders(local_orders: List[Dict[str, Any]], exchange_orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect discrepancies between local order states and exchange fills."""
        matched = 0
        discrepancies = []
        partial_fills = []

        local_map = {o["order_id"]: o for o in local_orders if "order_id" in o}
        ex_map = {o["order_id"]: o for o in exchange_orders if "order_id" in o}

        for o_id, loc in local_map.items():
            if o_id not in ex_map:
                discrepancies.append({"order_id": o_id, "issue": "ORDER_MISSING_ON_EXCHANGE"})
            else:
                ex = ex_map[o_id]
                loc_status = loc.get("status", "OPEN")
                ex_status = ex.get("status", "OPEN")

                if loc_status != ex_status:
                    discrepancies.append({"order_id": o_id, "issue": "STATUS_MISMATCH", "local": loc_status, "exchange": ex_status})

                if ex.get("filled_amount", 0.0) < loc.get("amount", 0.0) and ex.get("filled_amount", 0.0) > 0:
                    partial_fills.append({"order_id": o_id, "filled": ex["filled_amount"], "total": loc["amount"]})
                else:
                    matched += 1

        return {
            "status": "COMPLETED",
            "matched_orders": matched,
            "discrepancies": discrepancies,
            "partial_fills": partial_fills,
            "audited_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

reconciliation_engine = OrderReconciliationEngine()
