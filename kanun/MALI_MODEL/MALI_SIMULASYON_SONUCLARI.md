# MALİ MODEL: BİRLEŞİK BELİRSİZLİK, DUYARLILIK VE KIRILMA ANALİZİ (17 Oct 2026)

Kaynak: `mc_uc.py` (birleşik Monte Carlo, 6000 çekim/senaryo), `kirilma_izgara.py`, `kose_stres.py`, `tornado_senaryo.py`. Tüm dağılımlar varsayımdır (ölçülmemiş girdiler); aralıklar senaryoya göre `mc_uc.py` içinde tanımlıdır. Sonuçlar 4. yıl net, milyar TL.

## 1. Birleşik Monte Carlo (tüm girdiler birlikte değişir)

| Senaryo | P1 | P5 | P50 | P95 | P99 | P(net>0) | NPV P50 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| Kötümser | 2.12 | 2.77 | 5.30 | 10.10 | 13.20 | 1.000 | 15.77 |
| Orta | 3.80 | 5.79 | 15.28 | 41.85 | 62.38 | 1.000 | 46.06 |
| İyimser | 23.98 | 28.82 | 48.15 | 81.20 | 100.95 | 1.000 | 145.78 |

## 2. Spearman duyarlılık (girdi ↔ 4. yıl net, ilk 6)

**Kötümser:** n_toplam +0.89, s_kayitli +0.25, duz_oran +0.24, prim_odeme +0.20, medyan_W +0.13, u_ucretli -0.05
**Orta:** n_toplam +0.93, duz_oran +0.22, medyan_W +0.15, s_kayitli +0.14, prim_odeme +0.10, u_ucretli -0.05
**İyimser:** n_toplam +0.79, duz_oran +0.49, medyan_W +0.28, s_kayitli +0.10, u_ucretli -0.09, prim_odeme +0.09

## 3. Kırılma ızgarası (net, milyar TL): kayıtlı geçiş s × sahte fatura φ

Net, s=0..1 ve φ=0..0.2 aralığında hiçbir noktada sıfırın altına inmedi (s* ve φ* bulunamadı).

**Kötümser** (sütun: s; satır: φ)

| φ \ s | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0.00 | 1.8 | 2.7 | 3.7 | 4.7 | 5.6 | 6.6 | 7.6 | 8.5 | 9.5 | 10.4 | 11.4 |
| 0.01 | 1.8 | 2.7 | 3.7 | 4.7 | 5.6 | 6.6 | 7.5 | 8.5 | 9.5 | 10.4 | 11.4 |
| 0.02 | 1.8 | 2.7 | 3.7 | 4.7 | 5.6 | 6.6 | 7.5 | 8.5 | 9.5 | 10.4 | 11.4 |
| 0.05 | 1.7 | 2.7 | 3.7 | 4.6 | 5.6 | 6.5 | 7.5 | 8.5 | 9.4 | 10.4 | 11.4 |
| 0.10 | 1.7 | 2.6 | 3.6 | 4.6 | 5.5 | 6.5 | 7.5 | 8.4 | 9.4 | 10.4 | 11.3 |
| 0.20 | 1.6 | 2.5 | 3.5 | 4.5 | 5.4 | 6.4 | 7.4 | 8.3 | 9.3 | 10.3 | 11.2 |

**Orta** (sütun: s; satır: φ)

| φ \ s | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0.00 | 8.1 | 11.2 | 14.2 | 17.3 | 20.4 | 23.4 | 26.5 | 29.6 | 32.6 | 35.7 | 38.8 |
| 0.01 | 8.1 | 11.1 | 14.2 | 17.3 | 20.3 | 23.4 | 26.5 | 29.5 | 32.6 | 35.7 | 38.7 |
| 0.02 | 8.0 | 11.1 | 14.2 | 17.2 | 20.3 | 23.4 | 26.4 | 29.5 | 32.6 | 35.6 | 38.7 |
| 0.05 | 8.0 | 11.0 | 14.1 | 17.1 | 20.2 | 23.3 | 26.4 | 29.4 | 32.5 | 35.5 | 38.6 |
| 0.10 | 7.8 | 10.9 | 13.9 | 17.0 | 20.1 | 23.1 | 26.2 | 29.3 | 32.4 | 35.4 | 38.5 |
| 0.20 | 7.5 | 10.6 | 13.7 | 16.7 | 19.8 | 22.9 | 25.9 | 29.0 | 32.1 | 35.1 | 38.2 |

