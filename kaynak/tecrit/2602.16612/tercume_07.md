# 2602.16612 — Tercüme, Kısım 7 (kaynak satır 2270–2588, son)

> Not: Şekiller `[Şekil/dizge: ad]` ile işaretlidir. Kaynakta 2317–2344. satırlar `\st{…}` (üstü çizili = yazarlarca silinmiş) içindedir: "Englberger ve Dhami ile karşılaştırma" alt bölümü. Okundu; tercümeye **katılmadı** (yazarların kendi silme işaretine uyuldu), yalnız varlığı burada kayda geçirildi. Çeviri yapay zekâ çevirisidir.

# Ek C. Literatürle karşılaştırma

**Not (Tam dönüşümler).** Tanım (exact-trans)'taki tam dönüşüm kavramı literatürdekilerden şu bakımlardan ayrılır.
1. *Cebirsel yapı:* Bölüm (cebirsel yapı)'da ayrıntılı tartışıldığı üzere, literatür müdahaleler üzerinde sıra koruyan bir $\LtoHquery$ eşlemesi varsayar; biz varsaymayız.
2. *Örtenlik (surjectivity):* Rubenstein 2017 ve Beckers vd. 2019'da (Geiger 2023'ten farklı olarak) tam dönüşümün $\LtoH$ eşlemesinin örten olması **istenmez**. Ancak Beckers vd. 2019'da, bir nedensel *soyutlama* sayılabilmek için $\tau$'nun örten olması gerektiği gösterilir. Biz bunu, nedensel olsun olmasın her soyutlama ilişkisinin temel bir bileşeni sayarız; dolayısıyla Bölüm (soyutlama)'daki iki temel soyutlama türünde de $\tau$ zorunlu olarak bir epimorfizmdir. Bu bakımdan tam dönüşüm kavramımız Beckers vd. 2019'daki bir $\tau$-soyutlamaya daha yakındır.
3. *Nedensel model türleri:* \CF{} (karşıolgusal) soyutlama dışında, hiçbir tanımımız nedensel modellerin türü hakkında —esasen gizli sayılan değişken bulunmaması dışında— varsayım yapmaz: değişkenler ya girdidir ya değildir; $\Vint = V\setminus \Vin$'nin hepsi çıktı olmayabilir, ancak a priori hepsine müdahale düşünülebilir.⁵ Her nedensel soyutlama kavramı ancak üzerinde geçerli olduğu (müdahale) sorguları kümeleri kadar "güçlü" olduğundan, model türünü baştan kısıtlamak esaslı görünmez.
4. *Müdahale türleri:* Rubenstein 2017 ve Beckers vd. 2019'dan farklı olarak Tanım (exact-trans)'ta $\IntsetL$, $\IntsetH$ için Do-müdahalelerle kısıtlama yoktur. (Bu bakımdan bizimki Geiger 2023'teki kavrama yakındır.)

⁵ *Bu yüzden Beckers vd. 2019'daki kilit bir gözlem —onların anlamındaki "olasılıksal modellere" izin vermenin, kök düğümlerdeki olasılık dağılımlarının ince ayarından "haksız soyutlamaya" yol açabileceği— burada geçerli değildir.*

**Not (Güçlü nedensel soyutlamalar).** Tam dönüşümleri keyfî müdahaleler için tanımlasak da kavramsal olarak en önemlileri Do-müdahalelerdir; çünkü hepsine erişimle bir nedensel modelin tamamı belirlenebilir. $\model{L}$ ve $\model{H}$ modelleri arasında nedensel soyutlamanın "sade" bir örneği bu yüzden $\IntsetH$'nin bütün Do-müdahaleleri içerdiği durumdur — Beckers ve Halpern kendi $\tau$-soyutlama kavramına bu durumda "güçlü" derler. *Güçlü CA* kavramımız (Tanım strong-CA) bununla uyumlu olup birkaç noktada ayrılır.
1. Tam dönüşümlerde olduğu gibi (yukarı bkz.), model türüne kısıtlama ve sıra koruma varsayımı yoktur.
2. Daha önemlisi, $\IntsetH$ bütün Do-müdahaleler iken $\model{L}$ a priori kısıtsızdır ve bunun sonucu olarak sorgular üzerindeki $\LtoHquery$ eşlemesi, Beckers vd. 2019'daki gibi $\LtoH$ ile *doğurulan* değil, verilen verinin parçasıdır.

Saik çeşitli düşüncelerden gelir. Birincisi, sinir ağlarına dayalı modern yapay zekâ, nedensel soyutlamanın kapsamını yorumlanabilir değişkenlerin "dağıtık" alçak seviyeli temsillerini beklemeyi gerektirecek şekilde genişletmiştir. İkincisi, kuram açısından nedensel soyutlamayı —makine öğrenmesinden bağımsız olarak nedensel model çerçevesinin zaten içerdiği— genel müdahaleler bağlamında anlamak istenir. Beckers ve Halpern, Beckers vd. 2019'da esasen şunu söyleyen bir varsayım ileri sürerler: "güçlülük" (bütün yüksek seviyeli Do-müdahaleleri) "yapıcılığı" gerektirir, yani \varalign'daki gibi bir bölümlemeyi. Bu sezgi, alçak seviyede de baştan Do-müdahalelerle kısıtlamaya dayanır. Bizim \strongCA kurulumumuzda böyle bir kısıtlamanın $\VL$'nin bir bölümlemesini bulmaya denk olduğunu kontrol etmek zor değildir. Bu, kurulumlardaki öbür farklar sebebiyle onların varsayımını henüz cevaplamasa da, kavramımızın nedensel soyutlamayı daha ileri anlamak için yararlı bir açı sunduğunu düşündürür.

*[Üstü çizili alt bölüm (2317–2344): okundu, çevrilmedi — yukarıdaki nota bkz. İçeriğin özü: Englberger–Dhami 2025'in Markov kategorileri tabanlı tanımının, düzeltmeyle, yapıcı CA'yı değil mekanizma seviyesinde yapıcı soyutlamayı yakaladığı; Önerme 2.1'deki "her jeneratör en çok bir kez" kısıtının tekilliği sağlamadığı ($c_Y \neq c_Y\circ c_X \circ \discard{X}$ örneği); ve yapıcı soyutlamaların onların biçiminde olmayabileceği iddiası.]*

# Ek D. Paralel mekanizma kanalları ve diyagramlarda tutarlılık koşulları

Bölüm (dağıtık soyutlama), bir nedensel modelin doğurduğu (ve tersine onu doğuran) paralel mekanizma kanalı $\parmechdiag_\modelM$ kavramını tanıttı. Burada $\parmechdiag_\modelM$ ile $\io{\modelM}$ arasındaki ilişkiyi, dağıtık soyutlamaların tutarlılık koşullarını ifade etmede yararlı olacak biçimde daha da açıklığa kavuşturacağız.

Bunun için şu kavram yararlı olur. Bir SMC $\catC$, her $X$ nesnesinin bir $X^{\star}$ dualiyle ve $X \otimes X^{\star}$ ile $X^{\star} \otimes X$ üzerinde birim ve karşı-birimlerle (çeşitli aksiyomlara tâbi) geldiği zaman *kompakt kapalı*dır (Selinger 2010). Sadelik için ve ana örneklerimize uyduğundan $X^{\star} = X$ alabiliriz; tanım bu durumda her $X$ nesnesinin $X \otimes X$ üzerinde ayırt edilmiş bir durum ve bir etki (effect)⁶ çiftiyle gelmesine indirgenir; bunlar sırasıyla *fincan* (cup) ve *kapak* (cap) olarak çizilir ve şunları sağlar:
`[Şekil/dizge: cap-sym, cup-sym, snake]` (kompakt-kapanış)
$\catC$ ayrıca bir cd-kategorisi ise ek olarak şunlar istenir:
`[Şekil/dizge: cap-2, mult-map2]` (kompakt-kapanış-cd-1)

⁶ *Bir $X$ nesnesi üzerindeki etki, $I$ birim nesne olmak üzere $X \rightarrow I$ morfizmidir.*

Her keskin $x$ durumu için, "$x$'i baş aşağı çevirmek" olarak çizilen $x^\dagger$ ile gösterilen karşılık gelen belirleyici bir etki vardır:
`[Şekil/dizge: cap-3]` (xupsidedown)
(kompakt-kapanış-cd-1)(a)'dan, her normalleştirilmiş keskin $x$ durumunun $x^\dagger \circ x = 1$ sağladığı, (b)'den ise şunun geçerli olduğu çıkar:
`[Şekil/dizge: sharp-2]` (keskin-etki-kopya)
(keskin-etki-kopya)'yı $y$ ile bileştirerek, bütün keskin $x, y$ durumları için şu elde edilir:
`[Şekil/dizge: condition]` (kompakt-kapanış-2)
Ana örneğimiz, $\FStoch$ Markov kategorisinin, nesneleri yine sonlu kümeler olan ve $M \colon X \to Y$ morfizmleri artık keyfî (stokastik olması gerekmeyen) pozitif matrisler $M(y \mid x)$ olan daha geniş kompakt kapalı cd-kategorisi $\MatR$'nin içinde yer almasıdır. Burada fincan ve kapak her ikisi de yalnızca $\delta_{X,X}$'tir, yani "kusursuz korelasyon".

Son olarak, kompakt kapanışın ayrıca, kısmî iz kavramının kategorik genellemesi olan bir izli kategori de doğurduğunu hatırlarız (Selinger 2010). Her $C$ nesnesi için karşılık gelen fincan ve kapak, her $A,B$ nesneleri için $\Tr_C \colon \catC(A\otimes C, B \otimes C) \rightarrow \catC(A, B)$ eşlemesini tanımlar; $\Tr_C(f)$ şu şekilde verilir:
`[Şekil/dizge: trace-in-diags_b]`
Bütün bu parçalar birlikte, bir fonksiyonun sabit noktaları ile izler arasında bir ilişki verir; bu bizim kurulumumuzda $\parmechdiag_\modelM$ ile $\modelM$ arasında şu ilişki olarak belirir.

$\catC$'nin *yeterince* normalleştirilmiş keskin durumu vardır deriz: bütün normalleştirilmiş keskin $x$ durumları için $f \circ x = g \circ x$ iken $f = g$ oluyorsa.

**Lemma.** $\catC$, yukarıdaki özellikleri sağlayan ve yeterince normalleştirilmiş keskin durumlu kompakt kapalı bir cd-kategorisi olsun. O zaman $\Vout=\Vnin$ olan $\modelV$ değişkenleri üzerinde $\catC$'deki her nedensel $\modelM$ modeli için:
`[Şekil/dizge: M-vs-PM-via-traces]` (iz-koşulu)

*İspat.* $i, o$ sırasıyla $\Vinconc, \Vninconc$'un keskin durumları olsun. O zaman Lemma (sabit noktalar) gereği $\modelMio \circ i = o$ ancak ve ancak $\parmechdiag_\modelM \circ (i \otimes o) = (i \otimes o)$. $\parmechdiag_\modelM$, $\Vin$ üzerinde özdeşlik olduğundan bu, $\discard{\Vin} \circ \parmechdiag_\modelM \circ (i\otimes o) = o$ olmasına denktir. (kompakt-kapanış-2) sayesinde bu, aşağıdaki sol tarafın $1$'e eşit olmasına denktir; aşağıdaki eşitlik (keskin-etki-kopya)'dan gelir.
`[Şekil/dizge: fixedflip]`
Dolayısıyla yukarıdaki sağ taraf da denk olarak $1$'e eşittir. (kompakt-kapanış-2)'yi tekrar uygulayarak bu, (iz-koşulu)'nun sol tarafının $i$ ile bileştiğinde $o$ vermesine denktir. Bu keyfî $i$ durumları için geçerli olduğundan ve $\catC$'nin yeterince durumu bulunduğundan işimiz biter. ∎

Artık Bölüm (isoCCA)'daki bir \isoCCA için tutarlılık koşulunu (compose-exact-trans-explicit), Denklem (DDo-şekil)'deki alçak seviyeli dağıtık Do-müdahaleleri düşünerek şu daha doğrudan biçimde yazabiliriz:
`[Şekil/dizge: isoCCA-condition]`

\isointabs için tutarlılık koşulu da benzer biçimde yazılabilir.

**Not (üst-mertebe için iz hilesi).** Klasik nedensel modellerin, bir nedensel modelin verisinin yüksek mertebeden bir eşleme tanımladığı *bölünmüş-düğümlü nedensel modeller* (split-node) biçimcisinde denk bir temsili vardır (Barrett 2019; Lorenz 2023). Bu çalışmanın bir $\modelM$ modelinin paralel mekanizma süreci $\parmechdiag_\modelM$ dediği şey, muhasebedeki bazı farklılıklara kadar, bölünmüş-düğümlü bir modelin yüksek mertebeden eşlemesini temsil etmenin yaygın bir yoluyla esasen aynıdır. Yukarıdaki biçimde bir iz yapısı kullanarak $\parmechdiag_\modelM$ ile modelin girdi-çıktı süreci $\io{\modelM}$ arasında geçiş yapmak, Bölüm (nedensel soyutlama)'daki nedensel soyutlama kavramlarını bölünmüş-düğümlü modeller biçimcisinde yeniden ifade etmede esastır. Bölünmüş-düğümlü modeller ise klasik nedensel modellerin kuantum nedensel modellerin özel hâlleri olduğunu kesinleştirmenin de yolu olduğundan (Barrett 2019), "iz yapısı hilesi" kuantum nedensel soyutlama kavramlarını incelemek için de esastır (Bölüm kuantum soyutlama ve gelecek çalışmaya bkz.).

# Ek E. Kuantum–klasik indirgeme

Aşağıdaki örnek, $\QC$'deki bir $\modelML$ kuantum modelinden bir $\modelMH$ klasik modeline soyutlamayı gösterir; bu, kuantum modelin klasik olana bir "indirgenmesi" olarak görülebilir.

**Örnek (Kuantum karar modelleri).** (QCog) İnsan deneklerin klasik sonuçları $X_A, X_B$ olan $A$ ve $B$ kararlarını verdiği bir deney düşünelim; örneğin $X_A=X_B=\{\text{evet, hayır}\}$ cevap kümeli sorulara cevap vermek. Bu, "önce $A$ sonra $B$" için cevap dizileri üzerindeki $\orderedP{A,B}$ dağılımını ve "önce $B$ sonra $A$" için $\orderedP{B,A}$ dağılımını verir. Bir *karar modeli*, ilk durumu $\rho$ olan bir $S$ nesnesi ve her karar için $A, B$ kanallarını belirtir; öyle ki şu geçerli olunca dağılımlar yeniden elde edilir:⁷
`[Şekil/dizge: inst-model-general_b]`
"Önce $B$ sonra $A$" için de benzer denklemle birlikte. $\sem{S} = \hilbH$ olan $\QC$'deki *kuantum karar modelleri*, çeşitli psikolojik etkiler için açıklama olarak sunulmuştur (QCog).

⁷ *Bu yüzden bu, $\syn{S, A, B, \rho}$'dan oluşan $\SigS$ imzalı, $(S, A ,B ,\rho)$ olarak modellenen ve yukarıdaki gibi modellenen $\orderedP{A,B}, \orderedP{B,A}$ ile verilen $\sigQ$ sorgularına sahip bir bileşimsel modeldir.*

Böyle bir $\modelML$ modeli verildiğinde, sonlu $S$ kümesi, $\omega$ dağılımı ve $A,B$ kanallarıyla verilen klasik bir $\modelMH$ karar modeline soyutlama neyi gerektirir? $\HtoL =\id{\strucQ}$, $\LtoH_{X_A}=\id{}$ ve $\LtoH_{X_B} = \id{}$ olan bir \qdown $\modelML \to \modelMH$, iki modelin $\orderedP{A,B}$ ve $\orderedP{B,A}$ üzerinde çakıştığını, yani klasik bir $\modelMH$ modelinin gerçekten mevcut olduğunu söyler. Daha güçlü olarak, $\HtoLS = \id{\strucS}$ olan bir \strucdown şöyle bir $\LtoH \colon \hilbH \to S$ kanalı verirdi:
`[Şekil/dizge: qinst-abs-1]` `[Şekil/dizge: qinst-abs-2]`
ve $B$ için benzer. Son olarak, daha da güçlüsü $\LtoH \circ \LtoH^{-1} = \id{S}$ olan bir "hazırlama" kanalı $\LtoH^{-1} \colon S \to \hilbH$ de sunmak olurdu; böylece her kuantum $A$ kanalı bir "ölçüm" kanalı $\LtoH$, klasik $A$ kanalı ve yeniden hazırlama $\LtoH^{-1}$'e indirgenirdi. Örneğin $\LtoH, \LtoH^{-1}$'i bir ortonormal baz için ölçüm ve hazırlama kanalları almak $A$ ve $B$'yi bu bazda köşegen kılardı.

# Ek F. Soyutlamanın daha ileri biçimselleştirilmesi

## F.1 \qup'ın biçimselleştirilmesi
Şimdi (exact-partial) diyagramının hangi anlamda geçerli olduğunu, \qup'ları doğal dönüşümlerle ilişkilendirerek kesinleştirelim.

**Önerme (ex-trans).** Bir \qup $\qupcomponents{\HtoL}{\LtoH}{\queryLtoH}$, bir $\SigModel{\QLsubset}{M}$'nin ve iki \qdown'ın varlığına denktir:
`[Şekil/dizge: uabs]` ve (sorgu-hizalama) `[Şekil/dizge: Query-alignment-simpler-nodots_tilde]`
burada $\SigModel{\QLsubset}{M}$ iki \qdown'da da "yüksek seviyeli modeldir", $\HtoL$ sorgularda birebirdir ve $\widetilde{\queryLtoH}$ tiplerde özdeşlik, sorgularda örtendir. $\LtoHquery \colon \SigQL \pto \SigQH$ ile karşılık, $\QL = \HtoL(\QM)$ olan her $\QL$ için $\SigQH$'de $\queryLtoH(\QL) = \widetilde{\queryLtoH}(\QM)$ ile gerçekleşir.⁸

⁸ *\qdown'daki $\HtoL$ funktörünün, yalnız tipler üzerinde bir eşleme olan \qup'ın $\HtoL$'si ile anlaştığına dikkat edin.*

Yukarıda $\QLsubset$'teki her $\QM$ sorgusunun $\SigQH$'den $X$, $Y$ tipleri vardır, fakat $\SigQL$'de $\QL := \HtoL(\QM) \colon \HtoL(X) \to \HtoL(Y)$ sorgusuyla özdeşleştirilebilir; $\LtoHquery$'nin bunun üzerinde tanımlı olduğu ve $\SigQH$'deki görüntüsü $\queryLtoH(\QL) := \widetilde{\queryLtoH}(\QM)$ olan sorgu olarak düşünülür.

*İspat.* Yukarıdaki gibi \qdown'lar verilsin. $\SigQH$'deki tipler $\QLsubset$'tekilerle aynı olduğundan $(\HtoL, \LtoH)$'yi $\modelML$ ile $\modelMH$ arasında bir tip hizalaması olarak da görebiliriz. Şimdi $\widetilde{\queryLtoH}$'yi (sorgu-hizalama)'da özetlendiği gibi $\sigQL$'ye genişletiriz. $Q \in \SigQL$ için, $\LtoHquery(Q)$ tanımlıdır ancak ve ancak bir $Q' \in \QLsubset$ için $Q = \HtoL(Q')$ ise. Bu durumda $\LtoHquery(Q) := \widetilde{\queryLtoH}(Q')$ tanımlanır. $\widetilde{\queryLtoH}$, $\QLsubset$'ten örten olduğundan $\LtoHquery$ da $\SigQL$'den örtendir ve bir sorguyu $X \to Y$ tipli bir sorguya eşlediğinde o sorgunun $\HtoL(X) \to \HtoL(Y)$ tipli olduğu doğrulanabilir.

Tutarlılığın geçerli olduğunu denetlemek kalır. $Q \in \sigQL$ için $Q_H = \LtoHquery(Q)$ olsun. O zaman bir $Q' \in \QLsubset$ için $Q = \HtoL(Q')$ vardır. O zaman tutarlılık şu sebeple geçerlidir:
$$Q_H \circ \LtoH = \widetilde{\queryLtoH}(Q') \circ \LtoH = Q' \circ \LtoH = \LtoH \circ \HtoL(Q') = \LtoH \circ Q$$
İkinci eşitlikte $(\LtoH, \id{})$'in *katı* (strict) bir \qdown olduğunu kullandık. Üçüncü eşitlikte $(\HtoL, \LtoH)$'nin bir \qdown olduğunu kullandık.

Tersine, herhangi bir \qup verildiğinde, $\QLsubset$'i $\sigQH$ ile aynı tiplere sahip ve $\LtoHquery$'nin tanımlı olduğu her $Q \colon \HtoL(X) \to \HtoL(Y)$ sorgusu için bir $Q^* \colon X \to Y$ sorgusuna sahip olacak şekilde tanımlarız; ve $\sem{Q^*}_{M} := \semMH{\LtoHquery(Q)}$ ile bütün $X$ tipleri için $\sem{X}_{M} := \semMH{X}$ koyarız. $\HtoL(Q^*) := Q$ tanımlarız ve $\widetilde{\queryLtoH}$'yi $\widetilde{\queryLtoH}(Q^*) := \LtoHquery(Q)$ ve tiplerde özdeşlik olarak tanımlarız. O zaman tanım gereği $\HtoL$ tiplerde birebirdir ve $\widetilde{\queryLtoH}$ örtendir. $\sem{Q^*}_{M} := \semMH{\LtoHquery(Q)}$ olması, $(\widetilde{\queryLtoH}, \id{})$'in katı bir \qdown oluşturmasını sağlar. Son olarak $(\HtoL, \LtoH)$'nin bir \qdown oluşturması için tutarlılığı denetlemeliyiz; bu, daima $\sem{Q^*}_{M} \circ \LtoH = \semMH{\LtoHquery(Q)} \circ \LtoH = \LtoH \circ \HtoL(Q)$ olduğundan geçerlidir. ∎

## F.2 Soyutlamaların karakterizasyonu
Sınırlı CCA'ları ve \CF{} soyutlamaları daha kategorik biçimde şöyle karakterize edebiliriz.

**Lemma (zayıf-CA-karakterizasyon).** $\strucS$ yapı kategorili $\modelV$ üzerindeki herhangi bir nedensel model için, her sorguyu kendi diyagramına gönderen $\qabsMfunc \colon \WOpenqueries(V) \to \strucS$ funktörü, Do-sorguları için olan $\qabsMfunc \colon \Openqueries(V) \to \strucS$ üzerinden, $\qabsMfunc \colon \WOpenqueries(V) \to \Openqueries(V)$ funktörüyle çarpanlanır.⁹ O zaman bir sınırlı CCA, $\HtoL(\VinH) = \VinL$ olan ve aşağıdaki diyagramı değiştiren (tek) bir $\HtoL'$ sorgu eşlemesi bulunan bir \qdown'a denktir.
`[Şekil/dizge: II-diagram]` (II-diyagramı)

⁹ *$\WOpenqueries(V)$'nin her üretecinin serbest $\Openqueries(V)$ kategorisindeki bir diyagrama eşlenebildiğine dikkat edin; dolayısıyla böyle bir funktör vardır.*

*İspat.* (zayıfCA-sorgu-eşlemesi)'nin (II-diyagramı)'ndaki $\HtoL'$'nin varlığına denk olduğunu denetleriz. $\qabsMHfunc, \qabsMLfunc$ bütün değişkenleri koruduğundan her $V \in \VH$ için $\HtoL'(V) = \HtoL(V)$. Teorem (CCA-inceltme) ispatındaki gibi, girdileri koruyan her $\HtoL'$ sorgu eşlemesi, her $\openqueryshort{}{}{S}$'yi $\openqueryshort{}{}{\HtoL'(S)}$'ye göndermelidir; çünkü sonuncusu doğru girdi ve çıktılara sahip tek sorgudur ((sorgu-eşlemesi) ile tanımlı, $\HtoL$ yerine $\HtoL'$ konarak). Bu tek $\HtoL'$ eşlemesiyle, diyagramın değişmesinin ancak ve ancak (zayıfCA-sorgu-eşlemesi) geçerliyse olduğu görülebilir. ∎

**Lemma (CF-karakterizasyon).** $\FMCVen$, $U$ üzerindeki herhangi bir FCM $\modelM$ için, girdi sayılan tek bir $U$ tipiyle $\Openqueries(\FMCVen \cup \{U\})$'nun ayrık birleşimi ve bir $U$ durumu olan tek bir ek $\lambda$ sorgusuyla verilen soyut sorgular kümesi $\Openqueries(\FMCVen, U)_\lambda$ tanımlayalım. Her sorguyu diyagramına gönderen $\qabsMfunc \colon \absLthree(\FMCVen) \to \strucS$ funktörü, $\qabsMfunc$ ile gösterdiğimiz bir funktörle $\qabsMfunc \colon \Openqueries(\FMCVen, U)_\lambda \to \strucS$ üzerinden çarpanlanır. Bir \CF{} soyutlama, aşağıdakini değiştiren (tek) bir $\HtoL'$ sorgu eşlemesi bulunan ve $\HtoL'(U_H) = U_L$ olan bir \qdown $\qdownabs{\HtoL}{\LtoH}{\SigModel{\absLthree(\FMCVen_L)}{\modelML}}{\SigModel{\absLthree(\FMCVen_H)}{\modelMH}}$'dır:
`[Şekil/dizge: CFabs-diagram]` (CFabs)

*İspat.* Bunun \qdown'ın (CF-soyutlama-sorgu-eşlemesi) biçimini almasına denk olduğunu denetleriz. $X \in \FMCVen_H$ değişkenlerinde inşa gereği $\HtoL'(X) = \HtoL(X)$. Teorem (CCA-inceltme) ispatındaki gibi, tipleri korumak için girdileri koruyan her $\HtoL'$ sorgu eşlemesi her $\openqueryshort{}{}{S}$'yi $\openqueryshort{}{}{\HtoL(S)}$'ye göndermelidir ve inşa gereği $\lambda$'yı $\lambda$'ya göndermelidir. Böylece $\HtoL'$, $\HtoL$ ile tek olarak karakterize edilir. O zaman (CFabs)'ın değişmesinin ancak ve ancak (CF-soyutlama-sorgu-eşlemesi) geçerliyse olduğu görülebilir. Gerçekten, her $\Lthreequery{Y_1|_{\CFOpenSet_1},\dots,Y_m|_{\CFOpenSet_m}}$ sorgusuna karşılık gelen diyagramları yazıp $\HtoL'$ uygulamak, $\modelF$ için her açma kutusuna $\HtoL$ uygulamak demektir; bu da tam olarak $\Lthreequery{\HtoL(Y_1)|_{\HtoL(\CFOpenSet_1)},\dots,\HtoL(Y_m)|_{\HtoL(\CFOpenSet_m)}}$'ye karşılık gelen diyagramı verir. ∎

## F.3 $\Model(\catC)$ kategorisi
Kategorik bakışla, bu çalışmanın ana tanımlarını belirtmenin ve yakalamanın kısa bir yolu vardır; ancak sadelik sebebiyle önceki bölümlerde atlanmıştır. Şimdi bu yaklaşımı kısaca sunuyoruz. Bundan sonrası için, uygun türden bütün funktörler ve doğal dönüşümlerle bir d- veya cd-kategorisi $\catC$ sabitleyelim.

**Tanım.** $\Model(\catC)$, nesneleri $\catC$'de bir $\Gensig$ imzası ile $\Gensig$'nin bir $\modelM$ modelinden oluşan $\Gensig^{\modelM}$ çiftleri olan kategoridir. Bir $(F,\LtoH) \colon \Gensig^\modelM \to \Gensig'^{\modelM'}$ morfizmi ile $F \colon \Gensigcat \to \Gensigcat'$ funktörü ve aşağıdaki gibi bir epik doğal dönüşüm $\LtoH$'yi kastederiz.
`[Şekil/dizge: morphism-sigs]`
Bileşim $(G, \tau') \circ (F, \tau) = (G \circ F, \tau \circ \tau'_F)$ ile verilir; $\id{\SigC} = {\id{}, \id{}}$.

