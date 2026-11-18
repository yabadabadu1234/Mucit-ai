# TEK KART TASARIMI: LÜKSSÜZ, ESP32'SİZ, AVUÇ REDDİ ZARURETİ

**Tarih:** 2026-11-18
**Karar (padişahın):** Bütün lüksler terk edildi. Avuç reddi **zarurettir** (not defteri iddiasının şartı). ESP32 kullanılmaz; ekranı, dosya sistemini ve hafızayı süren **tek bir kart**, yalnız bu maksada göre kendimiz tarafından tasarlanır. Kamera ve telefon bağlantısı, çok fark etmezse olur; fark ederse olmaz.
**İşaretler:** [K] kaynaktan okundu · [H] benim hesabım · [?] yoklanmadı, tahmin.

## 1. Tek karta sığdıran yonga: Allwinner F1C100s / F1C200s

| Hüsûsiyet | Değer | Durum |
| :-- | :-- | :-- |
| Çekirdek | ARM9, 400 MHz | [K] |
| Hafıza | **Yonganın içinde** DDR1 (SiP): F1C100s 32 MB, F1C200s 64 MB | [K] |
| Paket | QFN-88, 10×10 mm | [K] |
| Ekran | RGB/TTL, **1280×720'ye kadar** (LCSC); bir forumda F1C100s için 800×480 yazıyor, tutarsız | [K, çelişkili] |
| Depolama | SPI NOR/NAND'den önyükleme, SD/TF, eMMC 4.41, USB OTG | [K] |
| Ses | 2 DAC, 1 ADC | [K] |
| Kamera | CSI ve TV-IN listede anılıyor, ayrıntı yok | [K, zayıf] |
| Yazılım | Melis veya Linux SDK; LicheePi Nano ve Widora kartları referans | [K] |
| Fiyat | F1C200S: LCSC'de 100+ adet **5,44 $** (arama özeti, sayfada kademe görünmedi); F1C100s için bir forum 1k adette 1,8–2,2 $ diyor | [K zayıf] / [?] |

**Neden bu yonga:** DDR'nin içerde olması, hızlı bellek yolunu kartta çizme derdini bitirir; kart sade kalır (katman sayısı veri sayfasından doğrulanmadı [?]). ESP32'de çerçeve belleği PSRAM'de olduğundan Wi-Fi yükünde titreme çıkıyordu (Sunton kartı); bu yongada panel doğrudan bir denetleyiciden sürülür [K, ESP32 tarafı].
**Sakıncası:** Allwinner belgeleri ve SDK'sı sınırlıdır, topluluk desteğine dayanılır; yongaların kullanım ömrü ve tedarik durumu bu araştırmada yoklanmadı [?].

## 2. Kartın blokları (kendi tasarımımız)

1. F1C200S + SPI NOR/NAND (yazılım) + microSD yuvası veya eMMC (notlar ve dosya sistemi).
2. 7" RGB panel için FPC konnektörü, ışık için yükseltici sürücü.
3. USB-C: şarj ve **bilgisayara bağlanma** (yazılımla USB depolama); ek donanım gerekmez.
4. Li-ion şarj devresi ve gerilim rayları (çekirdek, DDR, 3,3 V; değerler veri sayfasından [?]).
5. Dokunma/kalem modülü için I2C veya USB konnektörü (bkz. § 3).
6. İsteğe bağlı: kamera konnektörü (CSI/DVP).
7. Tuşlar. Wi-Fi ve Bluetooth **yok**; bu yüzden telefon bağlantısı kabloyla.

## 3. AVUÇ REDDİ: zarurettir ve yongadan bağımsızdır

Avuç reddini tek kart çözmez; **algılama katmanı** çözer. Üç yol:

| Yol | Nasıl çalışır | Kartımıza ne gelir | Bulunan |
| :-- | :-- | :-- | :-- |
| **A. EMR kalem sayısallaştırıcı** | Pilsiz kalem; yalnız kalemi görür, avuç hiç algılanmaz | Sensör ve denetleyici **satın alınan modüldür**, bizim çizeceğimiz bir devre değildir; kart onunla I2C/USB konuşur | Wacom özel ebatta modül yapıyor ("istek üzerine"); Huion ve Ugee hazır tabletleri var; **OEM fiyatı bulunamadı** |
| **B. Kapasitif panel + kalem/avuç ayırımı yapan denetleyici** | Temas alanı büyükse (satıcı beyanı: yaklaşık 5 cm² üstü) yok sayılır; kalem varlığı algılanınca özel algoritma | Panelin kendi denetleyicisi; kartımıza I2C | Parade TrueTouch ve PixArt PCT1336/1339 gibi denetleyicilerin "kalem + avuç reddi" desteği yazılı; **fiyat yok**; **GT911'in avuç reddi doğrulanmadı**; pasif kalemin sinyali dokunuşa göre 25 kat zayıf [K] |
| **C. Yalnız yazılım** | Büyük temas veya çoklu dokunuşu yazılımla yok saymak | Yazılım | Kalite güvencesi yok; "zaruret" iddiasını taşımaya yetmeyebilir [?] |

