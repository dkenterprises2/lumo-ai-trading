"use client";

import React from "react";

export default function TWAPConsolePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">TWAP Execution Console</h1>
        <p className="text-gray-400 mt-1">Time-Weighted Average Price order configuration and slice schedule visualization.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">TWAP CONFIG</span>
            <h3 className="text-lg font-bold text-white mt-1">10.0 BTC / 60 Minutes (12 Slices)</h3>
            <p className="text-xs text-gray-400">Interval: 300s | Random Jitter: Enabled (+/- 5%)</p>
          </div>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
            Start TWAP
          </button>
        </div>
      </div>
    </div>
  );
}
