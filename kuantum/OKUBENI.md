# `kuantum` — kapılar, devreler, spektral işleçler, topolojik mizan

Kaynak: `docs/kaynak/kuantum_kapi_kulliyati.tex`, `kuantum_topos.tex`,
`kuantum_operator_ogrenmesi.tex` — ve bunlara uygulanan **35 tashih**
(`docs/kaynak/tashih_kuantum.py`, `TASHIH_CETVELI_KUANTUM.md`).

Aşağıdaki bütün sayılar ölçülmüştür.

```
python3 -m pytest kuantum -q             # 219 sınama
python3 -m kuantum.devre                 # her modülün kendi gösterimi var
python3 -m kuantum.kapilar ; python3 -m kuantum.tda ; python3 -m kuantum.qsvt
python3 -m kuantum.surekli ; python3 -m kuantum.topolojik
python3 -m kuantum.eniyileme
```

## 1. `kapilar.py` — üniter kapılar

| Hüküm | Ölçüm |
|---|---|
| K7: `U₁(λ) ≠ R_z(λ)`; `U₁(λ) = e^{iλ/2}R_z(λ)` | tek kubitte genel faz, **kontrollüsünde değil**: `CU₁ ≠ CR_z` |
| Mølmer–Sørensen `MS(π/2)` `\|0…0⟩`ı nereye götürür? | **çift** `n`: tam GHZ (2 temel durum dolu); **tek** `n`: çift-parite alt uzayına yayılıyor (`n=3`→4, `n=5`→16) |
| SWAP = 3 CNOT | doğru dizilim `CNOT · CNOT' · CNOT` (ortadaki ters yönlü) |

## 2. `devre.py` — durum vektörü, QFT, QPE, Trotter

| Hüküm | Ölçüm |
|---|---|
| Kapıyı eksen görünümüyle uygulamak tam dizeyden hızlı, **farksız** | `n=10`: 0.79 ms / 2484 ms → **3145×**, fark **0.00e+00**; `n=18` eksen 52 ms, tam dizey 1099.5 GB tutardı |
| QFT devresi = QFT dizeyi | `n≤5` için ‖fark‖∞ ≤ **3.5e-15** |
| Son SWAP'lar şart | SWAP'sız hâl **üniter ama yanlış**: `n=3` fark 0.7071 |
| K8: QFT köşegen **değildir** | köşegen dışı azamî `n=3`: **0.3536** |
| QPE tam temsil edilen fazda kesin | `φ=3/8`: olasılık **1.000000**; `φ=1/3`, `m=8`: hata 1.3e-03, olasılık 0.684 |
| Trotter `O(1/n)`, Suzuki-2 `O(1/n²)` | `n` iki katına çıkınca hata oranı **2.00** ve **4.00** |

## 3. `tda.py` — Q-TDA

| Hüküm | Ölçüm |
|---|---|
| `β_k = dim ker Δ_k` | çember/torus örneklerinde doğru |
| Bottleneck mesafesi **bakışımlı** | aynı barkodda 0; kısa çubuk eklenince 0.010 = köşegen mesafesi; boş barkodla 0.500 = en uzun çubuğun yarısı |
| K32: Kahan hatası `N`'den bağımsız | `N=10⁴` ve `10⁵`te Kahan hatası **tam 0**, naif 3.1e-17 / 1.6e-16 |

**Düzeltilen kusur.** Bottleneck ilk hâlde bakışımsızdı (`W∞(A,B)=0.354`
ama `W∞(B,A)=0.371`). Sebep: köşegen vekillerinin yalnız bir tarafa
eklenmesi. İki tarafa da eklenip vekil–vekil kenarları verilince
bakışım sağlandı.

## 4. `qsvt.py` — blok kodlama ve tekil değer dönüşümü

