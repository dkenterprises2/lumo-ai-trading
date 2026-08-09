"use client";

import React from "react";

export default function VWAPConsolePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">VWAP Execution Console</h1>
        <p className="text-gray-400 mt-1">Volume-Weighted Average Price benchmark tracking and intraday curve modeling.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">VWAP BENCHMARK</span>
            <h3 className="text-lg font-bold text-white mt-1">Achieved VWAP: $64,812.50 vs Market VWAP: $64,810.00</h3>
            <p className="text-xs text-gray-400">Implementation Shortfall: +0.38 bps</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">MATCHED BENCHMARK</span>
        </div>
      </div>
    </div>
  );
}
