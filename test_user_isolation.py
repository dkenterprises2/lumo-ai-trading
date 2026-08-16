import asyncio
from trader import trader_manager

async def test_multi_user_isolation():
    print("=== TESTING PER-USER SETTING & TOGGLE ISOLATION ===")
    
    # 1. Fetch User 1 and User 2 traders
    t1 = await trader_manager.get_trader_for_user(1)
    t2 = await trader_manager.get_trader_for_user(2)
    
    # 2. Both default to True
    print(f"Initial: User 1 Arbitrage={t1.arbitrage_shadow_enabled}, User 2 Arbitrage={t2.arbitrage_shadow_enabled}")
    assert t1.arbitrage_shadow_enabled is True
    assert t2.arbitrage_shadow_enabled is True
    
    # 3. User 1 disables Arbitrage and Autonomous engine
    t1.arbitrage_shadow_enabled = False
    t1.autonomous_engine_enabled = False
    
    print(f"After User 1 Toggle: User 1 Arbitrage={t1.arbitrage_shadow_enabled} (Disabled)")
    print(f"After User 1 Toggle: User 2 Arbitrage={t2.arbitrage_shadow_enabled} (Still Enabled)")
    print(f"After User 1 Toggle: User 1 Autonomous={t1.autonomous_engine_enabled} (Disabled)")
    print(f"After User 1 Toggle: User 2 Autonomous={t2.autonomous_engine_enabled} (Still Enabled)")
    
    assert t1.arbitrage_shadow_enabled is False
    assert t2.arbitrage_shadow_enabled is True
    assert t1.autonomous_engine_enabled is False
    assert t2.autonomous_engine_enabled is True
    
    # 4. Re-enable for User 1
    t1.arbitrage_shadow_enabled = True
    t1.autonomous_engine_enabled = True
    print(f"Re-enabled for User 1: Arbitrage={t1.arbitrage_shadow_enabled}, Autonomous={t1.autonomous_engine_enabled}")
    
    print("\nSUCCESS: Per-user setting and toggle isolation verified 100%!")

if __name__ == "__main__":
    asyncio.run(test_multi_user_isolation())
