# 2609.04086 — Tercüme, Kısım 4 (kaynak satır 1306–1645)

> Çeviri yapay zekâ çevirisidir. Çevirenin notları `[Çevirenin notu: …]` ile ayrılmıştır.

*(Önceki cümlenin devamı, Bölüm 15.2 "Tip denetleyicileri ve program analizi":)* …Sonuç 1'i (Tip Çıkarma Teoremi, engelin bir örneği olarak), tip denetleyicisinin iki ispat teriminin dışsal (extensional) eşitliğini yalnız sentaktik yapıdan belirleyemeyeceğini söyler. Güvenlik için: tip açısından güvenli (tip denetleyicisinden geçen) bir program, yine de istenmeyen dışsal özelliklere sahip bir fonksiyonu hesaplayabilir. Tip denetleyicisi bu boşluğu özerk olarak tespit edemez.

**Kriptografik protokol doğrulaması.** Bir protokol doğrulayıcı (ör. ProVerif, Tamarin), sembolik yürütmeyle saldırı arayan sonlu bir sentaktik sistemdir. Teorem, protokolün sembolik biçiminden çok matematiksel yapısının özelliklerini sömüren anlamsal saldırı sınıflarının —doğrulayıcının kurallarının ulaşamadığı saldırıların— var olduğunu ima eder. Doğrulayıcı protokolü güvenli diye onaylar ve onayının yapısal boşlukları olduğunu özerk olarak belirleyemez.

### 15.3 Güvenlik sonucu, kesin biçimde ifade edilmiş
Sonuç bu sistemlerin "kötü" olduğu veya "değiştirilmesi gerektiği" değildir. Güvenlik garantilerinin sistemlerin kendilerinin tespit edemediği yapısal sınırları olduğudur. Bu sınırlar arızî (daha fazla kural veya daha fazla hesaplama eklenerek giderilebilir) değil, yapısaldır (sistemin sonlu sentaktik doğasına içkindir).

Pratik çıkarım şudur: herhangi bir sonlu sentaktik sistemin güvenliği *daha yüksek bir gözlem seviyesinde dışsal doğrulama* gerektirir: sistemin göremediğini gören bir doğrulayıcı. Hiçbir içsel iyileştirme —daha çok kural, daha çok örüntü, daha çok parametre— boşluğu kapatmaz; çünkü boşluk hesaplamalı değil, gözlemseldir.

Bu spekülatif bir iddia değildir. Teorem 5'in doğrudan sonucudur: sistemin kör noktaları vardır (SIP gereği), onları tespit edemez ($G_{\mathcal{S}}$'nin karar verilemezliği gereği) ve sistemi genişletmek yeni kör noktalar yaratır (genişletilemezlik teoremi gereği). Tek ileri yol gözlem seviyesini değiştirmektir; bir sonraki bölümün konusu budur.

## 16. Sınırın nasıl aşılacağı: gözlemsel çerçeve
Teorem, sonlu bir sentaktik $\mathcal{S}$ sisteminin kendi sınırları hakkında en az bir teoremler sınıfını özerk olarak ortaya çıkaramayacağını kurar. Engel hesaplamalı değildir (sistemin ne kadar hesaplama gücü olduğuna bağlı değildir), *gözlemseldir*: sistem, görmesi gereken bilgiyi içermeyen bir seviyede işler.

Bu engeli anlamanın ve aşmanın kesin çerçevesi, Buono 2026 (çerçeve)'de tanıtılan ve Buono 2026 (gözlemci)'de geliştirilen gözlemsel hiyerarşidir.

## 17. İleri yol
Teorem, sınırın her yönde mutlak olduğunu söylemez. Sınırın *mevcut gözlem seviyesinde* mutlak olduğunu söyler. Gözlemsel hiyerarşi, "seviye değiştirmenin" ne demek olduğu için kesin bir dil sağlar: gözlemci fonksiyonu $O$'yu değiştirmek, sisteme mevcut yeniden yazma kurallarının ulaşmadığı anlamsal seviyenin bir parçasına erişim vermek demektir.

