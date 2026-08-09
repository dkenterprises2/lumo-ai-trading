"use client";

import React from "react";

export default function AdminBackupsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Backup & Disaster Recovery Console</h1>
        <p className="text-gray-400 mt-1">Manual snapshots, automated RPO backup jobs, and database restoration.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">Snapshot Catalog</h2>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
            Create Snapshot Now
          </button>
        </div>

        <div className="border border-gray-800 rounded-lg p-4 bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">SNAP-2026-08-09</span>
            <h3 className="text-base font-semibold text-white mt-1">Automated Pre-Release Backup</h3>
            <p className="text-xs text-gray-400">Size: 42.8 MB | Status: SUCCESS</p>
          </div>
          <button className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">Restore</button>
        </div>
      </div>
    </div>
  );
}
