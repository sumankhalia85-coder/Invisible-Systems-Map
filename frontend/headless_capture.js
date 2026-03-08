const { chromium } = require('playwright');
(async ()=> {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const logs = { console: [], pageErrors: [], requestFails: [], badResponses: [] };

  page.on('console', msg => logs.console.push({ type: msg.type(), text: msg.text() }));
  page.on('pageerror', err => logs.pageErrors.push(String(err)));
  page.on('requestfailed', req => logs.requestFails.push({ url: req.url(), method: req.method(), failure: req.failure() }));
  page.on('response', async res => {
    try {
      const status = res.status();
      const url = res.url();
      if (status >= 400) logs.badResponses.push({ url, status });
      if (/earth|three-globe|three_globe|globe-gl|earth-blue-marble/i.test(url)) logs.badResponses.push({ url, status });
    } catch (e) {}
  });

  const target = process.argv[2] || 'http://localhost:3001/';
  console.log('Visiting', target);
  try {
    await page.goto(target, { waitUntil: 'networkidle', timeout: 20000 });
  } catch (e) {
    // continue even if goto times out
    console.log('goto error:', e.message);
  }
  await page.waitForTimeout(2500);

  const content = await page.content();
  const markers = ['GLOBE RENDER SUCCESS','GLOBE RENDER ERROR','earth-blue-marble','onPointClick','onArcClick','globe.gl'];
  const found = markers.map(m => ({ marker: m, found: content.includes(m) }));

  const out = { found, logs, htmlSnippet: content.slice(0, 4000) };
  console.log(JSON.stringify(out, null, 2));
  await browser.close();
  process.exit(0);
})();
