const { chromium } = require('playwright');

async function testInvalidCredentials() {
  console.log('🧪 Testing Feature #6: Invalid credentials error handling\n');

  const browser = await chromium.launch({
    headless: false, // Set to true for CI
    slowMo: 500 // Slow down for visibility
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Step 1: Navigate to /sign-in
    console.log('1️⃣  Navigating to /sign-in...');
    await page.goto('http://localhost:3004/sign-in');
    await page.waitForLoadState('networkidle');
    console.log('   ✅ Page loaded\n');

    // Take screenshot of initial state
    await page.screenshot({ path: 'verification/feature_6_01_initial.png' });
    console.log('   📸 Screenshot: feature_6_01_initial.png\n');

    // Step 2: Enter an email address
    console.log('2️⃣  Entering test email...');
    const testEmail = `test_${Date.now()}@example.com`;
    await page.fill('input[name="identifier"]', testEmail);
    console.log(`   ✅ Email entered: ${testEmail}\n`);

    // Step 3: Enter incorrect password
    console.log('3️⃣  Entering incorrect password...');
    await page.fill('input[type="password"]', 'WrongPassword123!');
    console.log('   ✅ Password entered: WrongPassword123!\n');

    // Take screenshot before submitting
    await page.screenshot({ path: 'verification/feature_6_02_before_submit.png' });
    console.log('   📸 Screenshot: feature_6_02_before_submit.png\n');

    // Step 4: Click Login button
    console.log('4️⃣  Clicking "Sign In" button...');
    await page.click('button[type="submit"]');
    console.log('   ✅ Button clicked\n');

    // Wait for error message to appear
    console.log('5️⃣  Waiting for error response...');
    await page.waitForTimeout(3000); // Wait for Clerk to validate

    // Take screenshot of error state
    await page.screenshot({ path: 'verification/feature_6_03_error_displayed.png' });
    console.log('   📸 Screenshot: feature_6_03_error_displayed.png\n');

    // Step 5: Verify error message appears
    console.log('6️⃣  Checking for error message...');
    const errorSelectors = [
      '[data-localization="errors.identification"]',
      '.clerk-alert-error',
      '[role="alert"]',
      '.clerk-form-field-error'
    ];

    let errorElement = null;
    let errorText = '';

    for (const selector of errorSelectors) {
      try {
        errorElement = await page.$(selector);
        if (errorElement) {
          errorText = await errorElement.textContent();
          console.log(`   ✅ Found error with selector: ${selector}`);
          console.log(`   📝 Error text: "${errorText.trim()}"`);
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }

    if (!errorElement) {
      // Try to find any text containing "error", "invalid", "incorrect", "not found"
      const pageText = await page.textContent('body');
      const errorKeywords = ['invalid', 'incorrect', 'not found', 'sign in', 'password', 'email'];
      const hasError = errorKeywords.some(keyword =>
        pageText.toLowerCase().includes(keyword) &&
        (pageText.toLowerCase().includes('incorrect') ||
         pageText.toLowerCase().includes('invalid') ||
         pageText.toLowerCase().includes('not found'))
      );

      if (hasError) {
        console.log('   ✅ Error detected in page text');
      } else {
        console.log('   ❌ No error message found');
        console.log('   📄 Full page text:');
        console.log(pageText.substring(0, 500));
      }
    }

    // Step 6: Verify page didn't redirect
    console.log('\n7️⃣  Checking if page redirected...');
    const currentUrl = page.url();
    if (currentUrl.includes('/sign-in')) {
      console.log(`   ✅ Still on /sign-in: ${currentUrl}`);
    } else {
      console.log(`   ❌ Page redirected to: ${currentUrl}`);
    }

    // Step 7: Verify password field is cleared
    console.log('\n8️⃣  Checking if password field was cleared...');
    const passwordValue = await page.inputValue('input[type="password"]');
    if (passwordValue === '') {
      console.log('   ✅ Password field cleared');
    } else {
      console.log(`   ⚠️  Password field still has value: "${passwordValue}"`);
    }

    // Final screenshot
    await page.screenshot({ path: 'verification/feature_6_04_final_state.png' });
    console.log('\n   📸 Screenshot: feature_6_04_final_state.png\n');

    // Summary
    console.log('═══════════════════════════════════════════════════');
    console.log('Feature #6 Verification Complete');
    console.log('═══════════════════════════════════════════════════');
    console.log('\n📋 Test Results:');
    console.log('  ✅ Navigated to /sign-in');
    console.log('  ✅ Entered email:', testEmail);
    console.log('  ✅ Entered incorrect password');
    console.log('  ✅ Clicked Sign In button');
    console.log(errorElement || errorText ? '  ✅ Error message displayed' : '  ⚠️  Error message not clearly found');
    console.log(currentUrl.includes('/sign-in') ? '  ✅ Page did not redirect' : '  ❌ Page redirected');
    console.log(passwordValue === '' ? '  ✅ Password field cleared' : '  ⚠️  Password field not cleared');
    console.log('\n📸 Screenshots saved to verification/');

  } catch (error) {
    console.error('\n❌ Test failed with error:', error.message);
    await page.screenshot({ path: 'verification/feature_6_error.png' });
    console.log('   📸 Error screenshot: feature_6_error.png');
  } finally {
    await browser.close();
  }
}

test_invalid_credentials().catch(console.error);