Somut olarak, bir $\mathcal{S}_{\mathrm{AI}}$ yapay zekâ sistemi için:
- Mevcut sistem $O_{\mathcal{S}_{\mathrm{AI}}} \prec O_\top$ olarak işler: belirteçleri, etkinleşmeleri, sentaktik örüntüleri görür, kendi hesaplamasının anlamsal özelliklerini görmez.
- Teorem, aynı gözlem seviyesinde hiçbir miktarda ek eğitim, parametre veya hesaplamanın kendi sınırlarının özerk farkındalığını üretmeyeceğini söyler.
- Ancak gözlemciyi değiştiren dışsal bir müdahale —örneğin sisteme kendi türetim uzayının bir üst-temsiline erişim vermek veya onu daha yüksek bir gözlem seviyesinde çalışan dışsal bir doğrulayıcıyla eşleştirmek— prensipte eksik bilgiyi sağlayabilir.
- Hangi $O'$ gözlemcisinin yeterli olduğunun ve böyle bir gözlemcinin fiziksel bir sistemin kısıtları içinde gerçeklenip gerçeklenemeyeceğinin kesin karakterizasyonu, programın merkezî açık sorusudur.

Buono 2026 (çerçeve, gözlemci)'nin gözlemsel çerçevesi bu soruyu kesin biçimde formüle etmek için matematiksel dili sağlar ve $\mathbf{P}_{O} = \mathbf{NP}_{O} \subsetneq \mathbf{P}$ yapısal çöküşü, gözlemsel eksenin gerçek olduğuna, hesaplamalı varsayımlardan bağımsız ve biçimsel analize açık olduğuna dair ilk koşulsuz kanıtı sağlar.

## 18. Alternatif yol: engel teoremi yoluyla sonuç
Bu makalenin ana sonucu (Teorem 5) Sentaktik Değişmezlik İlkesi'ne (Lemma 2) dayanır. Bu bölüm, aynı sonucun kesinlikle daha genel bir yoldan —Buono 2026 (engel)'in Yerel Sentaktik Engel teoremi— elde edilebileceğini gösterir. Engel teoremi SIP'i süperpozisyon kalkülüsünden keyfî yerel sentaktik sistemlere genelleştirir ve SIP'in tek başına sağlamadığı nicel bir boyut (türetim uzunluğu alt sınırları) ekler.

Türetim her adım için açık saikle adım adım sunulur.

### 18.1 Adım 1: sistem, yerel bir sentaktik sistem olarak
Sonlu bir $\mathcal{S} = (V, F, R, I)$ sentaktik sistemi (Tanım 1), Buono 2026 (engel) Tanım 3.1 anlamında yerel bir sentaktik sistemdir: her $l \to r \in R$ kuralı sabit bir derinlikte sonlu bir örüntüyü (sol taraf $l$) inceler; bu, bir yerellik yarıçapı $r_0$ tanımlar. Somut $R = \{0 + x \to x,\; s(x) + y \to s(x+y)\}$ durumu için yerellik yarıçapı $r_0 = 1$'dir: her kural yalnızca $+$'nın ilk argümanının en dıştaki fonksiyon sembolünü inceler.

### 18.2 Adım 2: korunan konumlar
$\Sigma$'ya göre taze (hiçbir kuralın hiçbir sol tarafında görünmeyen) $a, b$ Skolem sabitlerini ekleyin. $a$ ve $b$'nin göründüğü konumlar, Buono 2026 (engel) Tanım 3.5 anlamında korunur: o konumlarda hiçbir kural ateşlenmez (ilk-sembol çatışması: $a$ ne $0$ ile ne $s(\cdot)$ ile birleşir) ve hiçbir kural $a$ veya $b$'nin içinde yeniden yazmaz (iç yapısız sabitlerdir).

### 18.3 Adım 3: korunan kümeye çıpalı sentaktik değişmez
$\mathrm{Inv}(t) :=$ "$a$'nın her geçişi bir $a + u$ alt teriminin içindedir ve $b$'nin her geçişi bir $b + v$ alt teriminin içindedir" özelliği, Buono 2026 (engel) Tanım 3.8 anlamında $\mathcal{F}_{\mathrm{prot}}$'a çıpalı bir $\mathcal{S}$ sentaktik değişmezidir. Beş şartı sağlar: yerel denetlenebilirlik ($a$ ve $b$'nin hemen bağlamına bağlıdır); ilkleme (ilk cümlecik $a + b \neq b + a$'da geçerlidir); korunum (hiçbir kural $a + b$ veya $b + a$'yı değiştirmez, korumadan ötürü); çıpalama (herhangi bir ihlâl korunan konumda yeniden yazmayı gerektirirdi); tutarlılık ($a$ ve $b$ kalıcı olarak ayrı kaldığı için hiçbir türetilebilir literal eşitlenmiş konumlarda $a(\cdot) = b(\cdot)$ biçiminde değildir).

