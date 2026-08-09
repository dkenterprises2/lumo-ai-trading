"use client";

import React from "react";

export default function SecurityPoliciesPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Security Policy Enforcement Engine</h1>
        <p className="text-gray-400 mt-1">API key expiration, MFA enforcement, and rate limit policies.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-3">
        <div className="flex justify-between items-center border-b border-gray-800 pb-3">
          <span className="text-white font-medium">API_KEY_EXPIRATION (90 Days)</span>
          <span className="text-emerald-400 font-bold">ENFORCED</span>
        </div>
        <div className="flex justify-between items-center border-b border-gray-800 pb-3">
          <span className="text-white font-medium">MFA_FOR_ADMIN</span>
          <span className="text-emerald-400 font-bold">ENFORCED</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-white font-medium">RATE_LIMIT_STRICT (600 RPM)</span>
          <span className="text-emerald-400 font-bold">ENFORCED</span>
        </div>
      </div>
    </div>
  );
}
