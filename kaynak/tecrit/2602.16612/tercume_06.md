# 2602.16612 — Tercüme, Kısım 6 (kaynak satır 1940–2269)

> Not: Şekiller (`\tikzfig{…}`) metinde yoktur; yerleri `[Şekil/dizge: ad]` ile işaretlenmiştir. `\rl{}`, `\rlb{}` gibi gözden geçirme makroları çevrilmiştir, `\st{}` (üstü çizili) metin atlanmıştır. Çeviri yapay zekâ çevirisidir, insan doğrulaması yoktur.

## Soyutlama: sürekli PQC'ler ile
Bölüm "kuantum soyutlama"da yalnız sonlu klasik sistemlerle çalıştık; oysa pratikte kuantum modeller, girdileri $I$ ve çıktıları $O$ **sürekli** ($\mathbb{R}^n$) değerli PQC'ler olarak gerçeklenir. Üstelik PQC'nin tarif ettiği bütün fonksiyon genellikle bir ölçümün (veya ölçümler topluluğunun) **beklenti değeri** alınarak elde edilir; böylece her girdiyi beklenti değer(ler)ine götüren belirleyici bir $I \to O$ eşlemesi çıkar. Gerçekte $\QC$, $\mathbb{R}$ gibi sonsuz klasik sistemleri içeren ve beklenti değerleri klasik alt kategori üzerinde ek bir grafik unsur olarak modelleyen benzer tanımlı bir $\Hyb$ kategorisine yükseltilebilir (HybPaper). İleride yaklaşımımızı bu tür PQC'ler üzerinde işleyen soyutlamaları kapsayacak şekilde genişletmek ilginç olacaktır.

## Kuantum nedensel soyutlama
Kuantum soyutlama bölümünde, bileşimsel model sayılan kuantum devrelerinden yüksek seviyeli klasik nedensel modellere soyutlamalar gördük; kuantumdan klasiğe **gerçekten nedensel** bir soyutlamayı tarif etmek ise bir **kuantum nedensel model**den (Barrett vd. 2019; Allen vd. 2017) soyutlama gerektirir.
Costa ve Shrapnel'e ait, bileşimsel model olarak tanımlanabilen (Örnek QCM-as-comp-model-over-DAG) esasen belirli bir kuantum nedensel model alt sınıfı vardır; bunlar nedensel yapıdan çok bileşimsel yapı üzerinden tanımlanır. Fakat genelde kuantum nedensel modeller "yüksek mertebeden eşlemeler" ile tanımlanır ve bu yüzden (teknik açık sorular sebebiyle) henüz doğrudan bileşimsel model sayılamazlar. Yine de kuantum nedensel soyutlama kavramları, kuantum teorisinin temelleri ve nedensellik felsefesi açısından —dekoherensin "klasik gerçekliğin nedensel bakımdan tutarlı zuhuru"nu ne zaman verebileceğini incelemenin bir yolu olarak— ilginç olurdu.¹

¹ *Başka kuantum nedensel model çerçeveleri de vardır; fakat bunlar burada önerilen temel suali incelemeye uygun görünmez. Barrett vd. ile Allen vd.'nin çerçevelerine ve Costa–Shrapnel'in özel hâline ek olarak, Henson–Lal–Pusey'in kavramı "tam kuantum" değildir: ölçüm sonuçları gibi klasik değişkenler kavramın içine zaten gömülüdür; bu özelliği paylaşan başka çerçeveler de vardır (Fritz 2012, Laskey 2007, Pienaar 2015, Ried 2015, Ferradini 2025). Bunların ve başka çerçevelerin genel görünümü için Lorenz 2020 ve Allen 2017'ye bakınız.*

Gerçek kuantum nedensel soyutlamanın geliştirilmesi bu yüzden ileriki işe bırakılmıştır; bileşimsel model kavramını yüksek mertebeden eşlemeleri de içine alacak şekilde genişleterek ilk adımı atan Bölüm (kuantum soyutlama) ve Ek (izli kategori üzerinden soyutlama) olası başlangıç noktalarıdır.

## Döngüsel yapılar ve yaklaşık sürümler
Bu çalışmanın kullandığı nedensel model kavramı —literatürün çoğundakinden birçok bakımdan daha genel olsa da— **döngüsüzlüğü** (asiklik olmayı) varsaymıştır.
Oysa genelde döngüsel modeller üzerinden nedensel soyutlama incelemek için sebepler vardır: örneğin zamanla evrilen sistemlerin dengelenmesinin nedensel model bakışıyla incelenmesi (Rubenstein 2017); ayrıca XAI alanında makine öğrenmesi modellerinin yorumlanabilirliğinin de döngüselliği gerektirdiği ileri sürülmüştür (Geiger 2023).²

² *Dikkat: döngüsel nedensel modeller literatürünün geri kalanından farklı olarak Geiger 2023'teki kavram mümkün olan en zayıfıdır: esasen değişkenler üzerinde herhangi bir fonksiyondur; tek çözüm istemez, dışsal değişkenler üzerindeki bir stokastiklik verildiğinde çıktılar üzerinde iyi tanımlı bir olasılık dağılımı doğurmasını da istemez. Do-müdahalelerinden daha genel müdahalelere ve döngüsel yapılara izin verip çelişkili ya da tutarsız modelleri dışarıda bırakmak, şimdiye dek basit bir karakterizasyonu olmayan, önemsiz olmayan (non-trivial) bir iştir.*

Nedensel modellerin ve soyutlamanın kategorik işlenişini döngüsel nedensel modellere genellemek ilginç olurdu. Bunun tabiî bir yolu, bir $\modelM$ modelinin doğurduğu paralel-mekanizma süreci $\parmechdiag_\modelM$ ile Ek'te (izli kategori üzerinden soyutlama) çizilen "iz hilesi"dir; bir başka başlangıç noktası Ferradini 2025'in çerçevesidir. İkisi de kuantum nedensel modellerde soyutlamanın incelenmesiyle de doğal biçimde bağlantılıdır.

Kategorik soyutlama işlenişini genişletmenin bir başka yönü, makine öğrenmesi bağlamlarında önemli olan **yaklaşık soyutlamalara** (Beckers 2020; Geiger 2024; Geiger 2023) izin vermektir. Burada her sorgu için tutarlılık şartının tam olarak sağlanması istenmez; bunun yerine sol ve sağ tarafların uygun bir anlamda birbirine yakın olması istenir.

