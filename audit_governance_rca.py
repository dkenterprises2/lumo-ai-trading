import asyncio
import json
import sqlite3
from trader import trader_manager
from backend.ai_copilot.investigation.rca_service import trade_rca_service
from backend.learning.strategy_weight_loader import strategy_weight_loader
from backend.learning.learning_governance import learning_governance
from backend.database.session import AsyncSessionLocal
from backend.models.domain import ActiveStrategyWeights, TradeModel, PositionModel
from sqlalchemy import select

async def main():
    print("=== 1. AI GOVERNANCE & MODEL AUDIT ===")
    async with AsyncSessionLocal() as session:
        # Check active weights table
        res = await session.execute(select(ActiveStrategyWeights))
        weights = res.scalars().all()
        print(f"ActiveStrategyWeights rows in DB: {len(weights)}")
        for w in weights:
            print(f"  Version: {w.version}, Strategy: {w.strategy_name}, Regime: {w.market_regime}, Active: {w.is_active}, DeployedBy: {w.deployed_by}")
        
    approvals = await learning_governance.get_approvals(limit=10)
    print(f"Governance Approvals count: {len(approvals)}")
    print(f"Version history count: {len(await strategy_weight_loader.get_version_history('AI_HYBRID'))}")

    print("\n=== 2. TRADE RCA & TRADES AUDIT ===")
    for uid in [1, 2]:
        t = await trader_manager.get_trader_for_user(uid)
        print(f"\n--- User ID {uid} Trader History ---")
        print(f"trade_history count in memory: {len(getattr(t, 'trade_history', []))}")
        rca_trades = await trade_rca_service.list_recent_trades(user_id=uid, limit=20)
        print(f"RCA list_recent_trades count: {len(rca_trades)}")
        for rt in rca_trades[:5]:
            print("  ", rt)

    print("\n=== 3. SQLITE TRADES TABLE ROWS ===")
    conn = sqlite3.connect('lumo_trading.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, symbol, side, entry_price, exit_price, pnl_usd, pnl_pct, close_reason, user_id, timestamp, exit_time FROM trades ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    print(f"Total trades in DB table: {len(rows)}")
    for r in rows:
        print("  ", dict(r))
    conn.close()

if __name__ == "__main__":
    asyncio.run(main())
