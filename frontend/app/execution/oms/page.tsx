"use client";

import React from "react";

export default function OMSOrderLifecyclePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Institutional Order Management System (OMS)</h1>
        <p className="text-gray-400 mt-1">Lifecycle tracking across `CREATED` &rarr; `VALIDATED` &rarr; `RISK_APPROVED` &rarr; `ROUTED` &rarr; `FILLED`.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">ORDER_ID: ORD_P23_101</span>
            <h3 className="text-lg font-bold text-white mt-1">BUY 2.5 BTCUSDT @ $64,800.00</h3>
            <p className="text-xs text-gray-400">Timestamp: 2026-08-09 22:00:00 UTC</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">FILLED</span>
        </div>
      </div>
    </div>
  );
}