## Daha ileri biçimselleştirme
Bu çalışmanın temel tanımlarını biçimselleştirmede kategorik bakış açısından doğal olan bir adım daha vardır. Bu, nesneleri $\catC$ içindeki modeller, morfizmaları ise hem \qdown'ları hem \qup'ları kapsayacak şekilde tanımlanan bir $\Model(\catC)$ kategorisini tanımlamaya dayanır. Bu yaklaşımın ayrıntıları ve temel tanımları Ek'te (further-formalisation) bulunur; ileride tam geliştirilmesi ilginç olurdu.

Yaklaşımımızı (nedensel) soyutlamalar ile bilgisayar bilimindeki kategorik soyutlama kavramları (örneğin programlama dilleri veya tipler arasındakiler) arasındaki bağlantıları keşfetmek için kullanmak da ilginç olurdu. Bu sonuncular da çoğunlukla funktörler ve doğal dönüşümlerle biçimlendirilir; ki bunlar artık ayrıca eşlenikler (adjunction) oluşturur.

*[Kaynakça işaretleri atlanmıştır.]*

---

# Ek A. İspatlar

**Önerme (Değişken hizalama notu) ispatı.** Her monoidal $\HtoL \colon \strucV^*_H \to \strucV^*_L$ funktörü, $\varV_H$ içindeki her $V$'yi $\varV_L$ içinde bir $\HtoL(V)$ listesine gönderir ve özdeşlikleri korumalıdır. $\HtoL$ sorguları sorgulara gönderdiğinden, $\HtoL(Q_{(V)}) = Q_X$ olacak şekilde $\varV_L$ içinde bir $X$ altkümesi vardır ve o hâlde $\HtoL(V) = X$ olur. Ama bu durumda $\HtoL(Q_{\varV_H}) = Q_Y$ olacak şekilde bir $Y$ altkümesi vardır; bu, $V \in \varV_H$ için $\HtoL(V)$'lerin birleştirilmesine (concatenation) eşit olmalıdır. $Y$ tekrar içermediğinden $\HtoL(V)$'lerin hepsi ayrık olmalıdır. $\LtoH$'nin özellikleri ise \qdown'lar için olanlardır.

**Teorem (CCA, inceltme olarak) ispatı.** Bir yapıcı soyutlama $(\HtoL, \LtoH)$ verilsin. Bir \qdown'ı şöyle tanımlarız: $\HtoL$'yi tiplerde birleştirmeyle, sorgularda ise
$$\HtoL\big(\Do(S) \colon \VinH \otimes S \to X\big) := \big(\Do(\HtoL(S)) \colon \HtoL(\VinH \otimes S) \to \HtoL(X)\big) \tag{sorgu-eşlemesi}$$
ile tanımlarız; burada $\pi(\VinH) = \VinL$ kullanılır. $\LtoH$'yi keyfî tiplerde, (tau-çarpanları) denklemindeki gibi çarpımlar alarak tanımlarız. (CA soyutlama) denkleminin marjinallerini almak, $(\HtoL,\LtoH)$'nin bir \qdown oluşturduğunu söyleyen bütün gerekli doğallık denklemlerini verir.

Tersine, $(\HtoL, \LtoH)$ bir \qdown olsun. $\HtoL(\VinH) = \VinL$ ve $\HtoL$ sorguları sorgulara gönderen monoidal bir funktör olduğundan, (sorgu-eşlemesi)'ndeki gibi olmalıdır; çünkü sağ taraf $\VinL \otimes \HtoL(S)$ girdi tipli tek sorgudur. Şimdi çıktıları $\VoutH$ olan ve $\VintH$'nin tamamına müdahale eden yüksek seviyeli $Q$ sorgusunu düşünelim. O hâlde $\HtoL(Q)$, çıktıları $\HtoL(\VoutH)$ olan ve $\HtoL(\VintH)$'ye müdahale eden alçak seviyeli sorgudur. Dolayısıyla $\HtoL(X)$'lerin hepsi altkümedir ve $\HtoL(\VoutH) \subseteq \VoutL$'dir. Alçak seviyeli girdiler $\HtoL(\VinH \cup \VintH)$ tekrar içermediğinden, $\HtoL(X)$'ler ayrık olmalıdır. Öyleyse $(\HtoL,\LtoH)$ bir değişken hizalamadır (\varalign). O zaman doğallık, (CA soyutlama)'nın sağlandığını temin eder.

**Önerme (müdahale sorguları / interchange) ispatı.** Bir sınırlı CCA verildiğinde $\HtoL$'yi (zayıfCA-sorgu-eşlemesi) ile sorgular üzerinde tanımlar, $\HtoL, \LtoH$'yi her zamanki gibi çarpımlar alarak keyfî tiplere genişletiriz. Bütün sorgu tutarlılık şartları (zayıf-CA-doğal)'dan marjinaller alınarak çıkar.

Tersine, böyle bir \qdown verilsin. Sorguları sorgulara göndermesi gerektiğinden, çıktılarına bakmak $\HtoL(\VoutH) \subseteq \VoutL$ olması gerektiğini gösterir; varsayımla $\HtoL(\VinH) = \VinL$ ve $\HtoL(\VintH) \subseteq \VintL$. Dolayısıyla $\VinH$ ya da $\VintH$ içindeki $X$'ler için $\HtoL(X)$'ler ayrık altkümeler olmalıdır, ve $\VinL$ ile $\VintL$ ayrık olduğundan hepsi ayrıktır. Bu yüzden bir \varalign oluştururlar. Sonra (zayıf-CA-doğal), $\LtoH$'nin doğallığından çıkar.

**Önerme (Model-İndüksiyon) ispatı.** Varsayımla eşleme iyi tanımlıdır; doğallık şartı (ex-trans-induced)'ı doğrulamak kalır.

