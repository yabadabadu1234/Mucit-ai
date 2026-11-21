# DEFTER D1: YERLİ TEDARİKLİ, KAMERALI, GÜNEŞLİ DİJİTAL NOT DEFTERİ

**Tarih:** 2026-11-21
**Durum:** Tasarım ve donanım kodları yazıldı; **fiziksel kart üretilmedi, hiçbir kod gerçek donanımda koşmadı.** Testler sanal bilgisayarda, cihaz benzetimleriyle yapıldı.
**İşaretler:** [K] kaynaktan okundu · [H] hesap · [T] tahmin, yoklanmadı.

> **DONDURULDU (2026-11-21, padişahın tecrübesine dayanarak):** Bu tasarımın eksikleri çok ve benzetim ile gerçek arasındaki fark hayal kırıklığı doğurabilir; § 8'deki doğrulanmamışlar bunu zaten gösteriyor. İthal parça gerektirdiği için de (yongalar, panel, şarj entegreleri) gümrük işi çıkarıyor. **Kart üretilmeyecek.** Yerine, gerçek donanımda ölçerek ilerleyen ve yalnız Türkiye'de satılan parçalarla yapılan prototip yolu: `../defter_d0/GERCEK_PROTOTIP.md`. Buradaki çekirdek kodlar (avuç reddi, sayfa, PDF) taşınabilir kaldı ve oraya aktarılacak.

## 1. Şartlar ve nasıl okundu

| Şart | Okuma | Sonuç |
| :-- | :-- | :-- |
| Malzeme tamamen yerli kaynaktan | Yerli **üretim** varsa yerli üretim; yoksa Türkiye'deki satıcıdan | Yongalar, ekran paneli, kamera sensörü ve bellek kartı için yerli üretici **bulunamadı** (aşağıda § 2). "Tamamen yerli üretim" bu ürün için mümkün değil. |
| En ucuz malzeme, fiyat/performans | Her işlev için en ucuz uygun parça | BOM § 6 |
| Bellek en az 32 GB | microSD, FAT32 | 32 GB'lık kart 31,9 GB ondalık eder (sınanan CSD: 62.333.952 blok = 31.914.983.424 bayt); "en az 32 GB" tam isteniyorsa **64 GB** kart (64,02 GB) seçilmeli. Kod her ikisini tanıyor. |
| Kamera | OV2640 (2 MP, JPEG çıkışlı) | Donanım ve güç/pin hesabı var; **kamera sürücüsü yazılmadı** (§ 8) |
| Lightning ile telefona bağlanma | Aşağıda § 4 | Cihazda Lightning fişi **yok**; Type-C ile iki yoldan bağlanır |
| Type-C ile şarj | USB-C, 5,1 kΩ CC dirençleri | Var |
| Güneş paneli | Yerli TOPCon hücre şeritleri, cihazın arkasında | Var; katkısı § 5'te |
| Ekran olabildiğince ince | 7" renkli LCD + kapasitif dokunmatik | Gövde 10,4 mm; E-ink ile 6,25 mm (ertelenen model) |
| Avuç reddi | Dokunma denetleyicisinin temas boyutu + yazılım | `avuc.c`; eşikler **fabrikada kalibre edilir** (§ 7) |

## 2. Yerli kaynak durumu (araştırma)

| Parça | Yerli üretim | Yerli satıcı |
| :-- | :-- | :-- |
| Kart (PCB) | **Var**: Makro PCB (İstanbul) | — |
| Kart dizgisi | **Var**: Milsan (Niğde), Acces (İstanbul) | — |
| Lityum iyon hücre | **Var**: Aspilsan INR18650A28, 2.800 mAh, Kayseri; küçük adet satış şartı bulunamadı [K] | — |
| Güneş hücresi | **Var**: CW Enerji (TOPCon, 1,2 GW) ve Kalyon PV; küçük özel ebat panel için teklif gerekir; hücre verimi yazılı bulunamadı | — |
| Ekran modülü/paneli | Vestel TV ekranı montajı var, **panel fabrikası doğrulanamadı** | Hazır modüller satılıyor, çıplak 7" RGB panel bulunamadı |
| Mikrodenetleyici | Yok (BİLGEM "Çakıl" var, ticari satışı yok) | Direnc.net STM32F429IET6 listeliyor; ZIT6 yoklanmadı |
| Kamera sensörü | Yok | Robotistan OV2640 kartı 730,12 TL (KDV dahil) [K] |
| Şarj ve güç entegreleri | Yok | Direnc.net'te TP4056, MCP73831 listeli; BQ24074 bulunamadı |
| SDRAM, dokunma denetleyicisi, microSD | Yok | Yoklanmadı |
| Kasa | Yerli enjeksiyon mümkün görünür; araştırılmadı [T] | — |

