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

  // 1. In browser, use same-origin relative URL first for instant Next.js proxy rewrite without cross-origin preflight delays
  if (typeof window !== "undefined") {
    candidates.push("");
  }

  // 2. Explicit API Base URL if configured
  if (API_BASE && !API_BASE.includes("example.com")) {
    candidates.push(API_BASE);
  }

  // 3. Direct FastAPI backend servers
  candidates.push("http://127.0.0.1:8000");
  candidates.push("http://localhost:8000");

  if (typeof window !== "undefined" && window.location?.hostname) {
    const host = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : "";
    if (port !== ":8000") {
      candidates.push(`http://${host}:8000`);
    }
  }

  candidates.push("");
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
      if (res) {
        response = res;
        // Break immediately if backend responded with success or structured API response (not Next.js 404/500 proxy error)
        if (res.ok || res.status === 400 || res.status === 401 || res.status === 422) {
          break;
        }
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
      if (typeof body === "object" && body !== null) {
        const obj = body as Record<string, any>;
        if (typeof obj.detail === "string") {
          detail = obj.detail;
        } else if (typeof obj.detail === "object" && obj.detail !== null && typeof obj.detail.message === "string") {
          detail = obj.detail.message;
        } else if (Array.isArray(obj.detail)) {
          detail = obj.detail.map((item: any) => item.msg || JSON.stringify(item)).join(", ");
        } else if (typeof obj.message === "string") {
          detail = obj.message;
        } else if (typeof obj.error === "string") {
          detail = obj.error;
        }
      }
    } catch {
      // A non-JSON error response still has a meaningful HTTP status.
    }
    throw new ApiError(detail || `Backend request failed (${response.status}).`, response.status);
  }

  return response.json() as Promise<T>;
}


export async function checkBackendHealth(): Promise<{ status: string; service?: string; cors_frontend?: string }> {
  return requestJson<{ status: string; service?: string; cors_frontend?: string }>("/api/system/health");
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
  const data = await requestJson<{ status: string; message: string; auto_bot_enabled: boolean }>(`/api/bot/toggle?enable=${enable}`, {
    method: "POST"
  });
  console.log("Toggle response", data);
  return data;
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

export async function fetchRiskStatus(): Promise<any> {
  return requestJson<any>("/api/risk/status");
}

export async function fetchRiskConfig(): Promise<any> {
  return requestJson<any>("/api/risk/config");
}

export async function updateRiskConfig(payload: Record<string, any>): Promise<any> {
  return requestJson<any>("/api/risk/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
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

export async function fetchAllUnifiedTrades(): Promise<{ status: string; total_count: number; trades: any[] }> {
  return requestJson<{ status: string; total_count: number; trades: any[] }>("/api/portfolio/all-trades");
}

export async function fetchShadowCandles(
  symbol: string = "BTC/USDT",
  timeframe: string = "1d",
  startDate?: string,
  endDate?: string
): Promise<{ status: string; symbol: string; timeframe: string; count: number; candles: Array<{ time: number; open: number; high: number; low: number; close: number; volume: number }> }> {
  let url = `/api/shadow/candles?symbol=${encodeURIComponent(symbol)}&timeframe=${encodeURIComponent(timeframe)}`;
  if (startDate) url += `&start_date=${encodeURIComponent(startDate)}`;
  if (endDate) url += `&end_date=${encodeURIComponent(endDate)}`;
  return requestJson(url);
}

export async function startShadowReplay(
  symbol: string = "BTC/USDT",
  timeframe: string = "1d",
  startDate?: string,
  endDate?: string,
  playbackSpeed: number = 5
): Promise<any> {
  return requestJson<any>("/api/shadow/replay/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      symbol,
      timeframe,
      start_date: startDate,
      end_date: endDate,
      playback_speed: playbackSpeed
    })
  });
}

export async function pauseShadowReplay(sessionId?: string): Promise<any> {
  const url = sessionId ? `/api/shadow/replay/pause?session_id=${encodeURIComponent(sessionId)}` : "/api/shadow/replay/pause";
  return requestJson<any>(url, { method: "POST" });
}

export async function resumeShadowReplay(sessionId?: string): Promise<any> {
  const url = sessionId ? `/api/shadow/replay/resume?session_id=${encodeURIComponent(sessionId)}` : "/api/shadow/replay/resume";
  return requestJson<any>(url, { method: "POST" });
}

