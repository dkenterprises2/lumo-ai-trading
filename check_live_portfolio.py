import asyncio
from trader import trader_manager, PaperTrader
from backend.models.domain import UserModel
from backend.database.session import AsyncSessionLocal
from sqlalchemy import select

async def main():
    print("=== CHECKING ALL USER PAPER TRADING BALANCES ===")
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(UserModel))
        users = res.scalars().all()
        print(f"Total Users in DB: {len(users)}")
        
        for u in users:
            t = await trader_manager.get_trader_for_user(u.id)
            summary = t.get_portfolio_summary({})
            print(f"\n--- User: {u.username} (ID: {u.id}, Role: {u.role}) ---")
            print(f"  Cash / USDT Balance: ${t.usdt_balance:,.2f}")
            print(f"  Initial Balance:     ${t.initial_balance:,.2f}")
            print(f"  Total Equity:        ${summary.get('total_equity', 0):,.2f}")
            print(f"  Margin Used:         ${summary.get('margin_used', 0):,.2f}")
            print(f"  Unrealized PnL:      ${summary.get('unrealized_pnl', 0):,.2f}")
            print(f"  Realized PnL:        ${summary.get('realized_pnl', 0):,.2f}")
            print(f"  Open Positions:      {len(t.positions)}")
            print(f"  Is Balance Negative? {'YES (NEGATIVE)' if t.usdt_balance < 0 or summary.get('total_equity', 0) < 0 else 'NO (POSITIVE / SAFE)'}")

    # Also check default trader (User None / Default guest)
    t_def = trader_manager.get_default_trader()
    await t_def.initialize_and_restore_state()
    def_sum = t_def.get_portfolio_summary({})
    print(f"\n--- Default Guest / Paper Trader ---")
    print(f"  Cash / USDT Balance: ${t_def.usdt_balance:,.2f}")
    print(f"  Initial Balance:     ${t_def.initial_balance:,.2f}")
    print(f"  Total Equity:        ${def_sum.get('total_equity', 0):,.2f}")
    print(f"  Margin Used:         ${def_sum.get('margin_used', 0):,.2f}")
    print(f"  Unrealized PnL:      ${def_sum.get('unrealized_pnl', 0):,.2f}")
    print(f"  Realized PnL:        ${def_sum.get('realized_pnl', 0):,.2f}")
    print(f"  Open Positions:      {len(t_def.positions)}")
    print(f"  Is Balance Negative? {'YES (NEGATIVE)' if t_def.usdt_balance < 0 or def_sum.get('total_equity', 0) < 0 else 'NO (POSITIVE / SAFE)'}")

if __name__ == "__main__":
    asyncio.run(main())
