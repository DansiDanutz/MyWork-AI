#!/usr/bin/env python3
"""Automated backend QA checks for the Marketplace API."""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Iterable

import requests

BACKEND_URL = os.getenv(
    "MARKETPLACE_BACKEND_URL",
    "https://mywork-ai-production.up.railway.app",
).rstrip("/")
TIMEOUT = float(os.getenv("QA_TIMEOUT", "20"))
RETRIES = int(os.getenv("QA_RETRIES", "3"))
RETRY_BACKOFF = float(os.getenv("QA_RETRY_BACKOFF", "1.5"))
HEADERS = {
    "User-Agent": "MyWork-QA/1.0",
}

Check = tuple[str, str, bool, dict[str, Any] | None]
CHECKS: Iterable[Check] = (
    ("backend root", "/", False, None),
    ("health endpoint", "/health", True, {"status": "healthy"}),
    ("products API", "/api/products", True, None),
)


def _request_with_retries(url: str) -> requests.Response:
    last_exc: Exception | None = None
    for attempt in range(1, max(RETRIES, 1) + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        except Exception as exc:  # pragma: no cover - network errors
            last_exc = exc
            if attempt >= RETRIES:
                raise
            time.sleep(RETRY_BACKOFF * attempt)
            continue

        if response.status_code >= 500 and attempt < RETRIES:
            time.sleep(RETRY_BACKOFF * attempt)
            continue

        return response

    if last_exc:  # pragma: no cover - defensive
        raise last_exc
    raise RuntimeError(f"Unknown error requesting {url}")


def run_check(
    label: str, path: str, expect_json: bool, expected_subset: dict[str, Any] | None
) -> str | None:
    url = f"{BACKEND_URL}{path}"
    try:
        response = _request_with_retries(url)
    except Exception as exc:  # pragma: no cover - network errors
        return f"{label}: request to {url} failed ({exc})"

    if response.status_code >= 400:
        return f"{label}: HTTP {response.status_code} for {url}"

    if not expect_json:
        return None

    try:
        data = response.json()
    except json.JSONDecodeError:
        return f"{label}: expected JSON response from {url}"

    if expected_subset:
        for key, value in expected_subset.items():
            if data.get(key) != value:
                return f"{label}: expected {key}={value!r}, got {data.get(key)!r}"

    return None


def main() -> int:
    failures: list[str] = []
    print(f"Running backend QA checks against {BACKEND_URL}\n")

    for label, path, expect_json, expected_subset in CHECKS:
        error = run_check(label, path, expect_json, expected_subset)
        if error:
            failures.append(error)
            print(f"[FAIL] {error}")
        else:
            print(f"[OK] {label}")

    if failures:
        print("\nBackend QA failures detected:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nAll backend QA checks passed.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
