# Purchases Page - Test Plan & Verification

## Feature: User can view purchase history and download purchased products

### Implementation Summary

Created `/dashboard/purchases` page that displays user's order history with:
- Order cards showing product name, date, order number, license type
- Price and payment status badges
- Download buttons for completed orders
- Empty state with link to browse products
- Loading and error states

### Files Created

- `frontend/app/(dashboard)/purchases/page.tsx` (247 lines)
  - Fetches orders from `/api/orders?role=buyer`
  - Displays orders in card format
  - Handles download action via `/api/orders/{id}/download`
  - Shows empty state, loading, and error states

### Technical Details

**API Integration:**
- GET `/api/orders?role=buyer` - List buyer's orders
- POST `/api/orders/{id}/download` - Get download link for purchased product

**State Management:**
- `orders` - List of user's purchases
- `loading` - Loading state during API calls
- `error` - Error message if fetch fails

**Features:**
- Format dates using `toLocaleDateString`
- Format prices using `Intl.NumberFormat`
- Status badges: Completed (green), Pending (yellow), Failed (red)
- Download count tracking
- Order number display (e.g., "MW-2025-12345")

---

## Test Cases

### 1. Page Loads Successfully
**Steps:**
1. Navigate to http://localhost:3000/dashboard/purchases
2. Verify page loads without errors
3. Check browser console for JavaScript errors

**Expected Result:**
- Page loads successfully
- No console errors
- "My Purchases" heading visible
- ShoppingBag icon visible

---

### 2. Empty State Displayed (No Orders)
**Steps:**
1. Access page as new user with no purchases
2. Verify empty state UI

**Expected Result:**
- Package icon displayed
- "No purchases yet" message shown
- "Browse Products" button links to `/products`
- Background card style matches dark theme

---

### 3. Orders List Displayed
**Steps:**
1. Create test order in database
2. Refresh page
3. Verify order card displays correctly

**Expected Result:**
- Order card shows:
  - Product name (e.g., "Test Product")
  - Order date formatted (e.g., "Jan 25, 2025")
  - License type (e.g., "STANDARD License")
  - Order number (e.g., "MW-2025-12345")
  - Price formatted (e.g., "$49.00")
  - Status badge (Completed/Pending/Failed)
  - Download button (if completed)

---

### 4. Download Button Works
**Steps:**
1. Find completed order with download_url
2. Click "Download" button
3. Verify API call to `/api/orders/{id}/download`
4. Verify download count increases

**Expected Result:**
- API POST request made to download endpoint
- Download URL opens in new tab
- Order list refreshes
- Download count increments

---

### 5. Status Badges Display Correctly
**Test Different Payment Statuses:**

| Payment Status | Badge Color | Badge Text |
|----------------|-------------|------------|
| completed | Green | "Completed" |
| pending | Yellow | "Pending" |
| failed | Red | "Failed" |

**Steps:**
1. Create orders with different payment statuses
2. Verify badge colors and text match

---

### 6. Responsive Design
**Test on Different Screen Sizes:**

**Desktop (1024px+):**
- Order cards display in full width
- Product info and actions on same row
- All buttons visible

**Tablet (768px-1023px):**
- Cards stack appropriately
- Buttons remain accessible

**Mobile (<768px):**
- Order cards stack vertically
- Download button full width on mobile
- Text remains readable

---

### 7. Loading State
**Steps:**
1. Open browser Network tab
2. Throttle network to "Slow 3G"
3. Navigate to /dashboard/purchases
4. Observe loading spinner

**Expected Result:**
- Blue spinner displayed centered
- Spinner animation smooth
- Loading state clears when data arrives

---

### 8. Error Handling
**Steps:**
1. Stop backend server
2. Navigate to /dashboard/purchases
3. Verify error state displayed
4. Click "Retry" button
5. Restart backend server
6. Click "Retry" again

**Expected Result:**
- Error message shown: "Failed to load orders"
- "Retry" button visible and functional
- Page recovers when backend available

---

### 9. Date Formatting
**Test:**
- Order created on "2025-01-25T10:30:00Z"
- Display shows "Jan 25, 2025"

**Verify:**
- Date formatted in US locale
- Month abbreviation (Jan, Feb, etc.)
- Day and year displayed

---

### 10. Price Formatting
**Test Cases:**

| Amount | Display |
|--------|---------|
| 49.00 | "$49.00" |
| 99.99 | "$99.99" |
| 1000 | "$1,000.00" |

**Verify:**
- Currency symbol ($)
- Two decimal places
- Thousands separator

---

### 11. License Type Display
**Test Cases:**

| License Type | Display |
|--------------|---------|
| standard | "STANDARD License" |
| extended | "EXTENDED License" |
| unlimited | "UNLIMITED License" |

**Verify:**
- License type converted to uppercase
- "License" suffix added

---

### 12. Navigation Integration
**Steps:**
1. Click "Purchases" in sidebar
2. Verify active state styling

**Expected Result:**
- Purchases link highlighted
- Icon: ShoppingBag
- Background darker (active state)

