*(Bu parça kaynağın 1260–1599. satırlarını kapsar. Notasyon ve şekil geleneği `tercume_01.md` başındaki notla aynıdır. "`\isoCCA`/`\isointabs`" makroları: iso-yapıcı / iso-değiş-tokuş tecrit; "`\strucdown`": yapı-aşağı tecrit.)*

Açıkça, her $\inti \in \SigI$ için şu geçerlidir: [Şekil/dizge: induced-ex-trans] (41) Özellikle $\modinnin \circ \modelMio = \io{\inmod{\modelM}} \circ \modinin$.

*İspat.* Ek 'app:proofs'ta.

#### 5.5.2 İndüksiyon ve tecriti terkip etmek

Sorgu-yukarı tecritler terkip altında kapalı olduğundan, yukarıda tartışılan model indüksiyonu kavramı doğal bir inşa verir: $\modelV_L$ üzerinde bir $\modelML$ modelini ve bir belirlenimci izomorfizmayı düşünelim; bu 'ara' bir model indükler ve bu da bir üst seviyeli $\modelMH$ modeliyle tecrit edilir. Ortaya çıkan bileşke, $\modelML$ ile $\modelMH$ arasında 'dağıtık' bir tecrit bağıntısı verebilir. Daha ayrıntılı olarak şunlara sahip olalım:
- $\modelVone$ üzerinde 'düşük seviyeli' bir model $\Mone=\modelfrom{\parmechdiag_{\Mone}}$;
- $\Mone$'a saygı gösteren belirlenimci bir izomorfizma $\modin \colon \Vone \to \Vtwo$;
- $\Mtwo := \inmod{\Mone}$ üzerinde $\modin^{-1}$ tarafından saygı gösterilen bir $\Intwo$ müdahaleler kümesi;
- $\modelVthree$ üzerinde bir $\Mthree$ modeline bir sorgu-yukarı tecrit $\qupabs{}{\LtoH}{\LtoHquery}{\SigModel{\IntQsimple{\Intwo}}{\Mtwo}}{\SigModel{\IntQsimple{\Inthree}}{\Mthree}}$.

O halde $\Mone$ üzerinde $\Inone := \inducedintmap^{-1}(\Intwo)$ tanımlandığında bir sorgu-yukarı tecritler dizisine sahibiz: [Şekil/dizge: exact-trans-pair-new] (42) bu, $\Mone$'dan $\Mthree$'e genel bir sorgu-yukarı tecrit $(\LtoH \circ \modin, \LtoHquery \circ \inducedintmap)$ verecek biçimde terkip eder. Açıkça, $\LtoHquery$'nin tanımlı olduğu her $\inti\in \Intwo$ müdahalesi için şu geçerlidir: [Şekil/dizge: composing-exact-trans_b] (43)

Bu inşa, sorgu-yukarı tecrit $(\LtoH, \LtoHquery)$ bir yapıcı veya değiş-tokuş tecritinden doğduğunda özellikle ilgi çekicidir. Bu, [geiger2024finding, geiger2023causal] çalışmalarında örtük olarak ele alınan ve sonra tartışacağımız genel bir kavram verir.²⁷

²⁷ Onlar değiş-tokuş müdahalelerinin 'dağıtık bir sürümünü' getirmişlerdi; ancak biçiminin türetilmesi ve ilişkili bir tecrit kavramının tanımı yoktu.

**Tanım (İso-yapıcı/değiş-tokuş tecrit).** *İso-yapıcı* (sırasıyla *iso-değiş-tokuş*) *tecrit* ile (42)'deki gibi, $(\LtoHquery,\LtoH)$'nın bir yapıcı (sırasıyla değiş-tokuş) tecritten indüklendiği kurulumu kastederiz.

**İso-yapıcı tecrit.** İso-yapıcı tecritin ayrıntıda neye eşit olduğunu açmaya değer. $(\HtoL, \LtoH)$, $(\LtoHquery,\LtoH)$'yi indükleyen yapıcı nedensel tecritin verisi, $S \subseteq \Vthree$ ve $p$, $\HtoL(S)$'in keskin bir durumu olsun. Bileşke sorgu-yukarı tecrit o halde $\Mthree$ üzerindeki $\Do(S = \LtoH \circ p)$ müdahalelerini, $\Mtwo$ üzerindeki karşılık gelen $\Do(\HtoL(S)=p)$ müdahaleleri aracılığıyla, $\Mone$ üzerinde $\inducedintmap^{-1}(\Do(\HtoL(S)=p))$ biçimindeki müdahalelerle ilişkilendirir; bunlara *dağıtık Do-müdahaleleri* deriz ve genel olarak herhangi bir $\Stwo \subseteq \Vtwo$ için tanımlanırlar:

