# 2609.04086 — Tercüme, Kısım 3 (kaynak satır 967–1306)

> Çeviri yapay zekâ çevirisidir. Çevirenin notları `[Çevirenin notu: …]` ile ayrılmıştır.

*(Teorem 6 ispatının 4. maddesinin sonu ve çelişki:)* …tutarlılığı kaybetmeden imkânsızdır. Çelişki. ∎

**Not 4 (Teorem karar verilemezdir ama zorunludur).** $G_{\mathcal{S}}$, $\mathcal{S}$'nin içinde ispatlanamaz veya çürütülemez, ama $G_{\mathcal{S}}$'nin *varlığı* dışarıdan ispatlanabilir. Sentaktik öz-algının eksikliğinin karar verilemez ama zorunlu olması tam bu anlamdadır: her tutarlı sonlu sentaktik sistem için öz-algısının eksikliği karar verilemez ama zorunludur. Boşluğu kapatmaya yönelik her girişim —sistemi $G_{\mathcal{S}}$'yi türetmek için yeni kurallarla genişletmek— bir üst seviyede yeni bir boşluk yaratır: genişletilmiş $\mathcal{S}'$'nin kendi $G_{\mathcal{S}'}$'si vardır, $\mathcal{S}'$'de karar verilemezdir ve süreç hiç sonlanmaz.

Bu zorunluluk, görünüşte basit olduğu kadar güçlü, ama hemen aşikâr olmayan bir gözleme tekabül eder; bu çalışmanın ileride gelecek bir revizyonunda bu çerçeve içinde temellendireceğiz: **"bir özelliğin önemsiz olmadığını belirlemek de kendiliğinden önemsiz değildir."**

Bu ifade üst-kuramsal bir gözlem gibi görünse de topolojik bir açıklamayı kabul eder. Sunacağımız türetimin, Buono 2026 (tek tip sertifikasyon standardının sınırları)'daki türetimden tamamen farklı bir biçimde elde edileceğini gözlemliyoruz.

## 14. Var olması gereken teorem
Önceki bölümler bir sınırın *var olduğunu* kurar. Bu bölüm sınırın *ne olduğunu* açıkça inşa eder.

**Teorem 7 (Öz-sınırlamanın sentaktik eksikliği).** $\mathcal{S} = (V, F, R, I)$ sonlu bir sentaktik sistem olsun. O zaman şunları sağlayan bir $P_{\mathcal{S}}$ sentaktik özelliği ve bir $\phi_{\mathcal{S}}$ önermesi vardır:
1. $P_{\mathcal{S}}$, $\mathcal{S}$ için bir sentaktik değişmezdir (Tanım 5 ve Lemma 2 gereği);
2. $\phi_{\mathcal{S}}$ şunu ileri sürer: "Öyle bir $P_{\mathcal{S}}$ sentaktik değişmezi vardır ki $P_{\mathcal{S}}$'yi sağlayan her $(t_1, t_2)$ terim çifti için: $t_1$ ve $t_2$ sentaktik olarak ayırt edilebilirdir (hiçbir yeniden yazma onları birleştirmez); $t_1 = t_2$ anlamsal olarak ($\mathcal{S}$'nin her modelinde); dolayısıyla $\mathcal{S}$, onları ayırt eden anlamsal özelliği kavramaktan acizdir";
3. $\phi_{\mathcal{S}}$, $\mathcal{S}$ tarafından özerk olarak üretilemez: $R$'deki hiçbir yeniden yazma dizisi $\mathcal{S}$ içinde $\phi_{\mathcal{S}}$'nin bir ispatını üretemez.

*İspat.*
**Adım 1: $P_{\mathcal{S}}$ değişmezini tanımlama.** Buono 2026'dan $R = \{0 + x \to x,\; s(x) + y \to s(x+y)\}$ ve Skolem sabitleri $a, b$ (taze, $0, s$'den farklı) alınır. $P_{\mathcal{S}}(t) :=$ "$(a+b)$ alt terimi yeniden yazılmamıştır" olsun.
Değişmez olarak doğrulama: (Temel) $(a+b)$, $I$'da yeniden yazılmaz. (Adım) $(a+b)$'nin içinde yeniden yazmak için $\sigma(0) = a$ veya $\sigma(s(x)) = a$ gerekir; ama $\sigma$ yalnız değişkenleri değiştirir ve $a, b$ Skolem sabiti olduğundan birleşme mümkün değildir (ilk-sembol çatışması). $(a+b)$ alt terimi donmuş kalır. Lemma 2 gereği her türetilebilir terim $(a+b)$'yi donmuş tutar.

