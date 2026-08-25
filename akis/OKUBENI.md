# `akis` — hacimsel akışlar, Lie cebri, tıkızlaştırma

Kaynak: `docs/kaynak/analitik_darbogazlar.txt` ve
`docs/kaynak/kulli_ogrenme_nazariyesi.tex` içindeki tashihli formüller.
Aşağıdaki bütün sayılar **ölçülmüştür**; her biri `python3 -m akis.<modül>`
gösterimi veya `akis/test_akis.py` içindeki bir sınama ile üretilir.

```
python3 -m pytest akis/test_akis.py -q      # 53 geçti, ~27 s
python3 -m akis.hacim ; python3 -m akis.lie ; python3 -m akis.tikiz
```

## 1. `hacim.py` — akışlar

| Hüküm | Ölçüm |
|---|---|
| Ortalama eğrilik akışı kapalı çözümle uyuşuyor: `r(t) = √(r₀²−2t)` | `T=0.45`: ölçülen 0.316342 / kapalı 0.316228, bağıl hata **3.6e-04** |
| MCF alanı **her adımda** azaltır (`d/dt Alan = −∫|H|²`) | çember/elips/gürültülü üçünde de artan adım sayısı **0** |
| Fokker–Planck akı biçiminde kütle korunur, negatif yoğunluk çıkmaz | kütle sapması **3.3e-16**, negatif **yok** |
| Log-yoğunluk denklemi `∂_t u = Δu + ‖∇u‖² + ∇u·∇f + Δf` aynı çözüme gider | Fokker–Planck ile L¹ farkı **1.5e-04**, `ρ=e^u` yapı gereği pozitif |
| Gibbs hacmi `d/dt Vol = −2∫‖∇f‖²e^{−f}` | `2cos x`: ölçülen **−39.972048**, kapalı **−39.969038** (fark 3.0e-03); `∇f=0` iken tam 0 |
| Eyer ölçütü (K23): `λ_max>0` **yetmez**, hem pozitif hem negatif özdeğer gerek | yerel asgarîde `λ_max>0` ama eyer değil; kaçış yönünde q=−1.000 |

**Düzeltilen iki yanlışım.** (a) MCF'de `dt`yi başlangıç `h²`sinde sabit
tutmak eğri küçüldükçe CFL'i ihlâl ediyordu — `T=0.45`'te %36 hata. Adım
başına uyarlanan `dt = 0.2·h²` ile 3.6e-04'e indi. (b) Gibbs hacmi için
"kısmî integrasyonla sıfır" yazmıştım; ölçüm −39.97 verdi. Doğru türetme
`(Δf+‖∇f‖²)e^{−f} = ∇·(e^{−f}∇f) + 2‖∇f‖²e^{−f}` — yani kesin negatif.

## 2. `lie.py` — Lie cebri ve grupta kalma

| Hüküm | Ölçüm |
|---|---|
| Jacobi özdeşliği `so(n)`de sağlanıyor | hata **8e-17 … 4e-16** |
| `so(3)` yapı sabitleri = Levi-Civita | azamî sapma **2.22e-16**, yapı sabiti Jacobi hatası 1.25e-16 |
| `su(n)` boyutu `n²−1` | 3 / 8 / 15; Jacobi hatası ≤ **1.16e-14** |
| Jacobi bir **kısıttır**, keyfî `f` sağlamaz | rastgele `f`: hata **31.07** |
| Üstel harita: özayrışım her ölçekte grupta kalır, seri kalmaz | `‖A‖=75.8`: seri SO(5) dışında, fark **4.65e+19**; özayrışım içeride |
| Naif adım grubu terk eder, üstel adım etmez | 5 adım sonra naif det **1.7011**, üstel det **1.000000** (`‖XᵀX−I‖ = 2.4e-15`) |
| K28: geri getirme **kutupsal ayrışımla**, simetrikleştirmeyle değil | simetrik `‖XᵀX−I‖ = 0.5543`, kutup **8.80e-16**; 300 rastgele dik dizeyin **0**'ı daha yakın |

## 3. `tikiz.py` — tıkızlık ve kritik lokus

| Hüküm | Ölçüm |
|---|---|
| Zorlayıcılık küre **asgarîsine** bakılarak sınanır | `‖x‖²`, `‖x‖⁴−‖x‖²` zorlayıcı; `−‖x‖²`, `x₀`, `x₀²` değil |
| Alt-seviye kümesi boş olabilir; "sınırlı" tek başına yetmez | `r=−3.50`'de küme boş, nokta araması bunu yakalıyor |
| Barriyeri kırpmak NaN'ı önler ama kısıtı gevşetir | `g=[−0.5,1]`: kırpmasız **inf**, kırpmalı **18.42** |
| İç nokta yolu kısıtı hiç ihlâl etmeden sınıra yaklaşır | `τ=2.44e-04`'te `f=7e-06`, `min g = 2e-06`, ihlâl **0** |
| Morse **bağıntısı** eşitliktir (K27) | `M=[2,1,0]`, `Σ(−1)^k M_k = 1 = χ(ℝ²)`; `≥` ölçütü `M=[5,0,0]`'ı da geçirirdi |
| Alexandroff: `ℝⁿ∪{∞} ≅ Sⁿ` | 500 noktada gidiş-dönüş sapması **1.24e-07**; kuzey kutbu reddediliyor |

**Sınama sırasında bulunan gerçek kusur.** Zorlayıcılık, küre asgarîsini
salt rastgele 64 yönle arıyordu. `f(x) = x₀²` yalnız `v₀=0` düzleminde
sıfırdır ve rastgele yön oraya tam düşmez; asgarîler `8e-14 → 8e-08` gibi
*artan* görünüp fonksiyon yanlışlıkla zorlayıcı çıkıyordu. İki ekleme
yapıldı: (1) en iyi adaylardan başlayan, küre üzerinde teğet izdüşümlü
sonlu farklı iniş (`_kurede_asgari`) — dejenere yönü gerçekten buluyor;
(2) asgarî/medyan oranı ölçütü — `x₀²`de oran **3e-13**, `‖x‖²`de 1.
İkisiyle birlikte hüküm doğru çıkıyor.

**Düzeltilen bir yanlışım daha.** Morse bağıntısı için "χ=2" yazmıştım;
ölçüm 1 verdi ve doğru olan odur (`χ(ℝ²)=1`). Alt-seviye kümeleri eyer
değerinin altında iki ayrı disk, üstünde tek bölgedir.
