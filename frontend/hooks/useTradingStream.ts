"use client";

import { useEffect, useState, useRef } from "react";
import { PortfolioState, ScannerPair } from "@/types/trading";
import { WS_BASE_URL } from "@/lib/config";

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
  const [connectionState, setConnectionState] = useState<TradingConnectionState>("connecting");
  const [latency, setLatency] = useState<number | null>(null);
  const [livePrices, setLivePrices] = useState<Record<string, number>>({});
  const [portfolio, setPortfolio] = useState<PortfolioState | null>(null);
  const [positions, setPositions] = useState<any[]>([]);
  const [scannerPairs, setScannerPairs] = useState<ScannerPair[]>([]);
  const [botStatus, setBotStatus] = useState<any>(null);
  const [marketData, setMarketData] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const lastPingRef = useRef<number | null>(null);

  useEffect(() => {
    let pingInterval: ReturnType<typeof setInterval> | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let disposed = false;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 10;

    const connect = () => {
      if (disposed || reconnectAttempts >= maxReconnectAttempts) return;
      setConnectionState(reconnectAttempts > 0 ? "retrying" : "connecting");

      const token = typeof window !== "undefined" ? localStorage.getItem("lumo_access_token") : null;
      const wsUrl = token ? `${WS_BASE_URL}?token=${encodeURIComponent(token)}` : WS_BASE_URL;
      const ws = new WebSocket(wsUrl);

      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WS CONNECTED");
        reconnectAttempts = 0;
        setConnectionState("live");
        lastPingRef.current = Date.now();
        ws.send("ping");
        pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            lastPingRef.current = Date.now();
            ws.send("ping");
          }
        }, 15_000);
      };

      ws.onmessage = (event) => {
        console.log("WS MESSAGE", event.data);
        try {
          const data: StreamPayload = JSON.parse(event.data);
          if (data.type === "pong" && lastPingRef.current !== null) {
            setLatency(Date.now() - lastPingRef.current);
            lastPingRef.current = null;
          } else if (data.type === "TICKER_UPDATE" || data.type === "portfolio_update") {
            if (data.prices) setLivePrices(prev => ({ ...prev, ...data.prices }));
            if (data.portfolio) setPortfolio(data.portfolio);
            if (data.positions) setPositions(data.positions);
            if (data.scanner?.all_pairs) setScannerPairs(data.scanner.all_pairs);
            if (data.bot_status) setBotStatus(data.bot_status);
            if (data.market_data) setMarketData(data.market_data);
          }
        } catch { /* Ignore malformed messages and retain last valid state. */ }
      };

      ws.onerror = (e) => {
        console.error("WS ERROR", e);
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) ws.close();
      };

      ws.onclose = (e) => {
        console.warn("WS CLOSED", e.code, e.reason);
        if (pingInterval) {
          clearInterval(pingInterval);
          pingInterval = null;
        }
        if (disposed) return;
        if (reconnectAttempts >= maxReconnectAttempts) {
          setConnectionState("offline");
          return;
        }
        setConnectionState("retrying");
        const reconnectDelay = Math.min(15_000, 1_000 * 2 ** reconnectAttempts);
        reconnectAttempts += 1;
        reconnectTimer = setTimeout(connect, reconnectDelay);
      };

    };

    connect();

    return () => {
      disposed = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (wsRef.current) wsRef.current.close();
      if (pingInterval) clearInterval(pingInterval);
    };
  }, []);

  return {
    connectionState,
    isConnected: connectionState === "live",
    latency,
    livePrices,
    portfolio,
    positions,
    scannerPairs,
    botStatus,
    marketData
  };

}
