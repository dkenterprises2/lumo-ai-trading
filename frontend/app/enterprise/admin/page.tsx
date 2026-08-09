"use client";

import React from "react";

export default function EnterpriseSuperAdminPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Platform Super-Admin Control Panel</h1>
        <p className="text-gray-400 mt-1">Multi-tenant platform oversight, global MRR tracking, & feature flag controls.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Total Enterprise Tenants</span>
            <div className="text-2xl font-bold text-white mt-1">12 Active Orgs</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Monthly Recurring Revenue (MRR)</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">$59,988.00 / Mo</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Platform Status</span>
            <div className="text-2xl font-bold text-indigo-400 mt-1">HEALTHY (100% Uptime)</div>
          </div>
        </div>
      </div>
    </div>
  );
}
