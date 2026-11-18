# ÜRETİCİLER VE TEDARİKÇİLER (parça ve montaj)

**Tarih:** 2026-11-18
**Esas:** Fiyatlar hazır cihazdan değil, **parça üreticisinin veya onun mağazasının** sayfasından alınır. Hepsi tek adet perakende yahut asgarî sipariş fiyatıdır; seri sipariş fiyatı ancak teklifle öğrenilir. Hiçbir firmayla henüz temas kurulmadı.

---

Padişahın verdiği ekran bağlantılarının tek tek denetimi (dokunmatik, fiyat, stok) `EKRAN_ADAYLARI.md`de; 1.000 TL hedefi ve ekranı kendimiz üretme sorusu `MALIYET_ANALIZI.md`de; gezinme aracı `araclar/` klasöründe.

## 1. E-INK EKRAN (ana maliyet kalemi)

| Firma | Ülke / yer | Parça | Fiyat (kaynak) | Not | Temas |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **E Ink Holdings** | Tayvan | Kaleido 3 renkli panel; 6", 7", 7,8", 10,3", 13,3" boyları var. 7,8" modeller: EC078KH6, EC078KH7 (dokunmatik + ön ışık) | **Yayımlanmış fiyat yok** | Renkli E-ink'in **tek kaynağı**; 10,3" Kaleido 3'ün model sayfası sitede listelenmiyor. Renk 150 ppi, siyah-beyaz 300 ppi, 4096 renk | https://www.eink.com/contact · ortaklar: https://www.eink.com/partner · numune mağazası: https://shopkits.eink.com |
| **Good Display (Dalian)** | Çin | GDEP103TC2, 10,3" siyah-beyaz, 1404×1872 | **89,01 $** (indirimli; liste 98,90 $), kargo ABD'ye 41,69 $ — kendi mağazası buyepaper.com | Renkli 10,3" panel mağazada **yok** | buyepaper@good-display.com (mağaza sayfasındaki adres) |
| Good Display | Çin | GDEP103TC2-FT11, 10,3" siyah-beyaz, **ön ışık + dokunmatik** | **148,90 $** (kendi mağazası); Alibaba'da 73,50–117 $, asgarî 50 adet (üçüncü taraf) | Dokunmatik var, kalem katmanı yok | aynı |
| Good Display | Çin | IT8951 paralel sürücü kartı (10,3" ve 13,3" için), Arduino ve ESP32 uyumlu | fiyat okunmadı | İşletim sistemsiz sürüş için | https://www.good-display.com/product/472.html |
| Waveshare | Çin (Shenzhen) | 10.3inch e-Paper HAT (D), siyah-beyaz, IT8951 kartıyla | **243,99 $** (1–9 adet 240,99 $; 100+ adet 238,89 $) | Tam yenileme 450 ms, kısmî ~0,3 s; tazeleme 1,2 W, bekleme 0,1 W; STM32 örnek kodu var | https://www.waveshare.com/10.3inch-e-Paper-HAT-D.htm |
| Waveshare | Çin | 13,3" Spectra 6 renkli | 269,99–279,99 $ | **Tam yenileme 19 saniye: yazı tableti için kullanılamaz** | aynı site |

**Mânâsı:**
- Renkli ve yazıya elverişli E-ink bugün **yalnız Kaleido 3**'tür ve tek üreticisi E Ink'tir; fiyatı ancak E Ink'ten veya onun modül ortaklarından **teklifle** alınabilir.
- Aynı boydaki siyah-beyaz panel üreticinin kendi mağazasında 89 $ (dokunmatik ve ışıklısı 149 $). Kaleido 3, bu panelin üstüne renk süzgeci konmuş hâlidir; fiyatının bundan yüksek olacağı açıktır, ne kadar yüksek olacağı bilinmiyor.
- Spectra 6 gibi ucuz renkli tabela panelleri 19 saniyede yenilendiği için yazı tabletine uymaz.

## 2. KALEM KATMANI (EMR, pilsiz kalem)

| Firma | Ülke | Parça | Fiyat | Temas |
| :-- | :-- | :-- | :-- | :-- |
| Morgan Touch Technology | Tayvan | Elektromanyetik dokunma modülü (OEM/ODM) | yayımlanmamış | https://www.sourceready.com/supplier/detail/morgan-touch-technology-co-ltd |
| EMPEN (Panelook veri sayfası) | Çin | 10,1" ve 13,3" pilsiz EM sensörü, 4096 basınç, 266 rapor/saniye | yayımlanmamış | https://www.panelook.cn/upload/product/280195/202505163267.pdf |
| Shenzhen EMR modül üreticileri | Çin | Wacom uyumlu EMR sayısallaştırıcı | yayımlanmamış | Alibaba tedarikçi listesi: https://electronics.alibaba.com/supplier/wacom-emr |

## 3. İŞLETİM SİSTEMSİZ BEYİN (mikrodenetleyici)

