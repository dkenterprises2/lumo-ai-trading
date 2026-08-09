"use client";

import React from "react";

export default function ArbitrageGraphPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Cross-Exchange & Cross-Chain Arbitrage Graph</h1>
        <p className="text-gray-400 mt-1">Multi-hop graph route finder & net-spread profit calculator.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">PROFITABLE ROUTE (ARB-GRAPH-101)</span>
            <h3 className="text-base font-semibold text-white mt-1">BTC/USDT (Binance) &rarr; BTC/USDC (Bybit) &rarr; USDC (ETH) &rarr; USDT (Polygon)</h3>

            <p className="text-xs text-gray-400">Gross: 12.5 bps | Est Transfer Cost: 3.2 bps | Net Spread: +9.3 bps</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">PROFITABLE</span>
        </div>
      </div>
    </div>
  );
}
