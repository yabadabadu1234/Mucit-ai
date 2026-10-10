# MİKRO MÜKELLEFİYET MALİ ETKİ MODELİ

Dosyalar: `model.py` (hesap), `analiz.py` (senaryo, tornado, Monte Carlo, varyant), `grafik.py`, `xlsx_uret.py`, `MIKRO_MUKELLEF_MALI_MODEL.xlsx` (canlı formüllü Excel), `sonuc.json`. Grafikler `../GORSELLER/model_*.png`.

**Doğrulama.** Excel'deki formüller (Girdiler, Hesap, Sonuc sayfaları) bağımsız bir formül hesaplayıcısıyla (`formulas` kütüphanesi) çalıştırılıp Python modelinin Orta senaryo çıktılarıyla karşılaştırıldı; 14 kalemde göreli fark 10⁻¹⁵ mertebesindedir. Excel dosyası değerleri önbelleğe almadan kaydedilmiştir; Excel açıldığında kendisi hesaplar. Monte Carlo ve tornado Python'dadır; Excel'de statik değer olarak `Senaryolar_Python` sayfasındadır.

## 1. Yapı

1. **Nüfus.** Katılımcı sayısı $N$ (kararlı durumda); yıllık hasılat $H$ log-normal (medyan $m$ asgari ücret, yayılım $\sigma$), 0,1 ile 24 asgari ücret arasına kırpılmış, 60 geometrik dilimle ayrıklaştırılmış.
2. **Üç tür katılımcı.** (a) yeni: daha önce hiç vergi ve prim ödemeyen; (b) halen kayıtlı ($s$, rejime geçen): eski rejimde gelir vergisi (kâr marjı × $H$ üzerinden tarife) ve 4/b primi ödüyordu; teklif Madde 1 (p) ile bu kişilerin primi **sürer** (`prim_devam`=1), yani kaybedilen yalnız vergi farkıdır; (c) ücretli ek gelir ($u$): eski rejimde marjinal oranla ve kısmî uyumla vergi ödüyordu.
3. **Yeni rejim geliri.** $T(H)$ = GVK m.103 genel tarifesi (190.000 TL %15; 400.000'e kadar %20; 1.000.000'a kadar %27; 5.300.000'e kadar %35; üstü %40) uygulanan safi matrah $0{,}7\,H$ (götürü gider %30).
4. **Giderler.** BES aktarımı (tevkifatın %3'ü, vazgeçme payı kadar azalır) ve Devlet katkısı (%20); 90 günlük MYÖ primi hibesi ($H \geq 12$ asgari ücret ve çakışmasız olanlar için $3 \times W \times 0{,}21$); donanım KDV mahsubu (üst sınır tevkifatın %50'si); KGF (kullanım × kefalet × temerrüt × (1 − kurtarma)); PTT UETS; BT tek seferlik ve yıllık; itiraz; denetim.
5. **Sahte fatura.** Kurumsal akıştaki sahte pay $\varphi$, önlem etkinliği kadar azalır; kayıp = hacim × (kurumlar vergisi oranı − etkin tevkifat oranı).
6. **Zaman.** Beş yıl; katılım rampası %25, %55, %80, %100, %100; 1. yılda tek seferlik BT ve PTT; reel iskonto %5; sabit 2026 TL.
7. **Çıktılar.** Yıl yıl net etki, 5 yıllık bugünkü değer, kırılma noktası $s^*$, politika varyantları, tornado, Monte Carlo (4000 deneme, sabit tohum 20261010).

## 2. Girdi tablosu ve durumu

Durum sütunu: **M** mevzuattan okundu, **İ** ikincil kaynak, **H** varsayım (ölçülmemiş, veriyle doldurulacak).

| Girdi | Kötümser | Orta | İyimser | Durum |
| :-- | :-- | :-- | :-- | :-- |
| Medyan hasılat (asgari ücret katı) | 4.0 | 5.0 | 6.0 | H |
| Katılımcı sayısı N | 150000 | 350000 | 700000 | H |
| Halen kayıtlı olup geçenlerin payı s | 0.30 | 0.15 | 0.05 | H |
| Halen kayıtlı olanın prim devamı (1 = sürer) | 1 | 1 | 1 | Teklif Madde 1 (p) |
| Ücretli ek gelir payı u | 0.25 | 0.2 | 0.15 | H |
| Sahte fatura payı φ | 0.02 | 0.01 | 0.005 | H |
| Önlem etkinliği | 0.3 | 0.5 | 0.7 | H |
| 90 gün primi hak edenler | 0.5 | 0.35 | 0.2 | H |
| BES vazgeçme payı | 0.2 | 0.35 | 0.5 | H |
| KGF kullanım oranı | 0.08 | 0.05 | 0.03 | H |
| KGF temerrüt oranı | 0.15 | 0.1 | 0.06 | H |
| Donanım alan payı | 0.5 | 0.4 | 0.3 | H |
| Brüt asgari ücret 2026 | 33.030 | 33.030 | 33.030 | İ (birden çok kaynakta tutarlı) |
| Tarife eşikleri ve oranlar | 103. madde | 103. madde | 103. madde | M |
| MYÖ prim oranı %21, 4/b toplam %35,75 | | | | M (5510 m.81) |
| Devlet katkısı %20 | | | | İ (4632 Ek 1 dipnotu M; 10811 sayılı Karar metni okunmadı) |
| Götürü gider %30, BES %3, hibe prim 90 gün, donanım mahsup tavanı %50 | | | | Teklif hükmü |
| Eski rejim kâr marjı, eski prim ödeme oranı, ücretli uyumu, ücretli marjinal oranı, kurumsal pay, KGF kurtarma, PTT birim, BT giderleri, itiraz oranı ve birim gideri, denetim oranı | bkz. xlsx Girdiler | | | H |


## 3. Sonuçlar (4. yıl, milyar TL)

**Tasarım kararı.** İlk sürüm (halen kayıtlı olanlar prim ödemesini bırakarak girebilirken, s = %45/%25/%10) net etkiyi olumsuz buldu: Orta −5,6. İlk çare 24 aylık giriş kapısıydı (Orta +3,4); kapı dürüst esnafı dışladığı için bırakıldı. Seçilen çare **sigortalılığın sürekliliği** (Madde 1 (p)): giriş serbest, halen kayıtlı olanın 4/b primi sürer. Baskın yutulma kalemi hibe değil 4/b primi kaybıdır; prim sürünce net etki katılım payından bağımsız pozitif kalır.

| Kalem | Kötümser | Orta | İyimser |
| :-- | :-- | :-- | :-- |
| Katılımcı (kişi) | 150.000 | 350.000 | 700.000 |
| Halen kayıtlı olup geçenlerin payı s | %30 | %15 | %5 |
| Brüt tevkifat | 2.93 | 8.18 | 18.74 |
| BES ve Devlet katkısı | -0.08 | -0.19 | -0.34 |
| 90 gün prim hibesi (tüm uygun kişiler; eskiler çakışma kuralıyla düşer, yukarı yönlü) | -0.15 | -0.36 | -0.53 |
| Donanım KDV mahsubu | -0.32 | -0.63 | -0.97 |
| Yutulma: vergi | -1.05 | -1.82 | -2.30 |
| Yutulma: SGK primi (prim sürer) | 0.00 | 0.00 | 0.00 |
| KGF | -0.11 | -0.13 | -0.10 |
| Sahte fatura | -0.04 | -0.03 | -0.02 |
| BT işletme, itiraz, denetim | -0.09 | -0.09 | -0.30 |
| **Net (Hazine + SGK)** | **+1.08** | **+4.86** | **+14.19** |
| 5 yıllık bugünkü değer | +2.99 | +14.45 | +42.73 |

Herkes geçse (s = %100, ücretli ek gelir payı 0): Kötümser +0.11, Orta +1.08, İyimser +3.71; kırılma noktası **yoktur**. Monte Carlo (4000 deneme; s ~ beta(2,6), ortalama %25): 4. yıl net P5 1.4, P50 4.2, P95 11.3 milyar TL; net > 0 olasılığı %99,9 (prim sürekliliğinin tuttuğu varsayımına koşullu).

## 4. Varyantlar (Orta, 4. yıl net, milyar TL)

| Varyant | Net |
| :-- | :-- |
| G0 Seçilen: kapısız, halen kayıtlı olanın 4/b primi sürer (s=0,15) | 4.86 |
| G1 Prim sürekliliği olmasaydı (kapısız, s=0,15) | -1.09 |
| G2 Önceki karar: 24 ay giriş kapısı (s=0,05, prim sürekliliği yok) | 3.44 |
| G3 Harici öneri: düz %15 (%5 prim payı), hibe yok, kapısız (s=0,15) | 1.82 |
| G4 Seçilen, herkes geçse (s=1,00) | 1.08 |
| G5 Seçilen + 90 gün prim hibesi yok | 5.22 |
| G6 Seçilen + donanım KDV mahsubu yok | 5.49 |
| G7 Seçilen + (e) bendi yok: düz %10,5 | 4.29 |
| G8 Seçilen + götürü gider %25 | 5.52 |

## 5. Ne anlama geliyor

1. **Net etki, prim yükümlülüğü sürdüğü sürece pozitif ve s'ye dayanıklıdır;** Kötümserde marj ince (+0,11 ile +1,08).
2. Pozitifliği iddia ederken "prim sürekliliği hukuken tutarsa" şartı **her yerde** yazılmalıdır. Sigortalılığı sona erdirerek primden kurtulma, kapatıp yeniden açma ve aile bireyi adına tescil yolları modelde yoktur.
3. Bedel: eski–yeni prim asimetrisi; halen kayıtlı olanın vergisi artabilir (T, eski vergiden yüksek çıkabilir), bu yüzden geçiş cazibesi sınırlıdır.
4. Kademeli oran (e) +0,6 milyar TL katkı yapar ve oran arbitrajını kapatır. Götürü gideri %25'e çekmek +0,7 daha getirir ama ana mesajı değiştirir; uygulanmadı.
5. Geri akış karinesi (r) ve kimlik tekliği (s) gibi önlemlerin etkisi yalnız sahte fatura kalemi üzerinden yakalanır; bu kalem küçüktür.

## 6. Veri talebi (modelin ölçülmemiş girdilerini kapatacak)

| Girdi | Kurum | İstenen |
| :-- | :-- | :-- |
| s (kapı sızıntısı), eski vergi ve prim | SGK, GİB | Son 24 ayda 4/b sigortalısı veya gelir vergisi mükellefi olup tescil başvurusu yapabilecek kişi sayısı; hizmet ve fikir sektörü hasılat dağılımı; prim tahsilat oranı |
| N, u | TÜİK, GİB | Serbest çalışan ve ek iş yapan ücretli sayısı; 20/B kapsamındaki mükellef sayısı ve hasılatı |
| φ | GİB, MASAK | Hizmet faturalarında sahte fatura oranı |
| BES vazgeçme | EGM | Otomatik katılımda vazgeçme oranı |
| KGF | KGF, Hazine | Mikro ölçek faizsiz finansman temerrüt oranı |
| PTT, BT | PTT, GİB, BDDK | UETS birim gideri; portal ve banka entegrasyon maliyeti |

## Ek: seçeneklerin karşılaştırması (10/10/2026; Orta, 4. yıl net, milyar TL, genel devlet)

Harici bir metin üç yol önerdi (düz %15 birleşik tevkifat; hibeyi yalnız gençlere; sıfır hibe) ve "s=%100'de bile kesin kâr" iddia etti. Kapısız tasarımlar için tablo (prim tahsilat oranı π: 0,8 modelin varsayımı, 0,375 harici metnin iddiası, **yoklanmadı**):

| Tasarım (kapısız) | s=%5 | s=%30 | s=%100 | Kırılma s* (π=0,375 / π=0,8) |
| :-- | :-- | :-- | :-- | :-- |
| Mevcut metin, prim kalkıyor | +3,44 | −7,88 | −38,60 | %23,6 / %12,6 |
| Harici Yol 1: düz %15 (%5 prim payı), hibe yok | +6,35 | −4,97 | −35,69 | %35,6 / %19,0 |
| Harici Yol 2: hibe yalnız genç | +3,71 | −7,61 | −38,33 | %24,7 / %13,2 |
| Harici Yol 3: sıfır hibe, sıfır KDV mahsubu | +4,43 | −6,89 | −37,61 | %27,6 / %14,8 |
| Eşit prim payı %12 + hibe yok | +12,48 | +1,16 | −29,56 | %60,9 / %32,6 |
| **Seçilen: kapısız, halen kayıtlı olanın 4/b primi sürer** | +5,42 | +4,02 | +1,08 | yok / yok |

Sonuç: "s=%100'de bile kesin kâr" iddiası, prim kaybını (yutulma) hesaba katmadığı için **tutmuyor**; hibeyi kesmek açığı kapatmıyor, çünkü açığın baskın kalemi 4/b primi kaybıdır (Orta: prim −1,98, hibe −0,36). Prim yükümlülüğünü sürdüren tasarım, kapısız olup her $s$ için pozitif kalan **tek** tasarımdır. Prim, gelire oranlı bir tavanla indirilirse (halen kayıtlı olana kısmî rahatlama) yeniden s'ye bağımlı hâle gelir (%30·H tavanıyla s=%30'da −2,6). Bu varyantlar metne **işlenmedi.**
