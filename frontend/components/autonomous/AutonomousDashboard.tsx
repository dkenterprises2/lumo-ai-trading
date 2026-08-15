'use client';

import React, { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  Square,
  ShieldCheck,
  Zap,
  Activity,
  TrendingUp,
  RefreshCw,
  Clock,
  Layers,
  AlertTriangle,
  CheckCircle2,
  Lock,
  Cpu,
  Check,
  X,
  Sliders,
  FileText,
  BarChart3,
  Flame
} from 'lucide-react';
import { apiFetch } from '@/services/api';
import { ExecutionTimeline, StateTransition } from '@/components/execution/ExecutionTimeline';

export function AutonomousDashboard() {
  const [engineStatus, setEngineStatus] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [executions, setExecutions] = useState<any[]>([]);
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>('SCENARIO_A');
  const [validationReport, setValidationReport] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [selectedExec, setSelectedExec] = useState<any>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statusRes, metricsRes, execsRes, scenariosRes, reportRes] = await Promise.all([
        apiFetch('/api/autonomous/status'),
        apiFetch('/api/autonomous/metrics'),
        apiFetch('/api/autonomous/executions'),
        apiFetch('/api/autonomous-validation/scenarios'),
        apiFetch('/api/autonomous-validation/report')
      ]);

      if (statusRes.ok) {
        const d = await statusRes.json();
        setEngineStatus(d.engine || null);
      }
      if (metricsRes.ok) {
        const d = await metricsRes.json();
        setMetrics(d.metrics || null);
      }
      if (execsRes.ok) {
        const d = await execsRes.json();
        setExecutions(d.executions || []);
      }
      if (scenariosRes.ok) {
        const d = await scenariosRes.json();
        setScenarios(d.scenarios || []);
      }
      if (reportRes.ok) {
        const d = await reportRes.json();
        setValidationReport(d.report || null);
      }
    } catch (err) {
      console.warn('Autonomous dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, 4000);
    return () => clearInterval(timer);
  }, []);

  const handleAction = async (action: string) => {
    try {
      setActionLoading(true);
      const res = await apiFetch(`/api/autonomous/${action}`, { method: 'POST' });
      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error(`Autonomous action ${action} failed:`, err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRunScenario = async (scId: string) => {
    try {
      setActionLoading(true);
      const res = await apiFetch(`/api/autonomous-validation/run/${scId}`, { method: 'POST' });
      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error(`Run scenario ${scId} failed:`, err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRunAllScenarios = async () => {
    try {
      setActionLoading(true);
      const res = await apiFetch('/api/autonomous-validation/run-all', { method: 'POST' });
      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error('Run all scenarios failed:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const status = engineStatus?.status || 'STOPPED';
  const pipelineStages = [
    { key: 'market_data', label: 'Market Data', status: status === 'RUNNING' ? 'GREEN' : 'GRAY' },
    { key: 'opportunity', label: 'Opportunity', status: (metrics?.opportunities_detected ?? 0) > 0 ? 'GREEN' : 'YELLOW' },
    { key: 'risk', label: 'Risk Gate', status: (metrics?.risk_blocked_count ?? 0) > 0 ? 'RED' : 'GREEN' },
    { key: 'governance', label: 'Governance', status: (metrics?.governance_blocked_count ?? 0) > 0 ? 'RED' : 'GREEN' },
    { key: 'execution', label: 'Execution OMS', status: (metrics?.executions_started ?? 0) > 0 ? 'GREEN' : 'GRAY' },
    { key: 'position', label: 'Position Open', status: (metrics?.positions_open ?? 0) > 0 ? 'GREEN' : 'GRAY' },
    { key: 'exit', label: 'Exit Unwind', status: (metrics?.positions_closed ?? 0) > 0 ? 'GREEN' : 'GRAY' }
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6">
      {/* Header & Main Controls */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              AUTONOMOUS SHADOW TRADING ENGINE
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 font-medium">
                Phase 42 — Replay & Execution Proof
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              End-to-end real & replayed execution proof, Phase 34 risk gate, OMS routing, shadow position tracking & exit engine
            </p>
          </div>
        </div>

        {/* Engine Control Buttons */}
        <div className="flex items-center gap-2">
          {status === 'STOPPED' || status === 'PAUSED' ? (
            <button
              onClick={() => handleAction(status === 'PAUSED' ? 'resume' : 'start')}
              disabled={actionLoading}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold bg-emerald-600 hover:bg-emerald-500 text-slate-950 transition shadow-lg shadow-emerald-900/30 cursor-pointer disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-current" />
              {status === 'PAUSED' ? 'RESUME ENGINE' : 'START AUTONOMOUS ENGINE'}
            </button>
          ) : (
            <button
              onClick={() => handleAction('pause')}
              disabled={actionLoading}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20 transition cursor-pointer disabled:opacity-50"
            >
              <Pause className="w-4 h-4" />
              PAUSE
            </button>
          )}

          <button
            onClick={() => handleAction('stop')}
            disabled={actionLoading || status === 'STOPPED'}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold bg-rose-500/10 border border-rose-500/30 text-rose-400 hover:bg-rose-500/20 transition cursor-pointer disabled:opacity-50"
          >
            <Square className="w-4 h-4" />
            EMERGENCY STOP
          </button>

          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Mode & Safety Telemetry Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-mono">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className={`h-2.5 w-2.5 rounded-full ${
              status === 'RUNNING' ? 'bg-emerald-400 animate-ping' :
              status === 'PAUSED' ? 'bg-amber-400' : 'bg-rose-500'
            }`} />
            <span className="font-bold text-slate-200">
              AUTONOMOUS ENGINE: {status}
            </span>
          </div>
          <span className="text-slate-700">|</span>
          <span className="text-indigo-400 font-bold">SCAN: {status === 'RUNNING' ? 'ACTIVE' : 'IDLE'}</span>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            PAPER_MODE: TRUE
          </span>
          <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            SHADOW_MODE: TRUE
          </span>
          <span className="px-2.5 py-0.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold flex items-center gap-1">
            <Lock className="w-3.5 h-3.5" />
            LIVE_EXECUTION: FALSE
          </span>
        </div>
      </div>

      {/* Live Pipeline Monitor */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          Autonomous Pipeline Execution Status
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-7 gap-2 text-center">
          {pipelineStages.map((stage, idx) => (
            <div key={idx} className="relative bg-slate-950/80 p-3 rounded-xl border border-slate-800 flex flex-col items-center space-y-1">
              <span className={`h-2.5 w-2.5 rounded-full ${
                stage.status === 'GREEN' ? 'bg-emerald-400 shadow-md shadow-emerald-500/50 animate-pulse' :
                stage.status === 'RED' ? 'bg-rose-500 shadow-md shadow-rose-500/50' :
                stage.status === 'YELLOW' ? 'bg-amber-400' : 'bg-slate-700'
              }`} />
              <span className="text-xs font-bold text-slate-200 mt-1">{stage.label}</span>
              <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                stage.status === 'GREEN' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                stage.status === 'RED' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                stage.status === 'YELLOW' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'text-slate-500'
              }`}>
                {stage.status === 'GREEN' ? 'PASSED' : stage.status === 'RED' ? 'REJECTED' : stage.status === 'YELLOW' ? 'WAITING' : 'IDLE'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Deterministic Replay & Execution Proof Section */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h2 className="font-semibold text-white flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-amber-400" />
              Deterministic Market Replay & Autonomous Validation Framework
            </h2>
            <p className="text-xs text-slate-400">
              Run deterministic historical market tick scenarios (Scenarios A – J) to prove the end-to-end execution proof lifecycle
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold px-3 py-1 rounded bg-indigo-500/10 border border-indigo-500/30 text-indigo-300">
              SCORE: {validationReport?.validation_score !== undefined ? `${validationReport.validation_score}/100` : 'CALCULATING'}
            </span>
            <span className="text-xs font-mono font-bold px-3 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              {validationReport?.readiness_label || 'READY FOR SHADOW'}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 bg-slate-950 p-4 rounded-xl border border-slate-850">
          <div className="flex flex-col space-y-1">
            <label className="text-[11px] text-slate-400 font-medium">Replay Validation Scenario</label>
            <select
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              {scenarios.map((sc, idx) => (
                <option key={idx} value={sc.code}>
                  {sc.title} ({sc.category})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2 pt-4">
            <button
              onClick={() => handleRunScenario(selectedScenario)}
              disabled={actionLoading}
              className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl transition cursor-pointer disabled:opacity-50"
            >
              <Zap className="w-3.5 h-3.5 fill-current" />
              RUN SELECTED SCENARIO
            </button>

            <button
              onClick={handleRunAllScenarios}
              disabled={actionLoading}
              className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs rounded-xl transition cursor-pointer disabled:opacity-50"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              RUN ALL SCENARIOS (A – J)
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Summary Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 lg:grid-cols-10 gap-3 font-mono text-xs">
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <div className="text-[10px] text-slate-400 font-sans">Opportunities Detected</div>
          <div className="text-base font-bold text-slate-100">{metrics?.opportunities_detected ?? 0}</div>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <div className="text-[10px] text-slate-400 font-sans">Approved</div>
          <div className="text-base font-bold text-emerald-400">{metrics?.approved_count ?? 0}</div>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <div className="text-[10px] text-slate-400 font-sans">Risk Blocked</div>
          <div className="text-base font-bold text-rose-400">{metrics?.risk_blocked_count ?? 0}</div>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <div className="text-[10px] text-slate-400 font-sans">Gov Blocked</div>
          <div className="text-base font-bold text-purple-400">{metrics?.governance_blocked_count ?? 0}</div>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <div className="text-[10px] text-slate-400 font-sans">Executions Started</div>
          <div className="text-base font-bold text-cyan-400">{metrics?.executions_started ?? 0}</div>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <div className="text-[10px] text-slate-400 font-sans">Active Executions</div>
          <div className="text-base font-bold text-indigo-400">{metrics?.active_executions ?? 0}</div>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <div className="text-[10px] text-slate-400 font-sans">Positions Open</div>
          <div className="text-base font-bold text-amber-400">{metrics?.positions_open ?? 0}</div>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <div className="text-[10px] text-slate-400 font-sans">Positions Closed</div>
          <div className="text-base font-bold text-emerald-300">{metrics?.positions_closed ?? 0}</div>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800 col-span-2">
          <div className="text-[10px] text-slate-400 font-sans">Net Shadow PnL</div>
          <div className={`text-base font-bold ${(metrics?.net_shadow_pnl ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {metrics?.net_shadow_pnl !== undefined ? `$${metrics.net_shadow_pnl.toFixed(2)}` : '$0.00'}
          </div>
        </div>
      </div>

      {/* Autonomous Executions Blotter */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            Autonomous Execution Blotter & State Lifecycle
          </h2>
          <span className="text-xs text-slate-400">{executions.length} executions recorded</span>
        </div>

        {executions.length === 0 ? (
          <div className="p-8 text-center rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 font-sans">
            <ShieldCheck className="w-8 h-8 text-slate-500 mx-auto" />
            <div className="text-sm font-bold text-slate-300">No autonomous executions recorded</div>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              When the autonomous scanner or market replay engine processes executable opportunities, complete execution lifecycle records will appear here automatically.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300 font-mono">
              <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px]">
                <tr>
                  <th className="p-3">Execution ID</th>
                  <th className="p-3">Route</th>
                  <th className="p-3">Algorithm</th>
                  <th className="p-3">State</th>
                  <th className="p-3">Fees & Friction</th>
                  <th className="p-3">Net PnL</th>
                  <th className="p-3">Timeline</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {executions.map((ex, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition">
                    <td className="p-3 font-bold text-cyan-400">{ex.execution_id}</td>
                    <td className="p-3 font-sans font-semibold text-white">
                      {ex.symbol} ({ex.buy_exchange} $\rightarrow$ {ex.sell_exchange})
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 font-bold">
                        {ex.selected_algorithm || 'SMART_ROUTER'}
                      </span>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded font-bold ${
                        ex.status === 'COMPLETED' || ex.status === 'FILLED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                        ex.status?.includes('BLOCKED') || ex.status === 'REJECTED' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                        'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      }`}>
                        {ex.status}
                      </span>
                    </td>
                    <td className="p-3 text-slate-400">${ex.fees}</td>
                    <td className={`p-3 font-bold ${ex.net_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {ex.net_pnl !== undefined ? `$${ex.net_pnl}` : 'PNL PENDING'}
                    </td>
                    <td className="p-3">
                      <button
                        onClick={() => setSelectedExec(ex)}
                        className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg transition text-[11px] cursor-pointer"
                      >
                        VIEW TIMELINE
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Execution Timeline Modal */}
      {selectedExec && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700 p-6 rounded-2xl max-w-lg w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="font-bold text-white text-base flex items-center gap-2">
                <Activity className="w-5 h-5 text-indigo-400" />
                Execution Lifecycle Audit Log
              </span>
              <button
                onClick={() => setSelectedExec(null)}
                className="text-slate-400 hover:text-white font-bold text-sm"
              >
                ✕
              </button>
            </div>

            <ExecutionTimeline
              transitions={selectedExec.state_history || []}
              executionId={selectedExec.execution_id}
              algorithm={selectedExec.selected_algorithm}
              netPnl={selectedExec.net_pnl}
            />

            <button
              onClick={() => setSelectedExec(null)}
              className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl text-sm transition cursor-pointer"
            >
              Close Timeline
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
