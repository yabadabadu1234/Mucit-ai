# omega_kategori — (∞,∞)-kategori / kübik tip teorisi çekirdeği

Saf Python, hiçbir harici bağımlılık yok.

```
python3 -m omega_kategori.test_omega_kategori     # sınama takımı
python3 -c "from omega_kategori import turetimler; print(turetimler.rapor())"
```

## Ne olduğu

Bu, `(∞,∞)`-kategorileri ve HoTT'un uzay türetimlerini **fiilen denetleyen**
bir çekirdektir: CCHM tarzı, De Morgan aralıklı kübik tip teorisinin
tümü Python'da imâl edilmiş bir tip denetleyicisi ve indirgeyicisi.

Kilit nokta şudur: **hiçbir matematiksel iddia Python'da "kabul edilmez".**
Python yalnızca terim inşa eder; her iddia nesne dilinde bir terimdir ve
`denetleyici` tarafından makine ile doğrulanır. Bu yüzden aşağıdaki
"geçti" satırları, kendi kendini onaylayan beyanlar değil, denetlenmiş
neticelerdir.

## Katmanlar

| Dosya | İş |
|---|---|
| `aralik.py` | De Morgan aralık cebri **ve** yüz (kofibrasyon) kafesi |
| `sozdizim.py` | terimler |
| `cekirdek.py` | ikame, indirgeme, Kan işlemleri (asli işlem: `comp`) |
| `denetleyici.py` | iki yönlü tip denetleyici |
| `kutuphane.py` | nesne dilinde temel kütüphane |
| `denklik.py` | denklik yapıları + **açık boşluklar** |
| `turetimler.py` | uzayların türetilmesi + aksiyom/boşluk kütüğü |

### İki kafes, bir köprü

Kübik çekirdek yazarken en sık yapılan hata iki kafesi karıştırmaktır:

* **Aralık `I`**: `{i, ~i}` üzerine **serbest De Morgan cebri**.
  Burada `i ∧ ~i ≠ 0` — tümleyen kanunu **yoktur**.
* **Yüz kafesi**: `(i=0)`, `(i=1)` atomları. Burada `(i=0) ∧ (i=1) = ⊥`.

Köprü `aralik_esitligi(r, ε)`: bir aralık ifadesinin `0`/`1`e eşit olma
şartını yüz kafesine indirger (`(i∧j = 0) = (i=0) ∨ (j=0)` gibi). Sınama
takımı bu ayrımı açıkça sınar.

### Neden NbE değil, terim seviyesinde indirgeme

Kübik tip teorisinde değerlerin **aralık ikamesi** altındaki davranışı
incedir (yerli kapanışların ikamesi çift-ikame hatasına açıktır). Terim
seviyesinde bu bedavaya gelir: bir yüzün ikame altında **birden çok yüze
açılması** (`(i=0)[i↦j∧k] = (j=0)∨(k=0)`) doğrudan kofibrasyon cebrine
devredilir. Doğruluk, hız için tercih edilmiştir.

## (A) Hesaplanan ve denetlenen

* Π, Σ, seviyeli tümeller, `PathP`; η dâhil tanımsal eşitlik
* `comp` asli Kan işlemi; `transp`, `hcomp`, `fill` ondan türetilir
* Kan kuralları: Π, Σ, PathP, ℕ, ℤ, S¹
* **∞-grupoid kulesi**: her tipin `n`-morfizmleri; birleşme gibi kanunlar
  **katı eşitlik değil**, bir üst mertebeden morfizm (yol) olarak
* h-mertebeleri: büzülebilir / önerme / küme / grupoid / `n`-tip
* `Ωⁿ`, `J` (yol tümevarımı), lif, `isEquiv`, `Equiv`, `idEquiv`
* S¹ ve döngü kuvvetleri (`dongu³`, `dongu⁻²` …) — HIT'in `hcomp` kuralı
  eliminatörle doğru etkileşiyor
* **Kümeler** 0-mertebeye indirgemeden; **monoid / grup / değişmeli halka /
  kategori** bu kümeler üzerine Σ-tipleri olarak; **globüler tipler**
  `Glob(k+1) = Σ (Ob:U). Ob → Ob → Glob(k)`

## (B) İfade edilen, hesaplanmayan

`ua` teşkil edilir, tip denetiminden geçer, **uçları tanımsal olarak
doğrudur** (`ua e @ 0 ≡ A`, `ua e @ 1 ≡ B`). Fakat `ua` **boyunca taşıma
indirgenmez**: `comp^i (Glue …)` kuralı (CCHM 2018 §6.2) imâl edilmedi.

Bunun somut neticesi: **π₁(S¹) ≅ ℤ bu çekirdekte ifade edilebilir, fakat
hesaplanamaz.** Sarmal (helix) `S¹ → U` özyinelemesi `comp^i U` gerektirir,
o da `Glue` hesabına dayanır.

Bu boşluk **sessiz değildir**: ilgili kod yolu `EksikKural` yükseltir ve
sınama takımında bunun böyle olduğu ayrıca sınanır. Yapı taşları hazırdır
(`denklik.her_i_icin` = `∀i.φ`, `denklik.lifi_tamamla`); eksik olan
kuralın kendisidir.

## (C) Postulat

Aşağıdakiler nesne dilinde **ispatlanmaz**; aksiyom olarak eklenir.
Tipleri yine de makine ile denetlenir — yani "iyi teşkil edilmiş aksiyom"
oldukları doğrulanır:

* `R`, `top_R`, `carp_R`, `sifir_R` — pürüzsüz doğru ve halka işlemleri
* **Kock–Lawvere**: `D = Σ (x:R). x·x = 0` üzerindeki her fonksiyon tek bir
  afin form ile temsil edilir → türev kavramı buradan doğar
* `Im` — sonsuz küçük şekil kipi ℑ, ve birimi `X → ℑX`
* `uaBeta` — `ua` boyunca taşımanın denkliğin fonksiyonu olduğu

Pürüzsüz `∞`-topos ve yüksek topos teorisi bu katmandadır. Bu bir eksiklik
itirafı değil, sahanın hâlidir: **hiçbir kübik çekirdek — Cubical Agda
dâhil — pürüzsüz ∞-toposu hesaplayan bir indirgeyici vermez**; oralarda da
bu aksiyomdur.

## Menfî sınamalar

Bir tip denetleyicisinin "geçti" demesi, ancak yanlışı **reddettiği**
gösterilirse bir şey ifade eder. Takımda 7 menfî sınama vardır: tip
uyuşmazlığı, kapsam dışı değişken, yolun ucunun tutmaması, çakışan yüzde
uyuşmayan sistem, tabanla uyuşmayan sistem, kofibrasyonda sabit olmayan
`transp` çizgisi, ve yüzünde denkliği tutmayan `glue`.

## Şu anki durum

```
22 sınamanın 22'si geçiyor  (7'si menfî)
27 türetim tip denetiminden geçiyor, 1 bilinen eksik kural, 0 hata
```
