# `hesap` — tam aritmetik, `p`-adik norm, saklama maliyeti

Kaynak: `docs/kaynak/kuantum_hudutsuzluk.tex`.
Tashihler: **M23, M24, M25/M26, M27**.

```
python3 -m pytest hesap -q         # 35 sınama
python3 -m hesap.galois ; python3 -m hesap.padic ; python3 -m hesap.saklama
```

## `galois.py` — `ℤ[ζ₈][1/√2]` halkası

Kaynağın Galois iddiası **doğrudur ve gerçekten kodlanmıştır**:
`√2 = ζ₈+ζ₈⁷`, `i = ζ₈²`, Hadamard tam temsil ediliyor.

| Hüküm | Ölçüm |
|---|---|
| `√2·√2` tam olarak 2 | `Z8(2,0,0,0)` — **tamsayı eşitliği** |
| `i² = −1` | `Z8(-1,0,0,0)` — tam |
| Clifford+T halkada kapalı | 10/50/200/1000 kapıda `‖v‖²` tamsayı aritmetiğinde **tam 1** |
| float'ta hata birikiyor | `‖v‖²−1`: 5000 kapıda float64 **1.9e-13**, float32 **3.9e-05** |
| Asıl kazanç: **karar verilebilirlik** | `H T⁸ H` devresi tam aritmetikte `|0⟩`a **tam eşit**; float'ta eşit değil (sapma 4.7e-16), eşik seçmeden cevaplanamaz |

**Bedeli.** Süre float'tan **15–28 kat** yavaş. Bit uzunluğu ise
beklediğimden çok yavaş büyüyor: 100/400/1600/6400 kapıda **1, 6, 11, 36
bit**. ("Kapı sayısının yarısı kadar" yazmıştım; ölçüm yalanladı — sebep
`sade()`deki çift katsayı sadeleşmesi.)

**Sınamanın yakaladığı gerçek kusur.** `_yukselt`te `√2` ile çarpma
katsayı dönüşümünü yanlış yazmıştım. Doğrusu
`(a+bζ+cζ²+dζ³)(ζ−ζ³) = (b−d) + (a+c)ζ + (b+d)ζ² + (c−a)ζ³`.
Hata yalnız farklı `k` üsleri toplanınca ortaya çıkıyordu; rastgele devre
sınamaları **geçiyordu**, cebir tutarlılık sınaması yakaladı.

## `padic.py` — ultrametrik ve iki yanlış teşhis

| Hüküm | Ölçüm |
|---|---|
| Ultrametrik eşitsizlik (kaynak doğru) | `p=2,3,5`: 20 000 çiftte **0 ihlal**; `\|x\|≠\|y\|` olan her çiftte **eşitlik** (izoseles) |
| **M25/M26** terim | adı *ultrametrik*; "ultradinamik" diye bir sınıf yok |
| **M23** `Σ\|c\|_p² = 1` normalizasyon değil | `(½,½,½,½)`: arşimet **1**, `p`-adik **16**; `(3/5,4/5,0,0)`: 1 / **17/16**; `(⅓,⅔,⅔,0)`: 1 / **3/2** |
| **M23** üniter altında korunmuyor | Pisagor dönmesinde arşimet **200/200**, `p`-adik **78/200** |
| **M24** yuvarlama irrasyonellikten değil | `0.1+0.2 ≠ 0.3` (5.55e-17); `0.1` on kere → `0.99999999999999989`. Hepsi **rasyonel** |
| `p`-adik yakınsama arşimetin tersi | `Σ2^k` arşimet ıraksıyor, ardışık farkların 2-adik normu `0.5 → 0.0156` |

`(1,0,0,0)` hâlinde iki ölçüt de 1 veriyor — **tek örnekle sınamak bu
farkı gizlerdi**; o yüzden dört örnek var.

## `saklama.py` — M27: "N>400 saklanamaz" iddiasının dürüst hâli

| Hüküm | Ölçüm |
|---|---|
| İtiraz **keyfî** durum için DOĞRU | `N=300`: `10^90.3` katsayı — evren atomundan **10^10 kat** fazla |
| Kararlayıcı durumlar `O(N²)` | `N=1024`: **4.1 MB**, 2047 kapı **128 ms**, ölçüm 0.7 ms |
| Doğruluk sağlaması | Bell durumu: ilk ölçüm rastgele, ikinci **belirli** ve eşit — **200/200** |
| MPS `O(Nχ²)` | `N=4096, χ=32`: **134 MB**; norm tam vektörle 1e-12'de uyuşuyor |
| **Bedava sonsuzluk yok** | hacim yasası dolaşıklığında `χ ~ 2^{N/2}` ve maliyet keyfî duruma geri dönüyor (`N=80`: log₁₀bayt 27.5 / 25.3) |

Doğru cevap "sınır yoktur" değil, **hangi yapılı sınıfta olunduğunu
yazmaktır**. Kararlayıcı durumlar Gottesman–Knill gereği klasik olarak
verimli benzetilir — ucuz olmalarının sebebi budur.
