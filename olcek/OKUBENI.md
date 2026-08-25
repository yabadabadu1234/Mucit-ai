# `olcek` — performans muhasebesi

Kaynaklar: `docs/kaynak/l4_gpu_hiz_raporu.md`,
`docs/kaynak/veri_akis_hizi.tex`. Tashihler: **M31–M34**.

```
python3 -m pytest olcek -q         # 29 sınama
python3 -m olcek.hiz
```

## L4 raporu DOĞRU — bütün aritmetiği yeniden hesaplandı

Net güç `4×242 TFLOPS × 0.65 = 629.2 TFLOPS`; `90·D²` FLOP/token
(41 meleke `82D²` + RHT `4D²` + KAN `2D²` + Hodge `2D²`).

| `D` | FLOP/token | token/sn | metin MB/sn | rapor | tensör GB/sn |
|---|---|---|---|---|---|
| 4096 | 1.51e9 | 4.167e5 | 1.67 | 1.67 ✓ | 3.41 |
| 2048 | 3.775e8 | 1.667e6 | 6.67 | 6.67 ✓ | 6.83 |
| 1024 | 9.437e7 | 6.667e6 | 26.67 | 26.68 ✓ | 13.65 |
| 512 | 2.359e7 | 2.667e7 | 106.68 | 106.72 ✓ | 27.31 |

## M34 — raporun yazılmamış şartı (hata değil, eksik)

| `D` | `B` | yoğunluk (FLOP/bayt) | çatı (FLOP/sn) | durum |
|---|---|---|---|---|
| 512 | 1 | 1.0 | 3.00e11 | bellek-bağlı |
| 512 | 4096 | 3021.6 | 1.573e14 | FLOP-bağlı |
| 4096 | 1 | 1.0 | 3.00e11 | bellek-bağlı |
| 4096 | 4096 | 3921.7 | 1.573e14 | FLOP-bağlı |

`B=1`'de tepe gücün **1/524**'ü. FLOP-bağlı olmak için her iki boyutta
da **`B ≥ 1024`**. Şart yazılmazsa rapor tek cümlelik etkileşimli
kullanımda 500 kat iyimser okunur.

## M31–M33 — veri akış risalesinin üç hatası

| Tashih | Risale | Ölçülen |
|---|---|---|
| **M31** `log²N`, `N=10¹²` | `20² = 400` | `log₂²N = **1589.1**` (log₁₀ ile 144, ln ile 763 — hiçbiri 400) |
| **M32** `N³/log²N` | `1e28` | **6.293e+32** (`N²` alınsaydı 6.293e20; o da değil) |
| **M33** `Efektif Hız = Fizikî Hız × K` | `10^18 GB/sn` | **boyutça geçersiz**: `K` boyutsuz bir orandır |

**Çelişkinin ölçülen büyüklüğü.** Risalenin yazdığı `10^18 GB/sn`
(= 1e27 bayt/sn), aynı külliyattaki L4 raporunun `D=512` rakamından
(1.07e8 bayt/sn) **19 mertebe**, `D=4096`'dan **21 mertebe** uzak.
Formül harfiyen uygulanırsa (`1.2 TB/sn × K`) `7.55e44` bayt/sn çıkar —
**37 mertebe** fark. (Önce "22 mertebe" yazmıştım; ölçüm düzeltti.)

Doğru ayrım: *eşdeğer klasik iş* birimi **FLOP**, *fizikî veri hızı*
birimi **bayt/sn**. İkisi aynı cümlede çarpılamaz.

## Bu makinede gerçek ölçüm (GPU yok, CPU)

| `D` | `B` | süre (ms) | GFLOP/sn | token/sn |
|---|---|---|---|---|
| 128 | 1 | 0.121 | 11.1 | 8253 |
| 128 | 64 | 0.825 | 104.2 | 77549 |
| 512 | 1 | 1.673 | 12.8 | 598 |
| 512 | 64 | 5.882 | 233.9 | 10880 |

Aynı çatı etkisi bu CPU'da da görünüyor: yığın 1→64 olunca GFLOP/sn
**18×** artıyor. Varsayılan boyut 512, hızlı deneme 128.

**Sınamanın yakaladığı kusur.** Ölçüm 41 ardışık çarpımda float32
**taşıyordu** (inf/nan). Ağırlıklar `1/√D` ile ölçeklendi; FLOP sayısı
değişmedi, sayılar sınırda kaldı ve `sonlu_mu` alanı bunu her koşuda
denetliyor.
