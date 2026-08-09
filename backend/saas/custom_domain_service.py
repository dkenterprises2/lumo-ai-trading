from typing import Dict, Any, List

class CustomDomainService:
    """Custom Domain Mapping & DNS Verification Service."""

    def __init__(self):
        self._domains: List[Dict[str, Any]] = [
            {
                "domain": "trade.acmecapital.com",
                "tenant_id": "org_acme",
                "status": "VERIFIED",
                "dns_cname": "custom.lumo.trade"
            }
        ]

    def list_domains(self) -> List[Dict[str, Any]]:
        return self._domains

    def register_domain(self, domain: str, tenant_id: str = "org_acme") -> Dict[str, Any]:
        item = {
            "domain": domain,
            "tenant_id": tenant_id,
            "status": "PENDING_VERIFICATION",
            "dns_cname": "custom.lumo.trade"
        }
        self._domains.append(item)
        return item

custom_domain_service = CustomDomainService()
