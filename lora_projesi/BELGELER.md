# Parca belgeleri: ne okundu, ne cikti

Durum: **tam** = belge bastan sona okundu (resim ve grafik sayfalari dahil degil, yazi katmani); **kismi** = hangi bolumler okundugu yazili; **okunamadi** = uretici belgesine ulasilamadi, yalnizca dagitimci listesi var.

| Parca | Belge | Durum | Bulgu |
| :-- | :-- | :-- | :-- |
| AO3401A (ters baglanti MOSFET) | AOS Rev 3.1, 5 s | tam | VDS -30 V, VGS +-12 V, RDS(on) en fazla 50 mOhm @-10 V. Kapida 10 V zener: VGS -10 V. TVS kenetleme 24,4 V < 30 V. **Uygun.** |
| SMBJ15A (giris TVS) | Vishay 88392 | tam | Stand-off 15 V, VBR 16,7-18,5 V, kenetleme 24,4 V @24,6 A. Alici hatti (TPS62933 32 V, AO3401A 30 V, 25 V kondansatorler) kenetleme altinda. **Uygun.** |
| 1812L200 (PTC sigorta) | Littelfuse 1812L, 8 s | tam | **Hata bulundu:** BOM'daki "1812L200" son eksiz; 1812L200TH 8 V, /12 12 V, /16 16 V. 12 V besleme icin **1812L200/16DR** yazildi. 60 C'de tutma 1,5 A; elektronik 0,25-0,37 A ceker. |
| SS14 (D4 USB, D7 role) | Vishay 88746, 5 s | tam | VF 0,5 V @1 A; 0,1-0,2 A'de egriden ~0,35 V. D7 icin yeterli. D4 icin asagiya bakin (USB tek basina). |
| AP2112K-3.3 | Diodes DS39724, 18 s | tam | VIN 2,5-6 V, 600 mA, dropout 250 mV @600 mA, EN VBUS'a bagli. 4,3 V'ta sartnamesi: VBUS 5 V yeterli. **Uygun.** |
| MMBT2222A (Q2,Q3,Q4) | Diodes DS30041, 7 s | tam | IC 600 mA, VCEO 40 V, hFE >=75 @10 mA. Role 30 mA, taban 2,5 mA: doyar. **Uygun.** |
| SRD-12VDC-SL-A | Songle SRD genel belge, 2 s | tam | Bobin 400 ohm / 30 mA / 0,36 W, cekme %75 (9 V), azami surekli %120 (14,4 V). Kontak (A tipi): 10 A 30 VDC direncli, 5 A 28 VDC endüktif. Calisma -25..+70 C. **Uygun** (lamba 3 A varsayim). Not: elimdeki ilk dosya SLD serisiymis, kullanilmadi. |
| ESDA6V1-5SC6 (SIM TVS) | ST Rev 3, 5 s | tam | VBR 6,1-7,2 V, **kapasite 50 pF tipik**. SIMCom izin siniri 60 pF (iz dahil). Sinirda; SIM hatti yukselme suresi (40 ns) icin kaynak empedansi bilinmiyor. |
| TPS62933 | TI SLUSEA4D | kismi: s.1-10, 28-34 | VFB 0,8 V +-1% (25 C), +-2% (tum sicaklik). IHS_LIMIT 4,2-5,8 A. **Endüktör: Isat en az tepe akim; mumkunse >= IHS_LIMIT.** Cikis kapasitesi 3,3 V icin tipik 40 uF, en az 15 uF. 40,2k/10k = 4,016 V. |
| Bourns SRN6028-4R7M (L1, L2) | Bourns SRN6028 serisi (REV 09/17) ve SRN6028C serisi (REV 04/23) | tam | SRN6028-4R7M: L 4,7 uH %20, DCR en fazla 38 mOhm, Irms 3,0 A, **Isat 2,7 A (L %30 duser)**; onerilen taban 6,3 x 5,7 mm (pad 1,6 mm). SRN6028C-4R7M: DCR 30 mOhm, Irms 3,1 A, Isat 3,2 A, taban 6,5 x 6,5 mm, pad 2,5 mm: **ayak izi farkli**, takas yerlesim ister. Her ikisi de TI IHS_LIMIT (4,2-5,8 A) altinda; normal calisma icin yeterli, kisa devre tavsiyesini saglamaz. Belge ile BOM metni artik uyumlu. |
| Bourns SRP7028A-4R7M (alternatif) | Bourns, tablo ve olculer | kismi | **Isat 10 A (%20 dusus)**, Irms 5,5 A, DCR 40 mOhm, 7,3 x 6,6 x 2,8 mm. Tabani buyuk: yerlesim degisikligi gerektirir. |
| W5500 | WIZnet v1.1.0 | kismi: s.1-27, 57-63 | VDD 2,97-3,63 V; kristal +-30 ppm, C0 en fazla 7 pF, 18 pF yuk; MDIX yok; SCSn/RSTn ic cekme 50-112 kOhm. WIZnet referans semasi (RJ45 + manyetik) ile kristal ve damping direncleri **uyuyor**. |
| TXB0104 | TI SCES650K | kismi: s.1-6, 21-25 | PW pinleri **dogrulandi**; harici cekme 50 kOhm ustu olmali; VCCA <= VCCB; kullanilmayan kanalin iki ucu ayni durumda. **Uygun.** OE dogrudan VCCA'ya bagli (TI: acilis sirasinda dusuk tutan cekme direnci onerir). |
| TPS63031 | TI SLVS696D | kismi: s.1-13 | Iq 25 uA, UVLO 1,5 V, baslama 1,8 V, 1,5 uH tavsiyesi; giris >= 4,7 uF. **Uygun.** |
| RFM95W | HopeRF PRELIMINARY | kismi: guc tablosu | +17 dBm PA_BOOST 87 mA, +20 dBm 120 mA. |
| ESP32-S3-WROOM-1 | Espressif v1.8 | kismi: s.27-29 | VDD33 3,0-3,6 V; dis kaynak en az 0,5 A. |
| SIM7600 Hardware Design V1.08 | SIMCom | tam | Pin tablosu 87/87 uyuyor; VBAT 3,4-4,2 V, 2 A tepe; UART 1,8 V. |
| USBLC6-2SC6 (3 belge: ST DS4260 Rev 7, ST Rev 2 2005, Dowo) | ST Rev 7 + eski ST + Dowo | tam | Pin: 1 ve 6 I/O1, 3 ve 4 I/O2, 2 GND, 5 VBUS (uc belgede ayni). **ST: kapasite I/O-GND en fazla 3,5 pF**, VBR >= 6 V, IRM en fazla 150 nA (Rev 7), kenetleme 12 V @1 A / 17 V @5 A. Dowo kopyasi 0,8 pF yazar (ST degil, ayri uretici). **ESDA6V1-5SC6 (50 pF) yerine bu parca SIM hattinda SIMCom 60 pF sinirini rahat saglar** (hat basina 3,5 pF). Iki hat korur: SIM icin RST+CLK ve DATA+VDD olarak iki adet gerekir. |
| HR911105A (RJ45) (3 belge: HanRun, Handson, Rajguru) | HanRun HR911105A Rev A/3 (4 s) | tam (yazi + semalar resim olarak) | Pin: P1 TD+, P2 TD-, P3 RD+, P4 TD orta uc, P5 RD orta uc, P6 RD-, P7 NC, P8 govde GND (1000 pF/2 kV); LED: yesil 9(anot)/10(katot), sari 12(anot)/11(katot); 350 uH @8 mA, 1500 Vrms, ekleme kaybi en fazla 1 dB, 0..+70 C. **Bizim J3 baglantisi belgeye uyuyor** (1,2,3,4,5,6; 8 GND; 9 ve 12 +3V3, 10 LNK_K, 11 ACT_K). Delik: 4 ince delik 0,89 mm, 2 geng 1,63 mm, 2 govde 3,25 mm, LED 1,02 mm, adim 2,54 mm. Calisma sicakligi 0 C alti **uygun degil** (Sili icin kabul, ic mekan varsayimi). |
| Ra-01 / Ra-02 (SX1278) ve Ra-01S (SX1268) | Ai-Thinker + hestore | tam | Hepsi **410-525 MHz**: 915 MHz icin kullanilamaz. Ra-01S SX1268 (SX1276 ile register uyumsuz). Bu belgeler Sili isi icin gecersiz; yalnizca **Ra-01H** (868/915, SX1276) uygun. |
| SIMCom A7670 Series HW Design V1.00 | SIMCom, 61 s | tam | A7670**SA** (Tablo 1, sayfa 9 resimden okundu): GSM 850/900/1800/1900; LTE-FDD **B1 B2 B3 B4 B5 B7 B8 B28 B66**; B20 ve TDD yok; Cat 1 (10/5 Mbps). 24 x 24 x 2.5 mm LGA 88 pin. VBAT 3,4-4,2 V (tip 3,8). PWRKEY/RESET en fazla 10 nF. Akim tablosu LTE-FDD icin cogu satirda **TBD** (belge ilk surum). |
| Quectel EC200U Series HW Design V1.0 | Quectel, 94 s | kismi: s.1-17 (kapak, icerik, bantlar, ozellikler) | Belge yalniz **EC200U-CN (B1/B3/B5/B8, TDD B34/38/39/40/41, GSM 900/1800)** ve **EC200U-EU (B1/B3/B5/B7/B8/B20/B28, TDD B38/40/41, GSM 850/900/1800/1900)** icerir. **B2 ve B4 hicbirinde yok; "EC200U-AU" bu belgede gecmiyor.** 28 x 31 x 2.4 mm, 144 pin LCC+LGA, VBAT 3,3-4,3 V. |

