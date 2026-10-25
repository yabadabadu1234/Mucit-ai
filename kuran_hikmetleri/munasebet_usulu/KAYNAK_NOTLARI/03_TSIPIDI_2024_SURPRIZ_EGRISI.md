# Ders notu 3: Bir metnin "şaşırtıcılık eğrisi" neden dalgalanır?

**Künye.** Eleftheria Tsipidi, Franz Nowak, Ryan Cotterell, Ethan Wilcox, Mario Giulianelli, Alex Warstadt (ETH Zürih, bilgisayar bilimleri), *Surprise! Uniform Information Density Isn't the Whole Story: Predicting Surprisal Contours in Long-form Discourse*, Empirical Methods in Natural Language Processing (EMNLP) 2024 toplantısı bildirileri, s. 18820–18836, Miami, 12–16 Kasım 2024. Metin ACL Anthology'den PDF olarak alınıp baştan sona okundu (ekler dâhil). Şekillerin (Şekil 1, 4–7) çubukları metin katmanında yoktur; şekillerin rakamları okunamadı, yalnız metnin kendi yazdığı hükümler ve p-değerleri aşağıdadır. Kod: github.com/rycolab/surprisal-discourse (eserin kendi beyanı).

**Bu nüshanın hâli.** CLAUDE.md § 3-I 326–329 uyarınca yazıldı: eserin bütün tarifleri, formülleri, tecrübeleri ve itirazları vardır; anlatış düzyazıdır. Her bahsin başındaki **Girizgâh** ve içindeki gündelik misal benimdir, müelliflerin değildir. Müelliflerin sözü ile benim çıkarımım karışmasın diye çıkarımlar en sonda ayrı bölümdedir.

---

## 0. Evvelâ şu: bir metin hep aynı hızla mı bilgi verir?

Bir hikâye anlatıcısını dinliyorsunuz. Başlangıçta nerede, kim, ne zaman gibi bilgileri yavaş yavaş veriyor; sonra bir anda "ve kapı açıldı" diyerek sizi sarsıyor; sonra bir müddet sakin ilerliyor; en sonunda toparlıyor. Eğer anlatıcı baştan sona **aynı hızda** bilgi verseydi, yani her cümle size tam aynı miktarda yeni şey söyleseydi, dinlemesi tuhaf ve yorucu olurdu. Fakat dilbilimde uzun zamandır bunun **tersi** savunulur: iyi bir konuşan, bilgiyi mümkün olduğu kadar **eşit** dağıtır.

O hâlde suâl şudur: **Bir metin boyunca bilgi miktarı neden hiç sabit değildir; dalgalanma şansa mı bağlıdır, yoksa metnin kurulu yapısından (bölümlere, paragraflara, cümlelere ayrılışından) önceden anlaşılabilir mi?**

Bu suale bir hesapla cevap arayan, ETH Zürih'te bilgisayarla dil çözümlemesi yapan bir ekiptir (Eleftheria Tsipidi ve arkadaşları). Fikirleri üç cümlede özetlenir. Birincisi: konuşanların bilgiyi eşit dağıtma eğilimi (Uniform Information Density, UID) doğrudur ama **tek kuvvet değildir**. İkincisi: gözlenen dalgalanma, **metnin iç içe kurulu yapısıyla** bir ölçüde önceden anlaşılabilir (**Yapılı Bağlam Hipotezi**, Structured Context Hypothesis). Üçüncüsü: bu yapı ne kadar **derin ve ince** ise (retorik ağaç) o kadar iyi anlaşılır; ne kadar yüzeydeyse (paragraf ve cümle) o kadar az.

---

## 1. Mukaddime: bilgi miktarı nasıl ölçülür, UID nedir? (s. 1–2)

**Girizgâh.** "Bu cümle ne kadar bilgi taşıyor" sualine ölçülü bir cevap vermek için "şaşırtıcılık" fikri lâzım: bir söz beklediğimiz bir şeyse bize az bilgi verir, beklenmedikse çok. Müellifler bu fikri dil modelleriyle ölçüyor. Önce o ölçünün ne olduğunu ve neden metin boyunca eşit olması beklendiğini görelim.

**Şaşırtıcılık (surprisal).** Bir **dil modeli**, bir kelime dizisinin ihtimalini veren bir dağılımdır. Her dil modeli, **özyinelemeli** (autoregressive) biçimde şöyle ayrıştırılabilir: u = u₁ ⋯ u_T dizisi için

p(u) = p(EOS | u) · ∏_{t=1}^{T} p(u_t | u_{<t}).   (1)

Burada EOS dizi sonu işaretidir. Bir birimin (burada kelimenin) **Shannon şaşırtıcılığı**, onun bağlam içindeki ihtimalinin negatif logaritmasıdır:

s(u_t) = −log p(u_t | u_{<t}).   (2)

Şaşırtıcılığın dil işleme kuramında önemli bir yeri vardır: **şaşırtıcılık kuramı** (surprisal theory; Hale 2001, Levy 2008), bir birimin şaşırtıcılığının, okuyanın ya da dinleyenin beklentisini yenilemek için ödediği bedeli ölçtüğünü söyler. Bu kuramın kilit görüşü şudur: dil modeli insanınkine yeterince yakınsa, **bilgi miktarı** ve **işleme zorluğu** diye iki ayrı şey, **tek bir ölçüyle** ölçülebilir.

