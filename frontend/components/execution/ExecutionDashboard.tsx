"use client";

import React, { useState, useEffect } from "react";
import { 
  Zap, 
  Layers, 
  Activity, 
  ShieldAlert, 
  DollarSign, 
  RefreshCw, 
  Cpu, 
  BarChart3, 
  CheckCircle2, 
  Clock, 
  Crosshair,
  Compass,
  FileText,
  AlertCircle
} from "lucide-react";
import { apiFetch } from "@/services/api";

interface Order {
  order_id: string;
  client_order_id: string;
  symbol: string;
  side: string;
  order_type: string;
  quantity: number;
  filled_quantity: number;
  remaining_quantity: number;
  price?: number;
  average_fill_price: number;
  status: string;
  exchange: string;
  created_at: number;
}

interface Fill {
  fill_id: string;
  order_id: string;
  fill_price: number;
  fill_quantity: number;
  fee: number;
  liquidity_flag: string;
  exchange: string;
  timestamp: number;
}

export default function ExecutionDashboard() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [fills, setFills] = useState<Fill[]>([]);
  const [telemetry, setTelemetry] = useState<any>(null);
  const [costs, setCosts] = useState<any>(null);
  const [venueHealth, setVenueHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [algoTab, setAlgoTab] = useState<"TWAP" | "VWAP" | "ICEBERG">("TWAP");

  // Algorithm form inputs
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [side, setSide] = useState("BUY");
  const [quantity, setQuantity] = useState("1.0");

  const [jobs, setJobs] = useState<any[]>([]);

  const fetchData = async () => {
    try {
      const [resOrders, resFills, resTelem, resCosts, resHealth, resJobs] = await Promise.all([
        apiFetch("/api/execution/orders"),
        apiFetch("/api/execution/fills"),
        apiFetch("/api/execution/telemetry"),
        apiFetch("/api/execution/costs"),
        apiFetch("/api/execution/exchanges/health"),
        apiFetch("/api/execution/jobs")
      ]);

      if (resOrders.ok) setOrders(await resOrders.json());
      if (resFills.ok) setFills(await resFills.json());
      if (resTelem.ok) setTelemetry(await resTelem.json());
      if (resCosts.ok) setCosts(await resCosts.json());
      if (resHealth.ok) setVenueHealth(await resHealth.json());
      if (resJobs.ok) setJobs(await resJobs.json());
    } catch (e) {
      console.error("Failed to fetch execution telemetry", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 6000);
    return () => clearInterval(interval);
  }, []);

  const handleCreateAlgo = async () => {
    try {
      setSubmitting(true);
      setFeedback(null);

      const parsedQty = parseFloat(quantity);
      if (isNaN(parsedQty) || parsedQty <= 0) {
        setFeedback({ type: "error", message: "Please specify a valid quantity greater than 0." });
        setSubmitting(false);
        return;
      }

      const res = await apiFetch("/api/execution/jobs", {
        method: "POST",
        body: JSON.stringify({
          symbol: symbol.trim(),
          side,
          algo_type: algoTab,
          total_quantity: parsedQty,
          num_slices: 5
        })
      });

      if (res.ok) {
        const job = await res.json();
        setFeedback({
          type: "success",
          message: `${algoTab} Job ${job.job_id} successfully executed! Status: ${job.status} (${job.filled_quantity}/${job.total_quantity} filled @ avg $${job.average_fill_price || 'N/A'})`
        });
        fetchData();
      } else {
        const err = await res.json().catch(() => ({ detail: "Request failed" }));
        setFeedback({
          type: "error",
          message: `Failed to launch ${algoTab} job: ${err.detail || err.message || "Unknown server response"}`
        });
      }
    } catch (e: any) {
      console.error("Failed to create algorithm job", e);
      setFeedback({
        type: "error",
        message: `Failed to launch job: ${e.message || "Network error"}`
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      const res = await apiFetch(`/api/execution/jobs/${jobId}/cancel`, {
        method: "POST"
      });
      if (res.ok) {
        fetchData();
      }
    } catch (e) {
      console.error("Failed to cancel job", e);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12 text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin mr-2" />
        <span>Loading OMS / EMS Execution Intelligence...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-slate-100 font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between bg-slate-900/80 border border-slate-800 p-6 rounded-2xl backdrop-blur-md">
        <div>
          <div className="flex items-center space-x-3">
            <Zap className="w-8 h-8 text-cyan-400" />
            <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Institutional Order &amp; Execution Engine
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Smart order routing, algorithmic execution, slippage control, and execution telemetry.
          </p>
        </div>
      </div>

      {/* Top 4 Metrics Widgets */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Orders</span>
            <Clock className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-bold text-slate-100">{telemetry?.active_orders_count ?? 0}</span>
            <span className="text-xs text-slate-400">Live</span>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Filled Today</span>
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-bold text-emerald-400">{telemetry?.filled_today_count ?? 0}</span>
            <span className="text-xs text-slate-400">Orders</span>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Slippage</span>
            <Crosshair className="w-5 h-5 text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-bold text-amber-400">
              {telemetry && telemetry.average_slippage_pct !== undefined ? `${telemetry.average_slippage_pct}%` : "—"}
            </span>
            <span className="text-xs text-slate-400">Allowed</span>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl backdrop-blur-md">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Execution Cost Today</span>
            <DollarSign className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-bold text-indigo-400">
              {costs && costs.total_execution_cost_usd !== undefined ? `$${costs.total_execution_cost_usd.toFixed(2)}` : "$0.00"}
            </span>
          </div>
        </div>
      </div>

      {/* Algo Execution Wizard */}
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl backdrop-blur-md space-y-4">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-3">
          <Cpu className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-bold text-slate-200">Algorithmic Execution Wizard</h2>
          <div className="ml-auto flex space-x-2">
            {(["TWAP", "VWAP", "ICEBERG"] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setAlgoTab(tab)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${algoTab === tab ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20" : "bg-slate-800 text-slate-400 hover:text-slate-200"}`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="text-xs font-semibold text-slate-400">Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={e => setSymbol(e.target.value)}
              className="mt-1 w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-xl px-3 py-2 font-mono"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400">Side</label>
            <select
              value={side}
              onChange={e => setSide(e.target.value)}
              className="mt-1 w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-xl px-3 py-2 font-mono"
            >
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400">Total Quantity</label>
            <input
              type="text"
              value={quantity}
              onChange={e => setQuantity(e.target.value)}
              className="mt-1 w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-xl px-3 py-2 font-mono"
            />
          </div>
          <button
            onClick={handleCreateAlgo}
            disabled={submitting}
            className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 text-slate-950 font-bold text-sm rounded-xl py-2.5 shadow-lg shadow-cyan-900/30 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
          >
            {submitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Launching...</span>
              </>
            ) : (
              <span>Launch {algoTab} Job</span>
            )}
          </button>
        </div>

        {feedback && (
          <div className={`p-3.5 rounded-xl border flex items-center gap-3 text-xs font-semibold ${
            feedback.type === "success"
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
              : "bg-rose-500/10 border-rose-500/30 text-rose-400"
          }`}>
            {feedback.type === "success" ? (
              <CheckCircle2 className="w-4 h-4 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0" />
            )}
            <span className="flex-1">{feedback.message}</span>
            <button
              onClick={() => setFeedback(null)}
              className="text-slate-400 hover:text-white text-xs font-bold px-1"
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {/* Algorithmic Execution Jobs Monitor */}
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl backdrop-blur-md space-y-4">
        <h2 className="text-lg font-bold text-slate-200 flex items-center space-x-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          <span>Active Algorithmic Execution Jobs</span>
        </h2>

        {jobs.length === 0 ? (
          <div className="text-slate-400 text-sm bg-slate-950/40 p-4 rounded-xl border border-slate-800">
            No active algorithmic jobs running. Use the wizard above to launch TWAP, VWAP, or Iceberg jobs.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase font-semibold">
                  <th className="py-2.5 px-3">Job ID</th>
                  <th className="py-2.5 px-3">Algo</th>
                  <th className="py-2.5 px-3">Symbol</th>
                  <th className="py-2.5 px-3">Side</th>
                  <th className="py-2.5 px-3">Filled / Total</th>
                  <th className="py-2.5 px-3">Avg Fill Price</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {jobs.map((j: any) => (
                  <tr key={j.job_id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 text-cyan-300 font-bold">{j.job_id}</td>
                    <td className="py-2.5 px-3 text-slate-200">{j.algo_type}</td>
                    <td className="py-2.5 px-3 text-slate-200 font-bold">{j.symbol}</td>
                    <td className={`py-2.5 px-3 font-bold ${j.side === "BUY" ? "text-emerald-400" : "text-rose-400"}`}>{j.side}</td>
                    <td className="py-2.5 px-3 text-slate-300">{j.filled_quantity} / {j.total_quantity}</td>
                    <td className="py-2.5 px-3 text-slate-300">${j.average_fill_price ? j.average_fill_price.toFixed(2) : "0.00"}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        j.status === "COMPLETED" ? "bg-emerald-500/20 text-emerald-400" :
                        j.status === "RUNNING" ? "bg-cyan-500/20 text-cyan-400 animate-pulse" :
                        j.status === "REJECTED" ? "bg-rose-500/20 text-rose-400" :
                        "bg-amber-500/20 text-amber-400"
                      }`}>
                        {j.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      {["STARTING", "RUNNING"].includes(j.status) && (
                        <button
                          onClick={() => handleCancelJob(j.job_id)}
                          className="px-2.5 py-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 rounded text-xs font-bold"
                        >
                          Cancel
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Order Blotter & Active Orders Table */}
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl backdrop-blur-md space-y-4">
        <h2 className="text-lg font-bold text-slate-200 flex items-center space-x-2">
          <FileText className="w-5 h-5 text-emerald-400" />
          <span>OMS Order Blotter</span>
        </h2>

        {orders.length === 0 ? (
          <div className="text-slate-400 text-sm bg-slate-950/40 p-4 rounded-xl border border-slate-800">
            No orders submitted yet. Orders submitted via bot signals or API will appear here.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase font-semibold">
                  <th className="py-2.5 px-3">Order ID</th>
                  <th className="py-2.5 px-3">Symbol</th>
                  <th className="py-2.5 px-3">Side</th>
                  <th className="py-2.5 px-3">Quantity</th>
                  <th className="py-2.5 px-3">Avg Fill Price</th>
                  <th className="py-2.5 px-3">Exchange</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {orders.map(o => (
                  <tr key={o.order_id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 text-cyan-300 font-bold">{o.order_id}</td>
                    <td className="py-2.5 px-3 text-slate-200 font-bold">{o.symbol}</td>
                    <td className={`py-2.5 px-3 font-bold ${o.side === "BUY" || o.side === "LONG" ? "text-emerald-400" : "text-rose-400"}`}>{o.side}</td>
                    <td className="py-2.5 px-3 text-slate-300">{o.filled_quantity} / {o.quantity}</td>
                    <td className="py-2.5 px-3 text-slate-300">${o.average_fill_price.toFixed(2)}</td>
                    <td className="py-2.5 px-3 text-indigo-400 font-bold">{o.exchange}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${o.status === "FILLED" ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"}`}>
                        {o.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
