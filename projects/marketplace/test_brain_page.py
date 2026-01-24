#!/usr/bin/env python3
"""Test script to verify Brain Contributions page functionality."""

import requests
import json

API_URL = "http://localhost:8000/api/brain"

def test_brain_api():
    """Test brain API endpoints."""
    print("Testing Brain API...")

    # 1. Test stats endpoint
    print("\n1. Testing stats endpoint...")
    response = requests.get(f"{API_URL}/stats/overview")
    assert response.status_code == 200
    stats = response.json()
    print(f"   ✓ Stats: {stats['total_entries']} entries, {stats['verified_entries']} verified")

    # 2. Test search endpoint
    print("\n2. Testing search endpoint...")
    response = requests.get(API_URL)
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ Found {data['total']} entries")
    for entry in data['entries'][:2]:
        print(f"     - {entry['title']} ({entry['type']})")

    # 3. Test create entry
    print("\n3. Testing create entry...")
    unique_id = "TEST_BRAIN_VERIFY_999"
    test_entry = {
        "title": f"{unique_id}: Automated Test Entry",
        "content": "This is an automated test entry to verify brain functionality.",
        "type": "pattern",
        "category": "Testing",
        "tags": ["test", "automation"],
        "language": "Python",
        "framework": "pytest",
        "isPublic": True
    }

    response = requests.post(API_URL, json=test_entry)
    assert response.status_code == 201
    created = response.json()
    print(f"   ✓ Created entry: {created['id']}")

    # 4. Verify entry appears in search
    print("\n4. Verifying entry in search...")
    response = requests.get(API_URL, params={"q": unique_id})
    assert response.status_code == 200
    data = response.json()
    assert any(unique_id in e['title'] for e in data['entries'])
    print(f"   ✓ Entry found in search results")

    # 5. Test voting
    print("\n5. Testing vote functionality...")
    entry_id = created['id']
    response = requests.post(f"{API_URL}/{entry_id}/vote", json={"vote": 1})
    assert response.status_code == 200
    updated = response.json()
    assert updated['helpful_votes'] == 1
    print(f"   ✓ Vote recorded: {updated['helpful_votes']} upvotes")

    # 6. Test getting single entry
    print("\n6. Testing get single entry...")
    response = requests.get(f"{API_URL}/{entry_id}")
    assert response.status_code == 200
    entry = response.json()
    assert entry['id'] == entry_id
    print(f"   ✓ Retrieved entry: {entry['title']}")

    print("\n✅ All brain API tests passed!")
    return entry_id

if __name__ == "__main__":
    test_brain_api()