Kısaca, böyle bir morfizmi çoğunlukla $(F,\LtoH^F)$ yerine $F$ ile göstereriz. Bir $F$ morfizmine:
- $\tau=\id{}$ olduğunda *katı* deriz, böylece $\sem{-}' \circ F = \sem{-}$. Katı morfizmlerin bileşim altında kapalı olduğu kolayca görülür.
- $F$ üreteçleri üreteçlere gönderdiğinde *eşleme (map)*; ve $\Gensigcat'$'ün her üreteci bir $g$ üreteci için $F(g)$ biçiminde olduğunda *örten* deriz.

$\catC$'de $\SigS$ yapılı ve $\SigQ$ sorgulu herhangi bir bileşimsel $\modelM$ modeli, $\Model(\catC)$'de iki ayrı $\SigM$ ve $\QueryM$ nesnesine karşılık gelir. O zaman:
- Sorgular $\SigQ$, ancak ve ancak bir katı $\qabs{-} \colon \QueryM \to \SigM$ morfizmi varsa soyuttur.
- Bir \qdown $\modelML \to \modelMH$, tam olarak bir $\HtoL \colon \QueryMH\to \QueryML$ eşlemesidir.
- Bir \qdown, aşağıdaki diyagramı değiştiren bir $\HtoLS$ morfizmi varsa yapı-seviyeli iyi-huyludur (\strucdownprop):
`[Şekil/dizge: struc-level-simple]`
\strucdownprop \qdown durumu, $\HtoLS$ (ve dolayısıyla $\HtoL$) katı olduğunda katıdır.

