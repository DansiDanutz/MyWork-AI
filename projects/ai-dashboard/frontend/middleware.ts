import { NextRequest, NextResponse } from "next/server";

import {
  browserAuthConfigIsValid,
  browserAuthorizationIsValid,
  type BrowserAuthConfig,
} from "@/lib/browser-auth";

function authConfig(): BrowserAuthConfig {
  return {
    username: process.env.AI_DASHBOARD_BROWSER_USERNAME?.trim() ?? "",
    browserSecret: process.env.AI_DASHBOARD_BROWSER_SECRET ?? "",
    backendToken: process.env.AI_DASHBOARD_ADMIN_TOKEN ?? "",
  };
}

export async function middleware(request: NextRequest) {
  const config = authConfig();
  if (!browserAuthConfigIsValid(config)) {
    return new NextResponse("Dashboard authentication is not configured.", {
      status: 503,
      headers: { "cache-control": "no-store" },
    });
  }

  const valid = await browserAuthorizationIsValid(
    request.headers.get("authorization"),
    config,
  );
  if (!valid) {
    return new NextResponse("Administrator authentication is required.", {
      status: 401,
      headers: {
        "cache-control": "no-store",
        "www-authenticate": 'Basic realm="AI Dashboard", charset="UTF-8"',
      },
    });
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