$$\DDo(\Stwo=\stwo,\rho) := \inducedintmap^{-1}(\Do(\Stwo=\stwo))$$

Dolayısıyla $S'=\HtoL(S)$ ile $\Mone$ üzerindeki dağıtık Do-müdahalelerine ilgi duyarız. Bu müdahale edilmiş düşük seviyeli modeller için paralel mekanizma kanallarının şöyle olduğu hesaplanabilir (Ek 'app:proofs'ta kanıtlanmıştır). [Şekil/dizge: DI-relabel2_b] (44)

İso-yapıcı tecritler, genel olarak gerçek 'dağıtıklığa' sahip, iyi karakterize edilmiş bir tam dönüşümler sınıfı verir.²⁸ Aslında inşa gereği güçlü türdendir.

²⁸ Bu aynı zamanda yalnızca do-müdahalelerinin ötesine geçen tam dönüşümün genel kavramını (Tanım 'exact-trans') da güdüler.

**Önerme (isoCCA-is-strongCA).** Bir iso-yapıcı tecrit için $\Mone$'dan $\Mthree$'e genel sorgu-yukarı tecrit $(\LtoH \circ \modin, \LtoHquery \circ \inducedintmap)$ bir güçlü nedensel tecrittir (Tanım 'strong-CA'ya bakınız).

**İso-değiş-tokuş tecrit.** Benzer şekilde iso-değiş-tokuş tecrit için $\dvaralignpair{\HtoL}{\LtoH}$, $(\LtoH, \LtoHquery)$'yi indükleyen kısıtlı yapıcı nedensel tecritin değişken hizalaması, $S_1,\dots,S_n$ $\Vthree$'ün ayrık alt kümeleri ve $\{x_1,\dots,x_n\}$ $\Vone^{\text{in}}$'in girdi durumları olsun. Bileşke sorgu-yukarı tecrit o halde $\Mthree$ üzerindeki $\II((S_j,\LtoH \circ \modinin \circ x_j))^n_{j=1}$ değiş-tokuş müdahalelerini, $\Mtwo$ üzerindeki $\II((\HtoL(S_j), \modinin \circ x_j))^n_{j=1}$ değiş-tokuş müdahaleleri aracılığıyla, $\Mone$ üzerinde $\inducedintmap^{-1}(\II((\HtoL(S_j), \modinin \circ x_j))^n_{j=1})$ biçimindeki müdahalelerle ilişkilendirir; bunlara *dağıtık değiş-tokuş müdahaleleri* deriz ve genel olarak $\Vtwo$'nun herhangi ayrık $Y_1,\dots,Y_n$ alt kümeleri için tanımlıdır:

$$\DII((Y_j,x_j)^n_{j=1},\modin) := \inducedintmap^{-1}(\II(Y_j,\modinin \circ x_j)^n_{j=1})$$

Dolayısıyla $Y_j = \HtoL(S_j)$ ile $\modelL$ üzerindeki dağıtık değiş-tokuş müdahalelerine ilgi duyarız. $S:=\cup_j S_j$ koyarak yine bu müdahale edilmiş düşük seviyeli modeller için paralel mekanizma kanallarını şöyle hesaplayabiliriz: [Şekil/dizge: DII-relabel_b] (45) bunu Ek 'app:proofs'ta kanıtlıyoruz.

**İso-tecritler için tutarlılık.** Son olarak, yukarıda düşük seviyeli 'dağıtık' müdahalelerin verdiği modelleri paralel mekanizma kanalları cinsinden gösterdiğimizi, ama genel sorgu-yukarı tecrit için tutarlılık koşulunu açıkça yazmadığımızı gözleyin. İkincisi modellere $\Vin$'den $\Vout$'a girdi-çıktı süreçleri olarak atıfta bulunurken, birincisi yalnızca $\parmechdiag_\modelM$ kanalları cinsinden açık hale getirilebilir. İkisi arasındaki ilişki Lemma 'fixpoints'teki gibi $\parmechdiag_\modelM$ kanallarının sabit noktaları üzerinde bir niceleme içerir.

Aslında iki görünüm arasındaki ilişkiyi, sabit noktalara açık atıf olmaksızın, örn. iso-yapıcı tecritlerin diyagramatik bir tutarlılık koşuluna izin veren 'yapısal' kılmanın bir yolu vardır. Ancak biraz daha biçimcilik gerektirdiğinden bunu Ek 'app:abs-in-pm-via-tracedC'de sunuyoruz.

