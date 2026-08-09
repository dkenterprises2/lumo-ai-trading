"use client";

import React from "react";

export default function SecurityComplianceStatusPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">SOC 2 & ISO 27001 Readiness Status</h1>
        <p className="text-gray-400 mt-1">Audit readiness scorecards and evidence repository controls.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">SOC 2 Type II Readiness</div>
          <div className="text-3xl font-bold text-emerald-400 mt-2">98.4%</div>
          <div className="text-xs text-gray-500 mt-1">Security, Availability & Confidentiality</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">ISO 27001 Compliance</div>
          <div className="text-3xl font-bold text-indigo-400 mt-2">96.8%</div>
          <div className="text-xs text-gray-500 mt-1">110 / 114 Controls Passing</div>
        </div>
      </div>
    </div>
  );
}
