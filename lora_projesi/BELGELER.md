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
| Bourns SRN6028-4R7M (L1, L2) | **okunamadi**; Farnell listesi | okunamadi | Isat 2,7 A, Irms 3 A, DCR 38 mOhm. BOM'daki "Isat >= 5 A" **yanlisti**, duzeltildi. Normal calisma icin yeterli (modem tepe ~2,6 A), kisa devrede TI'nin tavsiyesi (>=5,8 A) saglanmiyor. |
| Bourns SRP7028A-4R7M (alternatif) | Bourns, tablo ve olculer | kismi | **Isat 10 A (%20 dusus)**, Irms 5,5 A, DCR 40 mOhm, 7,3 x 6,6 x 2,8 mm. Tabani buyuk: yerlesim degisikligi gerektirir. |
| W5500 | WIZnet v1.1.0 | kismi: s.1-27, 57-63 | VDD 2,97-3,63 V; kristal +-30 ppm, C0 en fazla 7 pF, 18 pF yuk; MDIX yok; SCSn/RSTn ic cekme 50-112 kOhm. WIZnet referans semasi (RJ45 + manyetik) ile kristal ve damping direncleri **uyuyor**. |
| TXB0104 | TI SCES650K | kismi: s.1-6, 21-25 | PW pinleri **dogrulandi**; harici cekme 50 kOhm ustu olmali; VCCA <= VCCB; kullanilmayan kanalin iki ucu ayni durumda. **Uygun.** OE dogrudan VCCA'ya bagli (TI: acilis sirasinda dusuk tutan cekme direnci onerir). |
| TPS63031 | TI SLVS696D | kismi: s.1-13 | Iq 25 uA, UVLO 1,5 V, baslama 1,8 V, 1,5 uH tavsiyesi; giris >= 4,7 uF. **Uygun.** |
| RFM95W | HopeRF PRELIMINARY | kismi: guc tablosu | +17 dBm PA_BOOST 87 mA, +20 dBm 120 mA. |
| ESP32-S3-WROOM-1 | Espressif v1.8 | kismi: s.27-29 | VDD33 3,0-3,6 V; dis kaynak en az 0,5 A. |
| SIM7600 Hardware Design V1.08 | SIMCom | tam | Pin tablosu 87/87 uyuyor; VBAT 3,4-4,2 V, 2 A tepe; UART 1,8 V. |
| USBLC6-2SC6 | ST | okunamadi (st.com'a erisim yok) | Pin dagilimi uc kaynakta ayni (pin 1/6, 3/4 G/Ç; 2 GND; 5 VBUS); kenetleme degeri kaynaklarda celisiyor. |
| HR911105A (RJ45) | HanRun | okunamadi | Pinleri KiCad kutuphanesi ve WIZnet J1B1211CCD referansi ile ortusuyor; HanRun belgesi alinamadi. |

## Bulgular ve ne yapildi
1. **PTC son eki:** 1812L200/16DR. BOM, sema, kart degeri guncellendi.
2. **Endüktör:** BOM metni gercek parametrelerle duzeltildi. Yerlesim degisikligi gerektiren iyilestirme (SRP7028A) karar bekliyor.
3. **BST kondansatoru:** X7R yazildi (TI: X5R veya daha iyisi, >= 16 V).
4. **Kristal:** BOM'a +-30 ppm ve C0 sarti yazildi.
5. **USB tek basina (12 V yok):** SS14 ~0,35 V dusurur, +3V3 hatti ~2,9 V olur; ESP32 modulu 3,0 V, W5500 2,97 V ister. Programlama icin calisir (ESP32 brown-out esigi modul belgesinde yazili degil), W5500 ve LoRa 12 V olmadan guvenilir degil. Cozum secenegi: D4 yerine dusuk dusumlu kapi (yerlesim degisikligi). **Karar bekliyor.**
