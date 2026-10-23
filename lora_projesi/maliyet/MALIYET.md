# Takim basina maliyet (1 verici + 1 alici), ~100 takim
Kaynakli kalemler [B] LCSC urun sayfalarindan okundu (fiyat ve stok canli sayfada degisebilir; ayrintili tablo `LCSC_FIYAT_TABLOSU.md`); [T] tahmin. Hesap: `maliyet.py`.

Toplam ~49 USD: okunan fiyatli kalemler 31,2, tahmin 17,8.
| Kalem | USD/takim | Kaynak |
| :-- | :-- | :-- |
| 2 x Ra-01H LoRa modulu | 9,30 | LCSC, 4,65/adet |
| A7670SA-LASE modem | 8,88 | LCSC C47088708, 10+ adet fiyati (LASC 6,97; stok 97) |
| 2 x ESP32-S3-WROOM-1-N4 | 6,72 | LCSC |
| W5500, TPS63031, 2 x TPS62933, role, RJ45, LM66100, 5 x USBLC6, bobin farki | ~6,3 | LCSC (`maliyet.py` [B] kalemleri) |
| PCBA montaj (iki kart) | 5,00 | tahmin |
| PCB 4 katman (iki kart) | 3,00 | tahmin |
| diger pasifler, konnektorler | ~9,8 | tahmin |

Onceki surum (SIM7600SA + 2 x RFM95W) ~101 USD idi; fark modemden (36,60 -> 8,88) ve LoRa modullerinden (31,52 -> 9,30) geliyor.
Uyari: A7670SA-LASE LCSC stogu 1 adet gorundu (LASC 97); 100 takim icin stok/teslim suresi sorulmadan fiyat kesin degildir. Ra-01H ve A7670SA son ek anlami belgelenmemistir.
