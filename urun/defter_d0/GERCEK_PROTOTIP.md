# GERÇEK PROTOTİP: YALNIZ TÜRKİYE'DE SATILAN PARÇALAR, ÖNCE ÖLÇ SONRA TASARLA

**Tarih:** 2026-11-21
**Karar (padişahın):** Gümrükle uğraştıracak bütün ürünler değişir; Deneyap kartları kullanılır; benzetimin gerçeği vermeyeceği, özel kartın eksiklerinin çok olduğu tecrübesi esas alınır.
**Mânâ:** Özel kart tasarımı (`defter_d1`) **dondurulmuştur**. Evvelâ gerçek parçalarla, gerçek ölçümle, hangi şeylerin çalıştığı bulunur; yeni bir kart ancak ölçümden sonra düşünülür.
**İşaretler:** [K] 2026-11-21'de sayfadan okundu · [T] tahmin · "stok yok" = sayfa stokta göstermedi.

## 1. Yerli satıcıdan alınabilenler

| Parça | Ne | Fiyat (TL) | Stok | Kaynak |
| :-- | :-- | :-- | :-- | :-- |
| **Deneyap Kart 1A v2 (Type-C)** | ESP32-S3-WROOM-1, 240 MHz çift çekirdek, 4 MB flaş, **8 MB PSRAM**, Li-Po şarj devresi ve konnektörü, **microSD soketi** (D16–D19), **kamera FPC**'si, Type-C, 23 GPIO, 3,3 V | 591 (resmî mağaza); Robotistan 590,99 KDV dahil | Resmî mağazada sepete eklenebilir; Robolink'te tükendi | [deneyapkart.org](https://deneyapkart.org/en/docs/deneyap-kart-1a-v2), [mağaza](https://magaza.deneyapkart.org/en/product/detail/deneyap-kart-1a-v2-type-c) |
| **Deneyap Kamera** | OV2640, 2 MP, 1600×1200 @ 15 fps, sabit odak 60 cm–sonsuz, 66°, 24 pin FFC | 279 (resmî); Robotistan 327,60 KDV dahil | Robotistan'da yok; resmîde belirsiz | [belge](https://docs.deneyapkart.org/en/Moduls/Deneyap-Camera/Technical-Specifications) |
| **Deneyap Li-Polymer batarya** | kapasitesi sayfadan okunamadı | 420 | Sepete eklenebilir | resmî mağaza |
| **microSD** | 32 GB Kioxia/SanDisk yaklaşık 690–739; 64 GB Kioxia 1.085 | — | — | Trendyol, Hepsiburada, karşılaştırma sayfaları |
| **Güneş paneli 6 V 500 mA (175×110 mm)** | yaklaşık 3 W; cihaz sırtının ebadına yakın | 436,70 KDV dahil | stok yazılı değil | [Robotistan](https://robotistan.com/solar-panel-6v-500ma-175x110mm) |
| **6 V MPPT güneş şarj modülü** | panel → pil | fiyat okunmadı | — | [Robotistan](https://www.robotistan.com/6v-mppt-solar-sarj-modulu) |
| **7" ESP32-S3 dokunmatik HMI** | 800×480, kapasitif, ESP32-S3-WROOM-1-N4R8 (8 MB PSRAM), microSD, Type-C, 4 Dupont kablosu | 3.538,78 KDV dahil | **yok** | [Robotistan](https://www.robotistan.com/70-inch-esp32-hmi-tft-lcd-touch-display-enclosed-en) |
| 7" ESP32-S3 TN dokunmatik | özellikleri yazılı değil | 3.388,10 KDV dahil | **yok** | [Robotistan](https://www.robotistan.com/esp32-s3-7-inch-tn-touch-display-en) |
| Deneyap OLED ekran | küçük OLED | 292 | — | resmî mağaza |

Robolink Deneyap kategorisinin sekiz ürünü de tükenmiş görünüyor [K]. Fiyat ve stok değişir; sipariş vermeden önce sayfa yeniden okunacak.

## 2. Deneyap neyi yapar, neyi yapmaz

**Yapar:** kamera, microSD, Li-Po şarj ve Type-C **tek kartta hazır**: benim kendi kartımda çizip doğrulayamayacağım şeylerin çoğu burada fabrikasında kurulmuş ve topluluk tarafından denenmiştir.
**Yapmaz:**
- **7" ekranı süremez.** Kartta ekran konnektörü yok; paralel RGB panel için pin sayısı ve eşlemesi doğrulanmadı; 23 GPIO'nun bir kısmı SD, düğme ve LED'e ayrılmış [K: belge, RGB sürüşü "doğrulanmadı"].
- Büyük ekran modülü Deneyap ailesinde **yok**; yalnız küçük OLED var.
- Güneş girişi yok; ayrı MPPT modülü gerekir.
- **Type-C portunun USB depolama (MSC) yapıp yapamayacağı kesin değil:** ESP32-S3'te varsayılan olarak Type-C bir USB-Serial-JTAG hattıdır; TinyUSB depolama için USB-OTG denetleyicisi gerekir [K: Espressif belgesi]. Deneyap şemasında hangisine bağlı olduğu bulunamadı. **Telefona bağlanma bu bilgiye bağlı; ilk deney bu.**
- Kart Espressif yongası taşır: yonga üretimi yerli değildir; Deneyap kartının üretim yeri doğrulanamadı.

## 3. İki ayrı tezgâh prototipi (birleştirmeden)

Tek bir birleşik cihaz yerine iki ayrı tezgâh, çünkü aynı kartla 7" ekranı ve kamerayı birleştirmek şu an mümkün görünmüyor ve her biri farklı bir bilinmeyeni çözüyor.

| Tezgâh | Parçalar | Maliyet (TL, KDV dahil, [K]) | Cevapladığı soru |
| :-- | :-- | :-- | :-- |
| **P1: depolama, kamera, güç, güneş, telefon** | Deneyap Kart 1A v2 (591) + Kamera (279–328) + Li-Po (420) + microSD 64 GB (1.085) + 6 V 500 mA panel (437) + MPPT modülü (fiyat okunmadı) | ≈ 2.810–2.860 + MPPT | USB'den telefona disk, kamera, SD güvenilirliği, gerçek akım, güneşten gerçek şarj |
| **P2: ekran, dokunma, avuç reddi, yazı** | 7" ESP32-S3 HMI (3.538,78; **şu an stokta yok**) + microSD (aynı kart) | ≈ 3.540 | Avuç ve kalem boyutu gerçekten ayrışıyor mu, yazı gecikmesi, ekran kalınlığı |

Toplam tezgâh ≈ 6.400 TL ve MPPT. Yedek: P2 için stok gelmezse 7" TN modeli (3.388,10) veya başka stoklu 7" ESP32-S3 dokunmatik aranır.

## 4. Deney listesi (her birinin geçme ölçüsü, kararı ve başarısızlık hâli)

| # | Deney (tezgâh) | Geçme ölçüsü | Neyi karara bağlar | Geçmezse |
| :-- | :-- | :-- | :-- | :-- |
| D1 | **Type-C'den USB depolama (P1):** Deneyap'tan SD kartı bilgisayara ve iPhone'a (Lightning adaptörü ve USB-C kablosu) disk olarak göstermek | Dosyalar uygulamasında ve bilgisayarda görünür; 100 MB yazma, SHA-256 eşleşir | Telefona bağlanma yolu | Kart okuyucu ve Wi-Fi aktarımı |
| D2 | SD güvenilirliği (P1): 10.000 küçük dosya, 1 GB sürekli yazma, 100 ani güç kesintisi | 0 bozuk dosya sistemi, 0 kayıp kayıtlı sayfa | Kayıt mimarisi | Yazma sıklığı ve yedekleme düzeni |
| D3 | Kamera (P1): 1600×1200 JPEG çekip SD'ye yazmak | 10 çekimde 0 hata; her çekim süresi ölçülür | Kamera özelliği | Daha düşük çözünürlük |
| D4 | **Gerçek akım ölçümü** (P1, P2): bekleme, yazma, kamera, USB (bir USB ölçer veya ampermetre) | Ölçülen değerler `defter_d1/parametreler.json`daki tahminlerle yan yana yazılır | Pil süresi (benzetimin ne kadar yanıldığı) | — |
| D5 | **Güneşten gerçek şarj** (P1): güneşte, pencerede, odada akım | Ölçülen Wh/gün; benzetimin 2,2 Wh tahminiyle kıyas | Güneşin değeri | Güneş çıkarılır |
| D6 | **Avuç reddi** (P2): dokunma denetleyicisinin ham temas boyutu; avuç, yumruk, parmak, pasif kalem; `avuc_kalibre_et` | Kalem ve avuç boyutları ayrışır (kalibrasyon kabul eder); 200 avuçlu yazma denemesinde 0 yanlış çizgi | **Avuç reddinin mümkün olup olmadığı** | Aktif kalem veya EMR katmanı |
| D7 | Yazı gecikmesi (P2): kalem ucu ile çizgi arası ölçülür | Hedefi padişah koyar; ölçü yazılır | Ekran seçimi | — |
| D8 | PDF (P1 veya P2): cihazda üretilen PDF telefonda açılır | Açılır, çizgiler doğru yerde | PDF özelliği | — |

Her deneyin ölçüsü ve sonucu `urun/defter_d0/SONUCLAR.md`ye yazılır (henüz yok); benzetimle fark **sayıyla** yazılır.

## 5. Kodun durumu

- `defter_d1/yazilim/` içindeki çekirdek kodlar (`avuc.c`, `sayfa.c`, `pdf.c`, `guc_yonetimi.c`, `msc_scsi.c`) donanımdan bağımsızdır ve **ESP32-S3'e taşınabilir**; ancak ESP32 bağlayıcı katmanı yazılmadı ve gerçek donanımda hiç koşmadı.
- SD sürücüsü ESP32'de yerleşik SD kütüphanesiyle değişebilir; `sdspi.c` yalnız bir yedektir.
- Doğrulanmamış varsayımlar (GT911 boyut alanı vb.) D6 ile doğrulanacak; HMI'nin dokunma denetleyicisi de sayfadan **belli değil**.

## 6. Hedefler üzerindeki etkisi

- **1.000 TL hedefi bu yolla karşılanmaz:** yerli perakende fiyatıyla yalnız 7" ekran modülü 3.400–3.540 TL. Bu prototip fiyat değil, **doğruluk** içindir; seri ürün fiyatı ancak ölçümden sonra, imalat teklifleriyle düşünülür.
- 7" HMI'nin kendi ESP32-S3'ü var; son ürün için Deneyap kartına ihtiyaç kalmayabilir (kamera ayrı sorun). Bu karar D1–D6'dan sonra.
- Güneş paneli ve kamera bu aşamada **ayrı ölçülür**, ürüne zorla katılmaz.

## 7. Henüz yoklanmayanlar

- Deneyap Li-Po bataryanın kapasitesi, MPPT modülünün fiyatı, Deneyap kamera stoğu ve resmî mağazada Deneyap Kamera ile Kart'ın gerçekten sepete eklenip eklenmediği.
- HMI'nin dokunma denetleyicisi ve temas boyutu raporlayıp raporlamadığı; HMI'nin serbest GPIO ve pil bağlantısı.
- Deneyap Kart Type-C'nin hangi USB hattına bağlı olduğu (şema).
- Gümrüksüzlük yalnız **Türkiye'deki satıcıdan** alma anlamındadır; Espressif yongaları ve ekran panelleri yine ithaldir, ama gümrüğü satıcı yapar.
