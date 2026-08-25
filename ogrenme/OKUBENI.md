# `ogrenme` — RKHS, operatör öğrenmesi, ızgara, Grassmann

Kaynak: `docs/kaynak/kulli_ogrenme_nazariyesi.tex`,
`kuantum_operator_ogrenmesi.tex`, `analitik_darbogazlar.txt`
(K19, K24, K25, K26, K30, K35 tashihleri).

```
python3 -m pytest ogrenme -q            # 98 sınama
python3 -m ogrenme.rkhs ; python3 -m ogrenme.operator
python3 -m ogrenme.izgara ; python3 -m ogrenme.grassmann
```

## 1. `rkhs.py` — çekirdek Hilbert uzayı

| Hüküm | Ölçüm |
|---|---|
| Moore–Aronszajn: çekirdek **PSD olmalı** | Gauss/Laplace/Matérn(½,3/2,5/2)/polinom: en küçük özdeğer ≥ −1.0e-13 |
| K24: salınımlı faz çekirdeği PSD **değil** | en küçük özdeğer **−5.8979** → temsil teoremi orada geçersiz |
| `λ` küçüldükçe eğitim artığı düşer, koşul sayısı patlar | `λ=1e-9`: koşul **3.5e+10**, sınama hatası 3.05e-02; en iyi sınama `λ=1e-3`'te 2.21e-02 |
| Nyström: `m` büyütmek bir yerden sonra fayda etmiyor | `m=600`'de hata 1.8e-05; tam Gram'ın sayısal rütbesi **250**'de doyuyor, hatayı artık kırpma eşiği belirliyor |
| Asıl kazanç **bellekte** | `m=20`: 0.14 MB / 6.48 MB → **45×** tasarruf |

**Düzeltilen yanlış beklenti.** `m=N`'de makine hassasiyeti beklemiştim;
ölçüm 5.2e-05 verdi. Araştırınca atılan özdeğer kütlesi 6e-14 çıktı —
yani sebep kesme değil, **sözde tersin koşullanması**. Sınama tam bunu
tartacak şekilde yeniden yazıldı.

## 2. `operator.py` — DeepONet / FINO

| Hüküm | Ölçüm |
|---|---|
| Kesilmiş SVD **en iyi** ayrışım (Eckart–Young) | ölçülen Frobenius hatası kapalı formla (`√Σ_{r>R}σ_r²`) **1e-9** içinde uyuşuyor |
| FINO ayrık çarpım = tam dizey | fark **4.4e-16**; `K=48`'de hız kazancı yok (0.56×), kazanç parametrede: `K=1024`, rütbe 8 → **64×** |
| K30: ölçek çarpanı **norma** girer, alana değil | doğru `‖v‖_L² = 0.7071067812` her `N`de; yanlış ölçekleme `N` ile `1/√N` gibi çöküyor (0.125 → 0.0156) |
| DeepONet ALS | test hatası **0.083** |

**İki gerçek kusur ve çözümü.** (a) ALS'de ölçek dejenerasyonu
(`cW_d, W_t/c`) normları 6e3/9e4'e uçuruyordu; `λ=1e-4` + tur başına
çarpan dengelemesiyle oturdu. (b) Hedef operatör **doğrusal** olduğu
için ham girdi dal öznitelikleri arasına eklendi; test hatası 0.80 →
0.083. Kalan salınım (12 turun 2'sinde ‰0.4) ALS'in **düzenlenmiş**
hedefi eniyilemesinden geliyor — açıklanıyor, örtülmüyor.

## 3. `izgara.py` — adaptif B-spline ızgarası ve sembolik kapanış

| Hüküm | Ölçüm |
|---|---|
| Zincir kuralı düğüm parametrelerinde doğru | `kuyruk = cumsum(dL/dt tersten)`; sonlu farkla uyuşuyor |
| Sadelik cezası **sıralamayı** bozar, **kabulü** bozmaz | `μ=0`'da doğru cevap (tanh) kazanıyor; `μ=0.02`'de sadelik `x`'i öne alıyor ama kabul eşiği o seçimi **reddediyor** |
| Kütüphanede tam olan hedefte ceza zararsız | `sin(3x)` her `μ`da kazanıyor (puan 1.000 → 0.400) |

## 4. `grassmann.py` — Grassmann manifoldu (K25, K26)

| Hüküm | Ölçüm |
|---|---|
| İzdüşüm `P = U(UᵀU)⁻¹Uᵀ` kanonik | `‖P−Pᵀ‖ = 4e-17`, `‖P²−P‖ = 8e-17`, `tr P = k` tam; taban döndürülünce `‖ΔP‖ = 4e-16` ama `‖Y−YQ‖ = 2.79` |
| **K26**: Log'da `arctan`, `arcsin` değil | gidiş-dönüş hatası — `θ_max=0.31`: arctan **6.4e-16**, arcsin **2.4e-02**; `θ_max=0.79`: arctan **8.2e-16**, arcsin **1.00** |
| Kaynağın `Tr(Exp(Log)) = Tr(G₂)` ölçütü **zayıf** | yanlış Log ile bile iz 3.0000000000 = hedefin izi; ama izdüşüm farkı **0.7154** |
| `‖Log‖_F = d_Gr` | 4 halde 1e-10 içinde |
| Geodezik doğrusal ve üçgeni kapatıyor | doğrusallık hatası ≤ **5.3e-15**, üçgen kapanma ≤ 1.0e-14 |
| Karcher ortalaması Öklit ortalamasından iyi ve taban**sız** | `Σd²` 13.446313 / 18.570492; taban değişince Karcher `‖ΔP‖ = 4e-15`, Öklit **1.2567** |
| **K25**: Tikhonov çekirdeği yok eder | 3 bileşenli çizgede `β₀ = 3`; `ker(L+εI) = 0`, `ε`a eşit özdeğer 3, kayma hatası 3.6e-16 |

**İki ölçüm düzeltmesi.** (a) `θ_max = π/2`'de `arctan` da bozuluyor
(7.9e-01): orası **kesim lokusudur**, `M = Y₁ᵀY₂` tekilleşir ve Log tek
değildir — Grassmann'ın kendi özelliği, kod kusuru değil; belgeye
yazıldı. (b) Karcher yinelemesine öntanımlı 60 tur vermiştim; ölçüm
artığın orada daha **3e-05** olduğunu gösterdi. Yakınsama **doğrusal**
(adım başına ~0.8 kat), 1e-13'e inmesi **307** tur alıyor; öntanım 400
yapıldı. İlginç olan, `Σd²`nin 60 turda da aynı çıkması: ortalamanın
*değeri* erken oturuyor, *artık* geç iniyor.
