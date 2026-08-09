"use client";

import React from "react";

export default function TradeInvestigationsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AI Trade Investigation & Root Cause Analysis (RCA)</h1>
        <p className="text-gray-400 mt-1">Automated evidence collection & timeline reconstruction across OMS, EMS, SOR, & risk logs.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">RCA_REPORT: RCA_ORD_P23_101</span>
            <h3 className="text-lg font-bold text-white mt-1">Partial fill caused by order book depth exhaustion on Binance</h3>
            <p className="text-xs text-gray-400">Confidence Score: 94% | Evidence Items: 3 Reconstructed Events</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">RCA COMPLETE</span>
        </div>
      </div>
    </div>
  );
}
