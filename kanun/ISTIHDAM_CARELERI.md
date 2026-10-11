# İSTİHDAM ÇARELERİ -- KÖK ÖLÇÜSÜ ATIL İŞGÜCÜ (F 3-I 270, 272)

Betik: `MALI_MODEL/istihdam_careleri.py`, çıktı: `MALI_MODEL/istihdam_careleri_out.txt`. Kaynak: TÜİK İşgücü 2025 (bülten 57996: t05, t11, t13, t15, t19, t26, t27, t03), SBB Haftalık Gelişmeler 9 Ekim 2026 s.25 (asgari ücret kaması), TÜİK Kurumsal Sektör Hesapları 2025 (GSMH).

> Tarihte ve milletlerde emsaller ve kanıt gücü: `ISTIHDAM_EMSALLERI.md` (F 3-I 273).

## 1. Teşhis: atıl işgücü 2025 = 12 077 bin kişi (yüzde 29,7)

| Bileşen | Bin kişi | Kaynak/yöntem |
| :-- | --: | :-- |
| İşsiz | 2 966 | t27 |
| Potansiyel işgücü | 5 129 | t05: iş bulma ümidi olmayan 2 608 · çalışabilir ama aramayan 2 348 · arayıp başlayamayan 173 |
| Zamana bağlı eksik istihdam | 3 982 | **türetildi**: 12 077 − 2 966 − 5 129 (iki kontrol tuttu: TÜİK 19,6 ve 19,9; bizim 19,6 ve 19,9) |
| Payda (işgücü + potansiyel) | 40 662 | 35 533 + 5 129 |

Seyir: atıl oranı 2022 yüzde 21,3 → 2025 yüzde 29,7, resmî işsizlik ise 10,4 → 8,3. Yani **işsizlik oranı düşerken atıl işgücü arttı**; resmî oran sorunu gizliyor. Kadın atıl oranı yüzde 39,1, erkek yüzde 24,0. 15-29 yaş ne eğitimde ne istihdamda: 4 711 bin, bunun 3 233 bini (yüzde 69) kadın. Uzun süreli işsiz (1 yıl+): 537 bin. İşsizlerden İŞKUR'a başvuran: 1 096 bin (yüzde 37). Kayıt dışı çalışan 8 344 bin (tarım dışı 4 609 bin; ücretli 2 843 bin).

**Yoklanamayan uyarı:** potansiyel işgücü 2021'de 3 275 bin idi, 2025'te 5 129 bin. Aynı dönemde işgücü dışı "ev işleriyle meşgul" 9 917 → 5 844 bin düştü, "çalışamaz halde" 4 998 → 7 690 ve "diğer" 2 925 → 4 665 bin çıktı. Kayma gerçek mi, sınıflama/tanım değişikliği mi, bu dosyalardan anlaşılmıyor. Sorusu: TÜİK metodoloji notu.

## 2. Bütçesiz tedbirler (önce bunlar; ölçü: hedef kitle ve tavan aritmetiği)

Elde **tedbir→dönüşüm esnekliği verisi yoktur**; bu yüzden aşağıdaki oranlar tahmin değil, "şu kadar dönüşürse şu kadar eder" tablosudur. Dönüşüm yüzdeleri varsayımdır (ölçülmedi). SGK getirisi: asgari ücretli istihdam başına ayda 12 799 TL (işveren payı 7 844,6 + işçi payı 4 954,5), yıllık 153,6 bin TL; ek gelir vergisi ve KDV sayılmadı.

| Tedbir (bütçesiz) | Hedef kitle (bin) | %1 dönüşüm | %5 dönüşüm | %10 dönüşüm |
| :-- | --: | :-- | :-- | :-- |
| B1 Potansiyel işgücüne eşleştirme/ilan yayını (ümitsizlere kanal) | 5 129 | 51 bin kişi · atıl −0,13 puan · SGK 7,9 mlr TL | 256 bin · −0,63 · 39,4 | 513 bin · −1,26 · 78,8 |
| B2 Eksik istihdamlıya tam zamana geçiş hakkı/esnek vardiya | 3 982 | 40 bin · −0,10 · 6,1 | 199 bin · −0,49 · 30,6 | 398 bin · −0,98 · 61,2 |
| B3 Kayıt dışı ücretlinin kayda geçişi | 2 843 | 28 bin · −0,07 · 4,4 | 142 bin · −0,35 · 21,8 | 284 bin · −0,70 · 43,7 |
| B5 Kadın NEET'e kısmi süreli/ev eksenli iş hakkı | 3 233 | 32 bin · −0,08 · 5,0 | 162 bin · −0,40 · 24,8 | 323 bin · −0,80 · 49,7 |

(B4: tarım dışı tüm kayıt dışı, 4 609 bin; B3 ile örtüşür.) Kapsam: B1, B2, B3, B5 hedef kümeleri **kısmen örtüşür**; toplamak çift sayımdır. Kaba üst sınır (örtüşme düşülmeden): yüzde 5 dönüşümde 759 bin kişi ≈ −1,9 puan; yüzde 10'da ≈ −3,9 puan (29,7 → ~25,8).

**"Kökten çözüm" rakamı:** atıl oranını 2022 düzeyine (yüzde 21,3) indirmek 8,4 puan, yani yaklaşık **3 416 bin kişi** demektir. Dört bütçesiz tedbirin yüzde 10 dönüşümü bile (örtüşme dahil üst sınır ~1 520 bin) bunun yarısına yetmez. Bütçesiz tedbirler tek başına kökten çözüm iddiasını **taşımaz**; bu satır sayıyla yazılmıştır.