Her halükârda iso-yapıcı bir tecrit için aday verisi verildiğinde şöyle belirleyebiliriz: Her yüksek seviyeli $\LtoHquery(\inti) = \Do(S = \LtoH \circ p)$ müdahalesi için önce $\io{\Mthree_{\LtoHquery(\inti)}}$'yi ve (43)'ün sağ tarafındaki bileşkeyi ele alırız. Öbür yandan $\inducedintmap^{-1}(\inti) = \inducedintmap^{-1}(\Do(\HtoL(S)=p))$ ile indüklenmiş modeli $\transform{\inducedintmap^{-1}(\inti)}{\Mone}$'i kanal (44) aracılığıyla hesaplayabilir, $\io{\transform{\inducedintmap^{-1}(\inti)}{\Mone}}$'yi ve (43)'ün sol tarafındaki bileşkeyi yeniden kurabilir ve çeşitli girdilerde sağ tarafla karşılaştırabiliriz. Benzer bir usul iso-değiş-tokuş tecrit için de işler.

## 6. Yapı-aşağı tecritler

Şimdiye dek tecrit bağıntılarını sorgular düzeyinde ele aldık. Ancak kategorik bakış, bileşimsel modellerin *yapı* düzeyine, yani tek tek bileşenleri cinsinden, uygulanan daha güçlü tecrit kavramlarını incelemeyi de önerir. Bu bölüm boyunca bütün bileşimsel modellerin $\catC$'de modeller olduğunu ve bütün sorguların soyut olduğu (Tanım 'abstract-query') $(\modelM,\SigS, \SigQ, \catC)$ verili *yapı ve sorgu* imzalarıyla geldiğini ele alırız.

**Tanım (Yapı-aşağı tecrit).** Bir *yapı-aşağı tecrit* $\strucdownabslarge{\HtoL}{\HtoLS}{\LtoH}{(\modelML,\SigS_L,\sigQ_L)}{(\modelMH,\SigS_H,\sigQ_H)}$, $\HtoL, \HtoLS$ funktörleri ve aşağıdaki gibi epik bir $\LtoH$ doğal dönüşümüyle, $\HtoL$ $\sigQ_H$'deki sorguları $\sigQ_L$'deki sorgulara eşleyecek ve üst kare değişecek biçimde verilir: [Şekil/dizge: mech-ref-swap_b] (46) Bir yapı-aşağı tecrit, $\LtoH=\id{}$ olduğunda *katı*dır.

Terminolojinin önerdiği gibi, böyle her veri gerçekten sorgu düzeyindeki bir tecritin de özel bir durumudur; şu basit sonuçla.

**Önerme (c-level-is-d-abs).** Herhangi bir yapı-aşağı tecrit (46), $\LtoH' := {\LtoHS} \circ 1_{\qabsMHfunc}$ ile bir sorgu-aşağı tecrit $\qdownabs{\HtoL}{\LtoH'}{\SigModel{\sigQL}{\modelML}}{\SigModel{\sigQH}{\modelMH}}$ indükler.

*İspat.* Ek 'app:proofs'ta.

Açıkça o halde bir yapı-aşağı tecrit, her yüksek seviyeli $\syn{X}$ değişkenine $\SigSL$'den bir düşük seviyeli değişkenler listesi $\HtoLS(\syn{X})$ ve $\catC$'de (belirlenimci) bir $\LtoHS \colon \HtoLS(X) \to X$ kanalı atar; bu, her zamanki gibi yüksek-değişken listelerine çarpımlarla genişler (13), (14). Sonra her yüksek seviyeli $\syn{f}$ bileşenini, düşük seviyeli yapı kategorisi $\strucSL$'de bir düşük seviyeli $\HtoLS(\syn{f})$ diyagramına gönderir; öyle ki $\catC$'de şu geçerlidir: [Şekil/dizge: mechanism-refinement-equation] O halde $\HtoLS$ otomatik olarak bir funktöre, $\LtoH$ bir doğal dönüşüme genişler; başka deyişle yukarıdakiler $\strucSH$'daki keyfî $\syn{f}$ diyagramları, yani bileşenlerin bileşkeleri için geçerlidir.

Ayrıca her zamanki gibi türler ve sorgular üzerinde yüksekten düşük seviyeye $\syn{Q} \colon \syn{X} \to \syn{Y}$'yi $\HtoL(\syn{Q}) \colon \HtoL(\syn{X}) \to \HtoL(\syn{Y})$'ye gönderen bir $\HtoL$ eşlememiz vardır. Son olarak bileşen eşlemesi bu (soyut) sorguların diyagramlarına saygı gösterir; öyle ki her böyle $\syn{Q}$ için düşük seviyeli yapı kategorisi $\strucSL$'de şu eşitlik geçerlidir: [Şekil/dizge: implementation-3] Özetle yüksek seviyeli sorguları $\catC$'de tutarlı temsilli düşük seviyeli sorgulara eşlemenin yanı sıra bir yapı-aşağı tecrit artık yüksek seviyeli biçimsel diyagramlardan düşük seviyeli biçimsel diyagramlara tutarlı bir eşleme de taşır. Dahası yüksek seviyeli bir sorgunun diyagramına uygulandığında, karşılık gelen düşük seviyeli sorgu için özdeş bir düşük seviyeli diyagram elde ederiz.

