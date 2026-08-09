"use client";

import React from "react";

export default function PlatformRunbooksPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Automated Operational Runbooks</h1>
        <p className="text-gray-400 mt-1">Cluster outage, database failover, market-data degradation, & emergency evacuation runbooks.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">RUNBOOK: DATABASE_FAILOVER</span>
            <h3 className="text-lg font-bold text-white mt-1">PostgreSQL High-Availability Failover</h3>
            <p className="text-xs text-gray-400">Target RPO: 15s | Target RTO: 5m | Dry-Run Status: PASSED_SIMULATED</p>
          </div>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1 rounded text-xs font-bold">Execute Dry-Run</button>
        </div>
      </div>
    </div>
  );
}