### 18.4 Adım 4: engel teoreminin Durum 1'i (imkânsızlık)
Buono 2026 (engel) Teorem 4.1, Durum 1'e göre: $\mathcal{S}$'deki hiçbir türetim $a + b = b + a$'yı ispatlamaz. İspat SIP'inkiyle aynı yapıdadır ama daha genel bir çerçevededir: $\mathrm{Inv}$ değişmezi her türetilebilir cümlecikte tümevarımla geçerlidir; $a + b = b + a$ diyen bir cümlecik, tutarlılık şartını ihlâl ederdi ($a$ ve $b$ başlı alt terimleri değişmezce kalıcı olarak ayrı tutulan konumlarda eşitlerdi); çelişki.

Bu, Tanım 9'daki $\phi_{\mathcal{S}}$'yi verir: $\mathcal{S}$'nin eşitleyemediği, sentaktik olarak ayrılmış, anlamsal olarak denk terimler vardır.

### 18.5 Adım 5: $\phi_{\mathcal{S}}$'den $G_{\mathcal{S}}$'ye (değişmeden)
Argümanın geri kalanı (Gödel numaralandırması, köşegen lemması, kendine-atıflı $G_{\mathcal{S}}$, Durum 1–3 ile karar verilemezlik, genişletilemezlik, evrensellik, çürütülemezlik) Bölüm 7–13'teki gibi aynen yürür; çünkü yalnız $\phi_{\mathcal{S}}$'nin varlığına ve anlamsal doğruluğuna bağlıdır, onu kurmak için kullanılan özel araca değil.

### 18.6 Adım 6: engel teoreminin Durum 2'si (nicel alt sınır)
Engel teoremi, SIP'in tek başına sağlamadığı ek bir sonuç sağlar: engeli aşmaya çalışan herhangi bir yerel genişleme üzerinde nicel bir alt sınır.

Buono 2026 (engel) Teorem 4.1, Durum 2'ye göre: $\mathcal{S}$'nin herhangi bir yerel $\mathcal{S}'$ genişlemesi ($\mathbb{N}$'ye göre sağlam ve aynı yerellik yarıçaplı), $n$-aygıtlı örnekler ailesinde $a + b = b + a$'yı ispatlamak için $\Omega(n)$ uzunlukta türetimler ve cümlecik-başına-konfigürasyon kodlaması altında $\Omega(2^n)$ gerektirir.

Bu, genişletilemezlik teoremini (Teorem 3) kesin bir biçimde güçlendirir: her $\mathcal{S}'$ genişlemesinin yalnız kendi karar verilemez $G_{\mathcal{S}'}$'sine sahip olması değil, engele yaklaşmanın *yapısal bedelinin* de örneğin karmaşıklığıyla en azından doğrusal (ve potansiyel olarak üstel) büyümesi. Engel yalnız mevcut değil, *niceliksel olarak yaklaşması zordur*: kural eklemek bedeli azaltmaz, çünkü bedel hesaplamalı değil gözlemseldir.

