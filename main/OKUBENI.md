# `main/` — Küllî Dimağ

`tecrit.md`'deki mimarinin **müstakil** modeli (kütük H32). `nefs/` ile
karıştırılmaz; ayrı kurulur, ayrı ölçülür.

```
python -m main.main kapasite   # kaç belirteç aynı anda tutuluyor
python -m main.main egit       # ARC ile gradyansız eğitim + değerlendirme
```

## Ne var

| dosya | ne |
|---|---|
| `dimag.py` | tipli kübit uzayları → MERA → 20 Hamiltonyen uzayı → 4'lü zırh → geri mühürleme → BEC → POVM |
| `optimize.py` | çift motor: AS-GEK + **bizzat dalga** (sürekli), Postnikov + tersine tavlama (ayrık) |
| `egitim.py` | ARC metniyle uygunluk (potansiyel), eğitim çevrimi, değerlendirme |
| `main.py` | kapasite ve eğitim ölçümlerinin giriş noktası |

## Ölçülenler (iddia edilen değil)

**Kapasite — iddia doğrulandı.** Bellek belirteç sayısıyla **doğrusal**
büyüyor; belirteç 4× arttığında bellek **4.00×** artıyor (karesel olsaydı
16× olurdu):

| belirteç | kübit | ağaç belleği | RSS | ileri geçiş |
|---|---|---|---|---|
| 1.024 | 4.096 | 128 KB | 35 MB | 10 ms |
| 16.384 | 65.536 | 2 MB | 40 MB | 20 ms |
| **65.536** | **262.144** | **8 MB** | **56 MB** | **76 ms** |

65 bin belirteç tek durumda, 8 MB'ta, tek çekirdekte 76 ms. Mesafe
`log₂N` kademede kapanıyor (65.536 için 17 kademe).

**Değerlendirme — iddia doğrulanmadı.** Bu ölçekte (parametre ≈ 1.700,
20 çevrim) ARC değerlendirme kümesinden **hiçbir soru tam çözülmedi**.
Ortalama hücre isabeti ≈ 0.02. Gizlenmiyor.

## Neyin iddia edilmediği

Kuantum donanımı yoktur; **kuantum hız avantajı iddia edilmez** (H19).
Süperpozisyon ve girişim gerçektir (genlikler işaretlidir, birbirini
söndürür) fakat klasik olarak simüle edilir; maliyet `O(N·D³)`. Ölçülen
kazanç hız değil **kapasitedir**.

Betti sayısı 256 düğümlük alt örneklemle hesaplanır (tam çizge `O(n²)`
bellek ister; 65.536 düğümde 32 GiB istedi). Bu tavan raporlanır.
