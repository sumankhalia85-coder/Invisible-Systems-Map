const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const page = await context.newPage();

  let sawSuccess = false;
  page.on('console', async msg => {
    try {
      const text = msg.text();
      console.log('PAGE_CONSOLE:', msg.type(), text);
      if (typeof text === 'string' && text.includes('GLOBE RENDER SUCCESS')) {
        sawSuccess = true;
        const path = 'capture_globe.png';
        await page.screenshot({ path, fullPage: true });
        console.log('SCREENSHOT_SAVED:', path);
        await browser.close();
        process.exit(0);
      }
    } catch (e) {}
  });

  try {
    await page.goto('http://localhost:3003', { waitUntil: 'networkidle' });
    // wait up to 20s for globe to render
    await page.waitForTimeout(20000);

    if (!sawSuccess) {
      const path = 'capture_globe_fallback.png';
      await page.screenshot({ path, fullPage: true });
      console.log('SCREENSHOT_FALLBACK_SAVED:', path);
      await browser.close();
      process.exit(0);
    }
  } catch (err) {
    console.error('CAPTURE_ERROR', err);
    try { await browser.close(); } catch(e){}
    process.exit(2);
  }
})();
