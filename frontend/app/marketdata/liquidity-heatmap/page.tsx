"use client";

import React from "react";

export default function LiquidityHeatmapPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Liquidity Heatmap Generator</h1>
        <p className="text-gray-400 mt-1">Resting order book liquidity density matrix and support/resistance clusters.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">SUPPORT CLUSTER</span>
            <h3 className="text-lg font-bold text-white mt-1">$64,800.00 (Density: 95%)</h3>
            <p className="text-xs text-gray-400">Resistance Cluster: $64,900.00 (Density: 88%)</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">CLUSTER DETECTED</span>
        </div>
      </div>
    </div>
  );
}
