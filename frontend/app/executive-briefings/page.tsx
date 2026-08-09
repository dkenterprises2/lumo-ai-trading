"use client";

import React from "react";

export default function ExecutiveBriefingsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AI-Generated Executive Briefings & Daily Reports</h1>
        <p className="text-gray-400 mt-1">Operational intelligence summaries, P&L attribution, & risk overview for executives.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-bold text-white">Daily Executive Operational & Risk Briefing</h3>
            <span className="text-xs text-gray-400 font-mono">Date: Today</span>
          </div>
          <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="bg-black/50 p-3 rounded border border-gray-800">
              <span className="text-gray-400">Net P&amp;L</span>
              <p className="text-base font-bold text-emerald-400 mt-1">+$142,500 (+2.14%)</p>
            </div>
            <div className="bg-black/50 p-3 rounded border border-gray-800">
              <span className="text-gray-400">Portfolio VaR</span>
              <p className="text-base font-bold text-indigo-400 mt-1">3.1% VaR</p>
            </div>
            <div className="bg-black/50 p-3 rounded border border-gray-800">
              <span className="text-gray-400">System Health</span>
              <p className="text-base font-bold text-emerald-400 mt-1">100% Uptime</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
