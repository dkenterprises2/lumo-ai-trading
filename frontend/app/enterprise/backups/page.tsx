"use client";

import React from "react";

export default function EnterpriseBackupsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Tenant Backups & Disaster Recovery</h1>
        <p className="text-gray-400 mt-1">Logical tenant database backups, point-in-time snapshots, & disaster drills.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">BACKUP_ORG_ACME_101</span>
            <h3 className="text-lg font-bold text-white mt-1">Full Logical Tenant Snapshot (145.2 MB)</h3>
            <p className="text-xs text-gray-400">RPO: 15s | RTO: 5m | DR Region: us-west-2</p>
          </div>
          <button className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1 rounded text-xs font-bold">Restore Backup</button>
        </div>
      </div>
    </div>
  );
}
