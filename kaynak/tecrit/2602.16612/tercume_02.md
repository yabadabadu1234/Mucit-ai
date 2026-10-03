*(Bu parça kaynağın 630–929. satırlarını kapsar: Bölüm 4'ün devamı, Bölüm 5'in başı. Notasyon ve şekil geleneği `tercume_01.md` başındaki notla aynıdır.)*

Epik belirlenimci morfizmalar için $\FStoch$'ta otomatik olsa da genelde $\LtoH$'nın *örten* olduğunu, herhangi bir $X \in \varV_H$'nin her keskin durumunun $\HtoL(X)$'in bir $s$ keskin durumu için $\LtoH \circ s$ biçiminde olması halinde söyleriz.

Şimdi, bir tecritte her seviyedeki sorguların kendilerini de ilişkilendirmek isteriz ve bunu yapabileceğimiz iki ana yol vardır. Her iki durumda da her yüksek seviyeli $\QH \colon \syn{X} \to \syn{Y}$ sorgusunu, $\catC$'de *tutarlılığın* geçerli olacağı biçimde en az bir düşük seviyeli $\QL \colon \HtoL(\syn{X}) \to \HtoL(\syn{Y})$ sorgusuyla ilişkilendiririz:

$$[\text{Şekil/dizge: consistency-intext\_tau-convention}] \tag{15}$$

burada $Q_H = \semMH{\QH}$, $Q_L=\semML{\QL}$.

**Aşağı tecritler.** İlk ilişki, sorgular üzerinde *yüksekten düşük* seviyeye bir $\HtoL$ eşlemesi içerir ve basit bir kategorik tarifle gelir.

**Tanım (Sorgu-aşağı tecrit).** Bir *sorgu-aşağı tecrit* $\qdownabs{\HtoL}{\LtoH}{\SigModel{\sigQL}{\refdefML}}{\SigModel{\sigQH}{\refdefMH}}$, bir $\HtoL$ funktörü ve şu biçimde bir epik doğal dönüşüm $\LtoH$ ile verilir: [Şekil/dizge: qref] öyle ki $\SigQH$'in her $\syn{Q}$ sorgusu için $\HtoL(\syn{Q})$, $\sigQL$'in bir sorgusudur.¹⁷

¹⁷ Yani yalnızca $\strucQL$ kategorisinin değil, $\sigQL$ imzasının.

Tanımı açarsak, bir sorgu-aşağı tecritin tam olarak bir tür-aşağı hizalama ($\HtoL$ türler üzerindeki eşlemesi ve $\LtoH$ dönüşümüyle verilen) ve her yüksek seviyeli $\QH \colon \syn{X} \to \syn{Y}$ sorgusunu bir düşük seviyeli $\QL := \HtoL(\QH) \colon \HtoL(\syn{X}) \to \HtoL(\syn{Y})$ sorgusuna gönderen ek bir $\HtoL$ eşlemesi olduğunu görürüz. $\LtoH$'nın doğallığı, tutarlılığın (15) $\sigQH$'deki her $\QH$ sorgusu için, $\QL = \HtoL(\QH)$ ile, geçerli olması gereksinimine eşittir. Yani $\catC$'de şunu elde ederiz: [Şekil/dizge: query-refinement-equation-alt]

