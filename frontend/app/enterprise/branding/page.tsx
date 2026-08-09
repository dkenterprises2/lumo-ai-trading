"use client";

import React from "react";

export default function EnterpriseBrandingPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">White-Label Branding Studio</h1>
        <p className="text-gray-400 mt-1">Tenant logo, favicon, color themes, custom CSS, & support portal links.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">App Name</span>
            <div className="text-xl font-bold text-white mt-1">Lumo Pro</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Primary Accent Color</span>
            <div className="text-xl font-bold text-indigo-400 mt-1">#6366F1</div>
          </div>
        </div>
      </div>
    </div>
  );
}
