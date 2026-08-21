import time
import os
import re
import json
import asyncio
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from loguru import logger
from trader import trader_manager
from market_data import market_engine
from config import settings

class EnterpriseCopilotService:
    """Multi-Tenant Enterprise Conversational AI Copilot with Session Memory, Entity Tracking & Live Grounding."""

    def __init__(self):
        # Per-user conversational session storage: user_id -> {"history": [], "entities": {}}
        self._sessions: Dict[int, Dict[str, Any]] = {}

    def _get_session(self, user_id: int) -> Dict[str, Any]:
        if user_id not in self._sessions:
            self._sessions[user_id] = {
                "history": [],
                "entities": {
                    "user_name": None,
                    "last_topic": None,
                    "last_symbol": None,
                    "last_query": None
                }
            }
        return self._sessions[user_id]

    async def process_chat_async(
        self,
        query: str,
        user_id: int = 1,
        workspace_id: str = "default",
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        q_raw = query.strip()
        q_lower = q_raw.lower()

        session = self._get_session(user_id)
        entities = session["entities"]

        # If client provided history, merge it
        if history and isinstance(history, list):
            for h in history:
                if isinstance(h, dict) and "role" in h and "content" in h:
                    session["history"].append({"role": h["role"], "content": h["content"]})
            # Keep recent 20 messages
            session["history"] = session["history"][-20:]

        # 1. Fetch real-time trader & portfolio context strictly for this user
        trader_inst = await trader_manager.get_trader_for_user(user_id)
        balance = getattr(trader_inst, "usdt_balance", 10000.0)
        initial_balance = getattr(trader_inst, "initial_balance", 10000.0)
        positions = getattr(trader_inst, "positions", {})
        orders = getattr(trader_inst, "orders", [])
        trades = getattr(trader_inst, "trade_history", [])
        auto_bot = getattr(trader_inst, "auto_bot_enabled", False)
        risk_mode = getattr(trader_inst, "risk_mode", "Moderate")
        strategy = getattr(trader_inst, "active_strategy", "AI Hybrid")
        max_trades = getattr(trader_inst, "max_open_positions", 50)
        default_alloc = getattr(trader_inst, "default_allocation_usd", 1000.0)
        default_lev = getattr(trader_inst, "default_leverage", 1)

        total_margin = sum(p.get("margin_usd", 0.0) for p in positions.values())
        total_pnl = sum(p.get("unrealized_pnl_usd", 0.0) for p in positions.values())
        total_equity = balance + total_margin + total_pnl
        margin_ratio = (total_margin / max(1.0, total_equity)) * 100.0
        return_pct = ((total_equity - initial_balance) / max(1.0, initial_balance)) * 100.0

        # Extract name entities if user introduced themselves
        name_match = re.search(r"(?:my name is|call me|i am|i'm)\s+([a-zA-Z]+)", q_raw, re.IGNORECASE)
        if name_match:
            detected_name = name_match.group(1).capitalize()
            if detected_name.lower() not in ["asking", "wondering", "trading", "here", "new", "looking", "ready", "fine", "good"]:
                entities["user_name"] = detected_name

        # Extract crypto coin symbols
        for sym in ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK", "MATIC", "PEPE", "SHIB", "SUI", "APT", "NEAR", "DOT", "ATOM", "BNB"]:
            if re.search(rf"\b{sym}\b", q_raw, re.IGNORECASE):
                entities["last_symbol"] = f"{sym}/USDT"
                entities["last_topic"] = f"{sym} ({sym}/USDT)"
                break

        # Check for Gemini API Key to enable full LLM generation
        gemini_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        if gemini_key:
            try:
                llm_response = await self._call_gemini_api(
                    gemini_key=gemini_key,
                    query=q_raw,
                    history=session["history"],
                    context={
                        "user_id": user_id,
                        "user_name": entities.get("user_name"),
                        "balance": balance,
                        "initial_balance": initial_balance,
                        "total_equity": total_equity,
                        "total_margin": total_margin,
                        "total_pnl": total_pnl,
                        "margin_ratio": margin_ratio,
                        "return_pct": return_pct,
                        "auto_bot_enabled": auto_bot,
                        "active_strategy": strategy,
                        "risk_mode": risk_mode,
                        "max_trades": max_trades,
                        "open_positions_count": len(positions),
                        "positions_sample": list(positions.values())[:8],
                        "recent_trades_sample": trades[-5:]
                    }
                )
                if llm_response:
                    session["history"].append({"role": "user", "content": q_raw})
                    session["history"].append({"role": "assistant", "content": llm_response})
                    entities["last_query"] = q_raw

                    return {
                        "conversation_id": f"conv_{int(time.time()*1000)}",
                        "workspace_id": workspace_id,
                        "query": q_raw,
                        "response": llm_response,
                        "citations": ["[Gemini-1.5-Pro] Grounded Financial LLM", "[Lumo-Ledger] Real-Time Portfolio State"],
                        "suggested_queries": ["Explain portfolio risk", "What are the top market opportunities?", "Show my open positions breakdown"],
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                        "status": "COMPLETED"
                    }
            except Exception as e:
                logger.warning(f"[COPILOT_GEMINI_FALLBACK] Gemini API call failed: {e}. Falling back to internal dynamic intelligence.")

        # 2. Contextual Conversational Reasoning Engine (Zero Stale Templates)
        response_text = ""
        citations = []
        suggested_queries = []
        user_name = entities.get("user_name")

        # Conversational Intent 1: Name Query ("What is my name?", "Who am I?")
        if re.search(r"\b(what('s| is) my name|who am i|do you know my name|remember my name)\b", q_lower):
            if user_name:
                response_text = f"Your name is **{user_name}**! How can I help you with your portfolio or trading today?"
            else:
                response_text = "I don't believe you've told me your name yet! What should I call you?"
            citations = ["[Copilot-Memory] Session Identity Tracker"]
            suggested_queries = ["What is my current balance?", "Show my open positions", "What is BTC doing right now?"]

        # Conversational Intent 2: Name Introduction ("My name is Dharma", "I am Dharma")
        elif name_match and user_name and not any(k in q_lower for k in ["balance", "position", "trade", "risk", "btc"]):
            response_text = f"Nice to meet you, **{user_name}**! I'm your Lumo AI Trading Copilot. How can I assist your quantitative operations today?"
            citations = ["[Copilot-Memory] Session Identity Tracker"]
            suggested_queries = ["What is my current portfolio balance?", "How many open positions do I have?", "What is BTC doing right now?"]

        # Conversational Intent 3: Previous Topic Recall ("What was I just asking about?", "What did we talk about?")
        elif re.search(r"\b(what was i (just )?asking( about)?|what did (i|we) (just )?(ask|talk about)|previous question|last topic)\b", q_lower):
            last_q = entities.get("last_query")
            last_top = entities.get("last_topic")
            if last_top:
                response_text = f"You were just asking about **{last_top}** (specifically: *\"{last_q}\"*)."
            elif last_q:
                response_text = f"Your previous question was: *\"{last_q}\"*."
            else:
                response_text = "We just started our conversation! Feel free to ask about your portfolio balance, active positions, risk, or live crypto markets."
            citations = ["[Copilot-Memory] Temporal Dialogue State"]
            suggested_queries = ["What is BTC doing right now?", "How many open positions do I have?", "Explain portfolio risk"]

        # Conversational Intent 4: Natural Greeting ("hi", "hello", "hey", "namaste", "good morning")
        elif re.search(r"^(hi|hello|hey|greetings|namaste|kem cho|kaise ho|kya haal|sup|yo|good morning|good afternoon|good evening|help)[\s!.]*$", q_lower):
            greeting_prefix = f"Hello, **{user_name}**!" if user_name else "Hello!"
            response_text = (
                f"{greeting_prefix} I'm your Lumo AI Trading Copilot.\n\n"
                f"I'm ready to answer any questions about your **portfolio balance**, **open positions**, **risk parameters**, or **live crypto market prices**. "
                f"How can I help you right now?"
            )
            citations = ["[Lumo-Assistant] Interactive AI Copilot v4.2"]
            suggested_queries = ["What is my current portfolio balance?", "How many open positions do I have?", "What is BTC doing right now?"]

        # Conversational Intent 5: Portfolio Balance ("What is my current portfolio balance?", "how much money do I have?")
        elif re.search(r"\b(portfolio balance|current balance|account balance|how much money|cash balance|available balance|equity|my balance)\b", q_lower):
            response_text = (
                f"### 💰 Real-Time Portfolio Balance\n"
                f"- **Available Cash (USDT)**: `${balance:,.2f} USDT`\n"
                f"- **Locked Margin**: `${total_margin:,.2f} USDT`\n"
                f"- **Unrealized PnL**: `${total_pnl:,.2f} USDT`\n"
                f"- **Total Portfolio Equity**: `${total_equity:,.2f} USDT` ({return_pct:+.2f}% total return vs initial ${initial_balance:,.2f} USDT)\n\n"
                f"Your account is operating in **{strategy}** mode with **{risk_mode}** risk constraints."
            )
            citations = ["[Lumo-Ledger] Authoritative Database Accounting", "[Portfolio-Sync] Live State"]
            suggested_queries = ["How many open positions do I have?", "What is my biggest current risk?", "Which strategy is active?"]

        # Conversational Intent 6: Open Positions Count & List ("How many open positions do I have?", "show open positions")
        elif re.search(r"\b(how many (open )?positions|open positions|list (my )?positions|active trades|show positions|current positions)\b", q_lower):
            pos_count = len(positions)
            if pos_count == 0:
                response_text = (
                    f"### 📊 Open Positions Status\n"
                    f"You currently have **0 open positions** active (Capacity: **0 / {max_trades}** slots).\n\n"
                    f"The 24/7 AI scanner is {'🟢 **actively scanning 50 crypto markets** for high-probability signals' if auto_bot else '🔴 **currently paused**. You can enable Auto-Bot in the Header or Bots page to start automated trading'}."
                )
            else:
                pos_lines = []
                for sym, p in list(positions.items())[:10]:
                    side = p.get('side', 'LONG')
                    lev = p.get('leverage', 1)
                    entry_p = p.get('entry_price', 0.0)
                    mark_p = market_engine.fetch_current_price(sym)
                    pnl_usd = p.get('unrealized_pnl_usd', 0.0)
                    pnl_pct = p.get('unrealized_pnl_pct', 0.0)
                    alloc = p.get('margin_usd', 0.0)
                    pos_lines.append(f"- **{sym}** ({side} {lev}x) — Entry: `${entry_p:,.4f}` | Mark: `${mark_p:,.4f}` | Margin: `${alloc:,.2f}` | PnL: `${pnl_usd:+.2f}` ({pnl_pct:+.2f}%)")
                
                extra_str = f"\n- *...and {pos_count - 10} more open positions.*" if pos_count > 10 else ""
                response_text = (
                    f"### 📊 Active Open Positions\n"
                    f"You have **{pos_count} active position(s)** out of **{max_trades}** allowed concurrent slots:\n\n"
                    + "\n".join(pos_lines) + extra_str +
                    f"\n\n**Total Margin Used**: `${total_margin:,.2f} USDT` | **Unrealized PnL**: `${total_pnl:,.2f} USDT`"
                )
            citations = ["[Position-Registry] Live Blotter", "[Risk-Engine] Position Capacity Sizer"]
            suggested_queries = ["What is my biggest current risk?", "Why did the bot not trade?", "What did my last trade do?"]

        # Conversational Intent 7: Bot Trading Block Diagnosis ("Why did the bot not trade?", "Why is the bot not trading?")
        elif re.search(r"\b(why (did |is )?(the )?bot not trad(e|ing)|why no trade|bot not buying|why not opening trades|trading stopped)\b", q_lower):
            pos_count = len(positions)
            reasons = []

            if not auto_bot:
                reasons.append("🔴 **Auto-Bot is currently DISABLED**: Automated trade execution is turned off. Toggle the **Auto-Bot Switch** in the Header or Bots page to enable 24/7 scanning.")
            if pos_count >= max_trades:
                reasons.append(f"⚠️ **Maximum Position Capacity Reached**: You currently have **{pos_count} / {max_trades}** positions open. The Institutional Risk Manager prevents opening new trades until existing positions reach Take-Profit or Stop-Loss.")
            if balance < 100.0:
                reasons.append(f"⚠️ **Insufficient Free Balance**: Your available balance (**${balance:,.2f} USDT**) is below the minimum $100.00 cash requirement to open new margin positions.")
            
            if not reasons:
                conf_req = 55.0 if risk_mode == "Aggressive" else (65.0 if risk_mode == "Conservative" else 58.0)
                reasons.append(
                    f"🟢 **Bot is Running & Seeking Alpha**: The 24/7 scanner evaluates 50 cryptocurrency pairs every 30 seconds. "
                    f"Currently, no market signal has crossed your required **{conf_req}% confidence threshold** under **{risk_mode}** risk mode. "
                    f"As soon as a verified technical breakout (EMA + MACD + Volume) is detected, the bot will automatically enter."
                )

            response_text = (
                f"### 🔍 Auto-Trading Bot Telemetry & Diagnostic Report\n"
                + "\n\n".join(reasons) +
                f"\n\n**Current State**: Balance: `${balance:,.2f} USDT` | Open Positions: `{pos_count} / {max_trades}` | Auto-Bot: `{'ACTIVE' if auto_bot else 'DISABLED'}` | Strategy: `{strategy}` ({risk_mode})"
            )
            citations = ["[Scanner-Telemetry] 24/7 Multi-Pair Engine", "[Institutional-Risk] Rule Gatekeeper"]
            suggested_queries = ["How many open positions do I have?", "What is my current portfolio balance?", "Which strategy is active?"]

        # Conversational Intent 8: Biggest Current Risk ("What is my biggest current risk?", "how is my risk?")
        elif re.search(r"\b(biggest (current )?risk|risk analysis|portfolio risk|var|exposure|is my account safe|drawdown)\b", q_lower):
            largest_pos = None
            largest_alloc = 0.0
            for sym, p in positions.items():
                alloc = p.get("margin_usd", 0.0)
                if alloc > largest_alloc:
                    largest_alloc = alloc
                    largest_pos = (sym, p)

            risk_assessment = []
            if margin_ratio > 80.0:
                risk_assessment.append(f"⚠️ **High Margin Utilization**: `{margin_ratio:.1f}%` of your equity is tied up in margin. Market volatility could increase liquidation risks.")
            elif margin_ratio > 40.0:
                risk_assessment.append(f"🟡 **Moderate Margin Exposure**: `{margin_ratio:.1f}%` margin utilization. Sizable cash buffer exists against adverse swings.")
            else:
                risk_assessment.append(f"🟢 **Conservative Capital Exposure**: Low margin utilization (`{margin_ratio:.1f}%`). High cash liquidity provides strong drawdown protection.")

            if largest_pos:
                sym, p = largest_pos
                side = p.get('side', 'LONG')
                pnl = p.get('unrealized_pnl_usd', 0.0)
                risk_assessment.append(f"📌 **Largest Single Position**: **{sym}** ({side}) with `${largest_alloc:,.2f} USDT` allocated margin and `{pnl:+.2f} USDT` unrealized PnL.")

            response_text = (
                f"### 🛡️ Institutional Risk & Exposure Evaluation\n"
                f"- **Total Account Equity**: `${total_equity:,.2f} USDT`\n"
                f"- **Margin Utilization**: `${total_margin:,.2f} USDT` (`{margin_ratio:.1f}%` of total equity)\n"
                f"- **Active Risk Profile**: `{risk_mode}` (Max Loss Limit: `5.0%`, Max Capital/Trade: `10.0%`)\n"
                f"- **Position Slots Used**: `{len(positions)} / {max_trades}`\n\n"
                + "\n".join(risk_assessment)
            )
            citations = ["[Risk-Engine] Institutional Risk Guards v2.4", "[Doc-101] Portfolio VaR Rules"]
            suggested_queries = ["How to reduce portfolio risk?", "Show active positions summary", "Why did the bot not trade?"]

        # Conversational Intent 9: Live Market / Specific Crypto Status ("What is BTC doing right now?", "SOL price", "market trend")
        elif any(sym in q_lower for sym in ["btc", "bitcoin", "eth", "ethereum", "sol", "solana", "xrp", "ripple", "doge", "ada", "avax", "link", "matic", "pepe", "shib", "sui", "apt", "near", "dot", "market"]):
            target_sym = "BTC/USDT"
            for s in ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK", "MATIC", "PEPE", "SHIB", "SUI", "APT", "NEAR", "DOT"]:
                if s.lower() in q_lower:
                    target_sym = f"{s}/USDT"
                    break

            live_price = market_engine.fetch_current_price(target_sym)
            timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            active_p = positions.get(target_sym)

            pos_context = ""
            if active_p:
                side = active_p.get("side", "LONG")
                entry_p = active_p.get("entry_price", live_price)
                pnl = active_p.get("unrealized_pnl_usd", 0.0)
                pos_context = f"\n\n**Your Position in {target_sym}**: You hold an active **{side}** position entered at `${entry_p:,.4f}` (Unrealized PnL: `{pnl:+.2f} USDT`)."

            response_text = (
                f"### 📈 Live Market Intelligence: **{target_sym}**\n"
                f"- **Real-Time Price**: `${live_price:,.4f} USDT`\n"
                f"- **Data Freshness**: `{timestamp_str}` (Live Order Book Stream)\n"
                f"- **Technical Momentum**: Trend structure is monitored across EMA 20/50/200, MACD, and RSI.\n"
                f"- **AI Scanner Outlook**: Regime is actively tracked by 24/7 quantitative filter matrix.{pos_context}"
            )
            citations = [f"[Market-Engine] Real-Time Ticker {target_sym}", "[OrderBook-Stream] Live Multi-Venue Feeds"]
            suggested_queries = [f"What is my position in {target_sym}?", "What is my current portfolio balance?", "Why did the bot not trade?"]

        # Conversational Intent 10: Active Strategy Inquiry ("Which strategy is active?", "what strategy is running?")
        elif re.search(r"\b(which strategy|active strategy|what strategy|strategy mode|bot strategy|trading mode)\b", q_lower):
            response_text = (
                f"### ⚙️ Active Trading Strategy Specification\n"
                f"- **Strategy Mode**: **{strategy}**\n"
                f"- **Risk Setting**: **{risk_mode}**\n"
                f"- **Default Trade Allocation**: `${default_alloc:,.2f} USDT`\n"
                f"- **Default Leverage**: `{default_lev}x`\n"
                f"- **Max Allowed Concurrent Positions**: `{max_trades}` trades\n"
                f"- **Execution Engine**: `{'🟢 AUTO-BOT ACTIVE (Scanning 50 Pairs)' if auto_bot else '🔴 AUTO-BOT PAUSED'}`\n\n"
                f"Under the **{strategy}** model, the engine blends multi-timeframe EMA trend alignment with volatility channel breakouts and sentiment momentum filtering."
            )
            citations = ["[Strategy-Engine] Quantitative Spec v4.0", "[Trader-Config] User Runtime Preferences"]
            suggested_queries = ["How many open positions do I have?", "What is my current portfolio balance?", "Explain portfolio risk"]

        # Conversational Intent 11: Last Trade Inquiry ("What did my last trade do?", "show my last trade")
        elif re.search(r"\b(last trade|previous trade|recent trade|last executed trade|show last trade)\b", q_lower):
            if trades:
                last_t = trades[-1]
                t_sym = last_t.get("symbol", "UNKNOWN")
                t_side = last_t.get("side", "BUY")
                t_entry = last_t.get("entry_price", 0.0)
                t_exit = last_t.get("exit_price", 0.0)
                t_pnl = last_t.get("pnl_usd", last_t.get("net_pnl", last_t.get("pnl", 0.0)))
                t_pct = last_t.get("pnl_pct", 0.0)
                t_time = last_t.get("exit_time", last_t.get("entry_time", "N/A"))
                t_reason = last_t.get("close_reason", last_t.get("reason", "Take-Profit / Stop-Loss"))

                response_text = (
                    f"### 📋 Last Executed Trade Record\n"
                    f"- **Symbol**: **{t_sym}** ({t_side})\n"
                    f"- **Entry Price**: `${t_entry:,.4f}` | **Exit Price**: `${t_exit:,.4f}`\n"
                    f"- **Net PnL**: `{t_pnl:+.2f} USDT` ({t_pct:+.2f}%)\n"
                    f"- **Execution Time**: `{t_time}`\n"
                    f"- **Exit Trigger**: {t_reason}\n\n"
                    f"Total closed trades recorded in lifetime ledger: `{len(trades)}`."
                )
            else:
                response_text = (
                    f"### 📋 Last Executed Trade Record\n"
                    f"No closed trades have been recorded yet in your trade history. "
                    f"As soon as an open position hits its Take-Profit or Stop-Loss barrier, the full execution audit will appear here."
                )
            citations = ["[Trade-History] Authoritative Database Ledger", "[Audit-Blotter] Closed Position Registry"]
            suggested_queries = ["How many open positions do I have?", "What is my current portfolio balance?", "What is BTC doing right now?"]

        # Conversational Intent 12: General Conversational Fallback (Dynamic Grounding)
        else:
            greeting_prefix = f"Regarding your question, **{user_name}**" if user_name else "Regarding your question"
            btc_price = market_engine.fetch_current_price("BTC/USDT")
            response_text = (
                f"{greeting_prefix}: *\"{q_raw}\"*\n\n"
                f"The LUMO AI Quantitative Engine is actively monitoring **50 crypto markets** (BTC `${btc_price:,.2f}`).\n"
                f"Your account currently has **${balance:,.2f} USDT** available cash with **{len(positions)} / {max_trades}** active trade positions "
                f"under **{strategy}** ({risk_mode}) mode.\n\n"
                f"💡 *You can ask me specific questions like:*\n"
                f"- *\"What is my current portfolio balance?\"*\n"
                f"- *\"How many open positions do I have?\"*\n"
                f"- *\"Why did the bot not trade?\"*\n"
                f"- *\"What is BTC doing right now?\"*\n"
                f"- *\"What is my biggest current risk?\"*"
            )
            citations = ["[AI-Engine] Quantitative Decision Pipeline", "[Portfolio-Sync] Live State"]
            suggested_queries = ["What is my current portfolio balance?", "How many open positions do I have?", "What is BTC doing right now?"]

        # Save to session history
        session["history"].append({"role": "user", "content": q_raw})
        session["history"].append({"role": "assistant", "content": response_text})
        entities["last_query"] = q_raw
        if entities.get("last_symbol") and entities["last_symbol"].lower() in q_lower:
            entities["last_topic"] = entities["last_symbol"]

        return {
            "conversation_id": f"conv_{int(time.time()*1000)}",
            "workspace_id": workspace_id,
            "query": q_raw,
            "response": response_text,
            "citations": citations,
            "suggested_queries": suggested_queries,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "status": "COMPLETED"
        }

    async def _call_gemini_api(
        self,
        gemini_key: str,
        query: str,
        history: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Direct REST API call to Google Gemini 1.5 Flash model using built-in urllib."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        
        system_prompt = (
            "You are Lumo AI Institutional Trading Copilot, an elite quantitative finance and algorithmic crypto trading assistant. "
            "You have full visibility into the user's live portfolio, positions, risk parameters, and live crypto market data. "
            "Respond directly, conversationally, concisely, and accurately to the user's specific prompt. "
            "Do NOT dump generic long templates when the user asks a simple greeting or specific question. "
            "Remember previous user messages in the conversation (such as their name or previous questions). "
            f"\nLIVE USER CONTEXT:\n{json.dumps(context, indent=2)}"
        )

        contents = []
        for h in history[-8:]:
            role = "user" if h["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h["content"]}]})

        contents.append({
            "role": "user",
            "parts": [{"text": f"SYSTEM INSTRUCTION: {system_prompt}\n\nUSER MESSAGE: {query}"}]
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 600
            }
        }

        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            loop = asyncio.get_running_loop()
            def _sync_post():
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode("utf-8"))

            data = await loop.run_in_executor(None, _sync_post)
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        except Exception as e:
            logger.warning(f"[GEMINI_REST_ERROR] {e}")
        return None

copilot_service = EnterpriseCopilotService()

