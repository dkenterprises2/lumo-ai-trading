"use client";

import React, { useState, useEffect, useRef } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, apiFetch } from "@/services/api";
import {
  Bot,
  Send,
  Sparkles,
  Shield,
  TrendingUp,
  Activity,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  Zap,
  Layers,
  BookOpen,
  ArrowRight,
  Trash2
} from "lucide-react";

interface ChatMessage {
  id: string;
  sender: "user" | "copilot";
  text: string;
  citations?: string[];
  suggestedQueries?: string[];
  timestamp: string;
}

const DEFAULT_PROMPTS = [
  "Explain my portfolio risk & margin exposure",
  "Analyze my active open positions",
  "How is the crypto market trending today?",
  "What are the top AI scanner opportunities?"
];

export default function EnterpriseAICopilotPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const currentPortfolio = stream.portfolio ?? portfolioQuery.data ?? null;

  // Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome_msg",
      sender: "copilot",
      text: "👋 Welcome to **Lumo AI Institutional Copilot**.\n\nI have real-time visibility into your **portfolio equity, active trades, risk limits, and live market regimes**. How can I assist your trading operations today?",
      citations: ["[Doc-101] Institutional Risk Guidelines", "[AI-Engine] Quantitative Decision Pipeline"],
      suggestedQueries: DEFAULT_PROMPTS,
      timestamp: "Just now"
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Portfolio Assistant Summary Query
  const assistantQuery = useQuery({
    queryKey: ["portfolio-assistant-summary"],
    queryFn: async () => {
      const res = await apiFetch("/api/portfolio-assistant/summary");
      if (!res.ok) return null;
      return res.json();
    },
    refetchInterval: 10000
  });

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSendMessage = async (queryText?: string) => {
    const textToSend = (queryText || inputText).trim();
    if (!textToSend || loading) return;

    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setLoading(true);

    try {
      const historyPayload = messages.slice(-10).map((m) => ({
        role: m.sender === "user" ? "user" : "assistant",
        content: m.text
      }));

      const res = await apiFetch("/api/copilot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: textToSend,
          history: historyPayload
        })
      });

      if (!res.ok) {
        throw new Error(`Copilot backend error (${res.status})`);
      }

      const data = await res.json();
      const copilotMsg: ChatMessage = {
        id: `copilot_${Date.now()}`,
        sender: "copilot",
        text: data.response || "Analysis complete.",
        citations: data.citations || [],
        suggestedQueries: data.suggested_queries || [],
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      };

      setMessages((prev) => [...prev, copilotMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: "copilot",
        text: `⚠️ **Error communicating with AI Copilot**: ${err.message || "Failed to process query."}\n\nPlease verify that the backend server is running.`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: `welcome_${Date.now()}`,
        sender: "copilot",
        text: "🧹 Conversation cleared.\n\nAsk me anything about your **portfolio, trades, risk parameters, or live crypto market opportunities**.",
        suggestedQueries: DEFAULT_PROMPTS,
        timestamp: "Just now"
      }
    ]);
  };

  const assistantData = assistantQuery.data;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header
          portfolio={currentPortfolio}
          newsSentiment={newsQuery.data ?? null}
          latency={stream.latency}
          connectionState={stream.connectionState}
          onToggleBot={(enable) => toggleBot(enable)}
          onSelectStrategy={(s) => setStrategy(s)}
        />

        <main className="space-y-6">
          {/* Header Title Banner */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-600/20 text-indigo-400 border border-indigo-500/30 shadow-lg shadow-indigo-500/10">
                <Sparkles className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
                  <span>Enterprise AI Copilot &amp; Knowledge Assistant</span>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    Live RAG
                  </span>
                </h1>
                <p className="text-xs text-slate-400">
                  Conversational portfolio risk explanations, trade investigations, and institutional intelligence
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleClearChat}
                className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 text-xs font-semibold flex items-center gap-1.5 transition"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear Chat</span>
              </button>
            </div>
          </div>

          {/* Main 2-Column Layout: Chat on Left/Center, Live Risk Summary on Right */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            {/* Left/Center: Interactive Conversational Terminal */}
            <div className="lg:col-span-2 flex flex-col h-[650px] rounded-2xl bg-slate-900/60 border border-slate-800/80 shadow-2xl backdrop-blur-xl overflow-hidden">
              {/* Chat Messages Container */}
              <div className="flex-1 p-5 overflow-y-auto space-y-4 scrollbar-thin scrollbar-thumb-slate-800">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-3 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {msg.sender === "copilot" && (
                      <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shrink-0 shadow-md">
                        <Bot className="h-4 w-4" />
                      </div>
                    )}

                    <div
                      className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed ${
                        msg.sender === "user"
                          ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-600/10"
                          : "bg-slate-950/80 border border-slate-800/90 text-slate-200 shadow-md"
                      }`}
                    >
                      <div className="whitespace-pre-wrap font-sans">{msg.text}</div>

                      {/* Citations */}
                      {msg.citations && msg.citations.length > 0 && (
                        <div className="mt-3 pt-2.5 border-t border-slate-800 flex flex-wrap gap-1.5">
                          {msg.citations.map((cite, i) => (
                            <span
                              key={i}
                              className="px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-700/80 text-[10px] font-mono text-indigo-300 flex items-center gap-1"
                            >
                              <BookOpen className="w-2.5 h-2.5" />
                              <span>{cite}</span>
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Suggested Query Buttons */}
                      {msg.suggestedQueries && msg.suggestedQueries.length > 0 && (
                        <div className="mt-3 pt-2 border-t border-slate-800/60 space-y-1.5">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                            Suggested Queries:
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {msg.suggestedQueries.map((sug, i) => (
                              <button
                                key={i}
                                type="button"
                                onClick={() => handleSendMessage(sug)}
                                className="px-2.5 py-1 rounded-xl bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[11px] font-semibold flex items-center gap-1 transition text-left cursor-pointer"
                              >
                                <span>{sug}</span>
                                <ArrowRight className="w-3 h-3 shrink-0" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="mt-2 text-[10px] text-slate-400 text-right font-mono">{msg.timestamp}</div>
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex gap-3 justify-start items-center">
                    <div className="h-8 w-8 rounded-xl bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-400 shrink-0 animate-pulse">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
                      <RefreshCw className="w-3.5 h-3.5 animate-spin text-indigo-400" />
                      <span>Analyzing portfolio matrices &amp; running quantitative inference...</span>
                    </div>
                  </div>
                )}

                <div ref={chatBottomRef} />
              </div>

              {/* Chat Input Bar */}
              <div className="p-4 border-t border-slate-800/80 bg-slate-950/60">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex gap-2"
                >
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Ask Lumo Copilot anything about portfolio risk, trades, execution shortfall..."
                    disabled={loading}
                    className="flex-1 px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-medium"
                  />
                  <button
                    type="submit"
                    disabled={!inputText.trim() || loading}
                    className="px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-600 to-pink-600 hover:brightness-110 active:scale-[0.98] text-white text-xs font-bold shadow-lg shadow-indigo-500/25 transition disabled:opacity-40 flex items-center gap-2 cursor-pointer"
                  >
                    <span>Send</span>
                    <Send className="w-3.5 h-3.5" />
                  </button>
                </form>
              </div>
            </div>

            {/* Right Column: Live Portfolio Assistant & Risk Metrics Panel */}
            <div className="space-y-4">
              {/* Portfolio Risk Pulse Card */}
              <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 shadow-xl space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
                  <div className="flex items-center gap-2.5">
                    <Shield className="w-5 h-5 text-emerald-400" />
                    <h3 className="font-bold text-sm text-slate-200">Live Portfolio Health</h3>
                  </div>
                  <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Safe Sizing
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>Available USDT Balance:</span>
                    <span className="font-mono font-bold text-cyan-300">
                      ${(assistantData?.usdt_balance ?? currentPortfolio?.usdt_balance ?? 10000).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Margin in Play:</span>
                    <span className="font-mono font-bold text-amber-300">
                      ${(assistantData?.total_margin_usd ?? currentPortfolio?.margin_used ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Total Portfolio Equity:</span>
                    <span className="font-mono font-bold text-emerald-400">
                      ${(assistantData?.total_value_usd ?? currentPortfolio?.total_portfolio_value ?? 10000).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Active Open Positions:</span>
                    <span className="font-mono font-bold text-purple-400">
                      {assistantData?.active_positions_count ?? (Array.isArray(currentPortfolio?.active_positions) ? currentPortfolio.active_positions.length : Object.keys(currentPortfolio?.active_positions || {}).length)} Positions
                    </span>
                  </div>
                </div>

                {/* Recommendations */}
                {assistantData?.recommended_actions && assistantData.recommended_actions.length > 0 && (
                  <div className="pt-2 border-t border-slate-800 space-y-1.5">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Risk Recommendations:
                    </span>
                    {assistantData.recommended_actions.map((rec: string, idx: number) => (
                      <div key={idx} className="p-2 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px] text-slate-300 flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Quick Prompt Helper Card */}
              <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 shadow-xl space-y-3">
                <div className="flex items-center gap-2 text-indigo-400 font-bold text-xs">
                  <Zap className="w-4 h-4" />
                  <span>Quick Intelligence Queries</span>
                </div>
                <div className="space-y-1.5">
                  {DEFAULT_PROMPTS.map((prompt, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => handleSendMessage(prompt)}
                      className="w-full text-left p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-950 border border-slate-800 hover:border-indigo-500/40 text-xs text-slate-300 hover:text-indigo-200 transition flex items-center justify-between group cursor-pointer"
                    >
                      <span>{prompt}</span>
                      <ArrowRight className="w-3 h-3 text-slate-600 group-hover:text-indigo-400 transition" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </main>

        <Footer
          dbSyncStatus={currentPortfolio?.database_sync_status}
          lastValidationTime={currentPortfolio?.last_validation_time}
          connectionState={stream.connectionState}
        />
      </div>
    </div>
  );
}
