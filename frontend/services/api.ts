import {
  PortfolioState,
  MarketSummary,
  AiSignal,
  NewsSentiment,
  ScannerPair,
  AccountingAudit
} from "@/types/trading";

import { API_BASE_URL as API_BASE } from "@/lib/config";


export class ApiError extends Error {
  constructor(message: string, public readonly status?: number) {
    super(message);
    this.name = "ApiError";
  }
}

function getApiCandidateBases(): string[] {
  const candidates: string[] = [];

  // 1. Relative path for Next.js port 3000 dev server & rewrites
  candidates.push("");

  if (API_BASE && !API_BASE.includes("example.com")) {
    candidates.push(API_BASE);
  }
  
  if (typeof window !== "undefined" && window.location?.hostname) {
    const host = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : "";
    candidates.push(`${window.location.protocol}//${host}${port}`);
    candidates.push(`http://${host}:8000`);
  }

  candidates.push("http://127.0.0.1:8000");
  candidates.push("http://localhost:8000");

  return Array.from(new Set(candidates));
}

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const token = typeof window !== "undefined" ? localStorage.getItem("lumo_access_token") : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const bases = getApiCandidateBases();
  let response: Response | null = null;

  for (const base of bases) {
    try {
      const res = await fetch(`${base}${path}`, {
        ...init,
        headers,
        credentials: "include",
        cache: "no-store"
      });
      if (res && (res.ok || res.status < 500)) {
        response = res;
        break;
      }
    } catch (err) {
      // Continue to next candidate host
    }
  }

  if (!response) {
    throw new ApiError("Unable to connect to Lumo Trading backend server. Please verify python main.py backend process is running.", 0);
  }


  // Handle Token Refresh on 401 Unauthorized
  if (response.status === 401 && path !== "/api/auth/login" && path !== "/api/auth/register" && path !== "/api/auth/refresh") {
    try {
      const activeBase = bases[0] || "http://127.0.0.1:8000";
      const refreshRes = await fetch(`${activeBase}/api/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include"
      });

      if (refreshRes.ok) {
        const refreshData = await refreshRes.json();
        if (refreshData.access_token) {
          localStorage.setItem("lumo_access_token", refreshData.access_token);
          headers["Authorization"] = `Bearer ${refreshData.access_token}`;

          // Retry original request with new token
          for (const base of bases) {
            try {
              const retryRes = await fetch(`${base}${path}`, {
                ...init,
                headers,
                credentials: "include",
                cache: "no-store"
              });
              if (retryRes) {
                response = retryRes;
                break;
              }
            } catch (e) {
              // Try next base
            }
          }
        }
      }
    } catch (e) {
      // Fallthrough to handle original response
    }
  }

  return response;
}



async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await apiFetch(path, init);

  if (!response.ok) {
    let detail = "";
    try {
      const body: unknown = await response.json();
      if (typeof body === "object" && body !== null && "detail" in body && typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // A non-JSON error response still has a meaningful HTTP status.
    }
    throw new ApiError(detail || `Backend request failed (${response.status}).`, response.status);
  }

  return response.json() as Promise<T>;
}


export async function fetchPortfolio(): Promise<PortfolioState> {
  return requestJson<PortfolioState>("/api/portfolio");
}

export async function fetchAccountingAudit(): Promise<AccountingAudit> {
  return requestJson<AccountingAudit>("/api/accounting/audit");
}

export async function fetchMarketSummary(symbol: string, timeframe: string = "1h"): Promise<MarketSummary> {
  return requestJson<MarketSummary>(`/api/market-summary?symbol=${encodeURIComponent(symbol)}&timeframe=${encodeURIComponent(timeframe)}`);
}

export async function fetchAiSignal(symbol: string, strategy: string = "AI Hybrid", riskMode: string = "Moderate"): Promise<AiSignal> {
  return requestJson<AiSignal>(`/api/ai-signal/${encodeURIComponent(symbol)}?strategy=${encodeURIComponent(strategy)}&risk_mode=${encodeURIComponent(riskMode)}`);
}

export async function fetchNewsSentiment(): Promise<NewsSentiment> {
  return requestJson<NewsSentiment>("/api/news-sentiment");
}

export interface ScannerSummary {
  timestamp?: number;
  top_buys?: ScannerPair[];
  top_sells?: ScannerPair[];
  all_pairs?: ScannerPair[];
}

export async function fetchScannerSummary(): Promise<ScannerSummary> {
  return requestJson<ScannerSummary>("/api/scanner/summary");
}

export async function submitOrder(payload: {
  symbol: string;
  side: "LONG" | "SHORT";
  order_type: string;
  allocation_usd: number;
  leverage: number;
  stop_loss_price?: number | null;
  take_profit_price?: number | null;
}): Promise<{ status: string; message: string }> {
  return requestJson<{ status: string; message: string }>("/api/trade/order", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function handlePositionAction(payload: {
  symbol: string;
  action: "CLOSE" | "PARTIAL_CLOSE" | "REVERSE" | "EDIT_SL_TP";
  ratio?: number;
  new_stop_loss?: number;
  new_take_profit?: number;
}): Promise<{ status: string; message: string }> {
  return requestJson<{ status: string; message: string }>("/api/trade/position-action", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function toggleBot(enable: boolean): Promise<{ status: string; message: string; auto_bot_enabled: boolean }> {
  return requestJson<{ status: string; message: string; auto_bot_enabled: boolean }>(`/api/bot/toggle?enable=${enable}`, {
    method: "POST"
  });
}

export async function setStrategy(strategy_name: string, risk_mode: string = "Moderate"): Promise<{ status: string; message: string; strategy_name?: string; risk_mode?: string }> {
  return requestJson<{ status: string; message: string; strategy_name?: string; risk_mode?: string }>(`/api/bot/strategy?strategy_name=${encodeURIComponent(strategy_name)}&risk_mode=${encodeURIComponent(risk_mode)}`, {
    method: "POST",
    body: JSON.stringify({ strategy_name, risk_mode })
  });
}


export async function depositVirtualFunds(amount: number): Promise<{ status: string; message: string; usdt_balance: number }> {
  return requestJson<{ status: string; message: string; usdt_balance: number }>("/api/wallet/deposit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount })
  });
}

export async function withdrawVirtualFunds(amount: number): Promise<{ status: string; message: string; usdt_balance: number }> {
  return requestJson<{ status: string; message: string; usdt_balance: number }>("/api/wallet/withdraw", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount })
  });
}

export async function resetPaperAccount(): Promise<{ status: string; message: string }> {
  return requestJson<{ status: string; message: string }>("/api/wallet/reset-paper-account", {
    method: "POST"
  });
}

export async function deleteUserAccount(): Promise<{ status: string; message: string }> {
  return requestJson<{ status: string; message: string }>("/api/user/delete-account", {
    method: "DELETE"
  });
}

export async function saveExecutionParameters(default_allocation_usd: number, default_leverage: number): Promise<{ status: string; message: string; default_allocation_usd: number; default_leverage: number }> {
  return requestJson<{ status: string; message: string; default_allocation_usd: number; default_leverage: number }>("/api/bot/parameters", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ default_allocation_usd, default_leverage })
  });
}


