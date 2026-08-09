import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.saas.tenant_backup_service import tenant_backup_service

def test_tenant_backups():
    bks = tenant_backup_service.list_backups()
    assert len(bks) >= 1
    new_b = tenant_backup_service.create_backup("org_acme")
    assert new_b["status"] == "COMPLETED"
    res = tenant_backup_service.restore_backup(new_b["backup_id"])
    assert res["status"] == "RESTORED_SIMULATED"
