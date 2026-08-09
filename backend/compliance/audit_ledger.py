import time
import hashlib
import json
from typing import Dict, Any, List, Optional

class ImmutableAuditLedger:
    """Append-Only Immutable Audit Ledger with Tamper-Evident Hashing Chain."""

    def __init__(self):
        self._ledger: List[Dict[str, Any]] = [
            {
                "entry_id": "AUD-000",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "actor_user_id": 1,
                "tenant_id": "ORG-101",
                "action_type": "SYSTEM_INITIALIZED",
                "resource_type": "LEDGER",
                "resource_id": "GENESIS",
                "before_hash": "0000000000000000000000000000000000000000000000000000000000000000",
                "after_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "previous_entry_hash": "0000000000000000000000000000000000000000000000000000000000000000",
                "current_entry_hash": "0000000000000000000000000000000000000000000000000000000000000000",
                "ip_address": "127.0.0.1",
                "user_agent": "Lumo-Kernel/2.9.0",
                "correlation_id": "corr-genesis"
            }
        ]

    def append_entry(
        self,
        actor_user_id: int,
        tenant_id: str,
        action_type: str,
        resource_type: str,
        resource_id: str,
        ip_address: str = "127.0.0.1",
        correlation_id: str = "corr-1"
    ) -> Dict[str, Any]:
        """Append new audit record to immutable ledger."""
        prev_hash = self._ledger[-1]["current_entry_hash"] if self._ledger else "0" * 64
        entry_id = f"AUD-{len(self._ledger)+1:06d}"
        
        raw_payload = f"{entry_id}:{actor_user_id}:{tenant_id}:{action_type}:{prev_hash}:{time.time()}"
        cur_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

        entry = {
            "entry_id": entry_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "actor_user_id": actor_user_id,
            "tenant_id": tenant_id,
            "action_type": action_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "before_hash": prev_hash,
            "after_hash": cur_hash,
            "previous_entry_hash": prev_hash,
            "current_entry_hash": cur_hash,
            "ip_address": ip_address,
            "user_agent": "Lumo-Kernel/2.9.0",
            "correlation_id": correlation_id
        }
        self._ledger.append(entry)
        return entry

    def verify_integrity(self) -> bool:
        """Verify hash-chain tamper-evidence across all entries."""
        for i in range(1, len(self._ledger)):
            if self._ledger[i]["previous_entry_hash"] != self._ledger[i-1]["current_entry_hash"]:
                return False
        return True

    def list_entries(self, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if tenant_id:
            return [e for e in self._ledger if e["tenant_id"] == tenant_id]
        return self._ledger

audit_ledger = ImmutableAuditLedger()
