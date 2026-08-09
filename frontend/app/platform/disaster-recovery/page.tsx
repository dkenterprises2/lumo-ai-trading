"use client";

import React from "react";

export default function PlatformDisasterRecoveryPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Disaster Recovery Readiness Scorecard</h1>
        <p className="text-gray-400 mt-1">Cross-region failover (us-east-1 &rarr; us-west-2), RPO (15s), & RTO (5m) verification.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">DR Failover Region</span>
            <div className="text-2xl font-bold text-white mt-1">us-west-2</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Target RPO</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">15 Seconds</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Target RTO</span>
            <div className="text-2xl font-bold text-indigo-400 mt-1">5 Minutes</div>
          </div>
        </div>
      </div>
    </div>
  );
}