$\modinnin \circ \modelM = \inmod{\modelM} \circ \modinin$ olduğunu göstermek yeter; çünkü o zaman her $\inti$ müdahalesi için $\modelM$'yi $\transform{\inti}{\modelM}$ ile değiştirerek (ex-trans-induced)'ı elde ederiz. $\vin$, $\Vin$'in keskin bir durumu olsun. $\vnin = \modelMio \circ \vin$ olsun ve $V$'nin bir durumu olarak $v = \vin \otimes \vnin$ tanımlansın. Lemma (sabit noktalar) gereği $v = \parmechdiag_\modelM \circ v$'dir. Dolayısıyla $\modin \circ v = \modin \circ \parmechdiag_\modelM \circ v = \parmechdiag_{\inmod{\modelM}} \circ \modin \circ v$. Lemma (sabit noktalar) tekrar gereği bu, ancak ve ancak $\modin \circ v = \win \otimes \wnin$ yazıldığında $\wnin = \io{\inmod{\modelM}} \circ \win$ ise geçerlidir. $\modin$ (girdilere-saygı) gibi çarpanlandığından $\win = \modinin \circ \vin$ ve $\wnin = \modinnin \circ \vnin = \modinnin \circ \modelMio \circ \vin$ olur. Böylece $\io{\inmod{\modelM}} \circ \modinin \circ \vin = \modinnin \circ \modelMio \circ \vin$. $\vin$ keyfî olduğundan (ve $\catC$'nin yeterince durumu olduğu varsayıldığından) $\io{\inmod{\modelM}} \circ \modinin = \modinnin \circ \modelMio$ sonucuna varırız.

**(DDo-şekil) ve (DII-şekil) denklemlerinin ispatı.** Önce (DDo-şekil)'i doğrularız. $\doendo{p}$, (II-diyagram)'ın sol tarafı olsun; $s$ durumu $p$ ile, $S$ ise $S'$ ile değiştirilsin. O zaman tanım gereği
$$\parmechdiag_{\DDo(S'=p,\rho)} := \modin^{-1} \circ \parmechdiag_{\inmod{\modelL}_{\Do(S'=p)}} \circ \modin = \modin^{-1} \circ \doendo{p} \circ \parmechdiag_{\inmod{\modelL}} \circ \modin = \modin^{-1} \circ \doendo{p} \circ \modin \circ \parmechdiag_\modelL;$$
önce (II-diyagram), sonra son adımda (ex-trans-induced) kullanılmıştır. Sonra (DII-şekil) denklemi, (II-diyagram)'ın sağ tarafı kullanılarak bunun özel bir hâlidir; şunu gözlemlediğimizde: çıktıların her $Y_j$ altkümesi için (özellikle $Y_j = \HtoL(S_j)$ için)
`[Şekil/dizge: DII-proof]`
geçerlidir; son adımda yine (ex-trans-induced) kullanılmıştır.

**Önerme (c-level-is-d-abs) ispatı.** $\LtoH \colon \semcompM{\modelL}{-} \circ \HtoLS \Rightarrow \semcompM{\modelH}{-}$'yi $\qabsMHfunc$ üzerindeki özdeşlik dönüşümü $1_{\qabsMHfunc}$ ile birleştirerek $\LtoH \circ 1_{\qabsMHfunc} \colon \semMLfunc \circ \HtoL \Rightarrow \semMHfunc$ dönüşümünü elde ederiz; çünkü $\semcompM{\modelL}{-} \circ \HtoLS \circ \qabsMHfunc = \semcompM{\modelL}{-} \circ \qabsMLfunc \circ \HtoL = \semMLfunc \circ \HtoL$ ve $\semcompM{\modelH}{-} \circ \qabsMHfunc = \semMHfunc$.

## A.1 Mekanizma seviyesinde nedensel soyutlama
Mekanizma seviyesinde nedensel soyutlama karakterizasyonumuzun ispatına doğru çalışıyoruz.

Önce bir nedensel $\modelM$ modeli için açık DAG $G=G_\modelM$ ile ilişkili ağ diyagramı $\netdiag{\modelM}$'yi hatırlayalım. Bu diyagramları şöyle karakterize edebiliriz.

**Tanım (ağ diyagramı).** *Ağ diyagramı*, tek çıktılı kutulardan, kopya eşlemelerinden ve atmadan (discard) kurulu bir $\diagD$ tel diyagramıdır:
`[Şekil/dizge: nd-box]` `[Şekil/dizge: nd-copy]` `[Şekil/dizge: nd-disc]`
ve tellerde, kopya eşlemeleri dizisiyle bağlı olmayan teller ayrı etiket alacak, her etiket en çok bir kez çıktı olarak ve herhangi bir kutuya en çok bir kez girdi olarak görünecek biçimde etiketlemeler bulunur.

Bu tür diyagramlar, kısım "nedensel modeller"de özetlenen karşılıkla açık DAG'lere denktir. Bir ağ diyagramı $\diagD$'ye, diyagramdaki her girdi olmayan değişkenin bir çıktıya yolu varsa *normalleştirilmiş* diyoruz. Girdi tellerinin yer değiştirmesine kadar böyle her diyagram şu biçimi alır:
`[Şekil/dizge: normalised-network-diag]`
burada $\diagD'$, $\discard{}$ içermeyen bir ağ diyagramıdır.

**Lemma (tekil ağ diyagramı).** $\SigS=\SigS_\modelM$, girdi değişkenleri $\Vin$ olan açık nedensel $\modelM$ modelinin imzası olsun; $X, Y$ da $\Sig$'den, hiçbiri tekrar değişken içermeyen değişken listeleri olsun.
1. $\strucScd = \FreeCD(\Sig)$ içinde bir $\diagD \colon X \to Y$ diyagramı, ancak ve ancak şu koşulla normalleştirilmiş ağ diyagramıdır: $c_V$'nin $\diagD$'de göründüğü her $V$ değişkeni için $c_V$ yalnız bir kez görünür, $V$ $\diagD$'nin girdisi değildir ve $V$'nin $\diagD$'de bir çıktıya yukarı yolu vardır.
2. $\dagG$'de $X$'ten geçmeyen bir $V \to Y$ yolu varsa, $c_V$ her $\diagD \colon X \to Y$ diyagramına aittir.
3. $\FreeCD(\Sig)$'de en çok bir normalleştirilmiş ağ diyagramı $\diagD \colon X \to Y$ vardır.
4. $X \subseteq \Vin$ ise $\FreeCart(\Sig)$'de en çok bir tek $\diagD \colon X \to Y$ morfizmi vardır.