**Düzgün Bilgi Yoğunluğu (UID).** İletişim, sınırlı kapasiteli gürültülü bir kanaldan işaret göndermeye benzetilebilir (Shannon 1948). Konuşan, kanalın kapasitesini **aşmadan** en çok bilgiyi göndermek ister. Eğer ortalama bilgi kapasiteyi aşarsa iletim hataya açık olur; kapasitenin altında kalırsa daha verimli bir ifade bulunabilirdi. En iyi usul, bilgiyi kanal kapasitesine mümkün olduğu kadar yakın, fakat dinleyeni yormayacak biçimde **düzgün dağıtmaktır**. Hipotez bu yüzden, şaşırtıcılığın bir konuşanın söyleyişi boyunca **mümkün olduğu kadar eşit** dağıldığını söyler (Fenk ve Fenk 1980; Genzel ve Charniak 2002; Jaeger ve Levy 2006; Meister ve arkadaşları 2021; Clark ve arkadaşları 2023). Hipotez katı uygulanırsa, her birim önceki bağlam verildiğinde aşağı yukarı aynı miktarda bilgi katar.

UID'ye tecrübî destek çoktur, fakat genellikle onun **yumuşak** (ihlâl edilebilir) hâline: hece düzeyinde (Bell ve arkadaşları 2003; Aylett ve Turk 2004, 2006), kelime düzeyinde (Meister, Clark), sözdizimi yapıları düzeyinde (Frank ve Jaeger 2008; Jaeger 2010), söylem bağlaçları düzeyinde (Torabi Asr ve Demberg 2012, 2015). Clark ve arkadaşları (2023) kelime sırasının UID için eniyilendiğini birçok dilde gösterdi.

**Bilgi eğrisi.** Fakat bir söylem içinde birimin bilgi miktarı **hiçbir zaman sabit çıkmaz**; bir şerit içinde dalgalanır. Yazarlar bu dalgalanmaya **bilgi eğrisi** (information contour) der (Şekil 1: İngilizce RST Söylem Ağaçlığı'ndan wsj_1111 belgesi; ham şaşırtıcılık, 5'lik yürüyen ortalama, paragraf/cümle/EDU sınırları ve modelin tahmini bir arada çizilmiş, çubukları okunamadı).

Bu dalgalanmaya iki bakış mümkündür: kuramca ilgisiz **gürültü** sayılabilir; veya UID'nin **tek kuvvet olmadığının** işareti. Yazarlar ikincisini savunur: konuşanlar ilgiyi tutmak, yazım gelenekleri ve ikna edici bir söylem kurmak gibi başka gayelere de sahiptir.

---

## 2. Arka plan: UID'nin zaafları ve alternatif görüşler (s. 2–3)

**Girizgâh.** Bir hipotez ancak zaafları sayılırsa ciddiye alınır. Yazarlar UID'nin neden eksik kaldığını iki yönden sayıyor: ölçülen eğrilerin bir bantta dalgalanması (tecrübî zaaf), ve UID'nin dilin başka baskılarını hesaba katmaması (kuramî zaaf). Bu iki zaaf, "yapılı bağlam" fikrinin kapısını açıyor.

**Tecrübî zaaflar.** Harf düzeyinde, kelime içindeki harflerin şaşırtıcılığı (Elman 1990), cümle içinde kelimelerin şaşırtıcılığı (Levy 2013; Futrell ve arkadaşları 2020) ve söylem yapısı içinde cümlelerin şaşırtıcılığı (Genzel ve Charniak 2003), şaşırtıcılık oranının **dil yapısına karşılık gelecek biçimde** dalgalandığını gösterdi. Meselâ kelime içinde harf şaşırtıcılığının tepeleri çoğu zaman **biçimbirim sınırlarına** denk gelir (Harris 1955; Elman 1990; Pimentel ve arkadaşları 2021); cümle içinde kelime şaşırtıcılığı **öbek sınırlarına** denk gelebilir (Jaeger ve Levy 2006). Fakat bütün bir söylemdeki tepe ve çukurlar daha az çalışılmıştır. Yazarlar bu dalgalanmaların **rastgele olmadığını**, bilişsel ve dilsel etkenlere bağlı olabileceğini öne sürer. Bilgi eğrisi öngörülebilir biçimde dalgalanıyorsa (meselâ **periyodik** bir yapı gösteriyorsa), bu UID'nin **güçlü** hâline karşı delil olurdu.

**Sabit Oran İlkesi (Constancy Rate Principle).** Genzel ve Charniak (2002), söylem seviyesinde bilgi eğrisini inceleyen kayda değer bir çalışmadır. İlke şunu söyler: beklenen şaşırtıcılık, yani bütün önceki birimler verildiğinde bir sonraki birimin dağılımının entropisi, söylem boyunca yaklaşık **sabit** kalır. Daha açık söylersek: yalnız **kendi cümlesi** bilindiğinde (bağlamdan kopuk) beklenen şaşırtıcılık söylem ilerledikçe **artar**; fakat **küresel bağlam** (şimdiye kadar söylenen her şey) da büyüdüğü için, bütün bağlam verildiğinde beklenen şaşırtıcılık **aynı kalır**. O günün araçları (n-gram dil modelleri ve ihtimalli sözdizimi çözümleyicileri) yüzünden yalnız birinci iddia (yerel bağlamda şaşırtıcılık artar) doğrulanabildi. Daha yeni çalışmalar, Transformer tabanlı modellerle küresel bağlamda şaşırtıcılığı da ölçtü ve **zayıf** bir sabitlik delili buldu; özellikle İngilizce dışı dillerde (Verma ve arkadaşları 2023) ve konuşma gibi başka iletişim türlerinde (Giulianelli ve Fernández 2021). Fakat sabitlik görülen yerde bile, Sabit Oran İlkesinin izah gücünün **ötesinde** bir bantta dalgalanma kalır.

