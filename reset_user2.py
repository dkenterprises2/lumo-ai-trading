import asyncio
from trader import trader_manager

async def main():
    t = await trader_manager.get_trader_for_user(2)
    res = await t.reset_paper_account_async(10000.0)
    print("Reset result:", res)
    print("New USDT balance for User 2:", t.usdt_balance)

if __name__ == "__main__":
    asyncio.run(main())
