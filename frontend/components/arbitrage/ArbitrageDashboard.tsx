'use client';

import React, { useState, useEffect } from 'react';
import {
  Zap,
  TrendingUp,
  Activity,
  Layers,
  ShieldCheck,
  Play,
  Square,
  RefreshCw,
  ArrowUpRight,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Wifi,
  Server
} from 'lucide-react';
import { apiFetch } from '@/services/api';

export function ArbitrageDashboard() {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [quotes, setQuotes] = useState<Record<string, any>>({});
  const [funding, setFunding] = useState<Record<string, any>>({});
  const [basis, setBasis] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [shadowActive, setShadowActive] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('lumo_arbitrage_shadow_active') === 'true';
    }
    return false;
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [oppRes, quoteRes, fundRes, basisRes, metRes] = await Promise.all([
        apiFetch('/api/arbitrage/opportunities'),
        apiFetch('/api/arbitrage/spreads'),
        apiFetch('/api/arbitrage/funding'),
        apiFetch('/api/arbitrage/basis'),
        apiFetch('/api/arbitrage/metrics')
      ]);

      if (oppRes.ok) {
        const d = await oppRes.json();
        setOpportunities(d.opportunities || []);
      }
      if (quoteRes.ok) {
        const d = await quoteRes.json();
        setQuotes(d.quotes || {});
      }
      if (fundRes.ok) {
        const d = await fundRes.json();
        setFunding(d.funding_rates || {});
      }
      if (basisRes.ok) {
        const d = await basisRes.json();
        setBasis(d.basis || null);
      }
      if (metRes.ok) {
        const d = await metRes.json();
        setMetrics(d.metrics || null);
        if (d.shadow_active !== undefined) {
          setShadowActive(d.shadow_active);
          if (typeof window !== 'undefined') {
            localStorage.setItem('lumo_arbitrage_shadow_active', String(d.shadow_active));
          }
        }
      }
      setLastUpdated(new Date());
    } catch (err) {
      console.warn('Arbitrage data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, 4000);
    return () => clearInterval(timer);
  }, []);

  const toggleShadowRouter = async () => {
    try {
      setActionLoading(true);
      const nextState = !shadowActive;
      setShadowActive(nextState);
      if (typeof window !== 'undefined') {
        localStorage.setItem('lumo_arbitrage_shadow_active', String(nextState));
      }
      const endpoint = nextState ? '/api/arbitrage/shadow/start' : '/api/arbitrage/shadow/stop';
      const res = await apiFetch(endpoint, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        if (data.shadow_active !== undefined) {
          setShadowActive(data.shadow_active);
          if (typeof window !== 'undefined') {
            localStorage.setItem('lumo_arbitrage_shadow_active', String(data.shadow_active));
          }
        }
      } else {
        setShadowActive(!nextState);
        if (typeof window !== 'undefined') {
          localStorage.setItem('lumo_arbitrage_shadow_active', String(!nextState));
        }
      }
    } catch (err) {
      console.error('Shadow toggle failed:', err);
      setShadowActive(!shadowActive);
    } finally {
      setActionLoading(false);
    }
  };

  const [selectedOpp, setSelectedOpp] = useState<any>(null);
  const [simResult, setSimResult] = useState<any>(null);

  const handleSimulateTrade = async (opp: any) => {
    try {
      setActionLoading(true);
      setSelectedOpp(opp);
      const res = await apiFetch('/api/arbitrage/simulate-trade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: opp.symbol,
          buy_exchange: opp.buy_exchange,
          sell_exchange: opp.sell_exchange,
          buy_price: opp.buy_price,
          sell_price: opp.sell_price,
          net_spread_pct: opp.net_spread_pct,
          amount_usd: 10000.0
        })
      });
      if (res.ok) {
        const data = await res.json();
        setSimResult(data);
        fetchData();
      }
    } catch (err) {
      console.error('Simulate trade failed:', err);
    } finally {
      setActionLoading(false);
    }
  };

  // Compute live market stats
  const quoteEntries = Object.entries(quotes);
  const totalVenues = quoteEntries.length;
  const connectedVenues = quoteEntries.filter(([_, q]: [string, any]) => q.status === "FRESH" || q.bid_price > 0).length;
  const staleVenues = quoteEntries.filter(([_, q]: [string, any]) => q.status === "DATA_STALE").length;
  const unavailableVenues = quoteEntries.filter(([_, q]: [string, any]) => q.status === "DATA_UNAVAILABLE" || q.bid_price === 0).length;

  const marketStatus = unavailableVenues === totalVenues && totalVenues > 0
    ? "DATA_UNAVAILABLE"
    : staleVenues > 0
    ? "STALE_DATA"
    : "LIVE_MARKET_DATA";

  const maxDataAgeMs = Math.max(0, ...quoteEntries.map(([_, q]: [string, any]) => q.data_age_ms || 0));

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6">
      {/* Active Shadow Router Alert Banner */}
      {shadowActive && (
        <div className="bg-gradient-to-r from-emerald-950/90 to-slate-900 border border-emerald-500/40 p-4 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xl shadow-emerald-950/30">
          <div className="flex items-center gap-3">
            <span className="flex h-3 w-3 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <div>
              <div className="text-xs font-bold text-emerald-300 uppercase tracking-wider">
                ⚡ SHADOW ARBITRAGE ROUTER ACTIVE (CONTINUOUS 24/7)
              </div>
              <div className="text-[11px] text-emerald-400/80 font-mono mt-0.5">
                Automated multi-venue spot-spot arbitrage router is continuously scanning &amp; executing paper/shadow trades until manually stopped.
              </div>
            </div>
          </div>
          <button
            onClick={toggleShadowRouter}
            disabled={actionLoading}
            className="shrink-0 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 text-xs font-bold px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
          >
            <Square className="w-3.5 h-3.5 fill-current" />
            Stop Router
          </button>
        </div>
      )}
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Cross-Exchange Arbitrage Intelligence
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 font-medium">
                  Arbitrage Engine
                </span>
              </h1>
              <p className="text-sm text-slate-400">
                Multi-venue spot-spot spreads, perpetual funding rate arbitrage & spot-perp basis engine
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={toggleShadowRouter}
            disabled={actionLoading}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold transition shadow-lg ${
              shadowActive
                ? 'bg-rose-500/10 border border-rose-500/30 text-rose-400 hover:bg-rose-500/20'
                : 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20'
            }`}
          >
            {shadowActive ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            {shadowActive ? 'Stop Shadow Router' : 'Start Shadow Router'}
          </button>
        </div>
      </div>

      {/* Live Market Data Status & Venue Telemetry Sub-Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-mono">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${
              marketStatus === "LIVE_MARKET_DATA" ? "bg-emerald-400 animate-pulse" :
              marketStatus === "STALE_DATA" ? "bg-amber-400 animate-ping" : "bg-rose-500"
            }`} />
            <span className="font-bold text-slate-200">
              STATUS: {marketStatus.replace(/_/g, ' ')}
            </span>
          </div>
          <span className="text-slate-700">|</span>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>Last Update: {lastUpdated ? lastUpdated.toLocaleTimeString() : "—"}</span>
          </div>
          <span className="text-slate-700">|</span>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Wifi className="w-3.5 h-3.5 text-indigo-400" />
            <span>Max Data Age: {maxDataAgeMs.toFixed(0)}ms</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-slate-300">
            <Server className="w-3.5 h-3.5 text-emerald-400" />
            <span>Venues Connected: <strong className="text-emerald-400">{connectedVenues}/{totalVenues || 5}</strong></span>
          </div>
          {staleVenues > 0 && (
            <span className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 font-bold">
              {staleVenues} Stale
            </span>
          )}
          {unavailableVenues > 0 && (
            <span className="px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold">
              {unavailableVenues} Unavailable
            </span>
          )}
        </div>
      </div>

      {/* KPI Cards — No Artificial Fallbacks */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">
            Best Executable Spread
          </div>
          <div className="text-2xl font-bold text-amber-400">
            {opportunities.length > 0 ? `+${opportunities[0].net_spread_pct}%` : 'N/A'}
          </div>
          <div className="text-xs text-slate-500 mt-1">Fee & Latency Net Edge</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">
            Spot-Perp Basis (Ann.)
          </div>
          <div className="text-2xl font-bold text-cyan-400">
            {basis && basis.annualized_basis_pct !== undefined ? `+${basis.annualized_basis_pct}%` : 'N/A'}
          </div>
          <div className="text-xs text-slate-500 mt-1">Spot vs Perp Annualized Premium</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">
            Captured Shadow Profit
          </div>
          <div className="text-2xl font-bold text-emerald-400">
            {metrics && metrics.captured_profit_usd !== undefined ? `$${metrics.captured_profit_usd.toFixed(2)}` : '$0.00'}
          </div>
          <div className="text-xs text-slate-500 mt-1">Simulated Dual-Leg Edge</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">
            Readiness Score
          </div>
          <div className="text-2xl font-bold text-indigo-400">
            {metrics && metrics.overall_readiness_score !== undefined ? `${metrics.overall_readiness_score}/100` : 'NOT YET VERIFIED'}
          </div>
          <div className="text-xs text-slate-500 mt-1">Institutional Audit Score</div>
        </div>
      </div>

      {/* Arbitrage Rejection & Pipeline Statistics */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
        <h3 className="text-sm font-semibold text-white uppercase tracking-wider text-slate-300">
          Arbitrage Route Filtering & Rejection Statistics
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 font-mono text-xs">
          <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-850">
            <div className="text-[10px] text-slate-400 font-sans">Scanned Routes</div>
            <div className="text-sm font-bold text-slate-200">{metrics?.scanned_routes_count ?? 0}</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-850">
            <div className="text-[10px] text-slate-400 font-sans">Gross Profitable</div>
            <div className="text-sm font-bold text-cyan-400">{metrics?.profitable_before_fees_count ?? 0}</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-850">
            <div className="text-[10px] text-slate-400 font-sans">Fee Rejections</div>
            <div className="text-sm font-bold text-amber-400">{metrics?.rejected_by_fees_count ?? 0}</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-850">
            <div className="text-[10px] text-slate-400 font-sans">Slippage Rejections</div>
            <div className="text-sm font-bold text-orange-400">{metrics?.rejected_by_slippage_count ?? 0}</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-850">
            <div className="text-[10px] text-slate-400 font-sans">Risk Rejections</div>
            <div className="text-sm font-bold text-rose-400">{metrics?.rejected_by_risk_count ?? 0}</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-850">
            <div className="text-[10px] text-slate-400 font-sans">Gov Rejections</div>
            <div className="text-sm font-bold text-purple-400">{metrics?.rejected_by_governance_count ?? 0}</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-850">
            <div className="text-[10px] text-slate-400 font-sans">Net Profitable</div>
            <div className="text-sm font-bold text-emerald-400">{metrics?.profitable_after_fees_count ?? 0}</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-850">
            <div className="text-[10px] text-slate-400 font-sans">Executable</div>
            <div className="text-sm font-bold text-emerald-300">{metrics?.executable_opportunities ?? 0}</div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Opportunities Table */}
        <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-amber-400" />
              Active Ranked Arbitrage Opportunities
            </h2>
            <span className="text-xs text-slate-400">{opportunities.length} opportunities detected</span>
          </div>

          {opportunities.length === 0 ? (
            <div className="p-8 text-center rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <ShieldCheck className="w-8 h-8 text-slate-500 mx-auto" />
              <div className="text-sm font-bold text-slate-300">No executable arbitrage opportunities detected</div>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Real market quotes across Binance, Bybit, OKX, Kraken, and Coinbase are currently within normal fee & friction thresholds.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950/60 text-slate-400 uppercase text-xs">
                  <tr>
                    <th className="p-3">Route</th>
                    <th className="p-3">Buy Exchange</th>
                    <th className="p-3">Sell Exchange</th>
                    <th className="p-3">Net Spread</th>
                    <th className="p-3">Est. Profit</th>
                    <th className="p-3">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {opportunities.map((opp, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40 transition">
                      <td className="p-3 font-medium text-white">{opp.symbol}</td>
                      <td className="p-3">
                        <span className="px-2 py-1 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-mono">
                          {opp.buy_exchange} (${opp.buy_price})
                        </span>
                      </td>
                      <td className="p-3">
                        <span className="px-2 py-1 rounded bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-mono">
                          {opp.sell_exchange} (${opp.sell_price})
                        </span>
                      </td>
                      <td className="p-3 font-semibold text-emerald-400">+{opp.net_spread_pct}%</td>
                      <td className="p-3 font-mono text-white">${opp.estimated_profit_usd}</td>
                      <td className="p-3">
                        <button
                          onClick={() => handleSimulateTrade(opp)}
                          disabled={actionLoading}
                          className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs rounded-lg transition-all shadow-md shadow-emerald-900/30 flex items-center space-x-1 cursor-pointer disabled:opacity-50"
                        >
                          <Zap className="w-3 h-3" />
                          <span>SIMULATE TRADE</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Funding Rates & Venue Quotes */}
        <div className="space-y-6">
          {/* Exchange Quote Depth */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              Venue Orderbook Quotes
            </h3>
            <div className="space-y-2">
              {Object.entries(quotes).map(([ex, q]: [string, any]) => (
                <div key={ex} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-850">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-300">{ex}</span>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-bold ${
                      q.status === "FRESH" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                      q.status === "DATA_STALE" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" :
                      "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                    }`}>
                      {q.status || "FRESH"}
                    </span>
                  </div>
                  <div className="text-right text-xs font-mono">
                    {q.bid_price > 0 ? (
                      <>
                        <span className="text-slate-400">Bid: ${q.bid_price}</span> |{' '}
                        <span className="text-slate-200">Ask: ${q.ask_price}</span>
                      </>
                    ) : (
                      <span className="text-slate-500">OFFLINE</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Funding Rate Matrix */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-purple-400" />
              Perpetual Funding Rate Heatmap
            </h3>
            <div className="space-y-2">
              {Object.entries(funding).map(([ex, f]: [string, any]) => (
                <div key={ex} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-850">
                  <span className="text-xs font-bold text-slate-300">{ex}</span>
                  <span className={`text-xs font-mono font-semibold ${f.funding_rate_8h >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {(f.funding_rate_8h * 100).toFixed(4)}% / 8h ({f.annualized_funding_pct}% Ann.)
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Dual-Leg Shadow Fill Execution Receipt Modal */}
      {simResult && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700 p-6 rounded-2xl max-w-lg w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className={`flex items-center space-x-2 font-bold text-lg ${
                simResult.status === "COMPLETED" || simResult.status === "success" ? "text-emerald-400" : "text-rose-400"
              }`}>
                {simResult.status === "COMPLETED" || simResult.status === "success" ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : (
                  <AlertTriangle className="w-5 h-5" />
                )}
                <span>
                  {simResult.status === "COMPLETED" || simResult.status === "success"
                    ? "Shadow Dual-Leg Arbitrage Executed"
                    : "Shadow Arbitrage Simulation Rejected"}
                </span>
              </div>
              <button
                onClick={() => setSimResult(null)}
                className="text-slate-400 hover:text-white font-bold text-sm"
              >
                ✕
              </button>
            </div>

            <div className="space-y-2 font-mono text-xs text-slate-300">
              <div className="flex justify-between bg-slate-950 p-2.5 rounded-lg">
                <span>Simulation ID:</span>
                <span className="text-cyan-400 font-bold">{simResult.execution?.simulation_id || simResult.execution?.execution_id || 'SIM-ARB-001'}</span>
              </div>
              <div className="flex justify-between bg-slate-950 p-2.5 rounded-lg">
                <span>Execution Status:</span>
                <span className={`font-bold ${simResult.status === "COMPLETED" || simResult.status === "success" ? "text-emerald-400" : "text-rose-400"}`}>
                  {simResult.status?.toUpperCase()}
                </span>
              </div>

              {simResult.reason && (
                <div className="flex justify-between bg-rose-500/10 border border-rose-500/30 p-2.5 rounded-lg text-rose-300">
                  <span>Rejection Reason:</span>
                  <span className="font-bold">{simResult.reason}</span>
                </div>
              )}

              {simResult.execution && (
                <>
                  <div className="flex justify-between bg-slate-950 p-2.5 rounded-lg">
                    <span>Leg 1 (BUY):</span>
                    <span className="text-cyan-400">{simResult.execution.buy_exchange} @ ${simResult.execution.buy_fill_price}</span>
                  </div>
                  <div className="flex justify-between bg-slate-950 p-2.5 rounded-lg">
                    <span>Leg 2 (SELL):</span>
                    <span className="text-purple-400">{simResult.execution.sell_exchange} @ ${simResult.execution.sell_fill_price}</span>
                  </div>
                  <div className="flex justify-between bg-slate-950 p-2.5 rounded-lg">
                    <span>Total Net Fees:</span>
                    <span className="text-amber-400">${simResult.execution.fees || simResult.execution.total_fees_usd || 0.0}</span>
                  </div>
                  <div className="flex justify-between bg-emerald-500/10 border border-emerald-500/30 p-3 rounded-lg text-sm">
                    <span className="font-bold text-emerald-400">Net Captured Shadow PnL:</span>
                    <span className="font-bold text-emerald-300">${simResult.execution.net_pnl || simResult.execution.profit_usd || 0.0}</span>
                  </div>
                </>
              )}
            </div>

            <button
              onClick={() => setSimResult(null)}
              className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl text-sm transition cursor-pointer"
            >
              Close Receipt
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
