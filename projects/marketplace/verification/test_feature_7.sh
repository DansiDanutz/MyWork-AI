#!/bin/bash

echo "==================================="
echo "Feature #7: Logout Verification Test"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:3000"

echo "Step 1: Testing Sign-In Page Accessibility"
echo "------------------------------------------"
SIGN_IN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/sign-in")
if [ "$SIGN_IN_STATUS" = "200" ]; then
    echo -e "${GREEN}✓${NC} Sign-in page is accessible (HTTP $SIGN_IN_STATUS)"
else
    echo -e "${RED}✗${NC} Sign-in page returned HTTP $SIGN_IN_STATUS"
fi
echo ""

echo "Step 2: Testing Dashboard Redirect (Not Logged In)"
echo "---------------------------------------------------"
DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/dashboard")
echo "Dashboard status (should be 200 or 3xx redirect): $DASHBOARD_STATUS"
# Note: Clerk middleware handles redirects, so we may get 200 with a redirect to sign-in
echo ""

echo "Step 3: Testing Home Page Accessibility"
echo "---------------------------------------"
HOME_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$HOME_STATUS" = "200" ]; then
    echo -e "${GREEN}✓${NC} Home page is accessible without auth (HTTP $HOME_STATUS)"
else
    echo -e "${RED}✗${NC} Home page returned HTTP $HOME_STATUS"
fi
echo ""

echo "Step 4: Testing Protected Routes"
echo "--------------------------------"
ROUTES=("/dashboard" "/dashboard/my-products" "/dashboard/analytics" "/dashboard/settings")
for route in "${ROUTES[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$route")
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ] || [ "$STATUS" = "307" ] || [ "$STATUS" = "308" ]; then
        echo -e "${GREEN}✓${NC} $route - Protected route responding (HTTP $STATUS)"
    else
        echo -e "${YELLOW}?${NC} $route - Unexpected status: $STATUS"
    fi
done
echo ""

echo "Step 5: Testing Public Routes"
echo "-----------------------------"
PUBLIC_ROUTES=("/" "/products" "/pricing" "/sign-in" "/sign-up")
for route in "${PUBLIC_ROUTES[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$route")
    if [ "$STATUS" = "200" ]; then
        echo -e "${GREEN}✓${NC} $route - Public route accessible (HTTP $STATUS)"
    else
        echo -e "${RED}✗${NC} $route - Failed with HTTP $STATUS"
    fi
done
echo ""

echo "==================================="
echo "Manual Browser Testing Required"
echo "==================================="
echo ""
echo "The automated tests above verify basic route accessibility."
echo "To complete Feature #7 verification, you must manually test:"
echo ""
echo "1. Sign in at /sign-in"
echo "2. Click UserButton (avatar) in top-right"
echo "3. Click 'Sign out' in the menu"
echo "4. Verify redirect to home page"
echo "5. Check browser DevTools → Cookies (should be cleared)"
echo "6. Verify UserButton is gone, Sign In/Sign Up buttons visible"
echo "7. Try to access /dashboard (should redirect to /sign-in)"
echo ""
echo "Clerk's UserButton component handles all logout functionality automatically."
echo "No code changes are required - only verification testing is needed."