*İspat.* (1): Tanım gereği her normalleştirilmiş ağ diyagramı ilk iki koşulu sağlamalıdır; yoksa diyagram yalnız kopya eşlemeleriyle bağlı olmayan iki $V$ teli içerirdi; son koşul da normalleştirme için gereklidir. Tersine, bunların geçerli olduğunu varsayalım. Tanım gereği $X, Y$ tekrarsızdır; bu yüzden her girdi ve çıktı en çok bir kez görünür ve $\diagD$ gerekli parçalardan kuruludur. $V$ diyagramın girdisi olsun. Tekrar etmediği ve hiçbir kutudan çıktı olarak doğamayacağı için bütün $V$ telleri kopya eşlemeleriyle bağlı olmalıdır. $V$ girdi olmasın ve diyagramda görünsün. O zaman imzanın doğası gereği $V$ bir $c_V$ kutusunun çıktısı olarak doğmalıdır; $V$ ile $c_V$ arasında başka kutu yoktur, çünkü başka hiçbirinin çıktı tipi $V$ değildir; bu yüzden bir kopya eşlemeleri dizisine indirgenebilir olmalıdır. Üstelik varsayımla böyle tek bir $c_V$ kutusu vardır; bu bütün $V$ örneklerini kapsar. Dolayısıyla $\diagD$ gerçekten bir ağ diyagramıdır.

(2): $Y_i \in Y$ için $V \to Y_i$ yolu olsun. $c_V$'nin $\diagD$'de göründüğünü, böyle bir yolun en kısa uzunluğu $n$ üzerinden tümevarımla kanıtlarız. $n=0$ ise $V = Y_i$'dir. $Y_i$ diyagramın girdisi olmadığından bir kutunun çıktısı olmalıdır ve bu yüzden $c_{Y_i}$ diyagramda görünür. Sonucun $n$ için doğru olduğunu varsayalım. $V$'nin en kısa yolu $(n+1)$ ise, en kısa yolu $n$ olan bir $W$ çocuğu vardır ve $c_W$ $\diagD$'de görünür. O zaman $\diagD$'de bir $V$ teli görünür, ve $V$ diyagramın girdisi olmadığından, benzer biçimde $c_V$ $\diagD$'de görünmelidir.

(3): $\diagD \colon X \to Y$ böyle normalleştirilmiş bir ağ diyagramı olsun. $\diagD$ bir ağ diyagramı olduğundan, girdilerinden her $X_i$ için $c_{X_i}$ $\diagD$'de görünemez. Dolayısıyla genelliği bozmadan her $X_i$'nin modelin kendi girdisi olduğunu varsayabiliriz.

$\dagG=\dagG_\modelM$, $\modelM$'ye karşılık gelen açık DAG olsun (çıktıların herhangi bir seçimi için). O zaman $\diagD$ de köşeleri $\dagG$'nin köşelerinin bir altkümesi olan bir açık DAG $H$'ye karşılık gelir. Üstelik $\diagD$, $\Sig$'den kurulduğu için $H$'nin kenarları $\dagG$'nin kenarlarının bir altkümesidir ve $V \in H \setminus \invar(H)$ ise $\Pa^\dagG(V) \subseteq H$'dir ve bütün $\Pa^\dagG(V) \to H$ kenarları $\diagD$'dedir. Dolayısıyla her $V \in H$ için $\Pa^H(V) = \Pa^G(V)$'dir.

İddia: $H$, $Y$'ye bir yolu bulunan bütün $V$ köşelerinin verdiği $\dagG$'nin tam alt-DAG'ı ile $\diagD$'nin diğer girdilerinin birleşimidir; bu da $H$'yi ve dolayısıyla $\diagD$'yi tekil kılar. Gerçekten, $\diagD$ normalleştirilmiş olduğundan $V \in H \setminus \invar(H)$ ise $H$'de bir $V \to Y$ yolu vardır ve dolayısıyla $G$'de de vardır. Tersine, $V$'nin $G$'de $Y$'ye bir yolu varsa (2) gereği $c_V$ $\diagD$'de görünür ve $V \in H$'dir.

(4): $\diagD \colon X \to ( )$ tek diyagramı $\discard{X}$ ile verilir. $\strucScart$'taki her morfizm belirleyici olduğundan, her $\diagD \colon X \to (Y_1,\dots,Y_n)$ diyagramı şu biçimi alır:
`[Şekil/dizge: cart-factors]`
Bu yüzden $n=1$ durumunu ele almak yeter. DAG üzerinde tümevarımla ilerleriz. $Y$'nin ebeveyni yoksa çıktısı $Y$ olan üreteç yoktur ve tek diyagram, yer değiştirmelere kadar, $\id{Y} \otimes \discard{}$ ile verilir. Şimdi $\Pa(Y)$ boş olmasın ve sonuç $Y$'nin bütün ebeveynleri için geçerli olsun. O zaman $Y$ modelin girdisi, dolayısıyla diyagramın girdisi değildir ve çıktı olarak bir $c_Y$ kutusundan doğmalıdır. O zaman diyagramı şöyle çarpanlayabiliriz ve tümevarımla bu onun tek biçimidir:
`[Şekil/dizge: pay-factor]`
∎

**Önerme (caus-mech-abs-main).** $\HtoLS \colon \strucSH \to \strucSL$ bir cd-funktörü olsun. Değişkenler ve tipler $X$ üzerinde $\HtoL(X) := \HtoLS(X)$ yazalım. O zaman $\HtoLS$ yapısal olarak iyi-huyludur ancak ve ancak $\HtoL(X)$ altkümeleri ayrıksa, $\HtoLS(\VoutH) \subseteq \VoutL$, $\HtoLS(\VinH) \subseteq \VinL$ ve şu kare değişmeliyse:
$$\text{[Şekil/dizge: CCA-square]} \tag{CCA-kare}$$
burada, (sorgu-eşlemesi)'ndeki gibi, $\HtoL(\Do(S) \colon \VinH \otimes S \to X) := (\Do(\HtoL(S)) \colon \HtoL(\VinH \otimes S) \to \HtoL(X))$ tanımlanır. Üstelik sorguları sorgulara gönderen ve diyagramı değiştirmeli kılan böyle tek bir $\HtoL$ funktörü vardır.

