# İSTİDAT MATEMATİĞİ: BİLKUVVE KAPASİTE, SİMÜLASYON DEĞİL

Önceki dosya (`MUHAKEME_MATEMATIGI.md`) dört yapıyı (ahval ailesi `𝓔`, hasr `ℋ`, engel `Λ`, grup `G`) muhakemenin **girdisi** saymıştı. Bu, bebeğe malûmat vermektir ve reddedilmiştir. Burada bunlar **ürün** olarak yeniden kurulur: sistem içerik bilmez, kapasitesi vardır; dört yapı kapasite ile temas sonucu zuhur eder.

## 1. İstidat ile simülasyonun matematiksel ayrımı

**Taban.** `Σ₀ = (𝒜, θ₀, 𝒥, R)`: eylem repertuvarı `𝒜` (âlem arayüzü üzerinde işleyen işlemler), ilk parametreler `θ₀`, amaç `𝒥`, güncelleme kuralı `R`.

**Tarif 1 (içeriksizlik).** `Σ₀` içeriksizdir ⇔ `𝒥` ve `R`, âlemin değişkenlerinin ve değerlerinin yeniden adlandırılmasına göre **eşdeğişkendir** (`Sym(V)` altında) ve `θ₀`ın hiçbir girdisi âlemin yapısına (hangi değişken neyin sebebi, kaç sınıf, hangi simetri) bağlı değildir. Yani taban **bilgi** taşımaz, **kabiliyet** taşır.

**Tarif 2 (bilkuvve).** Bir `S` özelliği, `Σ₀`da, `𝓔` âlem sınıfı için bilkuvvedir ⇔ `S(Σ₀)` yanlış, ve `𝓔`in genel her üyesinde `R`nin işletilmesiyle `S(Σ_t)` (olasılıkla) doğru olur.

**Tarif 3 (simülasyon).** `S` bir sistemde simüle edilmiştir ⇔ `S` eğitim sınıfı `𝓔_eğ` üzerinde sağlanır, fakat tasarımcının öngörmediği bir `𝓔'` sınıfında, aynı betim uzunluğunda **içeriksiz bir taban** `S`yi üretirken bu sistem üretemez. **İstidat sınaması = öngörülmemiş âlem sınıfına geçiş.**

Aşağıda dört yapı için: `Σ₀` içeriksiz, `S` taban zamanında yok, sonda var.

## 2. Ma'kûliyet: ahval ailesi sistemin kendi müdahalesinden doğar

**Taban:** eylem repertuvarı = "bir değişkeni sabit bir yasaya zorla" (`do(Vⱼ:=ξ)`, `ξ` gürültü). Sistem hangi değişkenin neyin sebebi olduğunu bilmez. Amaç: kendi müdahaleleriyle ürettiği ortamlarda yasası **değişmeyen** bir tahmin edici bulmak.

