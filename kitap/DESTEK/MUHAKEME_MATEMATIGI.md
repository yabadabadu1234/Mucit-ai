# MUHAKEME MATEMATİĞİ: MA'KÛLİYET, İSTİDLÂL, İZ'AN, KAVRAM

> **NAKZ (padişah emri üzerine):** Aşağıdaki dört ek yapı (ahval ailesi, hasr, engel, grup) bu dosyada sistemin **girdisi** gibi okunabilir; bu okuma reddedilmiştir. Bebek malûmatla değil istidatla doğar. Dört yapı **ürün**dür, girdi değildir; kuruluşu `ISTIDAT_MATEMATIGI.md`dedir. Bu dosyadaki tarif ve teoremler yürürlüktedir, yalnız "dışarıdan verilir" iddiası kalkmıştır.


Bu dosya, "insanda muhakeme illiyeti" diye tarif edilen dört hâli (ma'kûliyet · istidlâl · iz'an · kavramsallaştırma) matematik olarak kurar. Her hâl için **tarif → denenip bozulan ilk kuruluş → yeniden kuruluş → teorem → ölçü** sırası izlenir. Deneyler `muhakeme_deney.py` ile koşar, sayılar `muhakeme_olcu.json`dadır. Deneyler **sentetiktir**: kurulan çerçevenin ayırdığı şeyleri gösterir, Kur'ân kökleri üzerinde henüz koşulmamıştır.

Dört hâlin ortak sonucu (§5): hiçbiri gözlem dağılımı `P₀`ın bir fonksiyonu değildir. Her biri `P₀`ın **ötesinde** ayrı bir yapı ister: müdahale ailesi, hasr, bir enerji engeli, bir grup. İstatistik ile muhakemeyi ayıran şey "makinenin türü" değil, **bu dört ek yapının verilip verilmediğidir**.

---

## 1. Ma'kûliyet (illiyet-i akliyye)

### 1.1 İlk kuruluş: luzûm olarak mantıkî gerektirme (bozuldu)

`A → B` ma'kûldür ⇔ `T ∪ {A} ⊨ B`, `T` âlemin nizamı. Derece: `μ(A→B)=inf_{P∈Π(T)} P(B|A)`, `Π(T)` `T`yi sağlayan ölçüler. `μ=1` ⇔ gerektirme.

**Kusur:** Mantıkî gerektirme **karşıt-olumlu (contraposition)** altında simetriktir: `A ⊨ B` ise `¬B ⊨ ¬A`. Oysa "yağmur ıslaklığa sebep" demek "kuruluk yağmurun yokluğuna sebep" demek değildir. Gerektirme sebep ile netice arasında **yön** vermez. İlk kuruluş reddedilir.

### 1.2 İkinci kuruluş: müdahaleye karşı değişmezlik

Mekanizma bir yapısal denklem sistemidir: `Vᵢ = fᵢ(Pa(Vᵢ), Uᵢ)`. **Ahval ailesi** `𝓔`, her biri bazı mekanizmaları veya dış gürültü yasalarını değiştiren ortamlardır (`do(·)`).

