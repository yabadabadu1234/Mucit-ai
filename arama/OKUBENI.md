# `arama` — kuantum asgarî arama ve dalga bükümü

Kaynaklar: `docs/kaynak/kuantum_asgari_arama.tex`,
`docs/kaynak/kuantum_dalga_bukum.tex`.
Tashihler: **M18–M22**.

```
python3 -m pytest arama -q         # 41 sınama
python3 -m arama.grover ; python3 -m arama.bukum
```

## Kaynağın doğru yazdığı yerler

Faz kehaneti `O_f = Σe^{iγf(x)}|x⟩⟨x|` üniter (ölçüldü: 4.4e-16);
eşik kehaneti, Grover difüzyonu ve `m ≈ (π/4)√(2^N/K)` doğru;
adiyabatik ölçüt `T ≥ ħ·max|⟨E₁|dH/dt|E₀⟩|/g_min²` doğru;
WKB `T = e^{−γ}` doğru.

## `grover.py`

| Hüküm | Ölçüm |
|---|---|
| Başarı `m` ile **tekdüze artmıyor** | `K=1`: `m_opt=25`'te **0.9995**, `2·m_opt`'ta **0.0002** |
| **M18** `K` bilinmezse `m` seçilemez | gerçek `K=64` iken `K=1` varsayıp `m=25` koşmak: başarı **0.0991**; doğru `m=3` ile **0.9613** |
| Dürr–Høyer `K` bilinmeden buluyor | `N=256/1024/4096`: **20/20** başarı, sorgu/√N = 2.27 / 2.93 / 3.11 |
| **M19** sonlu `T`de başarı tam 1 değil | `T=1`: 0.0884, `T=64`: 0.9964, `T=256`: **0.99998** — hiçbirinde tam 1 |

`%100` cümlesi ayrıca LaTeX'te `%` kaçırılmadığı için **tamamen
kayboluyor**; iki kusur bir arada.

## `bukum.py`

| Hüküm | Ölçüm |
|---|---|
| **M20** tünelleme `O(1)` değil | genişlik 1: `T=7.97e-02` (deneme 12.6); genişlik 16: `T=2.64e-18` (deneme **3.8e+17**) |
| **M21** düz bağlantı ⇏ trivial holonomi | akı/2π=0.37: `F` her yerde 0 ama `\|W−1\| = 1.836`. Tam sayı akıda trivial. Ölçüt `F=0` değil **`W(γ)=1`** |
| Holonomi kenar sayısından bağımsız | `N=4,8,32,128` hepsinde `e^{2πi·0.37}` (1e-12) |
| **M22** GRAPE gradyanı `O(Δt²)` yaklaşımı | `M=10…160`: fark `1.29e-02 → 6.86e-05`, `fark/Δt²` **1.29→1.76 arası sabit** |
| Tam (Fréchet) gradyan | sonlu farkla **1.6e-10** |
| GRAPE yine de çalışıyor | sadakat 0.0052 → **1.000000**, tekdüze artıyor |

**Ölçümün yakaladığı gerçek kusur.** `tam_gradyan`ı önce özayrışımla
yazmıştım. Fréchet blok dizeyi `[[A,E],[0,A]]` **dejenere özdeğerlidir**;
`eig` orada çöküyor ve tam gradyan sonlu farktan 1.9e-01…4.5e-01
sapıyordu. Ölçekle-kare-al usulüne geçirilince **1.6e-10**'a indi.
