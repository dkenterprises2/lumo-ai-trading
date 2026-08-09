"use client";

import React from "react";

export default function AuditLedgerPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Immutable Audit Ledger</h1>
        <p className="text-gray-400 mt-1">Tamper-evident SHA-256 hash-chained audit ledger.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="bg-black/50 border border-gray-800 p-4 rounded-lg font-mono text-xs text-gray-300">
          <div className="text-emerald-400 font-bold mb-1">[AUD-000001] ACTION: SYSTEM_INITIALIZED</div>
          <div>Actor User ID: 1 | Tenant ID: ORG-101</div>
          <div>Previous Hash: 0000000000000000000000000000000000000000000000000000000000000000</div>
          <div>Current Hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855</div>
        </div>
      </div>
    </div>
  );
}
