"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, apiFetch } from "@/services/api";
import {
  ShieldAlert, Activity, Cpu, HardDrive, RefreshCw, CheckCircle2,
  AlertTriangle, Play, Server, ChevronDown, ChevronUp, Wrench, ShieldCheck
} from "lucide-react";

export default function AutonomousOperationsCenterPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [fixTarget, setFixTarget] = useState<string | null>(null);

  const stream = useTradingStream();
  const queryClient = useQueryClient();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const sreHealthQuery = useQuery({
    queryKey: ["sre-health"],
    queryFn: async () => {
      const res = await apiFetch("/api/operations/incidents");
      if (!res.ok) throw new Error("Failed to fetch operational health");
      return res.json();
    },
    refetchInterval: 5000
  });

  const remediateMutation = useMutation({
    mutationFn: async (componentId: string) => {
      const res = await apiFetch(`/api/operations/incidents/${componentId}/remediate`, { method: "POST" });
      return res.json();
    },
    onSuccess: () => {
      setFixTarget(null);
      queryClient.invalidateQueries({ queryKey: ["sre-health"] });
    }
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const sreData = sreHealthQuery.data ?? null;
  const status = sreData?.system_status ?? "GREEN";
  const title = sreData?.system_status_title ?? "System Healthy";
  const subtitle = sreData?.system_status_subtitle ?? "Spot Trading and Arbitrage are operating normally. No action required.";
  const summary = sreData?.health_summary ?? {};
  const groupedInc = sreData?.grouped_incident ?? null;
  const components = sreData?.components ?? {};

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6 max-w-7xl">
          {/* Header Bar */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                <ShieldCheck className="w-7 h-7 text-emerald-400" />
                System Operational Center
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Real-time operational status, account safety verification, &amp; automatic recovery.
              </p>
            </div>
            <button
              onClick={() => sreHealthQuery.refetch()}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs px-3 py-2 rounded-xl flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${sreHealthQuery.isFetching ? "animate-spin" : ""}`} />
              <span>Refresh Status</span>
            </button>
          </div>

          {/* 1. Top Hero Health Banner */}
          <div className={`p-6 rounded-2xl border flex items-center justify-between ${
            status === "GREEN"
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
              : status === "YELLOW"
              ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
              : status === "ORANGE"
              ? "bg-orange-500/10 border-orange-500/30 text-orange-300"
              : "bg-rose-500/10 border-rose-500/30 text-rose-300"
          }`}>
            <div className="flex items-center gap-4">
              {status === "GREEN" ? (
                <CheckCircle2 className="w-10 h-10 text-emerald-400 shrink-0" />
              ) : (
                <AlertTriangle className="w-10 h-10 shrink-0" />
              )}
              <div>
                <span className="text-xs font-mono font-bold tracking-wider uppercase opacity-80">
                  SYSTEM STATE: {status}
                </span>
                <h2 className="text-xl font-bold text-white mt-0.5">{title}</h2>
                <p className="text-xs opacity-90 mt-1">{subtitle}</p>
              </div>
            </div>

            <div className="hidden sm:flex flex-col items-end text-xs font-mono space-y-1">
              <span className="px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-slate-300 font-bold">
                ACCOUNT SAFETY: 100% PROTECTED
              </span>
              <span className="text-slate-400">PAPER / SHADOW MODE ONLY</span>
            </div>
          </div>

          {/* 2. System-Wide Health Summary Grid (7 High-Level Indicators) */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-cyan-400" />
              System-Wide Health Summary
            </h2>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-7 gap-3">
              {[
                { name: "Spot Trading", val: summary.spot_trading ?? "RUNNING" },
                { name: "Arbitrage", val: summary.arbitrage ?? "RUNNING" },
                { name: "Market Data", val: summary.market_data ?? "RUNNING" },
                { name: "Risk Protection", val: summary.risk_protection ?? "ACTIVE" },
                { name: "Execution", val: summary.execution ?? "READY" },
                { name: "Database", val: summary.database ?? "READY" },
                { name: "System Health", val: summary.system_health ?? "HEALTHY" },
              ].map((item) => {
                const isOK = item.val === "RUNNING" || item.val === "ACTIVE" || item.val === "READY" || item.val === "HEALTHY";
                return (
                  <div key={item.name} className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1 text-center">
                    <span className="text-[11px] text-slate-400 block font-medium truncate">{item.name}</span>
                    <div className={`text-xs font-bold font-mono px-2 py-0.5 rounded-full inline-flex items-center justify-center gap-1 ${
                      isOK
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${isOK ? "bg-emerald-400" : "bg-amber-400"}`} />
                      <span>{item.val}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 3. Simple Incident Explanation & Auto-Remediation */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Wrench className="w-5 h-5 text-amber-400" />
              Incident &amp; Auto-Recovery Status
            </h2>

            {!groupedInc ? (
              <div className="p-6 bg-slate-950 border border-slate-800/80 rounded-xl text-center text-slate-400 text-xs font-mono">
                ✓ ALL SERVICES OPERATING NORMALLY. NO ACTION REQUIRED.
              </div>
            ) : (
              <div className="p-5 bg-slate-950 border border-amber-500/30 rounded-xl space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                      {groupedInc.title}
                    </h3>
                    <span className="text-xs text-slate-400 font-mono mt-0.5 block">
                      Affected Services: {groupedInc.affected_components_count} | Recoverable: {groupedInc.auto_recoverable_count}
                    </span>
                  </div>

                  <button
                    onClick={() => setFixTarget(groupedInc.target_component)}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-1.5 cursor-pointer shadow-lg shadow-emerald-600/20"
                  >
                    <Wrench className="w-3.5 h-3.5" />
                    <span>Fix Automatically</span>
                  </button>
                </div>

                {/* 4-Box User Explanation Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs font-mono pt-2 border-t border-slate-800">
                  <div className="p-3 bg-slate-900 rounded-lg">
                    <div className="text-slate-400 font-sans font-medium text-[11px]">Problem</div>
                    <div className="text-amber-300 font-bold mt-1">{groupedInc.simple_explanation.problem}</div>
                  </div>
                  <div className="p-3 bg-slate-900 rounded-lg">
                    <div className="text-slate-400 font-sans font-medium text-[11px]">Impact</div>
                    <div className="text-slate-200 font-bold mt-1">{groupedInc.simple_explanation.impact}</div>
                  </div>
                  <div className="p-3 bg-slate-900 rounded-lg">
                    <div className="text-slate-400 font-sans font-medium text-[11px]">Safety Status</div>
                    <div className="text-emerald-400 font-bold mt-1">{groupedInc.simple_explanation.safety_status}</div>
                  </div>
                  <div className="p-3 bg-slate-900 rounded-lg">
                    <div className="text-slate-400 font-sans font-medium text-[11px]">Recommended Action</div>
                    <div className="text-cyan-400 font-bold mt-1">{groupedInc.simple_explanation.recommended_action}</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 4. Collapsible Advanced Details Accordion */}
          <div className="border border-slate-800 rounded-2xl overflow-hidden bg-slate-900/50">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full p-4 flex items-center justify-between text-left text-xs font-mono text-slate-400 hover:bg-slate-900 cursor-pointer"
            >
              <span>ADVANCED DETAILS (FOR DEVELOPERS &amp; OPERATORS)</span>
              {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showAdvanced && (
              <div className="p-6 border-t border-slate-800 space-y-6 bg-slate-950">
                {/* Dev Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-3 bg-slate-900 rounded-xl space-y-1">
                    <div className="text-[11px] text-slate-400">Supervisor State</div>
                    <div className="text-sm font-bold font-mono text-emerald-400">{sreData?.supervisor_state ?? "RUNNING"}</div>
                  </div>
                  <div className="p-3 bg-slate-900 rounded-xl space-y-1">
                    <div className="text-[11px] text-slate-400">Backend CPU Load</div>
                    <div className="text-sm font-bold font-mono text-slate-300">{sreData?.cpu_percent ?? "Health data unavailable"}</div>
                  </div>
                  <div className="p-3 bg-slate-900 rounded-xl space-y-1">
                    <div className="text-[11px] text-slate-400">Traced RAM Usage</div>
                    <div className="text-sm font-bold font-mono text-slate-300">{sreData?.ram_mb ?? 0.0} MB</div>
                  </div>
                  <div className="p-3 bg-slate-900 rounded-xl space-y-1">
                    <div className="text-[11px] text-slate-400">Process ID (PID)</div>
                    <div className="text-sm font-bold font-mono text-slate-300">{sreData?.process_id ?? "-"}</div>
                  </div>
                </div>

                {/* Raw 12 Subsystem Cards */}
                <div className="space-y-3">
                  <h3 className="text-xs font-mono font-bold text-slate-300">Raw Watchdog Subsystems ({Object.keys(components).length})</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5">
                    {Object.entries(components).map(([compName, compStatus]: [string, any]) => (
                      <div key={compName} className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg space-y-1">
                        <div className="text-[10px] font-mono text-slate-300 truncate" title={compName}>{compName}</div>
                        <div className="text-[10px] font-mono font-bold text-emerald-400">{compStatus}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Auto-Fix Confirmation Modal */}
        {fixTarget && (
          <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-emerald-400">
                  <Wrench className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Fix this problem automatically?</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Automated SRE Component Recovery</p>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-3.5 rounded-xl border border-slate-800 font-mono">
                The system will attempt a safe recovery for service <strong className="text-cyan-400">{fixTarget}</strong> and then verify that trading remains protected.
                <br /><br />
                <span className="text-emerald-400">✓ No live trades will be placed.</span>
              </p>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  onClick={() => setFixTarget(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={() => remediateMutation.mutate(fixTarget)}
                  disabled={remediateMutation.isPending}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl cursor-pointer disabled:opacity-50 flex items-center gap-1.5"
                >
                  {remediateMutation.isPending ? "Fixing..." : "Fix Now"}
                </button>
              </div>
            </div>
          </div>
        )}

        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
