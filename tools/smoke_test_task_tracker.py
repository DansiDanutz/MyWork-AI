#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.request


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value or default


BASE_URL = _get_env("TASK_TRACKER_BASE_URL", "http://localhost:3000").rstrip("/")
TIMEOUT = float(_get_env("SMOKE_TIMEOUT", "15"))
RETRIES = int(_get_env("SMOKE_RETRIES", "3"))
RETRY_BACKOFF = float(_get_env("SMOKE_RETRY_BACKOFF", "1.5"))


def fetch(url: str, expect_json: bool = False):
    headers = {"User-Agent": "MyWork-SmokeTest/1.0"}
    last_exc: Exception | None = None

    for attempt in range(1, max(RETRIES, 1) + 1):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                status = response.getcode()
                raw = response.read()
                if status >= 500 and attempt < RETRIES:
                    time.sleep(RETRY_BACKOFF * attempt)
                    continue
                if expect_json:
                    try:
                        return status, json.loads(raw.decode("utf-8"))
                    except Exception as exc:  # pragma: no cover
                        raise AssertionError(f"Invalid JSON response from {url}") from exc
                return status, raw.decode("utf-8", errors="replace")
        except Exception as exc:  # pragma: no cover - network errors
            last_exc = exc
            if attempt >= RETRIES:
                raise
            time.sleep(RETRY_BACKOFF * attempt)

    if last_exc:  # pragma: no cover - defensive
        raise last_exc
    raise AssertionError(f"Unknown error fetching {url}")


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
        "app root",
        lambda: assert_ok("app root", f"{BASE_URL}/"),
    )

    run_check(
        "health endpoint",
        lambda: assert_ok("health endpoint", f"{BASE_URL}/api/health", expect_json=True),
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
