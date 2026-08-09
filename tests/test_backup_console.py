import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.admin.backup_console import backup_console_manager

def test_backup_console():
    snap = backup_console_manager.create_backup()
    assert snap["backup_id"].startswith("BKP_")

    backups = backup_console_manager.list_backups()
    assert len(backups) >= 2
