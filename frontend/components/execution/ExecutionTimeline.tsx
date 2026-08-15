'use client';

import React from 'react';
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  Zap,
  ShieldCheck,
  TrendingUp,
  Activity,
  Layers,
  ArrowRight
} from 'lucide-react';

export interface StateTransition {
  execution_id: string;
  previous_state: string;
  new_state: string;
  reason: string;
  timestamp: number;
}

interface ExecutionTimelineProps {
  transitions: StateTransition[];
  executionId?: string;
  algorithm?: string;
  netPnl?: number;
}

export function ExecutionTimeline({ transitions, executionId, algorithm, netPnl }: ExecutionTimelineProps) {
  if (!transitions || transitions.length === 0) {
    return (
      <div className="p-4 text-center text-xs text-slate-500 font-mono">
        No state transition history available for execution timeline.
      </div>
    );
  }

  const getStepIcon = (state: string) => {
    switch (state) {
      case 'DETECTED':
      case 'VALIDATING':
        return <Activity className="w-4 h-4 text-cyan-400" />;
      case 'RISK_CHECK':
      case 'GOVERNANCE_CHECK':
        return <ShieldCheck className="w-4 h-4 text-purple-400" />;
      case 'APPROVED':
      case 'EXECUTING':
        return <Zap className="w-4 h-4 text-amber-400" />;
      case 'FILLED':
      case 'POSITION_OPEN':
      case 'MONITORING':
        return <Layers className="w-4 h-4 text-indigo-400" />;
      case 'EXIT_TRIGGERED':
      case 'CLOSING':
      case 'CLOSED':
      case 'COMPLETED':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-rose-400" />;
    }
  };

  const getStepColor = (state: string) => {
    if (['REJECTED', 'STALE', 'RISK_BLOCKED', 'GOVERNANCE_BLOCKED', 'LIQUIDITY_BLOCKED', 'EXCHANGE_UNHEALTHY', 'EXECUTION_FAILED', 'CANCELLED'].includes(state)) {
      return 'border-rose-500/30 bg-rose-500/10 text-rose-300';
    }
    if (['COMPLETED', 'CLOSED'].includes(state)) {
      return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300';
    }
    return 'border-slate-800 bg-slate-950/70 text-slate-300';
  };

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <div className="text-slate-400 text-[10px]">EXECUTION LIFECYCLE TIMELINE</div>
          <div className="text-sm font-bold text-white flex items-center gap-2">
            <span>{executionId || 'EXEC-AUTO'}</span>
            {algorithm && (
              <span className="px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-[10px]">
                {algorithm}
              </span>
            )}
          </div>
        </div>
        {netPnl !== undefined && (
          <div className="text-right">
            <div className="text-[10px] text-slate-400">NET SHADOW PNL</div>
            <div className={`text-sm font-bold ${netPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {netPnl !== null ? `$${netPnl.toFixed(2)}` : 'PNL PENDING'}
            </div>
          </div>
        )}
      </div>

      <div className="relative pl-6 space-y-3 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
        {transitions.map((t, idx) => (
          <div key={idx} className={`relative p-3 rounded-xl border ${getStepColor(t.new_state)} space-y-1`}>
            <div className="absolute -left-6 top-3 w-5 h-5 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center">
              {getStepIcon(t.new_state)}
            </div>
            <div className="flex items-center justify-between">
              <span className="font-bold text-white text-xs">{t.new_state}</span>
              <span className="text-[10px] text-slate-500 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {new Date(t.timestamp * 1000).toLocaleTimeString()}
              </span>
            </div>
            <p className="text-[11px] font-sans text-slate-400">{t.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