| Çözüm | Ne | Durum |
| :-- | :-- | :-- |
| ESP32-S3 + IT8951 | 4 tel SPI ile 10,3" paneli süren açık kaynak proje (H-cinread-it8951) | https://github.com/martinberlin/H-cinread-it8951 |
| Seeed XIAO EE03 | ESP32-S3 tabanlı, ED103TC2 (10,3" siyah-beyaz) panelini süren hazır kart | https://wiki.seeedstudio.com/cn/getting_started_with_ee03/ |
| EPDiy | ESP32 için açık kaynak E-ink sürücü kartı; 10,3" desteği tabloda doğrulanmadı | https://github.com/vroland/epdiy |

ESP32-S3; Wi-Fi ve Bluetooth (telefon ve bilgisayar bağlantısı), kamera arabirimi, SD kart (klasör sistemi) taşır; PDF çıkarma yazılımla yapılır. Bu, Android çalıştıran bir işlemciden çok daha ucuzdur. Kaleido 3 renk katmanının IT8951 ile sürülüp sürülemediği **doğrulanmadı** (E Ink'e sorulacak).

## 4. YERLİ MONTAJ (EMS, kart dizgi ve nihaî montaj)

| Firma | Yer | İş | Kaynak durumu |
| :-- | :-- | :-- | :-- |
| Milsan Elektronik | Niğde, Bor OSB | PCB, SMD ve THT hatları; savunma, medikal, otomotiv | firma tanıtım sayfası: https://milsan-elektronik-sanayi-tic-as.idef.com.tr |
| EMS Elektronik | — | PCB, SMD/THT montaj; prototip 2–3 hafta, seri 4–6 hafta | yabancı rehber sitesi (bestpcbs) |
| Acces Elektronik | İstanbul, Dudullu | fason kart üretimi, SMD dizgi hattı | dizin kaydı |
| ERKAR Elektronik | — | PCB montaj, SMD dizgi; 1–10 çalışan | dizin kaydı |

Bu listedeki bilgiler firma tanıtımı ve dizin kaydıdır; hiçbiri bağımsız doğrulanmadı. Teklif isterken sorulacaklar: otomatik dizgi mi el dizgisi mi, asgarî adet, parça tedarikini kim yapar, nihaî kutulama ve test yapılıyor mu.

## 5. GİRİŞİMCİ DESTEĞİ

| Program | Tutar | Kaynak durumu |
| :-- | :-- | :-- |
| KOSGEB Girişimci Destek Programı | **2 milyon TL'ye kadar** (Bakan Kacır'ın açıklaması); 2026 3. dönem İş Geliştirme başvurusu 12–31 Ekim 2026 arasındaydı | haber: https://www.ntv.com.tr/ntvpara/bakan-kacir-acikladi-girisimcilere-2-milyon-liraya-kadar-destek-1705910 ; resmî yönerge: https://webdosya.kosgeb.gov.tr/Content/Upload/Dosya/Giri%C5%9Fimcilik/2026/2026.07.13/Giri%C5%9Fimci_Destek_Program%C4%B1_Y%C3%B6nergesi__(14).pdf (henüz okunmadı) |
| KOSGEB kuruluş desteği | gerçek kişi işletme 10.000 TL, sermaye şirketi 20.000 TL | ikincil kaynak |
| Genç girişimci ek tutarı | 150.000 TL'den 250.000 TL'ye; toplam 2,5 milyon TL; oran %80 | tek ikincil kaynak, **doğrulanmalı** |
| TÜBİTAK BiGG 1512 | 2026 tutarı **doğrulanamadı** (bir blogda 200.000 TL hibe) | resmî duyuru okunacak |

Ürün yeni bir teknoloji cihazı olduğu için BiGG 1512 de uygun görünüyor; hangisinin daha uygun olduğu, iki programın şartları resmî metinden okununca yazılacak.

## 6. AYNI ANDA TEMAS KURULACAKLAR

1. **E Ink Holdings** (eink.com/contact): 10,3" Kaleido 3 paneli, dokunmatik ve EMR seçenekleri, asgarî sipariş, birim fiyat, IT8951 ile renkli sürüş.
2. **Good Display** (buyepaper@good-display.com): renkli 10,3" panel temini, IT8951 kartı fiyatı, 100 ve 1.000 adet fiyatı.
3. **Morgan Touch** ve bir **Shenzhen EMR** üreticisi: 10,3" pilsiz EMR sensörü ve kalem birim fiyatı.
4. **Yerli EMS** (Milsan, Acces): kart dizgi ve nihaî montaj teklifi.
5. **KOSGEB** il müdürlüğü: Girişimci Destek Programı şartları.

## 7. KAYNAKLAR

- E Ink Kaleido 3: https://www.eink.com/brand/detail/Kaleido3
- Good Display GDEP103TC2 (kendi mağazası): https://buyepaper.com/products/gdep103tc2 ; ışıklı ve dokunmatik: https://buyepaper.com/products/gdep103tc2-ft11
- Alibaba GDEP103TC2-FT11: https://www.alibaba.com/product-detail/Goodisplay-GDEP103TC2-FT11-10-3-Front_1601841802200.html
- Waveshare 10.3 HAT (D): https://www.waveshare.com/10.3inch-e-Paper-HAT-D.htm
- Türkiye EMS rehberi (bestpcbs): https://www.bestpcbs.com/blog/2026/03/pcb-prototyping-in-turkey/
