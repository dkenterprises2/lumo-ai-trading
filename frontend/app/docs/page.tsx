import React from "react";
import Navbar from "../../components/landing/Navbar";
import Footer from "../../components/landing/Footer";

export const metadata = {
  title: "Documentation & API Guide — Lumo AI Trading Platform",
  description: "REST API references, WebSocket stream documentation, and strategy integration guides."
};

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <div className="py-20 max-w-5xl mx-auto px-6 space-y-8">
        <h1 className="text-4xl font-extrabold">Documentation & Developer Guide</h1>
        <p className="text-gray-400">Complete API references and integration guides for the Lumo AI Trading Platform.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-950 border border-gray-800 p-6 rounded-2xl">
            <h3 className="text-xl font-bold mb-2">REST API Quickstart</h3>
            <p className="text-xs text-gray-400 mb-4">Authenticate using HMAC API keys and query endpoints.</p>
            <pre className="bg-black p-3 rounded font-mono text-xs text-emerald-400 overflow-x-auto">
              curl -H "X-API-KEY: lumo_pk_live..." https://api.lumo.trade/api/system/status
            </pre>
          </div>

          <div className="bg-gray-950 border border-gray-800 p-6 rounded-2xl">
            <h3 className="text-xl font-bold mb-2">WebSocket Real-Time Streams</h3>
            <p className="text-xs text-gray-400 mb-4">Subscribe to tenant-isolated real-time execution & tick feeds.</p>
            <pre className="bg-black p-3 rounded font-mono text-xs text-indigo-400 overflow-x-auto">
              wss://api.lumo.trade/ws?channel=tenant:ORG-101
            </pre>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
