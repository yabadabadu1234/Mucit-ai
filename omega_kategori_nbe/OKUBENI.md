# omega_kategori_nbe — kübik çekirdeğin NbE sürümü

`omega_kategori`nin **ikinci sürümü**. Eski sürüm yerinde duruyor; ikisi
yan yana yaşıyor. Aynı sözdizimi ve aynı aralık cebrini paylaşırlar,
**indirgeyicileri farklıdır**.

```
python3 -m omega_kategori_nbe.test_omega_kategori_nbe    # 21 sınama
```

## Neden

Terim seviyesindeki sürümde `sarim(dongu^n)` hesabı `|n| ≥ 2` için
bitmiyordu. Sebep doğruluk değil, ikame mimarisiydi: `ara_ikame` her
seferinde terim ağacını **kopyalıyordu**, ve S¹ içindeki bir `hcomp`'a
`sarmal` uygulanınca doğan `comp^i U` her katmanda bütün `Denklik`
kulesini taşıyordu.

## Ölçüm

Aynı makine, aynı kütüphane terimleri:

| iş | terim sürümü | NbE sürümü |
|---|---|---|
| `transport (ua sucEquiv) 3` | 0.80 s | **0.06 s** |
| `sarim(dongu¹)` | 0.78 s | **0.03 s** |
| `sarim(dongu²)` | **>100 s (bitmiyor)** | **0.07 s** |
| `sarim(dongu³)` | **>100 s (bitmiyor)** | **0.12 s** |
| `sarim(dongu⁵)` | **>100 s (bitmiyor)** | **0.20 s** |
| `sarim(dongu⁻¹)` | **>100 s (bitmiyor)** | **0.03 s** |

`sarim(dongu¹⁰) = +10` da 0.51 s'de düşüyor. **π₁(S¹) ≅ ℤ artık fiilen
hesaplanıyor.**

Negatif kuvvetler pozitiflerden ağır (`dongu⁻²` ≈ 8 s, `dongu⁻⁵` ≈ 41 s):
`ters` daha karmaşık bir `hcomp` yapısı doğuruyor. Yine de **bitiyor** —
eski sürümde hiç bitmiyordu.

## Mimari

| Dosya | Durum |
|---|---|
| `aralik.py`, `sozdizim.py`, `yazdir.py` | eski sürümden **aynen kopya** |
| `terimler.py` | **yeni** — yalnız terim İNŞA yardımcıları (indirgeme yok) |
| `cekirdek.py` | **yeniden yazıldı** — değerler, kapanışlar, Kan işlemleri |
| `denklik.py` | **yeniden yazıldı** — Glue'nun Kan hesabı, değer seviyesinde |
| `denetleyici.py` | **yeniden yazıldı** — tipler DEĞER olarak taşınıyor |
| `kutuphane.py` | eski sürümden kopya (saf sözdizim, `terimler`e bağlandı) |

### Kübik NbE'nin ince yeri

Değerlerin **aralık ikamesi** (`act`) altındaki davranışı. Yerli (native)
Python kapanışları bunu bozar: `λx. σ(f(x))` yazmak, argüman zaten
σ-dünyasından geldiği için çift-ikameye yol açar.

Çözüm: **bütün kapanışlar veri kurucusudur.** `ATuretilmis` /
`KTuretilmis` bir *modül seviyesi fonksiyon* + *alanlar demeti* taşır;
`act` alanları dönüştürüp yeniden kurar. Hiçbir yerde yakalayan lambda
yoktur. Sözdizimsel kapanışlarda (`ASoz`, `KSoz`) `act` **yalnız ortama**
uygulanır — gövdeye dokunulmaz. Kazanç buradan gelir: ortamlar küçük ve
paylaşımlı, terim ağaçları büyük ve paylaşımsızdı.

Nötrlerde `act` eliminasyonu **acted özne üzerinde yeniden işletir**
(`uygula`, `yol_uygula`, `cember_ind` … çağırarak); böylece `i↦0` bir
nötrü kanonik hâle getirdiğinde indirgeme kaçmaz.

### Korunan sağlamlık şartları

Eski sürümde bulunup düzeltilen iki hata burada **baştan** doğru:

* `hcomp {ℤ} [φ↦u] u₀ ↝ u₀` kuralı **yok** — sınır şartını kırar. Yerine
  kurucuya iten yapısal kural; dallar aynı kurucuyla başlamıyorsa `comp`
  takılı kalır.
* `_sabit_mi` **muhafazakârdır**: `L(0) == L(1)` sınaması yapılmaz
  (`ua e` tuzağı: iki uç da `ℤ` olduğu hâlde çizgi sabit değildir).
  Denetleyicideki `_sabit_cizgi_mi` ise normal formda serbest geçişe bakar.

## Durum

```
21 sınamanın 21'i geçiyor  (6'sı menfî)
uaβ hesaplanıyor · isoToEquiv denetimden geçiyor · π₁(S¹) ≅ ℤ HESAPLANIYOR
```

## Henüz taşınmadı

`turetimler.py`, `geometri.py`, `iliskiler.py` bu sürüme **taşınmadı**.
Bunlar saf sözdizim + tip denetimi katmanlarıdır; taşımak,
`denetle(t, tip_terim, g)` çağrılarını `denetle(t, g.d(tip_terim), g)`
hâline getirmekten ibarettir. Şimdilik o üç katman yalnız eski sürümde
çalışır.
