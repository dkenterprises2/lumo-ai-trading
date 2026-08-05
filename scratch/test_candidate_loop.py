import sys
import os
sys.path.insert(0, os.path.abspath("."))

from trader import PaperTrader

# Create dummy scanner results representing the user's scenario
top_buys = [
    {"symbol": "BTC/USDT", "direction": "LONG", "confidence_score": 85.0, "action": "BUY"},
    {"symbol": "ETH/USDT", "direction": "LONG", "confidence_score": 75.0, "action": "BUY"}
]
top_sells = [
    {"symbol": "XRP/USDT", "direction": "SHORT", "confidence_score": 73.0, "action": "SELL"},
    {"symbol": "ADA/USDT", "direction": "SHORT", "confidence_score": 73.0, "action": "SELL"}
]

current_prices = {
    "BTC/USDT": 65000.0,
    "ETH/USDT": 3500.0,
    "XRP/USDT": 0.55,
    "ADA/USDT": 0.40
}

# User already has BTC/USDT open
user_trader = PaperTrader(user_id=999, initial_balance=10000.0)


user_trader.auto_bot_enabled = True
user_trader.positions["BTC/USDT"] = {"symbol": "BTC/USDT", "side": "LONG", "size": 0.1, "entry_price": 64000.0, "margin_usd": 1000.0}


print("=== OLD ALGORITHM (SINGLE CANDIDATE ONLY) ===")
best_opp = top_buys[0] if top_buys else (top_sells[0] if top_sells else None)
best_sym = best_opp['symbol'] if best_opp else "NONE"

print(f"Selected Best Candidate: {best_sym}")
if best_sym in user_trader.positions:
    print(f"[SKIPPED] Position already open for {best_sym}. Terminating scan cycle!")
    print("Result: 0 trades opened. XRP/USDT and ADA/USDT ignored!")

print("\n=== NEW ALGORITHM (ITERATE RANKED CANDIDATES) ===")
candidates = sorted(top_buys + top_sells, key=lambda x: x['confidence_score'], reverse=True)
trade_executed = False

for candidate in candidates:
    sym = candidate['symbol']
    conf = candidate['confidence_score']
    direction = candidate['direction']
    
    print(f"Evaluating Candidate: Symbol={sym} | Direction={direction} | Confidence={conf}%")
    
    if conf < 65.0:
        print(f"  -> Skipped: Confidence {conf}% below 65%")
        continue

    if sym in user_trader.positions:
        print(f"  -> Skipped: Position already open for {sym}")
        continue

    print(f"  -> MATCH FOUND! Opening position for {sym}...")
    res = user_trader.open_position(
        symbol=sym,
        side=direction,
        price=current_prices[sym],
        allocation_usd=1000.0,
        leverage=1,
        stop_loss_price=3000.0,
        take_profit_price=4000.0
    )

    print(f"  -> open_position result: {res}")
    if res.get("status") == "success":
        trade_executed = True
        break

print(f"Final Open Positions Count: {len(user_trader.positions)} ({list(user_trader.positions.keys())})")
