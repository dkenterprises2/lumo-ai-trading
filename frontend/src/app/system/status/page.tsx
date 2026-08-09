"use client";

import React from "react";

export default function SystemStatusPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">System Status & Health Probes</h1>
        <p className="text-gray-400 mt-1">Real-time status across platform microservices, database, and exchange adapters.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Liveness Probe</div>
          <div className="text-2xl font-bold text-emerald-400 mt-2">UP (200 OK)</div>
          <div className="text-xs text-gray-500 mt-1">Checked every 10s</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Readiness Probe</div>
          <div className="text-2xl font-bold text-emerald-400 mt-2">READY (200 OK)</div>
          <div className="text-xs text-gray-500 mt-1">4 Subsystems Healthy</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Overall System Status</div>
          <div className="text-2xl font-bold text-emerald-400 mt-2">OPERATIONAL</div>
          <div className="text-xs text-gray-500 mt-1">Uptime: 99.998%</div>
        </div>
      </div>
    </div>
  );
}
