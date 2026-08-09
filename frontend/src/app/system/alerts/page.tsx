"use client";

import React from "react";

export default function AlertCenterPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Alert Center & Notification Rules</h1>
        <p className="text-gray-400 mt-1">Real-time system alerts, risk breaches, and exchange connectivity notifications.</p>
      </div>

      <div className="space-y-4">
        <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-4 flex items-center justify-between">
          <div>
            <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded">CRITICAL</span>
            <h3 className="text-lg font-semibold text-white mt-1">OKX WebSocket Stream High Latency</h3>
            <p className="text-sm text-gray-300">Latency exceeded 150ms threshold (measured: 184ms).</p>
          </div>
          <span className="text-xs text-gray-400">Status: FIRING</span>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <span className="bg-amber-500 text-black text-xs font-bold px-2 py-0.5 rounded">WARNING</span>
            <h3 className="text-lg font-semibold text-white mt-1">Daily Loss Limit Warning</h3>
            <p className="text-sm text-gray-300">Strategy Trend Following reached 80% limit.</p>
          </div>
          <span className="text-xs text-emerald-400">Status: RESOLVED</span>
        </div>
      </div>
    </div>
  );
}
