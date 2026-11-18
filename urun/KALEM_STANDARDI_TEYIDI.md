# KALEM STANDARDI TEYİDİ

**Tarih:** 2026-11-18
**Kayıt:** Kalem standardı bağımlı değişkendir; en düşük seviye kalem de desteklenir; kendi kalemimiz maliyete göre tayin edilebilir. **Pil için E-ink kullanılacak** (renkli E-ink, bkz. `HEDEF_HUSUSIYETLER.md`).

## 1. Teyit edilenler ve edilemeyenler

| Cihaz | Kalem standardı | Durum | Kaynak |
| :-- | :-- | :-- | :-- |
| Casper PAD M10 | **USI 2.0** (Turkcell ürün sayfası, Tamindir); Webtekno ve Hürriyet **MPP 2.0** yazıyor | **Çelişki.** Casper'ın kendi sayfası okunamadı (MediaMarkt 403). Satıcı sayfası ve Tamindir USI 2.0 diyor | [Turkcell M10](https://www.turkcell.com.tr/pasaj/bilgisayar-tablet/tabletler/android-tabletler/casper-pad-m10-8gb-ram128gb-tablet-ve-kalem), [Tamindir](https://www.tamindir.com/blog/not-tutmak-isteyen-ogrenciler-icin-en-iyi-kalemli-tabletler_112240/), [Webtekno](https://www.webtekno.com/casper-pad-m10-vs-casper-pad-h10-tabletleri-sizin-icin-karsilastirdik-h225712.html) |
| Casper M10 pil ve ekran | 8.000 mAh, 12,2" IPS, 2400×1600; kalem "tek şarjla günlerce" (Tamindir: 120 saat, 4096 seviye, ≤10 ms) | Satıcı sayfasından okundu; tablet için saat bilgisi yok ("gün boyu") | Turkcell M10 |
| Lenovo Tab Pen, Idea Tab | Lenovo'nun kalemleri **USI** tabanlı aktif kalem (USI Pen 2 = USI 2.0) | Genel bilgi doğrulandı; **hangi Idea Tab modeliyle hangi kalem geldiği doğrulanmadı** | [Lenovo USI Pen](https://lenovo.com/us/en/accessories-and-monitors/pens-and-supplies/pens/TAB-ACC-BO-Lenovo-USI-Pen/p/4X80Z49662) |
| BOOX, Bigme (E-ink) | **EMR (Wacom uyumlu)** pil gerektirmeyen kalem; BOOX kalemi 4096 seviye; Bigme'nin EMR kalemi bu kaynakta şarjlı görünüyor | Üçüncü taraf kalemlerin "Wacom EMR uyumlu" olarak satılması ve Bigme EMR kalemi kaynaklıdır; BOOX'un Wacom lisansı doğrudan teyit edilemedi | [Good e-Reader Bigme](https://goodereader.com/blog/?p=242690) |
| Samsung S Pen, Teclast M50T | Bu aramada **bulunamadı** | Doğrulanmadı | — |

## 2. Anlam

- LCD tabletlerde kalem **aktif** (pilli) tiptir; USI veya MPP. Ekranın içinde kalem için ayrı bir sayısallaştırıcı katman yoktur, bu yüzden standart seçimi ucuzdur.
- E-ink tabletlerde yazma çoğunlukla **EMR** (pilsiz kalem, ekranın arkasında algılayıcı katman) ile yapılıyor. Bu, cihaza algılayıcı katman maliyeti ekler ama kalem pilsiz ve ucuz olur.
- Padişahın "en düşük seviye kalem yeter" hükmüne göre ölçü, **basınç seviyesi ve gecikme değil**, yazının okunur çıkması ve palm rejection olacaktır. Hangi standardın maliyetçe en düşük olduğu, üretici fiyatları (`URETICILER.md`) çıkınca karar verilecektir.

## 3. Açık sual

- E-ink ekranlı rakiplerde (BOOX, Bigme, Penstar) kalem katmanının tedarikçisi ve tedarik fiyatı araştırılacak; renkli E-ink panelin (Kaleido 3, Gallery 3) panel maliyeti donanım dosyasında yer alacak.