### 6.1 Katı yapı-aşağı tecritler

Önemli bir özel durum, doğal dönüşümlerin aşikâr olduğu, $\LtoH=\id{}$ olan katı yapı-aşağı tecritlerdir. En son tanımlamış olsak da bunlar belki de bir yüksek seviyeli modeli düşük seviyeli bir modelle ilişkilendirmenin en basit yoludur. Burada her yüksek seviyeli bileşeni (sorgularla ilişkili diyagramlara saygı gösterirken) doğrudan düşük seviyeli bileşenlerin bir diyagramı olarak basitçe 'kutudan çıkarır', 'inceltir' veya 'gerçekleriz'. [Şekil/dizge: unboxing-generic_b]

**Örnekler.**
1. $\catC$'de bir $c$ kanalının bir açık nedensel *modeli* $\modelM$ ile, $\modelMio = c$ olanı kastederiz. [Şekil/dizge: modelof_b] Eşdeğer olarak girdi ve çıktıları koruyan katı bir yapı-aşağı tecrit $\strucdownabsshort{\modelM}{\syn{c}}$ vardır. Burada her iki modelin de sırasıyla $\modelMio$'ya ve $c$'ye gönderilen tek bir $\syn{io} \colon \syn{in} \to \syn{out}$ sorgusu olduğunu ve $\syn{c}$'nin değişkenlerinin $\syn{X_i}, \syn{Y_j}$ ve soyut olarak $\syn{io}$'yu temsil eden tek bir $\syn{c}$ bileşeni olduğunu ele alırız.²⁹ Örneğin bir $\omega$ dağılımını $\FStoch$'ta bir durum olarak ele alalım. $\omega$'nın $\catC$'deki bir nedensel modeli o halde ağ diyagramı bileşkesi $\omega$'yı veren, yani olağan 'bir dağılım için nedensel model' kavramıdır. Daha somut olarak aşağıdaki gibi bir $\omega$ dağılımını düşünelim; burada $S$ birinin sigara içip içmediğini, $L$ akciğer kanseri geliştirip geliştirmediğini ve $A$ yaşını temsil eder. Aşağıda sol taraftaki, sosyo-ekonomik geçmiş koşulları için ek bir saklı $B$ değişkenli nedensel model, şu eşitlik geçerli olduğunda $\omega$'nın bir nedensel modeli olurdu (bkz. [CorreaEtAl_2020_CalculusForStochasticInterventions, lorenz2023causal]). [Şekil/dizge: causal-model-of_b]

²⁹ Dolayısıyla $c$ ancak $\modelM$ ve $c$'nin yalnızca bir çıktısı varsa kendisi bir nedensel modeldir.

2. Katı yapı-aşağı tecritler, bir FCM'yi bir nedensel modeli 'inceltme' olarak görebilmemizin yolunu da yakalayabilir. Çoğunlukla içsel ve dışsal değişkenleri sırasıyla $\FMCVen = \{X_i\}^n_{i=1}$ ve $U = \{U_i\}^n_{i=1}$ olan bir FCM $\modelF$ (Tanım 'FCM'), $\FMCVen$ değişkenleri üzerinde bir (fonksiyonel olmayan) nedensel modelin $\modelM$ altında yatan (aday) belirlenimci $f_i$ mekanizmalarını temsil ediyor sayılır; burada bütün rastgelelik $U$ değişkenleri hakkındaki bilgisizliğimizden gelir ve ilgili 'gürültü' dağılımları $\lambda_i$'de yakalanır. Gerçekten herhangi bir FCM $\modelF$ verildiğinde, her $X_i \in \FMCVen$'e şu şekilde tanımlı $c_i$ mekanizmasını atayarak yalnızca $\FMCVen$ üzerinde bir nedensel model $\modelF|_{\FMCVen}$ tanımlayabiliriz: [Şekil/dizge: de-SCM_b] (47) burada $\Pa'(X_i)=\Pa(X_i) \setminus \{U_i\}$ ve $\Pa(X_i)$ $\modelF$'ye göre ebeveyn kümeleridir. Tersine $\FMCVen$ üzerinde (fonksiyonel olmayan) bir nedensel model $\modelM$ verildiğinde, onu $\modelF|_{\FMCVen} = \modelM$ olacak biçimde bir FCM $\modelF$'ye inceltmenin genelde birçok yolu vardır. O zaman katı bir yapı-aşağı tecrit $\strucdownabsshort{(\modelF,\SigS_{\modelF},\Openqueries(\syn{\FMCVen}))}{(\modelM,\SigS_{\modelM},\Openqueries(\syn{\FMCVen}))}$ elde ederiz; burada her iki modelde $\syn{X_i}$ ve $X_i$'yi özdeşleştirir ve her $\syn{c_i}$'yi (47)'nin $\catC$'de geçerli olacağı biçimde $\syn{f_i}$ ve $\syn{\lambda_i}$'nin bileşkesine sözdizimi olarak eşleriz. Böyle bir ilişkiyi aşağıdaki gibi, aynı adlı değişkenleri ve karşılık gelen kesikli kutuları özdeşleştirerek gösterebiliriz. [Şekil/dizge: FCMrefinement_c]