## Bulgular ve ne yapildi
1. **PTC son eki:** 1812L200/16DR. BOM, sema, kart degeri guncellendi.
2. **Endüktör:** BOM metni gercek parametrelerle duzeltildi. Yerlesim degisikligi gerektiren iyilestirme (SRP7028A) karar bekliyor.
3. **BST kondansatoru:** X7R yazildi (TI: X5R veya daha iyisi, >= 16 V).
4. **Kristal:** BOM'a +-30 ppm ve C0 sarti yazildi.
5. **USB tek basina (12 V yok):** SS14 ~0,35 V dusurur, +3V3 hatti ~2,9 V olur; ESP32 modulu 3,0 V, W5500 2,97 V ister. Programlama icin calisir (ESP32 brown-out esigi modul belgesinde yazili degil), W5500 ve LoRa 12 V olmadan guvenilir degil. Cozum secenegi: D4 yerine dusuk dusumlu kapi (yerlesim degisikligi). **Karar bekliyor.**
6. **A7670SA ve EC200U karsilastirmasi (yapistirilan yapay zeka metninin dogrulanmasi):** A7670SA'nin bantlari belgeden dogrulandi (yukarida). EC200U icin metindeki "EC200U-AU" **belgede yok**; belgedeki iki varyantin ikisinde de B2 ve B4 yok. Metindeki "yaklasik yarisi fiyat" iddiasi **hicbir belgede yok**, dagitimci fiyati okunmadan yazilmaz. Sili sebekelerinin hangi bantlari kullandigi bu belgelerde yok; "B2/B4/B7/B28 gerekir" ifadesi **hafizadan**, yoklanmamistir.
7. **A7670 gecis maliyeti:** farkli ayak izi (24x24 LGA, 88 pin), farkli pin haritasi, PWRKEY/RESET VBAT'a 50 kOhm cekili, bu pinlerde 10 nF ustu kondansator yasak (bizde C44/C45 100 nF). Yani modem takasi **yeniden sema + ayak izi + yerlesim** demektir.
8. **Kucuk dogrulamalar:** SS14 ve diger kalemler degismedi; Ra-01H icin pin tablosu okundu (onceki oturum).
