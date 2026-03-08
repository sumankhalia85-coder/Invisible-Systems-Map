const { chromium } = require('playwright');
const fs = require('fs');
(async ()=>{
  const target = process.argv[2] || 'http://localhost:3001/';
  console.log('Opening', target);
  const browser = await chromium.launch({ headless: false, args: ['--disable-gpu'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

  const logs = { console: [], pageErrors: [] };
  page.on('console', m => logs.console.push({ type: m.type(), text: m.text() }));
  page.on('pageerror', e => logs.pageErrors.push(String(e)));

  await page.goto(target, { waitUntil: 'networkidle' }).catch(e => console.log('goto err', e.message));
  await page.waitForTimeout(1600);

  // Switch to 3D Globe view
  try {
    const btn3d = await page.$('text=3D Globe');
    if (btn3d) { await btn3d.click(); console.log('Switched to 3D view'); }
    await page.waitForTimeout(800);
  } catch (e) { console.log('3D toggle error', e.message); }

  // Enable Climate layer
  try {
    const climateBtn = await page.$("text=Climate Monitor");
    if (climateBtn) { await climateBtn.click(); console.log('Toggled Climate layer'); }
    await page.waitForTimeout(900);
  } catch (e) { console.log('Climate toggle error', e.message); }

  // Try to click the globe canvas center to select a node
  try {
    // Try programmatic selection: fetch a climate node from backend and invoke debug hook
    const resp = await page.evaluate(async () => {
      try {
        const base = window.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const r = await fetch(`${base}/systems/climate`);
        return await r.json();
      } catch (e) { return null; }
    });

    if (resp && resp.nodes && Array.isArray(resp.nodes.features) && resp.nodes.features.length > 0) {
      const f = resp.nodes.features[0];
      const [lng, lat] = f.geometry.coordinates;
      const payload = { ...f.properties, coordinates: [lng, lat], system: 'climate' };
      // Call debug hook exposed by GlobeComponent
      await page.evaluate((p) => {
        if (window.__SELECT_GLOBE_POINT) window.__SELECT_GLOBE_POINT(p);
      }, payload);
      console.log('Programmatically selected climate node');
    } else {
      const canvas = await page.$('canvas');
      if (canvas) {
        const box = await canvas.boundingBox();
        console.log('Canvas bounding box:', box && { x: box.x, y: box.y, w: box.width, h: box.height });
        const cx = Math.floor((box.x || 0) + (box.width || 1280) / 2);
        const cy = Math.floor((box.y || 0) + (box.height || 800) / 2);
        await page.mouse.click(cx, cy);
        console.log('Clicked canvas at', cx, cy);
      } else {
        console.log('No canvas found');
      }
    }
  } catch (e) {
    console.log('Canvas click error', e.message);
  }

  // Wait longer to allow InfoPanel to fully render
  await page.waitForTimeout(5000);

  // Screenshot
  const screenshotPath = 'capture_headful.png';
  try {
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log('Saved screenshot to', screenshotPath);
  } catch (e) { console.log('screenshot error', e.message); }

  // Read InfoPanel content (prefer panel that contains "Environmental Telemetry" or fallback)
  const infoText = await page.evaluate(() => {
    const panels = Array.from(document.querySelectorAll('.glass-panel'));
    const found = panels.find(p => (p.innerText || '').includes('Environmental Telemetry')) || panels[panels.length - 1] || null;
    return found ? found.innerText.slice(0, 800) : null;
  });

  console.log('InfoPanel snippet:', infoText);
  console.log('Collected console messages count:', logs.console.length);
  console.log(JSON.stringify(logs, null, 2));

  await browser.close();
  process.exit(0);
})();
