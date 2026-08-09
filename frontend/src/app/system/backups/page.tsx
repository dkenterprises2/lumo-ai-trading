"use client";

import React from "react";

export default function BackupsConsolePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Backup & Disaster Recovery Console</h1>
        <p className="text-gray-400 mt-1">Automated database snapshot backup scheduling and recovery testing.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-white">Database Snapshots</h2>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
            Create Backup Snapshot
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Backup ID</th>
                <th className="px-4 py-3">Filename</th>
                <th className="px-4 py-3">Size (MB)</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Created At</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-white">BKP_20260809_0001</td>
                <td className="px-4 py-3">lumo_trading_20260809_0001.sqlite.gz</td>
                <td className="px-4 py-3">14.8 MB</td>
                <td className="px-4 py-3 text-emerald-400 font-semibold">COMPLETED</td>
                <td className="px-4 py-3">2026-08-09 12:00:00 UTC</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
