"use client";

import React from "react";

export default function RegulatoryReportsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Regulatory Reporting Engine</h1>
        <p className="text-gray-400 mt-1">Daily trading activity, risk limit breach, and tax exports (CSV / JSON / PDF).</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-white">Generated Reports</h2>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
            Generate Report
          </button>
        </div>

        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">REP-DAILY-2026</span>
            <h3 className="text-base font-semibold text-white mt-1">Daily Trading Activity & Exposure Report</h3>
            <p className="text-xs text-gray-400">Formats: CSV, JSON, PDF</p>
          </div>
          <button className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">Download CSV</button>
        </div>
      </div>
    </div>
  );
}