**İyimser** (sütun: s; satır: φ)

| φ \ s | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0.00 | 33.8 | 43.6 | 53.4 | 63.2 | 72.9 | 82.7 | 92.5 | 102.3 | 112.1 | 121.9 | 131.6 |
| 0.01 | 33.8 | 43.5 | 53.3 | 63.1 | 72.9 | 82.7 | 92.5 | 102.2 | 112.0 | 121.8 | 131.6 |
| 0.02 | 33.7 | 43.5 | 53.2 | 63.0 | 72.8 | 82.6 | 92.4 | 102.2 | 112.0 | 121.7 | 131.5 |
| 0.05 | 33.5 | 43.3 | 53.1 | 62.9 | 72.6 | 82.4 | 92.2 | 102.0 | 111.8 | 121.5 | 131.3 |
| 0.10 | 33.2 | 43.0 | 52.8 | 62.5 | 72.3 | 82.1 | 91.9 | 101.7 | 111.5 | 121.2 | 131.0 |
| 0.20 | 32.6 | 42.4 | 52.1 | 61.9 | 71.7 | 81.5 | 91.3 | 101.0 | 110.8 | 120.6 | 130.4 |

## 4. Birlikte en kötü / en iyi uç (her girdi aynı anda aleyhte / lehte)

| Senaryo | Taban | En kötü uç | En iyi uç |
|:--|--:|--:|--:|
| Kötümser | 4.65 | 1.94 | 7.45 |
| Orta | 12.66 | 4.45 | 27.53 |
| İyimser | 38.67 | 13.62 | 87.45 |

## 5. Dürüst sınırlılıklar

