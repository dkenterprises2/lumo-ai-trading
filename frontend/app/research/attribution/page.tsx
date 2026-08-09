"use client";

import React from "react";

export default function PerformanceAttributionPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Quantitative Performance Attribution</h1>
        <p className="text-gray-400 mt-1">Brinson & multi-factor performance attribution waterfalls.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Total Generated Alpha</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">+18.4%</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Selection Effect</span>
            <div className="text-2xl font-bold text-indigo-400 mt-1">+9.8%</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Allocation Effect</span>
            <div className="text-2xl font-bold text-amber-400 mt-1">+6.2%</div>
          </div>
        </div>
      </div>
    </div>
  );
}