Yerli perakende, ithalat fiyatının çok üstünde: OV2640 için yerli kart 730 TL, ithalat tahmini 2–4 $.

## 3. Mimari (tek kart)

STM32F429ZIT6 (Cortex-M4F 180 MHz; LTDC 83 MHz'e kadar, FMC SDRAM, DCMI kamera, USB OTG [K: ST sayfası]).
- Ekran: 7" 800×480 RGB565, LTDC; çerçeve tamponu 2 × 768 KB, 8 MB SDRAM (1,5 MB kullanılır).
- Dokunma: GT911, I2C (0x5D); kamera SCCB aynı hatta (0x30).
- Depolama: microSD, SPI kipinde (4 tel + algılama); USB'ye bağlanınca kart ana bilgisayara devredilir.
- Güç: pil → yükselt-alçalt 3,3 V; kamera için 2,8 V ve 1,3 V; arka ışık yükselticisi; şarj BQ24074; USB-C ve güneş girişi Schottky ile VEYA'lanır.
- 96 pin kullanılır / 114 var (kontrol payı %10 sağlandı; **alternatif işlev eşlemesi CubeMX ile doğrulanmadı**).

## 4. Lightning

- **Apple'ın kuralı:** Lightning fişli yardımcı cihazın Apple MFi lisansı ve kimlik doğrulama yongası gerekir; lisanssız cihazlar yalnız sınırlı işlev alır [K: Apple Platform Security]. Bu, "yerli" ve "ucuz" hedeflerine aykırıdır; **cihaza Lightning fişi konmadı.**
- **Çözüm:** Cihaz USB depolama olarak görünür (FAT32, tek bölüm). Lightning'li iPhone (14 ve eski) için Apple'ın Lightning–USB Kamera Adaptörü ile; USB-C'li iPhone (15 ve yeni) doğrudan kabloyla bağlanır; sürücü Dosyalar uygulamasında görünür [K: Apple destek sayfaları]. Apple'ın şartı: tek bölüm, FAT/FAT32/exFAT.
- Telefon, USB'den 100 mA'e kadar verir kabul edildi: yapılandırma "kendinden beslemeli", istenen akım 100 mA; şarj akımı telefonda 100 mA'e sınırlanır, şarj adaptöründe 1,5 A (`usb_tanim.c`, sınandı). USB üretici kimliği (VID) geliştirme kimliğidir; ürün için kendi kimliği gerekir (ücreti yoklanmadı).

## 5. Güç ve güneş (benzetim sonuçları, [H])

Pil: 2.800 mAh × 3,6 V × 0,95 = **9,58 Wh**. Yükler tahmindir [T] ve ±%30 bandıyla hesaplanmıştır.

| Mod | Güç (W) | Süre (saat) |
| :-- | :-- | :-- |
| Yazma (ekran açık) | 1,32 (0,92–1,71) | 7,3 |
| Okuma | 1,04 | 9,2 |
| Kamera | 1,65 | 5,8 |
| USB aktarımı (ekran kapalı) | 0,48 | 20,1 |
| Bekleme | 0,005 | 1.915 |

- Günlük profil (3 sa yazma, 1 sa okuma, 6 dk kamera, 6 dk USB): **5,31 Wh/gün** → şarjsız **1,8 gün** (1,4–2,6).
- **24 saat sürekli ekran açık** 31,6 Wh ister; pil 9,6 Wh. LCD ile bu hedef tutmaz (E-ink ertelendiği için güncellenebilir kabul edilmişti).
- Güneş: 9 şerit seri, arka yüzün %85'i, %22 hücre verimi [T] → STC tepe **3,5 W**. Şarj yolu iki biçimde hesaplandı: BQ24074'ün giriş gerilimi düşürmesi (DPM) ile ve ayrı MPPT şarj ile.

| Senaryo | W/m² [T] | DPM (W) | MPPT (W) |
| :-- | :-- | :-- | :-- |
| Açık hava, güneş elde | 700 | 1,67 | 2,17 |
| Açık hava, bulutlu | 150 | 0,36 | 0,43 |
| Pencere kenarı | 40 | 0,095 | 0,108 |
| Oda ışığı 500 lüks | 4,5 | 0,010 | 0,011 |

Günlük (1 sa güneş, 0,5 sa bulutlu, 3 sa pencere, 6 sa oda): DPM 2,19 Wh (tüketimin %41'i), MPPT 2,77 Wh (%52). **Bu toplamın 1,67 Wh'i güneşte geçen tek saattendir; pencere ve oda toplamı günde yalnız yaklaşık 0,35 Wh (%7).** Güneş, doğrudan güneşe çıkan kullanıcı için anlamlı; masada duran cihaz için küçük bir katkı. Verim %20/24 için sonuçlar `sonuclar/gunes.txt`te.

## 6. Kalınlık ve maliyet

**Kalınlık [K/T karışık, sonuçlar/kalinlik.txt]:** ekran + dokunmatik 5,25 mm [K], boşluk 0,3, kart 1,0, en yüksek bileşen (microSD soketi) 1,85, güneş laminatı 0,8, kabuk 1,2 → **gövde 10,4 mm**. Yerli hücre silindirik (18,4 mm) olduğundan pil **sırtta** (defter sırtı) durur: sırt 19,6 mm. E-ink 7,5" (1,1 mm [K]) ile gövde 6,25 mm olur.

**Maliyet (malzeme, 22 kalem, [T] ağırlıklı):** **46,3 – 81,6 $** ≈ 2.084 – 3.672 TL (1 $ = 45 TL varsayımı), nakliye, gümrük, KDV, tasarım ve sertifika hariç.
- Yerli üretim kalemleri: 11,5–24,0 $; yerli satıcıdan ithal: 13,5–19,0 $; yerli kaynak bulunamayan: 21,3–38,6 $.
- Çıkarılabilir: kamera 2–4 $ (yerli perakendede 730 TL), güneş 3,1–6,3 $.
- Yani 1.000 TL hedefinin **2–3,5 katı**. Büyük kalemler: mikrodenetleyici 11,5–15 $ (Farnell Türkiye F429IIT6: 10,32–13,55 €), panel 9–15 $, kart ve kasa. Daha ucuz yonga (F1C200S, LCSC 5,44 $ [K zayıf]) yerli satıcıda bulunamadı.

## 7. Donanım kodları ve testler (`yazilim/`)

| Modül | İşi | Sınama |
| :-- | :-- | :-- |
| `gt911.c` | Dokunma denetleyicisi, çok noktalı okuma, kare onayı | 28 kontrol: sürücü, hatalar, 5 nokta sınırı, ara kesinti |
| `avuc.c` | **Avuç reddi:** temas boyutuna göre kalem/parmak/avuç ayrımı, yumruk gölgesi, kalem önceliği, 30 ms karar penceresi ve tamponlama | 75 kontrol + 20.000 karelik rastgele özellik sınaması: avuç boyutuna ulaşmış izden **hiç nokta çıkmadı**, aynı anda iki kalem çıkmadı |
| `sdspi.c` | microSD SPI sürücüsü: başlatma, CSD'den kapasite (32 ve 64 GB), okuma/yazma, hata kodları | 52 kontrol: HC/SC/sürüm 1 kart, hata ve zaman aşımı, kart yok, 61 milyon blokluk adres |
| `msc_scsi.c` | USB depolama komut katmanı, ortam devri (yazılım ↔ ana bilgisayar) | 65 kontrol: SCSI cevapları, algı (sense) kodları, yazma koruması |
| `usb_tanim.c` | Cihaz ve yapılandırma tanımları, şarj akım sınırı | sınır tablosu, tanım uzunlukları |
| `guc_yonetimi.c` | Pil yüzdesi, ekran kararma/uyku, uyarı/kritik eşiği, USB ve şarj | 3.265 kontrol; boşalma benzetimi: kritik kayıt **tam bir kez**, kapanıştan önce notlar kaydedilir |
| `sayfa.c`, `pdf.c` | Strok kaydı, bozulma denetimli kayıt (CRC32), PDF üretimi, JPEG gömme | 22.047 kontrol; her tek bayt bozulması ve her kesilme reddedildi; PDF'yi pypdf (katı kip), xref denetimi ve pdftoppm çizimi doğruladı |
| `ltdc_zamanlama.c` | LTDC kayıt değerleri, PLLSAI bölenleri, tarama bant genişliği | kayıtlar elle hesapla eşleşti; 33,3 MHz'de 60 Hz; LTDC 66,6 MB/s, SDRAM tepe 180 MB/s |

- Eşikler koda sabit yazılmadı: `avuc_kalibre_et`, kalem ve avuç örneklerinden ölçer; iki küme çakışırsa **reddeder**.
- Devre denetimi (`simulasyon/erc.py`) 25 kontrol yapar ve kendi başarısızlığını da gösterir: 10 bozuk devre testi (aşırı yük, yanlış gerilim, pin taşması, çakışan I2C adresi, eksik CC direnci vb.) reddedildi. Denetim **gerçek bir kusur yakaladı**: kamera giriş-çıkışı 3,3 V'u aşabiliyordu; kamera hatları 2,8 V'a alındı ve seviye çevirici eklendi.
- ARM derlemesi (Cortex-M4, -Os, bağlama yapılmadı): 8.276 bayt kod, 0 bayt veri.
- Koşturma: `cd yazilim && make test`, `make hedef`; `cd simulasyon && python3 -m unittest test_simulasyon`.

## 8. Yapılmayanlar ve doğrulanmamışlar (açıkça)

1. **STM32 bağlayıcı katmanı** (I2C, SPI, LTDC, DCMI, USB yazmaçları) yazılmadı; kodlar `hal.h` arkasındadır.
2. **Kamera (OV2640) sürücüsü ve başlatma tablosu** yazılmadı.
3. GT911, SD kart ve SCSI **cihaz benzetimlerini ben kurdum**: testler kodun benim cihaz bilgime uyduğunu gösterir, gerçek cihaza uyduğunu **göstermez**. GT911'in temas boyutu alanını (bayt 5–6) ve yazmaç adreslerini hafızadan yazdım; veri sayfasından doğrulanmadı. Avuç ve kalem boyutlarının gerçekten ayrışıp ayrışmadığı ancak donanımda ölçülür.
4. Panel zamanlaması (AT070TN92 tipik değerleri) ve PLLSAI sınırları veri sayfasından teyit edilmedi [T].
5. Pin alternatif işlev eşlemesi, kart yerleşimi, şema ve devre kartı çizimi **yok**; yalnız blok düzeyinde devre denetimi var.
6. Güç, güneş, pil ve ekran tüketimi değerleri tahmindir; benzetim bandı ±%30.
7. Güneş panelinin yerli üreticisi küçük ebat için teyit edilmedi; Aspilsan hücresinin satış şartı bilinmiyor.
8. Sertifikalar (EMC, pil güvenliği, USB kimliği, Türkiye şartları) yoklanmadı.

## 9. Kararınızı bekleyenler

- **1.000 TL hedefi** bu tasarımla tutmuyor (2–3,5 kat). Hangisi gevşetilecek: kamera, güneş paneli, yerli satıcı şartı (ithal parça), yoksa ucuz yonga (F1C200S) ve Linux?
- Kart: 32 GB mı 64 GB mı?
- Yerli üretim şartı **tamamen** ise, yongalar ve panel için bir çıkış yok; bu şart yerli tedarik olarak mı okunacak?
