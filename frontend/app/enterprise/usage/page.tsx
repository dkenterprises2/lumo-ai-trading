"use client";

import React from "react";

export default function EnterpriseUsagePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Usage Metering & Quota Consumption</h1>
        <p className="text-gray-400 mt-1">API calls, WebSocket messages, RL training hours, & storage metering.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">API Calls Used</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">142,000 / 200,000</div>
            <div className="text-xs text-gray-500 mt-1">71.0% Utilization</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">WebSocket Messages</span>
            <div className="text-2xl font-bold text-indigo-400 mt-1">850,000</div>
            <div className="text-xs text-gray-500 mt-1">Real-Time Streams</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">RL Training Hours</span>
            <div className="text-2xl font-bold text-amber-400 mt-1">45.0 Hours</div>
            <div className="text-xs text-gray-500 mt-1">GPU Compute Cluster</div>
          </div>
        </div>
      </div>
    </div>
  );
}
