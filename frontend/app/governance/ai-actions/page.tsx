"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from "@/services/api";

export default function HumanInTheLoopGovernancePage() {
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
            <h1 className="text-3xl font-bold text-white tracking-tight">Human-in-the-Loop AI Action Approval Gate</h1>
            <p className="text-gray-400 mt-1">Review AI recommendations with supporting evidence, rationale, &amp; rollback plans.</p>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
              <div>
                <span className="font-mono text-xs text-amber-400 font-bold">ACTION_REQUEST: ACT_LIVE_DEPLOY_01</span>
                <h3 className="text-lg font-bold text-white mt-1">Promote alpha_momentum_v12 from SHADOW to LIVE</h3>
                <p className="text-xs text-gray-400">Evidence: 88% Robustness, Out-of-Sample Sharpe 2.18, 0 Rejections</p>
              </div>
              <div className="flex space-x-2">
                <button className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1 rounded text-xs font-bold">Approve Action</button>
                <button className="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-xs font-bold">Reject</button>
              </div>
            </div>
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
