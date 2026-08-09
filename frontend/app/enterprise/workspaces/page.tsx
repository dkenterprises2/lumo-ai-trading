"use client";

import React from "react";

export default function EnterpriseWorkspacesPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Isolated Workspaces</h1>
        <p className="text-gray-400 mt-1">Trading Desk, Research Lab, Treasury Operations, & Compliance Office desks.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">WS_TRADING</span>
            <h3 className="text-base font-semibold text-white mt-1">Trading Desk</h3>
            <p className="text-xs text-gray-400">Permissions: Execution, Order Flow, Market Data</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">ACTIVE</span>
        </div>

        <div className="bg-gray-900 border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">WS_RESEARCH</span>
            <h3 className="text-base font-semibold text-white mt-1">Research Lab</h3>
            <p className="text-xs text-gray-400">Permissions: Factor Analysis, Stat-Arb, Notebooks</p>
          </div>
          <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">ACTIVE</span>
        </div>
      </div>
    </div>
  );
}
