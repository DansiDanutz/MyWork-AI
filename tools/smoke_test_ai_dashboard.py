#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value or default


BACKEND_URL = _get_env(
    "AI_DASHBOARD_BACKEND_URL",
    "https://ai-dashboard-backend-production-c40e.up.railway.app",
).rstrip("/")
FRONTEND_URL = os.getenv("AI_DASHBOARD_FRONTEND_URL", "").strip().rstrip("/")
TIMEOUT = float(_get_env("SMOKE_TIMEOUT", "15"))


def fetch(url: str, expect_json: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": "MyWork-SmokeTest/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
        status = response.getcode()
        raw = response.read()
        if expect_json:
            try:
                return status, json.loads(raw.decode("utf-8"))
            except Exception as exc:  # pragma: no cover
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

    if FRONTEND_URL:
        run_check(
            "frontend root",
            lambda: assert_ok("frontend root", f"{FRONTEND_URL}/"),
        )
    else:
        print("[SKIP] frontend root (AI_DASHBOARD_FRONTEND_URL not set)")

    run_check(
        "backend root",
        lambda: assert_ok("backend root", f"{BACKEND_URL}/", expect_json=True),
    )

    run_check(
        "backend stats",
        lambda: assert_ok("backend stats", f"{BACKEND_URL}/api/stats", expect_json=True),
    )

    if failures:
        print("\nSmoke test failures:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("\nAll smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