| Hüküm | Ölçüm |
|---|---|
| SVD yolu ile devre yolu aynı | 12 halde **1e-15** — ama ancak doğru konvansiyonla |
| `1/x` yaklaşımı `[1/κ,1]` üzerinde | `κ=4`, derece 61: **1.26e-6**; `κ=8`, derece 61: 3.2e-3 |
| `P^SV(A) = Σ P(σ)\|u⟩⟨v|`, yani **`(A⁻¹)†`** | `‖P(A)−A⁻¹‖/‖A⁻¹‖ = 1.09e+00` (uyuşmuyor), `‖P(A)−(A⁻¹)†‖ = 1.67e-08` (uyuşuyor); `A⁻¹` istiyorsan `A†` ver |

**İki düzeltme.** (a) SVD ve devre yolları `d≥3`te 0.5 ayrılıyordu;
sebep QSP'nin Wx ile yansıma konvansiyonlarının karıştırılmasıydı.
Ölçümle görüldü ki orta fazları `π/2` olan yansıma konvansiyonu `|T_d|`
veriyor; `qsvt()` ona geçirildi → 1e-15. (b) "Ters alındı" sanmak:
Hermitesel `A`da `A⁻¹` ile `(A⁻¹)†` çakıştığı için hata gizleniyordu.

## 5. `surekli.py` — sürekli değişkenli (CV) fotonik

Sonsuz boyutlu uzay `N` boyutlu kesmede çalışılır; **kesmenin bedeli
ölçülür**.

| Hüküm | Ölçüm |
|---|---|
| `[a,a†] = I` kesmede sağlanmaz | sapma yalnız son köşegende ve tam **`−N`**; alt blok 1.4e-14 |
| Kesmede üniterlik **bozulmaz** | `D(3)`, `S(0.8)`, `V(0.3)`: `‖U†U−I‖ ~ 1e-15` her `N`de |
| `D(α)\|0⟩` = kapalı tutarlı durum | `α≤2`: fark **≤5.8e-16**; `⟨n⟩ = \|α\|²` tam |
| Sıkıştırma `S†x̂S = e^{−r}x̂` | `r=0.5`'te `N=80` yeter (6.6e-13); `r=1.5`'te `N=320` gerekir (1.2e-02); **`r=2.0`'de `N=320` bile yetmez** (2.9e+01) |
| Sıkıştırma belirsizlik **çarpımını** korur | `ΔxΔp = 0.500000` = `ħ/2`, yalnız `x`↔`p` paylaşımı değişir |
| Işık bölücü foton sayısını korur | `⟨n⟩` 1.000000 → 1.000000; `\|⟨0,1\|out⟩\|² = sin²θ` tam |
| Kerr ve kesirsel Fourier **köşegen** → kesme hatası yok | `‖K†K−I‖ = 2.2e-16` her `N`de; `F^aF^b = F^{a+b}` 1e-14 |
| Kübik faz yakınsaması `γ`ya bağlı | `γ=0.1`: `N=40`'ta 8e-16; `γ=2.0`: `N=160`'ta ancak **6e-02** |
| `a=1`de `F†x̂F = p̂` | fark **2.1e-14** |

**Düzelttiğim yanlış.** Modül başlığına önce "kesmede `D`, `S` tam
üniter *değildir*" yazmıştım. Ölçüm bunu yalanladı: üreteçleri
ters-Hermityen olduğundan üstelleri **her boyutta** üniterdir. Kesmenin
bedeli üniterliği bozmak değil, **başka bir operatör** vermektir; o da
iki kesme kıyaslanarak ölçülüyor. `scipy` bulunmadığı için `expm` de
özayrışımla yazıldı ve ters-Hermityen olmayan girdiyi **reddediyor**.

## 6. `topolojik.py` — anyonlar, Majorana, yüzey kodu