*İspat.* Son ifade için: $\qabsMLfunc$ ve $\qabsMHfunc$ tiplerde (değişkenlerde) özdeşlik olduğundan, $\HtoL$ ve $\HtoLS$ nesnelerde anlaşmalıdır. O zaman yukarıdaki, sorgulardan sorgulara tek iyi tipli funktörel eşlemedir; bu yüzden varsa $\HtoL$ funktörü tektir.

(CCA-kare)'nin değiştiğini varsayalım; her $\HtoLS(c_X)$'in normalleştirilmiş bir ağ diyagramı olması gerektiğini iddia ederiz. $Q = \openquery{X}{\VinH}{Y}$ sorgusunu düşünelim; $Y := \Pa(X) \setminus \VinH$. Tanım gereği $\qabsMH{Q} = c_x \otimes \discard{\VinH \setminus \Pa(X)}$. O hâlde $\qabsML{\HtoL(Q)} = \HtoLS(\qabsMH{Q}) = \HtoLS(c_X) \otimes \discard{\HtoL(\Vin \setminus \Pa(X))}$ ve sonuncusu normalleştirilmiş bir ağ diyagramı olmalıdır; dolayısıyla $\HtoLS(c_X)$ de olmalıdır.

$\HtoLS$ yukarıdaki koşulları sağlasın. Tanım gereği yapısal iyi-huyluluk, $(\HtoL(X))_{X \in \VH}$'nin yukarıdaki altküme ve ayrıklık koşullarını sağlamasını gerektirir. Varsayımla her $\HtoLS(c_X)$ normalleştirilmiş bir ağ diyagramıdır. Üstelik girdi olmayan değişkenlerinin $\mechlevelset(X)$ olduğunu iddia ederiz. Gerçekten $c_Y$ diyagramda görünsün; o zaman diyagram içinde $Y$'den $\HtoL(X)$ çıktısına bir yol olmalıdır. Ağ diyagramı olduğundan bu yol diyagramın girdisinden geçemez ve bu yüzden $Y \in \mechlevelset(X)$'dir. Tersine $Y \in \mechlevelset(X)$ ise $c_Y$, Lemma (2) gereği $\HtoLS(c_X)$'de görünür.

Şimdi her yapı türü (Kartezyen, Markov, cd) için (CCA-kare)'nin ancak ve ancak $\HtoL$ ilgili anlamda yapısal iyi-huylu olduğunda değiştiğini gösteririz.

**Kartezyen durum $\FreeCart(\Sig)$:** $\HtoL$ güçlü olmasın. $V \in \HtoL(Y) \cap \mechlevelset(X)$ olsun. O zaman $Y \notin \Pa(X)$'tir. $S := \Pa(X) \cup Y \setminus \VinH$ olsun. $Q = \openquery{X,Y}{\VinH}{S}$ sorgusunu düşünelim, yani (Q-yararlı)'daki gibi tanımlı, fakat şimdi $Y$ hem çıktı hem girdi. O zaman:
`[Şekil/dizge: cond-again]`
$\HtoLS(\qabsMH{Q})$, $V$'nin iki bağlantısız örneğini içerir: biri $\HtoLS(c_X)$'in içinde, biri $\HtoL(\id{Y})$'de. Dolayısıyla bir ağ diyagramı değildir.

Tersine $\HtoL$ güçlü olsun. Keyfî bir $Q = \openquery{X}{\VinH}{S}$ sorgusu alalım. $\HtoLS(\qabsMH{Q})$'nun $\HtoL(S)$'deki hiçbir $V$ için $c_V$ içermediğini göstereceğiz. Gerçekten $c_V$ bu diyagrama aitse, $\qabsMH{Q}$'da görünen ve $c_V$'nin $\HtoLS(c_Y)$'ye ait olduğu bir $c_Y$ vardır, yani $V \in \mechlevelset(Y)$. Fakat $c_Y$ bu biçimde görünüyorsa $Y \notin \HtoL(S)$'tir. Güçlülük gereği $\mechlevelset(Y) \cap \pi(S) = \emptyset$ olduğundan $V \notin \HtoL(S)$'tir. Böylece hem $\HtoLS(\qabsMH{Q})$ hem de $\qabsML{\HtoL(Q)}$, $\HtoL(S)$'deki hiçbir $V$ için $c_V$ içermeyen aynı tipten (ağ) diyagramlardır. $\modelM' := \openmodel_S(\modelML)$ dersek ikisini de bütün girdileri $\modelM'$ modelinin girdisi olan $\strucS_{\modelM'}$ içinde diyagramlar olarak görebiliriz. Lemma gereği $\strucS_{\modelM'}$'de eşittirler ve dolayısıyla $\strucSL$'de de eşittirler.

**Markov durumu $\FreeMarkov(\Sig)$:** $\HtoL$ ekstra güçlü olmasın. O zaman girdi olmayan $X,Y \in \varH$ ve $V \in \mechlevelset(X) \cap \mechlevelset(Y)$ vardır. $c_V$ mekanizması hem $\HtoLS(c_X)$'te hem $\HtoLS(c_Y)$'de görünür; bu yüzden $c_X, c_Y$'nin ikisini de içeren $\strucSH$'daki her ağ diyagramı $\diagD$ için $\HtoLS(\diagD)$, $c_V$'nin iki örneğini içerir ve ağ diyagramı değildir.