**Yukarı tecritler.** Birçok 'somut' sorgu için ise tipik olarak tek bir yüksek seviyeli sorguyla ilişkili birçok düşük seviyeli sorgu vardır (örn. belirli Do-müdahaleleri ve nedensel modellerin tam dönüşümleri kavramında olduğu gibi [rubenstein2017causal, BeckersEtAl_2019_AbstractingCausalModles]; Bölüm 5'e bakınız). Bunu yakalamak için ikinci tecrit kavramımızı, bunun yerine sorguların düşükten yüksek seviyeye kısmî bir $\LtoHquery$ eşlemesini kullanarak ele alırız. Sezgisel olarak $\LtoH$ o zaman aşağıdaki gibi bir doğal dönüşüm oluşturur: [Şekil/dizge: exact-nat-trans-2] (16)

Daha kesin olarak şunu tanımlarız.

**Tanım (Sorgu-yukarı tecrit).** Bir *sorgu-yukarı tecrit* $\qupabs{\HtoL}{\LtoH}{\queryLtoH}{\SigModel{\sigQL}{\modelML}}{\SigModel{\sigQH}{\modelMH}}$, bir tür-aşağı hizalama $(\HtoL,\LtoH)$ ve sorgular üzerinde şu biçimde kısmî örten bir $\queryLtoH \colon \SigQL \rightharpoonup \SigQH$ eşlemesiyle verilir: [Şekil/dizge: omega-queries] (17) öyle ki tutarlılık (15) $\QH = \queryLtoH(\QL)$ ile geçerlidir.

Dolayısıyla bir sorgu-yukarı tecritte, $\queryLtoH(\syn{Q}_L)$ tanımlı ve türü $\syn{X} \to \syn{Y}$ olduğunda $\syn{Q}_L$'nin türü $\HtoL(\syn{X}) \to \HtoL(\syn{Y})$'dir ve $\catC$'de şu geçerlidir: [Şekil/dizge: Q-tau-consistency] (18)

Yine bu bize sorgu-yukarı tecritlerin (16) resmindeki gibi bir tür doğal dönüşüm olduğunu söyler. Bunu Ek 'app:up-abs'ta Önerme 'ex-trans'ta, sorgu-yukarı tecritleri sorgu-aşağı tecritlerle ilişkilendirerek kesinleştiriyoruz.

Yararlı bir olgu, her iki tecrit kavramının da şu anlamda bileşimsel olmasıdır.

**Önerme.** Aşağı ve yukarı tecritlerin her biri terkip altında kapalıdır. Yani aşağıdakiler [Şekil/dizge: abstr-closed] sorgu-aşağı tecritlerse (sırasıyla sorgu-yukarı tecritlerse), şu da öyledir: [Şekil/dizge: abstr-closed-2]

Sonuç olarak tür hizalamaları da terkip altında kapalıdır.

*İspat.* Doğrulaması basittir.

**Aşağı tecritlerden yukarı tecritlere.** Önümüzdeki örneklerde tekrar tekrar göreceğimiz gibi bir sorgu-yukarı tecrit çoğunlukla bir sorgu-aşağı tecritin tutarlılık koşullarının belirli girdi durumlarına kısıtlanmasından doğar. Sonraki bölümde, aynı tür sorguların karşılık gelen soyut ve somut sürümleri aracılığıyla ilişkili, Şekil 1'de özetlenen bu tür birçok nedensel sorgu-aşağı ve sorgu-yukarı çifti örneğiyle karşılaşacağız.

Bunların aşağıdaki genel sonuçtan doğduğu görülebilir. Her $\syn{Q}$ sorgusunun seçilmiş bir girdi (kümesi) $\syn{Z_Q}$ ile geldiği bir sorgu modeli $\SigModel{\SigQ}{\modelM}$'i ele alalım. $\SigQ$ ile aynı türlere sahip ve her $\syn{Q} \in \SigQ$ ve $\syn{Z_Q}$'nun keskin bir $s$ durumu için bir $(\syn{Q},s)$ sorgusu olan bir $\SigQ^{\Sh}$ sorgular imzası tanımlarız; $\semM{(\syn{Q},s)}$ $\catC$'de şöyle verilir: [Şekil/dizge: Qssmall]

**Önerme (Exact-trans-from-ref).** $\qdownabs{\HtoL}{\LtoH}{\SigModel{\SigQL}{\modelML}}{\SigModel{\SigQH}{\modelMH}}$ bir sorgu-aşağı tecrit olsun; burada $\sigQH$ yukarıdaki biçimde ve $\LtoH$ örten olsun. Şu yolla bir sorgu-yukarı tecrit $\qupabsshort{\SigModel{\SigQL^\Sh}{\modelML}}{\SigModel{\SigQH^\Sh}{\modelMH}}$ elde ederiz: [Şekil/dizge: QS1a, QS1b, omega, QS2a, QS2b] $\syn{Z}_{\HtoL(\syn{Q})} := \HtoL(\syn{Z_Q})$ ile.

*İspat.* Örtenlik inşa gereğince geçerlidir ve tutarlılık sorgu-aşağı tecritin doğallığından, her $s$ durumuna uygulanarak, doğrudan çıkar: [Şekil/dizge: consistency-up-from-down-boxed-up] (19)

**Şekil 1.** Bölüm 5'teki birkaç nedensel tecrit biçiminin özeti; $\Ltwo$ ve $\Lthree$ nedensel hiyerarşinin ikinci (müdahaleli) ve üçüncü (karşı-olgusal) düzeyini gösterir (örn. bkz. [pearl2009causality, bareinboim2022pearl]).

| Düzey | Soyut | Somut | Tecrit türü |
| :-- | :-- | :-- | :-- |
| $\Ltwo$ | Do-sorgusu | Do-müdahalesi (somut Do-sorgusu) | yapıcı tecrit |
| $\Ltwo$ | değiş-tokuş sorgusu | değiş-tokuş müdahalesi (somut değiş-tokuş sorgusu) | kısıtlı yapıcı nedensel tecrit |
| $\Lthree$ | karşı-olgusal sorgu | somut karşı-olgusal sorgu | karşı-olgusal tecrit |

## 5. Nedensel tecrit

Bu bölümde yazındaki birçok nedensel tecrit kavramının tanımlarımızın, yani sorgu modelleri arasındaki doğal dönüşümlerin, özel durumları olarak nasıl biçimlendiğini göreceğiz. Boyunca $\catC$'de sırasıyla $\syn{V^{\text{in}}_{L/H}},\syn{V^{\text{out}}_{L/H}} \subseteq \syn{V_{L/H}}$ değişkenleri olan bir *nedensel* model çifti $\modelML$ ve $\modelMH$'yi ele alırız.

Her durumda önce tecriti yazına en yakın biçimde doğrudan tanımlayacak, sonra bunun Bölüm 3.1'den belirli bir nedensel sorgu seçimi için tanımlarımızın nasıl özel bir durumu olduğunu göreceğiz. Birkaç durumda, bir eşlemenin şu biçimi mevcut olacaktır.

**Tanım (Değişken hizalaması)** [BeckersEtAl_2019_AbstractingCausalModles, Def. 3.19], [geiger2023causal, Def 31]. $\catC$'deki somut değişkenler arasında bir *değişken hizalaması* $\dvaralign{\HtoL}{\LtoH}{\modelVL}{\modelVH}$ şunlarla verilir:
- $\HtoL(\VinH) = \VinL$ ve $\HtoL(\VoutH) \subseteq \VoutL$ sağlayan, $\VL$'nin ayrık alt kümeleri $(\HtoL(\syn{X}))_{\syn{X \in \VH}}$ kolleksiyonu;
- Her $\syn{X} \in \varV_H$ için $\catC$'de belirlenimci epik bir kanal: [Şekil/dizge: tau-X]

Dolayısıyla değişken hizalamaları tür-aşağı hizalamalara benzer; değişkenler tür olarak alınır ve şimdi $\HtoL(\syn{X})$'lerin ayrık alt kümeler oluşturması özelliği eklenir. Yine $\catC=\FStoch$'ta koşullar her eşlemenin örten bir $\LtoH \colon \HtoL(X) \to X$ fonksiyonu olduğu anlamına gelir.

**Not.** Herhangi somut değişkenler $\modelV$ için, $\varV$ türlü ve her $\syn{S} \subseteq \varV$ alt kümesi için $\qabs{\synQ_\syn{S}}_\modelV = \id{\syn{S}}$ olan bir $\synQ_\syn{S} \colon \syn{S} \to \syn{S}$ sorgusu olan soyut sorgular kümesini $\varV^*$ ile yazalım. O halde bir değişken hizalaması $\dvaralign{\HtoL}{\LtoH}{\modelVL}{\modelVH}$ aslında $\HtoL(\VinH) = \VinL$ ve $\HtoL(\VoutH) \subseteq \VoutL$ sağlayan bir sorgu-aşağı tecrit $\qdownabsshort{\SigModel{\varV^*_L}{\modelVL}}{\SigModel{\varV^*_H}{\modelVH}}$'dir; ispat için Ek 'app:proofs'a bakınız.

### 5.1 Tam dönüşümler

Belki de yazındaki, somut müdahaleleri düşükten yüksek seviyeye ilişkilendiren, ilk ve en zayıf tecrit kavramı, modellerin 'tam dönüşümü' diye anılır. [rubenstein2017causal, Def 3], [BeckersEtAl_2019_AbstractingCausalModles, Def 3.1] ve [geiger2023causal, Def 25]'i kurulumumuza şöyle uyarlıyoruz (kesin karşılaştırma için sonraki Not 'ET-notions'a bakınız).

**Tanım (Tam Dönüşüm).** Müdahale kümeleri $\IntsetL$, $\IntsetH$ olan nedensel modeller $\modelML, \modelMH$ verildiğinde, bir *tam dönüşüm* $\modelML \to \modelMH$, $\catC$'de (girdileriyle ayırt ettiğimiz) epik belirlenimci kanallar çifti $\LtoH \colon \VinLconc \to \VinHconc$ ve $\LtoH \colon \VoutLconc \to \VoutHconc$ ve kısmî örten bir $\LtoHquery \colon \IntsetL \to \IntsetH$ fonksiyonuyla verilir; öyle ki $\LtoHquery$, bir $\inti \in \IntsetL$ üzerinde tanımlı olduğunda şu geçerlidir: [Şekil/dizge: int-exact-trans-2-nodots] (20)

Verili bir $\IntsetL$ müdahale kümesi için $\IntsetioL$ sorgu imzasının her $\inti \in \IntsetL$ müdahalesi için bir $\inti : \syn{in_L} \rightarrow \syn{out_L}$ sorgusu içerdiğini, $\IntsetioH$ için de benzer olduğunu hatırlayın.

**Önerme.** Müdahale kümeleri $\IntsetL$, $\IntsetH$ ile $\modelML$'den $\modelMH$'ye bir $(\tau, \omega)$ tam dönüşümü, bir sorgu-yukarı tecrit $\qupabs{\HtoL}{\LtoH}{\queryLtoH}{\SigModel{\IntsetioL}{\modelML}}{\SigModel{\IntsetioH}{\modelMH}}$'ye eşdeğerdir.

*İspat.* Tanımlardan hemen çıkar; böyle herhangi bir sorgu-yukarı tecritin $\LtoHquery$'nin sorguları sorgulara eşlemesi için, türler üzerindeki $\HtoL$ eşlemesinin $\HtoL(\syn{in_H}) := \syn{in_L}$ ve $\HtoL(\syn{out_H}) := \syn{out_L}$ ile verilmesi gerektiğine dikkat edilerek.

Bu kavramın bir değişken hizalaması varsaymadığına dikkat edin. Bir değişken hizalaması istemenin hemen altında kalan, sade ve genel bir nedensel tecrit kavramı olarak düşünülebilecek daha güçlü bir sürüm şudur. Herhangi bir nedensel $\modelM$ için *aşikâr müdahale* ile hiçbir mekanizmayı değiştirmeyen $\noint$ müdahalesini kastederiz; böylece $\modelMio_\noint = \modelMio$.

**Tanım (Güçlü nedensel tecrit).** Müdahale kümeleri $\IntsetL$, $\IntsetH$ olan nedensel modeller $\modelML, \modelMH$ verildiğinde, $\modelML$'den $\modelMH$'ye bir $(\LtoH, \LtoHquery)$ tam dönüşümüne şunlar sağlanırsa *güçlü nedensel tecrit* denir:
1. $\VninH \subseteq \VoutH$, yani bütün girdi-olmayan değişkenler çıktıdır;
2. $\IntsetH=\Do(\modelV_H)$, yani yüksek seviyede *bütün* somut Do-müdahalelerini içerir;
3. $\IntsetL$ ve $\IntsetH$ aşikâr müdahaleleri içerir, $\LtoHquery(\nointL)=\nointH$ ile.

Tam dönüşümlerin ve güçlü nedensel tecritlerin örnekleri sonraki bölümlerde gelecektir; güdüler ve yazınla ilişki üzerine yorumlar Not 'strong-CA'ya ertelenmiştir.

### 5.2 Yapıcı tecrit

Şimdi nedensel tecritin merkezî, belki de *örnek* teşkil eden bir kavramına ulaşıyoruz; bu [BeckersEtAl_2019_AbstractingCausalModles]'te verilen en güçlü tecrit kavramını oluşturur ve YZ modelleri ve mikro değişkenlerin alt kümelerini makro değişkenlerle ilişkilendiren diğer senaryolar için özellikle yararlıdır.

**Tanım (Yapıcı Tecrit)** [BeckersEtAl_2019_AbstractingCausalModles, Def 3.19]. $\modelML, \modelMH$, $\catC$'de sırasıyla somut değişkenleri $\modelVL, \modelVH$ olan ve $\VninH \subseteq \VoutH$ olan nedensel modeller olsun. Bir *yapıcı tecrit* $\modelML \to \modelMH$, her $\syn{S} \subseteq \VintH$ için $\catC$'de şunun geçerli olduğu bir değişken hizalaması $\dvaralign{\HtoL}{\LtoH}{\modelVL}{\modelVH}$ ile verilir: [Şekil/dizge: causal-abstr-open-simple] (21)

Bir yapıcı tecrit böylece $\modelH$ üzerindeki (soyut) Do-müdahalelerini $\modelL$ üzerindekilerle yapısal olarak ilişkilendirir. Şimdi bunu kategorik olarak şöyle karakterize edebiliriz.

**Teorem 1.** $(\HtoL,\LtoH)$ değişken hizalamalı bir yapıcı tecrit $\modelML \to \modelMH$, $\HtoL(\VinH) = \VinL$ olacak biçimde bir sorgu-aşağı tecrit $\qdownabs{\HtoL}{\LtoH}{\SigModel{\Openqueries(\varL)}{\modelML}}{\SigModel{\Openqueries(\varH)}{\modelMH}}$'ye eşdeğerdir.

*İspat.* Ek 'app:proofs'ta.

Burada yapıcı tecriti, soyut Do-sorguları cinsinden tümüyle yapısal bir kavram olarak ortaya çıkardık; olağan sunum ise somut değerli Do-müdahaleleri cinsindendir. İkincisiyle bağ, girdi durumlarıyla terkip yoluyla basittir. Aşağıdaki, yapıcı tecriti aynı zamanda düşük seviyeli Do-müdahalelerini $\Do(S_L=s_L)$ yüksek seviyeli olanlara $\Do(S_H=s_H)$ örten biçimde eşlemesi gereken Do-müdahaleleri arasında bir sorgu-yukarı tecrit olarak görebileceğimizi söyler.

**Sonuç 1.** Örten $\LtoH$ ile herhangi bir yapıcı tecrit $\modelML \to \modelMH$, şu yolla $\qupabs{\HtoL}{\LtoH}{\LtoHquery}{\SigModel{\Do(\modelV_L)}{\modelML}}{\SigModel{\Do(\modelV_H)}{\modelMH}}$ biçiminde bir sorgu-yukarı tecrit tanımlar: $\LtoHquery(\Do(\HtoL(S)=s))) := \Do(S=\LtoH \circ s)$.

