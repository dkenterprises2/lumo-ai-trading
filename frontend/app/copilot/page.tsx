"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from "@/services/api";

export default function EnterpriseAICopilotPage() {
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
            <h1 className="text-3xl font-bold text-white tracking-tight">Enterprise AI Copilot &amp; Knowledge Assistant</h1>
            <p className="text-gray-400 mt-1">Conversational portfolio explanations, trade investigations, &amp; RAG-backed institutional knowledge.</p>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
            <div className="border border-gray-800 p-4 rounded-lg bg-black/40">
              <span className="font-mono text-xs text-indigo-400 font-bold">LUMO COPILOT RESPONSE</span>
              <p className="text-sm text-gray-200 mt-2">
                BTC exposure increased by +4.2% due to <span className="text-indigo-300 font-mono">alpha_momentum_v12</span> execution. Portfolio VaR increased from 2.8% to 3.1%. Average implementation shortfall was 3.4 bps.
              </p>
              <div className="mt-3 flex space-x-2 text-[10px] text-gray-400 font-mono">
                <span className="bg-gray-800 px-2 py-0.5 rounded border border-gray-700">[Doc-101] Institutional Risk Guidelines</span>
                <span className="bg-gray-800 px-2 py-0.5 rounded border border-gray-700">[Doc-204] Phase 21 Feature Store Lineage</span>
              </div>
            </div>
            <div className="flex space-x-2">
              <input type="text" placeholder="Ask Lumo AI Copilot anything about portfolio risk, trades, or execution..." className="flex-1 bg-black/50 border border-gray-800 text-white text-xs px-4 py-2 rounded focus:outline-none focus:border-indigo-500" />
              <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-xs font-bold">Ask Copilot</button>
            </div>
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
