# İLK MODEL: EN UCUZ ~7" LCD CİHAZ; KENDİ KARTIMIZ MI, HAZIR PARÇA MI?

**Tarih:** 2026-11-18
**Karar (padişahın):** E-ink sonraki modellere ertelendi. İlk model, **7 inça yakın en ucuz** cihaz.
**Para birimi:** Fiyatlar dolar (liste fiyatı, doğrulanmış teklif değil). TL'ye çevirmedim; 1 $ ≈ 0,9 € ve 1 € = 50 TL (padişahın kuru) varsayımıyla 1 $ yaklaşık 45 TL eder, bu yalnız kaba büyüklük içindir.
**İşaretler:** [K] kaynaktan okundu · [H] benim hesabım · [?] yoklanmadı, tahmin.

## 1. En ucuz ~7" ekran

| Ekran | Fiyat | Not |
| :-- | :-- | :-- |
| 7" IPS kapasitif dokunmatik (Hu Nan Future) | 3,5–6,5 $, asgarî 1 adet [K] | İlan güvenilir görünmüyor; çözünürlük ve arayüz yazılı değil |
| 7" 800×480, GT911 dokunmatik (Shenzhen Ansilon) | 9–15 $, asgarî 100 adet [K] | RGB arayüz, MCU'ya uygun |
| 7" 1024×600 IPS, RGB, dokunmatik (Wu He Tian Cheng, W070P50H1RI-Q53BC) | 18 $ (100–499), 15 $ (500–999), **12 $ (1.000+)** [K] | Arayüz RGB 50 pin |
| 7" 1024×600 IPS, dokunmatik (Shenzhen Reaper) | 10 $, asgarî 5 adet [K] | Arayüz yazılı değil |

Arayüz uyarısı: RGB paneli ESP32-S3 gibi mikrodenetleyici sürer; Android işlemcileri MIPI veya LVDS panel ister. Paneller birbirinin yerine takılmaz.

## 2. Üç yol

### A. Tam cihazı hazır alıp **yalnız yazılımı biz yapmak** (Android)

- 7" RK3326 Android tablet, 1024×600 kapasitif dokunmatik, 2 GB/32 GB, microSD, 0,3 ve 2 MP kamera, Wi-Fi, Bluetooth 4.0, USB OTG, hoparlör, pil, FCC ve CE (SMARTCN Q863): **1.000–4.999 adet 32,90 $; 5.000+ 29,90 $; 10.000+ 26,90 $; numune 36,90 $; süre 15 iş günü** [K]. Pil kapasitesi ilanda tutarsız (1800 ile 3000 mAh arası).
- Başka bir ilan 7" RK3326 tableti 19–23,9 $ gösteriyor ama aynı sayfada eski donanım (A33, Android 4.4) yazıyor; güvenilmez [K].
- Logo baskısı 100 adetten, "OEM/ODM var"; **yazılım önyükleme (preload) şartı ilanlarda yok**, tedarikçiye sorulacak [K].
- Hüsûsiyet karşılığı: dokunmatik ✓, kamera ✓, dosya sistemi ve klasör (Android) ✓, PDF çıkarma (uygulamamızla) ✓, telefon ve bilgisayar bağlantısı (Wi-Fi, Bluetooth, USB) ✓, renkli ekran ✓. **Kalem:** yalnız pasif (kapasitif) kalem; basınç ve avuç reddi için aktif kalem sayısallaştırıcısı olan model gerekir, ilanlarda bulunamadı. **Pil ömrü:** LCD ile 24 saat tutmaz (E-ink ertelendiği için bu hedef zaten güncellenebilirdi).
- Maliyet: ≈ 27–33 $ (1.000+ adet), nakliye, gümrük, KDV ve kalem hariç. Bu da yaklaşık 1.200–1.500 TL eder [H]; **1.000 TL hedefini gümrük ve KDV'den önce bile aşar.**

### B. Hazır ESP32-S3 + 7" ekran kartı alıp yazılımı biz yapmak

- Sunton ESP32-8048S070: ESP32-S3 N16R8 (16 MB flaş, 8 MB PSRAM), 7" 800×480 IPS, GT911 dokunmatik, SD yuvası, USB-C, hoparlör; **sokak fiyatı 21–28 $** [K].
- **Eksikleri:** pil bağlantısı ve şarj devresi yok, kamera desteği anılmıyor, boş GPIO yaklaşık 2; çerçeve belleği PSRAM'de olduğundan Wi-Fi yükünde titreme ve yırtılma çıkabiliyor; kart revizyonları farklı başlangıç kodu istiyor [K].
- Pil, şarj, kasa, kamera eklenince fiyat A yolunun yanına yaklaşır; hüsûsiyetler ise A'dan azdır (Android yok, PDF ve kamera işleme zor). Bu yol **prototip** için uygundur.

### C. **Kendi kartımızı** tasarlayıp yaptırmak (ESP32-S3 etrafında)

