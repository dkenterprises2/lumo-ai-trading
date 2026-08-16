"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, apiFetch } from "@/services/api";
import { Zap, CheckCircle2, Clock, Layers, RefreshCw, ArrowRight } from "lucide-react";

export default function AgenticOrchestrationPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const workflowsQuery = useQuery({
    queryKey: ["agent-workflows"],
    queryFn: async () => {
      const res = await apiFetch("/api/orchestration/workflows");
      if (!res.ok) throw new Error("Failed to fetch agent workflows");
      return res.json();
    },
    refetchInterval: 5000
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const workflows = workflowsQuery.data ?? [];

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6 max-w-7xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                <Zap className="w-7 h-7 text-indigo-400" />
                Agentic Workflow Orchestration
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Real self-learning pipeline workflow status across Research $\rightarrow$ Alpha Factory $\rightarrow$ Risk $\rightarrow$ Governance agents.
              </p>
            </div>
            <button
              onClick={() => workflowsQuery.refetch()}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs px-3 py-2 rounded-xl flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${workflowsQuery.isFetching ? "animate-spin" : ""}`} />
              <span>Refresh Workflows</span>
            </button>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              Active Self-Learning Agent Workflows ({workflows.length})
            </h2>

            {workflows.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs font-mono">
                No active agent workflow runs recorded in database.
              </div>
            ) : (
              <div className="space-y-4">
                {workflows.map((wf: any) => (
                  <div key={wf.workflow_id} className="p-5 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-sm text-indigo-400">{wf.workflow_id}</span>
                        <span className="text-xs text-slate-400">({wf.experiment_id})</span>
                      </div>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold flex items-center gap-1 ${
                        wf.status === "APPROVED_FOR_GOVERNANCE_REVIEW" || wf.status === "VALIDATED"
                          ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-400"
                          : "bg-amber-500/10 border border-amber-500/30 text-amber-400"
                      }`}>
                        {wf.status === "APPROVED_FOR_GOVERNANCE_REVIEW" ? (
                          <CheckCircle2 className="w-3.5 h-3.5" />
                        ) : (
                          <Clock className="w-3.5 h-3.5" />
                        )}
                        {wf.status}
                      </span>
                    </div>

                    {/* Agent Pipeline Visual Flow */}
                    <div className="flex items-center gap-2 py-2 overflow-x-auto">
                      {wf.pipeline?.map((agent: string, idx: number) => {
                        const isCurrent = wf.current_stage === agent;
                        return (
                          <React.Fragment key={agent}>
                            <div className={`px-3 py-1.5 rounded-xl border text-xs font-mono font-bold flex items-center gap-1.5 ${
                              isCurrent
                                ? "bg-indigo-600 text-white border-indigo-400 shadow-md shadow-indigo-500/20"
                                : "bg-slate-900 text-slate-400 border-slate-800"
                            }`}>
                              <span>{agent}</span>
                            </div>
                            {idx < wf.pipeline.length - 1 && (
                              <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                            )}
                          </React.Fragment>
                        );
                      })}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                      <div className="p-3 bg-slate-900 rounded-lg">
                        <div className="text-slate-400">Target Experiment</div>
                        <div className="text-white font-bold text-xs mt-1 truncate">{wf.experiment_id}</div>
                      </div>
                      <div className="p-3 bg-slate-900 rounded-lg">
                        <div className="text-slate-400">Current Agent Stage</div>
                        <div className="text-indigo-400 font-bold text-xs mt-1">{wf.current_stage}</div>
                      </div>
                      <div className="p-3 bg-slate-900 rounded-lg">
                        <div className="text-slate-400">Candidate Sharpe</div>
                        <div className="text-purple-400 font-bold text-xs mt-1">{wf.candidate_sharpe}</div>
                      </div>
                      <div className="p-3 bg-slate-900 rounded-lg">
                        <div className="text-slate-400">Passing Windows</div>
                        <div className="text-emerald-400 font-bold text-xs mt-1">{wf.consecutive_passing_windows} / 3</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
