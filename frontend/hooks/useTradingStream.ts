"use client";

import { useEffect, useState, useRef } from "react";
import { PortfolioState, ScannerPair } from "@/types/trading";
import { WS_BASE_URL } from "@/lib/config";

interface StreamPayload {
  type: string;
  prices?: Record<string, number>;
  portfolio?: PortfolioState;
  scanner?: {
    all_pairs: ScannerPair[];
  };
}

export type TradingConnectionState = "connecting" | "live" | "retrying" | "offline";

export function useTradingStream(selectedSymbol: string = "BTC/USDT") {
  const [connectionState, setConnectionState] = useState<TradingConnectionState>("connecting");
  const [latency, setLatency] = useState<number | null>(null);
  const [livePrices, setLivePrices] = useState<Record<string, number>>({});
  const [portfolio, setPortfolio] = useState<PortfolioState | null>(null);
  const [scannerPairs, setScannerPairs] = useState<ScannerPair[]>([]);
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
      const ws = new WebSocket(WS_BASE_URL);

      wsRef.current = ws;

      ws.onopen = () => {
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
        try {
          const data: StreamPayload = JSON.parse(event.data);
          if (data.type === "pong" && lastPingRef.current !== null) {
            setLatency(Date.now() - lastPingRef.current);
            lastPingRef.current = null;
          } else if (data.type === "TICKER_UPDATE") {
            if (data.prices) setLivePrices(prev => ({ ...prev, ...data.prices }));
            if (data.portfolio) setPortfolio(data.portfolio);
            if (data.scanner?.all_pairs) setScannerPairs(data.scanner.all_pairs);
          }
        } catch { /* Ignore malformed messages and retain the last valid state. */ }
      };

      ws.onclose = () => {
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

      ws.onerror = () => {
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) ws.close();
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
    isConnected: connectionState === "live",
    connectionState,
    latency,
    livePrices,
    portfolio,
    scannerPairs
  };
}
