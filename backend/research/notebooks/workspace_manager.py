from typing import Dict, Any, List

class QuantWorkspaceManager:
    """Collaborative Notebook Workspaces & Code Review Manager."""

    @staticmethod
    def list_workspaces() -> List[Dict[str, Any]]:
        return [
            {"workspace_id": "ws_quant_alpha", "name": "Alpha Discovery Workspace", "collaborators": 4},
            {"workspace_id": "ws_microstructure", "name": "Orderbook Research Lab", "collaborators": 2}
        ]

workspace_manager = QuantWorkspaceManager()