Kaynaklı kalemler: ESP32-S3-WROOM-1-N16R8 modülü 3,71–6,43 $ (LCSC, Digi-Key; 4,29 $) [K]; 7" 800×480 panel 9–15 $ (100 adet) [K]. Yalnız bu ikisi **12,7–21,4 $** eder.
Kaynaksız kalemler (tahmin): pil, şarj devresi, USB-C, SD yuvası, kamera modülü, kasa, kalem, kart payı, montaj. [?]
Kart üretimi ve montaj: JLCPCB'de 5 adet temel kart 2 $'dan; 4 katlı 100×100 mm, 5 adet yaklaşık 32,90 $ (üçüncü taraf karşılaştırma); montaj kurulumu 8 $ (ekonomik) veya 25–51 $ (standart), eklem başına 0,0016 $ [K]. Örnek: 300 eklemli kartta yerleştirme ücreti yaklaşık 0,5 $/kart [H]. Makro PCB fiyat yayımlamıyor; teklif lazım. Küçük adetli yurt dışı kart siparişi gümrükte takılabiliyor ve vergi kart bedelinin birkaç katı olabiliyor (tek forum tecrübesi) [K, zayıf].
Tahmini toplam: ≈ 20–35 $ [H, kaynaksız kalemler yaklaşık 8–15 $ varsayımıyla]; ayrıca tasarım emeği, birkaç prototip turu, yazılım (Android yok), CE/RED ve TSE uygunluğu [?].

## 3. Sorunuza cevap

**"Yalnız yazılım bizden olup bütün parçalar sipariş olsa mı daha ucuz, tasarım bizden olan parçalar olsa mı?"**

- **İlk aşamada hazır alıp yalnız yazılımı yapmak daha ucuz ve daha hızlıdır.** Hazır Android tablet 27–33 $'a pil, kamera, kasa, Wi-Fi, sertifika ve dosya sistemiyle birlikte geliyor. Kendi kartımız, aynı fiyat bandında daha az hüsûsiyet verir ve tasarım, prototip, sertifika giderini üstümüze yükler.
- **İşletim sistemsiz olmak ucuz kılmıyor.** Android tabletler seri üretimin ölçeğinden dolayı bu kadar ucuzdur; ESP32 kartı bile (21–28 $) pilsiz ve kamerasızdır. Bu, önceki "işletim sistemi çalıştıracak işlemci gerekmez, maliyet kısılır" varsayımımızı **tutmayan** bir bulgudur.
- **Makro PCB'yi kullanmak için** tasarlanacak kartlar, ancak A yolunda cihazı tamamlayan **küçük yardımcı kartlar** olur (örneğin aktif kalem arayüzü); SoC kartı değil. Bunların fiyatı teklif alınmadan bilinmez.
- Kendi kartımız ancak şu şartlarda mantıklı olur: yüksek adet, özel bir hüsûsiyet (örneğin E-ink veya özel kalem) ve Android'siz bir ürün kararı.

## 4. Önerilen sıra

1. **Numune:** SMARTCN (Shenzhen) gibi 2–3 ODM'den 7" RK3326 veya A133 tabletten numune ve teklif (1.000, 5.000 adet); **yazılım önyükleme, aktif kalemli model, pil kapasitesi ve gerçek yonga** yazılı olarak sorulacak.
2. **Yazılımı** Android uygulaması olarak biz yazarız (not, klasör, kamera üstüne not, PDF).
3. **Prototip için** Sunton kartı da alınabilir (21–28 $); ama ürün A yolunda gider.
4. **Makro PCB'den** yalnız yardımcı kart gerekirse teklif alınır.
5. **Gümrük:** tablet için bağlayıcı tarife bilgisi alınacak; KDV ve vergi dahil gerçek maliyet o zaman çıkar.

## 5. Kaynaklar

- SMARTCN Q863: https://smartcn.en.made-in-china.com/product/cxURHmyMsahk/China-7-Inch-Rk3326-Mali-GPU-PC-Quad-Core-Cortex-A35-1-3GHz-Android-Tablet-PC.html
- 7" RK3326 ilanı (tutarsız): https://www.globalsources.com/Android-tablet/Android-tablet-1163975910p.htm
- Sunton ESP32-8048S070: https://www.atomic14.com/esp32/boards/sunton-esp32-8048s070/
- ESP32-S3-WROOM-1 N16R8: https://www.lcsc.com/product-detail/C2913202.html
- 7" ekran ilanları: https://m.made-in-china.com/product/7-Inch-1024X600-TFT-LCD-in-Stock-Industrial-Capacitive-Touch-Automative-TFT-LCD-Display-Monitor-Screen-Panel-Module-1960361712.html
- JLCPCB montaj fiyatı: https://jlcpcb.com/help/article/pcb-assembly-price
- Kart üretimi karşılaştırması: https://www.nextpcb.com/blog/jlcpcb-vs-pcbway-vs-nextpcb-comparison-2026
- Pasif ve aktif kalem: https://www.parkablogs.com/node/12897
