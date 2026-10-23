# Takim basina maliyet (1 verici + 1 alici), ~100 takim
Kaynakli kalemler [B] dagitimci/LCSC sayfalarindan arama ile okundu (canli sayfada degisebilir); [T] tahmin. Hesap: `maliyet.py`.

Toplam ~101 USD: okunan fiyatli kalemler 79,8, tahmin 21,4.
| Kalem | USD/takim | Kaynak |
| :-- | :-- | :-- |
| SIM7600SA | 36,60 | DigiKey, 100 adet |
| 2 x RFM95W-915S2 | 31,52 | LCSC C6760738 (1000+ 15,76); Mouser tek adet 23,75 |
| 2 x ESP32-S3-WROOM-1-N4 | 7,32 | LCSC C2913197 |
| gerisi | 25,8 | W5500 2,49 ve TPS63031 1,89 okundu; digerleri tahmin |

**Iki gercek maliyet kalemi:** modem (%36) ve LoRa modulleri (%31).
- LoRa: Ai-Thinker Ra-01H (SX1276, RFM95W ile ayni yonga, 803-930 MHz) LCSC C503593, 18+ adette 4,38 USD: **takim basina ~22,8 USD tasarruf**. Pin tablosu ve ayak izi alinamadi (belge sitesi erisime kapali), tasarima alinmadi.
- Modem: SIM7600SA'dan ucuz ve Sili bantlarini kapsadigi dogrulanmis bir modul bu oturumda bulunamadi; A7670C-MASL (LCSC 8,62 USD) Cin bantlidir, Sili icin uygun degildir.
