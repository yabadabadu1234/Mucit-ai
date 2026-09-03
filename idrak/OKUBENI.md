# `idrak` — külliyatın mimarisi ARC-AGI-2 üzerinde

Bu paket, risalelerdeki parçaların **birbirine bağlandığı** ve gerçek
bir görev üzerinde ölçüldüğü yerdir.

```
python3 -m pytest idrak -q
python3 -m idrak.arc ; python3 -m idrak.kubit
python3 -m idrak.model ; python3 -m idrak.cozucu
```

## Veri

| Kaynak | İçerik |
|---|---|
| [arcprize/ARC-AGI-2](https://github.com/arcprize/ARC-AGI-2) | **1000** eğitim + **120** değerlendirme görevi |
| [cristianoc/arc-agi-2-abstraction-dataset](https://github.com/cristianoc/arc-agi-2-abstraction-dataset) | 120 değerlendirme görevinin **hepsi** için sözlü algoritma (`abstractions.md`) + tipli DSL + çalışan çözücü |

**Bölme: 900 / 100 / 120 (%80 / %9 / %11).** 50/50 değil, çünkü sınama
kümesinin tek işi tarafsız kestirimdir ve kestirimin standart hatası
`√(p(1−p)/n)` ile *sınama* boyutuna bağlıdır — 120 görevde ≈ 4.6 puan,
yeterli. Eğitimi yarıya indirmek kestirimi ancak 2.1 puana iyileştirir
ama öğrenmeyi doğrudan zayıflatır. Üstelik bölmeyi uydurmuyoruz: ARC'ın
kendi bölmesine uyuyoruz.

**Kendi denetimimin yakaladığı sızıntı.** İlk hâlde hedef örnek
bağlamın içindeydi — model kaideyi öğrenmeden **kopyalayarak**
çözebilirdi. Çıkarıldı. Kalan 33/300 sızıntı, çıktının görevler arası
gerçekten tekrar ettiği hâllerdir (verinin kendi özelliği).

**Uzunluk sınırı kapsamı ölçüldü ve düzeltildi:**

| bağlam | hedef | örnek | eğitim örneği | değerlendirme kapsamı |
|---|---|---|---|---|
| 768 | 320 | 3 | 1844 | **3 / 120 (%2)** |
| 2048 | 640 | 2 | 2964 | **65 / 120 (%54)** |
| 3072 | 900 | 2 | 3147 | 98 / 120 (%82) |

İlk ayarla model kümenin %98'ine **dokunamıyordu bile**; `2048/640/2`ye
geçildi.

## Kübit katmanı (`kubit.py`)

| Ölçüm | Sonuç |
|---|---|
| Kapılar dik mi? | `n=2…5`: `‖UᵀU−I‖` **3.6e-07 … 6.6e-07**, `det = +1.000000` |
| Norm korunuyor mu? | `max\|‖ψ‖²−1\|` **≤ 4.8e-07**; okuma toplamı 1.0000000 |
| Kontrollü kapı dolaşıklık üretiyor mu? | Bell durumu `[+0.7071, 0, 0, +0.7071]`, Schmidt `(0.7071, 0.7071)`; kontrollü açı 0 iken `(1.0, 0.0)` = çarpım durumu |
| Maliyet | `n=4`: 3.1 ms, `n=16`: **108 ms** — `2^n` ile büyüyor |

**Dürüstlük şartı.** Bu bir kuantum bilgisayarı **değildir**; klasik
benzetimdir. "Kübit koyduk, hızlandık" demek yanlış olurdu — ölçülen
tek kazanç norm korunumu ve dikliktir.

## Model (`model.py`) — D=512 varsayılan, D=128 hızlı deneme

| Risaledeki parça | Ölçüm |
|---|---|
| **M29** Hartley süzgeci, çift simetri | `‖r[k]−r[N−k]‖ = **0.00e+00**` — yalnız yarısı öğrenildiği için bozulması **imkânsız** |
| Süzgeç gerçekten evrişim mi? | dolaşımlıdan sapma **5.96e-08** |
| Cayley dik karışım (41 meleke) | `‖QᵀQ−I‖ = 7.2e-07`, `det = +1.000001` |
| Çözücü nedensel mi? | geçmiş değişimi **0.00e+00**; gelecek 1.5676 |
| Kodlayıcı nedensel mi? | 0.3272 — **beklenmiyor** (bağlam tam gözlenmiş) |
| Hartley vs dikkat | `N=2048`: 1.30 ms / 9.94 ms → **7.6×** |

Parametre: `D=128`'de 2.34 M.

## Doğrulanabilir çözücü (`cozucu.py`) — **ya ispat ya sükût**

`D₄` dihedral grubu (`reel.meleke`'deki permütasyon kapılarının ta
kendisi — sınamada `‖PᵀP−I‖ < 1e-12` ile teyit ediliyor) + renk
eşlemesi + döşeme + kırpma + ölçekleme + bakışım onarımı + bağlı
bileşen (nesne) seçimi + yerçekimi.

Bir aday, görevin **bütün gösterim çiftlerini** tam tutmadıkça
kullanılmaz; tutan aday yoksa **cevap verilmez**.

| Küme | tam çözülen | cevap verilen | yanlış | susulan | cevap verince isabet |
|---|---|---|---|---|---|
| resmî eğitim (1000) | **30 (%3.0)** | 32 | 2 | 968 | **%93.8** |
| doğrulama bölmesi (100) | **2** (`bc4146bd`, `1f85a75f`) | 2 | 0 | 98 | **%100** |
| resmî değerlendirme (120) | **0** | 0 | 0 | 120 | — |

Kullanılan kurallar: `D4:devrik`, `D4:dön90`, `D4:dön180`,
`D4:yatay_ayna`, `D4:dikey_ayna`, `aynalı_döşeme_1x2`,
`aynalı_döşeme_1x5`, `bakışım_onarımı_renk4`, `döşeme_1x2`, `fraktal`,
`kırp`, `kırp+D4:yatay_ayna`, `nesne:en_buyuk`, `nesne:en_kucuk`,
`nesne:tek_renk`, `renk_eşlemesi`, `yerçekimi:asagi`,
`yerçekimi:yukari`, `ölçek_2x2`, `ölçek_3x3`.

**Değerlendirme kümesinde 0/120 — ve bu bir başarısızlıktır, öyle
yazılıyor.** ARC-AGI-2'nin değerlendirme kümesi tam da bu sınıf basit
dönüşüm aramalarını yenmek için kuruldu; ARC-AGI-1'den farkı budur.

## Şekil kaidesi (`sekil.py`) — tam eşleşmenin ön şartı

**Ölçümün yakaladığı asıl kusur.** Şekil başı yokken model ürettiği
ızgaraların **%96'sını iyi biçimli** yapıyordu ama **şekli %0** doğru
oluyordu; yani tam eşleşme *imkânsızdı*. Şekil başı (`satir_bas`,
`sutun_bas` + kısıtlı çözümleme) eklendi, fakat 500 adımda doğrulama
şekil isabeti ancak **0.027**'ye çıktı.

Bunun mimarî mi eğitim eksikliği mi olduğunu **ölçtüm**: donuk
kodlayıcının havuz vektörü üstünde doğrusal yoklama satır **0.325**,
sütun **0.338** verdi. Bilgi kısmen orada ama 31 sınıflı bir
sınıflandırma olarak ağır.

Oysa ARC'ta şekil çoğunlukla gösterim çiftlerinden **cebirle** çıkar.
Her eksen için bağımsız kaide aranıyor — `sabit`, `oran` (aynı
kenarın `p/q`'si), `capraz` (öteki kenarın `p/q`'si; devrik bununla
kapanıyor) — ve katsayılar `Fraction` ile **tam** tutuluyor:
"yaklaşık 3 kat" kabul edilmiyor.

| Küme | kapsam | kapsayınca isabet | kipler |
|---|---|---|---|
| resmî eğitim (1076 sınama çifti) | **0.855** | **0.998** | `oran\|oran` 877, `sabit\|sabit` 34, `capraz\|oran` 5, … |
| resmî değerlendirme (167 çift) | **0.725** | **0.983** | `oran\|oran` 117, `capraz\|capraz` 2, `sabit\|sabit` 2 |

Kaide bütün gösterim çiftlerinde tutmazsa `None` döner — çözücüdeki
**ya ispat ya sükût** ölçütünün aynısı — ve sinir ağının şekil başına
dönülür. **Sızıntı yok:** kaide, `gorev_dizisi`'nin bağlamı kurarken
yaptığının aynısıyla hedef çift dışarıda bırakılarak çıkarılıyor.

## Eğitim (`egitim.py`) — SİLİNDİ (kütük H208)

Bu klasik PyTorch/AdamW eğitim döngüsü, H3'ün ("ana döngüde gradyan
ve kayıp yoktur") doğrudan ihlali olduğu ve `main/cikarim.py`nin
`Hendese` (cebirsel ebat kanunu) zaten aynı sorunu (ızgara ebadının
doğru çıkması) daha güçlü çözdüğü için tasfiye edildi. `model.py`,
`kubit.py`, `kategori.py` ayrı bir karara kadar yerinde duruyor.
