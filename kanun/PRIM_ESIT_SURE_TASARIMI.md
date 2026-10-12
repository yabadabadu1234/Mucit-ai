# EŞİT SÜRELİ EMEKLİLİK PRİMİ: TASARIM VE DENGE HESABI (F 3-I 305)

Kaynak: `MALI_MODEL/prim_esit_sure.py`, çıktı `prim_esit_sure_out.txt`. Teklif metni (Madde 5 (o)) **değiştirilmemiştir**; padişah "sistemi henüz oturtamadık" dedi, bu dosya öneridir.

## Sorun
Mevcut metinde gün, ödenen primin tam prime oranı kadar sayılır. Aylık net 66.060 TL (iki asgari ücret) kazanan 9000 güne yaklaşık 85 yılda ulaşır; aylık 22.000 TL kazanan 426 yılda. Fakir hiç emekli olamıyor.

## Önerilen usul
1. Primi ödeyen herkese (geliri geçim haddi olan 11.010 TL'yi aşan her ay) **aynı gün sayısı** yazılır: c₀ = 9000 ÷ (12 × T) gün/ay. T = 65 yıl için c₀ = 11,54 gün/ay.
2. Prim, gelirin geçim haddini aşan kısmıyla orantılı artar: p(y) = min(tam prim, θ × (y − 11.010)). Zengin fakirden çok öder.
3. θ, **gün fiyatı** esasıyla dengeye oturtulur: gün fiyatı = tam prim ÷ 30 = 393,61 TL. Toplanan prim = verilen gün × gün fiyatı. (Gün fiyatı aktüeryal gider değildir; hesaplanmamıştır, Ek B.)

## Sonuç (Orta senaryo gelir dağılımı; katkı yapanların payı %51,4)

| Hedef T (yıl) | Herkese gün/ay | θ (marjinal prim oranı) | Aylık prim, net 15.000 TL | 22.000 TL | 33.030 TL | 45.000 TL | 57.000 TL | Tam primin (11.808 TL) başladığı gelir |
| --: | --: | --: | --: | --: | --: | --: | --: | --: |
| 85 | 8,82 | 0,288 | 1.150 | 3.168 | 6.349 | 9.800 | 11.808 | 51.967 |
| 75 | 10,00 | 0,332 | 1.323 | 3.645 | 7.304 | 11.274 | 11.808 | 46.609 |
| **65** | **11,54** | **0,396** | **1.580** | **4.351** | **8.717** | **11.808** | **11.808** | **40.838** |
| 55 | 13,64 | 0,501 | 1.997 | 5.502 | 11.023 | 11.808 | 11.808 | 34.598 |
| 45 | 16,67 | 0,709 | 2.829 | 7.792 | 11.808 | 11.808 | 11.808 | 27.665 |

(Rejimin gelir tavanı, 24 brüt asgari ücret, aylık net en çok 57.100 TL demektir.)

## Okuma
- 65 yıl için fakirin gün başına ödediği 137 TL (1.580 ÷ 11,54), zenginin 1.023 TL; **zengin fakirden 7,5 kat fazla öder**, padişahın "bin / üç bin" örneğinden daha dik.
- Mevcut orantılı usulde net 15.000 TL'de prim 252 TL idi ve gün 1,28 idi; yeni usulde prim 1.580 TL, gün 11,54. **Fakir mutlak olarak daha çok öder** (gelirinin %10,5'i), fakat gün başına daha az öder.
- **Bedel (dürüst):** 65 yıl hâlâ bir ömürdür; 25 yıl (tam gün) için herkes tam prim ödemelidir. T küçüldükçe θ hızla artar (45 yılda marjinal %71).
- **Nakit etki:** ortalama aylık prim 392 TL'den 2.334 TL'ye çıkar (Orta: yılda yaklaşık +6,2 milyar TL nakit); bu, aynı tutarda ek emeklilik yükünü (gün fiyatıyla) doğurur; net etki gün fiyatı hesabında sıfırdır, aktüeryal hesabı yoktur.
- **Basamak:** geliri geçim haddinin hemen üstünde olan kişi hemen hemen primsiz 11,54 gün alır; bunu önlemek için günü (y − 11.010) üzerinden kısa bir aralıkta artırmak mümkündür (padişaha sorulur).
- **Sızıntı:** her kimlik ayrı 11,54 gün alır; tavan üstü bölme sızıntısı (`SIZINTI_TAVAN_BOLME.md`) bu tasarımla kapanmaz, her kimlikte yalnız prim artar.
