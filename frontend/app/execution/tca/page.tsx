"use client";

import React from "react";

export default function TCAPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Transaction Cost Analysis (TCA)</h1>
        <p className="text-gray-400 mt-1">Implementation shortfall, arrival price slippage, and execution efficiency scorecards.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Avg Implementation Shortfall</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">1.85 bps</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Avg VWAP Slippage</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">0.42 bps</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Execution Efficiency Score</div>
          <div className="text-2xl font-bold text-white mt-1">98.15 / 100</div>
        </div>
      </div>
    </div>
  );
}
