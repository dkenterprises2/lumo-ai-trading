"use client";

import React from "react";

export default function EnterpriseCustomDomainsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Custom Domains & SSL Automation</h1>
        <p className="text-gray-400 mt-1">Tenant custom domain mapping, CNAME verification, & Let's Encrypt SSL certificates.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">CNAME: custom.lumo.trade</span>
            <h3 className="text-lg font-bold text-white mt-1">trade.acmecapital.com</h3>
            <p className="text-xs text-gray-400">SSL Issuer: Let's Encrypt Authority X3 | Auto-Renew: Enabled</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">VERIFIED & SECURE</span>
        </div>
      </div>
    </div>
  );
}
