const isProduction = process.env.NODE_ENV === "production";
const rawApiUrl = process.env.NEXT_PUBLIC_API_URL;
const rawWsUrl = process.env.NEXT_PUBLIC_WS_URL;

if (isProduction) {
  if (!rawApiUrl || rawApiUrl.trim() === "") {
    throw new Error(
      "[CONFIG_ERROR] NEXT_PUBLIC_API_URL is required in production environment. Production builds must never compile with default API URL fallback."
    );
  }
  if (!rawWsUrl || rawWsUrl.trim() === "") {
    throw new Error(
      "[CONFIG_ERROR] NEXT_PUBLIC_WS_URL is required in production environment. Production builds must never compile with default WebSocket URL fallback."
    );
  }
}

export const API_BASE_URL: string = (rawApiUrl && rawApiUrl.trim() !== "")
  ? rawApiUrl.trim().replace(/\/+$/, "")
  : "http://127.0.0.1:8000";

export const WS_BASE_URL: string = (rawWsUrl && rawWsUrl.trim() !== "")
  ? rawWsUrl.trim()
  : "ws://127.0.0.1:8000/ws/stream";

if (typeof window !== "undefined") {
  console.log(`[CONFIG]\nAPI_BASE_URL=${API_BASE_URL}\nWS_BASE_URL=${WS_BASE_URL}`);
}