Her tedbirin nasıl bütçesiz yapılacağı (düzenleme ve idarî eylemler; hukukî ayrıntı yoklanmadı): B1 devlet kurumlarında/kamu kurumlarında açık pozisyon ve özel ilanlarının tek ilan portalına zorunlu açık veri akışı; B2 çalışana tam zamana geçiş teklifi önceliği hakkı; B3 mikro mükellefiyet teklifi (kayıt dışı kapı) -- zaten yazıldı; B5 kısmi süreli ve ev eksenli çalışma için sigorta ve iş sözleşmesi sadeleştirmesi. İslâm uygunluğu: bunların hiçbirinde faiz, kumar, belirsizlik veya haram faaliyet teşviki yoktur; ihtilaflı fıkhî kalem görülmedi (Claude müftî değildir, F 3-I 245); devlete giden metinde dinî sebep yazılmaz (F 246).

## 3. Bütçeli tedbir: işe alım prim desteği -- kırılma tablosu

Ek iş başına net = (1−d)·12 799·(T+H) − s·7 844,6·T. d = ölü ağırlık (desteksiz de işe alınacaklar), s = işveren payının desteklenen kısmı, T = destek ayı, H = destek sonrası istihdam ayı. Kırılma d\*: bunu aşan ölü ağırlıkta program zarar eder (iskonto yok).

| s | T | H=0 | H=12 | H=24 | H=36 |
| :-- | --: | --: | --: | --: | --: |
| 0,5 | 6 | 69,4% | 89,8% | 93,9% | 95,6% |
| 0,5 | 12 | 69,4% | 84,7% | 89,8% | 92,3% |
| 0,5 | 24 | 69,4% | 79,6% | 84,7% | 87,7% |
| 1,0 | 6 | 38,7% | 79,6% | 87,7% | 91,2% |
| 1,0 | 12 | 38,7% | 69,4% | 79,6% | 84,7% |
| 1,0 | 24 | 38,7% | 59,1% | 69,4% | 75,5% |

**Uyarı (getiri brüttür):** SGK primi gelecekte emeklilik ve sağlık yükümlülüğü doğurur; tablo bunu düşmedi, yani getiri fazla gösterilmiş olabilir. Ölü ağırlık bilinmiyor; literatürdeki değerler bu depoda yoklanmadı, yazılmadı.

## 4. Ani yük sınırı ve 10 yıllık simülasyon (sabit 2026 TL)

Yük sınırı **benim varsayımımdır** (padişah sayı vermedi): yıllık brüt çıkış GSMH'nin yüzde 0,1'i = 62,3 milyar TL. s=1, T=12'de bu 662 bin işe alıma karşılıdır. Pilot: ilk yıl 50 bin işe alım = 4,7 milyar TL (GSMH'nin yüzde 0,0076'sı); sonraki yıllar 100 bin, 200 bin, sonra sabit 200 bin = en çok 18,8 milyar TL/yıl (yüzde 0,030), sınırın üçte biri.

| d | elde kalma (yıl) | iskonto | 10 yıl kümülatif (mlr TL) | en derin açık (mlr TL) | başabaş yılı |
| --: | --: | --: | --: | --: | --: |
| 0,3 | 0,6 / 0,8 | 0 | +226 / +408 | 0 | 1 |
| 0,5 | 0,6 / 0,8 | 0 | +114 / +244 | −0,9 | 3 / 2 |
| 0,7 | 0,6 / 0,8 | 0 | +2,7 / +80,7 | −13,8 / −9,8 | 10 / 6 |
| 0,7 | 0,6 / 0,8 | %20 | −5,9 / +18,8 | −10,5 / −8,0 | yok / 6 |
| 0,8 | 0,6 / 0,8 | 0 | −53 / −1,1 | −53 / −24 | yok |

Sonuç (şartlı): s=1, T=12 programı, ölü ağırlık yüzde 70'in altındaysa 10 yılda kâr bırakır ve açık GSMH'nin yüzde 0,022'sini geçmez; yüzde 80'de zarar eder. Pilotun görevi d'yi **ölçmektir**: ölçülen d yüzde 70'in altındaysa ölçeklenir, üstündeyse durur.

## 5. Eşleştirme/danışmanlık maliyeti (bütçeli, küçük)

Kişi başı maliyet kırılması c\* = p·(1−d)·12 799·H (p = yerleşme olasılığı). p=0,05, d=0,8, H=12 → 1 536 TL/kişi; p=0,05, d=0,5, H=36 → 11 519 TL/kişi; p=0,02, d=0,8, H=12 → 614 TL. İŞKUR'a başvuran işsiz 1 096 bin → bunlara kişi başı 1 536 TL harcamak 1,7 milyar TL (GSMH'nin yüzde 0,0027'si).

## 6. Açık kalemler (padişaha)
1. Ani yük sınırı: yüzde 0,1 GSMH benim varsayımım; sizin sayınız?
2. Dönüşüm yüzdeleri (B1–B5) ve ölü ağırlık d ölçülmedi; veri kaynağı yok. Pilotla ölçülsün mü?
3. Potansiyel işgücündeki 2021→2025 sıçraması (ve "ev işi → çalışamaz/diğer" kayması) sınıflama değişikliği mi? TÜİK notu yoklanmadı.
4. "Kökten çözüm" hedefi **3 416 bin kişi** (3,4 milyon; 2022 düzeyi) diye okunsun mu, yoksa başka bir hedef atıl oranı mı?
5. İl/ilçe kırılımı: atıl işgücü il düzeyinde yayımlanmıyor; elde il bazında yalnız işsizlik, istihdam, katılım var (t00–t02). Atıl oranı il bazına yaymak çıkarımdır, yazılmadı.
