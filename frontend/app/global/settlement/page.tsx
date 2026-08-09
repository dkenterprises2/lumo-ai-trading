"use client";

import React from "react";

export default function SettlementPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Institutional Settlement Instruction Engine</h1>
        <p className="text-gray-400 mt-1">Post-trade settlement instructions, give-up matching, & ledger reconciliations.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">SETTLE-INST-101</span>
            <h3 className="text-lg font-bold text-white mt-1">$100,000.00 USDT &rarr; Binance Custody</h3>

            <p className="text-xs text-gray-400">Post-Trade Settlement Status: SETTLED_SIMULATED</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">SETTLED</span>
        </div>
      </div>
    </div>
  );
}
