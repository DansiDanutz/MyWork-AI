#!/usr/bin/env python3
"""Test analytics API endpoint."""

import requests

try:
    response = requests.get("http://localhost:8000/api/analytics?days=30")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:1000]}")
except Exception as e:
    print(f"Error: {e}")
