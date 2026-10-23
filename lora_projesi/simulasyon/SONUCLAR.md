# Simulasyon sonuclari (gercege yakin, varsayimlar acik)

Hepsi tekrar kosturulabilir: `modem_gsm_patlama.cir` (ngspice), `verici_pil_omru.py`, `alici_hesaplar.py`. Rakamlarin yaninda [belge] = uretici belgesinden, [cikarildi] = karttan olculdu, [varsayim] = benim kabulum.

## 1. Modem besleme hatti, GSM patlamasi (2 A, 577 us, 216 Hz) -- modem_gsm_patlama.cir
Model: 12 V giris (PTC 0,2 ohm [varsayim], MOSFET 0,08 ohm), TPS62933 ortalama akim modu modeli (belge: sabit frekansli tepe akim kipi, ic dengeleme; dis cevrim bant genisligi [varsayim]), cikis kondansatorleri ve **karttan cikarilan iz direncleri** [cikarildi: L2->modul 7,1 / 18 mOhm, C16 13,5 mOhm...].
| Durum | VBAT ayarli 3,79 V | VBAT ayarli 4,016 V (yeni) |
| :-- | :-- | :-- |
| cevrim 40 kHz, seramik %60, polimer ESR 30 mOhm | 3,67 V | 3,89 V |
| cevrim 10 kHz, seramik %40, ESR 100 mOhm | 3,33 V (**3,4 V altinda**) | 3,56 V |
| cevrim 5 kHz, seramik %30, ESR 200 mOhm | 2,92 V | 3,14 V |
Sonuc: modul alt siniri 3,4 V [belge V1.08]. 3,79 V ayarda kotumser kosulda sinir asiliyordu: **VBAT ayari 4,0 V'a cikarildi (R4 40,2k)**, polimer kondansator icin **ESR en fazla 40 mOhm sarti BOM'a yazildi**. Cok kotu uc durum (5 kHz, 200 mOhm) hala 3,4 V altinda; bu durum 40 mOhm sartiyla disarida kalir ama cevrim bant genisligi olculmedi.
Iz: 0,7 mm yol 2 A'de ~15-35 mV dusurur [cikarildi]; SIMCom'un "2 mm" onerisi bu kartta gerekli degil.

## 2. Verici pil omru -- verici_pil_omru.py
Alkalin AAA iki hucre, ic direnc dolulukla artiyor [varsayim: tipik egri]. TPS63031 giris 1,5 V'un altina inerse kesilir [belge: UVLO 1,4-1,6 V].
- +17 dBm TX (87 mA [belge]) + ESP32 bosta: pil %96'ya kadar (23 C), %92'ye kadar (0 C, ic direnc x2) bu yuku tasir.
- Uyku akimi toplami ~39 uA: TPS63031 Iq 25 uA [belge] + 4 uA [belge] + ESP32-S3 derin uyku 8 uA [belge] + RFM95W 0,2 uA [belge] + sizinti 2 uA [varsayim]. Ilk notlardaki "8 uA" sadece ESP32'ydi.
- Omur (SF7, 12 bayt, %85 kullanilabilir kapasite, 1000 mAh [varsayim]): gunde 10 basista 2,4 yil, 50'de 2,0, 200'de 1,3 yil. SF12'de gunde 50 basista 0,7 yil.

## 3. Alici 12 V butcesi ve isinma -- alici_hesaplar.py
3,3 V hatti en kotu ~300 mA, 12 V girisinden ortalama 250-370 mA, PTC tutma akimi 2 A [belge degil, parca adi]; lamba akimi sigortadan gecmez. TPS62933 kaybi 110-160 mW, Tj-Ta en fazla ~17 C (JEDEC 112 C/W, kotumser) [belge].

## 4. RF yolu -- alici_hesaplar.py
0,4 mm / h 0,18-0,24 mm / er 4,2-4,6: Z0 43-53 ohm, nominal 48,3 ohm [Hammerstad-Jensen, katman dizilimi varsayim]. En kotu sapma %14 (donus kaybi yaklasik -22 dB).

## 5. W5500 kristal ve Ethernet ciftleri -- alici_hesaplar.py
XI 28 mm, XO 32 mm: ~2,1 ve 2,4 pF iz kapasitesi; WIZnet'in ~1 cm'lik referansina gore ~0,75 pF seri yuk farki = ~4 ppm [kristal Cm/C0 varsayim]. Ethernet siniri +-50 ppm. Cift uzunluk farki 14,6 / 11,8 mm = 86 / 70 ps; 100BASE-TX sembol suresi 8000 ps. WIZnet referansi "esit uzunluk" der; fark olcude ihmal edilebilir ama referansin uzerine cikilmis degil.
