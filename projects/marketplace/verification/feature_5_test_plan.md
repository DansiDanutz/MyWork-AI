# Feature #5: User Login Test Plan

## Feature Description
Registered users can login with email/password and receive proper session tokens

## Test Environment
- Frontend: http://localhost:3001
- Backend: http://localhost:8000
- Auth Provider: Clerk (test keys configured)

## Pre-conditions
- Clerk is configured and running
- Backend database is empty (no existing users)
- Sign-in and sign-up pages exist

## Test Steps

### Step 1: Navigate to /sign-in
- [ ] Open browser to http://localhost:3001/sign-in
- [ ] Verify page loads without errors
- [ ] Check for Clerk sign-in form
- [ ] Verify styling (dark theme)

### Step 2: Create Test User (via Sign Up)
- [ ] Navigate to http://localhost:3001/sign-up
- [ ] Enter test email: test-login-feature@example.com
- [ ] Enter test password: TestPass123!
- [ ] Complete registration flow
- [ ] Verify redirect to /dashboard after sign-up

### Step 3: Sign Out
- [ ] Click user menu in navigation
- [ ] Click sign out
- [ ] Verify redirect to home page

### Step 4: Login with Valid Credentials
- [ ] Navigate to http://localhost:3001/sign-in
- [ ] Enter email: test-login-feature@example.com
- [ ] Enter password: TestPass123!
- [ ] Click "Sign In" button
- [ ] Wait for authentication to complete

### Step 5: Verify Redirect to Dashboard
- [ ] Check that URL changes to /dashboard
- [ ] Verify dashboard page loads
- [ ] Check for no console errors

### Step 6: Check Auth Token Storage
- [ ] Open browser DevTools
- [ ] Check Application > Cookies
- [ ] Verify __session cookie exists (httpOnly)
- [ ] Check for other Clerk session cookies

### Step 7: Verify User Menu in Navigation
- [ ] Check that "Sign In" and "Sign Up" buttons are gone
- [ ] Verify UserButton avatar appears in navigation
- [ ] Verify "Dashboard" link appears
- [ ] Verify notification icon is present

### Step 8: Verify Backend User Creation
- [ ] Check database for user record
- [ ] Verify clerk_id is stored
- [ ] Verify email matches test email

## Success Criteria
✅ User can sign up and create account
✅ User can sign in with valid credentials
✅ Redirect to /dashboard after successful login
✅ Auth token stored in httpOnly cookie
✅ User menu replaces sign-in/sign-up buttons in navigation
✅ Backend user record created with clerk_id
✅ No console errors during authentication flow

## Notes
- Clerk handles all authentication logic
- Backend syncs user data via webhook or API
- Session tokens managed by Clerk cookies
- Frontend uses Clerk components (SignIn, SignUp, UserButton)