### 6.2 Güçlü yapıcı nedensel tecrit

Prensipte Bölüm 5'teki nedensel sorgu-aşağı tecritlerden herhangi birinin bileşen düzeyine daha güçlü biçimde ne zaman genişlediği sorulabilir. Bu bölümde bunu yapıcı tecritler için yapacak ve bir yapı-aşağı tecrite genişleyen yapıcı nedensel tecrite *güçlü yapıcı nedensel tecrit* diyeceğiz. Bu, yazında şimdiye dek ele alınmamış yeni, daha güçlü bir nedensel tecrit kavramı verir.³⁰

³⁰ Bu aynı zamanda, $\LtoH=\id{}$ olan bir örnek olan Örnek 'strict-a-abs'ı (FCM-refine) da genelleştirir.

Açıkça, bir yapıcı tecriti bir sorgu-aşağı tecrit $\qdownabs{\HtoL}{\LtoH}{\SigModel{\Openqueries(\VL)}{\modelML}}{\SigModel{\Openqueries(\VH)}{\modelMH}}$ olarak ele alalım (Teorem 1). Bir güçlü yapıcı nedensel tecrit oluşturmak, her yüksek seviyeli mekanizmayı bir düşük seviyeli diyagrama gönderen ek bir $\HtoLS$ eşlemesinin olduğu anlamına gelirdi: [Şekil/dizge: strong-CA-1_b-nodots] (48) öyle ki $\catC$'de (her zamanki gibi $\semcompM{\modelML / \modelMH}{-}$'yi atmak için yazı tipi geleneğimizi kullanarak) şunun geçerli olması gerekir: [Şekil/dizge: strong-CA-2_c-nodots] (49) Sonra $\HtoLS$'yi, bütün $X \in \VH$ için $\HtoLS(X) = \HtoL(X)$ ile yüksek seviyeli diyagramlardan düşük seviyeli diyagramlara bir funktöre serbestçe genişletiriz.³¹ Dahası her $\syn{S} \subseteq \VninH$ alt kümesi için $\strucSL$'de, salt diyagramatik düzeyde bir eşitliğimiz vardır: [Şekil/dizge: MDSL] $=$ $\HtoLS$( [Şekil/dizge: MDSH] ) (50) Yani düşük seviyeli modeli $\HtoL(S)$'de açmak, yüksek seviyeli modeli $S$'de açma diyagramına $\HtoLS$ uygulamakla aynı biçimsel diyagramı verir.

³¹ Burada $\SigS_L$'nin değişkenlerinin $\Openqueries(\VL)$'nin türleri olduğunu kullanırız. Daha önceki gibi doğallık koşulunun (49) o zaman otomatik olarak keyfî yüksek seviyeli diyagramlara genişlediğine dikkat edin.

Modelin üzerine çok hafif varsayımlar altında $\HtoLS$ eşlemesinin var olduğunda tek olduğunu ve dolayısıyla bunu terminolojimizin önerdiği gibi $(\HtoL,\LtoH)$ tecritinin bir *özelliği* olarak görebileceğimizi birazdan göreceğiz. Bu amaçla şu salt çizge-kuramsal tanım yararlı olacaktır.

