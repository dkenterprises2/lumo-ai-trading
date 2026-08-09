"use client";

import React from "react";

export default function AIGuardrailsMonitoringPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AI Security Guardrails & Prompt Policy Enforcement</h1>
        <p className="text-gray-400 mt-1">Prompt sanitization, data redaction, hallucination checks, & cross-tenant security console.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">GUARDRAIL POLICY ENGINE</span>
            <h3 className="text-lg font-bold text-white mt-1">Enforcement Mode: STRICT</h3>
            <p className="text-xs text-gray-400">Prompt Sanitization: ACTIVE | Data Redaction: ENFORCED | Role Gates: ACTIVE</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">POLICY ENFORCED</span>
        </div>
      </div>
    </div>
  );
}
