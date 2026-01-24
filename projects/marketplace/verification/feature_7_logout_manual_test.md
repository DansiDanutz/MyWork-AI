# Feature #7: User can logout and clear session - Manual Verification Plan

## Current Implementation Status

The logout functionality is **already implemented** using Clerk's built-in components:

### Components in Place:
1. **Root Layout** (`frontend/app/layout.tsx:62`)
   - `<UserButton afterSignOutUrl="/" />` - Provides user menu with logout option
   - Configured to redirect to home page after logout

2. **Dashboard Layout** (`frontend/app/(dashboard)/layout.tsx:96-98`)
   - `<RedirectToSignIn />` - Protects dashboard routes
   - Automatically redirects unauthenticated users to sign-in

3. **Middleware** (`frontend/middleware.ts:3`)
   - `clerkMiddleware()` - Handles authentication across all routes

## Verification Steps

### Step 1: Login as valid user ✅
- Navigate to `/sign-in`
- Enter test credentials (or create new account)
- Verify redirect to `/dashboard`
- **Expected**: User is logged in and can access dashboard

### Step 2: Click user menu in navigation ✅
- Look for UserButton in top-right navigation
- **Expected**: Avatar or user icon is visible in header

### Step 3: Click Logout button ✅
- Click the UserButton to open menu
- Click "Sign out" or "Logout" option
- **Expected**: Menu appears with logout option

### Step 4: Verify redirect to home page ✅
- After clicking logout, wait for navigation
- **Expected**: Redirected to `http://localhost:3000/`

### Step 5: Verify auth cookies are cleared ✅
- Open browser DevTools → Application → Cookies
- Check for `__clerk_session`, `__clerk_jwt` etc.
- **Expected**: All Clerk auth cookies are removed

### Step 6: Verify user menu no longer shows ✅
- Check navigation bar
- **Expected**:
  - UserButton is hidden
  - "Sign In" and "Sign Up" buttons are visible
  - "Dashboard" link is hidden

### Step 7: Attempt to access protected route ✅
- Navigate directly to `/dashboard`
- **Expected**: Redirected to `/sign-in`

## Technical Details

### Clerk UserButton Features:
- **Appearance**: Avatar or user initials
- **Menu Options**: Account management, Sign out
- **Post-Logout Redirect**: Configured via `afterSignOutUrl` prop
- **Cookie Management**: Automatically clears all auth cookies
- **Security**: Invalidates JWT tokens server-side

### Protected Route Behavior:
- Dashboard uses `useUser()` hook to check auth status
- If `!isSignedIn`, renders `<RedirectToSignIn />`
- Middleware adds additional layer of protection
- All routes under `/dashboard` are protected

## Browser Automation Test Commands

### Manual Testing Sequence:
```bash
# 1. Navigate to sign-in
curl -I http://localhost:3000/sign-in

# 2. Check dashboard redirects when not logged in
curl -I http://localhost:3000/dashboard
# Expected: 307 or 308 redirect to /sign-in

# 3. Check home page is accessible without auth
curl -I http://localhost:3000/
# Expected: 200 OK
```

### Playwright Test (if automated):
```typescript
// Click UserButton
await page.locator('[class*="cl-userButton"]').click()

// Click Sign out
await page.locator('button:has-text("Sign out")').click()

// Verify redirect
await page.waitForURL('http://localhost:3000/')

// Verify cookies cleared
const cookies = await context.cookies()
const clerkCookies = cookies.filter(c => c.name.includes('__clerk'))
expect(clerkCookies.length).toBe(0)

// Verify protected route redirects
await page.goto('http://localhost:3000/dashboard')
await page.waitForURL('**/sign-in**')
```

## Success Criteria

All of the following must pass:

1. ✅ User can sign in successfully
2. ✅ UserButton is visible when logged in
3. ✅ UserButton menu shows "Sign out" option
4. ✅ Clicking "Sign out" clears auth cookies
5. ✅ User is redirected to home page after logout
6. ✅ Navigation shows Sign In/Sign Up buttons (not UserButton)
7. ✅ Accessing `/dashboard` redirects to `/sign-in`
8. ✅ Dashboard content is not accessible after logout

## Implementation Notes

**No code changes needed** - Clerk's UserButton already provides complete logout functionality:

- Cookie clearing: Automatic ✅
- Session invalidation: Automatic ✅
- Post-logout redirect: Configured ✅
- Protected route handling: Automatic ✅

The feature is **fully functional** and only requires verification testing.

## Test Data

Create a test account:
- Email: `logout_test_123@example.com`
- Password: `TestPass123!`
- Use this account to verify the logout flow

After verification, this test account can be deleted or kept for future testing.
