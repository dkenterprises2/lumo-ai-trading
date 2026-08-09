"use client";

import React from "react";

export default function PreTradeRiskControlsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Pre-Trade Risk Controls & Kill-Switch</h1>
        <p className="text-gray-400 mt-1">Fat-finger price bands, notional caps ($5M limit), exposure checks, & emergency kill-switch.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">PRE-TRADE RISK SYSTEM</span>
            <h3 className="text-lg font-bold text-white mt-1">Status: ACTIVE & ENFORCED</h3>
            <p className="text-xs text-gray-400">Fat Finger Limit: $5,000,000 | Kill Switch: STANDBY</p>
          </div>
          <button className="bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded text-xs font-bold">ACTIVATE KILL-SWITCH</button>
        </div>
      </div>
    </div>
  );
}
