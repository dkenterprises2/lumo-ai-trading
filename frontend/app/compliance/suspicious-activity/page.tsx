"use client";

import React from "react";

export default function SuspiciousActivityPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Suspicious Activity Reports (SAR)</h1>
        <p className="text-gray-400 mt-1">Regulatory SAR filings, risk scoring, and FIU escalation.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">SAR-2026-001</span>
            <h3 className="text-lg font-bold text-white mt-1">High Frequency Cancellation Burst</h3>
            <p className="text-xs text-gray-400">Risk Score: 88 / 100 | Status: UNDER_REVIEW</p>
          </div>
          <button className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">Escalate to FIU</button>
        </div>
      </div>
    </div>
  );
}