**Diğer ilgili çalışmalar.** Konuşmanın ve yazmanın söylem yapısıyla kayıtlı değiştiği biliniyor. Önceki çalışmalar şaşırtıcılık oranlarını şunlarla ilişkilendirmiştir: paragraf sınırları (Genzel ve Charniak 2003); metindeki konu değişimleri (Qian ve Jaeger 2011); açık alanlı sohbet (Xu ve Reitter 2016; Maës ve arkadaşları 2022); amaç odaklı diyalogda göreve bağlı bağlam birimleri (Giulianelli ve arkadaşları 2021); çok kişili konuşmalarda dil dışı bağlam işaretleri (Doyle ve Frank 2015).

**Kuramî zaaflar.** UID, dilbilgisinin dışındaki dil içi baskıları hesaba katmaz. Bazı birimler, bilgi profillerine bakılmaksızın, söylem şartları, ikna gayeleri veya estetik tercihler yüzünden bir bağlamda **tercih edilmeyebilir**. Bunun iyi bir misali **kontur ilkeleri**dir (contour principles): özdeş parçaların (veya aynı özelliği taşıyan parçaların) arka arkaya gelmesine karşı kayıtlar; bu da birimlerin bilgi miktarını eşit olmaktan çıkarır. Aslında sesbilgisinde seslerin özelliklerinin düzgün olmayışını açıklamak için geliştirilen **Zorunlu Kontur İlkesi** (Obligatory Contour Principle; Leben 1973), kelimeler, paragraflar (Genzel ve Charniak 2003) ve söylem konuları (Xu ve Reitter 2016) gibi farklı ince ayrıntı derecelerinde bilgi miktarına da uygulanmıştır. Kontur benzeri ilkeler ayrıca güzel yazının izahında ve öğretilmesinde kullanılır (Kharkwal ve Muresan 2014; Snow ve arkadaşları 2015; Archer ve Jockers 2016). İlk bakışta UID'yi bu ilkelerle uzlaştırmak kolay görünmüyor.

**Eksik tarif.** Daha geniş bir zaaf, UID'nin **belirsiz tarifli** olmasıdır: bilgi mümkün olduğu kadar eşit dağıtılsın diyor ama hangi şaşırtıcılık oranlarının "eşit" sayılacağını, eşitliğin dilin diğer yapısal baskıları **kontrol edildikten sonra** mı yoksa **bağımsız** mı aranacağını, ve şaşırtıcılığın **hangi bağlam kavramı içinde** eşit kalacağını söylemez. Kelimelerde (Collins 2014; Meister ve arkadaşları 2021) ve söylemdeki cümlelerde (Giulianelli ve Fernández 2021) farklı eşitlik tarifleri denenmiş, bulgular özellikle **daha büyük iletişim birimleri** hesaba katıldığında **küresel eşitliğe** (şaşırtıcılık söylem boyunca ortalamaya yakın kalıyor) işaret etmiştir.

---

## 3. Hipotez: Yapılı Bağlam Hipotezi (s. 3–4)

**Girizgâh.** Şimdiye kadar bağlam, genellikle **ardışık** bir şey sayıldı: paragraflar peş peşe, konu bölümleri peş peşe, diyalog turları peş peşe. Yazarlar bunun yerine bağlamın **iç içe** (ağaç gibi) olduğunu düşünüyor. Bir cümle yalnız önceki cümleden sonra gelmez; bir paragrafın içinde, onun da bir bölümün içindedir. Hipotez, bu iç içeliğin bilgi eğrisinde iz bırakacağıdır.

**Hipotez 1 (Yapılı Bağlam Hipotezi).** Bir söylemin bilgi eğrisi, onu oluşturan söylem birimlerinin **hiyerarşik yapısı** tarafından (kısmen) belirlenir.

Yazarlar bunu şöyle açar: UID'nin taban eşitliğinin ötesindeki dalgalanma, söylemin **yapılı temsilleri** hesaba katılırsa en azından kısmen izah edilebilir. Yani teorilerimiz cümle seviyesinin ötesindeki hiyerarşik bağımlılıkları dikkate alırsa, söylemin bilgi oranını **öngörme güçleri artmalıdır**. Tecrübe, İngilizce ve İspanyolca metinlerde sınanır. İki ayrı söylem yapısı temsili kullanılır:

**3.1 Geleneksel nesir yapısı (prose structure).** Belgenin paragraflara, paragrafların cümlelere bölünmesidir. En temel birimler kelimelerdir. Bu şekilde yapılandırılmış belge, derinliği en çok **üç** olan **sığ bir ağaç** olarak görülebilir.

