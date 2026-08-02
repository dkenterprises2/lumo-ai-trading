"use client";

import React from "react";
import { TradingConnectionState } from "@/hooks/useTradingStream";
import {
  LayoutDashboard,
  Scan,
  LineChart,
  ClipboardList,
  Crosshair,
  History,
  TrendingUp,
  BookOpen,
  Award,
  Bot,
  ChessKnight,
  ShieldAlert,
  Newspaper,
  FileSpreadsheet,
  Bell,
  Settings,
  Key,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Zap
} from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  connectionState: TradingConnectionState;
}

export const sidebarItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "scanner", label: "Market Scanner", icon: Scan },
  { id: "charts", label: "Charts", icon: LineChart },
  { id: "orders", label: "Orders", icon: ClipboardList },
  { id: "positions", label: "Positions", icon: Crosshair },
  { id: "trade-history", label: "Trade History", icon: History },
  { id: "pnl-history", label: "PnL History", icon: TrendingUp },
  { id: "wallet-ledger", label: "Wallet Ledger", icon: BookOpen },
  { id: "performance", label: "Performance", icon: Award },
  { id: "bots", label: "Bots", icon: Bot },
  { id: "strategies", label: "Strategies", icon: ChessKnight },
  { id: "risk-manager", label: "Risk Manager", icon: ShieldAlert },
  { id: "news", label: "News", icon: Newspaper },
  { id: "reports", label: "Reports", icon: FileSpreadsheet },
  { id: "alerts", label: "Alerts", icon: Bell },
  { id: "settings", label: "Settings", icon: Settings },
  { id: "api-keys", label: "API Keys", icon: Key },
  { id: "logout", label: "Logout", icon: LogOut, isDanger: true }
];

export function Sidebar({ activeTab, setActiveTab, collapsed, setCollapsed, connectionState }: SidebarProps) {
  return (
    <aside
      className={`fixed left-0 top-0 z-40 h-screen transition-all duration-300 border-r border-slate-800/80 bg-slate-950/90 backdrop-blur-xl flex flex-col justify-between ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="flex h-16 items-center justify-between px-4 border-b border-slate-800/80">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20">
              <Zap className="h-5 w-5 text-white" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-lg tracking-wider text-slate-100 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  LUMO AI
                </span>
                <span className="text-[10px] tracking-widest text-slate-400 uppercase font-semibold">
                  Enterprise v2.5
                </span>
              </div>
            )}
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-100 hover:border-slate-700 transition"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>

        {/* Navigation List */}
        <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)] scrollbar-thin scrollbar-thumb-slate-800">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                title={collapsed ? item.label : undefined}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border border-cyan-500/30 shadow-md shadow-cyan-500/10"
                    : item.isDanger
                    ? "text-rose-400 hover:bg-rose-500/10 hover:text-rose-300"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                <Icon className={`h-5 w-5 shrink-0 ${isActive ? "text-cyan-400" : ""}`} />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer / Account Profile */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/40">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 shrink-0 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center font-bold text-white text-xs">
            AI
          </div>
          {!collapsed && (
            <div className="flex flex-col overflow-hidden">
              <span className="text-xs font-semibold text-slate-200 truncate">Quantitative Trader</span>
              <span className={`flex items-center gap-1 font-mono text-[10px] ${connectionState === "live" ? "text-emerald-400" : "text-amber-400"}`}>
                <span className={`h-1.5 w-1.5 rounded-full ${connectionState === "live" ? "animate-pulse bg-emerald-500" : "bg-amber-500"}`}></span>
                {connectionState.toUpperCase()}
              </span>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