- Dağılımlar (aralık ve mod) benim varsayımımdır; ölçülmüş veri değildir. Sonuçlar ancak bu varsayımlar kadar güvenilirdir.
- Sahte fatura kaybı modelde çok küçük çıkıyor (φ=0,20'de bile net ~0,1 milyar TL). Nedeni: B2B nötr kuralı (kv %25) ile tevkifat %13,5 arasındaki fark küçük. Model sahte faturanın tüm zararını bu farka indirger; sahte faturanın tevkifatı sıfırlaması veya kimlik kiralamanın yarattığı sızıntı modelde yok. Bu, modelin en önemli yapısal açığıdır ve sonuçların iyimserliğini artırabilir.
- Kayıtlı 4/b primi sürdüğü için s'nin artması modelde her zaman olumludur (kayıtlı prim gelir sayılır). Bu, kayıtlı sigortalının gerçekte primini ödemeyi sürdürüp sürdürmeyeceği varsayımına dayanır (prim tahsil oranı π=0,8 varsayımı).
- Bağımsızlık varsayımı: girdiler birbirinden bağımsız çekildi; oysa n_toplam ile medyan_W, s ile prim_odeme gibi çiftler gerçekte ilişkili olabilir.
- Kötümser ve İyimser senaryo sınırları (N: 100 bin / 1,1 milyon) padişahın tahminleridir; modelin genel sonucu bu iki sınıra çok duyarlıdır (n_toplam tornado'da en büyük etken).
- Bu model genel devletin (Hazine+SGK) yalnız dördüncü yıl ve beş yıllık NPV'sini verir; ilk yıl kayıp/kazanç, iflas oranı ve genç seyri (genc3.py) bu MC'de yer almaz.


## 6. Tevkifat sızıntısı ve kimlik kiralama (model genişletildi: `model.py` sizinti, kiralama)

- **sizinti**: kurumsal akıştaki sahte faturanın payı; kayıp = sizinti × kurumsal_pay × N × EH × kv (alıcının gider indirimi). Taban 0.
- **kiralama**: kiralanan kimlikle tevkifatsız gelir payı; kayıp = kiralama × N × ET. Taban 0.
- Baz sonuçlar (sizinti=0, kiralama=0) değişmedi (Kötümser 4,65 / Orta 12,66 / İyimser 38,67).

**Kötümser** (satır: kiralama; sütun: sızıntı)

| kiralama \ sızıntı | 0.00 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|:--|--:|--:|--:|--:|--:|--:|
| 0.00 | 4.65 | 4.59 | 4.50 | 4.34 | 4.04 | 3.73 |
| 0.02 | 4.60 | 4.54 | 4.45 | 4.30 | 3.99 | 3.68 |
| 0.05 | 4.53 | 4.47 | 4.38 | 4.22 | 3.92 | 3.61 |
| 0.10 | 4.41 | 4.35 | 4.26 | 4.11 | 3.80 | 3.49 |
| 0.20 | 4.18 | 4.12 | 4.02 | 3.87 | 3.56 | 3.26 |

**Orta** (satır: kiralama; sütun: sızıntı)

| kiralama \ sızıntı | 0.00 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|:--|--:|--:|--:|--:|--:|--:|
| 0.00 | 12.66 | 12.42 | 12.07 | 11.47 | 10.27 | 9.07 |
| 0.02 | 12.48 | 12.24 | 11.88 | 11.28 | 10.09 | 8.89 |
| 0.05 | 12.20 | 11.96 | 11.60 | 11.01 | 9.81 | 8.61 |
| 0.10 | 11.74 | 11.50 | 11.14 | 10.54 | 9.35 | 8.15 |
| 0.20 | 10.82 | 10.58 | 10.22 | 9.62 | 8.42 | 7.23 |

**İyimser** (satır: kiralama; sütun: sızıntı)

| kiralama \ sızıntı | 0.00 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|:--|--:|--:|--:|--:|--:|--:|
| 0.00 | 38.67 | 37.77 | 36.42 | 34.18 | 29.69 | 25.20 |
| 0.02 | 37.98 | 37.08 | 35.73 | 33.49 | 29.00 | 24.51 |
| 0.05 | 36.94 | 36.04 | 34.69 | 32.45 | 27.96 | 23.47 |
| 0.10 | 35.21 | 34.31 | 32.96 | 30.72 | 26.23 | 21.74 |
| 0.20 | 31.74 | 30.84 | 29.50 | 27.25 | 22.76 | 18.28 |

**Tevkifatın tamamen kaçması (en kötü tek kalem):** net = baz − κ × brüt tevkifat. Üç senaryoda da κ=%50 kaçakta net pozitif kalır; kırılma oranı bulunamadı (κ>1 gerekir).

- Kötümser: brüt tevkifat 2.36; κ=0 → 4.65, κ=0,30 → 3.94, κ=0,50 → 3.47
- Orta: brüt tevkifat 9.23; κ=0 → 12.66, κ=0,30 → 9.89, κ=0,50 → 8.05
- İyimser: brüt tevkifat 34.63; κ=0 → 38.67, κ=0,30 → 28.28, κ=0,50 → 21.35

**Sonuç:** Sahte fatura sızıntısı ve kimlik kiralama modelde artık açıkça var. İyimser senaryoda bile sızıntı 0,86 (yani %86) olmadan net sıfırlanmıyor; Kötümser ve Orta'da sızıntı ve kiralamanın makul aralıklarında net pozitif kalıyor. Bu, önceki 'sahte fatura kaybı küçük' uyarısını nicelleştirir: model, sızıntıya karşı dayanıklıdır; asıl hassasiyet hâlâ n_toplam ve s'dedir.

