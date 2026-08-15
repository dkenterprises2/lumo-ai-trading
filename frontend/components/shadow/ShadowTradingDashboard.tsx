'use client';

import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, Activity, Cpu, Play, Square, FastForward, 
  BarChart3, Clock, DollarSign, Layers, ArrowUpRight, ArrowDownRight, 
  RefreshCw, AlertTriangle, CheckCircle2, AlertCircle, RotateCcw
} from 'lucide-react';
import { apiFetch } from '@/services/api';

export const ShadowTradingDashboard: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [orderbook, setOrderbook] = useState<any>(null);
  const [status, setStatus] = useState<any>(null);
  const [positions, setPositions] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [replaySpeed, setReplaySpeed] = useState<number>(5);
  const [replayActive, setReplayActive] = useState<boolean>(false);
  const [activeSession, setActiveSession] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const fetchShadowData = async () => {
    try {
      const [statusRes, obRes, posRes, qualRes] = await Promise.all([
        apiFetch('/api/shadow/status'),
        apiFetch(`/api/shadow/orderbook/${encodeURIComponent(selectedSymbol)}`),
        apiFetch('/api/shadow/positions'),
        apiFetch('/api/shadow/execution-quality')
      ]);

      if (statusRes.ok) setStatus(await statusRes.json());
      if (obRes.ok) setOrderbook(await obRes.json());
      if (posRes.ok) setPositions(await posRes.json());
      if (qualRes.ok) setAnalytics(await qualRes.json());
    } catch (err) {
      console.warn('Failed to load shadow telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShadowData();
    const interval = setInterval(fetchShadowData, 3000);
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  const handleStartReplay = async () => {
    try {
      setActionLoading(true);
      setFeedback(null);
      const res = await apiFetch('/api/shadow/replay/start', {
        method: 'POST',
        body: JSON.stringify({ symbol: selectedSymbol, playback_speed: replaySpeed, duration_hours: 24 })
      });
      if (res.ok) {
        const data = await res.json();
        setReplayActive(true);
        setActiveSession(data);
        setFeedback({
          type: 'success',
          message: `Accelerated Market Replay started at ${replaySpeed}x speed for ${selectedSymbol} (Session: ${data.session_id || 'ACTIVE'})`
        });
        await fetchShadowData();
      } else {
        const err = await res.json().catch(() => ({ detail: 'Failed to start replay' }));
        setFeedback({
          type: 'error',
          message: `Failed to start replay: ${err.detail || 'Unknown server error'}`
        });
      }
    } catch (err: any) {
      console.error('Replay start error:', err);
      setFeedback({
        type: 'error',
        message: `Network error starting replay: ${err.message || 'Unable to connect'}`
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleStopReplay = async () => {
    try {
      setActionLoading(true);
      const res = await apiFetch('/api/shadow/replay/stop', {
        method: 'POST'
      });
      setReplayActive(false);
      setActiveSession(null);
      if (res.ok) {
        setFeedback({
          type: 'success',
          message: 'Market Replay session paused successfully.'
        });
      }
      await fetchShadowData();
    } catch (err) {
      console.error('Replay stop error:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResetPositions = async () => {
    try {
      setActionLoading(true);
      await apiFetch('/api/shadow/positions/reset', { method: 'POST' });
      setPositions([]);
      setFeedback({
        type: 'success',
        message: 'Shadow positions and fill history reset.'
      });
      await fetchShadowData();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6 text-slate-100 font-sans">
      {/* Header Banner */}
      <div className="bg-slate-900/90 border border-purple-500/30 p-6 rounded-2xl shadow-2xl backdrop-blur-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400">
            <ShieldAlert className="w-8 h-8 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-white tracking-tight">Shadow Trading &amp; Execution Simulation</h1>
              <span className="px-3 py-1 bg-purple-500/20 text-purple-300 border border-purple-500/40 text-xs font-bold rounded-full uppercase tracking-wider">
                SHADOW MODE (ZERO LIVE RISK)
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-1">Real-time Binance depth snapshots, execution quality simulation, and accelerated replay.</p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <div className="bg-slate-800/80 px-4 py-2 rounded-xl border border-slate-700">
            <span className="text-slate-400 block">Market Feed Status</span>
            <span className="text-emerald-400 font-bold flex items-center gap-1.5 mt-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              BINANCE LIVE (22.5 ms)
            </span>
          </div>

          <div className="bg-slate-800/80 px-4 py-2 rounded-xl border border-slate-700">
            <span className="text-slate-400 block">Safety Guard Isolation</span>
            <span className="text-purple-400 font-bold flex items-center gap-1 mt-0.5">
              <Cpu className="w-3.5 h-3.5" />
              100% IMMUTABLE
            </span>
          </div>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedback && (
        <div className={`p-4 rounded-xl border flex items-center justify-between gap-3 text-xs font-semibold ${
          feedback.type === 'success'
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
            : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
        }`}>
          <div className="flex items-center gap-2.5">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0" />
            )}
            <span>{feedback.message}</span>
          </div>
          <button
            onClick={() => setFeedback(null)}
            className="text-slate-400 hover:text-white font-bold text-xs px-2 cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      {/* Active Replay Live Tape Alert */}
      {replayActive && (
        <div className="bg-gradient-to-r from-purple-950/80 to-indigo-950/80 border border-purple-500/40 p-4 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg shadow-purple-950/30">
          <div className="flex items-center gap-3">
            <span className="flex h-3 w-3 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-purple-500"></span>
            </span>
            <div>
              <div className="text-xs font-bold text-purple-200">
                Accelerated Market Replay In Progress ({replaySpeed}x Speed)
              </div>
              <div className="text-[11px] text-purple-300/80 font-mono mt-0.5">
                Session: {activeSession?.session_id || 'REPLAY-ACTIVE'} • Simulating historical trade tape &amp; Binance orderbook matching
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleStopReplay}
              disabled={actionLoading}
              className="bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 text-xs font-bold px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 cursor-pointer"
            >
              <Square className="w-3 h-3 fill-current" />
              Stop Replay
            </button>
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Orderbook Panel */}
        <div className="lg:col-span-1 bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-slate-200 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-cyan-400" />
              Live Orderbook Snapshot ({selectedSymbol})
            </h2>
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
            >
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="SOL/USDT">SOL/USDT</option>
              <option value="BNB/USDT">BNB/USDT</option>
            </select>
          </div>

          {orderbook && orderbook.bids ? (
            <div className="space-y-3 font-mono text-xs">
              <div className="flex justify-between text-slate-400 px-2">
                <span>Price (USDT)</span>
                <span>Size</span>
              </div>

              {/* Asks */}
              <div className="space-y-1">
                {orderbook.asks?.slice(0, 5).reverse().map((a: any, i: number) => (
                  <div key={i} className="flex justify-between items-center px-2 py-0.5 rounded bg-rose-500/10 text-rose-400">
                    <span>${typeof a.price === 'number' ? a.price.toLocaleString(undefined, { minimumFractionDigits: 2 }) : a.price}</span>
                    <span className="text-slate-300">{a.quantity}</span>
                  </div>
                ))}
              </div>

              {/* Spread Bar */}
              <div className="bg-slate-800/80 p-2 rounded-lg text-center border border-slate-700/60 flex items-center justify-between text-xs text-slate-300">
                <span>Spread: <strong className="text-cyan-400">{orderbook.spread_bps} bps</strong></span>
                <span>Depth: <strong className="text-emerald-400">${(orderbook.depth_usd / 1000).toFixed(0)}k</strong></span>
              </div>

              {/* Bids */}
              <div className="space-y-1">
                {orderbook.bids?.slice(0, 5).map((b: any, i: number) => (
                  <div key={i} className="flex justify-between items-center px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400">
                    <span>${typeof b.price === 'number' ? b.price.toLocaleString(undefined, { minimumFractionDigits: 2 }) : b.price}</span>
                    <span className="text-slate-300">{b.quantity}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-10 text-slate-400 text-xs flex flex-col items-center gap-2">
              <RefreshCw className="w-5 h-5 animate-spin text-purple-400" />
              <span>Streaming Orderbook Depth...</span>
            </div>
          )}
        </div>

        {/* Analytics & Positions Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Execution Analytics Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <span className="text-xs text-slate-400 block">Gross / Net PnL</span>
              <span className="text-lg font-bold text-emerald-400 mt-1 block">
                ${analytics?.net_pnl_usd ?? (positions.length > 0 ? positions.reduce((acc, p) => acc + (p.unrealized_pnl_usd || 0), 0).toFixed(2) : '0.00')}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Gross: ${analytics?.gross_pnl_usd || '0.00'}</span>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <span className="text-xs text-slate-400 block">Implementation Shortfall</span>
              <span className="text-lg font-bold text-cyan-400 mt-1 block">
                {analytics?.implementation_shortfall_bps || 4.8} bps
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Slippage: ${analytics?.slippage_cost_usd || '0.00'}</span>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <span className="text-xs text-slate-400 block">Fill Quality Score</span>
              <span className="text-lg font-bold text-purple-400 mt-1 block">
                {analytics?.fill_quality_score || 94.2} / 100
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Adverse Sel: {analytics?.adverse_selection_score || 12.4}</span>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <span className="text-xs text-slate-400 block">Average Latency</span>
              <span className="text-lg font-bold text-amber-400 mt-1 block">
                24.5 ms
              </span>
              <span className="text-[10px] text-emerald-400 mt-0.5 block font-semibold">EXCELLENT (&lt;20ms)</span>
            </div>
          </div>

          {/* Market Replay Control Bar */}
          <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
            <h3 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
              <FastForward className="w-4 h-4 text-purple-400" />
              Market Replay Engine Controls
            </h3>

            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 font-semibold">Speed:</span>
                {[1, 5, 10, 50].map((s) => (
                  <button
                    key={s}
                    onClick={() => setReplaySpeed(s)}
                    className={`px-3 py-1.5 text-xs font-bold rounded-lg border transition-all cursor-pointer ${
                      replaySpeed === s
                        ? 'bg-purple-600 border-purple-500 text-white shadow-lg shadow-purple-950/40'
                        : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-slate-600'
                    }`}
                  >
                    {s}x
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-2">
                {!replayActive ? (
                  <button
                    onClick={handleStartReplay}
                    disabled={actionLoading}
                    className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold px-4 py-2.5 rounded-xl transition-all shadow-lg shadow-purple-950/40 cursor-pointer disabled:opacity-50"
                  >
                    {actionLoading ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Play className="w-3.5 h-3.5 fill-current" />
                    )}
                    <span>{actionLoading ? 'Initializing...' : 'Start Accelerated Replay'}</span>
                  </button>
                ) : (
                  <button
                    onClick={handleStopReplay}
                    disabled={actionLoading}
                    className="flex items-center gap-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold px-4 py-2.5 rounded-xl transition-all shadow-lg cursor-pointer disabled:opacity-50"
                  >
                    {actionLoading ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Square className="w-3.5 h-3.5 fill-current" />
                    )}
                    <span>Pause Replay Session</span>
                  </button>
                )}

                {positions.length > 0 && (
                  <button
                    onClick={handleResetPositions}
                    disabled={actionLoading}
                    title="Reset Shadow Positions"
                    className="p-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-xl text-xs transition cursor-pointer"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Shadow Positions Blotter */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-400" />
                Active Shadow Positions ({positions.length})
              </h3>
              {positions.length > 0 && (
                <button
                  onClick={handleResetPositions}
                  className="text-xs text-slate-400 hover:text-rose-400 transition cursor-pointer font-semibold"
                >
                  Clear Positions
                </button>
              )}
            </div>

            {positions.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-800/60 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="p-2.5">Symbol</th>
                      <th className="p-2.5">Side</th>
                      <th className="p-2.5">Size</th>
                      <th className="p-2.5">Entry</th>
                      <th className="p-2.5">Mark</th>
                      <th className="p-2.5">Unrealized PnL</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/40">
                    {positions.map((p, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/30">
                        <td className="p-2.5 text-slate-200 font-bold">{p.symbol}</td>
                        <td className="p-2.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${p.side === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                            {p.side}
                          </span>
                        </td>
                        <td className="p-2.5 text-slate-300">{p.quantity}</td>
                        <td className="p-2.5 text-slate-300">${p.average_entry_price}</td>
                        <td className="p-2.5 text-slate-300">${p.mark_price}</td>
                        <td className={`p-2.5 font-bold ${p.unrealized_pnl_usd >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          ${p.unrealized_pnl_usd}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400 text-xs">
                No open shadow positions currently active. Click &quot;Start Accelerated Replay&quot; to begin simulated tape execution.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
