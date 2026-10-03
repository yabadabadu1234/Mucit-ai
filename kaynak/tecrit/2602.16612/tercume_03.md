*(Bu parça kaynağın 930–1259. satırlarını kapsar. Notasyon ve şekil geleneği `tercume_01.md` başındaki notla aynıdır.)*

İki model arasındaki ilişki bir değişken hizalaması cinsinden yeniden ifade edilebilir: $\HtoL(G_1)=\{X_1,...,X_{33}\}$, $\HtoL(U_1')=\{U_1,...,U_{33}\}$, $G_2,U_2'$ ve $G_3,U_3'$ için benzer biçimde ve $\HtoL(T')=\{T\}$, $\HtoL(A_1)=\{A_1 \}$, $\HtoL(U_{100})=\{U_{100} \}$, $\HtoL(A_2)=\{A_2\}$, $\HtoL(U_{101})=\{U_{101}\}$ ile; $\LtoH$ eşlemesi, $\LtoH_{T'}(t) = 1$ eğer $t>49$ ve aksi halde $0$, $\LtoH_{G_1} = \sum_{i=1}^{33} X_i$, $G_2$ ve $G_3$ için benzer, ve $\LtoH$'yı (dışsal) girdi değişkenlerinde ve $A_1,A_2$'de özdeşlik alarak verilir. O halde şu geçerlidir: [Şekil/dizge: CCA-example-fTprime-consistency, CCA-example-fG-consistency] (24) ve $f_{G_2}$ ile $f_{G_3}$ için benzer.

Bu verinin gerçekten bir yapıcı tecrit $\modelL \rightarrow \modelH$ tanımladığı denetlenebilir. Açıklayıcı bir örnek olarak $S=\{G_1\}$ üzerinde soyut bir Do-müdahalesi için tutarlılığı doğrularız; diğerleri benzer biçimde geçer. Soldan sağa sıra Denk. (21)'le eşleşir ama hesap aslında en kolay sağdan sola yapılır: (a) ve (d) tanım gereği geçerlidir; (b) $f_{G_2}$ ve $f_{G_3}$ için Denk. (24)'ün sağ tarafı gibi eşitlikler kullanır; (c) belirlenimci $\LtoH$ morfizmalarının üç örneğini kopyalama eşlemelerinden geçirir ve sonra Denk. (24)'ün sol tarafını kullanarak yeniden yazar. [Şekil/dizge: CCA-example-consistency-example-1 … -5; (d), (c), (b), (a) eşitlik adımları]

### 5.3 Kısıtlı yapıcı nedensel tecrit

Pratikte keyfî girdilerde yapıcı bir nedensel tecrit koşulunu doğrulamak mümkün olmayabilir; yalnızca düşük seviyeli modelin kendisinden doğan girdilerde (bir alt kümesinde) mümkün olabilir. Bu, bunun yerine değiş-tokuş sorgularına dayanan şu daha zayıf kavrama götürür [GeigerEtAl_2021_CausalAbstracttoinOfNN, geiger-etal-2020-neural].

**Tanım (Kısıtlı yapıcı nedensel tecrit).** Bir *kısıtlı yapıcı nedensel tecrit* $\modelML \to \modelMH$, bir değişken hizalaması $\dvaralign{\HtoL}{\LtoH}{\modelVL}{\modelVH}$ ile, bütün ayrık $\syn{S_1,\dots,S_n \subseteq \VintH}$ alt kümeleri için $\catC$'de şunun geçerli olduğu biçimde verilir: [Şekil/dizge: weak-CA-natural] (25)

Yukarıdakiler, aşağıdaki gibi biçimselleştirebileceğimiz değiş-tokuş sorguları $\WOpenqueries(\varV)$ arasında bir tutarlılık koşuluna karşılık gelir.

**Önerme.** $(\HtoL,\LtoH)$ değişken hizalamalı bir kısıtlı yapıcı nedensel tecrit $\modelML \to \modelMH$, $\HtoL(\VinH) = \VinL$, $\HtoL(\VintH) \subseteq \VintL$ olacak biçimde ve

$$\HtoL \big( \wopenquery{}{S_1,\dots,S_n} : \VinH \to X \big) = \wopenquery{}{\HtoL(S_1),\dots,\HtoL(S_n)} : \VinL \to \HtoL(X) \tag{26}$$

koşuluyla bir sorgu-aşağı tecrit $\qdownabs{\HtoL}{\LtoH}{\SigModel{\WOpenqueries(\varL)}{\modelML}}{\SigModel{\WOpenqueries(\varH)}{\modelMH}}$'ye eşdeğerdir.

*İspat.* Ek 'app:proofs'ta.

Yapıcı tecritin somut Do-müdahaleleriyle ilişkili olması gibi, kısıtlı yapıcı nedensel tecrit de somut değiş-tokuş müdahaleleriyle ilişkilidir. Bir sorgu-yukarı tecrit $\qupabsshort{\SigModel{\II(\modelVL)}{\modelML}}{\SigModel{\II(\modelVH)}{\modelMH}}$, düşük seviyeli değiş-tokuş müdahalelerini yüksek seviyeli olanlara tutarlı biçimde örten biçimde eşlemelidir ve kısıtlı yapıcı nedensel tecrit bunu yapmanın yapılı bir yolunu sağlar.

**Sonuç 2.** Örten $\LtoH$ ile herhangi bir kısıtlı yapıcı nedensel tecrit $\modelML \to \modelMH$, şu yolla $\qupabs{\HtoL}{\LtoH}{\LtoHquery}{\SigModel{\II(\modelVL)}{\modelML}}{\SigModel{\II(\modelVH)}{\modelMH}}$ biçiminde bir sorgu-yukarı tecrit tanımlar: $\LtoHquery ( \II(\HtoL(S_j), x_j)^n_{j=1}) := \II(S_j,\LtoH \circ x_j)^n_{j=1}$.

Yapıcı tecritte olduğu gibi böyle bir yukarı tecrit de somut (değiş-tokuş) müdahalelerinin bir tam dönüşümünü verir: $\qupabs{\HtoL}{\LtoH}{\LtoHquery}{\SigModel{\II(\modelVL)^{\mathsf{io}}}{\modelML}}{\SigModel{\II(\modelVH)^{\mathsf{io}}}{\modelMH}}$.

*İspat.* Böyle bir yukarı tecritte sorgular üzerindeki tutarlılık koşulu basitçe şu ifadeye dönüşür: [Şekil/dizge: II-concretely] (27) bu, (25)'ten hemen çıkar. Alternatif olarak Önerme 'Exact-trans-from-ref'i $\SigQH=\WOpenqueries(\VH)$, $\SigQL=\WOpenqueries(\VL)$ ile uygulayın. $\syn{Q} = \wopenquery{X}{\syn{S_1,\dots,S_n}}$ için $Z_Q = S_1 \otimes \dots \otimes S_n$ alırız.

**Not.** Bir kısıtlı yapıcı nedensel tecrit bağıntısından, (25)'in sağ tarafını şöyle yeniden yazabileceğimiz çıkar:¹⁹ [Şekil/dizge: weak-CA-rewrite-LHS] Dolayısıyla bir kısıtlı yapıcı nedensel tecrit tam olarak, bir yapıcı tecritin geçerli olduğu ama yalnızca $\HtoL(S)$'in şu biçimdeki girdi durumlarıyla sınırlı olduğu ifadesidir; burada $\syn{S = S_1 \cup \dots \cup S_n}$ ayrıktır. [Şekil/dizge: input-states] (28)

¹⁹ Yeniden yazma, (25)'in $\syn{S_1}=\dots = \syn{S_n} = \emptyset$ özel durumunu kullanır.

### 5.4 Karşı-olgusal tecrit

Önce karşı-olgusalların tanımlandığı nedensel model türünü adlandıralım.

**Tanım (Fonksiyonel Nedensel Model, FCM).** Bir Markov kategorisi $\catC$'de bir *Fonksiyonel Nedensel Model (FCM)*, değişkenleri $\Vout = \syn{\FMCVen}$, $\Vin=\emptyset$ olmak üzere $\syn{V = \FMCVen \cup U}$ biçiminde bölümlenmiş bir nedensel modeldir. *Dışsal* değişkenler $\syn{U}=\{\syn{U_i}\}^n_{i=1}$, her $\syn{U_i}$'nin ebeveyni olmayacak ve mekanizmaları aşağıda solda olacak biçimdedir ve *içsel* değişkenler $\syn{\FMCVen} = \{\syn{X_i}\}^n_{i=1}$ aşağıda sağdaki biçimdedir: [Şekil/dizge: noise-new, SCM-2] (29) burada $\Pa'(\syn{X_i}) \subseteq \syn{\FMCVen}$ ve $f_i = \semSM{\syn{f_i}}$ belirlenimcidir (2).²⁰

²⁰ Burada bir FCM'nin girdisi olmadığı tipik geleneğini izliriz; ancak ekstra girdili varyantlar kolayca ele alınabilir. Biçimsel olarak bir FCM'nin imzası her $\syn{f_i}$'nin belirlenimci olduğunu belirten denklemler içerir.

**Örnek.** $\catC = \FStoch$'ta bir FCM tam olarak olağan anlamda bir *Yapısal Nedensel Model (SCM)*'dir. Sonlu kümeler $X_i,U_i$'den ve her $i$ için $U_i$ üzerinde bir $\lambda_i$ dağılımı ve $\Pa'(X_i) \subseteq \FMCVen = \{X_1,\dots, X_n\}$ olacak biçimde bir $f_i \colon \Pa'(X_i) \times U_i \to X_i$ fonksiyonundan oluşur.

**Örnek.** Aşağıdaki, $\syn{\FMCVen=\{S,L,A\}}$ ve $\syn{U=\{U_S,U_L,U_A\}}$ olan bir FCM için bir ağ diyagramı gösterir. [Şekil/dizge: FCM-ex-smaller]

Yakından ilgili olarak şu vardır. *Belirlenimci* bir nedensel model $\modelF$ ile, mekanizmaları $c_X$ her $X \in \Vnin$ için belirlenimci olan bir nedensel modeli kastederiz.²¹ Biçimsel olarak herhangi bir FCM'yi iki açık nedensel modelin bir bileşkesi olarak görebiliriz:²² $\modelM = \modelF \circ \modelU$: $U$ girdili, bütün belirlenimci $f_i$ mekanizmalarını içeren $\FMCVen, U$ üzerinde belirlenimci bir model $\modelF$ ve yalnızca $U$ ve mekanizmalarını içeren, şu ortak duruma karşılık gelen bir $\modelU$ modeli: [Şekil/dizge: lambda-state]

²¹ Belirlenimci bir nedensel model olmanın değişkenlerin belirli bir bölümlenmesi üzerine koşul getirmediğine dikkat edin; dolayısıyla bir kök düğüm değişkeni ya bir girdidir ya da 'mekanizması' olarak keskin bir durumu (nokta dağılımı) vardır.
²² Açık nedensel modeller arasındaki terkip kavramının ayrıntıları için [lorenz2023causal, Bölüm 5.2]'ye bakınız; terkip, ilgili mekanizma kümelerinin birleşimini alır ve terkibin yapıldığı ilgili girdi ve çıktı değişkenlerini özdeşleştirir.

**Karşı-olgusal sorgular.** Şimdi [xia2024neural]'ı izleyerek FCM'lere özgü tanımlanabilir sorguları ele alalım. Soyut değişkenler $\syn{\CFVen}$ verildiğinde, $j=1,\dots,m$ için her $\CFOpenSet_j, Y_j \subseteq \syn{\CFVen}$ alt kümeleri seçimi için, girdileri $(\CFOpenSet_j)_{j=1}^m$ ve çıktıları $(Y_j)_{j=1}^m$ olan bir $\syn{\Lthreequery{Y_1|_{\CFOpenSet_1},\dots,Y_m|_{\CFOpenSet_m}}}$ sorgusu içeren, $\syn{\CFVen}$ türlü *karşı-olgusal (CF) sorgular* imzası $\absLthree(\syn{\CFVen})$'yi tanımlarız. $\syn{\CFVen}, \syn{U}$ üzerindeki herhangi bir FCM $\modelM = \modelF \circ \modelU$, sorguların bir modelini şöyle verir: [Şekil/dizge: L3-inC-simple_b] (30) Benzer şekilde $\catC$'de somut değişkenler $\model{\CFVen}$ verildiğinde, $\syn{\CFVen}$ türlü ve $j=1,\dots,m$ için $\CFOpenSet_j, Y_j \subseteq \syn{\CFVen}$ alt kümeleri ve $\CFOpenSet_j$'nin keskin durumları $\CFDostates_j$ seçimi için çıktıları $\syn{Y_1,\dots,Y_m}$ olan ve girdisi olmayan bir $\Lthreequery{Y_1|_{\CFDostates_1},\dots,Y_m|_{\CFDostates_m}}$ sorgusu olan *somut CF sorguları* imzası $\Lthree(\model{\CFVen})$'yi tanımlarız;²³ $\CFVen, U$ üzerindeki herhangi bir FCM $\modelM = \modelF \circ \modelU$ ile şöyle modellenir: [Şekil/dizge: conc-exp-simpler]

²³ Somut değişkenler belirtilmiş girdi ve çıktı alt kümeleriyle gelir; burada $\syn{\CFVen^{\text{in}}}=\emptyset$ isteriz; çünkü CF sorgularının türleri yalnızca (bu sorguların bir modelini veren herhangi bir FCM'de) içsel sayılan değişkenler üzerinde gezinir.

Somut CF sorguları *karşı-olgusallar*la yakından ilişkilidir. Özünde bir karşı-olgusal, somut bir CF sorgusundan doğan koşullu bir olasılık dağılımıyla verilir; ayrıntılar için bkz. [lorenz2023causal].²⁴

²⁴ $\Lthreequery{Y_1|_{\CFDostates_1},\dots,Y_n|_{\CFDostates_n}}$ gibi terimler ile 'karşı-olgusal ifadelerin birleşimleri' arasındaki ilişki dahil.

**Karşı-olgusal tecrit.** Şimdi, özünde [xia2024neural]'dan, ilişkili tecrit kavramıyla karşılaşabiliriz.

**Tanım (Karşı-olgusal tecrit).** $\modelML, \modelMH$, somut içsel değişkenleri $\model{\FMCVen}_L, \model{\FMCVen}_H$ olan FCM'ler olsun. Bir *CF tecriti* $\modelML \to \modelMH$, bir değişken hizalaması $\dvaralign{\HtoL}{\LtoH}{\model{\FMCVen}_L}{\model{\FMCVen}_H}$ ile, bütün CF sorguları $\Lthreequery{Y_1|_{\CFOpenSet_1},\dots,Y_m|_{\CFOpenSet_m}} \in \Lthree(\syn{\FMCVen_H})$ için $\catC$'de şunun geçerli olduğu biçimde verilir: [Şekil/dizge: compat-simpler_b_no_H] (31)

Şimdiye dek yukarıdakini hemen bir doğallık koşulu olarak tanıyabiliriz.

**Önerme.** Bir CF tecriti $\modelML \to \modelMH$, şu şekilde $\qdownabs{\HtoL}{\LtoH}{\SigModel{\absLthree(\syn{\FMCVen_L)}}{\modelML}}{\SigModel{\absLthree(\syn{\FMCVen_H})}{\modelMH}}$ biçimindeki bir sorgu-aşağı tecrit ile eşdeğerdir:

$$\HtoL(\Lthreequery{Y_1|_{\CFOpenSet_1},\dots,Y_m|_{\CFOpenSet_m}}) := \Lthreequery{\HtoL(Y_1)|_{\HtoL(\CFOpenSet_1)},\dots,\HtoL(Y_m)|_{\HtoL(\CFOpenSet_m)}} \tag{32}$$

*İspat.* Bir CF tecriti verildiğinde $\HtoL, \LtoH$'yı her zamanki gibi değişken çarpımlarına genişletin ve sorgular üzerinde bir eşlemeyi (32) ile tanımlayın. O halde (31) tam olarak tutarlılığın (doğallığın) geçerli olduğunu söyler. Tersine, böyle bir sorgu-aşağı tecrit verildiğinde tutarlılık (31)'in geçerli olmasını sağlar. Tanım gereği $\HtoL$ değişken alt kümelerini değişken alt kümelerine gönderir; bu $(\HtoL,\LtoH)$'yı bir değişken hizalaması yapar.

Yine somut bir sorgu-yukarı tecrit karşılığı vardır; burada somut karşı-olgusal sorgulara $\Lthree(\model{\CFVen})$ uygulanır.

**Sonuç 3.** Örten $\LtoH$ ile herhangi bir CF tecriti $\modelML \to \modelMH$, şu yolla $\qupabsshort{\SigModel{\Lthree(\model{\FMCVen}_L)}{\modelML}}{\SigModel{\Lthree(\model{\FMCVen}_H)}{\modelMH}}$ biçiminde bir sorgu-yukarı tecrit belirler:

$$\LtoHquery(\Lthreequery{\HtoL(Y_1)|_{\CFDostates_1},\dots,\HtoL(Y_m)|_{\CFDostates_m})} := \Lthreequery{Y_1|_{\LtoH \circ \CFDostates_1},\dots,Y_m|_{\LtoH \circ \CFDostates_m}} \tag{33}$$

*İspat.* Böyle bir sorgu-yukarı tecrit için tutarlılık koşulu şudur: [Şekil/dizge: compat-concrete_b_no_H] (34) bu (31)'den çıkar. Alternatif olarak Önerme 'Exact-trans-from-ref'i $\SigQH=\absLthree(\FMCVen_H)$, $\SigQL=\absLthree(\FMCVen_L)$ ile uygulayın. (30)'daki gibi her böyle $\syn{Q}$ sorgusu için $\syn{Z_Q}$, $\syn{\CFOpenSet_1 \otimes \dots \otimes \CFOpenSet_n}$'dir.

Yazındaki diğer kavramlarda olduğu gibi karşı-olgusal tecritler daha önce somut sorgu-yukarı tecritler olarak getirilmiştir [xia2024neural]. $\model{\CFVen}$ üzerinde bir *somut CF sorguları* kolleksiyonu ile türleri $\syn{\CFVen}$ değişkenleriyle verilen bir $\SigQ \subseteq \Lthree(\model{\CFVen})$ sorgu alt kümesini kastederiz. $\model{\FMCVen}_H$ üzerinde somut CF sorguları $\SigQ$ ve bir değişken hizalaması $\dvaralign{\HtoL}{\LtoH}{\model{\FMCVen}_L}{\model{\FMCVen}_H}$ verildiğinde, $\modelML, \modelMH$'nin, $\SigQ$'daki bütün $\Lthreequery{Y_1|_{\LtoH \circ \CFDostates_1},\dots,Y_m|_{\LtoH \circ \CFDostates_m}}$ sorguları için (34) geçerli olduğunda *$\SigQ$-$\LtoH$ tutarlılığı* [xia2024neural, Tanım 7] sağladığını söyleriz. O halde hemen şu çıkar.

**Sonuç 4.** $\modelML, \modelMH$ FCM'leri, ancak ve ancak veri, $\sigQH$'deki bütün $\Lthreequery{Y_1|_{\LtoH \circ \CFDostates_1},\dots,Y_m|_{\LtoH \circ \CFDostates_m}}$ sorguları için (33) yoluyla bir sorgu-yukarı tecrit $\qupabs{\HtoL}{\LtoH}{\LtoHquery}{\SigModel{\Lthree(\model{\FMCVen}_L)}{\modelML}}{\SigModel{\sigQH}{\modelMH}}$ belirliyorsa $\SigQ$-$\LtoH$ tutarlılığını sağlar.

### 5.5 Dağıtık nedensel tecrit

Yapıcı tecrit gibi tecrit kavramları 'yerel'dir; yüksek seviyedeki $\syn{V}$ değişkenlerini bir değişken hizalaması aracılığıyla düşük seviyedeki *ayrık* $\HtoL(\syn{V})$ alt kümeleriyle ilişkilendirirler. Bu özelliği taşımayan, 'dağıtık' diyebileceğimiz daha genel tecrit türlerinin, örn. ML'de, daha pratik olabileceği savunulmuştur [geiger2024finding, geiger2023causal]. Gerçekten Bölüm 5.1'deki tam dönüşümler ve güçlü nedensel tecrit, genel olarak böyle bir 'dağıtıklığa' izin verir. Bu bölümde, [geiger2024finding, geiger2023causal]'dan esinlenen, bir nedensel modeli tanımlamanın şu yolundan yararlanan, belirli bir dağıtık tecrit sınıfını tartışıyoruz.

#### 5.5.1 Model indüksiyonu

Bu bölüm boyunca $\modelM$ her zaman, $\Vout = \Vnin$ olan ve her $X$ değişkeninin $\catC$'de en az bir normalize durumu bulunan, $\modelV$ değişkenleri üzerinde belirlenimci bir açık nedensel modeli gösterecektir.

**Tanım (Belirlenimci kanallardan modeller ve tersi).** *Paralel mekanizma kanalını* $\parmechdiag_\modelM \colon V \to V$ şöyle tanımlarız: [Şekil/dizge: par-mech-2-conc-nodots] (35) burada $\syn{V} = \syn{X_1,\dots,X_n}$. Burada her girdi-olmayan $\syn{X}$ değişkeni için şunu koyarız: [Şekil/dizge: FX-only-nodots] $:=$ [Şekil/dizge: FX] (36) ve her girdi değişkeni $\syn{X}$ için şunu tanımlarız: [Şekil/dizge: FX-only-nodots] $:=$ [Şekil/dizge: mech-input-only] (37) Tersine, $\parmechdiag \colon V \to V$, $\catC$'de belirlenimci bir kanal olsun ve her $X$ üzerindeki marjinal için $\parmechdiag_X$ yazalım. Bir $\Sig_\parmechdiag$ imzasını ve $\modelfrom{\parmechdiag}$ modelini şöyle tanımlarız. (37) geçerli olduğunda $\syn{X}$'in bir girdi değişkeni olduğunu bildiririz. Aksi halde $\Pa(\syn{X})$'i, $\parmechdiag_X$'in (36)'daki gibi çarpanlara ayrıldığı en küçük değişken alt kümesi ve $c_X$'i karşılık gelen kanal olarak tanımlarız; bu [lorenz2023causal, Lemma 112] ile vardır. Sonra bu gösterimle bir $c_\syn{X} \colon \syn{\Pa(X) \to X}$ üreteci dahil ederiz. $\Sig_\parmechdiag$ geçerli bir nedensel imza tanımladığında, yani bu $\Pa(X)$ ebeveyn kümeleri $\syn{V}$ üzerinde çevrimsiz yönlü bir çizge doğurduğunda $\parmechdiag$ kanalına *çevrimsiz* deriz.

$\modelM$ açık belirlenimci bir nedensel model olarak sadık²⁵ ise $\parmechdiag_\modelM$'nin çevrimsiz olduğunu ve $\modelfrom{\parmechdiag_\modelM} = \modelM$ olduğunu görmek kolaydır. Yukarıdaki inşa tersine $\varVconc$ üzerindeki böyle herhangi bir çevrimsiz $\parmechdiag$ kanalından, $\parmechdiag_{\modelfrom{\parmechdiag}} = \parmechdiag$ ile, bir nedensel model $\modelfrom{\parmechdiag}$ tanımlamamıza izin verir.

²⁵ [lorenz2023causal]'in mekanizma-sadakati anlamında: $\modelM$'nin $Pa(X)$ ebeveyn kümeleri zaten (36)'nın geçerli olduğu asgarî olanlardır; yani $X$, $c_X$ aracılığıyla her ebeveyn değişkenine bağlıdır.

Bir modelin girdi-çıktı ve paralel mekanizma görünümlerini bağlayan yararlı bir olgu şudur.

**Lemma 1.** $\Vinconc \otimes \Vninconc$'ın herhangi bir keskin $v = (i, o)$ durumu için: [Şekil/dizge: io-view-vs-fixpoints]

*İspat.* Marjinalleri alınca ikincisi ancak ve ancak her $\syn{X} \in \Vnin$ değişkeni için $v_X = c_X \circ v|_\Pa(X)$ ise geçerlidir. Bir değişkenin en uzun ata zinciri üzerinde tümevarım yaparak bunun $o = \modelMio \circ i$'ye eşdeğer olduğu görülebilir.

**Örnek.** Do-müdahalelerinin ve değiş-tokuş müdahalelerinin $\parmechdiag_\modelM$'yi şöyle değiştirdiğini doğrulamak basittir. [Şekil/dizge: par-mech-do-nodots, par-mech-II-nodots] (38)

Şimdi yukarıdaki inşadan şu tanımı vermek için yararlanabiliriz.

**Tanım (Model İndüksiyonu).** $\modelM$, $\modelV$ değişkenleri üzerinde açık belirlenimci bir nedensel model olsun. $\model{W}$ başka bir somut değişkenler kümesi ve $\modin \colon V \simeq W$ belirlenimci bir izomorfizma olsun. Şu kanal: [Şekil/dizge: induced-model-nodots] (39) $\Win$ girdileriyle çevrimsizse²⁶ ve ayrıca $\modinin$, $\modinnin$ izomorfizmaları için: [Şekil/dizge: modelin] (40) $\modin$'in $\modelM$'ye *saygı gösterdiğini* söyleriz. Bu durumda *indüklenmiş* nedensel modeli $\inmod{\modelM} := \modelfrom{\parmechdiag_{\inmod{\modelM}}}$ olarak tanımlarız.

²⁶ Somut değişkenler olarak $\model{W}$'nin ${W^{\text{in}}}$ alt kümesiyle geldiğini ve buradaki koşulun (37) aracılığıyla tanımlı girdilerin bu ${W^{\text{in}}}$ kümesiyle örtüşmesi olduğunu hatırlayın.

Benzer şekilde $\modelM$ üzerinde bir $\Intset$ müdahaleler kümesi verildiğinde, $\modin$ her $\inti \in \Intset$ için $\transform{\inti}{\modelM}$'ye saygı gösteriyorsa $\SigModel{\Intset}{\modelM}$'e *saygı gösterir* deriz. Bu durumda her $\inti \in \SigI$ için $\inmod{\modelM}$ üzerinde $\transform{\inducedint{\inti}}{\inmod{\modelM}} := \inmod{\transform{\inti}{\modelM}}$ aracılığıyla indüklenmiş müdahale $\inducedint{\inti}$'yi tanımlarız. $\inmod{\modelM}$ üzerindeki bu tür müdahaleler kümesini $\inmod{\Intset}$ ile gösteririz.

Şimdi böyle bir model indüksiyonunun gerçekten bir sorgu-yukarı tecritin özel bir durumunu verdiğini gözleyelim. $\modelM$ üzerindeki herhangi $\Intset$ müdahalelerinin, $\syn{\invar, \outvar}$ türlü ve her $\inti \in \Intset$ için bir $\syn{\inti \colon \invar \to \outvar}$ sorgusu olan bir $\Intsetio$ sorgu imzası oluşturduğunu hatırlayın. Bu bölümde her böyle $\Intset$ kümesinin $\modelM$'nin kendisine karşılık gelen aşikâr $\noint$ müdahalesini içerdiğini daima varsayarız. Önerme 'ET-equiv-qup' ispatında olduğu gibi $\Intsetio$ sorgu imzalarına göre sorgu-yukarı tecritler için türler üzerinde yalnızca bir olası $\HtoL$ eşlemesi olduğunu hatırlayın ($\HtoL(\syn{in_H}) = \syn{in_L}$ ve $\HtoL(\syn{out_H}) = \syn{out_L}$). Bu yüzden bu bölümün geri kalanında karşılık gelen $\HtoL$'yı atacağız ve bir sorgu-yukarı tecritin verisine yalnızca $(\LtoHquery, \LtoH)$ olarak değineceğiz.

Son olarak anlambilim kategorisi $\catC$'nin *yeterince durumu olduğunu*, yani her keskin $x$ durumu için $f \circ x = g \circ x$ olduğunda $f = g$ olduğunu varsayacağız; bu $\FStoch$ için doğrudur.

**Önerme (Model-Induction).** $\modelM$, $\modelV$ üzerinde $\Intset$ müdahaleler kümeli açık belirlenimci bir nedensel model olsun. $\modin \colon V \to W$ belirlenimci bir izomorfizma olsun ve $\SigModel{\Intset}{\modelM}$'e saygı göstersin. O halde

$$\qupabslarge{}{\modin}{\inducedintmap}{\SigModel{\IntQsimple{\Intset}}{\modelM}}{\SigModel{\IntQsimple{\inducedintmap(\SigI)}}{\inmod{\modelM}}}$$

bir (eşlenik, bijektif) sorgu-yukarı tecrit tanımlar.
