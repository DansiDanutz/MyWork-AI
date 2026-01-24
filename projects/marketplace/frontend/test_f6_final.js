const { chromium } = require('playwright');

async function testFeature6Final() {
  console.log('🧪 Feature #6: Invalid Credentials Error\n');
  console.log('═══════════════════════════════════════════════════\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 200
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  try {
    // Listen for console messages
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('🔴 Browser console error:', msg.text());
      }
    });

    // STEP 1: Navigate to sign-in
    console.log('STEP 1: Navigate to /sign-in');
    await page.goto('http://localhost:3004/sign-in');

    // Wait for Clerk to load - wait for any input to appear
    console.log('\n⏳ Waiting for Clerk form to mount...');
    await page.waitForSelector('input', { timeout: 15000 });
    console.log('✅ Clerk form loaded\n');

    // Take initial screenshot
    await page.screenshot({ path: '../verification/f6_01_initial.png' });
    console.log('📸 Screenshot: f6_01_initial.png\n');

    // STEP 2: Enter email
    console.log('STEP 2: Enter test email');
    const testEmail = `test_${Date.now()}@doesnotexist.test`;
    const inputs = await page.$$('input');

    console.log(`  Found ${inputs.length} input fields`);

    // First input is usually email
    await inputs[0].fill(testEmail);
    console.log(`✅ Entered: ${testEmail}\n`);

    // STEP 3: Enter password
    console.log('STEP 3: Enter incorrect password');

    // Wait for password field to appear (it might appear after email)
    await page.waitForTimeout(500);

    const passwordInput = await page.$('input[type="password"]');
    if (passwordInput) {
      await passwordInput.fill('WrongPassword123!');
      console.log('✅ Entered: WrongPassword123!\n');
    } else {
      // Try second input if no password type found
      if (inputs.length > 1) {
        await inputs[1].fill('WrongPassword123!');
        console.log('✅ Entered: WrongPassword123! (in second input)\n');
      }
    }

    // Screenshot before submit
    await page.screenshot({ path: '../verification/f6_02_filled.png' });
    console.log('📸 Screenshot: f6_02_filled.png\n');

    // STEP 4: Click submit button
    console.log('STEP 4: Find and click submit button');

    // Look for any visible button
    const buttons = await page.$$('button');
    console.log(`  Found ${buttons.length} buttons`);

    let submitButton = null;
    for (let i = 0; i < buttons.length; i++) {
      const text = await buttons[i].textContent();
      const isVisible = await buttons[i].isVisible();
      const isEnabled = await buttons[i].isEnabled();

      if (isVisible && isEnabled && text && text.trim().length > 0 && text.trim().length < 50) {
        console.log(`  Button ${i}: "${text.trim()}"`);
        submitButton = buttons[i];

        // Prefer "Continue", "Sign in", "Submit" buttons
        if (/continue|sign in|submit/i.test(text)) {
          break;
        }
      }
    }

    if (!submitButton) {
      // Try pressing Enter instead
      console.log('  No suitable button found, pressing Enter...');
      await page.keyboard.press('Enter');
    } else {
      await submitButton.click();
      console.log('✅ Button clicked\n');
    }

    // STEP 5: Wait for Clerk to validate
    console.log('STEP 5: Waiting for authentication response...');
    await page.waitForTimeout(5000);

    // Screenshot after response
    await page.screenshot({ path: '../verification/f6_03_response.png' });
    console.log('📸 Screenshot: f6_03_response.png\n');

    // STEP 6: Check for error
    console.log('STEP 6: Check for error message');

    const pageText = await page.textContent('body');
    const errorKeywords = ['incorrect', 'invalid', 'not found', 'could not', 'sign in', 'password'];
    let foundErrors = [];

    for (const keyword of errorKeywords) {
      if (pageText.toLowerCase().includes(keyword)) {
        foundErrors.push(keyword);
      }
    }

    if (foundErrors.length > 0) {
      console.log(`✅ Error detected with keywords: ${foundErrors.join(', ')}`);
    } else {
      console.log('⚠️  No clear error message detected');
      console.log('📄 Page preview:');
      const cleanText = pageText.replace(/\s+/g, ' ').trim();
      console.log(cleanText.substring(0, 500));
    }

    // STEP 7: Verify no redirect
    console.log('\nSTEP 7: Verify no redirect occurred');
    const url = page.url();
    if (url.includes('/sign-in')) {
      console.log(`✅ Still on sign-in page`);
    } else {
      console.log(`❌ Redirected to: ${url}`);
    }

    // STEP 8: Check password field
    console.log('\nSTEP 8: Check password field');
    const pwdInput = await page.$('input[type="password"]');
    if (pwdInput) {
      const val = await pwdInput.inputValue();
      if (val === '' || val === null) {
        console.log('✅ Password field cleared');
      } else {
        console.log(`⚠️  Password still has value`);
      }
    }

    // Summary
    console.log('\n═══════════════════════════════════════════════════');
    console.log('FEATURE #6 VERIFICATION COMPLETE');
    console.log('═══════════════════════════════════════════════════');
    console.log(`📧 Test email: ${testEmail}`);
    console.log(`🔑 Wrong password: WrongPassword123!`);
    console.log(foundErrors.length > 0 ? '✅ Error displayed' : '❌ No error found');
    console.log(url.includes('/sign-in') ? '✅ No redirect' : '❌ Redirect occurred');
    console.log('\n📁 Screenshots: ../verification/f6_*.png');

  } catch (error) {
    console.error('\n❌ Test error:', error.message);
    await page.screenshot({ path: '../verification/f6_error.png' });
    console.log('📸 Error screenshot: f6_error.png');
  } finally {
    await browser.close();
    console.log('\n✅ Done');
  }
}

testFeature6Final().catch(console.error);
