"use client";

import React from "react";

export default function LiquidityRouterPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Smart Liquidity Seeking Router</h1>
        <p className="text-gray-400 mt-1">Multi-venue liquidity depth scoring & cross-exchange routing.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="space-y-3">
          <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
            <div>
              <span className="font-bold text-white">Binance (Score: 94.5 / 100)</span>
              <p className="text-xs text-gray-400">Liquidity Depth: $150,000 | Spread: 1.2 bps | Latency: 12.4 ms</p>
            </div>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">PRIMARY VENUE</span>
          </div>
        </div>
      </div>
    </div>
  );
}
