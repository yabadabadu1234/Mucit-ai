# omega_kategori — (∞,∞)-kategori / kübik tip teorisi çekirdeği

Saf Python, hiçbir harici bağımlılık yok (~4200 satır).

```
python3 -m omega_kategori.test_omega_kategori                       # 26 sınama
python3 -c "from omega_kategori import turetimler as T; print(T.rapor())"
python3 -c "from omega_kategori import geometri as G; print(G.rapor())"
```

## Ne olduğu

CCHM tarzı, De Morgan aralıklı kübik tip teorisinin **çalışan** bir
çekirdeği: indirgeyici + iki yönlü tip denetleyici. **Hiçbir matematiksel
iddia Python'da "kabul edilmez"** — Python yalnız terim inşa eder; her
iddia nesne dilinde bir terimdir ve denetleyiciden geçer.

| Dosya | İş |
|---|---|
| `aralik.py` | De Morgan aralık cebri **ve** yüz (kofibrasyon) kafesi |
| `sozdizim.py` | terimler |
| `cekirdek.py` | ikame, indirgeme, Kan işlemleri (asli işlem: `comp`) |
| `denklik.py` | **Glue'nun Kan hesabı** — `comp^i U` ve `comp^i (Glue …)` |
| `denetleyici.py` | iki yönlü tip denetleyici |
| `kutuphane.py` | nesne dilinde kütüphane (∞-grupoid, J, `ua`, isoToEquiv, sarmal) |
| `turetimler.py` | uzayların türetilmesi + boşluk kütüğü |
| `iliskiler.py` | uzaylar arası dönüşüm, ayrık uzaylar, uç haller, moduli |
| `geometri.py` | teğet demeti, tensörler, monoid/Lie nesneleri, de Rham |

### İki kafes, bir köprü

* **Aralık `I`**: `{i, ~i}` üzerine **serbest De Morgan cebri**. Burada
  `i ∧ ~i ≠ 0` — tümleyen kanunu **yoktur**.
* **Yüz kafesi**: `(i=0)`, `(i=1)` atomları; burada `(i=0) ∧ (i=1) = ⊥`.

Köprü `aralik_esitligi(r, ε)`. Terim seviyesinde indirgeme tercih edilmesinin
sebebi budur: bir yüzün ikame altında **birden çok yüze açılması**
(`(i=0)[i↦j∧k] = (j=0)∨(k=0)`) doğrudan cebre devredilir.

## Tümel değişmezlik HESAPLANIYOR

Glue'nun Kan kuralı tamamlandı; ikisi de imâl edildi:

* **`comp^i U`** — `cizgi_denkligi`. Taşımanın denklik olduğunu ayrıca
  ispatlamak yerine, **özdeşlik denkliğini denklik-tipleri çizgisi boyunca
  taşıyoruz**: `transp^i (Denklik A(0) A(i)) ⊥ (idEquiv A(0))`. Bu yalnız
  Σ/Π/Path'te `transp` gerektirir.
* **`comp^i (Glue A [φ ↦ (T,w)])`** — CCHM (2018) §6.2 silsilesi:
  `δ = ∀i.φ`, `a'1`, `t'1`, `pres`, denklikle lif tamamlama, `a1`, `glue`.
  `t1` ve `α`, `φ(1)`in **her yüzü için ayrı ayrı** o yüze kısıtlanmış
  bağlamda hesaplanır.

Ayrıca **`isoToEquiv`** (`izo_denklige`) imâl edildi ve tip denetiminden
geçiyor; `sucZ : ℤ → ℤ` bununla bir denkliğe çevriliyor.

**Delil** — aşikâr olmayan bir denklikle `uaβ`:

```
transport (ua sucEquiv) n  ↝  n+1      (n = −2, −1, 0, 1, 3 için sınandı)
```

Özdeşlik denkliğiyle geçiştirilemeyecek bir sınamadır; Glue kuralının
fiilen ve doğru işlediğini gösterir.

## π₁(S¹) — kısmen

`sarmal : S¹ → U` (`taban ↦ ℤ`, `dongu ↦ ua sucEquiv`) tip denetiminden
geçiyor ve:

```
sarim(dongu⁰) = +0        sarim(dongu¹) = +1
```

`|n| ≥ 2` ve negatif `n` için hesap **pratikte bitmiyor**. Sebebi doğruluk
değil, değerlendirici mimarisidir: S¹ içindeki bir `hcomp`'a `sarmal`
uygulanınca `comp^i U` doğar, o da her katmanda bütün `Denklik` kulesini
(Σ/Π/isContr) taşır; terim seviyesinde, paylaşımsız ikameyle çalışan bir
indirgeyicide terim patlar. Kapanışı NbE'ye (kapanışlı değerler) geçmeyi
gerektirir. `turetimler.bosluklar()` kütüğünde kayıtlıdır.

## Hız üzerine: neyin işe yaradığı, neyin yaramadığı

Denenen ve **tutulan**: `comp` tembel akıllı kurucuya çevrildi (tip yönlü
açılım artık yalnız `whnf` isteyince yapılıyor); `nf`/`whnf`/`ara_ikame`/
`komp` önbelleğe alındı. İkisi de doğru ve faydalı, fakat **S¹ hcomp
duvarını yıkmıyor**.

