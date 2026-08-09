"use client";

import React from "react";

export default function DeveloperPortalPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">API Developer Portal & OpenAPI Spec</h1>
        <p className="text-gray-400 mt-1">Interactive API documentation, SDKs, & developer app registration.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">API VERSION: v3.5.0</span>
            <h3 className="text-lg font-bold text-white mt-1">Lumo REST & WebSocket OpenAPI Spec</h3>
            <p className="text-xs text-gray-400">Registered Developer Apps: 3 Apps</p>
          </div>
          <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">OPENAPI v3</span>
        </div>
      </div>
    </div>
  );
}
