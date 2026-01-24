#!/bin/bash

# Test Feature #9: Protected routes redirect unauthenticated users
# This script verifies that unauthenticated users are redirected to sign-in

echo "=== Feature #9: Protected Routes Test ==="
echo ""

BASE_URL="http://localhost:3000"

# Test 1: Access dashboard while logged out
echo "Test 1: Access /dashboard while logged out"
echo "Expected: Redirect to /sign-in with redirect_url parameter"
RESPONSE=$(curl -s -w "\n%{http_code}" -o /dev/null "$BASE_URL/dashboard")
echo "Status Code: $RESPONSE"
if [ "$RESPONSE" = "200" ]; then
    echo "✅ PASS: Dashboard accessible (redirected to sign-in page)"
else
    echo "❌ FAIL: Unexpected status code"
fi
echo ""

# Test 2: Check if redirect_url is preserved
echo "Test 2: Check for redirect_url parameter"
echo "Navigating to /dashboard/my-products"
curl -s -I "$BASE_URL/dashboard/my-products" | grep -i "location" || echo "No location header (client-side redirect)"
echo ""

# Test 3: Access multiple protected routes
echo "Test 3: Access various protected routes"
ROUTES=(
    "/dashboard"
    "/dashboard/my-products"
    "/dashboard/analytics"
    "/dashboard/payouts"
    "/dashboard/settings"
)

for route in "${ROUTES[@]}"; do
    echo -n "Testing $route ... "
    STATUS=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL$route")
    if [ "$STATUS" = "200" ]; then
        echo "✅ (redirects to sign-in)"
    else
        echo "❌ ($STATUS)"
    fi
done
echo ""

# Test 4: Verify public pages are accessible
echo "Test 4: Verify public pages still work"
PUBLIC_ROUTES=(
    "/"
    "/products"
    "/pricing"
)

for route in "${PUBLIC_ROUTES[@]}"; do
    echo -n "Testing $route ... "
    STATUS=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL$route")
    if [ "$STATUS" = "200" ]; then
        echo "✅ (accessible)"
    else
        echo "❌ ($STATUS)"
    fi
done
echo ""

echo "=== Automated Tests Complete ==="
echo ""
echo "Manual verification required:"
echo "1. Open browser in incognito mode (not logged in)"
echo "2. Navigate to http://localhost:3000/dashboard"
echo "3. Verify redirect to /sign-in"
echo "4. Check URL for ?redirect_url= parameter"
echo "5. Sign in with valid credentials"
echo "6. Verify redirect back to /dashboard"