Denenen ve **reddedilen** — `hcomp {ℤ} [φ↦u] u₀ ↝ u₀`: bu kural **sağlam
değildir**. Somut karşı-örnek: `isoToEquiv` içindeki `fill0 1 1` tanımsal
olarak `t x₀ @ 1 = x₀` olmalıdır; kural onu `g (f x₀)` yapar. İkisi
propozisyonel eşit, tanımsal değil — sınır şartı kırılır ve `isoToEquiv`
imkânsız hâle gelir. Bu, evvelce fiilen yaşanmış bir hatadır.

Ayrıca optimizasyon sırasında eklediğim **"çizginin iki ucu eşitse çizgi
sabittir"** kısayolu da sağlam değildi ve `uaβ`yı özdeşliğe çevirip
**yanlış cevap** ürettiriyordu (`ua e` çizgisinin iki ucu da `ℤ` olabilir).
Kaldırıldı; sabitlik yalnız normal formda tespit ediliyor.

Gerçek çözüm NbE'dir (kapanışlı değerler, paylaşımlı ortam). Bu, terim
seviyesindeki indirgeyicinin baştan yazılmasıdır ve yapılmadı.

## Türetilen uzaylar (hepsi denetlenmiş)

**`turetimler`** — 28/28: ∞-grupoid kulesi (`n`-morfizmler; birleşme
**katı eşitlik değil**, üst mertebeden yol), h-mertebeleri, `Ωⁿ`, kümeler,
monoid / grup / değişmeli halka, kategori, globüler tipler
`Glob(k+1) = Σ (Ob:U). Ob → Ob → Glob(k)`, S¹ ve döngü kuvvetleri.

**`iliskiler`** — 23/23: `f^*`, `Σ_f`, `Π_f` ve `Σ_f ⊣ f^* ⊣ Π_f`;
ayrık uzaylar (0-kesilmişlik + "yüksek morfizmler önemsizleşir" **ispatı**);
kritik lokus; parametrik lif demeti (moduli) ve kip. **Zincir kuralı
`(g∘f)^* ≡ f^*∘g^*`, monoidal uyum `f^*(P×Q) ≡ f^*P × f^*Q` ve teğet
zinciri `T(g∘f) ≡ Tg∘Tf` bu çatıda TANIMSALDIR — `refl` ile ispatlanır.**

**`geometri`** — 24/24, mesajdaki silsileyi takip eder:

1. `D = Σ (x:R). x·x = 0`
2. **`TX := X^D`** — teğet demeti bir **haritalama uzayıdır**; uzayı kurmak
   teğetini de kurmaktır. Lif: `T_x X = Σ (v : D→X). v(0) = x`
3. `Mod_R`, doğrusal dönüşümler, dual `M*`
4. `(r,s)`-tensör: `r` kovektör + `s` vektör ↦ skaler; **her yuvada
   doğrusallık şartıyla** (`tensor_yapisi`). Metrik `(0,2)`, Riemann `(1,3)`
5. **Monoid nesnesi** `μ, η` — `Mod_R` içinde monoid nesnesi tam olarak
   birleşmeli birimli `R`-cebridir
6. **Lie**: parantez, antisimetri, Jacobi — ve `koherens_kulesi(n)` ile
   Jacobi'nin bir üst mertebeden yolla koherensi
7. **de Rham**: `Ωⁿ(X)`, `d` ve `d∘d = 0` (postulat, tipleri denetlenmiş)

## Postulat katmanı

Nesne dilinde **ispatlanmaz**, aksiyom eklenir; **tipleri** yine de makine
ile denetlenir: `R` ve halka işlemleri, **Kock–Lawvere**, sonsuz küçük şekil
kipi `ℑ`, dış türev `d`. Bu bir eksiklik itirafı değil sahanın hâlidir:
**hiçbir kübik çekirdek — Cubical Agda dâhil — pürüzsüz ∞-toposu hesaplayan
bir indirgeyici vermez.**

## Düzeltilen bir sağlamlık hatası

İlk sürümde "ℕ/ℤ ayrıktır, `comp = u0`" kuralı vardı. **Bu sağlam
değildi**: sistemin `i=1`deki değeri tabana yalnız propozisyonel eşittir,
tanımsal değil — kural bütün ℤ dolgularını çökertiyor, `isoToEquiv`'i
imkânsız kılıyordu. Yerine doğru yapısal kural kondu: taban kurucusuna göre
sistem bileşenlere dağıtılır, dallar aynı kurucuyla başlamıyorsa `comp`
**takılı kalır**.

## Menfî sınamalar

"Geçti" demek, ancak yanlışın **reddedildiği** gösterilirse bir şey ifade
eder. 7 menfî sınama: tip uyuşmazlığı, kapsam dışı değişken, yolun ucunun
tutmaması, çakışan yüzde uyuşmayan sistem, tabanla uyuşmayan sistem,
kofibrasyonda sabit olmayan `transp` çizgisi, yüzünde denkliği tutmayan
`glue`.

## Durum

```
28 sınamanın 28'i geçiyor  (7'si menfî)
turetimler: 28/28  ·  geometri: 24/24  ·  iliskiler: 23/23
```
