"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from "@/services/api";

export default function ExecutiveBriefingsPage() {
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
            <h1 className="text-3xl font-bold text-white tracking-tight">AI-Generated Executive Briefings &amp; Daily Reports</h1>
            <p className="text-gray-400 mt-1">Operational intelligence summaries, P&amp;L attribution, &amp; risk overview for executives.</p>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
            <div className="border border-gray-800 p-4 rounded-lg bg-black/40">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-white">Daily Executive Operational &amp; Risk Briefing</h3>
                <span className="text-xs text-gray-400 font-mono">Date: Today</span>
              </div>
              <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="bg-black/50 p-3 rounded border border-gray-800">
                  <span className="text-gray-400">Net P&amp;L</span>
                  <p className="text-base font-bold text-emerald-400 mt-1">+$142,500 (+2.14%)</p>
                </div>
                <div className="bg-black/50 p-3 rounded border border-gray-800">
                  <span className="text-gray-400">Portfolio VaR</span>
                  <p className="text-base font-bold text-indigo-400 mt-1">3.1% VaR</p>
                </div>
                <div className="bg-black/50 p-3 rounded border border-gray-800">
                  <span className="text-gray-400">System Health</span>
                  <p className="text-base font-bold text-emerald-400 mt-1">100% Uptime</p>
                </div>
              </div>
            </div>
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
