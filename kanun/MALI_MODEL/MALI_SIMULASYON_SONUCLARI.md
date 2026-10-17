# MALİ MODEL: VERİYE BAĞLI SENARYOLAR, BELİRSİZLİK VE KIRILMA ANALİZİ (Ekim 2026)

Üretici: `rapor_uret.py` (tüm rakamlar JSON çıktılarından alınır). Net ve NPV milyar TL, 4. yıl ve 5 yıl reel %5.

## 0. Senaryo girdileri (veriye bağlı)

N (katılımcı) TÜİK 2025 tablolarından: Kötümser = 2021 düzeyi (255 bin, kendi işyeri kurmak niyetli işsiz); Orta = 2025 (332 bin); İyimser = 2025'in 2021–2025 büyüme hızıyla (%6,8/yıl) 5 yıl uzatılması (462 bin). Dağılım σ(log) = 0,106 (aynı seriden). Brezilya MEI analogu (havuzun %20'si ≈ 1.047 bin) yalnızca dış sınır olarak kırılma ızgarasında ve tornado'da kullanıldı.

| Senaryo | N | Baz net | NPV5 | Brüt tevkifat |
|:--|--:|--:|--:|--:|
| Kötümser | 255.000 | 4.56 | 13.52 | 6.02 |
| Orta | 332.000 | 4.73 | 14.03 | 9.26 |
| İyimser | 462.000 | 8.77 | 26.29 | 14.60 |

## 1. Birleşik Monte Carlo (6000 çekim, tüm girdiler birlikte)

| Senaryo | P1 | P5 | P50 | P95 | P99 | P(net>0) | NPV P50 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| Kötümser | 1.71 | 2.10 | 3.44 | 5.56 | 6.69 | 1.000 | 10.13 |
| Orta | 3.70 | 4.40 | 7.57 | 12.74 | 15.75 | 1.000 | 22.68 |
| İyimser | 8.99 | 10.49 | 16.84 | 27.32 | 31.96 | 1.000 | 50.78 |

## 2. Spearman duyarlılığı (ilk 6)

- **Kötümser:** duz_oran +0.75, n_toplam +0.35, sigma -0.33, s_kayitli -0.30, ort_H_W +0.24, u_ucretli -0.11
- **Orta:** duz_oran +0.73, sigma -0.38, n_toplam +0.31, s_kayitli -0.29, ort_H_W +0.19, u_ucretli -0.15
- **İyimser:** n_toplam +0.32, s_kayitli +nan, duz_oran +0.84, sigma -0.28, ort_H_W +0.20, marj -0.12

## 3. Tek parametre tornado (17 parametre; düşük / yüksek uç)

**Kötümser** (taban 2.36)

| parametre | düşük uç değeri | yüksek uç değeri | Δ düşük | Δ yüksek |
|:--|--:|--:|--:|--:|
| n_toplam | 119000 | 475000 | 0.00 | 7.22 |
| duz_oran | 0.105 | 0.27 | -0.61 | 2.79 |
| sigma | 1.25 | 2 | 2.23 | 0.00 |
| s_kayitli | 0 | 0.489 | 0.00 | -0.87 |
| ort_H_W | 30 | 85 | -0.27 | 0.54 |
| prim_k | 3 | 12 | 0.51 | -0.23 |
| u_ucretli | 0 | 0.4 | 0.38 | -0.23 |
| prim_toplama | 0.5 | 1 | -0.22 | 0.00 |
| myo_uygun | 0.1 | 0.6 | 0.17 | -0.04 |
| kdv_donanim_pay | 0.2 | 0.6 | 0.14 | -0.05 |
| marj | 0.35 | 0.65 | 0.11 | -0.11 |
| kgf_alim | 0.02 | 0.1 | 0.07 | -0.02 |
| kgf_temerrut | 0.05 | 0.2 | 0.06 | -0.03 |
| bes_vazgecme | 0.1 | 0.6 | -0.01 | 0.04 |
| phi | 0 | 0.03 | 0.03 | -0.01 |
| onlem | 0.2 | 0.8 | -0.00 | 0.02 |
| prim_odeme | 0.4 | 1 | 0.00 | 0.00 |

**Orta** (taban 3.78)