**Örnek.** Değişkenlerde birebir olan bir katı $\IOSig(\varV) \to \Openqueries(\varV)$ eşlemesi vardır. Bir yapıcı nedensel soyutlama, aşağıdaki diyagramı değiştiren bir $\HtoL$ morfizminin tam kendisidir.
`[Şekil/dizge: io-factor_b]`

\qup'ları şöyle ele alabiliriz. *Dönüşüm*ü bir eşleme çifti olarak tanımlayalım:
`[Şekil/dizge: partial-map-sigs-2-flipped]` (tam-dönüşüm-tekrar)
öyle ki $\queryLtoH$ katı, örten ve değişkenlerde özdeşlik olsun. O zaman:
- Bir \qup, $\HtoL$'nin tiplerde ve üreteçlerde birebir olduğu özel durumdur.
- Bir \qdown, $\queryLtoH$'nin üreteçlerde bir eşleme (bijection) olduğu özel durumdur; böylece $\QLsubset^{M} = \QHC$ özdeşleştirebiliriz. Dolayısıyla bu basitçe bir $\HtoL \colon \QHC \to \QLC$ eşlemesidir.

Verilen sorgular ve modeller arasında, bu çalışmanın odaklandığından daha karmaşık ilişkilerle çalışırken, $\Model(\catC)$ kategorisinde çalışmak ve yukarıdaki terminolojiden yararlanmak özellikle yararlı olabilir. Bu kategorinin ve özelliklerinin tam keşfini ileriki işe bırakıyoruz.

