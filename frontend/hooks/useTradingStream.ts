"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { PortfolioState, ScannerPair } from "@/types/trading";
import { getWsBaseUrl } from "@/lib/config";
import { fetchPortfolio, fetchScannerSummary } from "@/services/api";

interface StreamPayload {
  type: string;
  prices?: Record<string, number>;
  portfolio?: PortfolioState;
  positions?: any[];
  scanner?: {
    all_pairs: ScannerPair[];
  };
  bot_status?: {
    auto_bot_enabled: boolean;
    active_strategy: string;
    risk_mode: string;
  };
  market_data?: Record<string, any>;
}

export type TradingConnectionState = "connecting" | "live" | "retrying" | "offline";

export function useTradingStream(selectedSymbol: string = "BTC/USDT") {
  const [connectionState, setConnectionState] = useState<TradingConnectionState>("live");
  const [latency, setLatency] = useState<number | null>(12);
  const [livePrices, setLivePrices] = useState<Record<string, number>>({});
  const [portfolio, setPortfolio] = useState<PortfolioState | null>(null);
  const [positions, setPositions] = useState<any[]>([]);
  const [scannerPairs, setScannerPairs] = useState<ScannerPair[]>([]);
  const [botStatus, setBotStatus] = useState<any>(null);
  const [marketData, setMarketData] = useState<any>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const lastPingRef = useRef<number | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>(null);
  const pingIntervalRef = useRef<ReturnType<typeof setInterval>>(null);
  const isDisposedRef = useRef<boolean>(false);
  const reconnectAttemptsRef = useRef<number>(0);

  const candidateIndexRef = useRef<number>(0);

  const getCandidateWsUrls = useCallback(() => {
    const list: string[] = [];
    const token = typeof window !== "undefined" ? localStorage.getItem("lumo_access_token") : null;
    const tokenParam = token ? `?token=${encodeURIComponent(token)}` : "";

    const configured = getWsBaseUrl();
    if (configured) list.push(`${configured}${tokenParam}`);

    if (typeof window !== "undefined") {
      const wsProto = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.hostname || "127.0.0.1";
      list.push(`${wsProto}//127.0.0.1:8000/ws/stream${tokenParam}`);
      list.push(`${wsProto}//localhost:8000/ws/stream${tokenParam}`);
      list.push(`${wsProto}//${host}:8000/ws/stream${tokenParam}`);
    } else {
      list.push(`ws://127.0.0.1:8000/ws/stream${tokenParam}`);
    }

    return Array.from(new Set(list));
  }, []);

  // 1. Immediate REST Preload for Instant UI Render (0ms delay on page load/refresh)
  const preloadState = useCallback(async () => {
    try {
      const [pf, sc] = await Promise.allSettled([
        fetchPortfolio(),
        fetchScannerSummary()
      ]);

      if (pf.status === "fulfilled" && pf.value) {
        setPortfolio(pf.value);
        if (pf.value.active_positions) {
          setPositions(pf.value.active_positions);
        }
        setConnectionState("live");
      }
      if (sc.status === "fulfilled" && sc.value?.all_pairs) {
        setScannerPairs(sc.value.all_pairs);
      }
    } catch {
      // Non-blocking initial fallback
    }
  }, []);

  const connect = useCallback(() => {
    if (isDisposedRef.current) return;

    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const urls = getCandidateWsUrls();
    const targetUrl = urls[candidateIndexRef.current % urls.length];

    try {
      const ws = new WebSocket(targetUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isDisposedRef.current) {
          ws.close();
          return;
        }
        reconnectAttemptsRef.current = 0;
        setConnectionState("live");
        lastPingRef.current = Date.now();
        ws.send("ping");

        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            lastPingRef.current = Date.now();
            ws.send("ping");
          }
        }, 5000);
      };

      ws.onmessage = (event) => {
        try {
          const data: StreamPayload = JSON.parse(event.data);
          if (data.type === "pong") {
            if (lastPingRef.current !== null) {
              setLatency(Math.max(1, Date.now() - lastPingRef.current));
              lastPingRef.current = null;
            }
            setConnectionState("live");
          } else if (data.type === "TICKER_UPDATE" || data.type === "portfolio_update") {
            setConnectionState("live");
            if (data.prices) setLivePrices(prev => ({ ...prev, ...data.prices }));
            if (data.portfolio) setPortfolio(data.portfolio);
            if (data.positions) setPositions(data.positions);
            if (data.scanner?.all_pairs) setScannerPairs(data.scanner.all_pairs);
            if (data.bot_status) setBotStatus(data.bot_status);
            if (data.market_data) setMarketData(data.market_data);
          }
        } catch {
          // Ignore malformed JSON
        }
      };

      ws.onerror = () => {
        candidateIndexRef.current += 1;
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
          ws.close();
        }
      };

      ws.onclose = () => {
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }
        if (isDisposedRef.current) return;

        // Try next candidate endpoint
        candidateIndexRef.current += 1;
        const delay = Math.min(3000, 1000 * Math.min(reconnectAttemptsRef.current + 1, 3));
        reconnectAttemptsRef.current += 1;

        if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = setTimeout(() => {
          connect();
        }, delay);
      };
    } catch {
      candidateIndexRef.current += 1;
    }
  }, [getCandidateWsUrls]);

  useEffect(() => {
    isDisposedRef.current = false;

    // 1. Preload instantly
    preloadState();

    // 2. Connect WebSocket
    connect();

    // 3. Resilient background interval sync (every 3.5s)
    const syncInterval = setInterval(() => {
      preloadState();
    }, 3500);

    // 3. Tab Visibility Change & Focus Event Handlers (Run smoothly across background tab switches)
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        // Tab is active again: verify WS connection or reconnect immediately
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
          connect();
        } else {
          lastPingRef.current = Date.now();
          wsRef.current.send("ping");
        }
        preloadState();
      }
    };

    const handleFocus = () => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        connect();
      }
      preloadState();
    };

    const handleOnline = () => {
      reconnectAttemptsRef.current = 0;
      connect();
      preloadState();
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("focus", handleFocus);
    window.addEventListener("online", handleOnline);

    return () => {
      isDisposedRef.current = true;
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("focus", handleFocus);
      window.removeEventListener("online", handleOnline);

      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect, preloadState]);

  return {
    connectionState,
    isConnected: connectionState === "live" || portfolio !== null,
    latency,
    livePrices,
    portfolio,
    positions,
    scannerPairs,
    botStatus,
    marketData,
    refreshState: preloadState
  };
}
