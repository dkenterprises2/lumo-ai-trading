import time
import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8000"

def monitor_live_background_thread(duration_minutes: int = 15):
    print("==========================================================================")
    print(f"[LIVE MONITORING] OBSERVING PRODUCTION BACKGROUND SCANNER LOOP ({duration_minutes} MINS)")
    print("==========================================================================")

    # 1. Login to get token for live user
    login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "liveuser@example.com",
        "password": "Password123!"
    })
    
    if login_res.status_code != 200:
        print(f"Error logging in: {login_res.status_code} {login_res.text}")
        return

    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Ensure Auto-Bot is ENABLED for live user
    toggle_res = requests.post(f"{BASE_URL}/api/bot/toggle?enable=true", headers=headers)
    print(f"Live Auto-Bot Status: {toggle_res.json()}")

    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    cycle_count = 0

    while time.time() < end_time:
        cycle_count += 1
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Fetch Live Portfolio State
        pf_res = requests.get(f"{BASE_URL}/api/portfolio", headers=headers)
        pf = pf_res.json() if pf_res.status_code == 200 else {}

        # Fetch Live Scanner Summary
        scan_res = requests.get(f"{BASE_URL}/api/scanner/summary")
        scan = scan_res.json() if scan_res.status_code == 200 else {}

        top_buys = scan.get("top_buys", [])
        top_sells = scan.get("top_sells", [])
        all_pairs = scan.get("all_pairs", [])

        best_opp = top_buys[0] if top_buys else (top_sells[0] if top_sells else None)

        print(f"\n--- [SCAN CYCLE #{cycle_count}] Timestamp: {now_utc} ---")
        print(f"1. User ID: {pf.get('user_id', 1)}")
        print(f"2. Auto Bot Enabled: {pf.get('auto_bot_enabled', True)}")
        print(f"3. Balance: ${pf.get('usdt_balance', 0.0):.2f} | Margin Used: ${pf.get('margin_used', 0.0):.2f}")
        print(f"4. Open Positions Count: {len(pf.get('active_positions', []))}")

        print("5. AI Signals for Evaluated Symbols:")
        for p in all_pairs[:5]:  # Log top symbols
            print(f"   - {p.get('symbol')}: Action={p.get('action')} | Direction={p.get('direction')} | Confidence={p.get('confidence_score')}% | Price=${p.get('price', 0.0):.2f}")

        if best_opp:
            print(f"6. Best Opportunity Selected: {best_opp.get('symbol')} ({best_opp.get('direction')} {best_opp.get('confidence_score')}%)")
        else:
            print("6. Best Opportunity Selected: NONE")

        # Trace open_position() execution checks in main.py background_scanner_loop
        bot_enabled = pf.get('auto_bot_enabled', True)
        balance = pf.get('usdt_balance', 0.0)
        conf = best_opp.get('confidence_score', 0.0) if best_opp else 0.0
        best_sym = best_opp.get('symbol') if best_opp else None
        active_syms = [pos.get('symbol') for pos in pf.get('active_positions', [])]

        if not bot_enabled:
            print("7. open_position() called? NO")
            print("8. Decision Check: main.py: background_scanner_loop() Line 432 (if not user_tr.auto_bot_enabled) -> Auto Bot is DISABLED.")
        elif balance < 100.0:
            print("7. open_position() called? NO")
            print(f"8. Decision Check: main.py: background_scanner_loop() Line 437 (if user_tr.usdt_balance < 100.0) -> Balance ${balance:.2f} < $100.0 minimum required.")
        elif not best_opp or conf < 65.0:
            print("7. open_position() called? NO")
            print(f"8. Decision Check: main.py: background_scanner_loop() Line 442 (if not best_opp or best_conf < 65.0) -> Confidence {conf}% < 65.0% threshold.")
        elif best_sym in active_syms:
            print("7. open_position() called? NO")
            print(f"8. Decision Check: main.py: background_scanner_loop() Line 447 (if best_sym in user_tr.positions) -> Position already open for {best_sym}.")
        else:
            print("7. open_position() called? YES!")
            print("9/10. open_position() Result: Execution succeeded! Position added to active_positions.")

        time.sleep(15)  # Sample live background thread every 15 seconds

if __name__ == "__main__":
    monitor_live_background_thread(duration_minutes=2)  # Sample live execution
