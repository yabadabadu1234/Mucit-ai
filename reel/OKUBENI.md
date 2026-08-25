# `reel` — sanal birimin ilgası

Kaynak: `docs/kaynak/reel_meleke_operatorleri.tex`,
`docs/kaynak/meleke_kuantum_kapilari.tex`.
Tashihler: **M9–M16, M28–M30** (`docs/kaynak/tashih_meleke.py`).

```
python3 -m pytest reel -q          # 58 sınama
python3 -m reel.hartley ; python3 -m reel.karmasik
python3 -m reel.meleke             # varsayılan D=512
python3 -m reel.meleke 128         # hızlı deneme
```

**Boyut.** `VARSAYILAN_BOYUT = 512`, `HIZLI_BOYUT = 128`.

## Kaynağın doğru yazdığı yerler (ölçülerek teyit)

| Hüküm | Ölçüm |
|---|---|
| RHT dik, simetrik, `RHT² = I` | `N=512`: `‖HᵀH−I‖ = 8.5e-14`, `‖H−Hᵀ‖ = 0.0` |
| `J² = −I` | tam **0.0** |
| `H_ℝ = [[A,−B],[B,A]]` simetrik ve `[J,H_ℝ] = 0` | ikisi de tam **0.0** |
| `cos(Ht)I + sin(Ht)J` kapalı biçimi | üstelle fark **0.0** — ama `J²=−I`'ye değil, **blok yapısına** borçlu: `[J,S]≠0` olan bir `S`de fark **18.55** |

## Tashihlerin ölçümü

| Tashih | Ölçüm |
|---|---|
| **M9/M10** Householder durumun tamamını negatiflemez | rastgele Ψ'de `‖UΨ+Ψ‖ = 1.9371`; `Ψ = v`'de **0.0**. `‖UΨ‖ = 1.000000` — **genlik yok edilemez**. Gerçekten silmek için izdüşüm gerekir: `⟨v|PΨ⟩ = 5.7e-18` ama `‖PΨ‖ = 0.995` (üniter değil) |
| **M11/M12** ihtimal kapısı üniter değil | `diag(√P)`: `‖AᵀA−I‖ = 0.911`; `diag(P)` (reel nüsha): **0.992** |
| **M13** şek/zan/yakîn | kaynağın işleci `‖M†M−I‖ = 1.0`; `SO(2)` hâli `3e-19`. Yakîn (θ=0.02) → 0.9996, şek (θ=π/4) → 0.5000 |
| **M14/M15** grup ≠ cebir | iki **dik** dizey: `‖C+Cᵀ‖ = 1.622` (`so(D)`de değil); iki **üreteç**: `0.0` |
| **M16** `ΠU = exp(ΣX)` | genel üreteçlerde fark **1.144**; sıra değiştirenlerde **1.9e-15** |
| **M28** reel Schrödinger işareti | `−J·H_ℝ` ile `exp(−iHt)` farkı **7.2e-16**; `+J·H_ℝ` ile **2.954**. Üstelik `+` hâli tam olarak `exp(+iHt)` — zamanın tersi |
| **M29** Hartley evrişim kaidesi | naif çarpım hatası `N=64`'te **22.51**, doğru kaide **7.1e-15**. Köşegen süzgeç: keyfî `r`'de dolaşımlıdan sapma **0.806**, çift simetrik `r`'de **7.2e-16**, QFT'de **4.2e-17** |
| **M30** genel işaret ölçülemez | `ρ(Ψ)` ile `ρ(−Ψ)` farkı **0.0**; alt uzay işaretinde **0.344** |

## Hız

| Ölçüm | Sonuç |
|---|---|
| 41 kapı, çarpanlı vs tam dizey | `D=128`: **15.7×**, `D=512`: **119.8×**; fark **6.8e-15** |
| Hızlı RHT (fft) vs `N×N` dizey | `N=4096`: **43.8×**, fark 3.3e-12; `N=16384` dizey 2.15 GB tutardı, hızlı yol 0.29 ms |

**Beklentimin ölçümle düzeltildiği yer.** Reel gömmeyi "iki kat iş, iki
kat bedel" diye yazmıştım. İşlem sayısı gerçekten iki kat (`8N³` / `4N³`)
ama duvar saati **tersini** söyledi: ölçülen oran `N=64,128,256` için
**0.41×, 0.32×, 0.44×** — reel gömme bu makinede karmaşık çarpımdan
**iki-üç kat hızlı**. Sebep BLAS'ın reel GEMM'inin çok daha iyi
eniyilenmiş olması. Yani kaynağın teklifi hız bakımından da savunulabilir
— ama sebebi "sanal sayı yanılsaması" değil, kütüphane gerçekliği.
Doğruluk her iki yolda aynı (fark 1e-13).