**Tanım (abstraction-abstract-conds).** $\pi$, $\modelML$ ile $\modelMH$ arasında bir yapıcı nedensel tecritin $(\HtoL,\LtoH)$ bölümü olsun ve her $\syn{X} \in \varH$ için tanımlayalım:
$$\mechlevelset(\syn{X}) := \{\syn{Z} \in \varL \mid \pi(\Pa(\syn{X}))\text{'dan geçmeyen}, \dagGL\text{'de bir yönlü } Z \to \pi(\syn{X}) \text{ yolu vardır}\}$$
$\pi$'ye şu hallerde:
- *güçlü* deriz, eğer $\syn{X} \neq \syn{Y}$ için $\mechlevelset(\syn{X}) \cap \pi(\syn{Y}) = \emptyset$;
- *ekstra-güçlü* deriz,³² eğer $\syn{X} \neq \syn{Y}$ için $\mechlevelset(\syn{X}) \cap \mechlevelset(\syn{Y}) = \emptyset$;
- *tam* deriz, eğer her $\syn{Y} \in \pi(\Pa(X) \setminus \VinH)$ için $\dagGL$'de bir yönlü $\syn{Y} \to \pi(X)$ yolu varsa.

³² Tanım gereği $\pi(\syn{X}) \subseteq \mechlevelset(X)$ olduğuna dikkat edin.

Sezgisel olarak $\mechlevelset(X)$, $\Pa(X)$'in düşük seviyeli temsilinin $X$'inkini ne ölçüde 'perdelediğini' yakalar.

Şimdi diyagramların eşitliğini (50) elde etmek için $(\HtoL,\LtoH)$ üzerindeki koşulları adlandırabiliriz. Aslında birkaç sonucu birden sunacağız; çünkü koşullar her modelin yapı kategorisi $\strucS$'nin, imzası $\Sig$ tarafından doğurulan, nasıl tanımlanmayı seçildiğine tam olarak bağlı olacaktır; bunun için birkaç seçeneği ve her biri için karşılık gelen bir sonucu ele alacağız.

Bunlardan ilki için örn. [cho2019disintegration]'daki Markov kategorisi kavramının hafif bir zayıflatılmasını ele alırız. Bir *cd-kategori* $\catC$, her $A$ nesnesi üzerinde (tek yerine) seçilmiş bir atma morfizması $\discard{A} \colon A \to I$ olması dışında bir Markov kategorisi gibi tanımlanır ve şunu sağlar: [Şekil/dizge: disc-nat, disc-I] Bir *cd-funktör* $F \colon \catC \to \catD$ de bu atma morfizmalarına saygı göstermelidir.³³

³³ Bir cd-kategoride $\discard{} \circ f = \discard{}$ olan bir $f$ morfizmasına *kanal* deriz. Cd-funktörler $F$ ve doğal dönüşümler $\alpha$ Markov durumu gibidir; ama ayrıca $F(\discard{A}) = \discard{F(A)}$ ve bütün dönüşüm bileşenleri $\alpha_X$ (ve $F$ için yapı izomorfizmaları) kanaldır.

