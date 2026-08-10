import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Let client-side useAdminGuard perform full JWT & RBAC validation via /api/auth/me
  return NextResponse.next();
}


export const config = {
  matcher: ["/admin/:path*"]
};
