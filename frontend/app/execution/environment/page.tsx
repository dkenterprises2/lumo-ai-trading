"use client";

import React from "react";

export default function EnvironmentSwitchingPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Execution Environment Switching (PAPER / SHADOW / LIVE)</h1>
        <p className="text-gray-400 mt-1">Governance-controlled environment switcher with mandatory live-mode risk approval gates.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">CURRENT ENVIRONMENT: PAPER</span>
            <h3 className="text-lg font-bold text-white mt-1">Lumo Paper Trading Simulator</h3>
            <p className="text-xs text-gray-400">Live Trading Guardrails: ACTIVE (Governance Approval Required for LIVE)</p>
          </div>
          <button className="bg-amber-600 hover:bg-amber-500 text-white px-3 py-1 rounded text-xs font-bold">Request LIVE Mode</button>
        </div>
      </div>
    </div>
  );
}
