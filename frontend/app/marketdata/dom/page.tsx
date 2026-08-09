"use client";

import React from "react";

export default function DepthOfMarketPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Depth-of-Market (DOM) Analytics</h1>
        <p className="text-gray-400 mt-1">Spread width, cumulative bid/ask depth, and depth-weighted imbalance.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Spread (Absolute / Bps)</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">$0.50 (0.08 bps)</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Cumulative Bid Depth</span>
            <div className="text-2xl font-bold text-indigo-400 mt-1">24.30 BTC</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Depth Imbalance Ratio</span>
            <div className="text-2xl font-bold text-amber-400 mt-1">0.68 (Bullish)</div>
          </div>
        </div>
      </div>
    </div>
  );
}
