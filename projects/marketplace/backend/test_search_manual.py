#!/usr/bin/env python3
"""Manual test for product search functionality"""

import sqlite3
import sys

def test_search():
    """Test search functionality directly in database"""
    db_path = "marketplace.db"

    print("=" * 70)
    print("MANUAL PRODUCT SEARCH TEST")
    print("=" * 70)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Test 1: Search for "SaaS"
    print("\n✅ Test 1: Search for 'SaaS'")
    search_term = "%SaaS%"
    cursor.execute(
        "SELECT id, title, description FROM products WHERE status = 'active' AND (title LIKE ? OR description LIKE ?)",
        (search_term, search_term)
    )
    results = cursor.fetchall()
    print(f"   Found {len(results)} result(s)")
    for row in results:
        print(f"   - {row['title']}")
    if len(results) > 0:
        print("   ✅ PASS: Search returns results")
    else:
        print("   ❌ FAIL: No results found")

    # Test 2: Search for "API"
    print("\n✅ Test 2: Search for 'API'")
    search_term = "%API%"
    cursor.execute(
        "SELECT id, title, description FROM products WHERE status = 'active' AND (title LIKE ? OR description LIKE ?)",
        (search_term, search_term)
    )
    results = cursor.fetchall()
    print(f"   Found {len(results)} result(s)")
    for row in results[:3]:
        print(f"   - {row['title']}")
    if len(results) > 0:
        print("   ✅ PASS: Search returns results")
    else:
        print("   ❌ FAIL: No results found")

    # Test 3: Search for non-existent term
    print("\n✅ Test 3: Search for 'xyzxyz123' (should return 0)")
    search_term = "%xyzxyz123%"
    cursor.execute(
        "SELECT id, title FROM products WHERE status = 'active' AND (title LIKE ? OR description LIKE ?)",
        (search_term, search_term)
    )
    results = cursor.fetchall()
    print(f"   Found {len(results)} result(s)")
    if len(results) == 0:
        print("   ✅ PASS: Correctly returns 0 results")
    else:
        print("   ❌ FAIL: Should return 0 results")

    # Test 4: Get all products (no search)
    print("\n✅ Test 4: Get all products (no search filter)")
    cursor.execute(
        "SELECT id, title FROM products WHERE status = 'active'"
    )
    results = cursor.fetchall()
    print(f"   Total products: {len(results)}")
    if len(results) > 0:
        print("   ✅ PASS: Returns all products")
    else:
        print("   ❌ FAIL: No products found")

    # Test 5: Search for "mobile"
    print("\n✅ Test 5: Search for 'mobile'")
    search_term = "%mobile%"
    cursor.execute(
        "SELECT id, title FROM products WHERE status = 'active' AND (title LIKE ? OR description LIKE ?)",
        (search_term, search_term)
    )
    results = cursor.fetchall()
    print(f"   Found {len(results)} result(s)")
    for row in results:
        print(f"   - {row['title']}")
    if len(results) > 0:
        print("   ✅ PASS: Search returns results")
    else:
        print("   ❌ FAIL: No results found")

    conn.close()

    print("\n" + "=" * 70)
    print("SEARCH FUNCTIONALITY TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    test_search()
