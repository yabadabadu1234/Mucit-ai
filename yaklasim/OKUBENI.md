# yaklasim — fonksiyon yaklaşımı ve eniyileme usulleri

Projenin ikinci modülü. `omega_kategori`/`omega_kategori_nbe` bir tip
teorisi çekirdeğidir: orada bir şey ya **ispatlanır** ya olmaz. Burası
başka bir zemindir: burada bir şey ya **ölçülür** ya olmaz.

Ortak edep şu: hiçbir usul her yerde iyi değildir, ve **her usulün zaafı
gösterilebilir olmalıdır**. Bu yüzden her katman, kendi usulünün işe
yaradığı hâli DE, çuvalladığı hâli DE aynı dosyada taşır.

```
python3 -m yaklasim.test_yaklasim          # 25 sınama (~53 s)
python3 -m yaklasim.kara_kutu              # her katmanın kendi raporu
python3 -m yaklasim.tikizlik
python3 -m yaklasim.akislar
python3 -m yaklasim.genisletme
python3 -m yaklasim.simgesel
python3 -m yaklasim.nedensel
python3 -m yaklasim.modern
```

Yalnız `numpy` gerekir.

## Katmanlar ve ölçülen iddialar

### `kara_kutu` — imkânsızlık sınırları

İki ayrı sınır, karıştırılmadan:

* **No Free Lunch** — sonlu uzayda **tam sayımla**: `m=3, n=3` için 27
  fonksiyonun hepsi ve 6 usulün hepsi taranır; gözlenen iz dağılımları
  ve ortalama en iyi değer **birebir aynı** çıkar. Bu "eniyileme zordur"
  demek değildir; "hedef sınıfı hakkında kabul yoksa usul seçmenin
  anlamı yoktur" demektir.
* **NFL nerede delinir** — hedef sınıfı *tek tepeli*ye daraltılınca
  üçdurum araması rastgele aramayı yener (0.53 vs 2.41). Kazanç
  usulden değil, **ön kabulden** gelir.
* **Nemirovski–Yudin / Nesterov** — kuvvetli kabuller altında bile
  birinci mertebe usuller için alt sınır. Sıfır-zinciri hususiyeti
  ölçülür (destek `[1,2,3,4,5]`), ve gradyan inişi ile Nesterov
  hızlandırması `f(x_t) − f* ≥ 3L‖x₀−x*‖²/(32(t+1)²)` sınırını
  **kırmıyor**.

  > Yazarken düşülen tuzak: sınır her `t` için AYRI bir fonksiyonda
  > (`k = 2t+1`) geçerlidir. Sabit `k=20` alıp `t`yi küçük tutunca sınır
  > kırılmış göründü — usul hızlı olduğu için değil, iddia yanlış
  > kurulduğu için. Düzeltildi.

### `tikizlik` — varlık

Asgarînin *var olması* bir topoloji meselesidir, *bulunması* ayrı bir
mesele. Ölçülenler: zorlayıcılık delili, alt seviye kümesinin
sınırlılığı, `e^{−x}` üzerinde **ulaşılmayan infimum** (usul kusurlu
değil, çözüm kümesi boş), ve tıkızlaştırılamayan iki karşı örnek:
`sin(1/x)` (iki dizi boyunca `±1`e ayrışıyor) ve `(x²−y²)/(x²+y²)`
(limit `cos 2θ`, yani yöne bağlı).

> Yazarken düşülen tuzak: yalnız rastgele yönlerle örneklerken
> `f(x)=Σ_{i≥1}xᵢ²` **zorlayıcı göründü**, çünkü rastgele bir yön
> eksene tam oturmaz. Artık koordinat eksenleri örnekleme kümesine
> zorla katılıyor; kaçış koridorları çoğu zaman eksenlerdedir.

### `akislar` — gradyanın akış olarak okunuşu

| okuyuş | taşınan | ölçülen |
|---|---|---|
| vektör akışı | tek nokta | sığ çukurdan çıkamıyor (kaldığı yer 0.9601) |
| topluluk (Langevin) | ölçü | topluluğun %85.8'i derin çukura geçiyor |
| Wasserstein | ölçü | serbest enerji `F[ρ]=∫fρ+T∫ρlogρ` düşüyor (1.337) |
| ortalama eğrilik | yüzey | `r² = r₀² − 2t` ile bağıl hata **2.1·10⁻⁶** |

Langevin'in durağan dağılımı analitik Gibbs `e^{−f/T}` ile toplam
değişim uzaklığı **0.028**'de uyuşuyor. Bedeli açık: yakınsama artık
dağılım mânâsındadır ve `T → 0`da kazanç kaybolur.

### `genisletme` — Kan genişletmesi ve ezber

Lawvere okuyuşunda metrik uzay `[0,∞]` üzerinde zenginleştirilmiş bir
kategoridir; `S ↪ X` boyunca Kan genişletmesi **tam olarak**
McShane–Whitney formülleridir:

```
(Lan f)(x) = supᵢ [f(xᵢ) − L·d(x,xᵢ)]     (en küçük L-Lipschitz genişleme)
(Ran f)(x) = infᵢ [f(xᵢ) + L·d(x,xᵢ)]     (en büyük)
```

