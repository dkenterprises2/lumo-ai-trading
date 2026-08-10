"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { TradingConnectionState } from "@/hooks/useTradingStream";
import {
  LayoutDashboard,
  Brain,
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
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Zap
} from "lucide-react";


interface SidebarProps {
  activeTab?: string;
  setActiveTab?: (tab: string) => void;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  connectionState: TradingConnectionState;
}

import { LogOut, User as UserIcon } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export const sidebarItems = [
  { id: "dashboard", label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { id: "learning", label: "Self-Learning AI", href: "/learning", icon: Brain },
  { id: "copilot", label: "AI Copilot", href: "/copilot", icon: Bot },

  { id: "nl-strategy", label: "NL Strategy Builder", href: "/nl-strategy-builder", icon: ChessKnight },
  { id: "portfolio-assistant", label: "Portfolio Assistant", href: "/portfolio-assistant", icon: TrendingUp },
  { id: "investigations", label: "Trade RCA", href: "/investigations", icon: Crosshair },
  { id: "operations-ai", label: "Operations AI (SRE)", href: "/operations-ai", icon: ShieldAlert },
  { id: "rag-library", label: "RAG Knowledge", href: "/rag-library", icon: BookOpen },
  { id: "orchestration", label: "Agent Orchestration", href: "/orchestration", icon: Zap },
  { id: "ai-actions", label: "AI Governance", href: "/governance/ai-actions", icon: Award },
  { id: "executive-briefings", label: "Executive Briefings", href: "/executive-briefings", icon: FileSpreadsheet },
  { id: "ai-guardrails", label: "AI Guardrails", href: "/ai-guardrails", icon: Key },
  { id: "scanner", label: "Market Scanner", href: "/scanner", icon: Scan },
  { id: "charts", label: "Charts", href: "/charts", icon: LineChart },
  { id: "orders", label: "Orders", href: "/orders", icon: ClipboardList },
  { id: "positions", label: "Positions", href: "/positions", icon: Crosshair },
  { id: "trade-history", label: "Trade History", href: "/history", icon: History },
  { id: "pnl-history", label: "PnL History", href: "/pnl", icon: TrendingUp },
  { id: "wallet-ledger", label: "Wallet Ledger", href: "/ledger", icon: BookOpen },
  { id: "performance", label: "Performance", href: "/performance", icon: Award },
  { id: "bots", label: "Bots", href: "/bots", icon: Bot },
  { id: "strategies", label: "Strategies", href: "/strategies", icon: ChessKnight },
  { id: "risk-manager", label: "Risk Manager", href: "/risk", icon: ShieldAlert },
  { id: "news", label: "News", href: "/news", icon: Newspaper },
  { id: "reports", label: "Reports", href: "/reports", icon: FileSpreadsheet },
  { id: "alerts", label: "Alerts", href: "/alerts", icon: Bell },
  { id: "settings", label: "Settings", href: "/settings", icon: Settings },
  { id: "api-keys", label: "API Keys", href: "/api-keys", icon: Key }
];


export function Sidebar({ activeTab, setActiveTab, collapsed, setCollapsed, connectionState }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

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
          {(user?.role?.toUpperCase() === 'SUPER_ADMIN' || user?.role?.toUpperCase() === 'SUPERADMIN' || user?.email?.toLowerCase() === 'jiodkd@gmail.com') && (
            <Link
              href="/admin"
              title={collapsed ? "Super Admin Console" : undefined}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold transition-all duration-200 ${
                pathname?.startsWith("/admin")
                  ? "bg-gradient-to-r from-purple-500/30 to-blue-500/20 text-purple-300 border border-purple-500/40 shadow-lg shadow-purple-500/20"
                  : "bg-purple-500/10 text-purple-400 border border-purple-500/20 hover:bg-purple-500/20"
              }`}
            >
              <ShieldCheck className="h-5 w-5 shrink-0 text-purple-400" />
              {!collapsed && <span className="truncate">Super Admin Console</span>}
            </Link>
          )}

          {sidebarItems.map((item) => {

            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/" && pathname?.startsWith(item.href));
            return (
              <Link
                key={item.id}
                href={item.href}
                onClick={() => setActiveTab && setActiveTab(item.id)}
                title={collapsed ? item.label : undefined}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border border-cyan-500/30 shadow-md shadow-cyan-500/10"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                <Icon className={`h-5 w-5 shrink-0 ${isActive ? "text-cyan-400" : ""}`} />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer / Account Profile & Logout */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/40">
        {user ? (
          <div className="flex items-center justify-between">
            <Link href="/profile" className="flex items-center gap-3 overflow-hidden">
              <img
                src={user.avatar || "https://api.dicebear.com/7.x/avataaars/svg?seed=LumoTrader"}
                alt={user.name}
                className="h-9 w-9 shrink-0 rounded-full border border-cyan-500/30 bg-slate-900"
              />
              {!collapsed && (
                <div className="flex flex-col overflow-hidden">
                  <span className="text-xs font-semibold text-slate-200 truncate">{user.name}</span>
                  <span className="text-[10px] text-cyan-400 truncate">{user.trading_mode} Mode</span>
                </div>
              )}
            </Link>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20 transition-colors"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-cyan-500/10 border border-cyan-500/20 rounded-xl text-xs font-semibold text-cyan-400 hover:bg-cyan-500/20 transition-colors"
          >
            <UserIcon className="h-4 w-4" />
            {!collapsed && <span>Sign In</span>}
          </Link>
        )}
      </div>
    </aside>
  );
}

