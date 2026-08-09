"use client";

import React from "react";

export default function EnterpriseSSOPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Enterprise SSO Configuration</h1>
        <p className="text-gray-400 mt-1">SAML 2.0, Google OAuth 2.0, & Microsoft Entra ID enterprise authentication.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">SAML 2.0 SSO</span>
            <h3 className="text-base font-semibold text-white mt-1">Entity ID: https://idp.acmecapital.com</h3>
            <p className="text-xs text-gray-400">JIT Provisioning: Enabled | Status: CONFIGURED_SIMULATED</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">ACTIVE</span>
        </div>
      </div>
    </div>
  );
}