| parametre | düşük uç değeri | yüksek uç değeri | Δ düşük | Δ yüksek |
|:--|--:|--:|--:|--:|
| duz_oran | 0.105 | 0.27 | -1.55 | 7.00 |
| n_toplam | 119000 | 475000 | -1.91 | 3.81 |
| s_kayitli | 0 | 0.489 | 2.12 | 0.00 |
| sigma | 1.25 | 2 | 2.06 | -0.72 |
| marj | 0.35 | 0.65 | 0.91 | -0.98 |
| ort_H_W | 30 | 85 | -0.44 | 0.82 |
| u_ucretli | 0 | 0.4 | 0.74 | -0.74 |
| prim_k | 3 | 12 | 0.54 | -0.25 |
| myo_uygun | 0.1 | 0.6 | 0.28 | -0.28 |
| prim_toplama | 0.5 | 1 | -0.24 | 0.00 |
| kdv_donanim_pay | 0.2 | 0.6 | 0.20 | -0.20 |
| kgf_alim | 0.02 | 0.1 | 0.06 | -0.10 |
| kgf_temerrut | 0.05 | 0.2 | 0.05 | -0.10 |
| bes_vazgecme | 0.1 | 0.6 | -0.07 | 0.07 |
| phi | 0 | 0.03 | 0.02 | -0.04 |
| onlem | 0.2 | 0.8 | -0.01 | 0.01 |
| prim_odeme | 0.4 | 1 | 0.00 | 0.00 |

**İyimser** (taban 11.04)

| parametre | düşük uç değeri | yüksek uç değeri | Δ düşük | Δ yüksek |
|:--|--:|--:|--:|--:|
| duz_oran | 0.105 | 0.27 | -3.81 | 17.22 |
| n_toplam | 119000 | 475000 | -8.31 | 0.00 |
| s_kayitli | 0 | 0.489 | 5.23 | 0.00 |
| sigma | 1.25 | 2 | 2.67 | -3.83 |
| marj | 0.35 | 0.65 | 2.12 | -2.30 |
| u_ucretli | 0 | 0.4 | 1.36 | -2.26 |
| ort_H_W | 30 | 85 | -1.26 | 2.26 |
| prim_k | 3 | 12 | 1.65 | -0.75 |
| myo_uygun | 0.1 | 0.6 | 0.29 | -1.18 |
| prim_toplama | 0.5 | 1 | -0.73 | 0.00 |
| kdv_donanim_pay | 0.2 | 0.6 | 0.22 | -0.66 |
| bes_vazgecme | 0.1 | 0.6 | -0.26 | 0.07 |
| kgf_alim | 0.02 | 0.1 | 0.03 | -0.20 |
| kgf_temerrut | 0.05 | 0.2 | 0.01 | -0.20 |
| phi | 0 | 0.03 | 0.02 | -0.08 |
| onlem | 0.2 | 0.8 | -0.03 | 0.01 |
| prim_odeme | 0.4 | 1 | 0.00 | 0.00 |

## 4. Kırılma ızgarası (net): s × φ (sahte fatura)

**Kötümser** (satır φ, sütun s)

| φ \ s | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0.00 | 2.4 | 2.1 | 1.9 | 1.7 | 1.4 | 1.2 | 1.0 | 0.7 | 0.5 | 0.2 | 0.0 |
| 0.01 | 2.4 | 2.1 | 1.9 | 1.7 | 1.4 | 1.2 | 0.9 | 0.7 | 0.5 | 0.2 | 0.0 |
| 0.02 | 2.4 | 2.1 | 1.9 | 1.6 | 1.4 | 1.2 | 0.9 | 0.7 | 0.5 | 0.2 | -0.0 |
| 0.05 | 2.3 | 2.1 | 1.9 | 1.6 | 1.4 | 1.1 | 0.9 | 0.7 | 0.4 | 0.2 | -0.1 |
| 0.10 | 2.3 | 2.0 | 1.8 | 1.6 | 1.3 | 1.1 | 0.8 | 0.6 | 0.4 | 0.1 | -0.1 |
| 0.20 | 2.1 | 1.9 | 1.7 | 1.4 | 1.2 | 0.9 | 0.7 | 0.5 | 0.2 | 0.0 | -0.2 |

**Orta** (satır φ, sütun s)

| φ \ s | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0.00 | 6.7 | 6.1 | 5.5 | 4.9 | 4.3 | 3.7 | 3.1 | 2.6 | 2.0 | 1.4 | 0.8 |
| 0.01 | 6.7 | 6.1 | 5.5 | 4.9 | 4.3 | 3.7 | 3.1 | 2.5 | 1.9 | 1.4 | 0.8 |
| 0.02 | 6.6 | 6.0 | 5.5 | 4.9 | 4.3 | 3.7 | 3.1 | 2.5 | 1.9 | 1.3 | 0.8 |
| 0.05 | 6.6 | 6.0 | 5.4 | 4.8 | 4.2 | 3.6 | 3.0 | 2.5 | 1.9 | 1.3 | 0.7 |
| 0.10 | 6.5 | 5.9 | 5.3 | 4.7 | 4.1 | 3.5 | 2.9 | 2.3 | 1.8 | 1.2 | 0.6 |
| 0.20 | 6.2 | 5.7 | 5.1 | 4.5 | 3.9 | 3.3 | 2.7 | 2.1 | 1.5 | 0.9 | 0.3 |