### 18.7 Özet: engel yolu ne ekler
Engel teoremi yolu aynı niteliksel sonuca (bir $G_{\mathcal{S}}$'nin varlığı, karar verilemezlik, genişletilemezlik) varır ama üç şey ekler:

*Genellik.* Engel teoremi yalnız süperpozisyon kalkülüsüne değil, her yerel sentaktik sisteme uygulanır. Bu, öz-sınırlama sonucunun alanını sonlu yerellik yarıçaplı her sisteme genişletir.

*Nicel genişletilemezlik.* Durum 2'nin alt sınırı, engeli aşmaya çalışmanın bedelinin kesin bir ölçüsünü verir. Genişletilemezlik yalnız "yeni bir $G$ doğar" değil, "eski $G$'ye ulaşmak $\Omega(n)$ veya $\Omega(2^n)$ adım tutar"dır.

*Gözlemsel yorum.* Engel teoremi sistemi yerellik yarıçapı $r_0$ olan kısıtlı bir $O_{\mathcal{S}}$ gözlemcisi olarak belirler (Buono 2026 (engel), Not 7.2). Öz-sınırlama bu durumda gözlemsel çöküşün doğrudan sonucudur: sistem gözlem seviyesinin üstünde yaşayanı göremez ve hiçbir miktarda yerel hesaplama boşluğu kapatmaz.

## 19. Asgarî yol: yalnız sonluluktan sonuç
Önceki bölümler öz-sınırlama teoremini Sentaktik Değişmezlik İlkesi (Bölüm 4–14) ve alternatif olarak Yerel Sentaktik Engel teoremi (Bölüm 18) yoluyla türetir. İkisi de mekanizmayı ve engelin bedelini aydınlatan somut araçlar kullanır (donmuş Skolem sabitleri, korunan konumlar, korunan kümelere çıpalı sentaktik değişmezler).

Bu bölüm, ne SIP'in, ne engel teoreminin, ne Skolem sabitlerinin, ne de herhangi bir standart dışı aygıtın sonuç için *mantıksal olarak gerekli* olmadığını gösterir. Teorem yalnız üç bileşenden çıkar: $R$'nin sonluluğu, türetim uzunluğu üzerinden standart tümevarım ve köşegen lemması. Her adım açıkça tartışılır.

### 19.1 Adım 1: $R$'nin sonluluğu yeniden yazılamayan terimlerin varlığını gerektirir
$\mathcal{S} = (V, F, R, I)$ sonlu bir sentaktik sistem olsun (Tanım 1). $R$ sonludur: $R = \{l_1 \to r_1, \ldots, l_m \to r_m\}$ diyelim. Her sol taraf $l_i$, belirli bir en dıştaki fonksiyon sembolü $\mathrm{head}(l_i) \in F$ olan sonlu bir terimdir. Şunu tanımlayın:
$$H := \{\mathrm{head}(l_1), \ldots, \mathrm{head}(l_m)\} \subseteq F.$$
$H$ sonludur (en çok $m$ unsuru vardır). $\mathcal{S}$ yeterince anlatımlı olduğundan (kendi Gödel numaralandırmasını kodlayabilir), $H$'de olmayan sembollerden kurulmuş terimleri temsil edebilir. $\mathcal{S}$'nin dilinde $c \notin H$ olan herhangi bir fonksiyon sembolü $c$ olsun (böyle bir sembol vardır: $\mathcal{S}$ Gödel numaralandırması aracılığıyla keyfî sayıda sabiti kodlayabilir ve $H$ sonludur). $t_c$, en dış sembolü $c$ olan herhangi bir terim olsun.

$R$'deki hiçbir kural $t_c$'nin kökünde uygulanabilir değildir: uygulanabilirlik $t_c$'nin kökte bir $l_i$ ile birleşmesini gerektirir; bu, $\mathrm{head}(t_c) = \mathrm{head}(l_i)$ olmasını gerektirir; ama $\mathrm{head}(t_c) = c \notin H$. Bu bir ilk-sembol çatışmasıdır ve hiçbir ikame onu çözmez.

Ek olarak $c$ bir sabitse (aritisi $0$), $t_c = c$'nin iç yapısı yoktur ve bu yüzden $t_c$'nin içinde de hiçbir konumda hiçbir kural uygulanamaz. Bu durumda $t_c$, $R$'deki hiçbir kural tarafından hiçbir konumda yeniden yazılamaz.

Böyle bir $t_c$'nin varlığı, $R$'nin sonluluğu ($H$'yi sonlu yapar) ve $\mathcal{S}$'nin anlatım gücü ($H$ dışında semboller sağlar) tarafından garanti edilir. Skolem sabiti gerekmez: $c$ basitçe başı hiçbir sol tarafla eşleşmeyen bir semboldür.

### 19.2 Adım 2: yeniden yazılamazlığın kalıcılığı
$t_c$ bir türetimin $0$. adımında yeniden yazılamazsa, sonraki her adımda da yeniden yazılamaz kalır. Argüman türetim uzunluğu $n$ üzerinden tümevarımdır.

*Temel durum ($n = 0$).* Adım 1 gereği $R$'deki hiçbir kural $t_c$'ye uygulanabilir değildir.

*Tümevarım adımı ($n \to n + 1$).* $n+1$. adımda bir $l_j \to r_j$ kuralı bir $C_n$ cümleciğine uygulanır. Bu kural, $C_n$'nin $l_j$ ile eşleşen bir alt terimine etki eder. Tümevarım hipotezi gereği $t_c$ ($C_n$'de nerede geçerse geçsin) hiçbir konumda hiçbir $l_i$ ile eşleşmez. Kural uygulaması ya:
- $t_c$'ye dokunmaz (yeniden yazma $t_c$'yi içermeyen bir konumda olur), bu durumda $t_c$ değişmeden ve yine yeniden yazılamaz kalır; ya da
- $t_c$'yi öz alt terim olarak içeren bir terime etki eder, ama bu durumda $t_c$'nin kendisi redeks değildir (redeks, bir $l_j$ ile eşleşen alt terimdir; $t_c$ eşleşmez), bu yüzden $t_c$ değişmeden $C_{n+1}$'e geçer.

