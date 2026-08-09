"use client";

import React from "react";

export default function AIGovernancePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AI Agent Governance & Approval Queue</h1>
        <p className="text-gray-400 mt-1">Multi-stage promotion workflow from Shadow mode to Approved Live trading.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">APPROVAL QUEUE</span>
            <h3 className="text-lg font-bold text-white mt-1">Version: ppo_bull_v2 (Pending Review)</h3>
            <p className="text-xs text-gray-400">Sharpe Ratio: 2.58 | Max Drawdown: -4.2%</p>
          </div>
          <div className="flex gap-2">
            <button className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1 rounded text-xs">Approve</button>
            <button className="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-xs">Reject</button>
          </div>
        </div>
      </div>
    </div>
  );
}
