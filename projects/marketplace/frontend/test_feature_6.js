const { chromium } = require('playwright');

async function testFeature6() {
  console.log('🧪 Feature #6: Invalid Credentials Error Handling\n');
  console.log('═══════════════════════════════════════════════════\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 500
  });

  const page = await browser.newPage();

  try {
    // STEP 1: Navigate to /sign-in
    console.log('STEP 1: Navigate to /sign-in');
    await page.goto('http://localhost:3004/sign-in', { waitUntil: 'networkidle' });
    console.log('✅ Page loaded\n');

    // Wait for Clerk to initialize
    console.log('⏳ Waiting for Clerk form to load...');
    await page.waitForTimeout(3000);

    // STEP 2: Look for email input
    console.log('\nSTEP 2: Find email input field');
    const emailInput = await page.$('input[type="text"], input[type="email"], input[name="identifier"]');
    if (!emailInput) {
      throw new Error('Email input not found');
    }
    console.log('✅ Email input found\n');

    // STEP 3: Enter test email
    console.log('STEP 3: Enter test email');
    const testEmail = `test_${Date.now()}@invalid-test.com`;
    await emailInput.fill(testEmail);
    console.log(`✅ Entered: ${testEmail}\n`);

    // STEP 4: Look for password input
    console.log('STEP 4: Find password input field');
    await page.waitForTimeout(500);
    const passwordInput = await page.$('input[type="password"]');
    if (!passwordInput) {
      throw new Error('Password input not found');
    }
    console.log('✅ Password input found\n');

    // STEP 5: Enter wrong password
    console.log('STEP 5: Enter incorrect password');
    await passwordInput.fill('WrongPassword123!');
    console.log('✅ Entered: WrongPassword123!\n');

    // STEP 6: Find and click submit button
    console.log('STEP 6: Find and click submit button');
    await page.waitForTimeout(500);

    // Try multiple button selectors
    const buttonSelectors = [
      'button:not([disabled])',
      'button[type="submit"]',
      'button:visible',
      'form button'
    ];

    let submitButton = null;
    for (const selector of buttonSelectors) {
      const buttons = await page.$$(selector);
      console.log(`  Testing selector "${selector}": ${buttons.length} buttons`);

      for (const button of buttons) {
        const text = await button.textContent();
        const isVisible = await button.isVisible();
        const isEnabled = await button.isEnabled();

        console.log(`    - "${text?.trim()}" visible=${isVisible} enabled=${isEnabled}`);

        if (isVisible && isEnabled && text && text.trim().length > 0) {
          submitButton = button;
          console.log(`    ✅ Selected button: "${text.trim()}"`);
          break;
        }
      }

      if (submitButton) break;
    }

    if (!submitButton) {
      throw new Error('Submit button not found');
    }

    // Click the button
    await submitButton.click();
    console.log('✅ Submit button clicked\n');

    // STEP 7: Wait for response
    console.log('STEP 7: Wait for authentication response...');
    await page.waitForTimeout(5000);

    // STEP 8: Check for error message
    console.log('\nSTEP 8: Check for error message');

    // Take screenshot of current state
    await page.screenshot({ path: '../verification/feature_6_error_state.png' });
    console.log('📸 Screenshot: feature_6_error_state.png');

    // Look for error indicators
    const pageText = await page.textContent('body');
    const errorIndicators = [
      'incorrect',
      'invalid',
      'not found',
      'could not',
      'failed'
    ];

    let hasError = false;
    const foundErrors = [];

    for (const indicator of errorIndicators) {
      if (pageText.toLowerCase().includes(indicator)) {
        hasError = true;
        foundErrors.push(indicator);
      }
    }

    if (hasError) {
      console.log(`✅ Error detected with keywords: ${foundErrors.join(', ')}`);
    } else {
      console.log('⚠️  No clear error message found');
      console.log('📄 Page preview (first 1000 chars):');
      console.log(pageText.substring(0, 1000));
    }

    // STEP 9: Verify no redirect
    console.log('\nSTEP 9: Verify page did not redirect');
    const currentUrl = page.url();
    if (currentUrl.includes('/sign-in')) {
      console.log(`✅ Still on sign-in page: ${currentUrl}`);
    } else {
      console.log(`❌ Page redirected to: ${currentUrl}`);
    }

    // STEP 10: Check password field
    console.log('\nSTEP 10: Check if password field was cleared');
    const passwordAfter = await passwordInput.inputValue();
    if (passwordAfter === '' || passwordAfter === null) {
      console.log('✅ Password field was cleared');
    } else {
      console.log(`⚠️  Password field still has value: "${passwordAfter}"`);
    }

    // Final summary
    console.log('\n═══════════════════════════════════════════════════');
    console.log('FEATURE #6 VERIFICATION SUMMARY');
    console.log('═══════════════════════════════════════════════════');
    console.log(`✅ Test email: ${testEmail}`);
    console.log(`✅ Wrong password: WrongPassword123!`);
    console.log(hasError ? '✅ Error message displayed' : '❌ Error message not found');
    console.log(currentUrl.includes('/sign-in') ? '✅ No redirect occurred' : '❌ Page redirected');
    console.log(passwordAfter === '' || passwordAfter === null ? '✅ Password field cleared' : '⚠️  Password field not cleared');
    console.log('\n📸 Screenshots saved to ../verification/');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    await page.screenshot({ path: '../verification/feature_6_test_error.png' });
    console.log('📸 Error screenshot: feature_6_test_error.png');
  } finally {
    await browser.close();
    console.log('\n✅ Test complete');
  }
}

testFeature6().catch(console.error);
