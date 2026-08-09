"use client";

import React from "react";

export default function ExecutionAlgorithmsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Algorithmic Execution Suite (TWAP, VWAP, POV, Iceberg)</h1>
        <p className="text-gray-400 mt-1">Institutional execution strategies with participation constraints & microstructure signals.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <span className="font-mono text-xs text-indigo-400 font-bold">TWAP</span>
          <h3 className="text-lg font-bold text-white">Time-Weighted Average Price</h3>
          <p className="text-xs text-gray-400">Equal time slicing with randomized interval jitter.</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <span className="font-mono text-xs text-emerald-400 font-bold">VWAP</span>
          <h3 className="text-lg font-bold text-white">Volume-Weighted Average Price</h3>
          <p className="text-xs text-gray-400">Dynamic participation tied to intraday volume profiles.</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <span className="font-mono text-xs text-amber-400 font-bold">POV</span>
          <h3 className="text-lg font-bold text-white">Percentage of Volume</h3>
          <p className="text-xs text-gray-400">Target participation rate with min/max caps.</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <span className="font-mono text-xs text-purple-400 font-bold">ICEBERG</span>
          <h3 className="text-lg font-bold text-white">Hidden Reserve Iceberg</h3>
          <p className="text-xs text-gray-400">Randomized display size & fill refresh logic.</p>
        </div>
      </div>
    </div>
  );
}
