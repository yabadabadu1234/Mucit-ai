# Ana model, kübit üstünde

`tecrit.md` mimarisinin (kütük H32) **tamamı** ana modele geçti (H40).
`S` diye ayrı bir reel hâl **yoktur**: nefsin bir andaki bütün hâli tek
bir kuantum durumudur, 41 melekenin hepsi ona vurulan üniter kapılardır,
hiçbiri hiçbir şey okumaz.

```
python -m nefs.qmain akis    # 41 üniter meleke, tek dalga, tek ölçüm
python -m nefs.qmain mpo     # MPO ile takas ağının karşılaştırması
python -m nefs.qmain egit    # ARC + mîzân ölçütüyle eğitim
```

`nefs/akis.py` (reel `S` üzerindeki eski akış) **yerinde durur** ve 41
sınaması geçmeye devam eder; ikisi aynı girdide karşılaştırılabilir.

## Zincir düzeni

```
[sat0 veri×4][sat0 yerel hüküm] [sat1 veri×4][sat1 yerel hüküm] …
   … [satN-1 veri×4][satN-1 yerel hüküm]  [ K Ü L L Î   H Ü K Ü M ]

küllî hüküm = makam(2) mîzân(4) tenakuz(2) tasdik(2) sükût(1) nakz(2) kelam(4)
```

**Makam bir faza kodlanır**: `00=Şek, 01=Zan, 10=Yakîn, 11=Vehim`.
𝒪₃₂ onu okumaz, **çevirir**: nakz uyanıksa Yakîn'den geri döndürür,
tenakuz uyanıksa Şek'e çeker, tasdik uyanıksa Yakîn'e çeker. Hükmün
sayısı ancak en sonda, POVM zayıf ölçümüyle doğar — ve bir sayı değil
**dağılımdır** (kütük H31).

## Ne var

| dosya | ne |
|---|---|
| `qyazmac.py` | kübit yazmacı, adresler, MPO toplama/dağıtma, POVM okuması |
| `qmeleke.py` | 41 melekenin üniter hâli + düz parametre vektörü |
| `qakis.py` | akış + BEC faz kilidi (yalnız tepede) |
| `qegitim.py` | ARC + mîzân ölçütü, AS-GEK + hedef güdümü + tünelleme |
| `mertebe.py` | 20 ∞-kategori lifi (`omega_kategori_nbe` ile denetlenmiş) |
| `qmain.py` | ölçümlerin giriş noktası |

## Ölçülenler (iddia edilen değil)

### Uzak kapı: MPO mu, takas ağı mı?

Aynı üniter, iki usul. 20 satır (113 kübit), 20 durak:

| χ | MPO kesmesi | MPO'da dolaşıklık | takas kesmesi | takasta dolaşıklık |
|---|---|---|---|---|
| 8 | 1,1e-01 | 1,93 → **2,08** | 1,60e+01 | 1,93 → 1,44 |
| 32 | 6,1e-02 | 2,50 → **3,43** | 2,96e+01 | 2,50 → 1,87 |
| 64 | **2,7e-03** | 2,61 → **4,09** | 2,06e+01 | 2,61 → 2,15 |

Takas ağı dolaşıklığı **sürükler ve yok eder**; `χ` büyütmek kapatmaz
(sebep MPS'in bir boyutlu oluşudur — H26). MPO hiçbir kübiti oynatmadığı
için sürüklemez. χ=64'te kesme **7600 kat** azdır.

**MPO'nun doğruluğu ispatlandı**, iddia edilmedi: kayıpsız şartlarda
(χ=512, kesme 1e-30) takas ağıyla fark **5,8e-08 – 4,3e-07**, MPO'nun
normu tam **1,000000**. MPO bağı yalnız **2**'dir: `R(Σφ) = Π R(φ)`
olduğu için zincirde taşınan şey sayaç değil, iki boyutlu dönme
cebrinin elemanıdır.

### Süperpozisyon ≠ dolaşıklık

| hâl | entropi | Schmidt |
|---|---|---|
| kodlanmış + Hadamard | **−0,000000** | 1 |
| MERA'dan sonra | 1,885774 | 8 |
| 41 meleke + BEC'ten sonra | 2,074127 | 8 |

norm hatası 1,11e-16.

### Belirteç okuması

Belirtecin dört kübitlik **ortak** dağılımı, sol ve sağ çevre sarılarak
tam hesaplanır. Bilinen hâllerde doğrulandı (fark **3,4e-09**), `ΣP = 1`
cebren sağlanır, dalga okunduktan sonra da diridir — çöküş yoktur.

## Neyin iddia edilmediği

Kuantum donanımı yoktur; **kuantum hız avantajı iddia edilmez** (H19).
Süperpozisyon ve yıkıcı girişim gerçektir (genlikler işaretlidir,
𝒪₁₀ Tezat `σ_z` ile birbirini söndürür) fakat klasik olarak simüle
edilir.

**Melekelerin okumamasının bedeli açıktır ve saklanmaz.** Bir meleke
kendi girdisine bakıp "şuna göre şu kadar dönderelim" diyemez. Açılar ya
öğrenilen parametreden gelir ya melekenin kendi tarifinden (altın oran,
∞-kategori mertebesi). Bilgi açıya değil **dolaşıklığa** girer.
