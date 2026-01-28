#!/usr/bin/env python3
"""
Test script to verify Brain webhook integration with Task Tracker.
This simulates the webhook payload that Task Tracker sends.
"""

import json
import os
import sys
import urllib.request

DEFAULT_WEBHOOK_URL = "https://mywork-ai-production.up.railway.app/api/analytics/brain/ingest"
WEBHOOK_URL = os.getenv("BRAIN_WEBHOOK_URL", DEFAULT_WEBHOOK_URL).strip()
ALLOW_PROD = os.getenv("ALLOW_PROD_WEBHOOK_TEST", "").strip().lower() in {"1", "true", "yes"}

# Simulate a Task Tracker analytics event
test_event = {
    "id": "test-event-123",
    "type": "task_created",
    "userId": "test-user-456",
    "properties": {"taskId": "task-789", "hasDescription": True, "source": "test-script"},
    "recordedAt": "2026-01-26T20:00:00Z",
    "source": "task-tracker",
}


def test_brain_webhook():
    """Test the Brain ingestion endpoint."""
    if WEBHOOK_URL.startswith("https://mywork-ai-production.up.railway.app") and not ALLOW_PROD:
        print("Refusing to send test data to production by default.")
        print(
            "Set ALLOW_PROD_WEBHOOK_TEST=true to proceed, or set BRAIN_WEBHOOK_URL to a non-prod endpoint."
        )
        return False

    print(f"Testing Brain webhook: {WEBHOOK_URL}")
    print(f"Event payload: {json.dumps(test_event, indent=2)}")

    try:
        data = json.dumps(test_event).encode("utf-8")
        req = urllib.request.Request(
            WEBHOOK_URL,
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
    success = test_brain_webhook()
    exit(0 if success else 1)