**Tanım (struc-well-behavedness).** $\strucSL, \strucSH$ ilgili serbest yapı kategorileri olan nedensel modeller $\modelML, \modelMH$ verildiğinde, $\syn{\VL}$'nin ayrık alt kümelerinin $(\HtoL(\syn{X}))_{X \in \syn{\VH}}$ kolleksiyonuna, $\HtoL$ şu hallerde *yapısal olarak iyi-huylu* deriz:
- $\Sig$'nin doğurduğu serbest cd-kategori $\strucS = \FreeCD(\Sig)$ kullanıldığında ([lorenz2023causal, tull2024towards]'teki gibi ve özünde [jacobs2019causal]), *ekstra-güçlü ve tam*;
- serbest Markov kategorisi $\strucS = \FreeMarkov(\Sig)$ kullanıldığında ([fritz2023free]'teki gibi), her mekanizmanın bir kanal olduğunu belirten belitleri eşdeğer olarak ekleyerek, *ekstra-güçlü*: [Şekil/dizge: mechanisms-channels]
- serbest Kartezyen kategori $\strucS = \FreeCart(\Sig)$ kullanıldığında, her mekanizmanın belirlenimci bir kanal olduğunu belirten daha fazla belitleri eşdeğer olarak ekleyerek, *güçlü*: [Şekil/dizge: mechanisms-det]

Tanım 'struc-well-behavedness'taki listeden aşağı inerken $\strucS$'ye daha çok diyagramatik belit ekleriz ve dolayısıyla eşitliğin (50) elde edilmesi daha kolaydır. Şimdi güçlü yapıcı nedensel tecriti karakterize eden ana sonucumuzu ispatlayabiliriz.

**Teorem 2 (strongCCAnew).** $\modelML$'nin her girdi değişkeninin $\catC$'de en az bir normalize durumu olduğunu varsayalım.³⁴ Her yapı-türü (Kartezyen, Markov veya cd) için şunların belirtilmesi denktir:
1. Bir güçlü yapıcı nedensel tecrit $(\HtoL,\HtoLS,\LtoH)$;
2. $\HtoL$'nin yapısal olarak iyi-huylu olduğu bir yapıcı nedensel tecrit $(\HtoL,\LtoH)$;
3. Aşağıdaki gibi yapısal olarak iyi-huylu bir cd-funktör $\HtoLS$ ve doğal dönüşüm $\LtoH$: [Şekil/dizge: struc-refinement_b]

³⁴ Daha genel olarak sonuç için yalnızca her girdi değişkeni $\syn{V} \in \Vin$ ve $\catC$'deki bütün $f, g \colon X \to Y$ için $\discard{V} \otimes f = \discard{V} \otimes g \implies f = g$ olmasını isteriz.

*İspat.* Ek 'app:strongCA-proof'ta.

Sonuç bize bir yapıcı nedensel tecritin ancak ve ancak $\HtoL$ bölümü, yapı türü seçimine bağlı olarak, güçlü, ekstra-güçlü veya ekstra-güçlü ve tam olma gibi karşılık gelen koşulları sağlıyorsa mekanizma düzeyine genişlediğini söyler. $\strucS = \FreeCD(\Sig)$ için bir sonuç belirtmiş olsak da tipik bir nedensel model için serbest Markov kategorisi $\strucS = \FreeMarkov(\Sig)$ kullanmak belki daha doğaldır; çünkü her mekanizmanın $\catC$'de bir kanal olacağını biliriz ve bu durumda $\HtoL$ ekstra-güçlü olmalıdır. Ancak sinir ağları gibi belirlenimci modeller için $\strucS = \FreeCart(\Sig)$ almak doğaldır ve şimdi yalnızca $\HtoL$'nin güçlü olmasını isteriz.

Eşdeğer olarak son koşul böyle bir tecriti salt yapı düzeyinde bir funktör cinsinden ifade eder. Yapı olarak serbest Markov kategorileri kullanıldığında bu son koşul daha da basit bir biçimde yakalanabilir.

**Lemma 2 (Markov-equiv).** $\VninH \subseteq \VoutH$ olan nedensel modeller $\modelML, \modelMH$ olsun. Bir cd-funktör $\HtoLS \colon \FreeMarkov(\Sig_\modelMH) \to \FreeMarkov(\Sig_\modelML)$ ancak ve ancak $\HtoLS(\netdiag{\modelMH})$, $\HtoLS(\VinH) = \VinL$, $\HtoLS(\VoutH) \subseteq \VoutL$ ve $\HtoLS(\syn{\VninH}) \subseteq \syn{\VninL}$ ile yine $\strucSL$'de bir ağ diyagramıysa yapısal olarak iyi-huyludur.

*İspat.* Ek 'app:strongCA-proof'ta.

Serbest Markov kategorileri kullanıldığında bir güçlü yapıcı nedensel tecrit belirtmek bu yüzden basitçe yukarıdaki anlamda genel ağ diyagramlarına saygı gösteren bir $\HtoLS$ cd-funktörü ve $\LtoH$ dönüşümü vermeye eşdeğerdir. Şaşırtıcı biçimde bu, yapıcı tecritlerin bu potansiyel olarak geniş sınıfını salt mekanizmalar ve girdi-çıktı davranışı cinsinden, dolayısıyla müdahalelere veya (Do-)sorgulara hiç açık atıf olmaksızın tanımlayabileceğimizi söyler. Açık bir soru o halde pratikteki bütün ilginç yapıcı tecrit durumlarının bu biçimde olup olmadığıdır; yani $\HtoL$ bölümlerinin güçlü olup olmadığıdır.

Şimdi güçlü yapıcı nedensel tecritlerin bazı örneklerini ve örnek olmayanlarını verelim.

**Örnek.** Yapıcı tecritin Örnek 'CCA'sı, $\strucS = \FreeCart(\Sig)$ alındığında — ki model belirlenimci olduğundan uygun bir seçimdir — ve aslında daha güçlü biçimde $\strucS = \FreeMarkov(\Sig)$ alındığında da mekanizma düzeyindedir. Bunu Teorem 2'nin $(1) \Leftrightarrow (2)$'si ile denetlemek kolaydır; çünkü $\HtoL$ açıkça basittir ve aslında ekstra-güçlü olduğunu görmek de basittir.³⁵

³⁵ Örnek 'CCA'daki Denk. (24)'ün koşullarının, Teorem 2'nin $(1) \Leftrightarrow (3)$'ü ve Lemma 2 nedeniyle bağıntıyı mekanizma düzeyinde daha doğrudan da kurmayı kolaylaştırdığına dikkat edin. $\HtoLS(\netdiag{\modelMH})$'nin bir ağ diyagramı olduğu açıktır.

Tanım 'struc-well-behavedness'ın farklı durumlarını örnekleyen başka pedagojik örnekler aşağıdadır.

**Örnek (notsimple).** $\modelML$ ve $\modelMH$, $\catC$'de şu ilgili ağ diyagramlarıyla tanımlı nedensel modeller olsun: [Şekil/dizge: CA-ex-1-DL, CA-ex-1-DH] $\catC$'de $a,b,c,d,e$ morfizmalarının hepsinin belirlenimci olduğunu ve $a=c \circ e$, $b = d\circ e$ olduğunu varsayalım. O halde $\syn{\HtoL :: X \mapsto \{X\}, Y \mapsto \{Y\}, W \mapsto \{W\}}$ koyarak $\LtoH=\id{}$ ile bir yapıcı nedensel tecrit vardır. Örneğin yüksek seviyeli girdi-çıktı kanalı için $\modelMHio = \modelMLio$ elde ederiz; çünkü: [Şekil/dizge: CA-ex-1-equality_b]

Bu tecrit ekstra-güçlü değildir; çünkü bu $\pi$ için $\mechlevelset(\syn{X}) = \{\syn{X, Z}\}$, $\mechlevelset(\syn{Y}) = \{\syn{Y,Z}\}$ ve $\mechlevelset(\syn{W}) = \{\syn{W}\}$'dir ve dolayısıyla $\mechlevelset(\syn{X})$ ve $\mechlevelset(\syn{Y})$ ayrık değildir. Yapı için serbest bir Markov kategorisi $\strucS=\FreeMarkov(\SigS)$ (veya serbest cd-kategori) kullanırsak hiçbir yapı-aşağı tecritin mümkün olmadığını görürüz; çünkü $\HtoLS(\netdiagout{\modelMH}{X,Y}) \neq \netdiagout{\modelML}{X,Y}$ bulunur. Gerçekten diyagram olarak: [Şekil/dizge: CA-ex-1-inequality] (51) Yine de bu tecrit *güçlü*dür ve yapı için bunun yerine serbest bir Kartezyen kategori $\strucS=\FreeCart(\SigS)$, yani her kutunun belirlenimci olmasını isteyen, alırsak (51) bir eşitliğe dönüşür ve gerçekten bir yapı-aşağı tecrit elde ederiz.

Bir yapıcı nedensel tecriti, yine $\tau = \id{}$ ile, alternatif olarak $\syn{\HtoL :: X \mapsto \{X\}}$, $\syn{Y \mapsto \{Y\}}$, $\syn{W \mapsto \{W,Z\}}$ koyarak tanımlayabileceğimize dikkat edin. Şimdi $\syn{N}=\syn{X},\syn{Y},\syn{Z}$'nin her biri için $\mechlevelset(\syn{N}) = \HtoL(\syn{N})$ olur; bu tecriti ekstra-güçlü kılar ve serbest Markov kategorileri kullanıldığında bile bir güçlü yapıcı nedensel tecrit tanımlar.

**Örnek.** $\modelML$ ve $\modelMH$, $\catC$'de şu ilgili ağ diyagramlarıyla tanımlı nedensel modeller olsun: [Şekil/dizge: CA-ex-2-nds_b] $\modelML$ ile $\modelMH$ arasında $\syn{\pi :: X \mapsto \{X\}, Y \mapsto \{Y,Y'\}, Z \mapsto \{Z,Z'\}}$ ve $\LtoH_X=id_X$ ile verilen bir yapıcı tecrit vardır: [Şekil/dizge: CA-ex-2-taus] Ancak bu *güçlü* değildir; çünkü $\syn{X \in \pi(X) \cap \mechlevelset(Y)}$.³⁶ Bu tecrit bir yapı-aşağı tecrite genişlemez ve gerçekten $\HtoLS$'yi (48)'deki gibi tanımlayamayız bile; çünkü $\HtoLS(\syn{a})$, $\strucSL$'de $\syn{Y} \otimes \syn{Y'}$'in bir durumu olurdu, ama böyle bir durum yoktur.

³⁶ Bu, koşul (52)'nin başarısız olduğu anlamına gelir; dolayısıyla gerçekten $\HtoLS$ tanımlanamaz.

**Not.** Herhangi bir yapıcı nedensel tecritin Denk. (49)'a yakın her yüksek seviyeli mekanizma için bir koşulu gerçekten ima ettiğine dikkat edin. Her $\syn{X} \in \VninH$ için $\syn{S}:=\Pa(X) \setminus \VinH$ koyalım. O halde $\catC$'de aşağıdaki sağ taraftaki eşitliğe sahibiz:
