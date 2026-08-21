const isProduction = process.env.NODE_ENV === "production";
const rawApiUrl = process.env.NEXT_PUBLIC_API_URL;
const rawWsUrl = process.env.NEXT_PUBLIC_WS_URL;

export function getApiBaseUrl(): string {
  if (rawApiUrl && rawApiUrl.trim() !== "") {
    return rawApiUrl.trim().replace(/\/+$/, "");
  }
  if (typeof window !== "undefined") {
    const host = window.location.hostname || "localhost";
    const port = window.location.port === "3000" ? "8000" : (window.location.port || "8000");
    return `${window.location.protocol}//${host}:${port}`;
  }
  return "http://127.0.0.1:8000";
}

export function getWsBaseUrl(): string {
  if (rawWsUrl && rawWsUrl.trim() !== "") {
    return rawWsUrl.trim();
  }
  if (typeof window !== "undefined") {
    const wsProto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.hostname || "localhost";
    const port = window.location.port === "3000" ? "8000" : (window.location.port || "8000");
    return `${wsProto}//${host}:${port}/ws/stream`;
  }
  return isProduction ? "wss://lumo-ai-trading-2.onrender.com/ws/stream" : "ws://127.0.0.1:8000/ws/stream";
}

export const API_BASE_URL: string = getApiBaseUrl();
export const WS_BASE_URL: string = getWsBaseUrl();

if (typeof window !== "undefined") {
  console.log(`[CONFIG] API_BASE_URL=${API_BASE_URL} | WS_BASE_URL=${WS_BASE_URL}`);
}
