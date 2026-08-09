from typing import Dict, Any, List

class WorkspaceService:
    """Workspace Isolation & Delegation Service."""

    def __init__(self):
        self._workspaces: List[Dict[str, Any]] = [
            {"workspace_id": "ws_trading", "org_id": "org_acme", "name": "Trading Desk", "status": "ACTIVE"},
            {"workspace_id": "ws_research", "org_id": "org_acme", "name": "Research Lab", "status": "ACTIVE"},
            {"workspace_id": "ws_treasury", "org_id": "org_acme", "name": "Treasury Operations", "status": "ACTIVE"},
            {"workspace_id": "ws_compliance", "org_id": "org_acme", "name": "Compliance Office", "status": "ACTIVE"}
        ]

    def list_workspaces(self, org_id: str = "org_acme") -> List[Dict[str, Any]]:
        return [w for w in self._workspaces if w["org_id"] == org_id]

    def create_workspace(self, org_id: str, name: str) -> Dict[str, Any]:
        ws = {
            "workspace_id": f"ws_{name.lower().replace(' ', '_')}",
            "org_id": org_id,
            "name": name,
            "status": "ACTIVE"
        }
        self._workspaces.append(ws)
        return ws

workspace_service = WorkspaceService()
