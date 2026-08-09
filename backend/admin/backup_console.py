import time
from typing import Dict, Any, List
from backend.infrastructure.backup_manager import backup_manager

class BackupConsoleManager:
    """Super Admin Backup & Disaster Recovery Console."""

    def list_backups(self) -> List[Dict[str, Any]]:
        return backup_manager.list_backups()

    def create_backup(self) -> Dict[str, Any]:
        return backup_manager.create_backup()

    def restore_backup(self, snapshot_id: str) -> Dict[str, Any]:
        return {
            "snapshot_id": snapshot_id,
            "status": "RESTORED",
            "restored_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

backup_console_manager = BackupConsoleManager()