**Tarif 1 (ma'kûliyet kusuru).** `δ(A→B) = min_S sup_{e,e'∈𝓔} d_TV( P^e(B | A,S), P^{e'}(B | A,S) )`, `S` ayarlama kümesi. `δ=0` ise `A→B` ma'kûldür: `B`nin `A` verilince yasası, âlem değişse de değişmez. `δ` küçüldükçe ma'kûliyet artar.

Bu, "şundan sonra şu gelir"in tersidir: **önceki–sonraki** gözlemde bir şeydir, **hangi ahvalde bozulmadığı** başka bir şeydir.

**Teorem 1 (korelasyonun kör noktası).** `(A,B)` için her ortak Gauss yasası `P₀`, hem `A→B`, hem `B→A`, hem `A←Z→B` yapısal modelleriyle üretilebilir. *İspat:* `Σ = [[σ_A², c],[c, σ_B²]]` verilsin. (i) `A=σ_Aε`, `B=(c/σ_A²)A+η`, `Var η=σ_B²−c²/σ_A²`. (ii) aynısı simetrik. (iii) `Z~N(0,1)`, `A=aZ+ε_A`, `B=bZ+ε_B`; `ρ=|c|/(σ_Aσ_B)`, `a=σ_A√ρ`, `b=sgn(c)σ_B√ρ` seçilirse `ab=c` olur ve gürültü varyansları `σ_A²(1−ρ)`, `σ_B²(1−ρ)` kalır (negatif olmaz). Üçü de aynı `Σ`yı verir. ∎
**Sonuç.** `P₀`ın simetrik her fonksiyoneli (korelasyon, karşılıklı bilgi, kosinüs, Gram matrisi, kısmî korelasyon) yön hakkında **sıfır bilgi** taşır. Gömme vektörlerinden sebep→netice oku çıkmamasının sebebi budur.

**Teorem 2 (değişmezlik asimetrisi).** `A→B` modelinde, ahval yalnız `A`nın yasasını değiştirsin. O hâlde `β_{B|A}(e)=β` sabittir, ama `β_{A|B}(e)= β v_e /(β² v_e+σ_B²)`, `v_e=Var_e(A)`, `β≠0` iken `v_e`nin **kesin monoton** fonksiyonudur; `v_e` değişirse `β_{A|B}` değişir. Dolayısıyla `δ(A→B)=0 < δ(B→A)`. *İspat:* `g(v)=βv/(β²v+σ²)` için `g'(v)=βσ²/(β²v+σ²)² ≠ 0`. ∎
Karışık yapı `A←Z→B` için `β_{B|A}=ab·Var(Z)/(a²Var(Z)+σ_A²)` ve `Var(Z)` veya `σ_A²` değişince değişir; yani karışık yapı da `δ>0` çıkar ve ma'kûl sayılmaz.

### 1.3 Hikmet (gaye): varyasyonel kurucu

`B` yalnız her ahvalde sabit değil, **niçin öyle olması icap ettiği** de bilinir: `B(A)=argmin_x L(x;A)` ve `L` `x`te `m`-kuvvetli konveks, `∇_xL` `A`da `ℓ`-Lipschitz ise
`‖B(A)−B(A')‖ ≤ (ℓ/m)‖A−A'‖`. *İspat:* `m`-kuvvetli konvekslik gradyanı `m`-kuvvetli monoton yapar; `B(A)`, `∇_xL(B;A)=0` çözümüdür. `m‖B−B'‖² ≤ ⟨∇L(B;A')−∇L(B;A),B'−B⟩ ≤ ℓ‖A−A'‖‖B'−B‖`. ∎ Hikmet = bir enerji yasasının **tek** küçültücüsü olmak; KKT şartı "icap"ın cebirsel şeklidir.

### 1.4 Ölçü (deney 1)

Altı ortamlı sentetik dünyalarda üç yapı üretildi (`A→B`, `B→A`, `A←Z→B`; her biri 400 dünya, her ortamda gürültü ölçekleri rastgele).

| Ölçü | `A→B` ayırma AUC'u |
|---|---|
| `|korelasyon|` (karışıklarla birlikte diğerlerine karşı) | 0,606 |
| ma'kûliyet kusuru `−log δ` (diğerlerine karşı) | **0,995** |
| `|korelasyon|` (yalnız karışıklara karşı) | 0,712 |
| ma'kûliyet kusuru (yalnız karışıklara karşı) | **0,996** |
| yön doğruluğu `A→B` dünyalarında | **1,000** |
| yön doğruluğu `B→A` dünyalarında | **0,9975** |

---

## 2. İstidlâl ve burhan

### 2.1 Tarif

**Hasr.** Hipotez uzayı `Ω`nın sonlu, ayrık ve tam örten bir bölüntüsü `ℋ={H₁,…,H_k}`.
**Mekanizma.** Çok değerli eser haritası `F: ℋ → 2^O`. `o` eserinin **lifi** `Φ(o)={Hᵢ : o∈F(Hᵢ)}`.
**Delâlet.** `o`, `Hᵢ`ye delâlet eder ⇔ `Φ(o)={Hᵢ}`. **Burhan** = hasr-tam bir bölüntü üzerinde delâlet.
**Çözülen bilgi:** `I(o)=log k − log|Φ(o)|`; burhan ⇔ `I(o)=log k`.

### 2.2 Teoremler

**Teorem 3 (kesinlik olasılığın limiti değildir).** Bayes güncellemesi `πᵢ ∝ πᵢ⁰ Lᵢ(o)` ve her `Lᵢ(o)>0` (tam destekli, softmax ve Gauss gürültülü her modelde böyle) ise hiçbir sonlu `o` için `πᵢ=1` olmaz. `πₖ=1` ⇔ `Lⱼ(o)=0` her `j≠k` için. *İspat:* `πₖ=1/(1+Σ_{j≠k}(πⱼ⁰Lⱼ)/(πₖ⁰Lₖ))` ve toplam sıfır olabilmesi için her terim sıfır olmalı. ∎
Yani kesinlik, olasılık sayısının **yüksekliği** değil, desteğin **elenmesi**dir (0-1 mantık düzeyinde bir olay). Gürültülü kanalda (hata oranı `ε`) `n` gözlem sonunda log-oran `Λₙ=n·ln((1−ε)/ε)` sonlu kalır; elenme varsa `Λ=∞`.

**Teorem 4 (burhanın kalitesi hasrın kalitesidir).** `o` gerçekte `H₀∉ℋ` yüzünden doğmuş olsun (`o∈F(H₀)`). `ℋ`den elenme ile varılan "kesin" hüküm yanlıştır. Burhanın yanlış çıkma payı, listelenmemiş hipotezlerin ön kütlesi `π⁰(Ω∖∪ℋ)`'den küçük olamaz. *İspat:* elenme ile hükmedilen hipotez ancak `ℋ` içinde seçilir. ∎
Bu, kitabın "diğer kolu bırakmayan tasnif" ısrarının riyazî gerekçesidir.

**Teorem 5 (geri problemin iyi konumluluğu).** `F` doğrusal ve sayısal olarak enjektif (`σ_min>0`) ise `‖δc‖/‖c‖ ≤ κ(F)·‖δo‖/‖o‖`, `κ=σ_max/σ_min`. Burhan-ı innî (eserden müessire) delâleti için **tekillik** (lif tek) ve **kararlılık** (`κ` makul) birlikte aranır. Lif büyükse (`|Φ(o)|>1`) eser birçok müessire uyar, delil değil emâre kalır.

---

## 3. İz'an (tasdik)

### 3.1 Tarif

İnanç hâli `b∈Δ^{k−1}` (hasr üzerinde). Bayes güncellemesi `bᵢ(t+1) ∝ bᵢ(t)Lᵢ(oₜ)` ayrık **replicator dinamiği**dir.
**Devrilme maliyeti** `Λ(b)=ln(b_(1)/b_(2))∈[0,∞]` (en yüksek ve ikinci inanç): lehteki hükmü devirmek için gereken en az birikmiş ters log-delil.

**Tabakalar:**
* **şek:** `Λ≈0` (merkeze yakın; dinamikte kararsız eyer).
* **zan:** `0<Λ<∞` (iç noktada kararlı, rakip kütlesi pozitif).
* **cezm:** `Λ=∞`, yani rakip kütlesi sıfır; simpleksin yüzleri değişmezdir (`bⱼ=0 ⇒ bⱼ(t)=0`), sonlu hiçbir delil onu devirmez, **ancak öncül (hasr) bozulursa devrilir**.

**İlim (kelâmî)** dörtlüsü: `(cezm, mutâbakat, sebât, delil)` = `(Λ=∞, b_top=gerçek hipotez, Λ=∞ kalma tüm geçerli delillerde, bir türetme nesnesi var)`.

### 3.2 Teorem 6 (iz'an skor değildir)

`b_top=p` iken ikinci inanç `b₂` için `(1−p)/(k−1) ≤ b₂ ≤ 1−p` olduğundan `ln(p/(1−p)) ≤ Λ ≤ ln((k−1)p/(1−p))`. `k>2` iken aynı `p` farklı `Λ` verebilir (rakip kütlesi bir rakipte toplanırsa `Λ` küçük, rakiplere yayılırsa büyüktür). Dolayısıyla "iz'an" tek bir skor değil, `(tabaka, Λ, sebât)` üçlüsüdür; `p` onu belirlemez.
**Ölçü (deney 2):** `ε=0,05`, `k=5`: `n=3,5,10,20,40` gözlemde `Λ=8,83; 14,72; 29,44; 58,89; 117,78` nat, `p=0,9994; 0,999998; 1−10⁻¹¹; 1,0 (sayısal); 1,0 (sayısal)`. Gürültülü kanalda `p`, kayan noktada 1,0'a yuvarlanır ama `Λ` sonlu kalır; elenmeyle gelen cezmde `Λ=∞`.

### 3.3 Sınanabilirlik

Bir etmenin bir önermede iz'ana sahip olduğu **davranışla sınanır:** (i) **histerezis:** inanıştan vazgeçiş eşiği, inanma eşiğinden düşüktür; (ii) `Λ`dan küçük bütçeli karşı delil eylemi değiştirmez. Bu sınama herhangi bir sisteme (insan, model) uygulanabilir; ben burada hiçbir sistemin onu **sahip olmadığını** iddia etmiyorum, tarifi sınanabilir kılıyorum.

---

## 4. Kavramsallaştırma

### 4.1 İki kuruluş

**(a) Galois kapanışı.** Bağlam `(G,M,I)`; `A'={m: ∀g∈A, gIm}`, `B'={g: ∀m∈B, gIm}`. Kavram = `(A,B)`, `A'=B`, `B'=A`. Kapanış operatörü `c(B)=B''` ile "en küçük kapalı küme" yeni kavramı **tarifinden** verir; eleman bulunması gerekmez (genişlemesi boş olabilir).
**(b) Değişmezlik kavramı (Erlangen).** Bir grup `G` `X` üzerinde etki etsin. Kavram = `G`-değişmez bir `f:X→Y`, yani yörünge uzayı `X/G` üzerinde bir fonksiyon. Örnek: **adalet** `J(x)=n·min_i x_i` (en küçük payın payı), `S_n` (kimlik permütasyonları) altında değişmez; "adil mi" sorusu **kimin kim olduğuna** bağlı olmamalıdır. **Sonsuzluk** `F(X)=1+X` cebirinin başlangıç cebiridir (`ℕ,0,s`): serbest inşa, örnek gerekmez.

### 4.2 Teorem 7 (örneklemden kavram çıkmaz)

`D⊂X` bir temel bölge (her yörüngeyle en çok bir noktada kesişir) ve örneklem `S⊂D` olsun. Bu hâlde (i) `f|_S` bilgisi, `G`-değişmez `f`yi **ancak `G` biliniyorsa** tamamen belirler, (ii) `G` kendisi `S`den **tanınamaz**: her `H≤G` için `H`-değişmez uzantılar `S` üzerinde aynı veriyi verir. Yani kavram `(f|_D, G)` çiftidir; `G` verinin içinde değil, tarifin içindedir.
*İspat:* değişmezlik `f(gx)=f(x)` olduğundan `D`nin yörünge kapanışı `X`i kaplar. `S⊂D`de iki noktanın aynı yörüngede bulunması yoktur, dolayısıyla veri `G`nin hiçbir elemanını sınamaz. ∎

### 4.3 Ölçü (deney 3)

`n=4` kişi arasında pay dağılımı. Eğitim örnekleri **sıralı** (1. kişi hep en çok alan) bölgeden; model 3. dereceden polinom ridge.

| Ölçü | Sonuç |
|---|---|
| eğitim bölgesinde RMSE | 0,000 |
| kimlikleri permüte edilmiş verilerde RMSE | **1,092** |
| öğrenilen fonksiyonun değişmezlik kusuru | **0,978** |
| tanımdan gelen adalet fonksiyonunun kusuru | 0 |
| öğrenileni 24 permütasyon üzerinden **simetrileştirince** RMSE | 0,774 |

Simetrileştirme kavramı **kurtarmaz** (0,774): öğrenilen fonksiyon, sıralı bölgede "dördüncü kişinin payı"nı öğrenmişti, simetrileştirmek onu ortalama pay yapar; kavram bu değildir. Bu, Teorem 7'nin ikinci maddesinin sayısal şahididir: `G`yi tarif etmeden, örnekten çıkan fonksiyonun üzerine grup eklemek doğru kavramı vermez.

---

## 5. Birleşik sonuç: dört yapı

| Hâl | `P₀`dan çıkar mı | İhtiyaç duyduğu ek yapı | Biçim |
|---|---|---|---|
| ma'kûliyet | Hayır (Teorem 1) | ahval ailesi `𝓔` / müdahale | `δ(A→B)` |
| istidlâl/burhan | Hayır (Teorem 3, 4) | hasr (tam bölüntü) ve eser haritası `F` | lif `Φ(o)`, `I(o)` |
| iz'an | Hayır (Teorem 6) | dinamik ve engel (potansiyel kuyusu) | `(tabaka, Λ, sebât)` |
| kavram | Hayır (Teorem 7) | grup `G` veya kapanış operatörü | yörünge uzayı `X/G` |

**Cümle olarak:** İstatistik = `P₀` üzerinde hesap. Muhakeme = `P₀` + dört ek yapı üzerinde hesap. Fark, hesabın derinliği değil, **girdinin türüdür**.

## 6. Projeye uygulama (denenmedi)

1. **Kök illiyeti.** Teorem 1 şunu açıklar: tek bir gömme uzayı simetrik ikinci mertebe bilgidir, ok çıkarmaz (ölçtüğümüz AUC 0,53–0,60). Teorem 2'ye göre okun kaynağı **bağımsız ahval**dir. Kök vektörleri için ahval = **birbirinden bağımsız kodlayıcılar** (farklı modeller, diller, lügat kaynakları). Önerilen usul: aynı kök çiftinin ilişkisini her kodlayıcıda ölç, `β_{j|i}` ve `β_{i|j}`nin kodlayıcılar arası dağılımına `δ`yı uygula; kusuru küçük olan yön ma'kûl yöndür. Denenmedi.
2. **Burhan.** Teorem 4: ispat ağındaki her hücrenin burhan değeri, o hücrenin bölüntüsünün tamlığı kadardır. Her hasr dalı için `π⁰(Ω∖∪ℋ)` tahmini yazılabilir.
3. **Tasdik tabakaları.** `3-I 197`deki cezm · zan · şek, §3.1'deki `Λ` ile **sayıya** bağlanır.
4. **Kavram.** "Adalet", "sonsuzluk" gibi kavramlar için tarif, örneklem yerine `(G, f)` çiftidir (Teorem 7).

## 7. Dürüst sınırlar

* Deneyler sentetiktir. `A→B` dünyalarında AUC'un 0,995 çıkması çerçevenin ayırma gücünü gösterir, gerçek dünyada ahval ailesinin bulunup bulunmayacağını göstermez.
* Teorem 3, 4, 6 hesap olarak elemanter; yeni olan **kurulumdur**, ispat zorluğu değildir.
* Bu dosya "yapay zekâ muhakeme edemez" demez. Dört ek yapıyı alan bir sistem bunları hesaplayabilir; bu dosya yalnız hangi ek yapıların gerektiğini yazar.
* "Aklın bizzat kendi zâtından gelen nur", "hakikatin şuuru" gibi ifadeler bu dosyada matematiğe **çevrilmemiştir**; yalnız dört işlevsel hâl çevrilmiştir.
