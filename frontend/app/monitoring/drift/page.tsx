"use client";

import React from "react";

export default function StrategyDriftMonitoringPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Strategy Performance Drift & Retirement Control</h1>
        <p className="text-gray-400 mt-1">Detection of performance decay, feature distribution drift, & automatic retirement.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-red-400 font-bold">ALERT: DRIFT-101</span>
            <h3 className="text-lg font-bold text-white mt-1">alpha_trend_old (Sharpe Decay &gt; 30%)</h3>
            <p className="text-xs text-gray-400">Recommendation: RETIRE FROM LIVE TRADING</p>
          </div>
          <button className="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-xs font-bold">Retire Strategy</button>
        </div>
      </div>
    </div>
  );
}
