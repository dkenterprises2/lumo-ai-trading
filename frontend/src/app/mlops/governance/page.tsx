"use client";

import React from "react";

export default function AIGovernancePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AI Governance & Model Decision Audit Trail</h1>
        <p className="text-gray-400 mt-1">Complete audit logs of model promotions, dataset hashes, and approvals.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Audit Trail Logs</h2>
        <div className="space-y-3">
          <div className="bg-black/50 border border-gray-800 rounded-lg p-4 font-mono text-xs text-gray-300">
            <div className="text-emerald-400 font-bold mb-1">[AUD-ML-101] MODEL_PROMOTED_TO_PRODUCTION</div>
            <div>Model ID: MOD-XGB-2026</div>
            <div>Dataset Hash: sha256_e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855</div>
            <div>Approver: Lead Risk Manager</div>
          </div>
        </div>
      </div>
    </div>
  );
}
