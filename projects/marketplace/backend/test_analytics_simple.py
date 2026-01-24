#!/usr/bin/env python3
"""Simple test for analytics API using urllib."""

import urllib.request
import json

try:
    # Test analytics endpoint
    url = "http://localhost:8000/api/analytics?days=30"
    print(f"Testing: {url}")

    with urllib.request.urlopen(url, timeout=5) as response:
        data = json.loads(response.read().decode())
        print(f"✅ Status: {response.status}")
        print(f"✅ Response keys: {list(data.keys())}")

        if 'stats' in data:
            stats = data['stats']
            print(f"\n📊 Analytics Stats:")
            print(f"  Total Revenue: ${stats.get('totalRevenue', 0):.2f}")
            print(f"  Total Sales: {stats.get('totalSales', 0)}")
            print(f"  Conversion Rate: {stats.get('conversionRate', 0):.2f}%")

        if 'topProducts' in data:
            products = data['topProducts']
            print(f"\n🏆 Top Products: {len(products)} items")

        if 'chartData' in data:
            chart = data['chartData']
            print(f"\n📈 Chart Data Points: {len(chart)}")

        print("\n✅ Analytics API is working!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nNote: Make sure backend is running on port 8000")