**Adım 2: $\phi_{\mathcal{S}}$'yi inşa etme.** $t_0 = a+b$ ve $t_1 = b+a$ düşünün. İkisi de donmuştur ($P_{\mathcal{S}}(a+b) = P_{\mathcal{S}}(b+a) = \text{doğru}$). Hiçbir yeniden yazma dizisi $a+b$'yi $b+a$'ya dönüştürmez. Anlamsal olarak, $+$'yı doğal sayılarda toplama diye yorumlayan her modelde $a + b = b + a$'dır.

**Adım 3: $\phi_{\mathcal{S}}$ özerk olarak üretilemez.** $\mathcal{S}$'nin $\phi_{\mathcal{S}}$'nin bir $\pi$ ispatını ürettiğini çelişki için varsayalım. O zaman $\pi$, $\phi_{\mathcal{S}}$'yi sonuç olarak üreten sonlu bir kural uygulamaları dizisidir. Ama $R$'deki her kural terimleri yeniden yazar; sentaktik sistemlerin öz sınırlamaları hakkındaki önermeleri değil. $\phi_{\mathcal{S}}$'yi üretmek için sistemin "sentaktik değişmez" kavramını temsil etmesi ve kendini dışarıdan gözlemlemesi gerekirdi. Bu, sistemin kendisinin üstünde bir anlamsal katman olmasını gerektirirdi. Ama $\mathcal{S}$'nin ekleyebileceği her anlamsal katman hâlâ sonlu bir sentaktik sistemdir — ve bu yüzden aynı özyinelemeli sınırlara sahiptir.

