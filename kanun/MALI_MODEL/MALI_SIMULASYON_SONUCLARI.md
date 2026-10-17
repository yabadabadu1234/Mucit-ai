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
| Kötümser | 2.92 | 3.59 | 5.92 | 9.52 | 11.19 | 1.000 | 17.66 |
| Orta | 3.95 | 4.90 | 8.49 | 14.47 | 17.32 | 1.000 | 25.47 |
| İyimser | 6.80 | 7.98 | 12.66 | 20.36 | 23.85 | 1.000 | 38.09 |

## 2. Spearman duyarlılığı (ilk 6)

- **Kötümser:** duz_oran +0.77, medyan_W +0.40, n_toplam +0.34, s_kayitli -0.27, u_ucretli -0.10, marj -0.07
- **Orta:** duz_oran +0.74, medyan_W +0.43, n_toplam +0.31, s_kayitli -0.27, u_ucretli -0.14, marj -0.13
- **İyimser:** n_toplam +0.31, s_kayitli +nan, duz_oran +0.85, medyan_W +0.32, marj -0.11, u_ucretli -0.10

## 3. Tek parametre tornado (17 parametre; düşük / yüksek uç)

**Kötümser** (taban 4.56)

| parametre | düşük uç değeri | yüksek uç değeri | Δ düşük | Δ yüksek |
|:--|--:|--:|--:|--:|
| n_toplam | 255000 | 1.047e+06 | 0.00 | 14.31 |
| duz_oran | 0.105 | 0.27 | -1.22 | 5.59 |
| medyan_W | 3 | 8 | -1.10 | 3.21 |
| s_kayitli | 0 | 0.489 | 0.00 | -1.68 |
| u_ucretli | 0 | 0.4 | 0.75 | -0.45 |
| prim_k | 3 | 12 | 0.75 | -0.34 |
| sigma | 0.6 | 1.2 | -0.63 | 0.20 |
| kdv_donanim_pay | 0.2 | 0.6 | 0.34 | -0.11 |
| prim_toplama | 0.5 | 1 | -0.33 | 0.00 |
| marj | 0.35 | 0.65 | 0.23 | -0.23 |
| myo_uygun | 0.1 | 0.6 | 0.21 | -0.05 |
| kgf_alim | 0.02 | 0.1 | 0.14 | -0.05 |
| kgf_temerrut | 0.05 | 0.2 | 0.12 | -0.06 |
| bes_vazgecme | 0.1 | 0.6 | -0.02 | 0.09 |
| phi | 0 | 0.03 | 0.05 | -0.03 |
| onlem | 0.2 | 0.8 | -0.01 | 0.04 |
| prim_odeme | 0.4 | 1 | 0.00 | 0.00 |

**Orta** (taban 4.73)

| parametre | düşük uç değeri | yüksek uç değeri | Δ düşük | Δ yüksek |
|:--|--:|--:|--:|--:|
| n_toplam | 255000 | 1.047e+06 | -1.11 | 10.28 |
| duz_oran | 0.105 | 0.27 | -1.94 | 8.80 |
| s_kayitli | 0 | 0.489 | 2.60 | 0.00 |
| medyan_W | 3 | 8 | -1.72 | 1.80 |
| marj | 0.35 | 0.65 | 1.10 | -1.16 |
| u_ucretli | 0 | 0.4 | 0.93 | -0.93 |
| prim_k | 3 | 12 | 0.55 | -0.25 |
| kdv_donanim_pay | 0.2 | 0.6 | 0.31 | -0.31 |
| sigma | 0.6 | 1.2 | -0.27 | -0.08 |
| myo_uygun | 0.1 | 0.6 | 0.24 | -0.24 |
| prim_toplama | 0.5 | 1 | -0.24 | 0.00 |
| kgf_alim | 0.02 | 0.1 | 0.07 | -0.12 |
| kgf_temerrut | 0.05 | 0.2 | 0.06 | -0.12 |
| bes_vazgecme | 0.1 | 0.6 | -0.08 | 0.08 |
| phi | 0 | 0.03 | 0.03 | -0.06 |
| onlem | 0.2 | 0.8 | -0.02 | 0.02 |
| prim_odeme | 0.4 | 1 | 0.00 | 0.00 |

**İyimser** (taban 8.77)

