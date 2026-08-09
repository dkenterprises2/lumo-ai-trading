"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from "@/services/api";

export default function AgenticOrchestrationPage() {
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
            <h1 className="text-3xl font-bold text-white tracking-tight">Agentic Workflow Orchestration &amp; Coordination Bus</h1>
            <p className="text-gray-400 mt-1">Cross-phase autonomous agent pipeline (Research &rarr; Alpha Factory &rarr; Risk &rarr; Governance).</p>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
              <div>
                <span className="font-mono text-xs text-indigo-400 font-bold">WORKFLOW_ID: WF_AGENT_101</span>
                <h3 className="text-lg font-bold text-white mt-1">AutoML to Shadow Deployment Pipeline</h3>
                <p className="text-xs text-gray-400">Agents: ResearchAgent &rarr; AlphaFactoryAgent &rarr; RiskAgent &rarr; GovernanceAgent</p>
              </div>
              <span className="text-xs bg-amber-950 text-amber-300 border border-amber-700 px-3 py-1 rounded">AWAITING GOVERNANCE</span>
            </div>
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