Tersine $\HtoL$ ekstra güçlü olsun. Markov durumunda her diyagramın kendiliğinden normalleştirilmiş olduğuna dikkat edelim. $\strucSH$'daki her ağ diyagramı $\diagD$ için $\HtoLS(\diagD)$'nin $\strucSL$'de yine bir ağ diyagramı olduğunu göstereceğiz. Gerçekten böyle her $\diagD$ için, her $c_Y$ en çok bir $\HtoLS(c_X)$'te görünebilir (çünkü $\HtoL$ ekstra güçlü olduğundan $\mechlevelset(X)$'ler ayrıktır) ve dolayısıyla $\HtoLS(\diagD)$'de en çok bir kez görünür. Çıktıya yolu yoksa Markov durumunda diyagramdan kendiliğinden çıkarılır. Dolayısıyla Lemma (1) gereği $\HtoLS(\diagD)$ bir ağ diyagramıdır. Özellikle her $Q \in \Do(\VH)$ için $\HtoLS(\qabsMH{Q})$ bir ağ diyagramıdır ve Lemma (3) ile işimiz biter.

**cd durumu $\FreeCD(\Sig)$:** Doluluk (fullness) başarısız olsun; yani bir $X$ için $Y \in \Pa(X)$ vardır, $Y$ girdi değildir ve $V \in \HtoL(Y)$ için $V \to \HtoL(X)$ yolu yoktur. Şu sorguyu düşünelim:
$$Q = \openquery{X}{\VinH}{(\Pa(Y) \setminus \VinH) \cup (\Pa(X) \setminus Y)}$$
İnşa gereği $\qabsMH{Q}$ şu diyagramdır:
`[Şekil/dizge: free-cd-pic]`
O zaman $\HtoLS(\qabsMH{Q})$, $c_V$'yi içeren $\HtoLS(c_Y)$'yi içerir. Ama $V \to \HtoL(X)$ yolu olmadığından $\HtoLS(\qabsMH{Q})$ diyagramında $c_V$'den çıktıya yol yoktur; bu da onu normalleştirilmiş ağ diyagramı yapmaz ve dolayısıyla $\qabsML{\HtoL(Q)}$'ye eşit olmaz. Demek ki doluluk gereklidir. Ekstra güçlülük de Markov durumu gereği gereklidir; çünkü $\HtoLS$ varsa serbest Markov kategorileri arasında bir funktöre kısıtlanır.

Şimdi ikisi de geçerli olsun. $\Openqueries(\varH)$'deki her $Q$ sorgusu için Markov durumunun ispatı $\HtoLS(\qabsMH{Q})$'nun bir ağ diyagramı olduğunu gösterdi; doluluğun onu normalleştirilmiş de kıldığını göstermek kalır ve Lemma (3) ile işimiz biter.

Bunun için, her $\HtoLS(c_X)$ diyagramının atma içermediğine dikkat edelim: çünkü normalleştirilmiştir ve doluluk diyagramın her girdisinin bir çıktıya yolu olmasını sağlar. Şimdi her $Q$ için $\qabsMH{Q}$ normalleştirilmiş bir ağ diyagramıdır ve (girdilerin yer değiştirmesine kadar) $\diagD' \otimes \discard{}$ olarak çarpanlanır; burada $\diagD'$ atma içermeyen bir ağ diyagramıdır. O zaman $\HtoLS(\qabsMH{Q}) = \HtoLS(\diagD') \otimes \discard{}$; burada yine $\HtoLS(\diagD')$ atma içermez, çünkü her $\HtoLS(c_X)$ içermez. Dolayısıyla $\HtoLS(\qabsMH{Q})$ da normalleştirilmiştir. ∎

**Teorem (strongCCAnew) ispatı.** Mekanizma seviyesinde nedensel soyutlamayı karakterize eden ana sonucu şimdi ispatlarız.

(funktör) ⟹ (mekanizma-seviye-CCA): Bu koşulları sağlayan $(\HtoLS, \LtoH)$ verilsin. Önerme (caus-mech-abs-main) gereği $(\HtoL, \HtoLS, \LtoH)$'yi bir mekanizma seviyesi soyutlama ve dolayısıyla mekanizma CCA yapan tek bir $\HtoL \colon \Do(\VH) \to \Do(\VL)$ vardır.

(mekanizma-seviye-CCA) ⟹ (yapıcı-CCA-iyi-huylu): $(\HtoL, \HtoLS, \LtoH)$ verilsin; varsayımla $(\HtoL, \LtoH)$ bir yapıcı nedensel soyutlamadır. İlki mekanizma seviyesi soyutlama olduğundan (CCA-kare) değişir; bu yüzden $\HtoLS$ yapısal iyi-huyludur ve dolayısıyla $\HtoL$ hizalaması da her yapı türü için yapısal iyi-huyludur.

(yapıcı-CCA-iyi-huylu) ⟹ (mekanizma-seviye-CCA): $(\HtoL, \LtoH)$, $\HtoL$ yapısal iyi-huylu olan bir yapıcı soyutlama olsun. O zaman $\HtoL$ sorgular üzerinde $\Do(S) \mapsto \Do(\HtoL(S))$ ile işler.

Bütün $X$ değişkenleri için $\HtoL(X) = \HtoLS(X)$ ile anlaşan, yapısal iyi-huylu tek bir $\HtoLS$ funktörünün varlığını iddia ederiz.

Gerçekten $\HtoLS$ yapısal iyi-huyluysa Önerme (caus-mech-abs-main) gereği (CCA-kare), $\HtoL \colon \Do(S) \mapsto \Do(\HtoL(S))$ sorgu eşlemesi için değişir; ki bu, Teorem (CCA-inceltme) gereği yapıcı soyutlamada $\HtoL$'nin tanımıdır. Dolayısıyla kare değişmelidir.

Şimdi girdi olmayan her $X \in \VninH$ için (güçlü-CA)'daki $\HtoLS(c_X)$'i tanımlamalıyız. $S := \Pa(X) \setminus \VinH$ ve sorguları şöyle tanımlayalım:
$$Q_X := \openquery{X}{\VinH}{S} \qquad \HtoL(Q_X) = \openquery{\HtoL(X)}{\VinL}{\HtoL(S)} \tag{Q-yararlı}$$
birincisini tanımlamak için $\VninH \subseteq \VoutH$, ikincisi için ise $\HtoL(\VoutH) \subseteq \VoutL$ kullanılır; çünkü $\HtoL$ bir \varalign'a aittir.

O zaman $\qabsMH{Q_X}$ normalleştirilmiş bir ağ diyagramıdır ve $\strucSH$'da:
`[Şekil/dizge: diagD-cond]` (S-özellik)
(CCA-kare) değiştiğinden:
`[Şekil/dizge: pis-unique-2-nodots]` (pis-tanım)
$\diagD_X := \HtoLS(c_X)$ diyagramı için; son adımda (Q-yararlı) ile $\HtoLS$'nin bir cd-funktörü olması ve $\HtoL(\VinH) = \VinL$ kullanılır. Şimdi sağ taraftaki gibi bir çarpanlamanın varlığının şuna denk olduğunu iddia ederiz:
$$\mechlevelset(X) \cap \VinL = \emptyset \tag{koşul-1}$$
Gerçekten, tanım gereği sol taraf normalleştirilmiş bir ağ diyagramıdır ve bu yüzden $X$'e yolu olmayan her girdi değişkeni basitçe atılmalıdır. O zaman (koşul-1), geri kalanların tam olarak $\HtoL(\Pa(X))$'te bulunduğunu, yani böyle bir çarpanlamanın var olduğunu söyler. Dolayısıyla $\HtoLS$'yi tanımlamak için (koşul-1), her $X \notin \VinH$ için geçerli olmalıdır ve bu durumda $\HtoLS(c_X)$, (pis-tanım)'daki tek $\diagD_X$ diyagramı olmalıdır. Bu da $\HtoLS$'yi, varsa, tekil kılar. $\HtoL$ güçlü ise bu özellik geçerlidir ve $\HtoLS$ tanımlanabilirdir, çünkü $\HtoL(\VinH) = \VinL$'dir. Bu yüzden $\HtoL$ yapısal iyi-huylu olduğunda daima geçerlidir. Son olarak $\LtoH$'nin gerçekten (güçlü-CA-doğal) doğallığını sağladığını denetlemeliyiz. Ama $\catC$'de:
`[Şekil/dizge: pis-proof-simpler-1-nodots]`
(S-özellik), (pis-tanım) ve sorgular için $\LtoH$'nin cd-doğallığı kullanılarak. Son olarak $\catC$ üzerindeki varsayımımız gereği, sağ taraftaki atmalara normalleştirilmiş durumlar uygulamak onları yok eder ve $\HtoL_X \circ \HtoLS(c_X) = c_X \circ \HtoL$ elde edilir. Dolayısıyla $\LtoH$ gerçekten böyle bir cd-doğal dönüşüme kısıtlanır. ∎

**Lemma (Markov-denk) ispatı.** Şart, Önerme (caus-mech-abs-main) gereği açıkça gereklidir; çünkü $Q = \openquery{\VoutH}{\VinH}{}$ ile tanımlanan sorgu için $\netdiag{\modelMH} = \qabsMH{Q}$'dur ve (CCA-kare) değişiyorsa $\HtoLS(\netdiag{\modelMH}) = \qabsML{\HtoL(Q)}$ olur; bu da onu normalleştirilmiş bir ağ diyagramı kılar ve $\HtoLS$'nin yapısal iyi-huylu olması tanımı gereği bu koşulları sağlar. Gerçekten $\HtoLS(\VinH) = \VinL$ ve bütün $\HtoLS(X)$'ler ayrık olduğundan $\HtoLS(\VninH) \subseteq \VninL$ olmalıdır.

Tersine bu koşulların yeterli olduğunu gösteririz. Geçerli olsunlar. $\HtoLS(\VninH) \subseteq \VninL$ olduğundan $\HtoLS(X)$'ler $X \in \VninH$ için ayrık altkümelerdir. $\HtoLS(\VinH) = \VinL$ olduğundan aynısı $X \in \VinH$ için geçerlidir. $\VninL$ ve $\VinL$ ayrık olduğundan $\HtoLS(X)$'lerin hepsi ayrıktır.

Her $\HtoLS(c_X)$'in bir ağ diyagramı olduğunu göstermeliyiz. $\HtoL(X)$'ler ayrık olduğundan diyagramın tekrarlı girdisi veya çıktısı yoktur. Şimdi $c_V$'nin iki örneğinin (normalleştirmeden sonra) $\HtoLS(c_X)$'e ait olduğunu varsayalım. İkisinin de $\HtoLS(c_X)$'in bir çıktısına yolu olduğundan $\HtoLS(\netdiag{\modelMH})$'nin de bir çıktısına yolları vardır ve atılamazlar; bu da sonuncuyu ağ diyagramı olmaktan çıkarır, çelişki. Sonra $V \in \HtoL(Y)$, $Y \in \Pa(X)$ olsun. O zaman $Y$ girdi olamaz (aksi hâlde $V$ girdi olurdu ve $c_V$ imzanın parçası olmazdı). O zaman Lemma (2) gereği $c_V \in \HtoLS(c_Y)$'dir. O zaman $c_V$ hem $\HtoLS(c_X)$'te hem $\HtoLS(c_Y)$'de (girdi ve çıktı tiplerinden dolayı) görünür; her birinin ilgili çıktılarına, $\HtoL(X)$ ve $\HtoL(Y)$'ye bir yolu vardır. Bunlar $\HtoLS(\netdiag{\modelMH})$'nin çıktıları olduğundan $c_V$'nin bu iki örneği diyagramdan çıkarılamaz (yani atılmaz) ve bu yüzden bu bir ağ diyagramı olamaz, çelişki. Dolayısıyla Lemma (1) gereği her $\HtoLS(c_X)$ kutusu gerçekten bir ağ diyagramıdır.

Tersine, $\HtoL$ ekstra güçlü olmasın. O zaman girdi olmayan $X,Y \in \varH$ ve $V \in \mechlevelset(X) \cap \mechlevelset(Y)$ vardır. Lemma (2) gereği $c_V$ hem $\HtoLS(c_X)$'te hem $\HtoLS(c_Y)$'de görünür ve tıpkı yukarıdaki gibi bu, $\HtoLS(c_X)$'i ağ diyagramı olmaktan çıkarır, çelişki. ∎

---

# Ek B. Cebirsel yapının korunumu

Müdahaleleri $\Intset^{\mathsf{io}}(\modelV)$, $\Do(\modelV)$ ve $\II(\modelV)$ gibi sorgu imzalarında örgütlemek, nedensel soyutlamayı biçimlendirmede yararlı olmuştur. Fakat (bunların ürettiği serbest kategoriler) çoğunlukla az ilginç bileşimsel yapıya sahiptir: sorguların kendilerinin ötesindeki tek yeni bileşkeler sorguların çarpımlarıdır.

Bununla birlikte müdahalelerin cebirsel yapısının ikinci bir anlamı vardır: onları ardışık olarak uygulayabiliriz. Bu, nedensel soyutlamada rol oynadığından, onu kurulumumuzda yakalayıp yakalayamayacağımızı sormak tabiîdir. Genel modeller ve sorgular için bunu yapmanın yararlı bir yolu şudur.

**Tanım.** Bir $\SigQ$ sorgu imzasının *monoid yapısı* vardır diyelim; aynı tiplere sahip bir $T$ sorgu imzası ve $\SigQ$'nun $T_{mor} \times M_\SigQ$ sorgularına sahip olacağı bir $(M_\SigQ,\bullet)$ monoidi varsa. $T$'nin iki tipi $in, out$ ve tam olarak bir $q \colon in \to out$ sorgusu varsa $\SigQ$ *bir monoid oluşturur* deriz. Monoid yapılı iki sorgu imzası $\SigQ, \SigQ'$ için bir $F \colon \SigQ \to \SigQ'$ eşlemesine, $F((Q,m)) = (F_Q(Q),F_M(m))$ biçiminde çarpanlanıyorsa ve $F_M \colon M_\SigQ \to M_{\SigQ'}$ bir monoid homomorfizmi ise *homomorfizm* deriz.

Önce monoid yapılı sorgulara dair bazı temel örnekleri gözlemleyelim.

**Örnekler.** $\modelV$ somut değişkenler kümesi olsun.
1. $\Openqueries(V)$ sorgu imzasının *monoid yapısı vardır*: $\ioqueries(V) \times \mathbb{P}(\Vint)$; burada $\ioqueries(V)$, $V$ üzerindeki girdi-çıktı sorgularını, $\mathbb{P}(\Vint)$ ise $S \bullet T := S \cup T$ altında altkümelerin monoidini gösterir. Bu durumda monoid çarpmasını, iki sorgunun çıktı altkümeleri aynı olduğunda tanımlı olmak üzere $\openquery{O}{\Vin}{S} \bullet \openquery{O}{\Vin}{T} = \openquery{O}{\Vin}{S \cup T}$ ile $\Openqueries(V)$'nin tamamında kısmî bir işleme genişletebiliriz.
2. $\Do(\modelV)$ sorgu imzası, önemsiz (trivial) "boş" müdahale $\noint$ ve $\Do(X =x) \bullet \Do(Y=y) := \Do(X = x, Y \setminus X = y|_{Y \setminus X})$ bileşimiyle *bir monoid oluşturur*.
3. Daha genel olarak herhangi bir $\Intset$ müdahaleler kümesi için, bileşim altında kapalıysa $\Intsetio$ sorgu imzası *bir monoid oluşturur*: $\{c_{X}\}_{X \in A_{\inti}}$ ve $\{c_{Y}'\}_{Y \in A_{\inti'}}$ "yeni" mekanizmaları olan iki $\inti,\inti'$ müdahalesi için $\inti \circ \inti'$ bileşkesi $\{c_{X}\}_{X \in A_{\inti}} \cup \{c_{Y}'\}_{Y \in A_{\inti'}\setminus A_{\inti}}$ ile tanımlanır; birim $A_{\inti} = \emptyset$ ile verilir.

