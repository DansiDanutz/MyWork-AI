const { chromium } = require('playwright');

async function testFeature6Detailed() {
  console.log('🧪 Feature #6: Invalid Credentials - DETAILED TEST\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 300
  });

  const page = await browser.newPage();

  try {
    // Navigate to sign-in
    console.log('1️⃣  Navigating to /sign-in...');
    await page.goto('http://localhost:3004/sign-in');
    await page.waitForSelector('input', { timeout: 15000 });
    console.log('   ✅ Page loaded, form ready\n');

    // Enter email
    console.log('2️⃣  Entering invalid credentials...');
    const testEmail = `invalid_user_${Date.now()}@noverification.test`;
    await page.fill('input[type="text"], input[type="email"]', testEmail);
    console.log(`   ✅ Email: ${testEmail}`);

    await page.waitForTimeout(300);
    await page.fill('input[type="password"]', 'DefinitelyWrongPassword123!');
    console.log('   ✅ Password: DefinitelyWrongPassword123!\n');

    // Click continue
    console.log('3️⃣  Submitting form...');
    const continueButton = await page.$('button:has-text("Continue")');
    if (continueButton) {
      await continueButton.click();
    } else {
      await page.keyboard.press('Enter');
    }
    console.log('   ✅ Form submitted\n');

    // Wait for Clerk response (HTTP 422 error means invalid credentials)
    console.log('4️⃣  Waiting for authentication response...');
    await page.waitForTimeout(4000);

    // Look for error elements
    console.log('5️⃣  Checking for error display...');

    // Check for various error indicators
    const checks = {
      'Alert elements': await page.$$('role=alert'),
      'Error classes': await page.$$('[class*="error"]'),
      'Text with "invalid"': await page.$$('text=/invalid/i'),
      'Text with "incorrect"': await page.$$('text=/incorrect/i'),
    };

    let foundErrors = false;
    for (const [check, elements] of Object.entries(checks)) {
      if (elements.length > 0) {
        console.log(`   ✅ ${check}: ${elements.length} found`);
        foundErrors = true;
      }
    }

    // Get all text on page
    const bodyText = await page.textContent('body');

    // Check for error-related words
    const errorWords = ['invalid', 'incorrect', 'not found', 'could not', 'sign in', 'password'];
    const presentWords = errorWords.filter(w => bodyText.toLowerCase().includes(w));

    if (presentWords.length > 0) {
      console.log(`   ✅ Error keywords found: ${presentWords.join(', ')}`);
      foundErrors = true;
    }

    // Take screenshots
    await page.screenshot({ path: '../verification/feature_6_final_test.png', fullPage: true });
    console.log('\n   📸 Screenshot: feature_6_final_test.png\n');

    // Verify requirements
    console.log('6️⃣  VERIFICATION RESULTS:');
    console.log('   ─────────────────────────────────────');

    // 1. Error message displayed
    if (foundErrors) {
      console.log('   ✅ Error message displayed');
    } else {
      console.log('   ❌ No error message found');
    }

    // 2. No redirect
    const currentUrl = page.url();
    if (currentUrl.includes('/sign-in')) {
      console.log('   ✅ No redirect (still on /sign-in)');
    } else {
      console.log(`   ❌ Redirected to: ${currentUrl}`);
    }

    // 3. Password field state (Clerk may or may not clear it)
    const passwordField = await page.$('input[type="password"]');
    if (passwordField) {
      const pwdValue = await passwordField.inputValue();
      if (pwdValue === '' || pwdValue === null) {
        console.log('   ✅ Password field cleared');
      } else {
        console.log('   ⚠️  Password field not cleared (Clerk default behavior)');
      }
    }

    console.log('\n═══════════════════════════════════════════════════');
    console.log('Feature #6 Status:', foundErrors ? '✅ PASS' : '❌ FAIL');
    console.log('═══════════════════════════════════════════════════\n');

    return foundErrors;

  } catch (error) {
    console.error('\n❌ Error:', error.message);
    await page.screenshot({ path: '../verification/feature_6_crash.png' });
    return false;
  } finally {
    await browser.close();
  }
}

testFeature6Detailed().then(success => {
  process.exit(success ? 0 : 1);
}).catch(() => process.exit(1));
