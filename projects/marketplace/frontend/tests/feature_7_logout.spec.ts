/**
 * Test Script for Feature #7: User can logout and clear session
 *
 * This test verifies:
 * 1. Login as valid user
 * 2. Click user menu in navigation
 * 3. Click Logout button
 * 4. Verify redirect to home page
 * 5. Verify auth cookies are cleared
 * 6. Verify user menu no longer shows
 * 7. Attempt to access protected route - should redirect to login
 */

import { test, expect, Page, BrowserContext } from '@playwright/test';

test.describe('Feature #7: User Logout', () => {
  let page: Page;
  let context: BrowserContext;

  test.beforeEach(async ({ browser }) => {
    context = await browser.newContext();
    page = await context.newPage();

    // Navigate to sign-in page
    await page.goto('http://localhost:3000/sign-in');
  });

  test.afterEach(async () => {
    await context.close();
  });

  test('Complete logout flow verification', async () => {
    console.log('🧪 Starting Feature #7 Verification: User Logout');

    // Step 1: Login as valid user
    console.log('✓ Step 1: Navigate to sign-in page');

    // Note: For testing, we'll create a test user or use existing credentials
    // In development mode, Clerk allows creating users easily

    // Check if we're on the sign-in page
    await expect(page.locator('h1')).toContainText('Welcome Back');
    console.log('✓ Step 1: Sign-in page loaded');

    // For automated testing, we need to handle the sign-in form
    // In development, Clerk shows a form where we can sign up/sign in
    // We'll use the dev mode to create a test user

    // Look for the sign-up link to create a test user first
    const signUpLink = page.getByText('Sign up').first();
    if (await signUpLink.isVisible()) {
      await signUpLink.click();
      await expect(page.locator('h1')).toContainText('Create Your Account');
      console.log('✓ Step 1: Navigated to sign-up for test user creation');

      // Fill in test user credentials
      const timestamp = Date.now();
      const testEmail = `test_${timestamp}@example.com`;
      const testPassword = 'TestPass123';

      // Clerk's form fields
      await page.fill('input[name="emailAddress"]', testEmail);
      await page.fill('input[name="password"]', testPassword);
      await page.fill('input[name="confirmPassword"]', testPassword);

      console.log(`✓ Step 1: Filled in test credentials: ${testEmail}`);

      // Submit the form
      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();

      // Wait for redirect to dashboard or success message
      await page.waitForURL('**/dashboard', { timeout: 10000 });
      console.log('✓ Step 1: User registered and redirected to dashboard');
    } else {
      // If sign-up link not visible, try to sign in with existing test account
      await page.fill('input[name="emailAddress"]', 'test@example.com');
      await page.fill('input[name="password"]', 'TestPass123');

      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();

      await page.waitForURL('**/dashboard', { timeout: 10000 });
      console.log('✓ Step 1: User logged in and redirected to dashboard');
    }

    // Verify we're logged in
    const url = page.url();
    expect(url).toContain('/dashboard');
    console.log('✓ Step 1: User successfully logged in');

    // Step 2: Click user menu in navigation
    console.log('✓ Step 2: Looking for user menu button');

    // The UserButton should be visible in the navigation
    // Clerk's UserButton is typically rendered as an avatar or user icon
    const userButton = page.locator('[class*="cl-userButton"]').first();
    await expect(userButton).toBeVisible({ timeout: 5000 });
    console.log('✓ Step 2: User menu button found in navigation');

    // Step 3: Click Logout button
    console.log('✓ Step 3: Clicking user menu to open it');

    // Click the user button to open the menu
    await userButton.click();
    console.log('✓ Step 3: User menu opened');

    // Wait for the menu to appear and look for the sign-out button
    const signOutButton = page.locator('button[aria-label*="Sign out"], button:has-text("Sign out"), button:has-text("Logout")').first();
    await expect(signOutButton).toBeVisible({ timeout: 5000 });
    console.log('✓ Step 3: Logout/Sign out button found');

    // Get current cookies before logout
    const cookiesBefore = await context.cookies();
    console.log(`✓ Step 3: Cookies before logout: ${cookiesBefore.length} cookies`);

    // Click the sign-out button
    await signOutButton.click();
    console.log('✓ Step 3: Clicked logout button');

    // Step 4: Verify redirect to home page
    console.log('✓ Step 4: Checking redirect after logout');

    // Wait for navigation to complete
    await page.waitForURL('http://localhost:3000/', { timeout: 5000 });
    expect(page.url()).toBe('http://localhost:3000/');
    console.log('✓ Step 4: Successfully redirected to home page');

    // Step 5: Verify auth cookies are cleared
    console.log('✓ Step 5: Checking auth cookies after logout');

    const cookiesAfter = await context.cookies();
    console.log(`✓ Step 5: Cookies after logout: ${cookiesAfter.length} cookies`);

    // Clerk-specific cookies should be cleared
    const clerkCookiesBefore = cookiesBefore.filter(c => c.name.includes('__clerk'));
    const clerkCookiesAfter = cookiesAfter.filter(c => c.name.includes('__clerk'));

    expect(clerkCookiesAfter.length).toBe(0);
    expect(clerkCookiesAfter.length).toBeLessThan(clerkCookiesBefore.length);
    console.log('✓ Step 5: Auth cookies cleared successfully');

    // Step 6: Verify user menu no longer shows
    console.log('✓ Step 6: Verifying user menu is hidden after logout');

    // The UserButton should not be visible
    // Instead, Sign In and Sign Up buttons should be visible
    const signInButton = page.locator('a[href="/sign-in"]');
    const signUpButton = page.locator('a[href="/sign-up"]');
    const dashboardLink = page.locator('a[href="/dashboard"]');

    await expect(signInButton).toBeVisible();
    await expect(signUpButton).toBeVisible();
    console.log('✓ Step 6: Sign In/Sign Up buttons visible (logged out state)');

    // Dashboard link should not be visible in navigation when logged out
    const dashboardLinkVisible = await dashboardLink.isVisible().catch(() => false);
    expect(dashboardLinkVisible).toBe(false);
    console.log('✓ Step 6: Dashboard link hidden (user menu not accessible)');

    // Step 7: Attempt to access protected route - should redirect to login
    console.log('✓ Step 7: Attempting to access protected route');

    // Try to access the dashboard directly
    await page.goto('http://localhost:3000/dashboard');

    // Should be redirected to sign-in page
    await page.waitForURL('**/sign-in**', { timeout: 5000 });
    expect(page.url()).toContain('/sign-in');
    console.log('✓ Step 7: Protected route redirected to sign-in page');

    // Verify we can't access dashboard content
    const dashboardContent = page.locator('h1, h2').filter({ hasText: /Menu|Overview|My Products/i });
    const isDashboardVisible = await dashboardContent.isVisible().catch(() => false);
    expect(isDashboardVisible).toBe(false);
    console.log('✓ Step 7: Dashboard content not accessible');

    console.log('✅ Feature #7 PASSED: User logout functionality working correctly');
  });

  test('Logout persists across page reloads', async () => {
    console.log('🧪 Testing logout persistence');

    // Sign in first
    await page.goto('http://localhost:3000/sign-in');
    await page.waitForLoadState('networkidle');

    // Create/sign in as test user
    const signUpLink = page.getByText('Sign up').first();
    if (await signUpLink.isVisible()) {
      await signUpLink.click();
      await page.fill('input[name="emailAddress"]', `persist_test_${Date.now()}@example.com`);
      await page.fill('input[name="password"]', 'TestPass123');
      await page.fill('input[name="confirmPassword"]', 'TestPass123');
      await page.locator('button[type="submit"]').first().click();
      await page.waitForURL('**/dashboard', { timeout: 10000 });
    }

    // Logout
    const userButton = page.locator('[class*="cl-userButton"]').first();
    await userButton.click();
    const signOutButton = page.locator('button:has-text("Sign out")').first();
    await signOutButton.click();
    await page.waitForURL('http://localhost:3000/');

    // Reload the page
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Verify still logged out after reload
    const signInButton = page.locator('a[href="/sign-in"]');
    await expect(signInButton).toBeVisible();
    console.log('✅ Logout persists across page reloads');
  });
});
