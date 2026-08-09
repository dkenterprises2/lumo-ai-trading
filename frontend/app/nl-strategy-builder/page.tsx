"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from "@/services/api";

export default function NaturalLanguageStrategyBuilderPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6">
          <div className="border-b border-gray-800 pb-4">
            <h1 className="text-3xl font-bold text-white tracking-tight">Natural Language Strategy Builder</h1>
            <p className="text-gray-400 mt-1">Transform plain-English trading prompts into executable DSL specifications &amp; backtests.</p>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
            <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
              <span className="text-xs text-gray-400 font-medium">Natural Language Input Prompt</span>
              <p className="text-sm text-indigo-300 font-mono mt-1">"Create a BTC trend-following strategy using 20-day momentum and ATR-based stops at 2.0 ATR."</p>
            </div>
            <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
              <span className="text-xs text-gray-400 font-medium">Generated Strategy DSL</span>
              <pre className="text-xs text-emerald-400 font-mono mt-1">strategy_btc_momentum_v1 = MomentumStrategy(symbol='BTCUSDT', lookback=20, stop_loss_atr=2.0)</pre>
            </div>
            <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-xs font-bold">Submit to Backtest &amp; Research</button>
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
