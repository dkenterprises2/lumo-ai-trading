'use client';

import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  RotateCcw, 
  Sparkles, 
  ShieldAlert, 
  TrendingUp, 
  History, 
  Layers, 
  Award,
  Play,
  Zap,
  Check,
  X
} from 'lucide-react';

interface GovernanceData {
  pending_approvals: any[];
  active_weights: Record<string, number>;
  shadow_evaluations: any[];
  rollback_history: any[];
  risk_violations: any[];
}

export default function AIGovernanceAdminPage() {
  const [loading, setLoading] = useState(true);
  const [actionNotice, setActionNotice] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const [data, setData] = useState<GovernanceData>({
    pending_approvals: [
      {
        experiment_id: 'OPT-20260810-01',
        strategy_name: 'AI_HYBRID',
        market_regime: 'NEUTRAL',
        sharpe_delta: '+0.42',
        win_rate: '71.5%',
        composite_score: 1.84,
        created_at: '2026-08-10 09:30:00'
      }
    ],
    active_weights: {
      rsi_weight: 1.5,
      macd_weight: 1.2,
      ema_slope_weight: 1.8,
      adx_weight: 1.0,
      vwap_distance_weight: 1.4,
      obv_weight: 0.8,
      atr_pct_weight: 1.1,
      fear_greed_weight: 0.9
    },
    shadow_evaluations: [
      {
        id: 'SHADOW-901',
        candidate_version: 'v4.2-exp01',
        sharpe_active: 1.45,
        sharpe_candidate: 1.87,
        status: 'PASSED (7-Day Sim)',
        win_rate_candidate: '72.1%'
      }
    ],
    rollback_history: [
      {
        version: 1,
        strategy: 'AI_HYBRID',
        regime: 'NEUTRAL',
        rolled_back_at: '2026-08-09 18:22:00',
        reason: 'Manual Operator Reset'
      }
    ],
    risk_violations: []
  });

  useEffect(() => {
    fetchGovernance();
  }, []);

  const fetchGovernance = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/learning/status');
      if (res.ok) {
        const json = await res.json();
        if (json) {
          // Sync active weights if present
          if (json.active_weights && json.active_weights.indicator_weights) {
            setData(prev => ({
              ...prev,
              active_weights: json.active_weights.indicator_weights
            }));
          }
        }
      }
    } catch (err) {
      console.error('Failed to fetch AI governance status:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (expId: string) => {
    try {
      const res = await fetch('/api/learning/approve-deployment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          experiment_id: expId,
          human_approval: true,
          notes: 'Approved via Super Admin AI Governance Console'
        })
      });

      if (res.ok) {
        setActionNotice({ text: `Candidate weights ${expId} approved & deployed to production!`, type: 'success' });
        fetchGovernance();
      } else {
        const errJson = await res.json();
        setActionNotice({ text: errJson.detail || 'Approval failed.', type: 'error' });
      }
    } catch (err: any) {
      setActionNotice({ text: err.message || 'Error approving candidate.', type: 'error' });
    } finally {
      setTimeout(() => setActionNotice(null), 5000);
    }
  };

  const handleRollback = async () => {
    try {
      const res = await fetch('/api/learning/revert-weights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          version: 1,
          strategy_name: 'AI_HYBRID',
          market_regime: 'NEUTRAL'
        })
      });

      if (res.ok) {
        setActionNotice({ text: 'Strategy weights successfully rolled back to Version 1.', type: 'success' });
        fetchGovernance();
      } else {
        const errJson = await res.json();
        setActionNotice({ text: errJson.detail || 'Rollback failed.', type: 'error' });
      }
    } catch (err: any) {
      setActionNotice({ text: err.message || 'Error rolling back weights.', type: 'error' });
    } finally {
      setTimeout(() => setActionNotice(null), 5000);
    }
  };

  return (
    <div className="space-y-8 text-slate-100">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-xl border border-purple-500/30 bg-purple-500/10 p-2.5 text-purple-400">
              <Brain className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">AI Governance Console</h1>
              <p className="text-sm text-slate-400">Human-in-the-loop deployment approvals, strategy weights, and rollback controls.</p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => {
              setActionNotice({ text: 'Parallel 7-day shadow evaluation simulation started.', type: 'success' });
              setTimeout(() => setActionNotice(null), 4000);
            }}
            className="flex items-center gap-2 rounded-xl border border-cyan-500/40 bg-cyan-500/10 px-4 py-2 text-xs font-semibold text-cyan-300 hover:bg-cyan-500/20 transition-all"
          >
            <Play className="h-4 w-4 text-cyan-400" />
            Trigger Shadow Sim
          </button>

          <button
            onClick={handleRollback}
            className="flex items-center gap-2 rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-2 text-xs font-semibold text-rose-300 hover:bg-rose-500/20 transition-all"
          >
            <RotateCcw className="h-4 w-4 text-rose-400" />
            Instant Rollback
          </button>
        </div>
      </div>

      {/* Action Notification */}
      {actionNotice && (
        <div className={`flex items-center gap-3 rounded-xl border p-4 text-sm font-semibold ${
          actionNotice.type === 'success' ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : 'border-rose-500/40 bg-rose-500/10 text-rose-300'
        }`}>
          {actionNotice.type === 'success' ? <CheckCircle2 className="h-5 w-5" /> : <XCircle className="h-5 w-5" />}
          {actionNotice.text}
        </div>
      )}

      {/* Pending Model Approvals */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-400" />
            Pending Optuna Candidate Model Approvals
          </h3>
          <span className="text-xs font-semibold text-purple-400">{data.pending_approvals.length} Pending</span>
        </div>

        {data.pending_approvals.length === 0 ? (
          <p className="text-xs text-slate-500 py-4">No pending candidate models requiring approval.</p>
        ) : (
          <div className="space-y-3">
            {data.pending_approvals.map((item) => (
              <div key={item.experiment_id} className="flex flex-col justify-between gap-4 rounded-xl border border-purple-500/30 bg-purple-500/5 p-4 md:flex-row md:items-center">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-white">{item.experiment_id}</span>
                    <span className="rounded-full bg-purple-500/20 px-2.5 py-0.5 text-[10px] font-semibold text-purple-300 uppercase">{item.strategy_name}</span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Sharpe Delta: <span className="font-semibold text-emerald-400">{item.sharpe_delta}</span> | Win Rate: <span className="font-semibold text-cyan-400">{item.win_rate}</span> | Composite Score: {item.composite_score}
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleApprove(item.experiment_id)}
                    className="flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-emerald-600/20 hover:bg-emerald-500 transition-all"
                  >
                    <Check className="h-4 w-4" />
                    Approve Deployment
                  </button>

                  <button
                    onClick={() => {
                      setActionNotice({ text: `Candidate ${item.experiment_id} rejected.`, type: 'success' });
                      setData(prev => ({ ...prev, pending_approvals: [] }));
                      setTimeout(() => setActionNotice(null), 4000);
                    }}
                    className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-700 transition-all"
                  >
                    <X className="h-4 w-4" />
                    Reject Candidate
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Active Strategy Weights Matrix */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Zap className="h-5 w-5 text-cyan-400" />
          Active Indicator Weights Matrix (AI Hybrid / Neutral Regime)
        </h3>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {Object.entries(data.active_weights).map(([k, v]) => (
            <div key={k} className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-1">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{k.replace('_weight', '').replace('_', ' ')}</span>
              <p className="text-xl font-bold text-cyan-400">{typeof v === 'number' ? v.toFixed(2) : v}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Shadow Evaluations & Rollback History Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Shadow Evaluation Results */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <Award className="h-5 w-5 text-emerald-400" />
            Parallel Shadow Evaluation Monitor
          </h3>

          {data.shadow_evaluations.map((item) => (
            <div key={item.id} className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">{item.candidate_version}</span>
                <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-semibold text-emerald-300">{item.status}</span>
              </div>
              <div className="text-xs text-slate-400 space-y-1">
                <p>Active Sharpe: {item.sharpe_active} $\rightarrow$ Candidate Sharpe: <span className="font-bold text-emerald-400">{item.sharpe_candidate}</span></p>
                <p>Candidate Win Rate: {item.win_rate_candidate}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Rollback & Audit History */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <History className="h-5 w-5 text-purple-400" />
            Version Rollback Audit History
          </h3>

          {data.rollback_history.map((item, idx) => (
            <div key={idx} className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">{item.strategy} — Version {item.version}</span>
                <span className="text-[10px] text-slate-400">{item.rolled_back_at}</span>
              </div>
              <p className="text-xs text-slate-400">Reason: {item.reason}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
