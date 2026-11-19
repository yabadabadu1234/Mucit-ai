const { chromium } = require('playwright');

async function main() {
  const url = process.argv[2];
  const cikti = process.argv[3] || 'sayfa.png';
  const metinDosyasi = process.argv[4];
  if (!url) {
    console.error('Kullanım: node gez.js <adres> [resim.png] [metin.txt]');
    process.exit(2);
  }
  const tarayici = await chromium.launch();
  const sayfa = await tarayici.newPage({ viewport: { width: 1280, height: 1800 } });
  try {
    const cevap = await sayfa.goto(url, { timeout: 45000, waitUntil: 'domcontentloaded' });
    console.log('durum', cevap && cevap.status());
    console.log('baslik', await sayfa.title());
    await sayfa.screenshot({ path: cikti, fullPage: true });
    if (metinDosyasi) {
      const metin = await sayfa.evaluate(() => document.body.innerText);
      require('fs').writeFileSync(metinDosyasi, metin);
    }
  } catch (hata) {
    console.error('hata', hata.message.split('\n')[0]);
    process.exitCode = 1;
  }
  await tarayici.close();
}

main();
