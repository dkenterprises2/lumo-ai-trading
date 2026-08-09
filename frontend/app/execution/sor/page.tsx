"use client";

import React from "react";

export default function SmartOrderRoutingPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Smart Order Router (SOR) & Liquidity Ladder</h1>
        <p className="text-gray-400 mt-1">Cross-venue liquidity aggregation, order routing optimizer, & fee/rebate model.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">SYMBOL: BTCUSDT</span>
            <h3 className="text-lg font-bold text-white mt-1">Best Bid: $64,800.00 | Best Ask: $64,800.50</h3>
            <p className="text-xs text-gray-400">Aggregated Venues: Binance (60%) + Bybit (40%) | Depth: $15,000,000</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">OPTIMALLY ROUTED</span>
        </div>
      </div>
    </div>
  );
}
