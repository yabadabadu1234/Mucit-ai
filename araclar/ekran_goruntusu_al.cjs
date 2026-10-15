const puppeteer = require("puppeteer");
const path = require("path");
const fs = require("fs");

async function capture() {
  const outDir = path.resolve(__dirname, "../docs/sunum_gorseller");
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
  });

  const page = await browser.newPage();
  // 2x deviceScaleFactor for ultra crisp, sharp retina text rendering
  await page.setViewport({ width: 1600, height: 1200, deviceScaleFactor: 2 });

  const htmlPath = "file://" + path.resolve(__dirname, "../docs/planli_eskitme_sunum_panosu.html");
  await page.goto(htmlPath, { waitUntil: "networkidle0" });

  // Capture all 8 slide cards (slide-00 to slide-07)
  for (let i = 0; i <= 7; i++) {
    const selector = `#slide-0${i}`;
    const el = await page.$(selector);
    if (el) {
      const outPath = path.join(outDir, `slide_0${i}.png`);
      await el.screenshot({ path: outPath });
      console.log(`Captured ${selector} -> ${outPath}`);
    } else {
      console.warn(`Element ${selector} not found!`);
    }
  }

  await browser.close();
  console.log("All 8 slides captured successfully!");
}

capture().catch(err => {
  console.error(err);
  process.exit(1);
});
