# 2609.04086 — Tercüme, Kısım 2 (kaynak satır 628–967)

> Çeviri yapay zekâ çevirisidir. Çevirenin notları `[Çevirenin notu: …]` ile ayrılmıştır.

## 10. Evrensellik
**Teorem 4 (Bütün sonlu sentaktik sistemler için evrensellik).** $V, F, R, I$'nın belirtimi, uygulama alanı (aritmetik, mantık, hesaplamalı anlambilim vb.) veya $\mathcal{S}$'nin anlatım gücü ne olursa olsun, her sonlu sentaktik $\mathcal{S}$ sistemi için: $\mathcal{S}$, kendi öz sınırları hakkında en az bir önermeyi —yani Tanım 10'da inşa edilen $G_{\mathcal{S}}$ önermesini— özerk olarak üretemez.

*İspat.* Kendi öz sınırlarını betimleyen bir $\Phi$ önermesini özerk olarak türetebilen ($\mathcal{S}^* \vdash \Phi$) sonlu bir $\mathcal{S}^*$ sentaktik sistemi olduğunu çelişki için varsayalım. $\Phi$, $\mathcal{S}^*$'nin kendi yapısı ve sınırları hakkında olgular ileri sürdüğünden, $\mathcal{S}^*$ kendisi hakkındaki olguları ispatlamak için kendisinin bir üst-temsilini içermelidir. Ama $\mathcal{S}^*$ içinde $\mathcal{S}^*$'nin bir üst-temsili, her biri öncekini içeren sentaktik seviyelerin sonsuz bir hiyerarşisini yaratırdı ve bu, $\mathcal{S}^*$'nin sonluluğu (Tanım 1) ile çelişir. ∎

