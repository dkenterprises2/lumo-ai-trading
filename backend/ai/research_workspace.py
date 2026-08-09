import time
from typing import Dict, Any, List, Optional
from backend.core.logger import logger

class ResearchProject:
    """Represents an active quantitative research project container."""
    def __init__(self, project_id: str, title: str, hypothesis: str, target_market: str = "SPOT"):
        self.project_id = project_id
        self.title = title
        self.hypothesis = hypothesis
        self.target_market = target_market
        self.status = "ACTIVE"  # DRAFT, ACTIVE, COMPLETED, ARCHIVED
        self.experiments: List[Dict[str, Any]] = []
        self.notes: List[Dict[str, Any]] = []
        self.created_at = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

class ResearchWorkspaceManager:
    """Research Workspace & Experiment Manager orchestrating projects & experiment timelines."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResearchWorkspaceManager, cls).__new__(cls)
            cls._instance._init_workspace()
        return cls._instance

    def _init_workspace(self):
        # user_id -> project_id -> ResearchProject
        self.user_projects: Dict[int, Dict[str, ResearchProject]] = {}

    def create_project(self, user_id: int, title: str, hypothesis: str, target_market: str = "SPOT") -> Dict[str, Any]:
        p_id = f"PROJ_{int(time.time())}"
        proj = ResearchProject(p_id, title, hypothesis, target_market)
        if user_id not in self.user_projects:
            self.user_projects[user_id] = {}

        self.user_projects[user_id][p_id] = proj
        logger.info(f"[RESEARCH_WORKSPACE] Created project {p_id} ('{title}') for user_id={user_id}.")
        return {
            "project_id": p_id,
            "title": title,
            "hypothesis": hypothesis,
            "target_market": target_market,
            "status": "ACTIVE"
        }

    def list_projects(self, user_id: int) -> List[Dict[str, Any]]:
        if user_id not in self.user_projects:
            self.create_project(user_id, "Multi-Factor Momentum Alpha", "Test EMA20/50 cross with RSI divergence on BTC/USDT", "SPOT")
            self.create_project(user_id, "High-Frequency Volatility Breakout", "Test Donchian channel expansion during high-volatility regimes", "FUTURES")

        return [
            {
                "project_id": p.project_id,
                "title": p.title,
                "hypothesis": p.hypothesis,
                "target_market": p.target_market,
                "status": p.status,
                "created_at": p.created_at
            }
            for p in self.user_projects[user_id].values()
        ]

    def list_dataset_catalog(self) -> List[Dict[str, Any]]:
        """Return catalog of historical & real-time research datasets."""
        return [
            {"dataset_id": "DS_BTC_1H_2024_2026", "name": "Binance BTC/USDT 1h Spot (2024-2026)", "records": 17520, "type": "OHLCV"},
            {"dataset_id": "DS_ETH_15M_2025_2026", "name": "Binance ETH/USDT 15m Spot (2025-2026)", "records": 35040, "type": "OHLCV"},
            {"dataset_id": "DS_SENTIMENT_FEAR_GREED", "name": "Crypto Fear & Greed Index Daily Series", "records": 1095, "type": "SENTIMENT"},
            {"dataset_id": "DS_ORDERBOOK_DEPTH_SAMPLE", "name": "Level-2 Orderbook Imbalance Depth Sample", "records": 500000, "type": "MICROSTRUCTURE"}
        ]

research_workspace_manager = ResearchWorkspaceManager()