**Soyutlamanın daha da genel, funktöryel bir görünümü.** Kategorik bakışla, belki de modelin ve modeller arası soyutlamanın en genel kavramı, (verilmiş imzaları olması gerekmeyen) kategoriler, funktörler ve bir doğal dönüşümden oluşan bir koleksiyondur:
`[Şekil/dizge: general-square]`
öyle ki $(\HtoL, \queryLtoH)$ çifti bir *bağıntı* oluşturur, yani $\langle \HtoL, \queryLtoH \rangle \colon \strucQ_M \to \strucQ_H \times \strucQ_L$ sadık (faithful) olur. Bu, soyutlamayı yüksek ve alçak seviyeli "sorguları" yapılı bir biçimde ilişkilendirmenin bir yolu olarak anlayabileceğimiz anlamına gelir. Yani bağıntıda bulunan $(Q_H, Q_L)$ morfizmleri ("sorguları") için kanonik tutarlılık denklemi (tutarlılık)'ı elde ederiz. Bu biçimde keyfî bağıntılara izin vermek, burada ele aldığımızdan daha genel (mutlaka kısmî fonksiyonla verilmeyen) yüksek ve alçak seviyeli sorguları yapılı biçimde ilişkilendirme yolları verirdi; ancak ileriki çalışmada keşfedilmesi ilginç olurdu.

*[Kaynak sonu: `\end{document}` satır 2588.]*
