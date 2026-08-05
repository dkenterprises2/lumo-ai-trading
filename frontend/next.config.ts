import type { NextConfig } from "next";

if (process.env.NODE_ENV === "production") {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL;

  if (!apiUrl || apiUrl.trim() === "" || apiUrl.includes("localhost") || apiUrl.includes("127.0.0.1")) {
    throw new Error(
      "[BUILD_ERROR] Production builds require NEXT_PUBLIC_API_URL pointing to the production API server domain."
    );
  }
  if (!wsUrl || wsUrl.trim() === "" || wsUrl.includes("localhost") || wsUrl.includes("127.0.0.1")) {
    throw new Error(
      "[BUILD_ERROR] Production builds require NEXT_PUBLIC_WS_URL pointing to the production WebSocket server domain."
    );
  }
}

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
