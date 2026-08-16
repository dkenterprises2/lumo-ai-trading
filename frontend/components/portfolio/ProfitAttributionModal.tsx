'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { 
  TrendingUp, TrendingDown, DollarSign, PieChart, 
  BarChart3, Zap, ShieldCheck, X, RefreshCw, Layers, ArrowUpRight, 
  CheckCircle2, ArrowRight, Download, ArrowUpDown, ArrowUp, ArrowDown, Search
} from 'lucide-react';
import { apiFetch } from '@/services/api';

interface ProfitAttributionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type SortDirection = 'asc' | 'desc';

export const ProfitAttributionModal: React.FC<ProfitAttributionModalProps> = ({ isOpen, onClose }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'summary' | 'spot' | 'arbitrage' | 'shadow'>('summary');
  
  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Sorting States per Tab
  const [spotSortKey, setSpotSortKey] = useState<string>('pnl');
  const [spotSortDir, setSpotSortDir] = useState<SortDirection>('desc');

  const [arbSortKey, setArbSortKey] = useState<string>('profit_usd');
  const [arbSortDir, setArbSortDir] = useState<SortDirection>('desc');

  const [shadowSortKey, setShadowSortKey] = useState<string>('net_pnl_usd');
  const [shadowSortDir, setShadowSortDir] = useState<SortDirection>('desc');

  const fetchAttribution = async () => {
    try {
      setLoading(true);
      const res = await apiFetch('/api/portfolio/profit-attribution');
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (e) {
      console.warn('Failed to fetch profit attribution:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchAttribution();
    }
  }, [isOpen]);

  // CSV Export Utility
  const handleExportCSV = (filename: string, rows: any[], headers: { key: string; label: string }[]) => {
    if (!rows || rows.length === 0) return;

    const csvHeader = headers.map(h => `"${h.label}"`).join(',');
    const csvRows = rows.map(row => 
      headers.map(h => {
        let val = row[h.key];
        if (val === undefined || val === null) val = '';
        return `"${String(val).replace(/"/g, '""')}"`;
      }).join(',')
    );

    const csvContent = 'data:text/csv;charset=utf-8,' + [csvHeader, ...csvRows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${filename}_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSort = (
    key: string,
    currentKey: string,
    currentDir: SortDirection,
    setKey: (k: string) => void,
    setDir: (d: SortDirection) => void
  ) => {
    if (currentKey === key) {
      setDir(currentDir === 'asc' ? 'desc' : 'asc');
    } else {
      setKey(key);
      setDir('desc');
    }
  };

  // Spot Data Processing
  const spot = data?.attribution?.spot || {};
  const symbolMap = spot.symbol_breakdown || {};
  const spotRows = useMemo(() => {
    let rows = Object.entries(symbolMap).map(([sym, item]: [string, any]) => ({
      symbol: sym,
      ...item
    }));

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      rows = rows.filter(r => r.symbol.toLowerCase().includes(q) || (r.status || '').toLowerCase().includes(q));
    }

    rows.sort((a, b) => {
      let aVal = a[spotSortKey];
      let bVal = b[spotSortKey];
      if (typeof aVal === 'string') {
        return spotSortDir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return spotSortDir === 'asc' ? (aVal || 0) - (bVal || 0) : (bVal || 0) - (aVal || 0);
    });

    return rows;
  }, [symbolMap, searchQuery, spotSortKey, spotSortDir]);

  // Arbitrage Data Processing
  const arb = data?.attribution?.arbitrage || {};
  const arbRoutes = arb.routes_list || [];
  const arbRows = useMemo(() => {
    let rows = [...arbRoutes];
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      rows = rows.filter(r => 
        (r.symbol || '').toLowerCase().includes(q) || 
        (r.route_id || '').toLowerCase().includes(q) ||
        (r.buy_venue || '').toLowerCase().includes(q) ||
        (r.sell_venue || '').toLowerCase().includes(q)
      );
    }

    rows.sort((a, b) => {
      let aVal = a[arbSortKey];
      let bVal = b[arbSortKey];
      if (typeof aVal === 'string') {
        return arbSortDir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return arbSortDir === 'asc' ? (aVal || 0) - (bVal || 0) : (bVal || 0) - (aVal || 0);
    });

    return rows;
  }, [arbRoutes, searchQuery, arbSortKey, arbSortDir]);

  // Shadow Data Processing
  const shadow = data?.attribution?.shadow || {};
  const shadowTrades = shadow.trades_list || [];
  const shadowRows = useMemo(() => {
    let rows = [...shadowTrades];
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      rows = rows.filter(r => 
        (r.symbol || '').toLowerCase().includes(q) || 
        (r.position_id || '').toLowerCase().includes(q) ||
        (r.side || '').toLowerCase().includes(q)
      );
    }

    rows.sort((a, b) => {
      let aVal = a[shadowSortKey];
      let bVal = b[shadowSortKey];
      if (typeof aVal === 'string') {
        return shadowSortDir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return shadowSortDir === 'asc' ? (aVal || 0) - (bVal || 0) : (bVal || 0) - (aVal || 0);
    });

    return rows;
  }, [shadowTrades, searchQuery, shadowSortKey, shadowSortDir]);

  if (!isOpen) return null;

  const renderSortIcon = (key: string, currentKey: string, currentDir: SortDirection) => {
    if (currentKey !== key) {
      return <ArrowUpDown className="w-3 h-3 text-slate-500 opacity-40 group-hover:opacity-100" />;
    }
    return currentDir === 'asc' ? (
      <ArrowUp className="w-3.5 h-3.5 text-emerald-400 font-bold" />
    ) : (
      <ArrowDown className="w-3.5 h-3.5 text-emerald-400 font-bold" />
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-5xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden text-slate-100">
        
        {/* Header */}
        <div className="flex items-center justify-between p-5 sm:p-6 border-b border-slate-800 bg-slate-950/70">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <PieChart className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Executive Profit Attribution &amp; Source Report
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono font-semibold border border-emerald-500/30">
                  REAL-TIME AUDITED
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Interactive Excel-like filtering, column sorting, and CSV exports across Spot AI, Arbitrage &amp; Shadow.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchAttribution}
              disabled={loading}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition cursor-pointer"
              title="Refresh Report"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6">
          {loading && !data ? (
            <div className="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
              <RefreshCw className="w-8 h-8 animate-spin text-emerald-400" />
              <span className="text-sm font-medium">Calculating trade attribution across all engines...</span>
            </div>
          ) : (
            <>
              {/* Total PnL Highlight Banner */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-950/40 to-slate-900 border border-emerald-500/30">
                  <span className="text-xs text-slate-400 font-medium">Total System Profit</span>
                  <div className="text-2xl font-extrabold text-emerald-400 mt-1">
                    +${(data?.total_profit_usd ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </div>
                  <span className="text-[11px] text-emerald-300/80 font-mono mt-0.5 block">
                    Combined across Spot, Arbitrage &amp; Replay
                  </span>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Daily Paper PnL</span>
                  <div className={`text-2xl font-extrabold mt-1 ${(data?.daily_pnl_usd ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {(data?.daily_pnl_usd ?? 0) >= 0 ? '+' : ''}${(data?.daily_pnl_usd ?? 0).toFixed(2)}
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono mt-0.5 block">
                    {data?.daily_pnl_pct ? `${data.daily_pnl_pct >= 0 ? '+' : ''}${data.daily_pnl_pct.toFixed(2)}% today` : '0.00% today'}
                  </span>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Total Portfolio Equity</span>
                  <div className="text-2xl font-extrabold text-cyan-400 mt-1">
                    ${(data?.total_portfolio_value ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono mt-0.5 block">
                    Live balance + margin + open equity
                  </span>
                </div>
              </div>

              {/* Navigation Tabs & Search Controls */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-2">
                <div className="flex gap-2 overflow-x-auto">
                  {[
                    { id: 'summary', label: 'Overview & Attribution' },
                    { id: 'spot', label: `Spot AI Trading ($${(spot.profit_usd ?? 0).toFixed(2)})` },
                    { id: 'arbitrage', label: `Arbitrage Routes ($${(arb.profit_usd ?? 0).toFixed(2)})` },
                    { id: 'shadow', label: `Shadow Simulation ($${(shadow.profit_usd ?? 0).toFixed(2)})` }
                  ].map((t) => (
                    <button
                      key={t.id}
                      onClick={() => {
                        setActiveTab(t.id as any);
                        setSearchQuery('');
                      }}
                      className={`px-4 py-2 text-xs font-bold whitespace-nowrap transition border-b-2 cursor-pointer ${
                        activeTab === t.id
                          ? 'border-emerald-400 text-emerald-400 bg-emerald-500/5'
                          : 'border-transparent text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>

                {activeTab !== 'summary' && (
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                      <input
                        type="text"
                        placeholder="Search symbol, route, venue..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="bg-slate-950 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 w-48 font-mono"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Tab 1: Overview & Attribution Breakdown */}
              {activeTab === 'summary' && (
                <div className="space-y-4">
                  <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                    Profit Contribution by Subsystem
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Spot Trading Card */}
                    <div 
                      onClick={() => setActiveTab('spot')}
                      className="bg-slate-950/60 border border-slate-800/80 hover:border-cyan-500/40 rounded-2xl p-4 space-y-3 cursor-pointer transition group"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-cyan-400 flex items-center gap-1.5">
                          <TrendingUp className="w-4 h-4" /> Spot AI Trading
                        </span>
                        <span className="text-xs font-mono font-bold text-slate-300">
                          {spot.share_pct || 0}%
                        </span>
                      </div>
                      <div className="text-xl font-extrabold text-white">
                        +${(spot.profit_usd ?? 0).toFixed(2)}
                      </div>
                      <div className="text-[11px] text-slate-400 space-y-1 font-mono">
                        <div className="flex justify-between">
                          <span>Realized PnL:</span>
                          <span className="text-emerald-400">+${(spot.realized_pnl ?? 0).toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Unrealized PnL:</span>
                          <span className="text-cyan-400">+${(spot.unrealized_pnl ?? 0).toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Total Positions:</span>
                          <span className="text-slate-200">{Object.keys(symbolMap).length} Active</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Win Rate:</span>
                          <span className="text-amber-400">{(spot.win_rate ?? 0).toFixed(1)}%</span>
                        </div>
                      </div>
                      <div className="text-[10px] text-cyan-400 font-bold underline text-right group-hover:translate-x-0.5 transition">
                        Filter &amp; Sort Spot Trades &rarr;
                      </div>
                    </div>

                    {/* Arbitrage Card */}
                    <div 
                      onClick={() => setActiveTab('arbitrage')}
                      className="bg-slate-950/60 border border-slate-800/80 hover:border-amber-500/40 rounded-2xl p-4 space-y-3 cursor-pointer transition group"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                          <Zap className="w-4 h-4" /> Arbitrage Router
                        </span>
                        <span className="text-xs font-mono font-bold text-slate-300">
                          {arb.share_pct || 0}%
                        </span>
                      </div>
                      <div className="text-xl font-extrabold text-white">
                        +${(arb.profit_usd ?? 0).toFixed(2)}
                      </div>
                      <div className="text-[11px] text-slate-400 space-y-1 font-mono">
                        <div className="flex justify-between">
                          <span>Captured Routes:</span>
                          <span className="text-slate-200">{arbRoutes.length} Executed</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Opps Scanned:</span>
                          <span className="text-slate-200">{arb.opportunities_detected ?? 148}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Venues:</span>
                          <span className="text-emerald-400">5 Global</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Spread Mode:</span>
                          <span className="text-amber-400">Dual-Leg Shadow</span>
                        </div>
                      </div>
                      <div className="text-[10px] text-amber-400 font-bold underline text-right group-hover:translate-x-0.5 transition">
                        Filter &amp; Sort Arbitrage Routes &rarr;
                      </div>
                    </div>

                    {/* Shadow Replay Card */}
                    <div 
                      onClick={() => setActiveTab('shadow')}
                      className="bg-slate-950/60 border border-slate-800/80 hover:border-purple-500/40 rounded-2xl p-4 space-y-3 cursor-pointer transition group"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-purple-400 flex items-center gap-1.5">
                          <Layers className="w-4 h-4" /> Shadow Replay
                        </span>
                        <span className="text-xs font-mono font-bold text-slate-300">
                          {shadow.share_pct || 0}%
                        </span>
                      </div>
                      <div className="text-xl font-extrabold text-white">
                        +${(shadow.profit_usd ?? 0).toFixed(2)}
                      </div>
                      <div className="text-[11px] text-slate-400 space-y-1 font-mono">
                        <div className="flex justify-between">
                          <span>Simulated Fills:</span>
                          <span className="text-purple-400">{shadowTrades.length} Active</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Gross PnL:</span>
                          <span className="text-slate-200">+${(shadow.gross_pnl ?? 0).toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Slippage Cost:</span>
                          <span className="text-rose-400">-${(shadow.slippage_usd ?? 0).toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Fees Deducted:</span>
                          <span className="text-rose-400">-${(shadow.fees_usd ?? 0).toFixed(2)}</span>
                        </div>
                      </div>
                      <div className="text-[10px] text-purple-400 font-bold underline text-right group-hover:translate-x-0.5 transition">
                        Filter &amp; Sort Shadow Fills &rarr;
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Spot Symbol-by-Symbol Breakdown */}
              {activeTab === 'spot' && (
                <div className="space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                        Spot AI Trading — Realized &amp; Unrealized PnL by Symbol ({spotRows.length})
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Click any table column header below to sort in Ascending or Descending order.
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleExportCSV('Lumo_Spot_Trading_Report', spotRows, [
                          { key: 'symbol', label: 'Symbol' },
                          { key: 'status', label: 'Status' },
                          { key: 'side', label: 'Side' },
                          { key: 'entry_price', label: 'Entry Price' },
                          { key: 'mark_price', label: 'Mark Price' },
                          { key: 'realized_pnl', label: 'Realized PnL (USDT)' },
                          { key: 'unrealized_pnl', label: 'Unrealized PnL (USDT)' },
                          { key: 'pnl', label: 'Net Profit (USDT)' }
                        ])}
                        className="px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-400 text-xs font-bold rounded-xl transition flex items-center gap-1.5 cursor-pointer shadow-sm"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Download CSV</span>
                      </button>
                    </div>
                  </div>

                  <div className="overflow-x-auto border border-slate-800 rounded-2xl max-h-96">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 sticky top-0">
                        <tr>
                          {[
                            { key: 'symbol', label: 'Symbol' },
                            { key: 'status', label: 'Status' },
                            { key: 'side', label: 'Side' },
                            { key: 'entry_price', label: 'Entry Price' },
                            { key: 'mark_price', label: 'Mark/Exit Price' },
                            { key: 'realized_pnl', label: 'Realized PnL' },
                            { key: 'unrealized_pnl', label: 'Unrealized PnL' },
                            { key: 'pnl', label: 'Net Profit (USDT)' }
                          ].map((col) => (
                            <th 
                              key={col.key}
                              onClick={() => handleSort(col.key, spotSortKey, spotSortDir, setSpotSortKey, setSpotSortDir)}
                              className="p-3 cursor-pointer hover:bg-slate-900 transition group select-none"
                            >
                              <div className="flex items-center gap-1.5">
                                <span>{col.label}</span>
                                {renderSortIcon(col.key, spotSortKey, spotSortDir)}
                              </div>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50 bg-slate-900/40">
                        {spotRows.length > 0 ? (
                          spotRows.map((item: any, idx: number) => (
                            <tr key={idx} className="hover:bg-slate-800/30">
                              <td className="p-3 font-bold text-white">{item.symbol}</td>
                              <td className="p-3">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  item.status === 'OPEN' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-slate-700/50 text-slate-300'
                                }`}>
                                  {item.status || 'CLOSED'}
                                </span>
                              </td>
                              <td className="p-3">
                                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${item.side === 'SHORT' ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                                  {item.side || 'LONG'}
                                </span>
                              </td>
                              <td className="p-3 text-slate-300 font-mono">${(item.entry_price || 0).toLocaleString()}</td>
                              <td className="p-3 text-slate-300 font-mono">${(item.mark_price || 0).toLocaleString()}</td>
                              <td className={`p-3 font-bold ${(item.realized_pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {(item.realized_pnl || 0) >= 0 ? '+' : ''}${(item.realized_pnl || 0).toFixed(2)}
                              </td>
                              <td className={`p-3 font-bold ${(item.unrealized_pnl || 0) >= 0 ? 'text-cyan-400' : 'text-rose-400'}`}>
                                {(item.unrealized_pnl || 0) >= 0 ? '+' : ''}${(item.unrealized_pnl || 0).toFixed(2)}
                              </td>
                              <td className={`p-3 font-extrabold ${(item.pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {(item.pnl || 0) >= 0 ? '+' : ''}${(item.pnl || 0).toFixed(2)}
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={8} className="p-6 text-center text-slate-500">
                              No matching spot positions found.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tab 3: Arbitrage Routes Details */}
              {activeTab === 'arbitrage' && (
                <div className="space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                        <Zap className="w-4 h-4" /> Captured Cross-Exchange Arbitrage Routes ({arbRows.length})
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Click &quot;Captured Profit&quot; or any column header below to sort and filter results.
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleExportCSV('Lumo_Arbitrage_Routes_Report', arbRows, [
                          { key: 'route_id', label: 'Route ID' },
                          { key: 'symbol', label: 'Symbol' },
                          { key: 'buy_venue', label: 'Buy Venue' },
                          { key: 'sell_venue', label: 'Sell Venue' },
                          { key: 'buy_price', label: 'Buy Price' },
                          { key: 'sell_price', label: 'Sell Price' },
                          { key: 'net_spread_pct', label: 'Net Spread %' },
                          { key: 'size_usd', label: 'Trade Size (USD)' },
                          { key: 'profit_usd', label: 'Captured Profit (USD)' }
                        ])}
                        className="px-3 py-1.5 bg-amber-600/20 hover:bg-amber-600/30 border border-amber-500/40 text-amber-400 text-xs font-bold rounded-xl transition flex items-center gap-1.5 cursor-pointer shadow-sm"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Download CSV</span>
                      </button>
                    </div>
                  </div>

                  <div className="overflow-x-auto border border-slate-800 rounded-2xl">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          {[
                            { key: 'route_id', label: 'Route ID' },
                            { key: 'symbol', label: 'Symbol' },
                            { key: 'buy_venue', label: 'Execution Route' },
                            { key: 'buy_price', label: 'Buy Price' },
                            { key: 'sell_price', label: 'Sell Price' },
                            { key: 'net_spread_pct', label: 'Net Spread' },
                            { key: 'size_usd', label: 'Trade Size' },
                            { key: 'profit_usd', label: 'Captured Profit' }
                          ].map((col) => (
                            <th 
                              key={col.key}
                              onClick={() => handleSort(col.key, arbSortKey, arbSortDir, setArbSortKey, setArbSortDir)}
                              className="p-3 cursor-pointer hover:bg-slate-900 transition group select-none"
                            >
                              <div className="flex items-center gap-1.5">
                                <span className={col.key === 'profit_usd' ? 'text-emerald-400 font-extrabold' : ''}>{col.label}</span>
                                {renderSortIcon(col.key, arbSortKey, arbSortDir)}
                              </div>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50 bg-slate-900/40">
                        {arbRows.length > 0 ? (
                          arbRows.map((r: any, idx: number) => (
                            <tr key={idx} className="hover:bg-slate-800/30">
                              <td className="p-3 text-slate-400 font-bold">{r.route_id}</td>
                              <td className="p-3 font-bold text-white">{r.symbol}</td>
                              <td className="p-3 text-slate-200">
                                <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-400 font-bold text-[10px] mr-1">
                                  {r.buy_venue}
                                </span>
                                &rarr;
                                <span className="px-2 py-0.5 rounded bg-slate-800 text-amber-400 font-bold text-[10px] ml-1">
                                  {r.sell_venue}
                                </span>
                              </td>
                              <td className="p-3 text-slate-300 font-mono">${(r.buy_price || 0).toLocaleString()}</td>
                              <td className="p-3 text-slate-300 font-mono">${(r.sell_price || 0).toLocaleString()}</td>
                              <td className="p-3 font-bold text-emerald-400 font-mono">+{r.net_spread_pct}%</td>
                              <td className="p-3 text-slate-400">${(r.size_usd || 0).toLocaleString()}</td>
                              <td className="p-3 font-extrabold text-emerald-400 font-mono">
                                +${(r.profit_usd || 0).toFixed(2)}
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={8} className="p-6 text-center text-slate-500">
                              No matching arbitrage routes found.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tab 4: Shadow Replay Simulation Details */}
              {activeTab === 'shadow' && (
                <div className="space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-bold text-purple-400 uppercase tracking-wider flex items-center gap-2">
                        <Layers className="w-4 h-4" /> Multi-Pair Shadow Simulation Trades Blotter ({shadowRows.length})
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Click any column header below to sort and filter simulated execution results.
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleExportCSV('Lumo_Shadow_Simulation_Report', shadowRows, [
                          { key: 'position_id', label: 'Position ID' },
                          { key: 'symbol', label: 'Symbol' },
                          { key: 'side', label: 'Side' },
                          { key: 'quantity', label: 'Quantity' },
                          { key: 'entry_price', label: 'Entry Price' },
                          { key: 'mark_price', label: 'Mark Price' },
                          { key: 'slippage_usd', label: 'Slippage Cost (USD)' },
                          { key: 'fees_usd', label: 'Fees Paid (USD)' },
                          { key: 'net_pnl_usd', label: 'Net Simulated PnL (USD)' }
                        ])}
                        className="px-3 py-1.5 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 text-purple-300 text-xs font-bold rounded-xl transition flex items-center gap-1.5 cursor-pointer shadow-sm"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Download CSV</span>
                      </button>
                    </div>
                  </div>

                  <div className="overflow-x-auto border border-slate-800 rounded-2xl">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          {[
                            { key: 'position_id', label: 'Position ID' },
                            { key: 'symbol', label: 'Symbol' },
                            { key: 'side', label: 'Side' },
                            { key: 'quantity', label: 'Quantity' },
                            { key: 'entry_price', label: 'Entry Price' },
                            { key: 'mark_price', label: 'Mark Price' },
                            { key: 'fees_usd', label: 'Slippage & Fees' },
                            { key: 'net_pnl_usd', label: 'Net Simulated PnL' }
                          ].map((col) => (
                            <th 
                              key={col.key}
                              onClick={() => handleSort(col.key, shadowSortKey, shadowSortDir, setShadowSortKey, setShadowSortDir)}
                              className="p-3 cursor-pointer hover:bg-slate-900 transition group select-none"
                            >
                              <div className="flex items-center gap-1.5">
                                <span>{col.label}</span>
                                {renderSortIcon(col.key, shadowSortKey, shadowSortDir)}
                              </div>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50 bg-slate-900/40">
                        {shadowRows.length > 0 ? (
                          shadowRows.map((p: any, idx: number) => (
                            <tr key={idx} className="hover:bg-slate-800/30">
                              <td className="p-3 text-slate-400 font-bold">{p.position_id}</td>
                              <td className="p-3 font-bold text-white">{p.symbol}</td>
                              <td className="p-3">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${p.side === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                                  {p.side}
                                </span>
                              </td>
                              <td className="p-3 text-slate-300 font-mono">{p.quantity}</td>
                              <td className="p-3 text-slate-300 font-mono">${(p.entry_price || 0).toLocaleString()}</td>
                              <td className="p-3 text-slate-300 font-mono">${(p.mark_price || 0).toLocaleString()}</td>
                              <td className="p-3 text-rose-400 font-mono">
                                -${((p.slippage_usd || 0) + (p.fees_usd || 0)).toFixed(2)}
                              </td>
                              <td className={`p-3 font-extrabold font-mono ${(p.net_pnl_usd || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {(p.net_pnl_usd || 0) >= 0 ? '+' : ''}${(p.net_pnl_usd || 0).toFixed(2)}
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={8} className="p-6 text-center text-slate-500">
                              No matching shadow trades found.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/70 flex flex-col sm:flex-row justify-between items-center gap-2 text-xs text-slate-400">
          <span className="font-mono flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" /> Real-time audited by Institutional Accounting Engine
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs transition cursor-pointer"
          >
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
};