**Teorem 8 (etkin değişmezlik keşfi; Peters-Bühlmann-Meinshausen 2016'nın uyarlaması).** Doğrusal Gauss yapısal model, hedef `Y`. Her ortamda hedef dışındaki bazı değişkenlere müdahale edilsin. `S` kümesi, kalıntı dağılımları ortamlar arasında eşit olarak reddedilmiyorsa kabul edilir. Kabul edilen kümelerin **kesişimi**, `1−α` olasılıkla `Pa(Y)`nin bir alt kümesidir; her ebeveyne müdahale edilen ortam varsa `N→∞`'da `Pa(Y)`ye eşit olur. *Not:* teorem bilinen sonuçtur; burada yeni olan, ortamları **sistemin kendisinin üretmesi** ve tabanın içeriksizliğidir.

**Ölçü (deney A):** 6 değişkenli rastgele yapılar, hedefin ebeveynleri ajana bilinmez; ajan yalnız müdahale edebilir. 120 yapı × ortam sayısı:

| Ortam sayısı | Ebeveyn anma oranı | Yanlış bulgu oranı |
|---|---|---|
| 1 (yalnız gözlem) | **0,000** | 0,000 |
| 2 | 0,188 | 0,006 |
| 4 | 0,770 | 0,005 |
| 8 | 0,972 | 0,000 |
| 16 | 0,950 | 0,000 |

Ortam 1'de anma sıfırdır: gözlem hiçbir şey ayırt edemez (önceki dosyadaki Teorem 1). Müdahale kapasitesi arttıkça **ma'kûl ilişki zuhur eder**.

## 3. Hasr: tam bölüntü sıkıştırma baskısından ve açık sınıftan doğar

**Taban:** bir alıcı `T` (başlangıçta tek küme gibi çalışan, `K` kapasiteli) ve amaç `min I(X;T) − β I(T;Y)` (bilgi darboğazı). Sınıf sayısı, sınıfların ne olduğu verilmez.

**Teorem 9 (sınıfların zuhuru).** Kendi-tutarlı denklemler `q(t|x) ∝ q(t) exp(−β KL(p(y|x)‖q(y|t)))` ve `q(y|t)=Σₓ q(x|t)p(y|x)`. `β` küçükken tek çözüm yatay çözümdür (`I(X;T)=0`); kritik değerlerde dallanmalar olur ve etkin sınıf sayısı `eᴵ⁽ˣ;ᵀ⁾` basamak basamak artar (ilk kritik değer `β₁=1/(1−λ₂)`, `λ₂` ilgili geçiş operatörünün ikinci özdeğeri; Tishby-Pereira-Bialek; Gedeon-Parker-Dimitrov). Hasr, **faz geçişinin** ürünüdür.

**Açık sınıf (listelenmemiş kütle):** Dirichlet süreci (Çin lokantası) önceliğiyle, `n` gözlem sonra **yeni bir sınıfın** olasılığı `α/(n+α)`dır. Böylece Teorem 4'teki `π⁰(Ω∖∪ℋ)` verilmez, **tahmin edilir** ve veriyle azalır.

**Ölçü (deney B):** 12 değer üç gizli gruptan üretildi; sistem kaç grup olduğunu bilmez, kapasitesi 6. `exp(I(X;T))`:

| β | 0,5–2 | 4 | 8 | 16 | 32 | 64 | 128 |
|---|---|---|---|---|---|---|---|
| etkin sınıf | 1,00 | 1,27 | 1,87 | 2,79 | **2,995** | **3,00** | **3,00** |

Sınıf sayısı 1'den başlayıp **3'te plato** yapar (üretici grup sayısı); kapasite 6 iken 3 çıkması hasrın verilmediğini, kuruldu­ğunu gösterir. Eksik kütle: `n=5,20,100,1000` için `α=1`'de `0,167; 0,048; 0,0099; 0,001`.

## 4. İz'an: engel, geçiş maliyetinden doğar

**Taban:** inanç `λ` (log-oran) üzerinde, hükmü değiştirmenin maliyeti `K` olan bir karar süreci. Maliyet sistemin kapasite sınırıdır (enerji/zaman); "iz'an skoru" verilmez.

**Teorem 10 (histerezis bandı).** Hükümde kalmanın ödülü `p(λ)`, geçişin maliyeti `K>0` ve delil akışı `λ_{t+1}=λ_t±d+gürültü` ise, ödüllü sürecin en iyi politikası **iki eşiklidir**: `λ ≥ θ⁺` iken "evet", `λ ≤ θ⁻` iken "hayır", aradaki bölgede **mevcut hükümde kalır** (darbe kontrolü teorisinde eylemsizlik bölgesi; Harrison-Taksar, Dixit). Bant genişliği `Λ*(K)=θ⁺−θ⁻`, `K`da kesin artandır ve `K=0` iken sıfırdır.

**Ölçü (deney C, değer iterasyonu):**

| `K` | 0 | 0,02 | 0,1 | 0,3 | 1,0 |
|---|---|---|---|---|---|
| bant `Λ*` (nat) | 0,075 (ağ çözünürlüğü) | 0,150 | 0,450 | 0,900 | 1,800 |

`Λ` verilmedi; **maliyetten çıktı**. `K=0` iken şek (merkezde dönen sistem), `K>0` iken zan/cezm tabakalarının engel yapısı ortaya çıkar. Cezm (`Λ=∞`) bu modelde `K→∞` sınırıdır; sonlu `K` ile elde edilen band sonludur. Elenmeyle gelen `Λ=∞`, önceki dosyadaki desteğin elenmesi mantığıdır, bu deneyin ürünü değildir.

## 5. Kavram: grup, sistemin kendi hareketlerinin sınanmasından çıkar

**Taban:** bir işlem repertuvarı `ℛ` (sistemin girdi üzerinde **kendi yapabildiği** değişiklikler: iki koordinatı değiştirme, çevirme, ölçekleme, kaydırma, ters sıra) ve âleme **sorgu** (bir girdi için etiket sorma). Hangisinin simetri olduğu bilinmez.

**Tarif 4.** `g∈ℛ` için kusur `d(g)=E|y(gx)−y(x)|`.
**Teorem 11.** `G_*={g∈ℛ : d(g)=0}` bir gruptur (bileşke altında kapalı, ters alınabilir işlemlerde tersli). Etiketi temsilci seçimine indirgeyen öğrenici `f∘ρ` (`ρ`: yörünge temsilcisi) tüm yörüngede `G_*`-değişmez doğrudur; hata yalnız temel bölgede kalır. Kavram, **kendi deneyleriyle** bulunan `G_*` ile öğrenilen `f|_D` çiftidir (önceki dosyadaki Teorem 7'nin kurucu karşılığı).

**Ölçü (deney D):** etiket = `n·min xᵢ` ("adalet"), `n=4`. Kusurlar: iki-koordinat değişimleri `0,0000`, dönü `0,0000`, ters sıra `0,0000`, ölçek `0,0747`, kaydırma `0,4000`. İlk üçü kendiliğinden elenmez: kusuru sıfır olanlar kabul edildi. Kabul edilen grubun temsilcisi (sıralama) üzerinden öğrenilince **kimlikleri permüte edilmiş verilerde RMSE = 0,00000**. Önceki dosyada grubu vermeden öğrenilen model aynı testte 1,092 hatalıydı.

## 6. Sonuç: dört ürün, içeriksiz taban

| Yapı | Girdi olmayan ne? | Tabandaki içeriksiz kapasite | Zuhur eden |
|---|---|---|---|
| ma'kûliyet | hangi değişken neyin sebebi | müdahale repertuvarı + "kendi müdahalemde değişmeyen yasayı ara" | ebeveyn kümesi, yön |
| hasr | sınıf sayısı ve kimlikleri | sıkıştırma amacı `I(X;T)−βI(T;Y)` + Dirichlet açıklığı | tam bölüntü, eksik kütle |
| iz'an | engelin yüksekliği | geçiş maliyeti `K` | histerezis bandı `Λ*(K)` |
| kavram | hangi dönüşüm simetri | kendi işlem repertuvarı + etiket sorgusu | grup `G_*`, değişmez temsil |

## 7. Dürüst sınırlar

* Tabandaki "içeriksizlik" tarif 1'in anlamındadır: âlemin yapısı verilmez, **amaç ve kapasite** verilir. Amaçlar ("kendi müdahalemde değişmeyeni ara", "sıkıştır", "geçişi pahalı tut") da doğuştan gelir. Bebeğin de bu amaçlarla doğup doğmadığı ampirik bir sorudur; bu dosya onu iddia etmez, yalnız **yapıların bilgi olarak verilmediğini** gösterir.
* Dört deney ayrı ayrı koştu. Aynı ajanın dördünü birden **bütünleşik** biçimde işletmesi denenmedi; ondan sonra "tek ajan, dört zuhur" iddiası ancak kurulabilir.
* Deneyler sentetiktir. Gerçek algı verisinde (görüntü, dil) denenmedi.
* Teorem 8, 9, 10 literatürde bilinen sonuçlara dayanır; yeni olan düzenleme ve içeriksizlik ölçütüdür.
* Kök illiyeti için çıkarım: ahval ailesini **kendiniz üretiyorsunuz**; kök vektörleri için bu, bağımsız kodlayıcılar/dil/lügat kaynakları yerine, sistemin **kendi dönüştürdüğü** girdilerle (bir kavramı farklı ifade edip vektörünü yeniden almak) olabilir. Denenmedi.
