"use client";

import React from "react";

export default function PlatformSREPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">SRE Control Center & Error Budgets</h1>
        <p className="text-gray-400 mt-1">SLO target monitoring (99.99%), error budget burn-down, & incident tracking.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800 flex justify-between items-center">
            <div>
              <span className="text-xs text-indigo-400 font-bold font-mono">LUMO-API (SLO: 99.9%)</span>
              <h3 className="text-xl font-bold text-white mt-1">99.98% Uptime</h3>
              <p className="text-xs text-emerald-400">82% Error Budget Remaining</p>
            </div>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">SAFE</span>
          </div>

          <div className="bg-black/50 p-4 rounded-lg border border-gray-800 flex justify-between items-center">
            <div>
              <span className="text-xs text-emerald-400 font-bold font-mono">LUMO-EXECUTION (SLO: 99.99%)</span>
              <h3 className="text-xl font-bold text-white mt-1">99.995% Uptime</h3>
              <p className="text-xs text-emerald-400">94% Error Budget Remaining</p>
            </div>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">SAFE</span>
          </div>
        </div>
      </div>
    </div>
  );
}
