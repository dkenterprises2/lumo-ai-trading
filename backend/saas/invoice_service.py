from typing import Dict, Any, List

class InvoiceService:
    """Tenant Invoice & Proration Calculation Service."""

    @staticmethod
    def list_invoices(tenant_id: str = "org_acme") -> List[Dict[str, Any]]:
        return [
            {
                "invoice_id": "INV-2026-08-01",
                "tenant_id": tenant_id,
                "amount_usd": 4999.00,
                "status": "PAID",
                "period": "Aug 2026",
                "pdf_url": f"https://api.lumo.trade/billing/invoices/INV-2026-08-01.pdf"
            }
        ]

invoice_service = InvoiceService()