Tenkit: "Tablet bu sebeple makbul değil" hükmüne bir karşı veri: Tamindir, Casper PAD M10'un kalemini USI 2.0, 4096 basınç seviyesi, avuç içi algılamalı olarak yazıyor ve tablet 13.999 TL [K, ikincil]; 12,2" ve 7" değil. Yani avuç reddi hazır tabletlerde de var; asıl mesele o tabletin boyutu ve fiyatıdır.

## 4. Tek kartlı cihazın maliyet tahmini (tek cihaz, ~1.000 adet varsayımı)

| Kalem | $ | Durum |
| :-- | :-- | :-- |
| F1C200S | 2–5,4 | [K zayıf] |
| 7" 800×480 RGB panel (dokunmatikli) | 9–15 (100 adet) | [K]; dokunmatiksizin fiyatı bulunamadı |
| Güç (şarj, rayları, ışık sürücüsü) | 1–2 | [?] |
| Konnektörler, SPI flaş, SD yuvası, tuşlar | 1–2 | [?] |
| Pil | 2–4 | [?] |
| Kart üretimi (4 katlı, ~170×110 mm) | 2–3 | [?]; JLCPCB'de 100×100 mm 4 katlı 5 adet ≈ 32,90 $ (prototip fiyatı) |
| Montaj | 0,5–1 | [H]: eklem başına 0,0016 $ × ~200–300 eklem; kurulum 8–51 $ ayrı |
| Kasa | 2–5 | [?] |
| Kalem | 0,3–1 pasif; aktif/EMR kalem için fiyat yok | [?] |
| **Toplam** | **≈ 20–37 $** (kalem katmanı hariç) | [H] |

- 1 $ ≈ 45 TL varsayımıyla ≈ 900–1.700 TL; nakliye, gümrük ve KDV hariç.
- **Önceki yollarla kıyas:** hazır Android tablet 27–33 $, ESP32 hazır kartı 21–28 $ (pilsiz). Tek kart, ESP32 modülünün marjını (≈ 4–6 $) kaldırır ama **ekran, pil ve kasa** (toplamın büyük kısmı) aynı kalır. Bu yüzden tek kart **birkaç dolar** kazandırır, yarıya indirmez.

## 5. Tasarım yükü (üstümüze alacağımız)

- Şema, kart yerleşimi, birkaç prototip turu; her tur JLCPCB'de yaklaşık 100–200 $ (4 katlı 5 adet + standart montaj kurulumu) ve parça bedeli [H].
- Önyükleyici, ekran, dokunma, dosya sistemi, USB depolama, PDF çıkarma yazılımı (Linux veya kendi RTOS'umuz).
- Test ve uygunluk: Wi-Fi ve Bluetooth bulunmadığından telsiz sertifikası yükü azalır; EMC ve ürün güvenliği (pil) yine vardır [?]. Türkiye'de ithal veya üretilen cihaz için TSE ve diğer şartlar yoklanmadı.
- En büyük belirsizlik: algılama modülü (§ 3) ve panel fiyatı.

## 6. Doğrudan sorulacaklar (teklif)

1. **Wacom, Huion, Ugee, Hanvon:** 7" EMR sensör + denetleyici modülü, I2C/USB, adet fiyatı, kalem fiyatı.
2. **PCAP panel üreticileri (CDTech ve benzerleri):** 7" 800×480 RGB, dokunmatiksiz ve dokunmatikli fiyatı; kalem + avuç reddi denetleyicisi seçeneği.
3. **Makro PCB:** 4 katlı ~170×110 mm kart, 100/1.000 adet fiyatı ve dizgi var mı.
4. **Allwinner distribütörü:** F1C200S adet fiyatı ve ömür durumu.
5. **Kamera:** CSI/DVP modül fiyatı; fark yaratıyorsa çıkarılır.

## 7. Kaynaklar

- LCSC F1C200S: https://www.lcsc.com/product-detail/Microcontroller-Units-MCUs-MPUs-SOCs_Allwinner-Tech-F1C200S_C2879851.html
- LCSC F1C100S: https://lcsc.com/product-detail/Microcontrollers-MCU-MPU-SOC_Allwinner-Tech-F1C100S_C1511928.html
- Widora F1C200s: https://widora.cn/_export/xhtml/f1c200_chip
- Palm rejection (CDTech): https://www.cdtech-display.com/knowledges/how-does-palm-rejection-pcap-enable-hand-resting-stylus-use/
- Pasif kalem zorluğu: https://www.eenewseurope.com/en/passive-stylus-design-for-large-capacitive-touchscreens/
- Wacom EMR: http://www.wacom.jp/jp/customercare/download/catalogue/pdf/0507_EMR_Pen_Technology_E.pdf
- Casper PAD M10 kalem: https://www.tamindir.com/blog/not-tutmak-isteyen-ogrenciler-icin-en-iyi-kalemli-tabletler_112240/
- JLCPCB montaj: https://jlcpcb.com/help/article/pcb-assembly-price
