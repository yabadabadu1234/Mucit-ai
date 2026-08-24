# omega_kategori_nbe — kübik çekirdeğin NbE sürümü

`omega_kategori`nin **ikinci sürümü**. Eski sürüm yerinde duruyor; ikisi
yan yana yaşıyor. Aynı sözdizimi ve aynı aralık cebrini paylaşırlar,
**indirgeyicileri farklıdır**.

```
python3 -m omega_kategori_nbe.test_omega_kategori_nbe    # 25 sınama
python3 -c "from omega_kategori_nbe import turetimler as T; print(T.rapor())"
python3 -c "from omega_kategori_nbe import geometri as G; print(G.rapor())"
python3 -c "from omega_kategori_nbe import iliskiler as I; print(I.rapor())"
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
| `sarim(dongu⁻¹)` | **>100 s (bitmiyor)** | **0.02 s** |
| `sarim(dongu⁻⁵)` | **>100 s (bitmiyor)** | **0.13 s** |
| `sarim(dongu⁻²⁰)` | **>100 s (bitmiyor)** | **0.82 s** |
| `sarim(dongu²⁰)` | **>100 s (bitmiyor)** | **1.04 s** |

**π₁(S¹) ≅ ℤ artık fiilen hesaplanıyor.** Tepe bellek: **21.7 MB**.

### Negatif kuvvet asimetrisi — teşhis ve tedavi

Bir ara `dongu⁻⁵` 27.4 s sürerken `dongu²⁰` 0.97 s sürüyordu. Sebep
`invEquiv` **değildi** (bu kodda öyle bir şey yok); sebep, umumî yol
tersleme `ters`in bir `hcomp` kurması ve terkip zincirinde bu hcomp'ların
**iç içe geçmesiydi**.

Tedavi kütüphane seviyesindedir, çekirdekte kısa yol değil: S¹ döngüsünün
tersi zaten aralık involüsyonuyla verilir, `dongu⁻¹ = <i> dongu(~i)`.
Ölçülen kazanç **245 kat** (`dongu⁻⁵`: 27.4 s → 0.11 s). Sağlaması
`dongu_kuvveti_genel_ters` ile kıyastır; ikisi aynı sarımı verir
(`test_dongu_tersi_genel_tersle_ayni_sarim`), yani hız bir yaklaşıklıktan
değil, aynı yolun daha sade bir sakininden geliyor.

### Bellek değil, zaman

Ölçüldü: en ağır hesapta bile tepe RSS **21.7 MB**. Yani darboğaz tahsis
değil, tekrar hesaptır. Profil, en sıcak noktanın aralık cebrindeki
antizincir normalleştirmesi olduğunu gösterdi (3.1 M çağrı, sürenin %42'si);
oradaki algoritmik düzeltme ve `yerine_koy`daki erken çıkış ~%30 kazandırdı.

**Ölçümle reddedilen:** kafes işlemlerini belleğe alma (hash-consing
fikrinin bu katmana tatbiki). Hız aynı kaldı, tepe bellek 20 MB'dan
**1281 MB**'a çıktı. Kaldırıldı.

**Sağlam olmayan:** yüz formülleri için ROBDD. ROBDD *Boole* fonksiyonlarını
kanonikleştirir; CCHM aralığı ise **serbest De Morgan cebridir** ve orada
`i ∧ ~i ≠ 0`. ROBDD bu ikisini özdeşleştirir, yani teorinin muhtaç olduğu
kanunu kırar. Mevcut temsil (yutma altında indirgenmiş DNF antizinciri)
zaten kanoniktir ve eşitliği hash ile O(1)'dir -- istenen gaye başka ve
**sağlam** bir yolla hâlihazırda sağlanmış durumdadır.

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

## Taşınan katmanlar

`turetimler.py`, `geometri.py`, `iliskiler.py` **taşındı** ve bu sürümde de
çalışıyor (`denetle_t` terim arayüzü ve `Baglam.genislet_t` üzerinden):

```
turetimler: 31/31   ·   geometri: 24/24   ·   iliskiler: 23/23
```

NbE sürümünde `turetimler` ayrıca π₁(S¹) hesabını da **doğrulanan türetim**
olarak taşır (`sarim(dongu²)=+2`, `sarim(dongu³)=+3`, `sarim(dongu⁻¹)=-1`).

## Durum

```
25 sınamanın 25'i geçiyor  (6'sı menfî)
uaβ hesaplanıyor · isoToEquiv denetimden geçiyor · π₁(S¹) ≅ ℤ HESAPLANIYOR
turetimler 31/31 · geometri 24/24 · iliskiler 23/23
```
