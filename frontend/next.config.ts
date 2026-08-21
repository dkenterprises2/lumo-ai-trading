import type { NextConfig } from "next";

if (process.env.NODE_ENV === "production" && process.env.ALLOW_LOCALHOST_BUILD !== "true" && !process.env.NEXT_PUBLIC_API_URL?.includes("localhost")) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL;

  if (!apiUrl || apiUrl.trim() === "") {
    throw new Error(
      "[BUILD_ERROR] Production builds require NEXT_PUBLIC_API_URL pointing to the production API server domain."
    );
  }
}

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*"
      }
    ];
  }
};

export default nextConfig;
