"use client";

import React from "react";

export default function PlatformDeploymentsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Progressive Delivery & Canary Deployments</h1>
        <p className="text-gray-400 mt-1">Canary traffic split (5% &rarr; 25% &rarr; 50% &rarr; 100%) and automated rollback triggers.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">DEP-V3.6.0-101</span>
            <h3 className="text-lg font-bold text-white mt-1">lumo-api Canary Deployment (25% Traffic)</h3>
            <p className="text-xs text-gray-400">SLO Analysis: HEALTHY | Latency Regression: None</p>
          </div>
          <div className="flex gap-2">
            <button className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1 rounded text-xs">Promote 50%</button>
            <button className="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-xs">Rollback</button>
          </div>
        </div>
      </div>
    </div>
  );
}
