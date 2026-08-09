"use client";

import React from "react";

export default function AdminPlatformMetricsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Platform Usage Analytics</h1>
        <p className="text-gray-400 mt-1">Platform-wide API throughput and WebSocket connections.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400">Total API Requests (24h)</div>
          <div className="text-3xl font-bold text-white mt-1">1,420,500</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400">Active WebSocket Streams</div>
          <div className="text-3xl font-bold text-indigo-400 mt-1">580 Connections</div>
        </div>
      </div>
    </div>
  );
}