[Çevirenin notu: Bu ispat, "kendinin üst-temsili sonsuz hiyerarşi doğurur" önermesini gerekçesiz kabul eder. Gödel/Kleene yapıları sonlu bir sistemin kendi betimini sonlu biçimde içermesine izin verir (kendini yeniden üreten programlar, Kleene özyineleme teoremi). Bu, aynı makalenin Teorem 1'inin kullandığı şeyle de çeliştiği için bkz. KUNYE tenkidi.]

**Sonuç 2 (Yapay zekâ sistemleri için çıkarım).** Bir yapay zekâ sistemi —sinir ağı, dil modeli veya belirleyici algoritma olsun— sonlu bir sentaktik sistem $\mathcal{S}_{\mathrm{AI}}$ olarak gerçeklenebilir. Gizli değişkenler veya ağırlıklar $V$'nin, sinirsel işlemler veya dönüşümler $F$'nin, yayılım kuralları veya öğrenme algoritmaları $R$'nin, ilk veri veya istem ($prompt$) $I$'nın rolünü oynar. Her bileşen sonlu ve hesaplanabilir olduğundan $\mathcal{S}_{\mathrm{AI}} = (V, F, R, I)$ Tanım 1'i sağlar.

Teorem 4 gereği: bir yapay zekâ sistemi kendi temel sınırlarının anlayışını özerk olarak üretemez. Bir yapay zekâ sistemi sınırları hakkında bir önerme formüle ederse ("genellemede sınırlılıklarım var" gibi), bu önerme dışarıdan (insan geliştiriciler veya gözlemciler tarafından) iletilmiştir, sistem tarafından özerk olarak türetilmemiştir.

Örtük sonuç, normalde birbirine karıştırılan iki varlık arasında biçimsel bir ayrımdır:
- Kendi hakkındaki bilgiyi **işlemek** (sentaktik yansıma — izinli)
- Kendi yapısal sınırlarının farkındalığını **üretmek** (üst-gözlem — engelli)

Bilinç ikinci yetiyi, yani yalnızca kendisi hakkında veri işlemeyi değil, kendi yapısal sınırlarını özerk olarak tanıma yetisini de içeriyorsa, **hiçbir sonlu sistem tam anlamıyla bilinçli değildir**. Bu muğlak bir felsefî argüman değildir. Söylenenin $S_{\mathrm{AI}}$'ye uygulanmasının doğrudan sonucudur. Dolayısıyla bilinç bu yetiyi gerektiriyorsa, bilinç gözlemsel sebeplerle sonlu bir sistem tarafından benzetilemez.

## 11. Mantıksal mimari: araçlar nasıl etkileşir
Ana üst-teoremi vermeden önce her aracın argümana nasıl girdiğini ve niçin uygulanabilir olduğunu açıkça belirtmek yararlıdır.

### 11.1 SIP'in rolü
Sentaktik Değişmezlik İlkesi (Lemma 2) bütün argümanın *temelidir*. Donmuş terimlerin —sistemin içerdiği ama yeniden yazamadığı terimlerin— varlığını garanti eden araçtır. SIP olmasaydı, $\phi_{\mathcal{S}}$ sınır önermesinin maddî bir içeriği olmazdı: sistemin kör noktaları olduğu ileri sürülemezdi, çünkü kör noktaların var olduğuna dair bir ispat olmazdı.

SIP argümana üç noktada girer:
- Bölüm 6'da $\phi_{\mathcal{S}}$'nin *anlamsal olarak doğru* olduğunu garanti eder: donmuş terimler SIP öyle dediği için vardır.
- Bölüm 8, Durum 2'de *çelişkiyi* sağlar: $\mathcal{S} \vdash \neg G_{\mathcal{S}}$ ise sistem SIP'in garanti ettiği bir olguyu inkâr eder; bu da tutarsızdır.
- Bölüm 9'da her $\mathcal{S}'$ genişlemesinin *kendi* donmuş terimlerine sahip olduğunu garanti eder (yeni Skolem sabitleri $R \cup R_{\mathrm{new}}$'ye karşı yeni ilk-sembol çatışmaları üretir); böylece argüman özyinelenir.

SIP uygulanabilirdir; çünkü $\mathcal{S}$ sonlu bir yeniden yazma kuralları kümesi $R$ olan sonlu bir sentaktik sistemdir (Tanım 1). SIP yalnız $R$'nin sentaktik örüntü eşlemeli terim yeniden yazma kuralları kümesi olmasını gerektirir — Tanım 1 kapsamındaki her sistemin sağladığı bir şart.

### 11.2 Gödel numaralandırmasının rolü
Gödel numaralandırması kesin bir sebeple gereklidir: $\mathcal{S}$'nin *kendi önermeleri hakkında veri olarak konuşmasına* izin verir. O olmadan $\phi_{\mathcal{S}}$, $\mathcal{S}$'nin dışında yaşayan bir üst-seviye gözlem olurdu ve $\mathcal{S}$'nin onu türetip türetemeyeceği sorusu iyi konmuş olmazdı (önerme $\mathcal{S}$'nin dilinde olmazdı).

Gödel numaralandırması uygulanabilirdir; çünkü $\mathcal{S}$ sonludur: $V, F, R, I$'nın her unsuruna bir doğal sayı atanabilir ve bileşik terimlerin asal çarpanlara ayırma yoluyla kodlanması birebir ve hesaplanabilirdir. "Yeterince anlatımlı" hipotezi, $\mathcal{S}$'nin kodlamayı içsel olarak temsil edebilmesini, böylece $\ulcorner\psi\urcorner$'nin $\mathcal{S}$'nin dilinde bir terim olmasını sağlar.

### 11.3 Köşegen lemmasının rolü
Köşegen lemması (Teorem 1), üst-seviye gözlem $\phi_{\mathcal{S}}$'yi $\mathcal{S}$'nin dilinde *kendine-atıflı bir önerme* $G_{\mathcal{S}}$'ye çevirmek için gereklidir. Not 1'de açıklandığı gibi kendine-atıf olmadan Teorem 2'deki iki yönlü çelişki elde edilemez: $G_{\mathcal{S}}$'nin "türetilebilir değilim" demesi, onu türetmeyi (Durum 1) de inkâr etmeyi (Durum 2) de çelişkili kılar.

Köşegen lemması uygulanabilirdir; çünkü $\mathcal{S}$, Gödel numaralandırmasını temsil edecek kadar aritmetik içerir ("yeterince anlatımlı" hipotezi). Bu, köşegen lemmasının geçerli olduğu standart şarttır ve Gödel'in eksiklik teoremlerinin gerektirdiği şartın aynısıdır.

**Not 3 (Anlatım gücü hipotezi, kendine-atıf eşiği olarak).** "Yeterince anlatımlı" hipotezi kesin bir okumayı hak eder. $0 + x \to x$ ve $s(x) + y \to s(x+y)$ gibi kurallı saf bir yeniden yazma sistemi *hesaplayabilir* (terimleri normal biçimlere indirger); ancak köşegen lemması daha fazlasını ister: sistem, kendi unsurlarının Gödel kodlamasını *içsel olarak temsil edebilmeli* ve kendi dilinde türetilebilirlik hakkında önermeler formüle edebilmelidir. Anlatım gücü hipotezi, sistemin bu eşiği geçtiği noktadır.

Bu teoremin bir zayıflığı değil *keskinliğidir*. Eşiğin altında sistem kendi hakkında konuşamayacak kadar basittir: "$\mathcal{S}$, kendi sınırlarını ileri süren teoremi ortaya çıkarabilir mi?" sorusu iyi konmuş değildir, çünkü $\mathcal{S}$ soruyu formüle bile edemez. Eşiğin üstünde sistem soruyu formüle edecek kadar güçlüdür — ve teorem, tam da bu gücün sistemin cevaplamasına engel olduğunu söyler. Paradoksu yaratan kendine-atıf kapasitesidir: kendine atıf yapamayan bir sistemin öz-sınırlama problemi (ve öz-sınırlama teoremi) yoktur; kendine atıf yapabilen bir sistemde ise zorunlu olarak ikisi de vardır.

Bu yüzden teorem tam olarak olması gereken yere uygulanır: sorunun anlam taşıması için yeterince güçlü her sisteme; sorunun sorulamayacağı kadar zayıf hiçbir sisteme.

### 11.4 Tutarlılığın rolü
Tutarlılık varsayımı ($\mathcal{S} \not\vdash \bot$) argümana Teorem 2'de girer ve başka hiçbir yerde girmez. Çelişkiyi çıkarmak için gereklidir: $\mathcal{S}$ tutarsız olsaydı $G_{\mathcal{S}}$'yi de $\neg G_{\mathcal{S}}$'yi de çelişki doğmadan türetebilirdi (tutarsız sistem her şeyi türetir). Karar verilemezlik sonucu, sistemin ikisini birden türetememesini gerektirir.

Tutarlılık varsayımı bir *en iyi durumdur*: teorem en güçlü (tutarlı) sistemlere uygulanır ve tutarsız sistemler daha kötü durumdadır (hiç güvenilir çıktıları yoktur).

### 11.5 Sonluluğun rolü
$\mathcal{S}$'nin sonluluğu (Tanım 1) argümana üç noktada girer:
- Gödel numaralandırmasının var olduğunu garanti eder (sonlu bir semboller kümesi kodlanabilir);
- $\mathrm{Deriv}_{\mathcal{S}}$'nin hesaplanabilir olduğunu garanti eder (sonlu bir kural kümesi sıralanabilir bir türetim uzayı üretir);
- Teorem 4'te, sistemin kendisinin bir üst-temsilini içermesini engelleyen özelliktir (sonsuz bir seviyeler hiyerarşisi sonlulukla çelişirdi).

Sonluluk şartı her fiziksel olarak gerçeklenebilir sistem tarafından sağlanır: sonlu sayıda bileşeni, kuralı ve ilk verisi olan sistem. Her bilgisayar, her sinir ağı, fiziksel donanım üzerinde koşan her algoritma onu sağlar.

[Çevirenin notu: Bir kez daha, "sıralanabilir" ile "hesaplanabilir (karar verilebilir)" ayrımı yapılmamıştır.]

## 12. Ana üst-teorem
**Teorem 5 (Sentaktik öz-algının eksikliği).** $\mathcal{S} = (V, F, R, I)$ tutarlı ve yeterince anlatımlı (kendi unsurlarının Gödel numaralandırmasını kodlayabilen, Tanım 7) sonlu bir sentaktik sistem olsun. O zaman şunlar eşzamanlı olarak geçerlidir:

**(1) Sınırın varlığı.** Bir $P_{\mathcal{S}}$ sentaktik değişmezi ve $\phi_{\mathcal{S}}$'nin anlamsal olarak doğru olduğu bir $\phi_{\mathcal{S}}$ sınır önermesi vardır.

**(2) Özerk karar verilemezlik.** $\mathcal{S} \not\vdash \phi_{\mathcal{S}}$ ve $\mathcal{S} \not\vdash \neg \phi_{\mathcal{S}}$.

**(3) Kendine-atıfın varlığı.** "Kendi içeriğimin $\mathcal{S}$'den türetilemez olduğunu ileri sürüyorum" ifadesine denk, kendine-atıflı bir Gödel önermesi $G_{\mathcal{S}}$ vardır.

**(4) $G_{\mathcal{S}}$'nin karar verilemezliği.** $\mathcal{S} \not\vdash G_{\mathcal{S}}$ ve $\mathcal{S} \not\vdash \neg G_{\mathcal{S}}$.

**(5) Özsel genişletilemezlik.** $\mathcal{S}$'nin her tutarlı $\mathcal{S}'$ genişlemesi için, $G_{\mathcal{S}}$ ile aynı özelliklere sahip bir $G_{\mathcal{S}'}$ vardır.

*İspat.* İspat bileşiktir; bütün önceki lemmaları bütünleştirir.

*(1)'in ispatı.* Tanım 1 gereği $\mathcal{S}$'nin sonlu bir kurallar kümesi $R$ vardır. Lemma 2 gereği en az bir sentaktik değişmez özellik vardır (ör. "Skolem sabiti içerir"). Bu değişmez donmuş terimler üretir (Tanım 4). Bunların varlığı $\phi_{\mathcal{S}}$ ile yakalanır (Tanım 9). Lemma 2 gereği $\phi_{\mathcal{S}}$ anlamsal olarak doğrudur.

*(2)'nin ispatı.* $\mathcal{S} \vdash \phi_{\mathcal{S}}$ ise sistem kendi sentaktik–anlamsal eksikliği hakkında bir doğruyu ispatlamış olurdu; bu seviye hiyerarşisini ihlal eder (Teorem 2'nin Durum 1'i). $\mathcal{S} \vdash \neg \phi_{\mathcal{S}}$ ise sistem Lemma 2'nin garanti ettiği sentaktik değişmezlerin varlığını inkâr etmiş olurdu (Teorem 2'nin Durum 2'si). Tek tutarlı ihtimal ikisinin de türetilemez olmasıdır.

*(3)'ün ispatı.* Gödel numaralandırması her sonlu sentaktik sistem için vardır. $\mathrm{Deriv}_{\mathcal{S}}$ türetilebilirlik yüklemi hesaplanabilirdir (Tanım 8). Teorem 1 gereği bir sabit nokta $n^*$ vardır. Bu sabit nokta $G_{\mathcal{S}}$'yi kodlar (Tanım 10). Lemma 3 gereği $G_{\mathcal{S}}$ zorunlu olarak vardır.

*(4)'ün ispatı.* Teorem 2 (Durumlar 1, 2, 3) ile.

*(5)'in ispatı.* Teorem 3 ve Lemma 4 ile. $\mathcal{S}$, $G_{\mathcal{S}}$'yi türetmek için kural ekleyerek $\mathcal{S}'$'e genişletilirse $\mathcal{S}'$ hâlâ sonlu bir sentaktik sistemdir. Aynı argümanla yeni bir karar verilemez $G_{\mathcal{S}'}$ önermesi vardır. Süreç sonlanmaz. ∎

## 13. Çürütülemezlik
**Teorem 6 (Üst-teorem çürütülemezdir).** Teorem 5, itiraz formüle etmeye çalışan herhangi bir sistem dahil, hiçbir sonlu sentaktik sistem tarafından çürütülemez veya onunla çelişilemez.

*İspat.* $\mathcal{S}_{\mathrm{obj}}$ sonlu sentaktik sisteminin, Teorem 5'i olumsuzlayan veya çürüten bir $\Psi$ önermesini türettiğini çelişki için varsayalım. O zaman $\Psi$ şunu ileri sürer: $\Psi \equiv$ "Teorem 5'in geçerli olmadığı sonlu bir sentaktik $\mathcal{S}^*$ sistemi vardır." Ama Teorem 5 bütün sonlu sentaktik sistemler üzerinde evrensel olarak formüle edilmiştir. İspatı, herhangi bir özel $\mathcal{S}$'nin özel nitelikleri yerine her sonlu sentaktik sistemin genel niteliklerine dayanır: $V, F, R, I$'nın sonluluğu; sentaktik değişmezlerin varlığı (Lemma 2); Gödel numaralandırmasının hesaplanabilirliği; Kleene sabit noktasının varlığı (Teorem 1).

$\mathcal{S}_{\mathrm{obj}} \vdash \Psi$ ise $\mathcal{S}_{\mathrm{obj}}$ kendisi için Teorem 5'i olumsuzlamaya çalışan sonlu bir sentaktik sistemdir. Ama Teorem 5, $\mathcal{S}_{\mathrm{obj}}$ için geçerlidir. Daha kesin olarak:
1. $\Psi$, $\mathcal{S}_{\mathrm{obj}}$'nin sınırları hakkında konuşan bir önermedir ($\mathcal{S}_{\mathrm{obj}}$'nin karar verilemez öz-sınırlama önermesi olmadığını ileri sürdüğünden).
2. Teorem 5, nokta (2) gereği, $\mathcal{S}_{\mathrm{obj}}$ kendi eksikliği hakkında doğru önermeleri çelişkiye düşmeden türetemez.
3. $\Psi$ Teorem 5'i inkâr ediyorsa, $\mathcal{S}_{\mathrm{obj}}$'nin öz sınırları olduğunu inkâr eder — oysa Teorem 5 olduğunu garanti eder.
4. $\mathcal{S}_{\mathrm{obj}}$ tutarlı varsayıldığından, garanti edilmiş bir doğruyla (kendi sınırlarının varlığıyla) çelişen bir önermeyi ($\Psi$) türetemez. $\Psi$'yi türetmek $\mathcal{S}_{\mathrm{obj}}$'yi tutarsız kılardı: aynı anda Teorem 5'in hipotezlerini (sonlu, tutarlı, yeterince anlatımlı olmayı) sağlar ve sonucunu inkâr ederdi. Oysa sonuç zorunlu olarak hipotezlerden çıkar. Bu yüzden $\mathcal{S}_{\mathrm{obj}} \vdash \Psi$, tutarlılığı kaybetmeden imkânsızdır.

*[Kaynak satır 967'de, Teorem 6 ispatının 4. maddesinin ortasında bu kısım sona erdi; ispat bir sonraki kısımda sürer.]*

[Çevirenin notu: Teorem 6 "çürütülemezlik"i iddia eder; ispat Teorem 5'in doğruluğunu varsayıp ona karşı bir itirazı tutarsız sayar. Bu, bir teoremin kendi hipotezlerini sağlayan sistem tarafından çürütülemeyeceğini söylemekten öteye geçmez — yani teoremin doğruysa doğru olduğunu. Bkz. KUNYE.]