| parametre | düşük uç değeri | yüksek uç değeri | Δ düşük | Δ yüksek |
|:--|--:|--:|--:|--:|
| duz_oran | 0.105 | 0.27 | -3.07 | 13.90 |
| n_toplam | 255000 | 1.047e+06 | -3.95 | 11.16 |
| s_kayitli | 0 | 0.489 | 4.12 | 0.00 |
| medyan_W | 3 | 8 | -3.88 | 1.83 |
| u_ucretli | 0 | 0.4 | 1.09 | -1.82 |
| marj | 0.35 | 0.65 | 1.64 | -1.75 |
| prim_k | 3 | 12 | 1.10 | -0.50 |
| myo_uygun | 0.1 | 0.6 | 0.18 | -0.70 |
| kdv_donanim_pay | 0.2 | 0.6 | 0.22 | -0.66 |
| prim_toplama | 0.5 | 1 | -0.49 | 0.00 |
| sigma | 0.6 | 1.2 | -0.17 | -0.39 |
| bes_vazgecme | 0.1 | 0.6 | -0.21 | 0.05 |
| kgf_alim | 0.02 | 0.1 | 0.02 | -0.16 |
| kgf_temerrut | 0.05 | 0.2 | 0.01 | -0.16 |
| phi | 0 | 0.03 | 0.01 | -0.07 |
| onlem | 0.2 | 0.8 | -0.02 | 0.00 |
| prim_odeme | 0.4 | 1 | 0.00 | 0.00 |

## 4. Kırılma ızgarası (net): s × φ (sahte fatura)

**Kötümser** (satır φ, sütun s)

| φ \ s | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0.00 | 4.6 | 4.2 | 3.7 | 3.3 | 2.9 | 2.5 | 2.0 | 1.6 | 1.1 | 0.7 | 0.3 |
| 0.01 | 4.6 | 4.2 | 3.7 | 3.3 | 2.9 | 2.4 | 2.0 | 1.6 | 1.1 | 0.7 | 0.3 |
| 0.02 | 4.6 | 4.1 | 3.7 | 3.3 | 2.8 | 2.4 | 2.0 | 1.5 | 1.1 | 0.7 | 0.2 |
| 0.05 | 4.5 | 4.0 | 3.6 | 3.2 | 2.8 | 2.3 | 1.9 | 1.5 | 1.0 | 0.6 | 0.2 |
| 0.10 | 4.4 | 3.9 | 3.5 | 3.1 | 2.6 | 2.2 | 1.8 | 1.3 | 0.9 | 0.5 | 0.0 |
| 0.20 | 4.1 | 3.7 | 3.2 | 2.8 | 2.4 | 1.9 | 1.5 | 1.1 | 0.7 | 0.2 | -0.2 |

**Orta** (satır φ, sütun s)

| φ \ s | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0.00 | 8.1 | 7.4 | 6.7 | 6.0 | 5.4 | 4.7 | 4.0 | 3.3 | 2.6 | 1.9 | 1.2 |
| 0.01 | 8.1 | 7.4 | 6.7 | 6.0 | 5.3 | 4.7 | 4.0 | 3.3 | 2.6 | 1.9 | 1.2 |
| 0.02 | 8.1 | 7.4 | 6.7 | 6.0 | 5.3 | 4.6 | 3.9 | 3.2 | 2.6 | 1.9 | 1.2 |
| 0.05 | 8.0 | 7.3 | 6.6 | 5.9 | 5.2 | 4.5 | 3.9 | 3.2 | 2.5 | 1.8 | 1.1 |
| 0.10 | 7.8 | 7.2 | 6.5 | 5.8 | 5.1 | 4.4 | 3.7 | 3.0 | 2.3 | 1.6 | 1.0 |
| 0.20 | 7.6 | 6.9 | 6.2 | 5.5 | 4.8 | 4.1 | 3.4 | 2.8 | 2.1 | 1.4 | 0.7 |

**İyimser** (satır φ, sütun s)

| φ \ s | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 0.00 | 14.2 | 13.1 | 12.0 | 10.9 | 9.8 | 8.7 | 7.5 | 6.4 | 5.3 | 4.2 | 3.1 |
| 0.01 | 14.2 | 13.1 | 12.0 | 10.9 | 9.7 | 8.6 | 7.5 | 6.4 | 5.3 | 4.2 | 3.1 |
| 0.02 | 14.2 | 13.1 | 11.9 | 10.8 | 9.7 | 8.6 | 7.5 | 6.4 | 5.3 | 4.2 | 3.0 |
| 0.05 | 14.1 | 13.0 | 11.9 | 10.8 | 9.6 | 8.5 | 7.4 | 6.3 | 5.2 | 4.1 | 3.0 |
| 0.10 | 14.0 | 12.8 | 11.7 | 10.6 | 9.5 | 8.4 | 7.3 | 6.2 | 5.1 | 3.9 | 2.8 |
| 0.20 | 13.7 | 12.6 | 11.5 | 10.4 | 9.2 | 8.1 | 7.0 | 5.9 | 4.8 | 3.7 | 2.6 |