export async function stepShadowReplay(steps: number = 1, sessionId?: string): Promise<any> {
  return requestJson<any>("/api/shadow/replay/step", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ steps, session_id: sessionId })
  });
}

export async function seekShadowReplay(targetPct: number, sessionId?: string): Promise<any> {
  return requestJson<any>("/api/shadow/replay/seek", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_pct: targetPct, session_id: sessionId })
  });
}

export async function stopShadowReplay(sessionId?: string): Promise<any> {
  const url = sessionId ? `/api/shadow/replay/stop?session_id=${encodeURIComponent(sessionId)}` : "/api/shadow/replay/stop";
  return requestJson<any>(url, { method: "POST" });
}

export async function setShadowReplaySpeed(speed: number, sessionId?: string): Promise<any> {
  return requestJson<any>("/api/shadow/replay/speed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ playback_speed: speed, speed, session_id: sessionId })
  });
}

export async function getLearnedLessons(): Promise<any> {
  return requestJson<any>("/api/learning/lessons");
}

export async function updateLessonStatus(lessonId: string, newStatus: string): Promise<any> {
  return requestJson<any>(`/api/learning/lessons/${encodeURIComponent(lessonId)}/state`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ new_status: newStatus })
  });
}

export async function getTradeExperiences(symbol?: string, limit: number = 20): Promise<any> {
  const q = symbol ? `?symbol=${encodeURIComponent(symbol)}&limit=${limit}` : `?limit=${limit}`;
  return requestJson<any>(`/api/learning/experiences${q}`);
}


// --- SPOT RESEARCH & NEW/MEME COIN DISCOVERY API ---
export async function fetchDiscoveredCoins(category?: string, forceRefresh: boolean = false) {
  const params = new URLSearchParams();
  if (category) params.append("category", category);
  if (forceRefresh) params.append("force_refresh", "true");
  const res = await fetch(`/api/spot/discovered-coins?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch discovered coins");
  return res.json();
}

export async function fetchCoinResearch(symbol: string) {
  const res = await fetch(`/api/spot/coin/${encodeURIComponent(symbol)}/research`);
  if (!res.ok) throw new Error(`Failed to fetch research for ${symbol}`);
  return res.json();
}

export async function executePaperValidationTest(symbol: string, allocationUsd: number = 250) {
  const res = await fetch(`/api/spot/coin/${encodeURIComponent(symbol)}/paper-test?allocation_usd=${allocationUsd}`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to execute paper test" }));
    throw new Error(err.detail || "Paper test rejected");
  }
  return res.json();
}

export async function fetchPaperValidationTests() {
  const res = await fetch(`/api/spot/paper-tests`);
  if (!res.ok) throw new Error("Failed to fetch paper validation tests");
  return res.json();
}

export async function fetchResearchEvidence(limit: number = 50, category?: string) {
  const params = new URLSearchParams();
  params.append("limit", limit.toString());
  if (category) params.append("category", category);
  const res = await fetch(`/api/spot/evidence/events?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch research evidence");
  return res.json();
}

// --- AUTONOMOUS SPOT BOT & ISOLATED SUB-WALLET API ---
export async function fetchSpotBotStatus() {
  const res = await fetch(`/api/spot/bot/status`);
  if (!res.ok) throw new Error("Failed to fetch spot bot status");
  return res.json();
}

export async function updateSpotBotConfig(config: any) {
  const res = await fetch(`/api/spot/bot/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!res.ok) throw new Error("Failed to update spot bot config");
  return res.json();
}

export async function toggleSpotBot(enabled?: boolean) {
  const url = enabled !== undefined ? `/api/spot/bot/toggle?enabled=${enabled}` : `/api/spot/bot/toggle`;
  const res = await fetch(url, { method: "POST" });
  if (!res.ok) throw new Error("Failed to toggle spot bot");
  return res.json();
}

export async function resetSpotSubWallet(initialCapitalUsd: number = 10000) {
  const res = await fetch(`/api/spot/wallet/reset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ initial_capital_usd: initialCapitalUsd }),
  });
  if (!res.ok) throw new Error("Failed to reset spot sub-wallet");
  return res.json();
}

export async function fetchSpotBotLessons(limit: number = 20) {
  const res = await fetch(`/api/spot/bot/lessons?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch spot bot lessons");
  return res.json();
}

export async function closeSpotBotTrade(tradeId: string) {
  const res = await fetch(`/api/spot/bot/close-trade/${encodeURIComponent(tradeId)}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to close spot bot trade");
  return res.json();
}
