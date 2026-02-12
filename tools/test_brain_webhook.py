#!/usr/bin/env python3
"""
Test script to verify Brain webhook integration with Task Tracker.
This simulates the webhook payload that Task Tracker sends.
"""

import argparse
import json
import os
import sys
import urllib.request

DEFAULT_WEBHOOK_URL = "https://mywork-ai-production.up.railway.app/api/analytics/brain/ingest"


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes"}


def _resolve_webhook_url(cli_url: str | None) -> str:
    if cli_url:
        return cli_url.strip()
    return os.getenv("BRAIN_WEBHOOK_URL", DEFAULT_WEBHOOK_URL).strip()


# Simulate a Task Tracker analytics event
test_event = {
    "id": "test-event-123",
    "type": "task_created",
    "userId": "test-user-456",
    "properties": {"taskId": "task-789", "hasDescription": True, "source": "test-script"},
    "recordedAt": "2026-01-26T20:00:00Z",
    "source": "task-tracker",
}


def run_brain_webhook_test(webhook_url: str, allow_prod: bool) -> bool:
    """Test the Brain ingestion endpoint."""
    if webhook_url.startswith("https://mywork-ai-production.up.railway.app") and not allow_prod:
        print("Refusing to send test data to production by default.")
        print(
            "Set ALLOW_PROD_WEBHOOK_TEST=true to proceed, or set BRAIN_WEBHOOK_URL to a non-prod endpoint."
        )
        return False

    print(f"Testing Brain webhook: {webhook_url}")
    print(f"Event payload: {json.dumps(test_event, indent=2)}")

    try:
        data = json.dumps(test_event).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "MyWork-Brain-Test/1.0"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")

            print(f"\nResponse Status: {status}")
            print(f"Response Body: {body}")

            if status == 200:
                result = json.loads(body)
                print(f"\n[SUCCESS] Event received!")
                print(f"   Event ID: {result.get('event_id', 'N/A')}")
                print(f"   Processed at: {result.get('processed_at', 'N/A')}")
                return True
            else:
                print(f"\n[FAILED] Unexpected status code {status}")
                return False

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Brain webhook ingestion.")
    parser.add_argument(
        "--url", help="Override webhook URL (defaults to BRAIN_WEBHOOK_URL or production)."
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Allow sending test events to production.",
    )
    args = parser.parse_args()

    resolved_url = _resolve_webhook_url(args.url)
    allow_prod = args.prod or _env_bool("ALLOW_PROD_WEBHOOK_TEST")

    success = run_brain_webhook_test(resolved_url, allow_prod)
    exit(0 if success else 1)