| Hüküm | Ölçüm |
|---|---|
| `F` gerçel, simetrik, `F² = I` | 1.1e-16; `F`, `R`, `B` üçü de üniter (≤2e-16) |
| Yang–Baxter `σ₁σ₂σ₁ = σ₂σ₁σ₂` | **2.4e-16** |
| Fazlar keyfî değil (şahit) | `e^{−3πi/5}` yazılırsa hata **0.4490**; rastgele üniter çiftlerde 1.28–1.52 |
| Örgü grubu sonlu değil, hedefe yaklaşıyor | farklı öğe ~`1.88^L`; Hadamard'a mesafe `0.8202 → 0.1189 → 0.0864 → 0.0292` (uzunluk 13, 44337 öğe) |
| Majorana `{γ_j,γ_k} = 2δ_{jk}I` | hata **tam 0.0** (`n=2,3,4`) |
| Jordan–Wigner `Z` zinciri **şart** (şahit) | zincirsiz kurulumda köşegen dışı hata **2.00** |
| Kitaev `[A_s,B_p] = 0` | yıldız–yüz ortak kenar histogramı yalnız `{0,2}`; `L=2`'de tam dizeyle `max‖A_sB_p−B_pA_s‖ = 0.0` |
| Mantıksal kubit sayısı 2 | `L=2…5`: kubit `2L²`, bağımsız dengeleyici `2L²−2` (GF(2) sırasıyla), mantıksal **2** |

**Ölçümün düzelttiği yer.** Örgü yoğunluğunu önce rastgele kelimelerle
arıyordum: uzunluk 4, 8 ve 16'da mesafe hep 0.2074 çıkıyor, "yakınsama
yok" gibi görünüyordu. Sebep, sabit deneme sayısının büyüyen uzayı
gitgide kötü örtmesiydi. Genel faza göre tekilleştirilmiş **tüketici**
aramaya geçilince gerçek davranış göründü: iniyor, ama **basamaklı**.

## 7. `eniyileme.py` — adiyabatik, QAOA, parametre kaydırma

| Hüküm | Ölçüm |
|---|---|
| Adiyabatik başarı `T` ile artıyor | 4-döngü: `T=0.5`→0.1456 … `T=128`→**1.0000** |
| `T ≳ 1/Δ_min²` ölçütü burada **işlemiyor** | 4-döngünün `Δ_min`i (1e-04) `K₄`ünkinden (2.4e-02) küçük olduğu hâlde `T=128`de başarısı **daha yüksek** (1.0000 / 0.9992) |
| Sebep: hedefin temel öz-uzayı dejenere | katlılık 2 ve 6; `Δ(1) = 0` — kapanma **zararsız**, başarı alt uzaya örtüşmeyle ölçülüyor |
| QAOA `p` arttıkça iyileşiyor | `K₄` MaxCut (en iyi −4): `\|+⟩` −3.000 → `p=1` **−3.6975** → `p=2` **−4.000000** |
| Köşegen faz + kubit kubit karıştırıcı, tam dizeyden hızlı ve **farksız** | `n=12`: 0.0021 s / 61.95 s → **29572×**, fark **5.7e-16** |
| Parametre kaydırma `G²=I` iken **tam** | sonlu farkla fark ≤ **1.7e-10** (kalanı sonlu farkın kendi hatası) |
| Şart bozulunca **yanlış** (şahit) | `n̂ = diag(0,1,2)` ile kaydırma −0.4822, gerçek türev **−1.3812** |

**Ölçümün yakaladığı iki hata.** (a) Hız kıyasında karıştırıcının
Hamiltonyenini `−ΣX` yazmıştım (`e^{−iβΣX}` için `+ΣX` olmalı); iki yol
1.5e-01 ayrıldı, işaret düzeltilince 5.7e-16. (b) `G²≠I` şahidi önce
**hiç fark vermiyordu** (0.0000): seçtiğim `H` yalnız komşu seviyeleri
bağlıyordu, o yüzden `⟨H⟩` saf `2π`-periyotlu bir sinüs oluyor ve kural
tesadüfen doğru çıkıyordu. `\|0⟩↔\|2⟩` bağı eklenince şahit gerçekten
şahit oldu.
