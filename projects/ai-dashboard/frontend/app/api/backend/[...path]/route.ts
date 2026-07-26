import { NextRequest, NextResponse } from "next/server";

import {
  browserAuthConfigIsValid,
  browserAuthorizationIsValid,
  type BrowserAuthConfig,
} from "@/lib/browser-auth";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const MAX_REQUEST_BYTES = 1_000_000;
const MUTATING_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);
const SAFE_SEGMENT = /^[A-Za-z0-9._~-]+$/;

function authConfig(): BrowserAuthConfig & { backendUrl: string } {
  return {
    username: process.env.AI_DASHBOARD_BROWSER_USERNAME?.trim() ?? "",
    browserSecret: process.env.AI_DASHBOARD_BROWSER_SECRET ?? "",
    backendToken: process.env.AI_DASHBOARD_ADMIN_TOKEN ?? "",
    backendUrl: process.env.AI_DASHBOARD_BACKEND_URL?.trim() ?? "",
  };
}

function backendBaseUrl(value: string): URL | null {
  try {
    const url = new URL(value);
    const localHttp =
      url.protocol === "http:" && ["127.0.0.1", "localhost"].includes(url.hostname);
    if (url.protocol !== "https:" && !localHttp) return null;
    if (url.username || url.password || url.search || url.hash) return null;
    return url;
  } catch {
    return null;
  }
}

function errorResponse(status: number, detail: string): NextResponse {
  return NextResponse.json(
    { detail },
    { status, headers: { "cache-control": "no-store" } },
  );
}

function requestHasSameOrigin(request: NextRequest): boolean {
  const origin = request.headers.get("origin");
  const host = request.headers.get("host");
  if (!origin || !host) return false;

  try {
    const originUrl = new URL(origin);
    const forwardedProtocol = request.headers
      .get("x-forwarded-proto")
      ?.split(",", 1)[0]
      .trim();
    const protocol = forwardedProtocol || request.nextUrl.protocol.replace(/:$/, "");
    return originUrl.host === host && originUrl.protocol === `${protocol}:`;
  } catch {
    return false;
  }
}

async function proxy(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const config = authConfig();
  const baseUrl = backendBaseUrl(config.backendUrl);
  if (!browserAuthConfigIsValid(config) || !baseUrl) {
    return errorResponse(503, "Dashboard proxy is not configured");
  }

  const authenticated = await browserAuthorizationIsValid(
    request.headers.get("authorization"),
    config,
  );
  if (!authenticated) {
    return errorResponse(401, "Administrator authentication is required");
  }

  if (MUTATING_METHODS.has(request.method)) {
    if (!requestHasSameOrigin(request)) {
      return errorResponse(403, "Cross-origin dashboard mutations are forbidden");
    }
  }

  const { path } = await context.params;
  if (path.length < 2 || path[0] !== "api" || path.some((part) => !SAFE_SEGMENT.test(part))) {
    return errorResponse(404, "Unsupported backend route");
  }

  const contentLength = Number(request.headers.get("content-length") ?? "0");
  if (!Number.isFinite(contentLength) || contentLength > MAX_REQUEST_BYTES) {
    return errorResponse(413, "Dashboard request is too large");
  }

  let body: ArrayBuffer | undefined;
  if (MUTATING_METHODS.has(request.method)) {
    if (!request.headers.get("content-type")?.startsWith("application/json")) {
      return errorResponse(415, "Dashboard mutations require JSON");
    }
    body = await request.arrayBuffer();
    if (body.byteLength > MAX_REQUEST_BYTES) {
      return errorResponse(413, "Dashboard request is too large");
    }
  }

  const upstream = new URL(baseUrl);
  const prefix = upstream.pathname.replace(/\/$/, "");
  upstream.pathname = `${prefix}/${path.map(encodeURIComponent).join("/")}`;
  upstream.search = request.nextUrl.search;

  const headers = new Headers({
    accept: request.headers.get("accept") ?? "application/json",
  });
  headers.set("authorization", `Bearer ${config.backendToken}`);
  if (body) headers.set("content-type", "application/json");

  try {
    const response = await fetch(upstream, {
      method: request.method,
      headers,
      body,
      cache: "no-store",
      redirect: "manual",
    });
    const responseHeaders = new Headers({ "cache-control": "no-store" });
    const contentType = response.headers.get("content-type");
    if (contentType) responseHeaders.set("content-type", contentType);

    return new NextResponse(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch {
    return errorResponse(502, "Dashboard backend is unavailable");
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
