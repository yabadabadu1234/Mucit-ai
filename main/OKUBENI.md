# `main/` — Küllî Dimağ

`tecrit.md`'deki mimarinin **müstakil** modeli (kütük H32). `nefs/` ile
karıştırılmaz; ayrı kurulur, ayrı ölçülür.

```
python -m main.main uzaylar   # 20 ∞-kategori uzayı, makine tip denetimi
python -m main.main kubit     # süperpozisyon, dolaşıklık, bellek büyümesi
python -m main.main egit      # Hamiltonyen parametrelerini öğret + değerlendir
```

## Akış

```
belirteçler
  → KÜBİT YAZMACI  (N kübit, MPS; yazmac.py)
  → Hadamard: SÜPERPOZİSYON  (2^N taban durumu, entropi hâlâ 0)
  → MERA: dolanıklık çözücü U + izometri W  → DOLAŞIKLIK (entropi > 0)
  → 20 ∞-KATEGORİ UZAYINA fırlatım F_m       (kategori.py)
  → her uzayda kendi Hamiltonyeni e^{−ηH_m}  (hamiltonyen.py)
  → her uzayda kendi 4'lü zırhı              (zirh.py)
       Sheaf · Homotopi · Betti · Kohomoloji  — katman değil, enine kesit
  → tünelleme vanası Γ  → esas uzaya geri mühür F_m†
  → BEC faz kilidi (Gross–Pitaevskii) — yalnız tepede
  → POVM zayıf ölçüm: P(x) = Tr(E_x ρ_kök), ÇÖKÜŞ YOK
```

## Ne var

| dosya | ne |
|---|---|
| `yazmac.py` | hakiki kübit yazmacı: MPS durumu, Hadamard, SO(4) iki-kübit kapıları, MERA, von Neumann entropisi |
| `kategori.py` | 20 uzay; `omega_kategori_nbe` ile **kurulur** ve makineyle **denetlenir** |
| `hamiltonyen.py` | uzay başına `H_m = ΣE_m\|σ⟩⟨σ\| + ΣJ_m(\|σ⟩⟨τ\|+h.c.)`, Trotter evrimi, tünelleme |
| `zirh.py` | enine zırh: sheaf, homotopi, Betti (β₀>1 = ezber cezası), kohomoloji tıkanıklığı |
| `dimag.py` | bütün boru hattı + BEC + POVM |
| `optimize.py` | çift motor: AS-GEK + **bizzat dalga** (sürekli), Postnikov + tersine tavlama (ayrık) |
| `egitim.py` | ARC metniyle uygunluk (potansiyel), eğitim çevrimi, değerlendirme |

## Ölçülenler (iddia edilen değil)

### Süperpozisyon ≠ dolaşıklık — 4.096 kübit

| hâl | entropi S | Schmidt rütbesi |
|---|---|---|
| `\|0…0⟩` çarpım durumu | −0,000000 | 1 |
| Hadamard (**süperpozisyon**) | −0,000000 | 1 |
| MERA(6) (**dolaşıklık**) | **1,979102** | **8** (âzamî S = 2,0794) |

norm hatası 0,00e+00. Hadamard'dan sonra 2^4096 taban durumunun **hepsi**
eşit genliktedir ama entropi sıfırdır: süperpozisyon dolaşıklık değildir.
Dolaşıklığı MERA üretir (H24).

### 6.000.000 kübit — tek çekirdek, χ = 8, float32

| iş | ölçüm |
|---|---|
| yazmaç kurulumu | 19,8 sn — durum **2,86 GB**, kübit başına **512 B** |
| Hadamard (süperpozisyon) | 15,0 sn — entropi −0,000000 |
| MERA(2) (dolaşıklık) | 459,4 sn — **S = 1,5405**, Schmidt = 8 |
| norm hatası | **0,0e+00** |
| âzamî yerleşik bellek | **3,37 GB** (durumun 1,18 katı) |

Bellek kübit sayısıyla **doğrusal**: kübit 4× arttığında bellek 4,00×.

### 20 uzay — makineyle denetlendi

`turetimler.morfizm_tipi(A, n)` ile kurulur, `denetleyici.denetle_t` ile
denetlenir. **20/20** uzay tip denetiminden geçti; **14**'ü tam mertebede
kuruldu (0–9, 13, 17, 19, 20). Daha yüksek mertebeler
`kutuphane.dongu_uzayi_n` temsilcisiyle tutulur ve bu gizlenmez —
`Uzay.tam_kuruldu` alanında yazar. Ölçülen kurulum süresi: n=10 → 0,04 sn,
n=16 → 0,28 sn, n=20 → 0,66 sn, n=22 → 1,05 sn.

`iliskiler.tikanma_postulati`, `kesit_tipi` ve `evrensel_demet` akitleri de
denetimden geçti.

## Neyin iddia edilmediği

Kuantum donanımı yoktur; **kuantum hız avantajı iddia edilmez** (H19).
Süperpozisyon ve girişim gerçektir (genlikler işaretlidir, birbirini
söndürür) fakat klasik olarak simüle edilir. Ölçülen kazanç hız değil
**kapasitedir**.

MERA(2) 6 milyon kübitte 459 saniye sürüyor — bu ucuz değildir ve
öyleymiş gibi gösterilmiyor. Kesme hatası da yazılır (5,83).
