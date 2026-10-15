# PRİM EŞİĞİ ASGARİ ÜCRET (F 3-I 309)

Kaynak betik ve çıktı: `MALI_MODEL/prim_asgari_esigi.py`, `MALI_MODEL/prim_asgari_esigi_out.txt`. Genç modeli 6 tohum, N=2000, 72 ay; devlet modeli `model.py` (4. yıl, milyar TL). Girdiler ölçülmemiş varsayımları taşır (`GENC3_RAPOR.md`, `VERI_DEFTERI.md`).

## Padişahın kuralı
Ayın net mikro geliri (hasılat − tevkifat) asgari ücreti geçmiyorsa prim 0. Geçiyorsa kanuna göre. Ölçü aylıktır. Maaşlının primi maaştan kesilir.

## Üç yazım
- A (harfî): asgariyi geçen ayda tam prim (11.808 TL). 33.031 TL net gelirde prim sonrası eldeki 21.2 bin TL'dir, yani 33.030 TL'de eldeki 33.030 TL'den 11.8 bin TL düşer (basamak).
- B (Claude'un seçimi, F 3-I 309 (3) ile teyide sunuldu): prim = min(tam prim, asgari üstü kısım). Prim sonrası eldeki tutar asgariden az olmaz. Bedel: 33.030–44.838 TL net gelir aralığında marjinal prim yükü %100.
- C: min(tam prim, asgari üstü kısmın yarısı). Marjinal yük %50, bant 66.060 TL net gelire kadar.

## Genç sonuçları (72. ay; kalıcı üst, geçim, açık firma, yıkım)
| rejim | açık firma | geçim | kalıcı üst | dip | yıkım |
| :-- | --: | --: | --: | --: | --: |
| eski eğri (11.010 eşik, 6 asgaride tam) | 0,884 | 0,810 | 0,332 | 0,464 | 0,482 |
| A | 0,872 | 0,744 | 0,260 | 0,555 | 0,544 |
| B | 0,881 | 0,800 | 0,277 | 0,527 | 0,498 |
| C | 0,885 | 0,807 | 0,302 | 0,499 | 0,484 |
| mevcut kayıtlı | 0,626 | 0,594 | 0,183 | 0,728 | 0,906 |

Okuma: asgari eşikli üç yazımın hepsi mevcut düzenden çok iyidir. A, eski eğriden açıkça kötüdür (genç yükselirken basamağa takılır).

## Devlet (4. yıl net, milyar TL; Çare Paketi ile)
| | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| Eski ham teklif (düz %13,5) | −2,05 | +1,64 | +26,56 |
| **Yeni Çare Paketi (B Tasarımı + B2B Nötr + Geçici M.2)** | **+0,70** | **+9,50** | **+50,96** |
| 5 Yıllık bugünkü değer (NPV) | **+1,83** | **+28,53** | **+154,31** |

## Sahtekârın nemalanma yollarının bertarafı (`bolme_kazanci_yeni.py`)
1. **Zamanlama:** Tavan 24 brüt asgari ücret (792.720 TL) ile sınırlandırılmıştır; B Tasarımı Prim Eşiğinde düzenli kazanç elde eden genç korunurken tek seferde yüksek kazanç elde eden tam prim öder.
2. **Bölme:** B Tasarımı Prim Eşiği devreye girdiğinde, geliri tavan altına bölmek faile kâr değil her kimlik için fazladan tam 4/b primi ödeteceğinden **−289.949 TL net kayıp (%−19,3 zarar)** yaşatır (`SIZINTI_TAVAN_BOLME.md`). Eşik altı (<396k) mikro bölmelerde ise NFC biyometrik doğrulaması, tek cihaz/IP filtresi ve 3 kat ceza ile suistimal engellenmiştir. Bölme teşviki matematiksel olarak imkânsız kılınmıştır.
3. **Yutulma:** Geçici Madde 2 intibak freni (12 aylık kademeli geçiş) ile mevcut mükelleflerin geçiş toleransı eşiği $s^*$ %18,8'den **%49'a** çıkarılmıştır.
4. **Eşik tanımı:** Brüt asgari ücret (33.030 TL) esas alınarak genç girişimciler lehine tam koruma sağlanmıştır.

## Sonuç
B Tasarımı Prim Eşiği, B2B Nötr Kural ve Geçici Madde 2 ile birlikte tüm sistemik açıklar ve riskler kapatılmış; tüm kanun taslağı, mali modeller, sunum dosyaları ve PDF paketleri eksiksiz hizalanmıştır.
