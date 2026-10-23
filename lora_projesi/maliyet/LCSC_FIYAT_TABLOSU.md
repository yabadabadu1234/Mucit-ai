# LCSC fiyatlari (cekildi: 2026-10-23, LCSC product/detail API + JLCPCB parca arama API; USD)
Stok ve fiyat anlik degisir. "Kademe" = LCSC fiyat basamagi. Modem/LoRa icin 100 takim = 100 modem, 200 LoRa varsayildi.

| Parca | LCSC kodu | Stok | Fiyat kademeleri |
| :-- | :-- | --: | :-- |
| SIM7600SA | C5353975 | 14 | 1: 35,48 · 10+: 34,56 |
| SIM7600SA-H | C17702592 | 20 | 1: 45,74 · 10+: 44,56 |
| A7670SA-LASE | C47088708 | 1 | 1: 9,10 · 10+: 8,88 |
| A7670SA-LASC | C18548276 | 97 | 1: 7,15 · 10+: 6,97 |
| A7670SA-FASE | C5371767 | 13 | 1: 11,85 · 10+: 11,58 |
| A7670SA-MASC | C22357883 | 0 | 1: 27,86 · 200+: 11,11 · 1000+: 10,56 |
| RFM95W-915S2 (RF Solutions) | C6760738 | 0 | 1: 41,58 · 200+: 16,59 · 1000+: 15,76 |
| Ra-01H | C503593 | 3043 | 1: 6,49 · 10+: 6,37 · 18+: 4,65 |
| ESP32-S3-WROOM-1-N4 | C2913197 | 2143 | 1: 4,33 · 100+: 3,36 · 650+: 3,21 |
| W5500 | C32843 | 10296 | 1: 2,85 · 100+: 1,99 · 500+: 1,89 |
| TPS63031DSKR | C15516 | 4266 | 1: 1,12 · 100+: 0,65 · 500+: 0,59 |
| TPS62933DRLR | C3200405 | 16380 | 1: 0,51 · 100+: 0,283 · 500+: 0,272 |
| SRD-12VDC-SL-A | C93716 | 13510 | 5: 0,54 · 50+: 0,43 · 200+: 0,37 |
| HR911105A | C12074 | 0 (JLCPCB aramasi 52714 dedi) | 1: 1,74 · 93+: 1,03 · 496+: 0,95 |
| USBLC6-2SC6 (ST) | C7519 | 38750 | 5: 0,18 · 150+: 0,119 · 500+: 0,101 |
| USBLC6-2SC6 (UMW) | C2687116 | 125090 | 10: 0,048 · 100+: 0,039 |
| ESDA6V1-5SC6 (ST) | C6650 | 3010 | 1: 0,21 · 150+: 0,157 |
| SRN6028-4R7M (Bourns) | C3221249 | 6 | 1: 0,59 · 100+: 0,374 |
| SRP7028A-4R7M (Bourns) | C840529 | 148 | 1: 1,17 · 100+: 0,754 |

## Takim maliyeti (100 takim; bu tablo ile guncellenen kalemler + eski TAHMIN kalemleri aynen)
| Senaryo | USD/takim |
| :-- | --: |
| Eski model (maliyet.py) | 101,22 |
| Ayni tasarim, LCSC guncel fiyat | 96,93 |
| + Ra-01H (2 adet) | 73,05 |
| + A7670SA-LASC modem | 69,34 |
| + A7670SA-LASE modem | 71,25 |
| Ra-01H + A7670SA-LASE | 47,37 |
| Ra-01H + A7670SA-LASC | 45,46 |

Not: toplamin yaklasik 21 USD'si hala tahmindir (konektorler, pasifler, PCB, montaj; maliyet.py "T" kalemleri). A7670SA son ekleri (LASC/LASE/FASE/MASC) icin belgede esleme yok; hangisi Sili icin uygun dogrulanmadi.

## A7670SA son ekleri: ne doğrulandı (2026-10-23)
- SIMCom A7670SA datasheet'i (LCSC'deki FASE belgesi, V2021.01) ve A7670 serisi tanıtım belgesi (LCSC'deki LASC ve LASE belgeleri, V2020.02) **tek bir SA bant listesi** verir: LTE-FDD B1/B2/B3/B4/B5/B7/B8/B28/B66, GSM 850/900/1800/1900. Son ekler (LASC/LASE/FASE/MASC) için ayrı bant tablosu yoktur.
- LCSC'nin kendi "Frequency Range" alanı bu belgelerle çelişir (LASE: B1-B7, FASE: B1-B4, LASC: tam liste). Katalog girişi hatalıdır; belge esas alınır.
- Son ek anlamı SIMCom belgelerinde **yazılı değil**. Üçüncü taraf iki kaynak (kullanıcı kılavuzu, bir blog) LASE = GNSS yok, FASE = GNSS ve BT var der; LASC/MASC/MASE için kaynak bulunamadı.
- Şili LTE bantları (Kimovil, Wikipedia, registromultibanda; kaynaklar kısmen tutarsız): B28 (700 MHz, üç büyük operatör), B7 (2600), B2 (1900), B4 AWS (WOM'un ana bandı), B66 (WOM), Claro 850 (B5). A7670SA hepsini taşır; **B3 Şili listesinde yok, gerekli değil**.
- Karar: tasarım **A7670SA ailesi** için yapılır (24x24 LGA, 88 pad; aynı ayak izi). BOM'da ana kod **A7670SA-LASE** (GNSS/BT yok, bu projede gerekmez). LASC aynı bant listesini taşır ve %21 ucuzdur ama farkı belgelenmemiştir: satın almadan önce LCSC/SIMCom'a yazılı soru olarak sorulacaktır; tasarımı etkilemez.
