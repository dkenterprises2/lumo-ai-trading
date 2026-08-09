"use client";

import React from "react";

export default function SecurityIncidentsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Security Incident Management</h1>
        <p className="text-gray-400 mt-1">Real-time security incident response and containment queue.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">INC-2026-001</span>
            <h3 className="text-base font-semibold text-white mt-1">Failed API Key Auth Burst Detected</h3>
            <p className="text-xs text-gray-400">Severity: LOW | Status: CONTAINED</p>
          </div>
        </div>
      </div>
    </div>
  );
}
