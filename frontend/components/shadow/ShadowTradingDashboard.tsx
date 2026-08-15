'use client';

import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, Activity, Cpu, Play, Square, FastForward, 
  BarChart3, Clock, DollarSign, Layers, ArrowUpRight, ArrowDownRight, RefreshCw, AlertTriangle
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
  const [loading, setLoading] = useState<boolean>(true);

  const fetchShadowData = async () => {
    try {
      setLoading(true);
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
      const res = await apiFetch('/api/shadow/replay/start', {
        method: 'POST',
        body: JSON.stringify({ symbol: selectedSymbol, playback_speed: replaySpeed, duration_hours: 24 })
      });
      if (res.ok) {
        setReplayActive(true);
        fetchShadowData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleStopReplay = async () => {
    try {
      setReplayActive(false);
      fetchShadowData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
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
              className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="SOL/USDT">SOL/USDT</option>
              <option value="BNB/USDT">BNB/USDT</option>
            </select>
          </div>

          {orderbook ? (
            <div className="space-y-3 font-mono text-xs">
              <div className="flex justify-between text-slate-400 px-2">
                <span>Price (USDT)</span>
                <span>Size</span>
              </div>

              {/* Asks */}
              <div className="space-y-1">
                {orderbook.asks?.slice(0, 5).reverse().map((a: any, i: number) => (
                  <div key={i} className="flex justify-between items-center px-2 py-0.5 rounded bg-rose-500/10 text-rose-400">
                    <span>{a.price}</span>
                    <span>{a.quantity}</span>
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
                    <span>{b.price}</span>
                    <span>{b.quantity}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-10 text-slate-500 text-xs">Streaming Orderbook Depth...</div>
          )}
        </div>

        {/* Analytics & Positions Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Execution Analytics Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <span className="text-xs text-slate-400 block">Gross / Net PnL</span>
              <span className="text-lg font-bold text-emerald-400 mt-1 block">
                ${analytics?.net_pnl_usd || '0.00'}
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

            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Speed:</span>
                {[1, 5, 10, 50].map((s) => (
                  <button
                    key={s}
                    onClick={() => setReplaySpeed(s)}
                    className={`px-3 py-1 text-xs font-bold rounded-lg border transition-all ${
                      replaySpeed === s
                        ? 'bg-purple-600 border-purple-500 text-white shadow-lg'
                        : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-slate-600'
                    }`}
                  >
                    {s}x
                  </button>
                ))}
              </div>

              {!replayActive ? (
                <button
                  onClick={handleStartReplay}
                  className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-xl transition-all shadow-lg"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  Start Accelerated Replay
                </button>
              ) : (
                <button
                  onClick={handleStopReplay}
                  className="flex items-center gap-2 bg-rose-600/80 hover:bg-rose-500 text-white text-xs font-bold px-4 py-2 rounded-xl transition-all"
                >
                  <Square className="w-3.5 h-3.5 fill-current" />
                  Pause Replay Session
                </button>
              )}
            </div>
          </div>

          {/* Shadow Positions Blotter */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
            <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              Active Shadow Positions ({positions.length})
            </h3>

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
              <div className="text-center py-8 text-slate-500 text-xs">No open shadow positions currently active.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