Sonuç olarak aynı zamanda Do-müdahalelerinin bir tam dönüşümünü, yani her $\Do(\modelV)^{\mathsf{io}}$'nun yalnızca iki tür taşıyan bir $\Intsetio$ imzası olarak anlaşıldığı ${\qupabs{\HtoL}{\LtoH}{\LtoHquery}{\SigModel{\Do(\modelV_L)^{\mathsf{io}}}{\modelML}}{\SigModel{\Do(\modelV_H)^{\mathsf{io}}}{\modelMH}}}$ biçiminde bir sorgu-yukarı tecriti de tanımlar. Aslında bir güçlü nedensel tecrit (Tanım 'strong-CA') tanımlar.

*İspat.* Böyle bir sorgu-yukarı tecritin tutarlılık koşulu tam olarak şudur: [Şekil/dizge: constr-CA-explicit-2] (22) Alternatif olarak bu, $\SigQH=\Openqueries(\VH)$ ve $\SigQL=\Openqueries(\VL)$ ile Önerme 'Exact-trans-from-ref'in özel bir durumudur; burada $\syn{Q}=\Do{(\syn{S})}$ için $\syn{Z_Q} = \syn{S}$ alırız. Sonra Denk. (22)'yi Denk. (19)'un bir örneği olarak tanıyabiliriz. Sorgu türlerinin yalnızca $\syn{in,out}$ olduğu ifade hemen çıkar.

