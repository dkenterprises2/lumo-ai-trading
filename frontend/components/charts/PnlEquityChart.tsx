"use client";

import React from "react";
import { EquitySnapshot } from "@/types/trading";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";
import { TrendingUp } from "lucide-react";

interface PnlEquityChartProps {
  pnlHistory: EquitySnapshot[];
}

export function PnlEquityChart({ pnlHistory }: PnlEquityChartProps) {
  const formattedData = (pnlHistory || []).map((h) => ({
    ...h,
    formattedTime: h.timestamp
  }));

  const minEquity = pnlHistory.length > 0 ? Math.min(...pnlHistory.map((d) => d.equity)) * 0.995 : "auto";
  const maxEquity = pnlHistory.length > 0 ? Math.max(...pnlHistory.map((d) => d.equity)) * 1.005 : "auto";

  return (
    <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400">
            <TrendingUp className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-base">Live Equity & PnL History Curve</h3>
            <p className="text-xs text-slate-400">Database Single Source of Truth Snapshot</p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-cyan-400" />
            <span className="text-slate-300 font-medium">Portfolio Equity</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
            <span className="text-slate-300 font-medium">Realized PnL</span>
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00f2fe" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#00f2fe" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="formattedTime" stroke="#64748b" tick={{ fontSize: 11 }} tickLine={false} />
            <YAxis domain={[minEquity, maxEquity]} stroke="#64748b" tick={{ fontSize: 11 }} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#090d16",
                borderColor: "#334155",
                borderRadius: "12px",
                fontSize: "12px"
              }}
            />
            <Area
              type="monotone"
              dataKey="equity"
              stroke="#00f2fe"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#equityGrad)"
              name="Equity ($)"
            />
            <Line
              type="monotone"
              dataKey="realized_pnl"
              stroke="#00e676"
              strokeWidth={1.5}
              dot={false}
              name="Realized PnL ($)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
