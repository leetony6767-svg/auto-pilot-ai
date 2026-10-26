// Test multilingual switching on deployed site
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 375, height: 812 } // iPhone size
  });
  const page = await context.newPage();

  console.log('=== Testing zh-TW (default) ===');
  await page.goto('https://auto-pilot-ai.onrender.com/');
  await page.waitForLoadState('networkidle');

  // Check ticker
  const ticker = await page.textContent('.ticker-content span').catch(() => 'N/A');
  console.log('Ticker:', ticker?.substring(0, 80));

  // Check hero title
  const heroTitle = await page.textContent('.hero-title').catch(() => 'N/A');
  console.log('Hero title:', heroTitle?.substring(0, 60));

  console.log('\n=== Switching to Indonesian (id) ===');
  await page.selectOption('#langSelector', 'id');
  await page.waitForTimeout(500); // Wait for language switch

  const tickerId = await page.textContent('.ticker-content span').catch(() => 'N/A');
  console.log('Ticker (ID):', tickerId?.substring(0, 80));

  const heroTitleId = await page.textContent('.hero-title').catch(() => 'N/A');
  console.log('Hero title (ID):', heroTitleId?.substring(0, 60));

  const navStatus = await page.textContent('.navbar-status span:last-child').catch(() => 'N/A');
  console.log('Nav status (ID):', navStatus);

  // Check if Indonesian text is present
  const hasIndonesian = tickerId?.includes('Siap') || tickerId?.includes('Melayani');
  console.log('\n=== Result ===');
  console.log('Indonesian text loaded:', hasIndonesian ? '✓ YES' : '✗ NO');

  // Screenshot
  await page.screenshot({ path: 'test-id-lang.png', fullPage: false });
  console.log('\nScreenshot saved: test-id-lang.png');

  await browser.close();
})();