**Örnek (CCA).** Yapıcı bir tecritin şu basit örneği [BeckersEtAl_2019_AbstractingCausalModles]'tendir.¹⁸ Aşağıda sırasıyla solda ve sağda gösterilen, $\FStoch$'ta açık belirlenimci nedensel modeller $\modelL$ ve $\modelH$'yi ele alalım. [Şekil/dizge: CCA-example-L_b, CCA-example-H] (23)

¹⁸ Aslında [rubenstein2017causal]'dandır, ancak orada tam dönüşümleri örnekleyen kısıtlı müdahale kümeleriyle tartışılmıştır.

Burada $X_1,..., X_{99}$, bir dilekçe üzerinde 99 bireyin oylarını temsil eden (`1' 'evet'e karşılık gelir) $\{0,1\}$ değerli ikili değişkenlerdir, $T$ dilekçeyi destekleyenlerin toplam sayısıdır (yani $f_T = \sum_i X_i$) ve $A_1$, $A_2$ dilekçe kampanyasının yürütmeyi seçebileceği iki olası reklamı temsil eden bazı ayrık değişkenlerdir; $\{f_{X_i}\}_{i=1}^{99}$, $f_{A_1}$ ve $f_{A_2}$ ilgili türlerdeki bazı fonksiyonlardır ve $U_{1},..., U_{101}$ (dışsal) girdi sayılan arka plan değişkenleridir. Yüksek seviyeli model, seçmenlerin üç ayrı gruba $G_1,G_2$ ve $G_3$ bölünmesinden doğar. $G_1$, $U_1' = \prod_{i=1}^{33} U_i$ ile $[1,33]$'te değerlidir ve $f_{G_1}(a_1,a_2,u_1') = \sum_{i=1}^{33} f_{X_i}(a_1,a_2,(u_1')_i)$; benzer şekilde $G_2, U_2',f_{G_2}$ ve $G_3, U_3', f_{G_3}$ için; son olarak $T'$ ikilidir ve dilekçenin kabul edilip edilmediğini temsil eder; $f_{T'}(g_1,g_2,g_3)$, $g_1+g_2+g_3 > 49$ ise bir, değilse sıfır verir.
