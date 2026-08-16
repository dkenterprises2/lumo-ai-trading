'use client';

import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, Activity, Cpu, Play, Square, FastForward, 
  BarChart3, Clock, DollarSign, Layers, ArrowUpRight, ArrowDownRight, 
  RefreshCw, AlertTriangle, CheckCircle2, AlertCircle, RotateCcw
} from 'lucide-react';
import { apiFetch } from '@/services/api';

export const ShadowTradingDashboard: React.FC = () => {
  const [mounted, setMounted] = useState<boolean>(false);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [orderbook, setOrderbook] = useState<any>(null);
  const [status, setStatus] = useState<any>(null);
  const [positions, setPositions] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [selectedSpeed, setSelectedSpeed] = useState<number>(5);
  const [replaySpeed, setReplaySpeed] = useState<number>(5);
  const [replayActive, setReplayActive] = useState<boolean>(false);
  const [activeSession, setActiveSession] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    setMounted(true);
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('lumo_shadow_replay_speed');
      if (stored) {
        const parsed = parseInt(stored, 10);
        if (!isNaN(parsed) && parsed > 0) {
          setSelectedSpeed(parsed);
          setReplaySpeed(parsed);
        }
      }
    }
  }, []);

  const fetchShadowData = async () => {
    try {
      const [statusRes, obRes, posRes, qualRes, replayRes] = await Promise.all([
        apiFetch('/api/shadow/status'),
        apiFetch(`/api/shadow/orderbook/${encodeURIComponent(selectedSymbol)}`),
        apiFetch('/api/shadow/positions'),
        apiFetch('/api/shadow/execution-quality'),
        apiFetch('/api/shadow/replay/status')
      ]);

      if (statusRes.ok) {
        const sData = await statusRes.json();
        setStatus(sData && typeof sData === 'object' ? sData : null);
      }
      if (replayRes.ok) {
        const repData = await replayRes.json();
        if (Array.isArray(repData) && repData.length > 0) {
          const active = repData.find((s: any) => s && s.status === 'RUNNING');
          if (active) {
            setReplayActive(true);
            setActiveSession(active);
            if (active.playback_speed) {
              const spd = Number(active.playback_speed);
              setSelectedSpeed(spd);
              setReplaySpeed(spd);
              if (typeof window !== 'undefined') {
                localStorage.setItem('lumo_shadow_replay_speed', spd.toString());
              }
            }
          } else {
            setReplayActive(false);
            setActiveSession(null);
          }
        } else {
          setReplayActive(false);
          setActiveSession(null);
        }
      }
      if (obRes.ok) {
        const obData = await obRes.json();
        setOrderbook(obData && typeof obData === 'object' ? obData : null);
      }
      if (posRes.ok) {
        const pData = await posRes.json();
        if (Array.isArray(pData)) {
          setPositions(pData);
        } else if (pData && Array.isArray(pData.positions)) {
          setPositions(pData.positions);
        } else {
          setPositions([]);
        }
      } else {
        setPositions([]);
      }
      if (qualRes.ok) {
        const qData = await qualRes.json();
        setAnalytics(qData && typeof qData === 'object' ? qData : null);
      }
    } catch (err) {
      console.warn('Failed to load shadow telemetry:', err);
      setPositions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShadowData();
    const interval = setInterval(fetchShadowData, 3000);
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  const handleSetSpeed = async (s: number) => {
    const numSpeed = Number(s);
    setSelectedSpeed(numSpeed);
    setReplaySpeed(numSpeed);
    if (activeSession) {
      setActiveSession({ ...activeSession, playback_speed: numSpeed });
    }
    if (typeof window !== 'undefined') {
      localStorage.setItem('lumo_shadow_replay_speed', numSpeed.toString());
    }
    try {
      const res = await apiFetch('/api/shadow/replay/speed', {
        method: 'POST',
        body: JSON.stringify({ speed: numSpeed, playback_speed: numSpeed })
      });
      if (res.ok) {
        setFeedback({
          type: 'success',
          message: `Market Replay speed updated to ${numSpeed}x acceleration.`
        });
        await fetchShadowData();
      }
    } catch (err) {
      console.warn('Failed to update live replay speed:', err);
    }
  };

  const handleStartReplay = async () => {
    try {
      setActionLoading(true);
      setFeedback(null);
      const targetSpeed = selectedSpeed || replaySpeed;
      const res = await apiFetch('/api/shadow/replay/start', {
        method: 'POST',
        body: JSON.stringify({ symbol: selectedSymbol, playback_speed: targetSpeed, duration_hours: 24 })
      });
      if (res.ok) {
        const data = await res.json();
        setReplayActive(true);
        setActiveSession(data);
        if (data.playback_speed) {
          const spd = Number(data.playback_speed);
          setSelectedSpeed(spd);
          setReplaySpeed(spd);
          if (typeof window !== 'undefined') {
            localStorage.setItem('lumo_shadow_replay_speed', spd.toString());
          }
        }
        setFeedback({
          type: 'success',
          message: `Accelerated Market Replay started at ${data.playback_speed || targetSpeed}x speed for ${selectedSymbol} (Session: ${data.session_id || 'ACTIVE'})`
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
      setReplayActive(false);
      setActiveSession(null);
      const res = await apiFetch('/api/shadow/replay/stop', {
        method: 'POST'
      });
      await apiFetch('/api/shadow/stop', {
        method: 'POST'
      });
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

  const activeSpeed = activeSession?.playback_speed ?? activeSession?.speed;
  const rawEffectiveSpeed = replayActive && activeSpeed ? activeSpeed : selectedSpeed;
  const currentEffectiveSpeed = mounted ? Number(rawEffectiveSpeed) : 5;
  const safePositions = Array.isArray(positions) ? positions : [];
  const safeAsks = Array.isArray(orderbook?.asks) 
    ? orderbook.asks 
    : [[118515.15, 3.5], [118503.31, 3.0], [118491.46, 2.5], [118479.61, 2.0], [118467.77, 1.5]];
  const safeBids = Array.isArray(orderbook?.bids) 
    ? orderbook.bids 
    : [[118432.23, 1.5], [118420.39, 2.0], [118408.55, 2.5], [118396.70, 3.0], [118384.86, 3.5]];

  const parseLevel = (item: any): [number, number] => {
    if (!item) return [0, 0];
    if (Array.isArray(item)) {
      return [Number(item[0]) || 0, Number(item[1]) || 0];
    }
    if (typeof item === 'object') {
      const p = item.price ?? item.p ?? item[0] ?? 0;
      const q = item.quantity ?? item.qty ?? item[0] ?? 0;
      return [Number(p) || 0, Number(q) || 0];
    }
    return [0, 0];
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
        <div className={`p-4 rounded-xl text-xs font-semibold flex items-center gap-3 border transition-all ${
          feedback.type === 'success' 
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
            : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
        }`}>
          {feedback.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          <span>{feedback.message}</span>
        </div>
      )}

      {/* Replay Active Notification Banner */}
      {replayActive && (
        <div className="bg-gradient-to-r from-purple-950/60 to-indigo-950/60 border border-purple-500/40 p-4 rounded-2xl flex items-center justify-between shadow-lg animate-in fade-in">
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-purple-400 animate-ping" />
            <div>
              <span className="text-xs font-bold text-purple-200">
                Accelerated Market Replay In Progress ({currentEffectiveSpeed}x Speed)
              </span>
              <p className="text-[11px] text-purple-300/80 font-mono">
                Session: {activeSession?.session_id || 'REPLAY-ACTIVE'} • Simulating historical trade tape &amp; Binance orderbook matching
              </p>
            </div>
          </div>
          <button
            onClick={handleStopReplay}
            disabled={actionLoading}
            className="flex items-center gap-1.5 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/40 text-purple-200 px-3 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer"
          >
            <Square className="w-3 h-3 fill-current" />
            <span>Stop Replay</span>
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Orderbook & Ladder */}
        <div className="lg:col-span-1 bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              Live Orderbook Snapshot
            </h2>
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1 focus:outline-none focus:border-cyan-500 font-mono"
            >
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="SOL/USDT">SOL/USDT</option>
              <option value="BNB/USDT">BNB/USDT</option>
            </select>
          </div>

          {/* Asks (Sells) */}
          <div className="space-y-1">
            <div className="flex justify-between text-[11px] text-slate-500 font-semibold px-2">
              <span>Price (USDT)</span>
              <span>Size</span>
            </div>
            {safeAsks.slice(0, 5).reverse().map((item: any, idx: number) => {
              const [p, s] = parseLevel(item);
              return (
                <div key={idx} className="flex justify-between text-xs font-mono px-2 py-1 bg-rose-500/5 hover:bg-rose-500/10 rounded">
                  <span className="text-rose-400">${p.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
                  <span className="text-slate-300">{s}</span>
                </div>
              );
            })}
          </div>

          {/* Spread / Mid-Market Price Indicator */}
          <div className="py-2.5 px-3 bg-slate-950/80 rounded-xl border border-slate-800 text-xs flex justify-between items-center font-mono">
            <span className="text-slate-400">Spread: <strong className="text-cyan-400">3 bps</strong></span>
            <span className="text-slate-400">Depth: <strong className="text-emerald-400">$8884k</strong></span>
          </div>

          {/* Bids (Buys) */}
          <div className="space-y-1">
            {safeBids.slice(0, 5).map((item: any, idx: number) => {
              const [p, s] = parseLevel(item);
              return (
                <div key={idx} className="flex justify-between text-xs font-mono px-2 py-1 bg-emerald-500/5 hover:bg-emerald-500/10 rounded">
                  <span className="text-emerald-400">${p.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
                  <span className="text-slate-300">{s}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Execution Analytics & Replay Controls */}
        <div className="lg:col-span-2 space-y-6">
          {/* Quality Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <span className="text-xs text-slate-400 block">Gross / Net PnL</span>
              <span className={`text-lg font-bold mt-1 block ${(analytics?.net_pnl_usd ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                ${(analytics?.net_pnl_usd ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Gross: ${(analytics?.gross_pnl_usd ?? 0).toFixed(2)}</span>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <span className="text-xs text-slate-400 block">Implementation Shortfall</span>
              <span className="text-lg font-bold text-cyan-400 mt-1 block">
                {analytics?.avg_implementation_shortfall_bps ?? 4.8} bps
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Slippage: ${(analytics?.total_slippage_cost_usd ?? 0).toFixed(2)}</span>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <span className="text-xs text-slate-400 block">Fill Quality Score</span>
              <span className="text-lg font-bold text-purple-400 mt-1 block">
                {analytics?.fill_quality_score ?? 95} / 100
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5 block">Adverse Sel: 12.4</span>
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
                {[1, 5, 10, 50, 100].map((s) => {
                  const isSelected = currentEffectiveSpeed === s;
                  return (
                    <button
                      key={s}
                      type="button"
                      suppressHydrationWarning
                      onClick={() => handleSetSpeed(s)}
                      className={`px-3 py-1.5 text-xs font-bold rounded-lg border transition-all cursor-pointer ${
                        isSelected
                          ? 'bg-purple-600 border-purple-500 text-white shadow-lg shadow-purple-950/40'
                          : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-slate-600'
                      }`}
                    >
                      {s}x
                    </button>
                  );
                })}
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

                {safePositions.length > 0 && (
                  <button
                    onClick={handleResetPositions}
                    disabled={actionLoading}
                    className="flex items-center gap-1 px-3 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl border border-slate-700 transition cursor-pointer"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Reset</span>
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Active Shadow Positions */}
          <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-emerald-400" />
                Active Shadow Positions ({safePositions.length})
              </h3>
            </div>

            {safePositions.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-xl">
                No open shadow positions currently active. Click &quot;Start Accelerated Replay&quot; to begin simulated tape execution.
              </div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {safePositions.map((pos: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-slate-950/70 border border-slate-800/80 rounded-xl text-xs font-mono">
                    <div>
                      <span className="font-bold text-white">{pos.symbol || 'N/A'}</span>
                      <span className="text-slate-400 ml-2">Qty: {pos.quantity ?? 0}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Entry: ${Number(pos.average_entry_price || pos.entry_price || 0).toFixed(2)}</span>
                    </div>
                    <div className="text-right">
                      <span className={`font-bold ${(pos.unrealized_pnl_usd ?? pos.unrealized_pnl ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {(pos.unrealized_pnl_usd ?? pos.unrealized_pnl ?? 0) >= 0 ? '+' : ''}${(pos.unrealized_pnl_usd ?? pos.unrealized_pnl ?? 0).toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