**3.2 Retorik Yapı Kuramı (Rhetorical Structure Theory, RST; Mann ve Thompson 1988).** Yüksek derecede hiyerarşik bir söylem çözümlemesi çerçevesidir; kısımlar arasındaki ilişkileri de tasnif eder. Temsil bir **ağaçtır** (Şekil 2: wsj_1111'deki bir cümlenin alt ağacı, ATTRIBUTION-ELABORATION-OBJECT-ATTRIBUTE-E örneği): yapraklar, genellikle **cümlecikler** olan metin parçalarıdır ve **temel söylem birimleri** (elementary discourse units, EDU) denir. İç düğümler, bitişik, temel olmayan birimlerin kapsadığı aralıklardır; bunlara **karmaşık söylem birimleri** (CDU) denir. Müellifler esas olarak ağacın hiyerarşik yapısıyla ilgilenir, fakat ağaç ek bilgi de taşır: bir düğüm, esas bilgiyi veriyorsa **çekirdek** (nucleus), yardımcı bir vazifesi varsa **uydu** (satellite) diye işaretlenir; düğümler ayrıca birimlerin **retorik ilişkileriyle** (SONUÇ, AÇIKLAMA gibi) etiketlenir. Bu çalışmada retorik ilişki etiketleri kullanılmadı (veri hazırlığı bölümüne bkz.).

---

## 4. Usul (s. 4–5)

**Girizgâh.** Bir hipotezi sınamak için iki şey lâzım: bir ölçü (bilgi eğrisinin kendisi) ve bir tahmin aracı (yapıdan eğriyi tahmin etmek). Yazarlar bilgi eğrisini **dört** biçimde ölçüyor ve yapıdan çıkardıkları **dört aile** değişkenle bunu öngörmeye çalışıyor. Aradaki farkı sayan, yapının **gerçekten bilgi taşıyıp taşımadığını** ortaya koyan, bir temel modelle kıyastır.

Amaç, bir metnin bilgi eğrisinin söylem temsilinden öngörülüp öngörülemeyeceğini ölçmektir. Modeller, bilgi miktarı ölçülerini (**bağımlı değişkenler**) bir dizi **öngörücüyle** (bağımsız değişkenler) tahmin eder; bazıları kolaylık için **taban öngörücü** (baseline), bazıları **bağımsız öngörücü** diye adlandırılır. Bütün değişkenlerin özeti Çizelge 1'de (Ek B).

**4.1 Bağımlı değişkenler.** Bilgi eğrisi dört tür ölçüyle ifade edilir (Ek D'de biçimsel tarif):

1. **Küresel birim başına şaşırtıcılık (belge şaşırtıcılığı).** Bir birimin, belgenin başından itibaren **bütün önceki bağlam** verilince şaşırtıcılığı.
2. **Yürüyen ortalama.** Bu şaşırtıcılığın 3, 5 ve 7 birimlik pencerelerde yürüyen ortalaması. (Pencere büyüdükçe çok yerel tepe ve çukurlar yumuşar.)
3. **Küresel şaşırtıcılık ile yerel bağlamdaki şaşırtıcılık arasındaki fark.** Bu, birimle önceki bağlamı arasındaki **noktasal karşılıklı bilgiye** (pointwise mutual information, PMI) eşittir. Yerel bağlam, mevcut cümleden veya mevcut EDU'dan başlayan bağlam sayılır (Genzel ve Charniak 2002; Giulianelli ve Fernández 2021). Küresel bağlam, belgede birimden önceki **her şeydir**.
4. Aynı PMI, **hiç yerel bağlam olmaksızın** da hesaplanır: bu, küresel şaşırtıcılık ile birimin **unigram** (tek başına) şaşırtıcılığı arasındaki farktır.

Bu ölçüler, söylemin **daha geniş bağlamının** o anki birimin bilgisini ne kadar değiştirdiğini ayrıntılı olarak ölçmek içindir.

**4.2 Taban öngörücüler.** Her tecrübede iki: birimin **uzunluğu** (harf sayısıyla) ve **bir önceki birimin şaşırtıcılığı**. Bunlar, doğrudan Yapılı Bağlam Hipotezine bağlı olmayan ama bilgi eğrisini öngörmesi beklenen niceliklerdir.

**4.3 Bağımsız öngörücüler.** Taban öngörücülerin ötesinde, iki ağaç türünden (nesir ağacı ve RST ağacı) türetilen **dört aile** öngörücü:

- **Göreli konum (relative position).** En ince birimin (belgenin kelimesi) bir üst yapısal biriminin başından uzaklığı, üst birimin uzunluğuna bölünmüş hâlde. Meselâ bir kelimenin, bulunduğu paragrafın başına uzaklığı, paragraftaki kelime sayısına bölünmüş.
- **En yakın sınır (nearest boundary).** Bir birimin, bir üst yapısal birimin **en yakın sınırına** (sol veya sağ) uzaklığı, yine üst birimin uzunluğuna bölünmüş. Bu öngörücüler, şaşırtıcılık ile birimin üst ve ata birimlerdeki konumu arasında **monoton olmayan** bir ilişki olup olmadığını sınamayı sağlar.
- **Hiyerarşik konum (hierarchical position).** Bir birimin, hiyerarşik yapıda **ebeveyni içindeki** göreli konumu; meselâ bir birimin cümle içindeki, veya bir paragrafın (birimi içeren) belge içindeki konumu. Bu öngörücüler, bağlam yapısının hangi seviyesinin şaşırtıcılığı en çok etkilediğini anlamayı sağlar.
- **Geçiş öngörücüleri (parsing transitions).** Nesir ve RST ağaçlarının **ayrıştırma bilgisini** kodlar. Ağaçların ikili hâle getirilmiş (binarize) biçimleri, bağlamdan bağımsız dilbilgileri için kullanılan yaygın ayrıştırma stratejileriyle (yukarıdan aşağıya, aşağıdan yukarıya, sol köşeden) gezilir ve yapraklar arasındaki **PUSH** (yığına koy) ve **POP** (yığından çıkar) hareketleri kaydedilir (Şekil 3; ayrıntı Ek C).

**4.4 Tahmin çerçevesi.** Farklı söylem temsillerinin öngörme gücünü ölçmek için, hem bağımsız hem taban öngörücüleri içeren bir **Bayesçi doğrusal regresör** (**hedef model**) ile yalnız taban öngörücülerini içeren (**taban model**) kıyaslanır. Her öngörücü seti için **5 katlı çapraz sınama**: dört katta sonsal dağılım tahmin edilir, beşincide sınanır. Regresör Pyro çerçevesiyle (Bingham ve arkadaşları 2019) **rastgele değişimli çıkarım** (stochastic variational inference; Hoffman ve arkadaşları 2013) kullanılarak, AutoNormal kılavuz, Adam eniyileyici (öğrenme oranı 0,03) ve kanıt alt sınırı (ELBO; Kingma ve Welling 2014) hedefiyle uydurulur. Sonra sınanan katta, Bayesçi sonsal altında **beklenen ortalama kare hata** (MSE) hesaplanır; bütün katların hataları toplanarak bütün veri için beklenen MSE tahmin edilir. Bir öngörücü setinin gücü, taban modelle hedef modelin beklenen MSE farkı olarak ölçülür: **ΔMSE**. Bir öngörücü grubunun ΔMSE'sinin istatistik bakımından anlamlı olup olmadığı, çapraz sınama sonuçlarıyla **eşleştirilmiş permütasyon testi** ile sınanır.

---

## 5. Veri (s. 5–6)

**Girizgâh.** Bir kuramın sınanması, veriye bağlıdır; bu veri ise **elle işaretlenmiş** söylem ağaçlarıdır. Mevcut en meşhur iki toplu ağaçlık kullanıldı.

- **İngilizce RST Söylem Ağaçlığı** (Carlson ve arkadaşları 2001; Carlson ve Marcu 2001): yalnız eğitim kısmı, **347 belge**, Wall Street Journal'dan.
- **İspanyolca RST Söylem Ağaçlığı** (da Cunha ve arkadaşları 2011): 9 alandan (gökbilim, matematik, hukuk gibi) **267 uzman metni**; ağaçlarında düğüm eksikliği olan 11 belge atıldı (256 belge kaldı).

**Ön işleme ve RST işaretlemesi.** Braud ve arkadaşlarını (2017) izleyerek: RST ağaçlarının parçası olmayan belge başlıkları atlandı; yazarların kodu ağaçları **sağa ikili** (right-binarize) hâle getirmek için kullanıldı. İlişki etiketlerinin uyumlaştırılması yapılmadı, çünkü deneylerde hiçbir retorik ilişki etiketi kullanılmadı.

**Nesir yapısı işaretlemesi.** İngilizce belgeler, Penn Treebank'taki düz metinlerle eşleştirilerek paragraf ve cümle sınırları bulundu (Marcus ve arkadaşları 1999). İspanyolca Ağaçlık paragraf sınırlarını doğrudan veriyor; cümle yapısı bir **metin–cümle ayırıcı** ile geri kazanıldı, gerektiğinde elle düzeltildi. Nesir ağaçları RST ağaçlarıyla uyumlu olsun diye NLTK (Bird ve arkadaşları 2009) ile sağa ikili hâle getirildi.

**Şaşırtıcılık tahmini.** İngilizcede sonraki-birim şaşırtıcılığı **NousResearch/Yarn-Llama-2-7b-64k** dil modeliyle hesaplandı (Peng ve arkadaşları 2024); seçim sebebi, **uzun bağlam penceresi** (64 bin) ile birlikte hesap bütçesine yetecek kadar **hafif** olmasıdır. İspanyolcada **LINCE Mistral 7B Instruct** modeli kullanıldı. (Bunlar sırasıyla ilk ve ikinci dil modeline ait müellif beyanlarıdır.)

**Hesap kaynağı (Ek A).** Gerçek şaşırtıcılık değerleri, 24 GB VRAM'li bir RTX 4090 ve 64 GB RAM ile **6 saatte**; tahmin deneyleri 10 GB VRAM'li bir RTX 3080 ve 32 GB RAM ile toplam **70 saatte** çıkarıldı.

---

## 6. Bulgular (s. 6–7)

**Girizgâh.** Yazarlar beş suâl soruyor ve bunlar yüzeyden derine sıralıdır: Q1–Q4, RST'nin yüzeyli öngörücülerinden derin öngörücülerine; Q5, RST ile geleneksel nesir yapısını kıyaslar. Her suale ΔMSE ile cevap verilir; ΔMSE ne kadar **büyükse** (negatif işaretli tablolarda mutlak değer olarak) öngörme gücü o kadar fazla demektir.

**Q1: Bilgi eğrisi, bir söylem birimi içindeki göreli konumdan öngörülebilir mi?** RST göreli konum öngörücüleriyle eğitilen modellerin ΔMSE'si çizildi (Şekil 4). Bu öngörücüleri modele koymak, sınanan veride taban modele göre **daha düşük hata** doğurdu (p < 0,001): yapılı bağlam, bir metnin bilgi eğrisini öngörmeye yardım eder. **Göreli konum**, İngilizcede bağımlı değişkenlerin hepsinde en iyi RST grubu (Şekil 4a; p < 0,001 diğer bütün gruplara karşı), İspanyolcada ikinci en iyisi (Şekil 4b; hiyerarşik konum hariç bütün gruplara karşı p < 0,001).

**Q2: Bir söylem birimi içindeki göreli konumun tesiri monoton değil mi?** Olası monoton olmayan tesiri hesaba katmak için, **en yakın sınıra göreli mesafe** içeren öngörücülerle modeller eğitildi (birimin sonuna yakın bilginin, ortada düşüş sonrası artması gibi veya birimin sınırlarına yakın daha düşük oran gibi durumları yakalar). Netice olarak ΔMSE hem İngilizcede hem İspanyolcada, göreli konum öngörücülerine göre taban modele **daha az** iyileşme verdi (p < 0,001). Yani bir birimin söylem birimi içindeki konumunun tesiri **monoton** modellenmeye daha uygundur.

**Q3: Yüksek mertebeli yapılardaki göreli konum, bilgi eğrisini öngörür mü?** Hiyerarşik söylem yapılarının izah gücünü ölçmek için, birimin hiyerarşik yapıdaki **ebeveyni içindeki göreli konumunu** öngörücü olarak içeren modeller kullanıldı. **Hiyerarşik konum**, incelenen bütün bağımlı değişkenlerin anlamlı öngörücüsüdür ve test edilen bütün öngörücü gruplarının ya **en iyisi ya da ikincisidir**. İngilizce veride, göreli konumdan ılımlı derecede daha az öngörücüdür (p < 0,001; Şekil 4a). İspanyolcada belge şaşırtıcılığının ve yürüyen ortalamasının **en güçlü** öngörücüsüdür (p < 0,001, diğer bütün öngörücülere karşı) ve PMI bağımlı değişkenlerinde göreli konumla **başabaş** (p > 0,001).

**Q4: Söylem ayrıştırma geçişleriyle kodlanan hiyerarşik yapı, bilgi eğrisini öngörmeye yardım eder mi?** Hiyerarşik yapıyı temsil etmenin başka bir yolu olarak, RST ağaç yapısını bileşen ayrıştırma algoritmalarıyla türeten öngörücüler kullanıldı (Ek C). ΔMSE her durumda negatif (yani taban modele göre öngörme gücü artıyor) olmakla beraber, **geçiş öngörücüleri**, göreli ve hiyerarşik konumdan **anlamlı olarak daha zayıf** öngörücülerdir (p < 0,001), hem İngilizcede hem İspanyolcada.

**Q5: Hangi söylem yapısı temsili bilgi eğrisini en iyi izah eder: RST mi nesir yapısı mı?** Şekil 5, bütün RST öngörücülerinin ve nesir yapısı (PS) benzerlerinin İngilizce veride bağımlı değişkenler üzerindeki ΔMSE'sini kıyaslar. İki model kuruldu: **RST all** ve **PS all** (her temsilden türetilen bütün öngörücüleri içeren). Belge şaşırtıcılığı ve 5'lik yürüyen ortalama için RST öngörücüleri, PS öngörücülerinden **daha iyidir** (p < 0,001). PMI (belge ve unigram), 3 ve 7'lik yürüyen ortalamalar için de benzer eğilim görülür (Şekil 7). Ayrıca yerel bağlama bağlı PMI değişkenlerinde **en güçlü öngörücü ailesi ile yerel bağlam arasında bir uyum** vardır: RST öngörücülerinin gücü **EDU'ya bağlı PMI** için daha yüksektir (p < 0,001), PS öngörücüleri ise **cümleye bağlı PMI** için daha iyidir (p < 0,001). Bulgular iki dilde tutarlıdır (İspanyolca için Şekil 6, Ek E).

**Özet.** Dil modelinden çıkarılan bilgi eğrileri, **söylem yapısına bağlılık** gösteriyor. Bu bağlılıklar hem geleneksel nesir yazmanın yapı birimleriyle hem de daha hiyerarşik söylem birimleriyle belirlenir. Fakat izah gücü, birimler arasındaki **retorik ilişkilerle** belirlenen daha ince ve daha yüksek mertebeli yapılarda **daha fazladır**.

---

## 7. Gelecek çalışma: UID'nin açıklamadığı beş sebep (s. 7–8)

**Girizgâh.** Yazarlar, model bilgi eğrisindeki dalgalanmanın **yalnız küçük bir kısmını** izah ettiğini açıkça yazıyor (Şekil 1'de yapılı bağlam, taban oran etrafındaki salınımları öngörmeye yardım eder; fakat sapmaların küçük bir kısmını hesaba katar). Dalgalanmanın geri kalanının izahı için, tecrübeyle henüz sınanmamış beş sezgi sıralıyorlar. Bunlar müellifin hükmü değil, **açık hipotezlerdir**.

1. **İlgiyi sürdürmek.** Yüksek şaşırtıcılık, dinleyenin dikkatini canlı tutabilir. Müzik sentezinde şaşırtıcılığı değiştirmenin dinleyicinin ilgisini etkilediği önerilmiştir (Kothinti ve arkadaşları 2020; Bjare ve arkadaşları 2024). Dile genişletilince Venkatraman ve arkadaşları (2023), toplam şaşırtıcılık sabit tutulduğunda bilgi yoğunluğunun **düzgün olmamasının** metin kalitesiyle bağlantılı olduğunu buldu.
2. **Anlamayı kolaylaştırmak.** Aşırı bilgi yoğun içerik anlamayı güçleştirebilir. Bu durumda **tekrar, yineleme ve özet** gibi düşük şaşırtıcılıklı içerik, söylemdeki stratejik yerlerde yeni bilgiyi pekiştirir ve karışıklığı azaltır. Fazlalık (redundancy), hata düzelten kodların önemli bir özelliğidir (Hamming 1950); tekrar, gürültülü kanal şartlarında (ikinci dil öğrenenlerin konuşmaları gibi) anlama için önemlidir (Cervantes ve Gainer 1992).
3. **Üretim kayıtları.** Tepe ve çukurlar yalnız dinleyen düşüncesiyle olmaz. Konuşanın cümle kurmak için harcayacağı gayret sınırlıdır; bu yüzden konuşmanın akışını sürdürmek için tekrarı kullanabilir (Giulianelli ve arkadaşları 2022) veya yeni, daha bilgili bir söz kurarken söz hakkını elinde tutmak için (Bergey ve DeDeo 2024).
4. **Estetik gelenekler.** Genel estetik ilkeler veya özel üslûp gelenekleri, şaşırtıcılığı kasten oynatabilir. Tekrar birçok söz sanatının (Harris 2017) ortak unsurudur; kafiye ve vezin gibi şiir araçları öngörülebilirliği artırır. Bütün bir anlatı seviyesinde, duygusal eğrilerin gelenekselleştiği veya birkaç **ilk örnek** (arketip) etrafında kümelendiği ileri sürülmüştür (Reagan ve arkadaşları 2016; Brown ve Tu 2020); bu fikir, bilgi miktarına genişletilmiş değildir (yazarların bilgisi kadarıyla).

Bu açıklamaların her biri yaygın ve cazip sezgilere dayanır, fakat UID hipotezinin kapsamı dışındadır. Daha mühimi, ilgi ve anlaşılırlık gibi özelliklerle işaretlenmiş farklı türlerden metinlerde şaşırtıcılık eğrilerine bakılarak sınanabilecek **tecrübî tahminler** yaparlar. Bundan sonra, şaşırtıcılık eğrisine bir söylemle ilişkilendirilebilecek **birçok zaman serisinden yalnız biri** olarak bakmak, ve bunların birbirleriyle **anlamlı biçimde ilişkili** olup olmadığını görmek gerekecek.

---

## 8. Netice, sınırlar (s. 8)

**Netice.** Kuramî katkı: UID'nin zaafları sayıldı ve bilgi eğrisinin söylem ağaçlarıyla (nesir ve RST) nasıl dalgalandığını öngören ilk hipotez, Yapılı Bağlam Hipotezi, ortaya konuldu. Tecrübî katkı: İngilizce ve İspanyolcada iki yapılı söylem temsili sınanarak bu hipoteze destek bulundu. Yazarlar bu çalışmayı, insan kültürlerinde gözlenen geniş söylem, metin ve yazım türü çeşitliliğini izah edecek kuramlar yolunda **bir adım** olarak görüyor.

**Sınırlar (yazarlarca).**

- **Yalnız iki dil:** İngilizce ve İspanyolca. Genişletmek için yazarlar Baskça (Iruskieta ve arkadaşları 2013, 2015), Brezilya Portekizcesi (Maziero ve arkadaşları 2015; Cardoso ve arkadaşları 2011; Collovini ve arkadaşları 2007; Pardo ve Seno 2005; Pardo ve Nunes 2003, 2004), Felemenkçe (Van Der Vliet ve arkadaşları 2011; Redeker ve arkadaşları 2012) ve Almanca (Stede 2004; Stede ve Neumann 2014; Bourgonje ve Stede 2020) için RST işaretli külliyat buldu; bunların da sınanması bir sonraki adımdır.
- **Yalnız doğrusal modeller** kullanıldı. Söylem sınırları ile şaşırtıcılık arasındaki ilişkinin monoton olup olmadığı sınansa da, ilişki **doğrusal olmayabilir**.
- **Kuramî tartışma her boyuttaki birim için geçerli olsa da, ölçülen ve tahmin edilen yalnız dil modelinin kelime-benzeri birimleri (token)** idi. Karakterler, sesbirimler, cümleler, tonlama öbekleri veya başka birimler hesaba katılırsa sonuçlar değişebilir.

**Etik beyan.** Yazarlar etik bir mesele öngörmedi.

---

## 9. Bu eserin modernliği ve yeniliği (3-I 325 EK sınaması; benim hükmüm)

**Modern mi?** Evet; Kasım 2024, bugün (Ekim 2026) iki yıllık. Kullandığı dil modelleri (Llama-2-7B-64k, Mistral-7B) 2023 modelleridir; bugünkü en güçlü modeller değildir.

**Yeni bir şey ortaya koyuyor mu?** Evet, fakat **ölçülü**. *Eski olan:* şaşırtıcılık kuramı (Hale 2001, Levy 2008), UID (Fenk ve Fenk 1980; Jaeger ve Levy 2006), Sabit Oran İlkesi (Genzel ve Charniak 2002), RST (1988). *Yeni olan:* (a) UID'nin zaaflarının **bu çerçevede** sayılıp bir hipotezle (Yapılı Bağlam) cevaplanması; (b) bilgi eğrisini **ağaç yapıdan öngörmek** ve **hangi derinliğin** (nesir mi, RST mi) daha iyi öngördüğünü ölçmek; (c) aynı ölçünün iki dilde tutması. Eser kendisi **ön delil** sunduğunu söyler (modeller doğrusaldır ve eğri dalgalanmasının yalnız küçük bir kısmı izah edilir). Bu bakımdan "tam bir kuram" değil, **iyi kurulmuş bir ilk adım**dır.

**Sayı veriyor mu?** Evet: ΔMSE, p-değerleri, katılan belge sayıları. Fakat şekillerdeki ΔMSE büyüklükleri metin katmanında yoktur; bu notta yalnız **sıralamalar** ve p-değerleri vardır.

---

## 10. Bize bağ (ÇIKARIM; müelliflerin sözü değildir, padişahın sözü de değildir, hüküm değildir, hiçbiri verimizde sınanmamıştır)

**Girizgâh.** Bu nottaki bütün anlatış müelliflerindir. Şimdi şu suali soruyoruz: Kur'ân'ın âyet ve kısım yapısında "ne zaman yoğun, ne zaman sakin" gibi bir **bilgi akışı** ölçüsü kurulabilir mi; ve bu ölçü kısım hudutlarını (3-I 319, 320) belirlemede yardım eder mi?

**Birinci bağ: ölçü hazır.** Eser bize **sayıya dökülebilir bir ölçü** verir: her birimin (kelime, âyet) dil modeli altındaki şaşırtıcılığı s(u) = −log p(u | bağlam). Bu bizim sorumuza **ilk defa** gelen sayılı ölçüdür (Roberts'ta ve Tsvilodub'da âyetin kendisine uygulanabilecek böyle bir ölçü yoktu). **Sınama fikri:** âyetler için şaşırtıcılık eğrisi çıkarıp, mevcut kısım hudutlarında (Fâtiha, Bakara 1–10) tepe ve çukurların hudutlarla ilişkisini ölçmek. **Şart:** Arapça bir dil modeli ve ağaç yapısı gerekir; ikisi de elimizde değil. **Sınanmadı.**

**İkinci bağ: yapı gerekli.** Eserin ana bulgusu, eğrinin **derin ağaç yapıyla** (RST) yüzey yapıdan (paragraf) daha iyi öngörüldüğüdür. Bizim ihtiyaç ağacı ve münâsebet hiperkenarları bir tür **söylem ağacı**dır; yani eserin ölçüsüne bizim ağaçla girmek mümkün olabilir. Bu bir tahmindir.

**Üçüncü bağ: sınır.** Yazarlar eğri dalgalanmasının **yalnız küçük bir kısmını** izah edebildiklerini söyler. Dolayısıyla "âyet sırası şaşırtıcılık hesabından çıkar" demek mümkün değildir; olsa olsa **bir kısım** tahmin edilir. Ayrıca eserin ölçüsü **dil modelinin ihtimalidir**; padişahın "insan ihtimalle konuşmuyor, kesin" hükmü (3-I 306) ile ilişkisi açık sualdir: şaşırtıcılık, konuşanın kararı değil, **okuyanın/dinleyenin beklentisinin** bir ölçüsüdür. Konuşan (yazar) için değil muhatap için bir ölçüdür.

**Dördüncü bağ: Kur'ân için dikkat.** Eserin hipotezleri (ilgiyi sürdürmek, anlamayı kolaylaştırmak, üretim kayıtları, estetik gelenekler) **beşerî yazar** için yazılmıştır. Kur'ân'a uygulanırsa bunlar murâd-ı ilâhî diye değil, **hikmet ihtimali** olarak (3-I 318 (4)) ve katiyet derecesiyle yazılır.

**Beşinci bağ: matematiğin cinsi.** Bu eserde **ihtimal, entropi, karşılıklı bilgi ve regresyon** vardır; yani sayısal bir matematik. Fakat bunlar **ölçü** matematiğidir; **neden bu sıra** suâline cevap veren bir **türetme** matematiği değildir. İkisi (Tsipidi'nin ölçüsü ve Roberts'ın sual yığını) yan yana konulabilir: Roberts yapıyı, Tsipidi yapının bilgi izini verir.
