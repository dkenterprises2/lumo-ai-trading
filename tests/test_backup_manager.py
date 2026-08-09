import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.infrastructure.backup_manager import backup_manager

def test_backup_manager_creation():
    snapshot = backup_manager.create_backup()
    assert snapshot["status"] == "COMPLETED"
    assert snapshot["size_mb"] > 0

    backups = backup_manager.list_backups()
    assert len(backups) >= 2
