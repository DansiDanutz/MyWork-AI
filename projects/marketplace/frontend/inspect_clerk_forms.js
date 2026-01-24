const { chromium } = require('playwright');

async function inspectClerkForm() {
  console.log('🔍 Inspecting Clerk Sign-In Form...\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 300
  });

  const page = await browser.newPage();

  try {
    await page.goto('http://localhost:3004/sign-in');
    await page.waitForLoadState('networkidle');

    // Wait a bit for Clerk to initialize
    await page.waitForTimeout(2000);

    console.log('Page loaded. Checking form elements...\n');

    // Try different selectors
    const selectors = [
      'button[type="submit"]',
      'button:has-text("Sign in")',
      'button:has-text("Continue")',
      'button[data-localization]',
      '.clerk-form-button-primary',
      'button[class*="form"]',
      'button'
    ];

    for (const selector of selectors) {
      const elements = await page.$$(selector);
      console.log(`Selector "${selector}": found ${elements.length} element(s)`);

      if (elements.length > 0) {
        for (let i = 0; i < Math.min(elements.length, 3); i++) {
          const text = await elements[i].textContent();
          const visible = await elements[i].isVisible();
          const enabled = await elements[i].isEnabled();
          console.log(`  [${i}] text="${text?.trim()}" visible=${visible} enabled=${enabled}`);
        }
      }
    }

    console.log('\n📸 Screenshot saved as: clerk_form_inspection.png');
    await page.screenshot({ path: '../verification/clerk_form_inspection.png', fullPage: true });

  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
}

inspectClerkForm().catch(console.error);
