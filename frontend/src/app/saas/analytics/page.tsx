"use client";

import React from "react";

export default function SuperAdminAnalyticsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Super Admin SaaS Analytics</h1>
        <p className="text-gray-400 mt-1">Platform-wide Monthly Recurring Revenue (MRR), active tenants, and ARPU.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Monthly Recurring Revenue (MRR)</div>
          <div className="text-3xl font-bold text-emerald-400 mt-2">$48,200.00</div>
          <div className="text-xs text-gray-500 mt-1">ARR: $578,400.00</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Active Tenants</div>
          <div className="text-3xl font-bold text-white mt-2">48 Orgs</div>
          <div className="text-xs text-gray-500 mt-1">Total Seats: 210</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Average Revenue Per User (ARPU)</div>
          <div className="text-3xl font-bold text-indigo-400 mt-2">$1,004.16</div>
          <div className="text-xs text-gray-500 mt-1">Churn Rate: 0.8%</div>
        </div>
      </div>
    </div>
  );
}