İki durumda da $t_c$, $C_{n+1}$'de yeniden yazılamaz kalır.

Bu, bir türetimin uzunluğu üzerinden standart tümevarımdır. Sentaktik Değişmezlik İlkesi'nin (Lemma 2) içeriğidir ama onu ayrı bir ilke olarak adlandırmayı gerektirmez: "$t_c$ yeniden yazılamaz" özelliğine uygulanan tümevarımdır.

### 19.3 Adım 3: sınır önermesi anlamsal olarak doğrudur
Tanımlayın:
> $\phi_{\mathcal{S}} :=$ "$\mathcal{S}$'nin dilinde, $R$'deki hiçbir kuralın hiçbir konumda uygulanabilir olmadığı bir $t_c$ terimi vardır."

Adım 1 ve 2 gereği $\phi_{\mathcal{S}}$ doğrudur: $t_c$ terimi vardır (Adım 1) ve kalıcı olarak yeniden yazılamaz kalır (Adım 2). $\phi_{\mathcal{S}}$'nin doğruluğu yalnız $R$'nin sonluluğuna ve $\mathcal{S}$'nin anlatım gücüne bağlıdır.

### 19.4 Adım 4: sınır önermesi özerk olarak türetilemez
$\mathcal{S}$'deki bir türetim, kural uygulamalarının sonlu bir dizisidir. Her $l_j \to r_j$ kuralı, $l_j$ ile eşleşen bir alt terimi $r_j$ ile değiştirerek bir terimi dönüştürür. Kurallar *tek tek konumlardaki tek tek terimlere* etki eder: $R$ kümesini bütün olarak incelemezler, bir terimi bütün sol taraflara karşı eşzamanlı karşılaştırmazlar ve hangi terimlerin yeniden yazılabilir olduğu ya da olmadığı hakkında akıl yürütmezler.

$\phi_{\mathcal{S}}$, *$R$'nin küresel yapısı* hakkında bir olgu ileri sürer: sol taraf başları kümesi $H$'nin dildeki bütün sembolleri kapsamadığı ve bu yüzden hiçbir kuralın ulaşmadığı bir terimin var olduğu. Bu iddiayı üretmek, sistemin şunları yapmasını gerektirirdi:
1. $R$'deki bütün kuralları sıralamak;
2. her sol tarafın baş sembolünü çıkarmak;
3. $H$ kümesini hesaplamak;
4. $H$'nin dilin sembollerini tüketmediğini gözlemlemek;
5. yeniden yazılamaz bir terimin var olduğu sonucuna varmak.

Bu adımların her biri üst-seviye bir işlemdir: $R$ üzerinde veri olarak işler, terimler üzerinde yeniden yazma hedefi olarak değil. $R$'nin kuralları üst-seviye işlemler yapmaz — terimleri yeniden yazar. Bir yeniden yazma dizisi $C_0 \Rightarrow C_1 \Rightarrow \cdots \Rightarrow C_n$ terimleri terimlere dönüştürür; kural kümesinin yapısı hakkında bir önerme üretmez. Bir türetimin çıktısı bir terim veya cümleciktir; sistemin neyi yeniden yazıp yazamayacağı hakkında bir üst-ifade değildir.

[Çevirenin notu: Adım 4'ün "kurallar meta-işlem yapmaz" gerekçesi, sistemin $\mathcal{S}$'nin Gödel kodlamasını içsel olarak temsil edebildiği ("yeterince anlatımlı") hipoteziyle gerilimdedir: böyle bir sistemde $R$'nin kodu üzerinde işlem yapan türetimler kurulabilir (Bölüm 11.3, Not 3). Bkz. KUNYE tenkidi.]

*[Kaynak satır 1645'te okuma bu kısımda sona erdi.]*