---

### 13. Download Count Display
**Steps:**
1. Create completed order with download_count=2
2. View order details
3. Verify "Downloads used: 2" shown

**Expected Result:**
- Download count displayed in gray text
- Located below order card divider
- Updates after download

---

### 14. Order Number Format
**Test:**
- Verify order number format: "MW-YYYY-#####"
- Example: "MW-2025-12345"

**Verify:**
- "MW-" prefix
- 4-digit year
- 5-digit random number
- Monospace font for readability

---

## Manual Testing Checklist

### Visual Verification
- [ ] Dark theme styling matches other pages
- [ ] Cards have proper spacing (4 units gap)
- [ ] Icons sized correctly (w-4 h-4 for small, w-6 h-6 for medium)
- [ ] Fonts hierarchy clear (product name larger, metadata smaller)

### Interaction Verification
- [ ] Download button hover state (bg-blue-700)
- [ ] Browse Products button hover state
- [ ] Retry button hover state
- [ ] No button clicks cause errors

### Responsive Verification
- [ ] Test on 1920x1080 (desktop)
- [ ] Test on 768x1024 (tablet)
- [ ] Test on 375x667 (mobile)
- [ ] No horizontal scrolling
- [ ] No text overflow

### Accessibility Verification
- [ ] Keyboard navigation works (Tab through buttons)
- [ ] Screen reader announces order details
- [ ] Focus indicators visible
- [ ] Color contrast sufficient (WCAG AA)

---

## API Integration Tests

### Backend API Verification

**1. GET /api/orders?role=buyer**
```bash
curl http://localhost:8000/api/orders?role=buyer
```

**Expected Response:**
```json
{
  "orders": [
    {
      "id": "...",
      "order_number": "MW-2025-12345",
      "product_id": "...",
      "product_name": "Test Product",
      "amount": 49.00,
      "license_type": "standard",
      "status": "completed",
      "payment_status": "completed",
      "download_url": "https://...",
      "download_count": 0,
      "created_at": "2025-01-25T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

**2. POST /api/orders/{id}/download**
```bash
curl -X POST http://localhost:8000/api/orders/{order_id}/download
```

**Expected Response:**
```json
{
  "download_url": "https://files.mywork.dev/...",
  "downloads_remaining": 4
}
```

---

## Browser Automation Tests

### Test with Playwright (if available)

```typescript
test("displays purchases list", async ({ page }) => {
  await page.goto("/dashboard/purchases")
  await expect(page.locator("h1")).toContainText("My Purchases")
})

test("empty state shows browse link", async ({ page }) => {
  await page.goto("/dashboard/purchases")
  await expect(page.locator("text=Browse Products")).toBeVisible()
})

test("download button triggers download", async ({ page }) => {
  await page.goto("/dashboard/purchases")
  await page.click("button:has-text('Download')")
  // Verify new tab opened
})
```

---

## Edge Cases

### 1. Very Long Product Names
- Product name: "This is an extremely long product name that should be truncated"
- Expected: Truncated with ellipsis

### 2. Zero Price Orders
- Amount: 0.00
- Expected: "$0.00" displayed

### 3. Multiple Pages of Orders
- Total: 45 orders, page_size: 20
- Expected: Show first 20, pagination controls (future enhancement)

### 4. Download Limit Reached
- download_count: 5, max_downloads: 5
- Expected: Hide download button or disable with message

### 5. Very Old Orders
- Order from 2020-01-01
- Expected: Date formatted correctly

---

## Performance Tests

### 1. Large Order List
- 100 orders
- Target: Page loads in < 2 seconds

### 2. Slow Network
- Throttle to "Fast 3G"
- Target: Loading spinner appears smoothly

### 3. API Latency
- Backend response time: 500ms
- Target: Spinner displays, no UI lag

---

## Security Tests

### 1. Cannot Access Other Users' Orders
- User A tries to access User B's orders
- Expected: API returns only User A's orders

### 2. Download Button Protected
- Unauthenticated user cannot download
- Expected: API returns 401 Unauthorized

### 3. Download Count Limits
- Try to download 6 times with limit of 5
- Expected: API returns error after limit

---

## Success Criteria

✅ Page loads without errors
✅ Displays empty state when no orders
✅ Displays order list with all required fields
✅ Download button works for completed orders
✅ Status badges display correctly
✅ Responsive design on mobile/tablet/desktop
✅ Loading and error states handle gracefully
✅ Dates and prices formatted correctly
✅ Navigation integration working
✅ No TypeScript errors
✅ No console errors during normal operation

---

## Notes

- Future enhancements: pagination, filtering by status, sorting by date/price
- Download tracking will be more useful once file upload is implemented
- Order numbers are generated automatically in backend
- Escrow release dates not shown in this view (will be in seller's view)

---

**Test Status:** ⏳ Pending manual verification
**Build Status:** ✅ TypeScript compilation successful
**API Endpoints:** ✅ Backend endpoints implemented