**İyimser** (satır φ, sütun s)

| φ \ s | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0.00 | 18.3 | 16.8 | 15.3 | 13.8 | 12.4 | 10.9 | 9.4 | 7.9 | 6.5 | 5.0 | 3.5 |
| 0.01 | 18.2 | 16.8 | 15.3 | 13.8 | 12.3 | 10.9 | 9.4 | 7.9 | 6.4 | 5.0 | 3.5 |
| 0.02 | 18.2 | 16.7 | 15.2 | 13.8 | 12.3 | 10.8 | 9.3 | 7.9 | 6.4 | 4.9 | 3.5 |
| 0.05 | 18.1 | 16.6 | 15.2 | 13.7 | 12.2 | 10.7 | 9.2 | 7.8 | 6.3 | 4.8 | 3.4 |
| 0.10 | 17.9 | 16.5 | 15.0 | 13.5 | 12.0 | 10.6 | 9.1 | 7.6 | 6.1 | 4.7 | 3.2 |
| 0.20 | 17.6 | 16.1 | 14.7 | 13.2 | 11.7 | 10.2 | 8.8 | 7.3 | 5.8 | 4.3 | 2.9 |

## 5. Sızıntı (sizinti) × kimlik kiralama (kiralama)

**Kötümser** (satır kiralama, sütun sızıntı)

| kiralama \ sızıntı | 0.00 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|:--|--:|--:|--:|--:|--:|--:|
| 0.00 | 2.36 | 2.28 | 2.17 | 1.97 | 1.58 | 1.18 |
| 0.02 | 2.30 | 2.22 | 2.11 | 1.91 | 1.52 | 1.12 |
| 0.05 | 2.21 | 2.13 | 2.01 | 1.82 | 1.43 | 1.03 |
| 0.10 | 2.06 | 1.98 | 1.86 | 1.67 | 1.27 | 0.88 |
| 0.20 | 1.76 | 1.68 | 1.56 | 1.36 | 0.97 | 0.58 |

**Orta** (satır kiralama, sütun sızıntı)

| kiralama \ sızıntı | 0.00 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|:--|--:|--:|--:|--:|--:|--:|
| 0.00 | 3.78 | 3.59 | 3.30 | 2.82 | 1.86 | 0.91 |
| 0.02 | 3.63 | 3.44 | 3.15 | 2.67 | 1.72 | 0.76 |
| 0.05 | 3.41 | 3.22 | 2.93 | 2.45 | 1.50 | 0.54 |
| 0.10 | 3.04 | 2.85 | 2.56 | 2.08 | 1.13 | 0.17 |
| 0.20 | 2.30 | 2.11 | 1.82 | 1.35 | 0.39 | -0.57 |

**İyimser** (satır kiralama, sütun sızıntı)

| kiralama \ sızıntı | 0.00 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|:--|--:|--:|--:|--:|--:|--:|
| 0.00 | 11.04 | 10.57 | 9.86 | 8.69 | 6.34 | 4.00 |
| 0.02 | 10.68 | 10.21 | 9.50 | 8.33 | 5.98 | 3.63 |
| 0.05 | 10.13 | 9.66 | 8.96 | 7.78 | 5.44 | 3.09 |
| 0.10 | 9.23 | 8.76 | 8.05 | 6.88 | 4.53 | 2.19 |
| 0.20 | 7.42 | 6.95 | 6.24 | 5.07 | 2.72 | 0.37 |

## 6. Birlikte en kötü / en iyi uç

| Senaryo | Taban | En kötü | En iyi |
|:--|--:|--:|--:|
| Kötümser | 2.36 | 1.64 | 12.50 |
| Orta | 3.78 | 1.70 | 19.13 |
| İyimser | 11.04 | 1.72 | 20.44 |

## 7. Sınırlılıklar

- N aralığı 2021–2025 niyet serisinden türetildi; yalnızca iki sayı noktası (2021, 2025) ve beş yıl var. Niyet ≠ katılım: kendi işyeri kurmak isteyen işsiz sayısı, mikro mükellefiyete geçecek kişi sayısının bir vekilidir. Serbest çalışanların geçişi bu sayıya dahil değil.
- Brezilya analogu (%19–20) yalnızca dış sınır; Türkiye'de bu oran verilerle doğrulanmadı.
- s, φ, sızıntı, kiralama, π, KGF, BES: veri yok, varsayım. Sonuçların bunlara duyarlılığı §3–§5'te.
- Model yalnızca 4. yıl ve 5 yıllık NPV verir; ilk yıl etkisi ve genç seyri bu raporda yok.

