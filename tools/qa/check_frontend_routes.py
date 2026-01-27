#!/usr/bin/env python3
"""Automated frontend QA checks for the Marketplace UI."""

from __future__ import annotations

import os
import sys
from typing import Iterable

import requests

FRONTEND_URL = os.getenv(
    "MARKETPLACE_FRONTEND_URL",
    "https://frontend-hazel-ten-17.vercel.app",
).rstrip("/")
TIMEOUT = float(os.getenv("QA_TIMEOUT", "20"))
BYPASS = os.getenv("VERCEL_AUTOMATION_BYPASS_SECRET", "")

session = requests.Session()
headers = {"User-Agent": "MyWork-QA/1.0"}
if BYPASS:
    headers["x-vercel-protection-bypass"] = BYPASS
    headers["Cookie"] = f"__Secure-next-auth.session-token={BYPASS}"
session.headers.update(headers)

Route = tuple[str, str]
ROUTES: Iterable[Route] = (
    ("/", "Home page"),
    ("/pricing", "Pricing page"),
    ("/products", "Products catalog"),
    ("/status", "Status page"),
)


def check_route(path: str, label: str) -> str | None:
    url = f"{FRONTEND_URL}{path}"
    try:
        resp = session.get(url, timeout=TIMEOUT, allow_redirects=True)
    except Exception as exc:  # pragma: no cover - network errors
        return f"{label}: request to {url} failed ({exc})"

    if resp.status_code >= 400:
        return f"{label}: HTTP {resp.status_code} for {url}"

    if not resp.text.strip():
        return f"{label}: empty response body from {url}"

    return None


def main() -> int:
    failures: list[str] = []
    print(f"Running frontend QA checks against {FRONTEND_URL}\n")

    for path, label in ROUTES:
        error = check_route(path, label)
        if error:
            failures.append(error)
            print(f"[FAIL] {error}")
        else:
            print(f"[OK] {label}")

    if failures:
        print("\nFrontend QA failures detected:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nAll frontend QA checks passed.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
