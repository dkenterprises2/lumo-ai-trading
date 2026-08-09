"use client";

import React from "react";

export default function AdminSubscriptionsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Tenant Subscriptions Console</h1>
        <p className="text-gray-400 mt-1">Active plan tiers and seat-based billing distribution.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">Active Plan Tiers</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-black/50 border border-gray-800 p-4 rounded-lg">
            <div className="text-sm text-gray-400 font-medium">Free Simulator</div>
            <div className="text-2xl font-bold text-white mt-1">12 Orgs</div>
          </div>
          <div className="bg-black/50 border border-gray-800 p-4 rounded-lg">
            <div className="text-sm text-gray-400 font-medium">Pro Trader ($199/mo)</div>
            <div className="text-2xl font-bold text-indigo-400 mt-1">28 Orgs</div>
          </div>
          <div className="bg-black/50 border border-gray-800 p-4 rounded-lg">
            <div className="text-sm text-gray-400 font-medium">Enterprise ($999/mo)</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">8 Orgs</div>
          </div>
        </div>
      </div>
    </div>
  );
}