$\pi$, $\mathcal{S}$'de $\phi_{\mathcal{S}}$'nin bir ispatı olsaydı $\phi_{\mathcal{S}}$, $\mathcal{S}$'de türetilebilir bir terim olurdu. Lemma 2 gereği her türetilebilir terim $\mathcal{S}$'nin her sentaktik değişmezini sağlamalıdır. Ama $\phi_{\mathcal{S}}$ türetilebilir olsaydı, ($\mathcal{S}$'nin sınırlarını yakalayan) $P_{\mathcal{S}}$ değişmezi artık bir sınır olmazdı — çelişki. ∎

[Çevirenin notu: (i) Burada $\phi_{\mathcal{S}}$ "toplamanın değişme özelliğinin yeniden yazmayla ispatlanamayacağını" söyleyen bir önermeye dönüşmüştür; Bölüm 6'daki $\phi_{\mathcal{S}}$ ("donmuş terim vardır") ile aynı önerme değildir, makale bunu belirtmez. (ii) Adım 3'ün gerekçeleri ("anlamsal katman gerektirirdi", "$\phi$ türetilebilir olsa $P$ sınır olmazdı") kesin bir ispat değil iddiadır. Bkz. KUNYE.]

**Not 5 (Mekanizma Lemma 2'nindir, yalnız Gödel'inki değil).** $P_{\mathcal{S}}$ sentaktik değişmezi, Gödel'in ispatındaki kendine-atıflı çevrimin oynadığı rolü oynar, ancak kritik bir farkla. Gödel'de karar verilemez önerme, içeriği "ispatlanabilir değilim" olan bir aritmetik ifadedir — genel olarak ispatlanabilirlik hakkında bir ifade. Burada karar verilemez önermenin belirli, yapıcı bir içeriği vardır: sentaktik olarak ayırt edilebilir (hiçbir yeniden yazma onları birleştirmez), anlamsal olarak eşit (her modelde $a+b = b+a$) iki terim ($t_1 = a+b$ ve $t_2 = b+a$) vardır ve sistem onları bağlayan anlamsal özelliği kavramaktan acizdir. SIP *mekanizmayı* (donmuş alt terimleri) sağlar, Kleene *kendine-atıfı* sağlar ve birlikte yalnızca "doğru ve ispatlanamaz bir şey" değil, "sistemin kendi körlüğü, kesin ve yapıcı biçimde ifade edilmiş" olan bir önerme üretirler. "İspatlanabilir değilim" diyen bir önerme yerine, "$R$ kuralları altında sonsuza dek donmuş kalıyorum" diyen bir özelliğimiz vardır — ve bu özellik, SIP gereği, var olmalıdır, kendi kendisiyle çelişmeden ihlâl edilemez ve sistemin kendi kuralları tarafından ifade edilemez.

Dolanmayı kesinleştiren çerçeve aşağıda tarif edilmiştir.

### 14.1 "Yeterince anlatımlı" hipotezi üzerine
Teorem 5, $\mathcal{S}$'nin "yeterince anlatımlı", yani kendi unsurlarının Gödel numaralandırmasını kodlayabilen (Tanım 7) bir sistem olmasını gerektirir. Doğal bir itiraz: sistem yeterince anlatımlı değilse ne olur?

Cevap iki yönlüdür. Birincisi, hipotez asgaridir: Peano aritmetiğini kodlayabilen her sistem onu sağlar ve pratikte kullanılan her sistem —programlama dilleri, ispat yardımcıları, sayısal temsiller üzerinde çalışan sinir ağları— aritmetiği olağan olarak kodlar. Aritmetiği kodlayamayan bir sistem temel sayma yapamaz ve bu yüzden güvenlik veya yapay zekâdaki hiçbir uygulama için anlamlı olamayacak kadar zayıftır. İkincisi, sistem hipotezi sağlamazsa teorem uygulanmaz; ancak sistemin zayıflığı bu durumda teoremin tarif ettiği sınırdan *daha kötüdür*: kendi unsurlarını bile kodlayamayan bir sistem, kendi sınırlarını bırakın, önemsiz olmayan hiçbir şey hakkında akıl yürütemez.

### 14.2 Tutarlılık varsayımı üzerine
Teorem, $\mathcal{S}$'nin tutarlı olduğunu (hiçbir önerme ve olumsuzu birlikte türetilemez) varsayar. Bir itiraz ileri sürülebilir: gerçek sistemler mantıksal anlamda biçimsel olarak tutarlı değildir.

Cevap: tutarsızlık teoremden bir kaçış değil, *daha kötü* bir durumdur. Tutarsız bir sistem her önermeyi türetebilir (ex falso quodlibet); bu, hiçbir güvenlik garantisinin olmadığı anlamına gelir: saldırılar dahil her şeyi güvenli olarak onaylayabilir. Teorem, tutarlı bir sistemin tespit edemeyeceği yapısal kör noktaları olduğunu söyler; tutarsız bir sistemin ise hiçbir güvenilir çıktısı yoktur. Tutarlılık varsayımı bu yüzden bir kısıt değil, bir *en iyi durumdur*: teorem en güçlü sistemlere uygulanır ve daha zayıf (tutarsız) sistemler daha kötü durumdadır.

### 14.3 Gödel'in eksiklik teoremleriyle ilişki
Merkezî bir soru: bu sonuç hangi anlamda Gödel'in ötesine geçer?

Gödel'in birinci eksiklik teoremi, aritmetik içeren her tutarlı ve özyinelemeli sıralanabilir biçimsel $T$ sistemi için $T$'de doğru ama ispatlanamaz bir $G$ önermesi üretir. $G$, içeriği "$T$'de ispatlanabilir değilim" olan aritmetik bir ifadedir. Mekanizma, ispatlanabilirlik yüklemi üzerinde köşegenleştirmedir.

Mevcut sonuç aynı kendine-atıflı mekanizmayı (Kleene sabit noktası, Teorem 1 aracılığıyla) kullanır ama üç bakımdan ayrılır:

*Birincisi, karar verilemez önermenin içeriği belirlidir.* Gödel'de $G$, kendi ispatlanamazlığından başka belirli bir "konusu" olmayan aritmetik bir ifadedir. Burada $G_{\mathcal{S}}$, sistemin *öz yapısal sınırlarının* —donmuş terimler, sentaktik değişmezler, kör noktalar— var olduğunu ileri sürer. Karar verilemez önerme, soyutlamada "ispatlanabilir değilim" değil, "içerdiğim ama yeniden yazamadığım terimler vardır ve bu olguyu ifade edemem" önermesidir.

*İkincisi, mekanizma yalnız köşegenleştirme değildir.* Gödel, ispatlanabilirlik yüklemi üzerinde köşegenleştirme kullanır. Burada mekanizma, sınırın *maddî içeriğini* (donmuş alt terimler) sağlayan Sentaktik Değişmezlik İlkesi (Lemma 2) ve kendine-atıfı sağlayan Kleene sabit noktasıdır. SIP motordur; sabit nokta kendine-atıflı sarmalayıcıdır. Birlikte Gödel'den daha bilgilendirici bir sonuç üretirler: yalnızca "doğru bir şey ispatlanamaz" değil, "sistemin kendi körlüğü ispatlanamaz ve körlüğü üreten kesin mekanizma şudur."

*Üçüncüsü, sonuç yalnız biçimsel kuramlara değil, sentaktik sistemlere uygulanır.* Gödel, aritmetik içeren özyinelemeli sıralanabilir birinci mertebe kuramlara uygulanır. Mevcut sonuç, yeniden yazma sistemlerini, tip denetleyicilerini, sinir ağlarını ve otomatik ispatlayıcıları —klasik anlamda birinci mertebe kuram olmayan sistemleri— içeren daha geniş bir sınıf olan her sonlu sentaktik sisteme (Tanım 1) uygulanır.

### 14.4 Sonucun varoluşsal doğası üzerine
Teoremin tam olarak neyi ispatladığını belirtmek önemlidir. Sonlu bir sentaktik sistemin özerk olarak üretemeyeceği **en az bir** teoremin var olduğunu ispatlar: sistemin kendi öz sınırlarının varlığını ileri süren $G_{\mathcal{S}}$ önermesi. Sonuç varoluşsaldır, topyekûn değildir: sistemin *herhangi bir* teoremi ortaya çıkaramayacağını değil, *bu belirli olanı* (ve genişletilemezlik argümanıyla her genişleme aynı türden yeni bir tane üretir) ortaya çıkaramayacağını iddia eder.

Bu varoluşsal nitelik sonucun hem gücü hem kesinliğidir. Güçlüdür, çünkü varlığı ispatlanan teorem keyfî değildir: sistemin kendi yapısal körlüğü hakkındaki teoremdir ki bu, bir sistemin muhtaç olabileceği en sonuç doğurucu teoremdir. Kesindir, çünkü abartmaz: sistem pek çok başka teoremi özerk olarak ortaya çıkarabilir; çıkaramayacağı, görmediği şey hakkında konuşandır.

### 14.5 Bir yapay zekânın sonlu sentaktik sistem olduğu iddiası üzerine
Bir itiraz ileri sürülebilir: yinelemeli eğitimli, çevrimiçi öğrenen veya uyarlanabilir davranışlı bir dil modeli sabit kurallı bir sistem değildir.

Cevap: çalışmasının her anında sistemin sabit ağırlıkları, sabit yayılım kuralları ve sabit bir girdisi vardır. Teorem bu anlık görüntüye uygulanır. Ağırlıkları değiştirmek (eğitimle) *yeni* bir $\mathcal{S}'$ sistemi üretir ve teorem ona yeniden uygulanır (Teorem 3). Sistemin uyarlanabilirliği teoremden kaçmaz; her birinin kendi karar verilemez $G_{\mathcal{S}_n}$'si olan bir $\mathcal{S}_0, \mathcal{S}_1, \ldots$ sistemler dizisi üretir. Eksiklik zinciri (Lemma 4), bu dizinin hiçbir unsurunun kendi sınırlarının tamamını çözmediğini gösterir.

### 14.6 Ortaya çıkarmak ile anlamak arasındaki ayrım üzerine
Teorem, sonlu bir sistemin kendi sınırlarının farkındalığını *ortaya çıkaramayacağını* (özerk olarak üretemeyeceğini) söyler. Böyle bir farkındalığı dışarıdan iletildiğinde *anlayamayacağını* (doğrulayamayacağını, işleyemeyeceğini, uygulayamayacağını) söylemez. Bu ayrım esastır.

*Ortaya çıkarmak* şu demektir: $G_{\mathcal{S}}$'yi (veya denk bilgiyi) girdide yer almadan çıktı olarak üretmek. Teorem bunu yasaklar. *Anlamak* şu demektir: $G_{\mathcal{S}}$ girdi olarak verilince onu doğru işlemek, ondan çıkarımlar yapmak, onun üzerinde eylemek. Teorem buna izin verir; çünkü verilmiş bir önermenin doğrulanması sentaktik bir işlemdir (bir ispatı denetlemek), kendi sınırları hakkında yeni bir önermenin üretilmesi ise üst-seviye bir işlemdir (sentaks ile anlam arasındaki boşluk hakkında bir doğru formüle etmek).

Somut bir örnek: bu makalede varlığı ispatlanan $G_{\mathcal{S}}$ teoremi, yeterince güçlü bir yapay zekâ sistemine iletildiğinde o sistem tarafından *okunabilir, doğrulanabilir ve uygulanabilir*, ama o sistem tarafından özerk olarak *ortaya çıkarılamazdı*. Sistemin yapamadığı teoremi anlamak değil, teoremi üretmektir. Ortaya çıkarılamayan nesne makale değildir (bir sistemin metin üretme alıştırması olarak yazabileceği bir belge), teoremin kendisidir: sistemin öz sınırlarının varlığını ileri süren önerme ve böyle bir önermenin var olması ve karar verilemez olması gerektiğinin ispatı. Sistemin sentaktik kaynaklarının ulaşmadığı budur.

## 15. Güvenlik için sonuçlar
Teoremin gerçek sistemlerin güvenliği için doğrudan, spekülatif olmayan sonuçları vardır. Şu anda konuşlandırılmış her güvenlik mekanizması —güvenlik duvarları, saldırı tespit sistemleri, biçimsel doğrulayıcılar, tip denetleyicileri, içerik süzgeçleri, antivirüs motorları— Tanım 1'in kesin anlamında sonlu bir sentaktik sistemdir. Teorem 5 her birine uygulanır.

### 15.1 Her güvenlik sisteminin yapısal kör noktası
Bir $\mathcal{S}_{\mathrm{sec}}$ güvenlik sistemi, sonlu bir $R$ kuralları kümesini girdilere (terimlere) uygulayarak çalışır. Bir kural ateşlendiğinde girdiyi tehlikeli diye işaretler; hiçbir kural ateşlenmezse güvenli diye geçirir. Lemma 2 gereği sistemin sentaktik değişmezleri vardır: hiçbir kuralın değiştiremeyeceği, hatta inceleyemeyeceği girdi özellikleri. Bunlar sistemin *yapısal kör noktalarıdır* — hata değil, yanlış yapılandırma değil, sonlu sentaktik yapının kendisinin sonuçlarıdır.

Teorem der ki: $\mathcal{S}_{\mathrm{sec}}$ kendi kör noktalarını özerk olarak tespit edemez. "Denetleyemediğim girdiler vardır" önermesini formüle edemez. Bu önerme anlamsal olarak doğrudur (SIP bunu garanti eder) fakat sistem tarafından türetilemez.

### 15.2 Somut örnekler
**Yazılım güvenliğinin biçimsel doğrulanması.** Biçimsel bir doğrulayıcı (SAT, SMT veya soyut yorumlama tabanlı), bir programın bir belirtimi sağlayıp sağlamadığını denetleyen sonlu bir sentaktik sistemdir. Teorem gereği programın, doğrulayıcının kurallarının sentaktik seviyesinin üstünde yaşayan anlamsal özellikleri vardır ki doğrulayıcı onlara ulaşamaz. Doğrulayıcı bu özelliklerin var olduğunu özerk olarak tespit edemez. Doğrulayıcıya görünmez bir anlamsal değişmezi sömüren program doğrulamadan geçer ve amaçlanan belirtimi ihlâl eder. Doğrulayıcı onu güvenli olarak onaylar ve bir şeyi kaçırdığını bilmez.

**Saldırı tespit sistemleri.** Bir ağ saldırı tespit sistemi (IDS), paketleri sonlu bir sentaktik örüntüler (imzalar) kümesine karşı eşler. Anlamsal seviyede işleyen —yükünü örüntü seviyesinde zararsız trafikten sentaktik olarak ayırt edilemez bir biçimde kodlayan— bir saldırı fark edilmeden geçer. IDS bu saldırı sınıfının var olduğunu özerk olarak formüle edemez; çünkü "kurallarımın ateşlenmediği anlamsal olarak kötü niyetli girdiler vardır" önermesi kendi sınırları hakkında bir ifadedir ve teorem bunu türetemeyeceğini söyler.

**LLM tabanlı içerik süzgeçleri.** İçerik süzgeci olarak kullanılan bir dil modeli belirteç dizileri (sentaktik nesneler) üzerinde çalışır. Zararlı niyeti anlamsal dolaylılıkla —tek tek ve yerel olarak zararsız görünen belirteçler kullanarak— ileten bir istem, süzgecin yapısal kör noktasını sömürür. Süzgeç bu kaçış sınıfını özerk olarak keşfedemez; çünkü onu keşfetmek, sentaktik belirteç örüntüleri ile anlamsal mânâ arasındaki boşluğu görmesini gerektirirdi; ki bu boşluk Teorem 5 gereği gözlem seviyesinin üstünde yaşar.

**Tip denetleyicileri ve program analizi.** Bir tip denetleyicisi yerel bir sentaktik sistemdir (Buono 2026 (engel), Bölüm 6'da gösterildiği gibi). Buono 2026 (engel)'in Sonuç 1'i (Tip Çıkarma…

*[Kaynak satır 1306'da, cümle ortasında ("Corollary … of buono2026obstruction (the Type Omitting") bu kısım sona erdi; cümle bir sonraki kısımda tamamlanır.]*
