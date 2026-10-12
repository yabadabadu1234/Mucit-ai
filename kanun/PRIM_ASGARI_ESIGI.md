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

## Devlet (4. yıl net, milyar TL; %13,5)
| | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| eski eğri | −2,05 | +1,64 | +26,56 |
| A | −1,65 | +3,83 | +37,17 |
| B | −1,90 | +2,57 | +31,45 |
| C | −2,06 | +1,75 | +27,59 |

B için oran duyarlılığı: Kötümser %20'de −0,92, %27'de +0,15, kırılma %26,0; Orta %27'de +10,37; İyimser %27'de +59,89.

## Sahtekârın nemalanma yolları (yalnız bu kural bakımından; sayılar betikten)
1. Zamanlama: aylık ölçü olduğundan faturayı aylara eşit yaymak primi düşürür. Yıllık net gelir 396.000 TL ise düzleştiren kişi 0 öder, dalgalı çalışan A'da 58.728, B'de 41.819 TL öder. Yıllık 600.000 TL ve üstünde düzleştirmek kazandırmaz (ay hep eşiğin üstündedir). Tavan 24 brüt asgari (792.720 TL) bu kazancı sınırlar.
2. Bölme: aynı iş 3 kişiye bölünürse 600.000 TL'lik gelirde prim 0'a iner (her biri aylık eşiğin altında). Kazanç kişi başı en çok yıllık tam prim kadardır (141.699 TL). Çare: gerçek faaliyet şartı ve (i) bendindeki toplulaştırma, (s) bendindeki kimlik tekliği; sahte ortak bu kuralla kesilmez, "kalan risk"tir.
3. Yüksek kazançlı yeni şirket: Madde 1 (p) uyarınca halen 4/b sigortalı olan, eski işinin primini ödemeye devam eder; yeni şirketin ilk ayında gelir 0 ise prim 0 olması yeni şirketin batmaması içindir ve Hazine'ye ek prim kaybı yoktur. Asıl sızıntı prim değil vergi oranı farkıdır: tavana kadar (792.720 TL) hasılatı eski işten yeni şirkete kaydırmak, marjinal oranı %40 olan kişi için yılda en çok (0,40−0,135)×792.720 ≈ 210.071 TL kazandırır (hesap; ayrıntı `SIZINTI_TAVAN_BOLME.md`).
4. Eşik tanımı: brüt asgari (33.030 TL) mi net asgari (28.075,50 TL) mi padişahça söylenmedi; metin brüt asgariyi yazdı (çocuk için daha lehte).

## Henüz hizalanmayanlar (F 3-I 309 teyidi bekliyor)
Madde 5 (o), I.A özeti ve Dürüstlük Notu yeni kurala çevrildi. II-A, III.E mali model blokları, D.2/D.4 tabloları, A.2 D8/D9, A.4 K14, Ek B, `EMEKLILIK_HESABI.md`, CİMER metinleri eski eğriye göredir. Resim paketi yenilenmedi (F 3-I 305 (5)).
