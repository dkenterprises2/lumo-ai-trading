import sys
import os
sys.path.insert(0, os.path.abspath("."))

from trader import PaperTrader

def run_candidate_selection(user_trader, scanner_results, current_prices):
    top_buys = sorted([s for s in scanner_results if "BUY" in s['action']], key=lambda x: x['confidence_score'], reverse=True)
    top_sells = sorted([s for s in scanner_results if "SELL" in s['action']], key=lambda x: x['confidence_score'], reverse=True)

    if not user_trader.auto_bot_enabled:
        return "DISABLED"

    if user_trader.usdt_balance < 100.0:
        return "LOW_BALANCE"

    # Combine & deduplicate candidates while preserving confidence ranking
    all_candidates = top_buys + top_sells
    candidates = sorted(all_candidates, key=lambda x: x['confidence_score'], reverse=True)

    seen_symbols = set()
    trades_opened = 0

    for idx, cand in enumerate(candidates, 1):
        sym = cand['symbol']
        conf = cand['confidence_score']
        direction = cand['direction']

        if sym in seen_symbols:
            continue
        seen_symbols.add(sym)

        if conf < 65.0:
            print(f"  [CANDIDATE #{idx}] Symbol={sym} | Confidence={conf}% | Decision=SKIPPED | Reason=Below Threshold")
            continue

        if sym in user_trader.positions:
            print(f"  [CANDIDATE #{idx}] Symbol={sym} | Confidence={conf}% | Decision=SKIPPED | Reason=Already Open")
            continue

        if direction not in ["LONG", "SHORT"]:
            print(f"  [CANDIDATE #{idx}] Symbol={sym} | Confidence={conf}% | Decision=SKIPPED | Reason=Invalid Direction")
            continue

        print(f"  [CANDIDATE #{idx}] Symbol={sym} | Confidence={conf}% | Decision=PASSED")

        alloc = min(1500.0, user_trader.usdt_balance * 0.20)
        price = current_prices.get(sym, 100.0)

        # Risk parameters
        sl_price = price * 0.90 if direction == "LONG" else price * 1.10
        tp_price = price * 1.10 if direction == "LONG" else price * 0.90

        res = user_trader.open_position(
            symbol=sym,
            side=direction,
            price=price,
            allocation_usd=alloc,
            stop_loss_price=sl_price,
            take_profit_price=tp_price,
            leverage=1
        )


        if res.get("status") == "success":
            print(f"  [POSITION] Symbol={sym} | OPENED SUCCESSFULLY")
            trades_opened += 1
            break
        else:
            print(f"  [POSITION] Symbol={sym} | REJECTED BY RISK MANAGER | Message={res.get('message')}")
            continue

    return trades_opened

print("=== REGRESSION SUITE VERIFICATION ===")

# Test 1: Highest candidate already open -> Second candidate opens
print("\n--- TEST 1: Highest candidate already open ---")
trader1 = PaperTrader(user_id=101, initial_balance=10000.0)
trader1.auto_bot_enabled = True
trader1.positions["BTC/USDT"] = {"symbol": "BTC/USDT", "side": "LONG", "size": 0.1, "entry_price": 64000.0, "margin_usd": 1000.0}

scanner1 = [
    {"symbol": "BTC/USDT", "direction": "LONG", "confidence_score": 85.0, "action": "BUY"},
    {"symbol": "ETH/USDT", "direction": "LONG", "confidence_score": 75.0, "action": "BUY"}
]
prices1 = {"BTC/USDT": 65000.0, "ETH/USDT": 3500.0}
res1 = run_candidate_selection(trader1, scanner1, prices1)
assert res1 == 1, f"Expected 1 trade, got {res1}"
assert "ETH/USDT" in trader1.positions, "ETH/USDT position should be open!"
print("TEST 1 PASSED: Second candidate opened successfully.")

# Test 2: Highest candidate fails risk manager -> Second candidate opens
print("\n--- TEST 2: Highest candidate fails risk manager (e.g. invalid SL) ---")
trader2 = PaperTrader(user_id=102, initial_balance=10000.0)
trader2.auto_bot_enabled = True
# Modify open_position behavior for BTC to simulate risk manager error
old_open_pos = trader2.open_position
def mock_open_pos(symbol, side, price, allocation_usd, stop_loss_price, take_profit_price, leverage=1, **kwargs):
    if symbol == "BTC/USDT":
        return {"status": "error", "message": "Risk Manager: Capped allocation exceeded"}
    return old_open_pos(symbol, side, price, allocation_usd, stop_loss_price, take_profit_price, leverage, **kwargs)

trader2.open_position = mock_open_pos

res2 = run_candidate_selection(trader2, scanner1, prices1)
assert res2 == 1, f"Expected 1 trade, got {res2}"
assert "ETH/USDT" in trader2.positions, "ETH/USDT should be opened after BTC rejection!"
print("TEST 2 PASSED: Continued to second candidate after risk manager rejection.")

# Test 3: Every candidate rejected -> No trade
print("\n--- TEST 3: Every candidate rejected ---")
trader3 = PaperTrader(user_id=103, initial_balance=10000.0)
trader3.auto_bot_enabled = True
scanner3 = [
    {"symbol": "BTC/USDT", "direction": "LONG", "confidence_score": 50.0, "action": "BUY"}, # below 65%
    {"symbol": "ETH/USDT", "direction": "LONG", "confidence_score": 60.0, "action": "BUY"}  # below 65%
]
res3 = run_candidate_selection(trader3, scanner3, prices1)
assert res3 == 0, f"Expected 0 trades, got {res3}"
print("TEST 3 PASSED: No trades opened when all candidates are below confidence threshold.")

# Test 4: Duplicate symbol appears -> Evaluated only once
print("\n--- TEST 4: Duplicate symbol appears ---")
trader4 = PaperTrader(user_id=104, initial_balance=10000.0)
trader4.auto_bot_enabled = True
scanner4 = [
    {"symbol": "ETH/USDT", "direction": "LONG", "confidence_score": 80.0, "action": "BUY"},
    {"symbol": "ETH/USDT", "direction": "SHORT", "confidence_score": 70.0, "action": "SELL"}
]
res4 = run_candidate_selection(trader4, scanner4, prices1)
assert res4 == 1, f"Expected 1 trade, got {res4}"
assert len(trader4.positions) == 1, "Only 1 position should exist!"
print("TEST 4 PASSED: Duplicate symbol evaluated only once.")

# Test 5: Loop stops immediately after 1 successful trade
print("\n--- TEST 5: Loop stops immediately after 1 successful trade ---")
trader5 = PaperTrader(user_id=105, initial_balance=10000.0)
trader5.auto_bot_enabled = True
scanner5 = [
    {"symbol": "BTC/USDT", "direction": "LONG", "confidence_score": 85.0, "action": "BUY"},
    {"symbol": "ETH/USDT", "direction": "LONG", "confidence_score": 75.0, "action": "BUY"}
]
res5 = run_candidate_selection(trader5, scanner5, prices1)
assert res5 == 1, f"Expected 1 trade, got {res5}"
assert len(trader5.positions) == 1, "Should open exactly 1 trade!"
print("TEST 5 PASSED: Loop stopped immediately after 1 successful trade.")

print("\nALL 5 REGRESSION TESTS PASSED CLEANLY!")