## 5. Sızıntı (sizinti) × kimlik kiralama (kiralama)

**Kötümser** (satır kiralama, sütun sızıntı)

| kiralama \ sızıntı | 0.00 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|:--|--:|--:|--:|--:|--:|--:|
| 0.00 | 4.56 | 4.40 | 4.17 | 3.78 | 3.00 | 2.22 |
| 0.02 | 4.44 | 4.28 | 4.05 | 3.66 | 2.88 | 2.09 |
| 0.05 | 4.26 | 4.10 | 3.87 | 3.48 | 2.69 | 1.91 |
| 0.10 | 3.95 | 3.80 | 3.56 | 3.17 | 2.39 | 1.61 |
| 0.20 | 3.35 | 3.20 | 2.96 | 2.57 | 1.79 | 1.01 |

**Orta** (satır kiralama, sütun sızıntı)

| kiralama \ sızıntı | 0.00 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|:--|--:|--:|--:|--:|--:|--:|
| 0.00 | 4.73 | 4.49 | 4.13 | 3.53 | 2.32 | 1.12 |
| 0.02 | 4.54 | 4.30 | 3.94 | 3.34 | 2.14 | 0.94 |
| 0.05 | 4.26 | 4.02 | 3.66 | 3.06 | 1.86 | 0.66 |
| 0.10 | 3.80 | 3.56 | 3.20 | 2.60 | 1.40 | 0.20 |
| 0.20 | 2.87 | 2.63 | 2.27 | 1.67 | 0.47 | -0.73 |

**İyimser** (satır kiralama, sütun sızıntı)

| kiralama \ sızıntı | 0.00 | 0.02 | 0.05 | 0.10 | 0.20 | 0.30 |
|:--|--:|--:|--:|--:|--:|--:|
| 0.00 | 8.77 | 8.39 | 7.82 | 6.87 | 4.98 | 3.09 |
| 0.02 | 8.47 | 8.10 | 7.53 | 6.58 | 4.69 | 2.80 |
| 0.05 | 8.04 | 7.66 | 7.09 | 6.14 | 4.25 | 2.36 |
| 0.10 | 7.31 | 6.93 | 6.36 | 5.41 | 3.52 | 1.63 |
| 0.20 | 5.85 | 5.47 | 4.90 | 3.95 | 2.06 | 0.17 |

## 6. Birlikte en kötü / en iyi uç

| Senaryo | Taban | En kötü | En iyi |
|:--|--:|--:|--:|
| Kötümser | 4.56 | 3.12 | 7.96 |
| Orta | 4.73 | 3.23 | 12.69 |
| İyimser | 8.77 | 3.27 | 13.52 |

## 7. Sınırlılıklar

- N aralığı 2021–2025 niyet serisinden türetildi; yalnızca iki sayı noktası (2021, 2025) ve beş yıl var. Niyet ≠ katılım: kendi işyeri kurmak isteyen işsiz sayısı, mikro mükellefiyete geçecek kişi sayısının bir vekilidir. Serbest çalışanların geçişi bu sayıya dahil değil.
- Brezilya analogu (%19–20) yalnızca dış sınır; Türkiye'de bu oran verilerle doğrulanmadı.
- s, φ, sızıntı, kiralama, π, KGF, BES: veri yok, varsayım. Sonuçların bunlara duyarlılığı §3–§5'te.
- Model yalnızca 4. yıl ve 5 yıllık NPV verir; ilk yıl etkisi ve genç seyri bu raporda yok.


## 8. Düzeltme kaydı (bu sürüm)

- **Kayıtlı 4/b primi çift sayılıyordu.** Önceki sürümlerde kayıtlı kişinin sürdürdüğü 4/b primi yasanın yeni geliri gibi toplanıyordu (Orta'da yaklaşık 18 milyar TL/yıl). Bu, mevcut durum (statüko) olduğu için yasanın net etkisine girmez; kaldırıldı. Sonuç: aynı girdilerle net değerler düştü.
- **s artık SGK verisine bağlı:** Orta ve İyimser = gözlenen kayıtlı oran (%48,9); Kötümser = 0 (en kötü sınır). Bu bağlama, kayıtlı kişinin gelirinin yeni vergi rejimine geçişini (vergi farkı) modeller; prim farkı artık sıfırdır.
- Köşe analizinde s'nin yönü düzeltildi: s'nin düşmesi kötüleştirir.
