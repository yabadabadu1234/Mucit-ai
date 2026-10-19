// A3 kitap render'ı: kitap HTML'ini başlık (h1/h2) kesim noktalarına göre A3 yükseklikli sayfalara böler.
// Kullanım: node a3_render.js [--html yol] [--cikti klasör] [--vw 1404] [--dsf 1.6]
// Her çalıştırmada çıktı klasöründeki eski sayfalar silinir (birikmez). Sayfalar JPEG (kalite 85).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const arg = (ad, varsayilan) => { const i = args.indexOf(ad); return i >= 0 ? args[i + 1] : varsayilan; };
const DIR = __dirname;
const HTML = path.resolve(arg('--html', path.join(DIR, '..', 'kuran_hikmetleri_kitap.html')));
const CIKTI = path.resolve(arg('--cikti', path.join(DIR, 'sayfalar')));
const VW = Number(arg('--vw', 1404));
const DSF = Number(arg('--dsf', 1.6));
const PAGE_H = 3175;                 // A3 dikey, 192 dpi (2246 x 3175 px)
const H = PAGE_H / DSF;              // sayfa yüksekliği CSS px cinsinden

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const ctx = await b.newContext({ viewport: { width: VW, height: 1000 }, deviceScaleFactor: DSF });
  const p = await ctx.newPage();
  await p.goto('file://' + HTML, { waitUntil: 'load' });
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
  fs.rmSync(CIKTI, { recursive: true, force: true });
  fs.mkdirSync(CIKTI, { recursive: true });
  fs.writeFileSync(path.join(path.dirname(CIKTI), 'kesimler.json'), JSON.stringify({ total: info.total, pages: cuts.length, cuts }, null, 1));
  console.log('toplam', info.total, 'sayfa', cuts.length);
  for (let i = 0; i < cuts.length; i++) {
    const [y0, y1] = cuts[i];
    await p.screenshot({ path: path.join(CIKTI, `p${String(i + 1).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 85, fullPage: true,
      clip: { x: 0, y: y0, width: VW, height: y1 - y0 } });
    if (i % 25 === 0) console.log('çekildi', i + 1, '/', cuts.length);
  }
  await b.close();
  console.log('bitti');
})().catch(e => { console.error(e); process.exit(1); });
