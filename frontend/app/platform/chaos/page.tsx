"use client";

import React from "react";

export default function PlatformChaosPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Chaos Engineering & Resilience Testing</h1>
        <p className="text-gray-400 mt-1">Pod termination, network latency injection, & database failover drills.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">CHAOS-101 (PASSED)</span>
            <h3 className="text-lg font-bold text-white mt-1">Pod Termination Test (staging namespace)</h3>
            <p className="text-xs text-gray-400">Blast Radius: 10% pods | Success Criteria: 100% Request Recovery</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">PASSED</span>
        </div>
      </div>
    </div>
  );
}
