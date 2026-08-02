"use client";

import React, { useState } from "react";
import { Candle } from "@/types/trading";
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
import { LineChart } from "lucide-react";

interface MarketChartProps {
  symbol: string;
  timeframe: string;
  chartData: Candle[];
  onTimeframeChange: (tf: string) => void;
}

export function MarketChart({
  symbol,
  timeframe,
  chartData,
  onTimeframeChange
}: MarketChartProps) {
  const [showSMA, setShowSMA] = useState(true);
  const [showEMA, setShowEMA] = useState(true);

  const formattedData = chartData.map((item) => ({
    ...item,
    formattedTime: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }));

  const minPrice = chartData.length > 0 ? Math.min(...chartData.map((d) => d.low)) * 0.998 : "auto";
  const maxPrice = chartData.length > 0 ? Math.max(...chartData.map((d) => d.high)) * 1.002 : "auto";

  return (
    <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400">
            <LineChart className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-base flex items-center gap-2">
              {symbol} Market Curve
              <span className="text-xs px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 font-mono">
                {timeframe}
              </span>
            </h3>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Timeframe Buttons */}
          <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-950 border border-slate-800 text-xs">
            {["1m", "5m", "15m", "1h", "4h", "1d"].map((tf) => (
              <button
                key={tf}
                onClick={() => onTimeframeChange(tf)}
                className={`px-2.5 py-1 rounded-lg font-medium transition ${
                  timeframe === tf
                    ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          {/* SMA / EMA Toggles */}
          <div className="flex items-center gap-3 text-xs text-slate-400 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
            <label className="flex items-center gap-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={showSMA}
                onChange={(e) => setShowSMA(e.target.checked)}
                className="rounded border-slate-700 bg-slate-900 text-amber-400 focus:ring-0 cursor-pointer"
              />
              <span className="text-amber-400 font-semibold">SMA 20</span>
            </label>
            <label className="flex items-center gap-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={showEMA}
                onChange={(e) => setShowEMA(e.target.checked)}
                className="rounded border-slate-700 bg-slate-900 text-purple-400 focus:ring-0 cursor-pointer"
              />
              <span className="text-purple-400 font-semibold">EMA 9</span>
            </label>
          </div>
        </div>
      </div>

      {/* Chart Canvas Area */}
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00f2fe" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#00f2fe" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="formattedTime" stroke="#64748b" tick={{ fontSize: 11 }} tickLine={false} />
            <YAxis domain={[minPrice, maxPrice]} stroke="#64748b" tick={{ fontSize: 11 }} tickLine={false} />
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
              dataKey="close"
              stroke="#00f2fe"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#priceGradient)"
              name="Price ($)"
            />
            {showSMA && (
              <Line
                type="monotone"
                dataKey="sma_20"
                stroke="#ffd600"
                strokeWidth={1.5}
                dot={false}
                name="SMA 20"
              />
            )}
            {showEMA && (
              <Line
                type="monotone"
                dataKey="ema_9"
                stroke="#a855f7"
                strokeWidth={1.5}
                dot={false}
                name="EMA 9"
              />
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