Bölüm (nedensel soyutlama)'daki nedensel soyutlama kavramlarının çoğu, ilgili müdahale kümelerinde bulunan bu cebirsel yapıyı gerçekten korur. Aşağıdakinin doğrulanması kolaydır ve ispatı atlıyoruz.

**Önerme (CA-kavramları-homomorfizmle).** Örnek (monoid yapılı sorgular)'daki monoid yapılar verildiğinde:
(a) Her yapıcı nedensel soyutlama için $\HtoL \colon \Do(\varH) \to \Do(\varL)$ sorgu eşlemesi bir homomorfizmdir; ve onun tanımladığı \qup'ın $\LtoHquery \colon \Do(\modelV_L) \to \Do(\modelV_H)$ sorgu eşlemesi de homomorfizmdir.³
(b) Her \isoCCA, sorgu eşlemesi $\LtoHquery$ homomorfizm olan bir bütün \qup tanımlar.

³ *Burada $\HtoL$, Tanım (sorgu-ref)'deki kısıt sayesinde yapıcı nedensel soyutlamadaki $\HtoL$ funktörüyle tanımlanan imzalar arası eşlemedir; ve karşılık gelen \qup'ın $\LtoHquery$ eşlemesinin homomorfizm olması, onun tanım kümesinde (ki inşa gereği bileşim altında kapalıdır) homomorfizm olması demektir.*

