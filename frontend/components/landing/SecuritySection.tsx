"use client";

import React from "react";

export default function SecuritySection() {
  return (
    <section className="py-20 bg-black border-b border-gray-800/60">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <div className="space-y-6">
          <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">Enterprise Security & Compliance</span>
          <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Bank-Grade Security Architecture
          </h2>
          <p className="text-gray-400 text-base leading-relaxed">
            API secrets are encrypted using SHA-256 hashing. Multi-tenant database context isolation and tenant-isolated WebSockets guarantee complete separation of fund data.
          </p>
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="bg-gray-950 border border-gray-800 p-4 rounded-xl">
              <div className="text-xl font-bold text-white mb-1">SOC 2 Type II</div>
              <div className="text-xs text-gray-400">Security & Privacy Compliant</div>
            </div>
            <div className="bg-gray-950 border border-gray-800 p-4 rounded-xl">
              <div className="text-xl font-bold text-white mb-1">AES-256 + HMAC</div>
              <div className="text-xs text-gray-400">Secret Encryption</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-950 border border-gray-800 p-8 rounded-2xl space-y-4">
          <h3 className="text-xl font-bold text-white mb-4">Security Checklist</h3>
          <ul className="space-y-3 text-sm text-gray-300">
            <li className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">✓</span>
              <span>Tenant-isolated database schema context</span>
            </li>
            <li className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">✓</span>
              <span>HMAC-signed API requests with rate limiting</span>
            </li>
            <li className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">✓</span>
              <span>Automatic backup snapshotting with RPO &lt; 5s</span>
            </li>
            <li className="flex items-center gap-3">
              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">✓</span>
              <span>Full AI model decision audit logging</span>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
