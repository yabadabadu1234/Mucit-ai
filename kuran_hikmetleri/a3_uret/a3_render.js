// A3 kitap render'ı: kitap HTML'ini kesim noktalarına göre A3 yükseklikli sayfalara böler.
// Çalıştırma: node kuran_hikmetleri/a3_uret/a3_render.js
// Çıktı: a3_uret/sayfalar/pNNNN.png, a3_uret/kesimler.json
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const DIR = __dirname;
const VW = 1404, DSF = 1.6;
const PAGE_W = 2246, PAGE_H = 3175;          // A3 portrait at 192 dpi
const H = PAGE_H / DSF;                      // page height in CSS px (1984)
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const ctx = await b.newContext({ viewport: { width: VW, height: 1000 }, deviceScaleFactor: DSF });
  const p = await ctx.newPage();
  await p.goto('file:///home/user/Mucit-ai/kuran_hikmetleri/kuran_hikmetleri_kitap.html', { waitUntil: 'load' });
  const info = await p.evaluate(() => {
    const total = document.documentElement.scrollHeight;
    const cands = [...document.querySelectorAll('h1,h2')].map(e => Math.round(e.getBoundingClientRect().top + scrollY)).filter(v => v > 0).sort((a, b) => a - b);
    return { total, cands };
  });
  const cuts = [];
  let start = 0;
  while (start < info.total - 1) {
    const target = start + H;
    let cut = target;
    if (target < info.total) {
      const lo = start + H * 0.6;
      const cand = info.cands.filter(c => c > lo && c <= target);
      if (cand.length) cut = cand[cand.length - 1];
    } else cut = info.total;
    cuts.push([Math.round(start), Math.round(Math.min(cut, info.total))]);
    start = cut;
  }
  fs.writeFileSync(path.join(DIR, 'kesimler.json'), JSON.stringify({ total: info.total, pages: cuts.length, cuts }, null, 1));
  console.log('total', info.total, 'pages', cuts.length);
  fs.mkdirSync(path.join(DIR, 'sayfalar'), { recursive: true });
  for (let i = 0; i < cuts.length; i++) {
    const [y0, y1] = cuts[i];
    await p.screenshot({ path: path.join(DIR, 'sayfalar', `p${String(i + 1).padStart(4, '0')}.png`), fullPage: true,
      clip: { x: 0, y: y0, width: VW, height: y1 - y0 } });
    if (i % 25 === 0) console.log('shot', i + 1, '/', cuts.length);
  }
  await b.close();
  console.log('done');
})().catch(e => { console.error(e); process.exit(1); });