**Homomorfizm mi, sıra-koruma mı?** Bileşim altında kapalı olan, yani monoid yapılı sorgu imzaları arasındaki bir tam dönüşüm (Tanım exact-trans) için $\LtoHquery$ eşlemesi homomorfizm olabilir de olmayabilir de.
Literatürde bu eşlemenin, $\inti \circ \inti' = \inti'$ olduğunda $\inti \leq \inti'$ ile tanımlanan $\leq$ kısmî düzeni altında **sıra koruyan** olması istenir (Rubenstein 2017; Beckers vd. 2019; Geiger 2023).⁴
Müdahalelerin cebirsel yapısını inceleyen Geiger 2023, bunun yerine müdahaleler arasındaki değişme ilişkilerini önemli sayar.
Homomorfizm olmak hem değişme hem sıra ilişkilerinin korunmasını gerektirir; sonuncusu için, $\inti \circ \inti' = \inti'$ olduğunda $\LtoHquery(\inti') = \LtoHquery(\inti \circ \inti') = \LtoHquery(\inti) \circ \LtoHquery(\inti')$ olur.
Bu yüzden basitçe $\omega$'nın homomorfizm olmasını istemek daha tabiî olabilir.
Bu aynı zamanda *güçlü CA*'nın (Tanım strong-CA) bir sonraki pekiştirmesi için tabiî bir koşul verebilir; bu çalışmadaki bütün güçlü CA örneklerinde sağlanmaktadır.

⁴ *Do-müdahalelerinden daha genelini ele almayan Rubenstein 2017 ve Beckers 2019'da korunması istenen kısmî düzen $\Do(S=s) \leq \Do(S'=s')$ ancak ve ancak $S \subseteq S'$ **ve** $s'|_{S}=s$'dir. Yukarıda ele alınan kısmî düzenin korunması, açıkça bu düzen için sıra korumayı gerektirir.*

*[Kaynak satır 2269'da okuma sona erdi; satır 2270–2587 sonraki kısımdadır.]*