Üç iddia da ölçüldü: örnek noktalarda **tam** oturma (hata `0.0`),
Lipschitz sabitinin aşılmaması (6.283 ≤ 6.283), ve evrensel hususiyet
(hedefin ikisinin arasında kalması).

**Zaafı ve sebebi ölçüldü:** gürültülü veride tam oturma bedava
değildir — veriyi Lipschitz yapan sabit `6.28`den **4.46·10³**'e fırlar,
genişletme dikenleşir. Aynı zaafın çekirdek tarafı: `λ→0`da sınama
hatası **117**, `λ=0.1` sırt bağlanımında **0.228**. Düzenlileme eğitim
hatasını yükseltip sınama hatasını düşürür — takas budur.

> `λ = 0` sayısal olarak erişilebilir değildir: Gram dizeyinin koşul
> sayısı burada `6.3·10⁸`. "Tam aradeğerleme" yerine `λ=10⁻⁸` alınıp
> koşul sayısı rapor ediliyor.

Sobolev eğitimi (değer + türev uydurma) türev hatasını `2.93 → 0.30`
indiriyor; bedeli türev verisi gerektirmesi.

### `simgesel` — Occam cezalı formül arama

SINDy usulü + BIC. Temiz veride `2x² − 3sin x` **tam olarak** bulunuyor
(katsayılar `1e-8` içinde). Gürültülü veride cezasız ölçüt hep en büyük
modeli seçerken (`k=3`) BIC doğru boyutta duruyor (`k=2`).

**Zaafı:** doğru formül kütüphane dışındaysa (`log(2+x)`) usul yine bir
formül döndürür, aralık içinde iyi görünür (RMSE `4.7·10⁻³`), aralık
dışında **175**'e fırlar. Usul "bilmiyorum" demez.

> `m·log(RSS)` terimi, temiz veride `10⁻²⁸` ile `10⁻²⁹` arasındaki
> **anlamsız** farkı büyütüp fazla terimli modeli seçtiriyordu. BIC'e
> sayısal gürültü tabanı eklendi.

### `nedensel` — do-hesabı

Üretici model bilerek kurulur (`b = 0.8`), sonra üç tahmin kıyaslanır:

| tahmin | değer |
|---|---|
| ham bağlanım `E[Y\|X]` | **−0.402** (işaret bile ters) |
| arka kapı düzeltmesi | 0.798 |
| fiilî müdahale `do(X)` | 0.803 |

**Zaafı:** arka kapı, karıştırıcının *ölçüldüğünü* varsayar. Gizli bir
`U` eklenince yalnız `Z` ile düzeltme 2.007'de yanlı kalır. do-hesabı
bir hesap usulüdür; neyin ölçüldüğü bir **veri** meselesidir.

Ayrıca "ne kadar çok değişken katarsan o kadar iyi" yanlıştır: çatalda
şart koşmak düzeltir (0.799 → −0.002), çarpışmada **bozar**
(0.004 → −0.801, Berkson yanlılığı).

### `modern` — KAN, Fourier işlemcisi, DeepONet

* **KAN** `[2,1,1]`, RBF kenar tabanlı, hedef `exp(sin πx + y²)`.
  En iyi başlangıçta bağıl sınama hatası **0.005**, ve kenar
  fonksiyonları geri okunuyor: `φ₁ ~ sin(πx)` hata **0.0056**,
  `φ₂ ~ y²` hata **0.0061**. Fakat 6 başlangıcın yalnız **4**'ü iyi
  havzaya düşüyor; kalanlar `φ₁`in monoton kaldığı çukurda takılıyor.
  Yani "KAN okunabilir" iddiası **şartlıdır**.

  > İki hata ölçümle yakalandı: (i) `∂s/∂c₁` kenar tabanının KENDİSİDİR,
  > türevi değil — karıştırılınca model hiç öğrenmedi; (ii) dış ızgara
  > yenilenmezse `s` ızgaranın dışına çıkıp modeli çökertiyor
  > (kalıntı 0.58 → 0.99).

* **FNO** — `−u''=a` işlemcisi. `N=64`te öğrenilen kip çarpanları
  `N=256`da hatasız çalışıyor (`1.4·10⁻¹⁶`): **çözünürlükten
  bağımsızlık** ölçüldü. Zaafı da ölçüldü: eğitimde görülmemiş yüksek
  kiplerde hata `2.0·10⁻³`e çıkıyor.

* **DeepONet** — aynı işi `N=64`te `2.7·10⁻¹³` hatayla öğreniyor, fakat
  `N=256` girdiyi **olduğu gibi kabul edemiyor** (dal sabit duyu
  ızgarasında okur).

  > Burada bir iddia ölçümle **düştü**: yeniden örnekledikten sonra
  > FNO'nun daha doğru olduğunu yazmıştım; ölçüm ikisini denk buldu
  > (`2.6·10⁻¹³` vs `1.4·10⁻¹⁶`, ikisi de sıfır sayılır). Fark
  > doğrulukta değil, **arayüzdedir**. Metin düzeltildi.

## Durum

```
25 sınamanın 25'i geçiyor  (~53 s)
```

Ölçümle **reddedilen** üç iddia yukarıda ayrı ayrı kayıtlıdır; kod
onları gizlemez, sebepleriyle taşır.
