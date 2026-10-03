# 2609.04086 — Tercüme, Kısım 5 (kaynak satır 1645–1974)

> Çeviri yapay zekâ çevirisidir. Çevirenin notları `[Çevirenin notu: …]` ile ayrılmıştır.

*(Bölüm 19.4'ün sonu:)* Bu yüzden $\phi_{\mathcal{S}}$, $\mathcal{S}$ tarafından özerk olarak türetilemez.

### 19.5 Adım 5: kendine-atıflı önerme ve karar verilemezliği
Köşegen lemması (Teorem 1) "$n$'nin kodladığı önerme $\mathcal{S}$'nin türetemeyeceği bir sınırı ileri sürer" hesaplanabilir fonksiyonuna uygulanınca, şöyle kendine-atıflı bir $G_{\mathcal{S}}$ önermesi vardır: $G_{\mathcal{S}} \leftrightarrow$ "$\mathcal{S}$'nin türetemeyeceği bir sınırı kodluyorum."

*$\mathcal{S} \vdash G_{\mathcal{S}}$ ise:* $\mathcal{S}$ sonlu bir yerel yeniden yazma adımları dizisiyle $R$ hakkında küresel bir olguyu (yeniden yazılamaz terimlerin varlığını) ileri süren bir önermeyi türetmiş olur. Ama her yeniden yazma adımı tek bir konumdaki tek bir örüntüyü görür; böyle adımların hiçbir sonlu dizisi bütün konumlardaki bütün örüntüler hakkında bir sonuç üretmez. Türetim, Adım 4'te sayılan beş üst-seviye işlemi yapmak zorunda kalırdı ki $R$'nin kuralları bunları sağlamaz. Kuralların yerelliği ile çelişki.

*$\mathcal{S} \vdash \neg G_{\mathcal{S}}$ ise:* $\mathcal{S}$ "$\mathcal{S}$'nin dilindeki her terim $R$'deki bir kural tarafından yeniden yazılabilir" önermesini türetmiş olur. Ama Adım 1–2 gereği $t_c$ vardır ve kalıcı olarak yeniden yazılamazdır. $\mathcal{S}$ tutarlı olduğundan, kendi kural kümesinin sonluluğunun garanti ettiği bir olguyla çelişen bir önermeyi türetemez. Çelişki.

*Sonuç:* $\mathcal{S} \not\vdash G_{\mathcal{S}}$ ve $\mathcal{S} \not\vdash \neg G_{\mathcal{S}}$.

### 19.6 Adım 6: genişletilemezlik
$\mathcal{S}$'yi sonlu sayıda kural ekleyerek $\mathcal{S}' = (V', F', R \cup R_{\mathrm{new}}, I)$'ne genişletin. O zaman $R' = R \cup R_{\mathrm{new}}$ hâlâ sonludur. Sol taraf başları kümesi $H' = H \cup \{\mathrm{head}(l) : l \to r \in R_{\mathrm{new}}\}$ hâlâ sonludur. $\mathcal{S}'$'nin dili (anlatım gücü gereği) $H'$ dışında semboller içerdiğinden, $c' \notin H'$ olan yeni bir yeniden yazılamaz terim $t_{c'}$ vardır. Aynı argümanla yeni bir $\phi_{\mathcal{S}'}$ ve yeni bir $G_{\mathcal{S}'}$ doğar. Zincir hiç sonlanmaz.

### 19.7 Özet: bu yol neyi kullanır
Bütün argüman şunları kullanır:
- *$R$'nin sonluluğu* (Tanım 1'den): $H$'yi sonlu kılar, yeniden yazılamaz terimleri garanti eder;
- *Türetim uzunluğu üzerinden tümevarım* (standart): kalıcılığı kurar;
- *Köşegen lemması* (standart, anlatım gücü hipotezinden): kendine-atıflı $G_{\mathcal{S}}$'yi üretir;
- *Tutarlılık* (Teorem 5'in hipotezinden): Durum 2'deki çelişkiyi etkin kılar.

SIP yok, engel teoremi yok, Skolem sabiti yok, korunan konum yok, çıpalı değişmez yok. Sınır *sonluluğun kendisinin* sonucudur: sonlu bir kural kümesinin sonlu bir örüntü kümesi vardır ve sonlu bir örüntü kümesi yeterince anlatımlı bir dildeki bütün terimleri kapsayamaz. SIP bu olguyu adlandırır; engel teoremi bedelini nicelleştirir; ama olgu örüntü eşlemeye uygulanan sonluluktur, bundan fazlası değil.

**Not 6 (Daha zengin yolların gerekliliği üzerine).** Burada sunulan asgarî yol, ondan önce gelen daha zengin yollar olmadan keşfedilemezdi. SIP (Bölüm 4) olguyu açığa çıkardı: donmuş alt terimleri sınırın somut tezahürü olarak belirledi ve yeniden yazılamazlığın kalıcı olduğunun ilk ispatını sağladı. Engel teoremi (Bölüm 18) olguyu keyfî yerel sistemlere genelleştirdi ve bedelini nicelleştirdi; bütün örneklerin altında yatan yapısal örüntüyü —kuralların yerelliği ile değişmezlerin küreselliği— görünür kıldı. Ancak olguyu bu giderek daha genel mercekler aracılığıyla gördükten sonra çekirdeğin örüntü eşlemeye uygulanan sonluluk olduğu fark edilebildi: sonlu bir sol taraf kümesinin sonlu bir baş sembol kümesi vardır ve sonlu bir baş sembol kümesi yeterince anlatımlı bir dili tüketemez.

Asgarî yol, ara aşamaları gerektiren bir soyutlama sürecinin son noktasıdır. SIP iskeledir; engel teoremi mimarî plandır; asgarî yol kendi başına duran binadır — ama onlarsız inşa edilemezdi. Makale üç yolu da sunar, çünkü her biri ötekilerin vermediği bir şey katar: SIP somut mekanizmayı (donmuş Skolem sabitleri), engel teoremi nicel bedeli ($\Omega(n)$ veya $\Omega(2^n)$), asgarî yol sebebi (sonluluğu) verir. Birlikte tam bir resim sağlarlar; ayrı ayrı her biri kısmîdir.

[Çevirenin notu: Asgarî yolun Adım 1'inde "yeniden yazılamaz terim vardır" kolayca doğrudur; fakat $\phi_{\mathcal{S}}$'nin "özerk türetilemezliği"nin ispatı Adım 4'teki "kurallar meta-işlem yapmaz" cümlesine dayanır; bu, bir ispat değil bir tanım iddiasıdır (bkz. KUNYE).]

## 20. Birleştirici ilke: sonlu kapsama
Bölüm 19'un asgarî yolu, öz-sınırlama teoreminin çekirdeğinin tek bir ilke olduğunu gösterir: *sonlu bir inceleme mekanizması yeterince zengin bir alanın bütün unsurlarını kapsayamaz*. Bu bölüm, aynı ilkenin, tam olarak aynı mantıksal biçimde, Sentaktik Değişmezlik İlkesi'nin, Yerel Sentaktik Engel teoreminin ve gözlemsel çerçevenin altında yattığını ve bu sonuçların her birinin asıl özel aygıtı olmadan ilkeden yeniden türetilebileceğini gösterir.

### 20.1 İlke, ifade ve ispat
**Tanım 11 (Sonlu inceleme mekanizması).** *Sonlu inceleme mekanizması*, $(\mathcal{M}, \mathcal{P}, \mathcal{D})$ üçlüsüdür:
- $\mathcal{D}$ bir kümedir (unsurlar alanı);
- $\mathcal{P} = \{p_1, \ldots, p_m\}$ sonlu bir örüntü kümesidir;
- $\mathcal{M}$, $\mathcal{D}$'nin unsurlarını $\mathcal{P}$'deki örüntülerle eşleyerek onlara etki eden bir sistemdir: $\mathcal{M}$, ancak $d$ bir $p_i \in \mathcal{P}$ ile eşleşirse $d \in \mathcal{D}$'ye etki eder.

$d \in \mathcal{D}$ unsuru, en az bir $p_i \in \mathcal{P}$ ile eşleşirse *kapsanmıştır*; aksi hâlde *kapsanmamıştır*.

**Teorem 8 (Sonlu Kapsama İlkesi).** $(\mathcal{M}, \mathcal{P}, \mathcal{D})$ sonlu bir inceleme mekanizması olsun (Tanım 11). $\mathcal{D}$ en az bir kapsanmamış unsur içeriyorsa —yani hiçbir $p_i \in \mathcal{P}$ ile eşleşmeyen bir $d^* \in \mathcal{D}$ varsa— şu üç özellik geçerlidir:

**(i) Varlık.** $\mathcal{D}$'nin, $\mathcal{M}$'nin etki edemeyeceği unsurları vardır.

**(ii) Kalıcılık.** $\mathcal{M}$'nin işlemlerinin hiçbir sonlu yinelemesi $d^*$'ı kapsama içine getirmez. Yani $\mathcal{M}$, her $d_{i+1}$'in $d_i$'den $\mathcal{M}$'nin bir işlemiyle elde edildiği bir $d_0, d_1, d_2, \ldots$ unsurlar dizisi üretir ve $d^*$ bir $d_i$'nin alt unsuru olarak görünürse, $d^*$ $d_{i+1}$'de kapsanmamış kalır.

**(iii) Körlük.** $\mathcal{M}$ ayrıca tutarlıysa (bir önermeyi ve olumsuzunu birlikte türetemezse) ve yeterince anlatımlıysa (kendi örüntülerinin bir numaralandırmasını kodlayabilir ve onlar hakkında önermeler formüle edebilirse), $\phi :=$ "$\mathcal{D}$'de kapsanmamış bir unsur vardır" önermesi anlamsal olarak doğrudur ama $\mathcal{M}$ tarafından özerk olarak türetilemez.

(i) ve (ii) özellikleri her sonlu inceleme mekanizması için koşulsuz geçerlidir. (iii) özelliği ek hipotezleri gerektirir; çünkü $\phi$'yi formüle etmek kendine-atıf gerektirir, kendine-atıf anlatım gücü gerektirir ve çelişkiyi türetmek tutarlılık gerektirir. Öz-sınırlama teoremi (Teorem 5) bu ilkenin sonlu sentaktik sistemler için bir örneklenmesidir, ön şartı değil.

*İspat.* **(i)** Hipotezle $d^* \in \mathcal{D}$ hiçbir $p_i \in \mathcal{P}$ ile eşleşmez. $\mathcal{M}$ ancak $d$ bir $p_i$ ile eşleşirse $d$'ye etki ettiğinden, $\mathcal{M}$ $d^*$'a etki edemez.

**(ii)** İşlem sayısı üzerinden tümevarım. $0$. adımda $d^*$ (hipotezle) kapsanmamıştır. $n+1$. adımda $\mathcal{M}$, bir $p_j \in \mathcal{P}$ ile tanımlı bir işlemi bir $d_n$ unsuruna uygular. Bu işlem yalnız $d_n$'nin $p_j$ ile eşleşen alt unsuruna etki eder. $d^*$ hiçbir $p_j$ ile eşleşmediğinden, işlem ya $d^*$'a dokunmaz (onu değiştirmeden bırakır) ya da $d^*$'ı içeren ama $d^*$'ın kendisi olmayan bir alt unsura etki eder ($d^*$ eşleşen alt unsur olmadığından). İki durumda da $d^*$, $d_{n+1}$'de kapsanmamış kalır.

**(iii)** $\phi$ önermesi $\mathcal{P}$'nin küresel yapısı hakkında bir olgu ileri sürer: $\mathcal{P}$'nin $\mathcal{D}$'nin tamamını kapsamadığı. $\phi$'yi üretmek, $\mathcal{M}$'nin $\mathcal{P}$'yi veri olarak incelemesini (bütün örüntüleri sıralamak, kapsamlarını hesaplamak, boşluğu gözlemlemek) gerektirirdi. Ama $\mathcal{M}$'nin işlemleri $\mathcal{P}$ *tarafından* tanımlıdır: unsurlara örüntülere göre etki ederler, örüntü kümesinin kendisine değil. İşlemler yereldir (bir unsurda bir örüntü); önerme küreseldir (bütün unsurlara karşı bütün örüntüler). Teorem 2'deki aynı argümanla (Durum 1: yerel işlemler küresel öz-bilgi üretemez; Durum 2: $\phi$'yi inkâr etmek $d^*$'ın varlığıyla çelişir), $\phi$ özerk olarak türetilemez. ∎

### 20.2 Örnekleme 1: SIP (Buono 2026)
SIP'te $\mathcal{M}$, kuralları $R$ olan yeniden yazma sistemi $\mathcal{S}$'dir. Örüntüler $\mathcal{P}$ sol taraflar $\{l_1, \ldots, l_m\}$'dir. Alan $\mathcal{D}$, imza üzerindeki bütün terimlerin kümesidir. Bir terim bir $l_i$ ile eşleşirse (birleşme başarılı olursa) kapsanmıştır. $a, b$ Skolem sabitleri, hiçbir $l_i$ ile eşleşmeyen (ilk-sembol çatışması) $\mathcal{D}$'nin özel unsurlarıdır. Buono 2026 Lemma 5 kalıcılık adımıdır: $a+b$ $0$. adımda kapsanmamışsa tümevarımla her adımda kapsanmamış kalır.

Skolem sabitleri gerekli değildir. $c \notin H = \{\mathrm{head}(l_1), \ldots, \mathrm{head}(l_m)\}$ olan her $c$ sembolü aynı kapsanmamışlığı üretir. SIP, kapsanmamış özel unsurların Skolem sabitleri olduğu sonlu kapsama ilkesinin bir örneklenmesidir; ama ilke her kapsanmamış unsur için geçerlidir.

### 20.3 Örnekleme 2: engel teoremi (Buono 2026)
Engel teoreminde $\mathcal{M}$, yerellik yarıçapı $r_0$ olan yerel bir sentaktik sistem $\mathcal{R}$'dir. Örüntüler $\mathcal{P}$, kuralların inceleyebileceği $\mathrm{ctx}_{r_0,p}(t)$ yerel bağlamlarıdır. Alan $\mathcal{D}$, bütün küresel konfigürasyonların kümesidir. Bir konfigürasyon, $r_0$ yarıçapı içinde bir kural onu ötekilerden ayırt edebiliyorsa kapsanmıştır. Buono 2026 (engel) Lemma 4.2'nin aygıt ailesi, yerel olarak ayırt edilemez ($r_0$ içinde aynı bağlam) ama küresel olarak ayrı $2^n$ konfigürasyon sağlar — $\mathcal{D}$'nin $\mathcal{P}$'nin kapsamı dışındaki unsurları.

Durum 1 (imkânsızlık) varlık ve kalıcılık adımlarıdır: korunan konumlara çıpalı $\mathrm{Inv}$ değişmezi hiçbir kural kapsanmamış konumlara ulaşmadığı için asla ihlâl edilmez. Durum 2 (alt sınır) bedelin nicelleştirilmesidir: her kural uygulaması en çok $c$ konfigürasyonu kapsar, bu yüzden bütün $2^n$'yi kapsamak $\Omega(n)$ adım gerektirir.

Korunan konumlar, çıpalı değişmez ve Buono 2026 (engel) Tanım 3.8'in beş şartı, belirli kapsanmamış unsurların gerçekten $\mathcal{P}$'nin dışında olduğunu doğrulamak için biçimsel aygıttır. İlke için gerekli değildirler; ilkenin belirli bir ortamda uygulandığının sıkı doğrulaması için gereklidirler.

### 20.4 Örnekleme 3: gözlemsel çerçeve (Buono 2026)
Buono 2026 (çerçeve)'nin koşulsuz çöküşü $\mathbf{P}_{O_{\mathrm{prof}}} = \mathbf{NP}_{O_{\mathrm{prof}}} \subsetneq \mathbf{P}$, sonlu kapsama ilkesinin doğrudan sonucudur: profil gözlemcisi $O_{\mathrm{prof}}$ dizgileri sembol-frekans vektörlerine eşler, sembollerin sırasını atar. Yalnızca sırayla ayrılan dizgiler kapsanmamıştır (aynı profile eşlenir). Sıra hesaplamalı içeriği taşıdığından ($\mathbf{P}$ ile $\mathbf{NP}$'yi ayıran dillere üyeliği belirlediğinden), gözlemci ilgili ayrımları göremez ve $\mathbf{P}$ ile $\mathbf{NP}$, $O_{\mathrm{prof}}$ altında çöker.

Gözlemci Dünyası (Buono 2026, gözlemci) bunu bir gözlemciler hiyerarşisine genişletir: $O_\bot \prec O_{\mathrm{len}} \prec O_{\mathrm{prof}} \prec O_\top$. Her gözlemcinin sonlu (veya yapısal olarak sınırlı) bir gözlenebilirler kümesi vardır; hiyerarşide yukarı çıkmak kapsamı artırır. Sonlu kapsama ilkesi der ki: $O_\top$'nin altındaki her seviyede kapsam eksiktir ve gözlemcinin göremediği ayrımlar vardır. Gözlemsel eksen hesaplamalı eksene diktir; çünkü kapsama sınırlaması hesaplama gücüyle (gözlemcinin ne kadar hızlı hesapladığı) değil, gözlemsel erişimle (gözlemcinin ne görebildiği) ilgilidir.

Bunların hiçbiri SIP'i, Skolem sabitlerini veya yeniden yazma biçimciliğini gerektirmez. Yalnızca gözlemcinin görüntüsünün alandan küçük olmasını gerektirir — sonsuz (veya yeterince zengin) bir alan üzerinde sonlu kapsama.

### 20.5 Ortak kök olarak ilke
Dört sonuç —SIP, engel teoremi, Gözlemci Dünyası— aynı ilkenin üç örneklenmesidir [Çevirenin notu: kaynak "dört sonuç" yazar, tabloda üç satır vardır]:

| Sonuç | $\mathcal{P}$ (sonlu kapsama) | $\mathcal{D} \setminus \mathcal{P}$ (kapsanmamış) |
| :-- | :-- | :-- |
| SIP | $R$'nin sol tarafları | başı $\notin H$ olan terimler |
| Engel | $r_0$ yarıçaplı yerel bağlamlar | küresel olarak ayrı, yerel olarak özdeş konfigürasyonlar |
| Gözlemci Dünyası | $O_i$ seviyesindeki gözlenebilirler | yalnız $O_{i+1}$'de görünür ayrımlar |

Her durumda üç sonuç çıkar: kapsanmamış unsurların varlığı ($\mathcal{P}$'nin sonluluğu ve $\mathcal{D}$'nin zenginliğiyle), kalıcılık (mekanizmanın işlemleri $\mathcal{P}$ ile tanımlıdır ve onun dışına ulaşamaz) ve körlük ("kapsanmamış unsurlar vardır" önermesi $\mathcal{P}$ hakkında, $\mathcal{M}$'nin formüle edemeyeceği üst-seviye bir iddiadır).

Bu ortak kök, özel örneklemeler olmadan görülemezdi. SIP olguyu yeniden yazma sistemlerinde belirledi. Engel teoremi onu yerel sistemlere genelleştirdi ve bedelini nicelleştirdi. Gözlemci Dünyası onu hesaplamaya dik bağımsız bir eksene yerleştirdi. Ancak her ortamda aynı yapı görüldükten sonra yapı tek bir ilke olarak tanınabildi ve ancak o zaman her sonuç asıl aygıtı olmadan ilkeden yeniden türetilebildi. Özel biçimcilikler özel nicel sonuçlar ($\Omega(2^n)$ alt sınırı, koşulsuz çöküş) için gerekli kalır; ama niteliksel çekirdek —sonlu kapsama yapısal körlük demektir— bir kez ifade edilen tek bir ilkedir.

### 20.6 Sonlu kapsama, klasik imkânsızlık sonuçlarının ortak kökü olarak
Sonlu kapsama ilkesi —sonlu bir inceleme mekanizması yeterince zengin bir alanın bütün unsurlarını kapsayamaz— yalnız bu makalede ele alınan sonuçların kökü değildir. Hesaplanabilirlik ve karmaşıklık kuramında hep ayrı ayrı ele alınmış birkaç klasik imkânsızlık sonucunun da köküdür. Bu alt bölüm, her sonuç için bağlantıyı açık kılar; her durumda sonlu mekanizma $\mathcal{M}$'yi, sonlu kapsama $\mathcal{P}$'yi, alan $\mathcal{D}$'yi ve kapsanmamış unsuru belirler.

**Durma probleminin karar verilemezliği (Turing, 1936).** Durma problemini karara bağlayan bir Turing makinesi $M_e$'nin sonlu bir programı (sonlu bir durumlar ve geçişler kümesi) olurdu. Kapsama $\mathcal{P}$, $M_e$'nin sonlu programının doğru sınıflandırabileceği girdi-çıktı davranışları kümesidir. Alan $\mathcal{D}$, sayılabilir sonsuz olan bütün (program, girdi) çiftlerinin kümesidir. Turing'in köşegen inşası, şu girdide…

*[Kaynak satır 1974'te, cümle ortasında ("Turing's diagonal construction produces a specific machine $D$ that, on") bu kısım sona erdi; cümle bir sonraki kısımda tamamlanır.]*
