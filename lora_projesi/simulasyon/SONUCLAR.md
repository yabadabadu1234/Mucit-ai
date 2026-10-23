# Simulasyon sonuclari (gercege yakin, varsayimlar acik)

Hepsi tekrar kosturulabilir: `modem_gsm_patlama.cir` (ngspice), `verici_pil_omru.py`, `alici_hesaplar.py`. Rakamlarin yaninda [belge] = uretici belgesinden, [cikarildi] = karttan olculdu, [varsayim] = benim kabulum.

## 1. Modem besleme hatti, GSM patlamasi (2,8 A, 577 us, 216 Hz) -- modem_gsm_patlama.cir
Model: 12 V giris (PTC 0,2 ohm [varsayim], MOSFET 0,08 ohm), TPS62933 ortalama akim modu modeli (belge: sabit frekansli tepe akim kipi, ic dengeleme; **dis cevrim bant genisligi [varsayim], veri sayfasinda yok**), cikis kondansatorleri (2 x 22 uF, 330 uF polimer, 10 uF, 100 nF) ve **karttan cikarilan iz direncleri** [cikarildi: bobinden C14 1,0 / C15 2,8 / C16 5,6 / C48 21 mOhm; modul VBAT pedlerine 18-19 mOhm; iz agi cozumu ile, 1 oz bakir]. Patlama akimi 2,8 A [A7670SA belgesi: VBAT en az 300 uF ve 2,8 A kaynak]. VBAT ayari 4,016 V.
| Durum (cevrim bant genisligi, seramik payi, polimer ESR) | Modul VBAT en dusuk |
| :-- | :-- |
| 40 kHz, %60, 30 mOhm | 3,83 V |
| 20 kHz, %50, 40 mOhm | 3,54 V |
| 10 kHz, %40, 40 mOhm | 2,90 V (**3,4 V altinda**) |
| 5 kHz, %30, 40 mOhm | 1,63 V |
Sonuc: modul alt siniri 3,4 V [belge]. **Sonuc cevrim bant genisligine siddetle bagli; bu deger olculmedi.** 20 kHz ve ustunde sinir tutuyor, 10 kHz'de tutmuyor. Kondansatorlerin yuku tasimasi tek basina yetmez (2,8 A x 577 us = 1,6 mC, ~384 uF'ta 4 V dusus); yukun cogunu cevirici karsilar. Prototipte VBAT patlamasi osiloskopla olculmeli; tutmazsa daha genis bantli bir cevirici gerekir.
Iz: bobinden modul pedlerine direnc 18-19 mOhm; 2,8 A'de ~52 mV dusus [cikarildi]. SIMCom'un "2 mm" onerisi bu dusus butcesi icin gerekli degil; hat 41 mm boyunca 1,0 mm, geri kalani 0,4 mm.

## 2. Verici pil omru -- verici_pil_omru.py
Alkalin AAA iki hucre, ic direnc dolulukla artiyor [varsayim: tipik egri]. TPS63031 giris 1,5 V'un altina inerse kesilir [belge: UVLO 1,4-1,6 V].
- Ra-01H 915 MHz TX 97 mA ortalama [belge, Ra-01H Tablo 1.1] + ESP32 bosta 30 mA: pil %95,5'a kadar (23 C), %91'e kadar (0 C, ic direnc x2) bu yuku tasir.
- Uyku akimi toplami ~39 uA: TPS63031 Iq 25 uA [belge] + 4 uA [belge] + ESP32-S3 derin uyku 8 uA [belge] + SX1276 uyku 0,2 uA [yonga degeri; Ra-01H belgesinde uyku akimi yok] + sizinti 2 uA [varsayim].
- Omur (SF7, 12 bayt, %85 kullanilabilir kapasite, 1000 mAh [varsayim]): gunde 10 basista 2,4 yil, 50'de 2,0, 200'de 1,3 yil. SF12'de gunde 50 basista 0,7 yil. (RFM95W 87 mA'dan Ra-01H 97 mA'ya gecis sonucu degistirmedi.)

## 3. Alici 12 V butcesi ve isinma -- alici_hesaplar.py
3,3 V hatti en kotu ~300 mA, 12 V girisinden ortalama 250-370 mA, PTC tutma akimi 2 A [belge degil, parca adi]; lamba akimi sigortadan gecmez. TPS62933 kaybi 110-160 mW, Tj-Ta en fazla ~17 C (JEDEC 112 C/W, kotumser) [belge].

## 4. RF yolu -- alici_hesaplar.py
0,4 mm (modem anten hatti da 0,4 mm) / h 0,18-0,24 mm / er 4,2-4,6: Z0 43-53 ohm, nominal 48,3 ohm [Hammerstad-Jensen, katman dizilimi varsayim]. En kotu sapma %14 (donus kaybi yaklasik -22 dB).

## 5. W5500 kristal ve Ethernet ciftleri -- alici_hesaplar.py
XI 19,5 mm, XO 20,9 mm: ~1,5 ve 1,6 pF iz kapasitesi; WIZnet'in ~1 cm'lik referansina gore ~0,39 pF seri yuk farki = ~2 ppm [kristal Cm/C0 varsayim]. Ethernet siniri +-50 ppm. Cift uzunluk farki TX 2,1 mm, RX 2,8 mm = 12 ve 17 ps; 100BASE-TX sembol suresi 8000 ps. Hangi iz parcalarinin hangi cifti olusturdugu net adlarindan okundu (sema ile dogrulanmadi). WIZnet referansi "esit uzunluk" der; fark olcude ihmal edilebilir ama referansin uzerine cikilmis degil.
