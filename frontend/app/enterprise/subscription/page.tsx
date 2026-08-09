"use client";

import React from "react";

export default function EnterpriseSubscriptionPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Subscription Plans & Entitlements</h1>
        <p className="text-gray-400 mt-1">Tier licensing across Free, Starter, Pro, Institutional, Enterprise, & White-Label.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-6 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">CURRENT PLAN: ENTERPRISE TIER</span>
            <h3 className="text-xl font-bold text-white mt-1">$4,999.00 / month</h3>
            <p className="text-xs text-gray-400 mt-1">Includes 50 Seats, Multi-Asset OMS/EMS, SAML SSO, & White-Labeling.</p>
          </div>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-xs font-bold">Change Plan</button>
        </div>
      </div>
    </div>
  );
}
