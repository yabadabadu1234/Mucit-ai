# RİSK SİMÜLASYONU — SEÇİLEN (S) VE MODEL K (K1) (F 3-I 256, padişah: "Onu da, bilinen riskleri de simüle et")

Kod: `risk.py`, `risk2.py`; sonuç: `sonuc_risk.json`, `sonuc_risk2.json`. Ölçü: yıl-4 net etki, milyar TL/yıl. S = teklifin mevcut hâli; K1 = S + kuluçka 3 yıl, sonra net gelirin %5'i prim (geri akış %60 varsayımı). Hepsi **modeldir**, ölçülmüş değildir; risk parametreleri benim varsayımımdır.

## 1. Tek tek risk (yıl-4 net, mlr TL)
| Risk | Kötümser S / K1 | Orta S / K1 | İyimser S / K1 |
| :-- | :-- | :-- | :-- |
| R0 risksiz | +1,08 / +1,25 | +4,86 / +5,52 | +14,19 / +16,02 |
| R1 prim sürekliliği %50 tutar | **−1,47** / −1,30 | +1,89 / +2,55 | +12,20 / +14,04 |
| R2 prim sürekliliği hiç tutmaz | **−4,02** / −3,85 | **−1,09** / −0,43 | +10,22 / +12,05 |
| R3 dolaşma %10 | +1,08 / +1,25 | +4,85 / +5,50 | +14,10 / +15,94 |
| R4 dolaşma %30 | +1,08 / +1,25 | +4,81 / +5,47 | +13,94 / +15,78 |
| R5 sahte bağımsızlık %3, test yok | +0,91 / +1,07 | +4,39 / +5,05 | +13,14 / +14,98 |
| R6 aynısı, tek müşteri testi %70 önler | +1,03 / +1,20 | +4,72 / +5,38 | +13,87 / +15,71 |
| R7 kayıtlı payı s=%30 | +1,08 / +1,25 | +4,02 / +4,53 | +10,99 / +12,25 |
| R8 K'de geri akış %100 | +1,08 / +1,08 | +4,86 / +4,86 | +14,19 / +14,19 |
| R9 K'de geri akış %150 | +1,08 / +0,88 | +4,86 / +4,04 | +14,19 / +11,89 |
| R10 K'de katılım kaybı, puan başı %1 | +1,08 / +1,18 | +4,86 / +5,24 | +14,19 / +15,22 |
| R11 K'de katılım kaybı, puan başı %3 | +1,08 / +1,05 | +4,86 / +4,69 | +14,19 / +13,61 |
| R12 bileşik (prim %50 + dolaşma %10 + sahte %3 + geri akış %100 + kayıp %1/puan) | **−1,64** / −1,56 | +1,40 / +1,32 | +11,08 / +10,52 |
| R13 bileşik + tek müşteri testi | −1,52 / −1,45 | +1,73 / +1,64 | +11,81 / +11,22 |

## 2. Okunuşu (tenkitli)
1. **Belirleyici risk prim sürekliliğidir.** Kırılma noktası (prim yükümlülüğünün sürmesi gereken en düşük pay): Kötümser **%78,7** (K1 %75,5), Orta **%18,3** (K1 %7,2), İyimser 0. Yani sürekliliğin hukuken tutmaması hâlinde Kötümser senaryo açıkça zarardır; Orta'da yarı tutsa bile pozitif kalır. Bu, teklifin **en zayıf noktasıdır**; 3-I 253/255'teki "pozitif" ibaresi ancak bu şartlıdır.
2. **Dolaşma modelde etkisiz çıktı** (Orta R4: −0,05). Bu "risk yok" demek değildir: modelde dolaşan kişi yalnızca tevkifat dilimini böler; aile bireyi adına **tescille yutulmaya girmek**, tavan aşan işletmenin parçalanması ve prim kaçışı modellenmedi. Sonuç alt sınırdır.
3. **Sahte bağımsızlık (Brezilya tipi)** %3'te Orta'da −0,47 mlr; tek müşteri testi bunun %70'ini önlerse −0,14'e iner. Oranlar (işçi+işveren SGK %30, ücretli vergi %15) **hafızadan varsayımdır, yoklanmadı**.
4. **Model K:** prim sürekliliği kırılma noktasını Orta'da %18'den %7'ye indirir, fakat geri akış %150 veya katılım kaybı puan başı %3 olursa S'nin altına düşer (Orta R9: 4,04 < 4,86). Yani K1 **kârlı değil, koşullu**; üstünlüğü adalet (yeni girişimci 3 yıl sonra sigortalı olur) ve bazı koşullarda küçük kâr.
5. **Monte Carlo (4000 çekiliş; risk parametreleri rastgele: sürekliliğin %25 olasılıkla kısmen tutmaması, dolaşma 0–%20, sahte bağımsızlık 0–%5, geri akış 0,4–1,1, katılım kaybı 0–%3/puan):**
   | Senaryo | P(net<0) | %5 | medyan | %95 |
   | :-- | :-- | :-- | :-- | :-- |
   | Kötümser S | %19,3 | −3,09 | +1,00 | +1,07 |
   | Kötümser K1 | %19,3 | −2,79 | +0,96 | +1,19 |
   | Orta S | %5,7 | −0,18 | +4,58 | +4,82 |
   | Orta K1 | %3,8 | +0,27 | +4,44 | +5,31 |
   Kötümser'de zarar olasılığı K1'le de değişmedi: risk, K'nin etkilemediği prim sürekliliğidir.
6. **Adalet riski (asimetri) ölçüldü:** aynı hasılatta eski usulle yük (vergi + 4/b primi %80 ödeme) / yeni rejim yükü: H=1W'de **33,4×**, 2W'de 17,1×, 4W'de 8,9×, 8W'de 4,8×, 16W'de 2,4×, 24W'de 1,6× (W=33.030 TL). Prim sürekliliği şartı bu farkı korur; küçük gelirli eski mükellef için son derece ağırdır. Bu, **kapı kaldırılınca doğan asıl adaletsizliktir**; kapıyı geri getirmek (3-I 253) başka bir adaletsizlik doğurur. Bir uzlaşma, eski mükellefin primini **gelire oransal** yapmaktır (Bağ-Kur'un eski basamak sistemi, İspanya 2023); bunun mali bedeli prim sürekliliğinin kırılma noktasına bakılarak seçilir: Orta'da en çok %81'lik prim kaybı (devam ≥ %18) pozitif kalır, **Kötümser'de ancak devam ≥ %79 iken** pozitiftir. Bu uzlaşma henüz simüle edilmedi; sonraki iş.

## 3. Hüküm
- Teklif **şartlı pozitiftir**: pozitif kalması prim sürekliliğinin hukuken tutmasına bağlıdır; Kötümser senaryoda bu şart %79'dur.
- Model K ana metne **alınmadı**; kazanç küçük ve geri akış/katılım varsayımlarına duyarlı.
- Açık ve padişaha ait karar: eski mükellef için prim sürekliliğini **tam** mı (adaletsizlik 1,6–33×), yoksa **gelire oransal** mı (adil, kârı düşürür) kuralım? Şıklar sayıyla yukarıda.
