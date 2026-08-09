"use client";

import React from "react";

export default function AdminRevenuePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Platform Revenue Analytics</h1>
        <p className="text-gray-400 mt-1">MRR, ARR, ARPU, and plan distribution.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400">MRR</div>
          <div className="text-3xl font-bold text-emerald-400 mt-1">$48,200.00</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400">ARR</div>
          <div className="text-3xl font-bold text-white mt-1">$578,400.00</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400">ARPU</div>
          <div className="text-3xl font-bold text-indigo-400 mt-1">$1,004.16</div>
        </div>
      </div>
    </div>
  );
}
