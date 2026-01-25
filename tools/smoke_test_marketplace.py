#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urljoin


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value or default


FRONTEND_URL = _get_env(
    "MARKETPLACE_FRONTEND_URL",
    "https://frontend-hazel-ten-17.vercel.app",
).rstrip("/")
BACKEND_URL = _get_env(
    "MARKETPLACE_BACKEND_URL",
    "https://mywork-ai-production.up.railway.app",
).rstrip("/")
TIMEOUT = float(_get_env("SMOKE_TIMEOUT", "15"))
VERCEL_BYPASS = os.getenv("VERCEL_AUTOMATION_BYPASS_SECRET", "").strip()


def fetch(url: str, expect_json: bool = False):
    headers = {"User-Agent": "MyWork-SmokeTest/1.0"}
    if VERCEL_BYPASS:
        headers["x-vercel-protection-bypass"] = VERCEL_BYPASS
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
        status = response.getcode()
        raw = response.read()
        if expect_json:
            try:
                return status, json.loads(raw.decode("utf-8"))
            except Exception as exc:  # pragma: no cover - diagnostics
                raise AssertionError(f"Invalid JSON response from {url}") from exc
        return status, raw.decode("utf-8", errors="replace")


def assert_ok(label: str, url: str, expect_json: bool = False):
    status, data = fetch(url, expect_json=expect_json)
    if status < 200 or status >= 300:
        raise AssertionError(f"{label} returned HTTP {status}: {url}")
    return data


def main() -> int:
    failures = []

    def run_check(label: str, fn):
        try:
            fn()
            print(f"[OK] {label}")
        except Exception as exc:
            failures.append(f"{label}: {exc}")
            print(f"[FAIL] {label}: {exc}")

    run_check(
        "frontend root",
        lambda: assert_ok("frontend root", f"{FRONTEND_URL}/"),
    )
    run_check(
        "backend root",
        lambda: assert_ok("backend root", f"{BACKEND_URL}/", expect_json=True),
    )

    def check_health():
        data = assert_ok("backend health", f"{BACKEND_URL}/health", expect_json=True)
        if data.get("status") != "healthy":
            raise AssertionError(f"health status is {data.get('status')!r}")

    run_check("backend health", check_health)

    def check_products():
        data = assert_ok(
            "backend products",
            urljoin(f"{BACKEND_URL}/", "api/products"),
            expect_json=True,
        )
        if not isinstance(data, dict):
            raise AssertionError("products response is not an object")

    run_check("backend products", check_products)

    if failures:
        print("\nSmoke test failures:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("\nAll smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
