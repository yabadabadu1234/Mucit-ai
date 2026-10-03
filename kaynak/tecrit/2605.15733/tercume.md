# Hipokampüs–Entorinal Esinli Bir Dünya Modelinde Yapı Tecriti ve Genelleme

Yazarlar: Tianqiu Zhang*, Muyang Lyu*, Xiao Liu, Si Wu (*eşit katkı) — Pekin Üniversitesi / HHMI Janelia — arXiv:2605.15733 — 15 Mayıs 2026 (ICML 2026 şablonu). Proje sayfası: hpc-mec-worldmodel.github.io

> Tercüme notu: İngilizce LaTeX kaynağından çevrilmiştir. Formüller aynen; `[anahtar]` atıflardır. Şekiller depoda yoktur, yalnız başlıkları çevrilmiştir. HPC = hipokampüs, MEC = medial entorinal korteks. "Latent transition" = örtük geçiş; "structure abstraction" = yapı tecriti; "path integration" = yol bütünleme. Kaynakta ek bölümler `Sections/*.tex` dosyalarına bölünmüştü; hepsi okundu (bkz. KUNYE).

## Özet

İnsanlar, örüntü çıkarımını ve bilgi aktarımını kolaylaştırmak için tecrübeleri yapılı temsillere tecrit eder. Hipokampal-entorinal (HPC-MEC) devresinin hem uzamsal hem kavramsal uzayları temsil ettiği bilinse de, sürekli, yüksek boyutlu dinamiklerden soyut yapıları eşzamanlı çıkarma mekanizmaları az anlaşılmıştır. Örtük geçişleri aynı anda çıkaran ve öngörücü bir görsel dünya modeli kuran, beyinden esinli hiyerarşik bir model öneriyoruz. Mimarimiz, yapı çıkarımı için bir ters model ile ilişkisel yapıları (MEC) bütünleşik epizodik sahnelerden (HPC) ayrıştıran bir HPC-MEC eşleme modeli kullanır. İlkel dönüşüm dinamiklerini ölçüt olarak kullanarak modelin yapı tecriti kapasitesini gösteririz. Hız güdümlü yol bütünlemeden yararlanarak çerçeve, farklı bağlamlarda sağlam öngörü ve yapı yeniden kullanımını mümkün kılar ve böylece yapısal genellemeyi gerçekler. Bu çalışma, dünya modellerinin beyinden esinli, öz-denetimli öğrenmesinin yeniden kullanılabilir soyut bilginin edinilmesini nasıl kolaylaştırdığını anlamak için yeni bir hesaplamalı çerçeve sunar.

## 1. Giriş

Hipokampal-entorinal devre geleneksel olarak uzamsal bellek ve seyrüsefer bağlamında incelenmiştir [keefe1978hippocampus, hafting2005microstructure]. Son zamanlarda ortaya çıkan araştırmalar bu devrenin fiziksel uzay seyrüseferinin ötesine geçerek soyut kavramsal uzayları kodladığını, çeşitli yüksek seviyeli bilişsel görevleri desteklediğini gösterir [behrens2018cognitive]. Bu sinirsel mimari, içerik ve yapı temsillerini çarpanlara ayırarak soyut ilişkileri anlamak için bilişsel iskeleler sağlar [lerousseau2024space]. Önemli deneysel ve kuramsal deliller [manns2006evolution, TolmanEichenbaumMachineUnifying2020] işlevsel bir bölünmeyi destekler: hipokampüs (HPC) bireysel tecrübelerden içeriğe özgü bilgiyi bağlarken [eichenbaum2017integration], medial entorinal korteks (MEC) soyut yapıları kodlar [julian2018human, bao2019grid]. Bu ayrım yapısal genellemeyi mümkün kılar; sistemin çıkarılan yapısal temsilleri yeni bağlamlarla esnek biçimde bağlamasına izin verir [doi:10.1073/pnas.0802631105].

MEC içindeki ızgara hücreleri bu soyut yapıların kurulmasında temeldir [behrens2018cognitive]. Çeşitli uzamsal ölçeklerdeki periyodik altıgen ateşleme örüntüleriyle karakterize edilen [giocomo2011computational] aynı aralıklı ızgara hücreleri, sürekli çekici sinir ağları (CANN) olarak işleyen modüllerde örgütlenir [amari1977dynamics, ben1995theory, wu2008dynamics]. Dahası hız girdileri alındığında ızgara hücreleri ağ etkinliğini bu çekici manifoldu boyunca sürer; soyut uzaylarda yol bütünlemeyi [burak2009accurate, gardnerToroidalTopologyPopulation2022] ve zihinsel simülasyon ve planlamayı mümkün kılar.

HPC ve MEC arasındaki sinerji, bağlama özgü içeriğin soyut ilişkisel yapılara bağlanmasını sağlar [TolmanEichenbaumMachineUnifying2020, chandraEpisodicAssociativeMemory2025]. Sonraki durumları öngörmek için MEC içinde yol bütünleme yaparak bu devre, fiilen bir dünya modelinin [haWorldModels2018, lecunPathAutonomousMachine] biyolojik gerçeklemesi olarak iş görür. Bu çerçevede MEC'in sürdürdüğü soyut yapılar, geçişlerin altlarındaki dinamiğe dayanarak kompakt temsillere kodlandığı politika öğrenmesindeki örtük eylemler kavramına [bruceGenieGenerativeInteractive2024, lapo] paraleldir.

Bu kavramsal uyumlara rağmen sinirbilimdeki mevcut bilişsel harita modelleri çoğunlukla ölçeklenmekte zorlanır; bu soyut yapıların doğrudan yüksek boyutlu, gerçek-dünya görsel sahnelerinden nasıl çıkarılabileceğini göstermeyi başaramaz. Bu boşluğu kapatmak için HPC-MEC devresinin temel işlevlerini tecrit edip ham video dizilerinden karmaşık geçiş dinamiklerini öğrenen, beyinden esinli bir dünya modeli geliştiririz. Araştırmamız iki temel soruyu ele alır:

- *Bir model, önceden denetim olmaksızın somut duyusal içeriğin temsillerini aynı anda nasıl öğrenip dizilerden soyut yapıları nasıl çıkarabilir?*
- *Bu çıkarılan yapılar, farklı nesneler ve ortamlar boyunca sağlam yapısal genellemeyi kolaylaştırmak için nasıl kullanılabilir?*

Bu çalışmada, gerçek-dünya dizilerinden soyut yapıları eşzamanlı çıkarabilen ve anlamlı bir örtük uzay öğrenebilen, HPC-MEC devresinden esinli hiyerarşik bir dünya modeli öneriyoruz. Model iki bileşenden oluşur: dizilerden soyut örtük geçişleri çıkaran bir ters model (Bölüm 3.2) ve dizilerden soyut yapıları çıkarırken hız güdümlü yol bütünleme ile sonraki çerçeveyi öngörmeyi öğrenen HPC-MEC esinli hiyerarşik bir dünya modeli (Bölüm 3.1). Modelimiz soyut yapıları farklı ortamlar ve nesneler arasında esnek biçimde yeniden kullanmada sağlam yetenekler sergiler. Dahası gerçek-dünya insan etkinliği senaryolarında etkili öngörü başarımı sergiler ve daha önce görülmemiş ortamlara genelleşir (Bölüm 5).

Bu çalışmanın başlıca katkıları:
- **Yapı tecriti için HPC-MEC dünya modelinin öz-denetimli öğrenmesi:** Soyut yapıları ortaklaşa çıkaran ve HPC-MEC esinli bir dünya modeli öğrenen öz-denetimli bir çerçeve getiriyoruz. Girdi yalnızca gözlem dizilerinden oluşur; dinamikler üzerinde açık önsel gerektirmez.
- **Yapı tecriti çözümlemesi:** İlkel dönüşüm dinamiklerini denetlenebilir bir örnek olarak kullanıp modelin görünüşü dinamikten ayrıştırdığını, periyodikliği ve sınıf-içi yapı paylaşımını gösteriyoruz.
- **Farklı bağlamlar arası yapı genellemesi:** Benzer geçiş dinamiklerinden paylaşılan yapıları çıkarmayı öğrenen ve soyut yapıları çeşitli ortamlar ve nesne kategorileri boyunca esnek biçimde yeniden kullanan, beyinden esinli hiyerarşik bir dünya modeli öneriyoruz. Bu aktarım kapasitesi, MEC'te kodlanan soyut yapıların HPC'de saklanan içerik ayrıntılarıyla bütünleşmesiyle mümkün olur. Modelimiz ayrıca dağılım-dışı veri kümelerine genelleme yetenekleri gösterir.

## 2. İlgili Çalışmalar

**Bilişsel harita modelleri.** Bilişsel harita modelleri tipik olarak yapısal tecriti MEC'e, duyusal bağlamayı HPC'ye ve duyusal öngörüyü ikisinin etkileşimine atfeder. Tolman-Eichenbaum Makinesi (TEM) [TolmanEichenbaumMachineUnifying2020], önceden tanımlı eylemlerden gözlemleri öngören bilişsel haritalar oluşturmak için tekrarlayan ağlar kullanarak uzamsal alanların ötesine uzanır; ancak ortamlar boyunca soyut haritaları yeniden öğrenmeyi gerektirir. Klon-yapılı bilişsel çizgeler (CSCG) [georgeClonestructuredGraphRepresentations2021] önsel kısıtlar olmaksızın yapısal ilişkilerin çizge tabanlı Markovsal temsillerini sunar fakat ayrık alanlarla sınırlı kalır. Vector-HaSH [chandraEpisodicAssociativeMemory2025], epizodik bellekler oluşturan ızgara hücrelerini sürmek için hipokampal durumlardan hız girdileri üretir ama hız vektörleri bütün diziyi ezberleyerek öğrenilir. Bütün bu çalışmalar sürekli ve gerçek-dünya ortamlarında dizilerden paylaşılan soyut yapıyı çıkarmanın kritik adımından yoksundur.

**Soyut hız çıkarımı.** Sinirbilimde [iyerflexible], yüksek boyutlu gözlemlerden soyut hızları çıkarmak ve onları düşük boyutlu ızgara hücresi hız girdilerine eşlemek için bir ters model kullanır. Ancak bu yaklaşım yalnızca basit yapay uyaranlara odaklanarak HPC-MEC devrelerindeki karmaşık temsil öğrenmesini önemli ölçüde basitleştirir.

**Gözlemlerden örtük geçişleri çıkarmak.** Dünya modelleri [haWorldModels2018, lecunPathAutonomousMachine] geçmiş gözlem ve eylemlere dayanarak gelecek gözlemleri öngören üretken modellerdir. Gerçek eylemler mevcut olmadığında, yalnız-gözlem gösterimlerinden eylemleri çıkarmak ve gelecek durumları öngörmek için genellikle ters ve ileri dinamik modelleri kullanılır [bruceGenieGenerativeInteractive2024, yeBECOMEPROFICIENTPLAYER2023, lapo]. Genie [bruceGenieGenerativeInteractive2024], FICC [yeBECOMEPROFICIENTPLAYER2023] ve LAPO [lapo] esas olarak 2B oyun ortamlarını hedeflerken LAPA [yeLatentActionPretraining2024], Moto [chenMotoLatentMotion2024], IGOR [chenIGORImageGOalRepresentations2024] ve UniVLA [bu2025univla] politika modellerini ön-eğitmek için gerçek-dünya ortamlarından örtük eylem çıkarımına odaklanır. AdaWorld [gaoAdaWorldLearningAdaptable2025b] örtük eylem aktarımını başarır ama büyük ölçekli önceden eğitilmiş bir video difüzyon modeline dayanır. Onların çerçevesi durum-eylem etkileşimleri için AdaLN [peebles2023scalable] kullanırken bizim modelimiz bu bütünleşmeyi sağlamak için biyolojik temelli CANN dinamiklerinden yararlanır.

**Şekil 1.** **Model mimarisine genel bakış.** (A) Video klipleri gözlem gömmeleri $\boldsymbol{s}$'yi elde etmek için görsel kodlayıcıdan geçer; bunlar HPC gömmeleri $\boldsymbol{p}$'yi üretmek için HPC üzerinden kodlanır, sonra MEC gömmeleri $\boldsymbol{g}$'yi üretmek için MEC'e geçirilir. Son olarak üretken yol onları gözleme çözer. Çok-ölçekli VAE eğitim sırasında sabittir. (B) $\boldsymbol{z}_t$ örtük geçişi, sürekli çekici dinamikleri kullanarak bir sonraki MEC gömmesi $\boldsymbol{g}_{t+1}$'i üretmek için $t$ zamanındaki MEC gömmesi $\boldsymbol{g}_t$ üzerinde işler. (C) Ters model, örtük geçişleri MEC gömmeleri $\boldsymbol{g}$'den çıkarmak için kullanılır.

## 3. Yöntemler

Model esas olarak iki parçaya ayrılır: HPC-MEC eşleme modeli (Şekil 1(A, B)) ve ters model (Şekil 1(C)). Önce video dizilerinden gözlem gömmelerini çıkarmak için önceden eğitilmiş çok-ölçekli VQ-VAE'yi [tianVisualAutoregressiveModeling2024] kullanırız. HPC-MEC eşleme modeli soyut yapıları hiyerarşik çıkarır ve hız güdümlü yol bütünlemeyle sonraki-durum öngörüsü yapar (Şekil 1(B)). Ters model, altta yatan soyut yapıları kapsayan MEC gömmelerinden örtük geçişleri çıkarmak için kullanılır. Son olarak VQ-VAE'nin kod çözücüsü üretilen gözlem gömmesinden bir sonraki çerçeveyi yeniden kurar. Genel süreç Şekil 1'de gösterilmiştir.

**Şekil 2.** **HPC-MEC eşleme modeline genel bakış.** (A) HPC-MEC eşleme modelinin grafiksel modeli. Görsel çıkarım akışı (düz pembe ok) $\boldsymbol{s}_{1:T}^{\text{inf}} \rightarrow \boldsymbol{p}_{1:T}^{\text{inf}} \rightarrow \boldsymbol{g}_{1:T}^{\text{inf}}$ kodlama sürecini modeller. Zamansal bağımlılık (kesikli pembe ok) temsillerin sürekliliğini ve tutarlılığını sağlar. Üretim akışı (düz mavi ok) geçiş dinamiğini ve $\boldsymbol{g}_{2:T}^{\text{gen}} \rightarrow \boldsymbol{p}_{2:T}^{\text{gen}} \rightarrow \boldsymbol{s}_{2:T}^{\text{gen}}$ kod çözme sürecini modeller. Görsel geri bildirim (kesikli mor ok) biriken yol bütünleme hatasını düzeltebilir. (B) CANN esinli MEC örtük uzayında hız-benzeri tecritlerin işleme mekanizması.

### 3.1 HPC-MEC Esinli Hiyerarşik Dünya Modeli

HPC-MEC eşleme modeli, iki ana bilgi akışı içeren hiyerarşik bir kodlayıcı-kod çözücü mimarisidir: görsel çıkarım akışı ve üretim akışı. Yalnızca yeniden-kurma tabanlı bir kodlayıcı-kod çözücü olarak işlemek yerine model, MEC gömmelerine örtük geçişleri uygulayarak yol bütünleme yapar; böylece sonraki gözlemleri üretebilir ve bir dünya modeli olarak hizmet eder. HPC-MEC eşleme modelinin grafiksel modeli Şekil 2(A)'da gösterilmiştir.

**Görsel çıkarım akışı.** Girdi video çerçeveleri $\boldsymbol{o}_{1:T}$ gözlem gömmeleri $\boldsymbol{s}_{1:T}^{\text{inf}}$'yi elde etmek için VQ-VAE kodlayıcısınca işlenir (ayrıntı için Ek B.3'e bakınız). $\boldsymbol{s}_{1:T}^{\text{inf}}$ sonra içerik bilgisini yakalayan daha yüksek boyutlu HPC gömmeleri $\boldsymbol{p}_{1:T}^{\text{inf}}$'ye kodlanır. Son olarak MEC, $\boldsymbol{p}_{1:T}^{\text{inf}}$'yi daha düşük boyutlu MEC gömmeleri $\boldsymbol{g}_{1:T}^{\text{inf}}$'ye sıkıştırır. HPC ve MEC ikisi de zaman bağımlılıklarını yakalamak için zamansal nedensel maskeli uzay-zaman Transformer kodlayıcıları kullanır [yeLatentActionPretraining2024].

**Üretim akışı.** MEC'in geçiş dinamiği, yol bütünleme yapabilen CANN esinli şablon eşleştirme [wu2008dynamics, yoon2013specific] olarak gerçeklenir. Sürekli Çekici Sinir Ağı (CANN), bilgiyi etkinlik örüntüsünde kararlı, sürekli bir temsilde tutmak için tasarlanmış özel bir tekrarlayan sinir ağı türüdür. CANN, mevcut yapısal durumu metrik uzayı içinde kararlı, yerelleşmiş bir sinirsel etkinlik "yumrusu" (bump) olarak sürdürür. Bu özgü geometrik düzenlilik, onları ızgara hücrelerinin yol bütünlemesine uygun kılar [burak2009accurate, gardnerToroidalTopologyPopulation2022]. Anahtar, ağın öteleme-değişmez geometrik yapısının işleçler aracılığıyla esnek durum geçişlerini kolaylaştırmasıdır (matematiksel ayrıntılar Ek B.4'te). Modelimizde çıkarılan $\boldsymbol{z}_t$ örtük geçişi tam da böyle bir işleç olarak iş görür. Örtük geçiş etkinlik yumrusunu ağın metrik eksenleri boyunca denetimli biçimde kaydırır. CANN dinamiklerini basitleştirmek için MEC gömmesi $\boldsymbol{g}_t$'nin her boyutu bir-boyutlu bir CANN'ın yumru merkeziyle temsil edilir: $\boldsymbol{g}_t = [g_{t}^1, g_{t}^2, \ldots, g_{t}^n]$; burada $n$ CANN sayısı, $g_{t}^i$ $t$ anında $i$-inci CANN'ın yumru merkezidir (Şekil 2(B)). Sonra $\boldsymbol{z}_t$, MEC gömmesi $\boldsymbol{g}_t$ ile bütünleşerek somut bir hız terimine dönüştürülür. Özellikle model önce $\boldsymbol{z}_t$ ile $\boldsymbol{g}_{t}^{\text{gen}}$'nin birleştirilmişini CANN dinamiğine doğrudan hız girdisi olan bir yer değiştirme vektörü $\Delta \boldsymbol{g}_{t}^{\text{gen}}$'yi üretmek için eşler. Yol bütünleme dinamiği bir ayrık zaman adımında şu denklemle basitleştirilebilir:

$$\boldsymbol{g}_{t+1}^{\text{gen}} = \boldsymbol{g}_{t}^{\text{gen}} \oplus \Delta \boldsymbol{g}_{t}^{\text{gen}} = \boldsymbol{g}_{t}^{\text{gen}} \oplus f_{\text{forward}}(\boldsymbol{z}_t, \boldsymbol{g}_t^{\text{gen}}) \tag{1}$$

Burada $\oplus$ faz kaydırma işlecini temsil eder ve $f_{\text{forward}}$ bir MLP olarak gerçeklenir. Bu güncelleme kuralı $\boldsymbol{g}_t$'nin her boyutunun ilgili hız bileşenine göre kaymasına izin verir; birlikte bir sonraki MEC gömmesi $\boldsymbol{g}_{t+1}$'i oluşturur. $\boldsymbol{z}_t$ örtük geçişinin boyutluluğu $\boldsymbol{g}_t$'ninkinden küçük olduğundan, $f_{\text{forward}}$ örtük geçişi karşılık gelen MEC gömmesiyle birleştirerek $\Delta \boldsymbol{g}_{t}^{\text{gen}}$ yer değiştirme vektörünü üreten bir dönüşüm işlevi görür. Bu mekanizmayla model örtük geçişleri somut dinamiklere dönüştürerek gelecek durumları öngörebilir.

**Görsel geri bildirim.** Bu model, bir başlangıç gözlemi ve bir örtük geçişler dizisi sağlayarak otoregresif öngörüyü mümkün kılar. MEC'te hız girdileri kullanarak yol bütünleme yapan ızgara hücrelerine benzer biçimde modelimiz gelecek durumları öngörmek için örtük geçişleri birleştirir. Ancak yalnızca yol bütünlemeye güvenmek zamanla hataları kaçınılmaz biriktirir. Görsel çıkarım akışı bunu, biriken hataları düzeltmek için geri bildirim sağlayarak ele alır. Özellikle görsel girdi mevcut olduğunda model, bir sonraki durumu öngörmek için gözlemden çıkarılan MEC gömmesi $\boldsymbol{g}_t^{\text{inf}}$'yi kullanarak mevcut durumu düzeltir:

$$\boldsymbol{g}^{\text{gen}}_{t+1} = \boldsymbol{g}^{\text{inf}}_{t} \oplus f_{\text{forward}}(\boldsymbol{z}_t, \boldsymbol{g}^{\text{inf}}_{t}) \tag{2}$$

**Soyut yapıların hiyerarşik ayrımı.** Geçiş dinamiklerini ve yeniden-kurmayı tek örtük uzayda bütünleştiren önceki dünya modellerinin [lapo, yeLatentActionPretraining2024, chenMotoLatentMotion2024] aksine HPC-MEC eşleme modelimiz içerik-zengin dinamikleri ve altta yatan soyut yapıları ayrı ayrı kodlar. MEC geçiş dinamiklerinin soyut yapılarını öğrenmeye odaklanırken HPC yeniden-kurma için daha zengin bağlamsal bilgiyi sürdürür. Bu ayrım özellik yeniden kullanımını ve verimli temsili güdüler: MEC nesneler arasındaki paylaşılan dinamikleri yakalar, HPC zamana bağımlı epizodik belleği korur. Sonuç olarak model, görünüşü soyut dinamiklerle karıştırmadan geçiş örüntülerini görsel bağlamlar arasında genelleştirir.

### 3.2 Örtük Geçişleri Çıkarmak

Ters model, yüksek boyutlu gözlem uzayından doğrudan eşleme yapmak yerine $\boldsymbol{z}_t$ örtük geçişini ardışık MEC gömmeleri $\boldsymbol{g}_{t}^{\text{inf}}$ ve $\boldsymbol{g}_{t+1}^{\text{inf}}$'den çıkarır. Öz-hareket yokluğunda gömmeler arasındaki geçişler örtük geçişleri öğrenmek için pratik bir vekil işlevi görür. Bunun üzerine kurarak örtük geçişleri bilişsel harita üzerinde hareketler olarak çerçeveleriz. Görevimiz bu nedenle bu soyut örtük geçişleri durum farklarından öğrenerek soyut bir bilişsel harita türetmektir. MEC gömmeleri arasındaki geçişler, ters modelin sonra düşük boyutlu örtük geçiş uzayına damıttığı en belirgin ve gürültüsüz dinamikleri yakalar:

$$\boldsymbol{z}_t = f_{\text{inverse}}(\Delta \boldsymbol{g}_{t}^{\text{inf}})= f_{\text{inverse}}(\boldsymbol{g}_{t+1}^{\text{inf}} \ominus \boldsymbol{g}_{t}^{\text{inf}}) \tag{3}$$

Burada $\ominus$ faz farkı işlecini temsil eder ve $f_{\text{inverse}}$ bir MLP olarak gerçeklenir. Ardışık MEC gömmeleri arasındaki fark üzerinde işleyerek $\boldsymbol{z}_t$, HPC'de zaten kodlanmış fazlalık görsel özellikleri dışlarken yalnızca düşük boyutlu geçiş dinamiklerini yakalar.

Dolayısıyla ters dinamik modeli $f_{\text{inverse}}$, $\Delta \boldsymbol{g}_{t}^{\text{inf}}$'yi $\boldsymbol{z}_t$'ye sıkıştırır ve ileri dinamik modeli $f_{\text{forward}}$, bir sonraki MEC gömmesi $\boldsymbol{g}_{t+1}^{\text{gen}}$'i türetmek için $\Delta \boldsymbol{g}_{t}^{\text{gen}}$'yi öngörmek üzere $\boldsymbol{z}_t$'yi $\boldsymbol{g}_{t}^{\text{gen}}$ ile birlikte kullanır (Denklem 1). Bu şekilde model, bir yol bütünleme görevi aracılığıyla eniyilenen bir $\Delta \boldsymbol{g}_{t}$ geçiş otokodlayıcısı gibi işler; bu da $\boldsymbol{z}_t$ örtük geçişinin sıkıştırılmış soyut yapıları yakalamasını daha da teşvik eder.

### 3.3 Eğitim Aşamaları

Ters modeli ve HPC-MEC eşleme modelini öz-denetimli bir öğrenme paradigmasında eğitiriz. Girdimiz yalnızca video dizilerinden oluşur; böylece altta yatan dinamikler üzerinde herhangi bir önsel kısıta gerek kalmaz. HPC-MEC sisteminin kararlı uzamsal kodlamasını taklit ederek duyusal girdi ile öz-hareket ipuçları arasında tutarlılığı zorlamak için [TolmanEichenbaumMachineUnifying2020]'dan uyarlanan bir hizalama kaybı kullanırız. Eğitim sürecini üç aşamaya böleriz:

1. **Görsel çıkarım akışının ve üretim akışının kod çözme sürecinin eğitimi:** Bu aşama modeli, anlamlı HPC gömmeleri $\boldsymbol{p}_{1:T}^{\text{inf}}$ ve MEC gömmeleri $\boldsymbol{g}_{1:T}^{\text{inf}}$ oluşturmak için gözlem gömmelerini yeniden kurmaya eğitir. Eğitim amacı yeniden-kurma, hizalama ve düzenlileştirme kayıplarını birleştirir:
$$\mathcal{L}_{\text{phase1}} = \mathcal{L}_{\text{reconstruction}}(\boldsymbol{s}_{1:T}^{\text{inf}}, \boldsymbol{s}_{1:T}^{\text{rec}}) + \mathcal{L}_{\text{alignment}}(\boldsymbol{p}_{1:T}^{\text{inf}}, \boldsymbol{p}_{1:T}^{\text{rec}}) + \mathcal{L}_{\text{regularization}}(\boldsymbol{p}_{1:T}^{\text{inf}}, \boldsymbol{g}_{1:T}^{\text{inf}})$$
Burada $\boldsymbol{s}_{1:T}^{\text{rec}}$ ve $\boldsymbol{p}_{1:T}^{\text{rec}}$ sırasıyla $\boldsymbol{g}_{1:T}^{\text{inf}}$'den yeniden kurulan gözlemler ve HPC gömmeleridir. Yeniden-kurma ve hizalama kayıpları MSE ile ölçülür. Düzenlileştirme kaybı, gömmelerin kovaryansını ve varyansını asgarîleştirerek modeli yapılı bir örtük uzay öğrenmeye teşvik eder [bardes2022vicreg].
2. **Ters modelin ve üretim akışının geçiş dinamiklerinin eğitimi:** Aşama 1'de elde edilen anlamlı gömmeleri kullanarak ters modeli ardışık MEC gömmeleri $\boldsymbol{g}^{\text{inf}}$'den $\boldsymbol{z}$ örtük geçişlerini çıkarmak için eğitiriz. Eşzamanlı olarak geçiş dinamiklerini üretilen MEC gömmesi $\boldsymbol{g}^{\text{gen}}$'i öngörmek için eğitiriz. Çok adımlı yol bütünlemeden biriken hataları önlemek ve modelin örtük geçişleri atlayan kestirmeler öğrenmesini engellemek için tek-adımlı öngörüye odaklanırız. Eğitim amacı Aşama 1'i ek hizalama ve geçiş kayıplarıyla genişletir:
$$\mathcal{L}_{\text{phase2}} = \mathcal{L}_{\text{phase1}} + \mathcal{L}_{\text{alignment}}(\boldsymbol{g}_{2:T}^{\text{inf}}, \boldsymbol{g}_{2:T}^{\text{gen}}) + \mathcal{L}(f_{\text{fwd}}(\boldsymbol{z}_{1:T-1}, \boldsymbol{g}_{1:T-1}^{\text{inf}}), \Delta \boldsymbol{g}_{1:T-1}^{\text{inf}})$$
3. **HPC-MEC eşleme modelinin ve ters modelin ortaklaşa ince ayarı:** Bu son aşamada Aşama 2 kayıp fonksiyonunu kullanarak bütün model parametrelerini ortaklaşa ince ayarlarız. Aşama 2'den farklı olarak model artık yalnızca $\boldsymbol{g}_{1}^{\text{inf}}$'yi ve ters modelden gelen örtük geçiş dizisini kullanarak yol bütünleme ve ileri öngörü yaparak otoregresif açılımlar üretmeyi öğrenir. MEC gömmeleri bu aşamada dinamikle ilgili soyut yapıları yakalamayı öğrenir. Farklı aşamalardaki model eğitiminin ayrıntılı tarifi Ek C.1'dedir.

### 3.4 Deney Kurulumu

Modelimizi üç tür veri kümesiyle değerlendiririz. Model, nesnelerle karmaşık etkileşimler içeren, açık eylem etiketi olmayan, geniş ölçekli bir insan etkinliği video veri kümesi olan Something-Something v2 (SSv2) üzerinde [DBLP:journals/corr/GoyalKMMWKHFYMH17] eğitilir. Modelimizin dağılım-dışı yeteneğini değerlendirmek için birkaç simüle veri kümesi kullanılır; bunlar arasında 3B nesne geçiş veri kümeleri (COIL-100 [nene1996columbia], MIRO [kanezaki2018rotationnet], OmniObject3D [wu2023omniobject3d]) ve simüle ortamlar (Franka Kitchen [gupta2019relay], Block Pushing [florence2022implicit], Push-T [chi2023diffusion] ve LIBERO Goal [liu2023libero]) vardır.

**Şekil 3.** **HPC ve MEC gömmelerinin çözümlemesi.** (A) Periyodiklik sınıfına göre gruplanmış HPC ve MEC gömmelerinin UMAP görselleştirmesi. Her nesne iki tam dönüş tamamlar. (B) Nesne kategorisine göre gruplanmış HPC ve MEC gömmelerinin UMAP görselleştirmesi. (C) HPC ve MEC gömmeleri kullanılarak nesne kategorilerinin sınıflandırma doğruluğu. (D) Bireysel bir nesne için çıkarım ve üretim gömmeleri arasındaki hizalama.

## 4. Yapı Tecriti Çözümlemesi

Bölüm 5'te ayrıntılandığı gibi modelimiz hem karmaşık insan-nesne etkileşimlerinde (SSv2) hem çeşitli dağılım-dışı veri kümelerinde bağlamlar arası sağlam yapısal genelleme yanında güçlü tek-adımlı ve otoregresif öngörüler elde eder. Bu yetenekleri süren temsilleri ortaya çıkarmak ve modelin dizisel veriden soyut yapıları çıkarma kapasitesini doğrulamak için, SSv2 ile ön-eğitilmiş modelimizi dönme, öteleme ve ölçekleme içinde denetimli geçişler içeren OmniObject3D'den render edilmiş dağılım-dışı bir 3B nesne veri kümesinde değerlendiririz. HPC ve MEC gömmeleri arasındaki hiyerarşik işlemenin paylaşılan yapısal temsillerin ortaya çıkışını nasıl kolaylaştırdığını özellikle çözümleriz. Son olarak bu çözümlemeyi, böyle yapı tecritinin robotik simüle ortamlara kolayca genellendiğini göstermek için genişletiriz.

### 4.1 Niteliksel Çözümleme

3B dönen nesnelerin hem HPC hem MEC örtük uzaylarını görselleştirerek modelin belirli nesne içeriğini altta yatan soyut dinamiklerden ayrıştırma yeteneğini gösteririz.

**Periyodik paylaşılan yapılar.** Önce periyodik dönüş örüntülü nesneleri belirler ve görsel benzerliğe göre üç periyodiklik sınıfına ayırırız: periyot 1 ($360^{\circ}$), $\frac{1}{2}$ ($180^{\circ}$) ve $\frac{1}{4}$ ($90^{\circ}$). UMAP [mcinnes2018umap] ile boyut indirgeme çözümlemesi yoluyla bu periyodiklik sınıflarının gömme uzayında ayırt edici düşük boyutlu yörüngeler sergilediğini gözleriz (Şekil 3(A)). Periyot 1 olan nesne tam bir dairesel yörünge oluşturur; periyot $\frac{1}{2}$ olan nesne iki örtüşen dairesel yörünge oluşturur. Üç beyaz ve bir kahverengi yüzü olan periyot $\frac{1}{4}$'lük nesne ardışık benzer görsel geçişler için örtük geçiş yapısını yeniden kullanır; iki örtüşen küçük dairesel yörünge oluştururken geri kalan ayrı geçişler daha büyük yarım-periyot dairesel bir yörünge oluşturur. Hem HPC hem MEC gömmeleri benzer periyodiklik örüntüleri sergiler ama MEC temsilleri daha belirgin tanımlı paylaşılan dönüş özellikleri oluşturur. Bunu doğrulamak için aşağıdaki gibi çok-sınıflı çözümlemeler yaparız.

**Sınıf-içi paylaşılan yapılar.** Sınıf-içi paylaşılan yapıları çözümlemek için her biri birden çok örnek içeren üç nesne kategorisini inceleriz: kabaklar, kırmızı elmalar ve sarı elmalar. Her nesnenin dönüş dizilerini modelimizle işleyip HPC ve MEC gömmelerini çıkarır ve bu temsilleri UMAP ile görselleştiririz. Sonuçlar (Şekil 3(B)), hem HPC hem MEC kategoriler arası ayrım sergilerken $\boldsymbol{p}^{\text{inf}}$'ın ayrıca açık kategori-içi farklılaşma gösterdiğini ortaya koyar. Özellikle farklı sınıf-içi nesneler için $\boldsymbol{p}^{\text{inf}}$ ayrı dairesel yörüngeler oluşturur ve nesneye özgü özellikleri yansıtır. Buna karşılık $\boldsymbol{g}^{\text{inf}}$ ve $\boldsymbol{g}^{\text{gen}}$ yörüngeleri büyük ölçüde örtüşür ve sınıf-içi paylaşılan dönüş özelliklerini yakalar. Bu paylaşılan yapılar üretim akışı boyunca yayılır, $\boldsymbol{p}^{\text{gen}}$ manifoldunu biçimlendirir ve dönüş özelliklerini yüksek boyutlu uzayda daha belirgin kılar. Dahası $\boldsymbol{p}^{\text{inf}}$ ve $\boldsymbol{p}^{\text{gen}}$'in küresel manifoldları doğal olarak farklılık gösterse de bireysel nesnelerin çıkarım ve üretim gömmelerinin UMAP izdüşümleri hem HPC'de hem MEC'te yüksek tutarlılık korur (Şekil 3(D)).

### 4.2 Niceliksel Çözümleme

HPC'nin daha özgül içerik bilgisini bağladığını, MEC'in ise daha genellenebilir soyut yapıları kodladığını göstermek için bazı niceliksel deneyler de yaparız.

**Sınıf-içi yapı paylaşımının nicelenmesi.** MEC'in sınıf-içi paylaşılan yapıları tecrit ettiği, HPC'nin ise daha çok kimlik özelliği tuttuğu (Bölüm 4.1'de belirtilen) iddiasını nicelemek için, HPC ve MEC gömmelerinden nesne kategorilerini sınıflandırmak için ayrı hafif kod çözücüler eğitiriz. Test nesneleri eğitim sırasında dışlanır; böylece daha yüksek test doğruluğu nesne sınıfları içinde daha büyük yapısal tutarlılığı gösterir. Sonuçlarımız, eğitim yakınsamasından sonra $\boldsymbol{p}^{\text{inf}}$ üzerindeki test doğruluğunun $\boldsymbol{g}^{\text{inf}}$ ve $\boldsymbol{g}^{\text{gen}}$'dan tutarlı olarak düşük olduğunu gösterir; bu, HPC gömmelerinin daha çok içeriğe özgü ayrıntı kodladığını gösterir. Buna karşılık MEC gömmeleri sınıf-içi paylaşılan yapıları daha iyi yakalar ve yeni örneklere genellemeyi artırır (Şekil 3(C)).

**Geçiş çözme deneyi.** Dönüş, öteleme ve ölçekleme farklı dönüşümlerini içeren 3B nesne geçiş dizileri kullanırız. Her dizi rastgele kategori, başlangıç konumu, yönelim ve boyutlu bir nesne içerir. Bu dizileri sıfır-atışlı genelleme için modelimize besler ve elde edilen örtüklerde geçiş türünü öngörmek için aynı gizli boyutlu geçiş kod çözücüleri eğitiriz. Bu, örtük temsillerin tecritini ve geçiş anlambilimini ölçmemizi sağlar. Tablo 1'de gösterilen sonuçlardan, örtük geçişin ($z$) geçiş türlerini çözmede en yüksek doğruluğa ulaştığını, ardından MEC uzayındaki durum geçişlerinin ($\Delta g^{inf}$) geldiğini görürüz. Daha çok özgül ayrıntı içerdiği için HPC uzayından ($\Delta p^{inf}$) geçiş bilgisini tecrit etmek daha zordur. Bu sonuçlar MEC'in daha içerikten-bağımsız yapıları çıkardığını gösterir; bunlar çok etkili ve anlamsal olarak anlamlıdır.

**Tablo 1.** Farklı gömmelerde çözme doğruluğu.

| Gömme | $\boldsymbol{p}^{\text{inf}}$ | $\boldsymbol{g}^{\text{inf}}$ | $\Delta \boldsymbol{p}^{\text{inf}}$ | $\Delta \boldsymbol{g}^{\text{inf}}$ | $\boldsymbol{z}$ |
| :-- | --: | --: | --: | --: | --: |
| Doğruluk ↑ | 0.3330 ± 0.0163 | 0.3486 ± 0.0156 | 0.8386 ± 0.0263 | 0.8868 ± 0.0212 | **0.9064 ± 0.0145** |

**Şekil 4.** **Tek-adımlı ve otoregresif öngörü değerlendirmesi.** (A) SSv2 test veri kümesinde değerlendirilen tek-adımlı öngörü. (B) SSv2 test veri kümesinde görsel geri bildirimli ve görsel geri bildirimsiz otoregresif öngörü. (C) Dağılım-dışı bir veri kümesi olan COIL-100'de tek-adımlı öngörü.

**Robotik dinamiklere genelleme.** Bulgularımızı karmaşık ortamlarda daha ileri doğrulamak için aynı eylemin (örn. Franka Kitchen'daki "üst dolabı açmak") değişen bağlamlarda (örn. farklı nesne konumları veya mikrodalga durumları) yapıldığı dizileri çözümleriz. Sonra HPC uzayındaki ($\Delta \boldsymbol{p}$), MEC uzayındaki ($\Delta \boldsymbol{g}$) ve örtük geçiş uzayındaki ($\boldsymbol{z}$) durum geçişlerinin kosinüs benzerliğini hesaplarız. Sonuçlar Tablo 2'de gösterilmiştir. Örtük geçiş yörüngelerinin en yüksek benzerliği sergilediğini ve MEC uzayının HPC uzayından daha yüksek yapısal hizalama gösterdiğini görürüz. Bu sonuçlar, modelin robotik simüle ortamlardan içerikten-bağımsız yapıları etkili çıkarabildiğini düşündürür.

**Tablo 2.** Örtük zamansal farkların dizi benzerliği.

| Geçişler | $\boldsymbol{z}$ | $\Delta \boldsymbol{g}^{\text{inf}}$ | $\Delta \boldsymbol{g}^{\text{gen}}$ | $\Delta \boldsymbol{p}^{\text{inf}}$ | $\Delta \boldsymbol{p}^{\text{gen}}$ |
| :-- | --: | --: | --: | --: | --: |
| Kos. Ben. ↑ | **0.235 ± 0.021** | 0.146 ± 0.063 | 0.152 ± 0.057 | 0.024 ± 0.061 | 0.114 ± 0.056 |

## 5. Epizodik Sentez ve Yapısal Genelleme

Modelin yapı tecriti kapasitesini kurduktan sonra bu örtük yapıların ikili bir amaca hizmet ettiğini gösteririz: epizodik belleklerin sentezini kolaylaştırmak ve sağlam yapısal genellemeyi mümkün kılmak. Özellikle çerçevemiz bu soyut yapılardan yeni varlıklar arasında aktarım için yararlanır. Altta yatan geçişleri belirli duyusal içerikten ayrıştırarak model, tümüyle farklı nesneler veya sahneler için benzer hareketler üretebilir; böylece sıfır-atışlı aktarımı etkili biçimde gösterir.

### 5.1 Tek-adımlı ve Otoregresif Öngörüler

Tek-adımlı öngörü için model girdi videosundan örtük geçişi başarıyla çıkarır ve gerçek dizinin dinamiğiyle eşleşen çerçeveler üretir (Şekil 4(A)). Otoregresif öngörü için model, başlangıç çerçevesine bir örtük geçişler dizisi uygulayarak bütün diziyi üretir (Şekil 4(B)). Modelin daha uzun diziler üretirken bile iyi tutarlılığı koruduğunu, ancak üretim kalitesinin zamanla giderek azaldığını buluruz. Bu, MEC'te biriken yol bütünleme hatalarına karşılık gelir. Biyolojik sistemlere benzer biçimde model, duyusal girdiden görsel geri bildirim alarak bileşik hataları düzeltebilir. Modelin başarımını dördüncü açılım adımında görsel geri bildirim getirdikten sonra sınarız ve sonraki çerçevelerde daha doğru ayrıntılarla iyileşmiş üretim kalitesi gözleriz (Şekil 4(B)). Örtük geçişlerin geçiş dinamiklerini yönetmedeki rolünü incelemek için Ek F'de tartışılan ek bir ablasyon çalışması yaparız.

**Dağılım-dışı veri kümelerine genelleme.** Modelin dağılım-dışı sahneleri üretmek için örtük geçişleri etkili çıkarıp kullanıp kullanamayacağını değerlendirmek için modeli görülmemiş 3B nesne geçiş veri kümelerinde değerlendiririz. Sonuçlarımız modelin temel dönüş dönüşümlerini örtük geçişler olarak başarıyla belirlediğini ve gerçeğe yakın diziler ürettiğini gösterir (Şekil 4(C)). Modeli ayrıca insan videolarından önemli dağılımsal kaymaları olan simüle ölçütlerde değerlendiririz; bu sanal alanlara genellemeyi potansiyel olarak sınırlayabilir. Tam sonuçlar Ek G'de verilmiştir. Bulgularımız, modelin Franka Kitchen gibi daha doğal ortamlarda daha sağlam, Push-T gibi yapay ortamlarda daha az etkili başarım gösterdiğini ortaya koyar.

**Şekil 5.** **Yapısal genelleme.** (A) SSv2'de farklı sahneler arasında tek-adımlı örtük geçiş aktarımı. (B)(C) Ardışık örtük geçişleri aktararak tek-adımlı ve otoregresif öngörü. (D)(E) SSv2'de örtük geçişlerin otoregresif yeniden kullanımı. (F)(G) Nesne kategorileri arasında dönüş ve ölçekleme dinamiklerinde örtük geçişlerin otoregresif yeniden kullanımı.

### 5.2 Bağlamlar Arası Yapısal Genelleme

Modelimizin örtük geçişleri yeniden kullanma yeteneğini doğrulamak için hem doğal insan etkinliği verisi hem simüle veri kümeleriyle değerlendirmeler yaparız.

Tek-adımlı örtük geçiş yeniden kullanımının sonuçları Şekil 5(A)'da gösterilmiştir. Mor vurgulu çerçeve çiftlerinden, nesnelerin kaybolması veya kapılması gibi el hareketlerini yakalayan örtük geçişi çıkarırız. Sonra aynı örtük geçişi farklı sahnelere uygular ve sonraki çerçeveleri üretiriz. Üretilen çerçeveler özgün çerçeve çiftlerinin dinamiğini başarıyla taklit eder.

Örtük geçiş aktarılabilirliğini daha ileri incelemek için bir videodan çıkarılan örtük geçiş dizilerini farklı bağlamlar içeren çerçevelere uyguladığımız deneyler yaparız. Elma dönüşünü bir vaka çalışması olarak kullanıp sarı elma içeren bir diziden örtük geçişleri çıkarır ve olgun bir kırmızı elmanın dönüşünü üretmek için uygularız. Sonuçlarımız, üretilen dizideki doku özelliklerinin olgun kırmızı elmaya karşılık gelirken dönüş dinamiğinin örtük geçişlerin türetildiği sarı elmayla hizalandığını ortaya koyar (Şekil 5(B)). Yalnızca çıkarılan örtük geçişleri ve başlangıç çerçevesini kullanarak otoregresif öngörü yaptığımızda üretilen dizinin kaynak dizinin dönüş dinamikleriyle hizalı kaldığını, ancak doku özelliklerinin giderek saptığını, gerçek diziden daha parlak hale geldiğini gözleriz (Şekil 5(C)). İnsan etkinliği senaryolarında ardışık örtük geçiş yeniden kullanımını gösteren iki örnek de Şekil 5(D,E)'de sunarız. Ortaya çıkan görüntü dizisi, yeni sahnenin içerik bilgisini korurken kaynak senaryonun dinamiklerini yakalar. Şekil 5(F, G), iki ek vakayı gösterir: nesne kategorileri arasında dönüş ve ölçekleme dinamiği aktarımı.

### 5.3 Taban Çizgisi Karşılaştırması

Modelimizi, gerçek eylem etiketleri olmaksızın yalnız-gözlem videolarından örtük geçişleri çıkarmak ve yeniden kullanmak için hizalanan en gelişkin örtük eylem modelleri LAPA [yeLatentActionPretraining2024], Moto [chenMotoLatentMotion2024] ve AdaWorld LAM [gaoAdaWorldLearningAdaptable2025b] ile karşılaştırırız. İki standart ölçü kullanırız: yerel yapısal tutarlılık için Yapısal Benzerlik İndeksi (SSIM) [wang2004image] ve algısal benzerlik için Öğrenilmiş Algısal Görüntü Yaması Benzerliği (LPIPS) [zhang2018unreasonable]. Tablo 3'te görüldüğü gibi modelimiz hem tek-adımlı hem otoregresif öngörüde daha düşük LPIPS puanları elde eder; bu, gerçek dinamiklerle daha yakın görsel benzerliği ve örtük geçişlerin daha etkili çıkarılmasını gösterir. Franka Kitchen veri kümesinde Moto ve AdaWorld LAM anlamlı dinamikleri öngörmekte güçlük çeker, çoğunlukla önceki çerçevelerle neredeyse özdeş statik öngörülere dejenere olur. Buna karşılık modelimiz hem alan-içi hem dağılım-dışı veri kümelerinde sağlam başarımı korur. Bunu HPC-MEC esinli mimarimize atfederiz: örtük geçişleri iç içe birleşik bir uzayda öğrenen taban çizgilerinin aksine hiyerarşik modelimiz bunları daha yapılı bir uzayda öğrenir; soyut örtük geçişler verir ve otoregresif bileşik hataları belirgin biçimde hafifletip dağılım-dışı dayanıklılığı artırır.

**Tablo 3.** Modeller ve aşağı akış veri kümeleri arasında SSIM ve LPIPS'in niceliksel karşılaştırması. Her model 8-adımlı dizi üretimi yapar. * dağılım-dışı veri kümelerini gösterir.

| Veri kümesi | Model | SSIM ↑ tek-adım | SSIM ↑ otoreg. | LPIPS ↓ tek-adım | LPIPS ↓ otoreg. |
| :-- | :-- | --: | --: | --: | --: |
| SSv2 | LAPA | 0.744±0.022 | 0.659±0.027 | 0.357±0.017 | 0.448±0.017 |
| | Moto | 0.668±0.027 | 0.566±0.029 | 0.301±0.022 | 0.480±0.012 |
| | AdaWorld(LAM) | **0.763±0.023** | 0.654±0.018 | 0.295±0.026 | 0.448±0.022 |
| | VQ-VAE ablasyonu | 0.717±0.023 | 0.677±0.031 | 0.313±0.013 | 0.378±0.017 |
| | Bizim model | 0.752±0.019 | **0.687±0.018** | **0.274±0.026** | **0.356±0.015** |
| COIL-100* | LAPA | 0.589±0.038 | 0.682±0.020 | 0.301±0.021 | 0.385±0.016 |
| | Moto | 0.700±0.031 | 0.642±0.043 | 0.352±0.041 | 0.473±0.031 |
| | AdaWorld(LAM) | 0.778±0.039 | 0.715±0.042 | 0.312±0.048 | 0.415±0.060 |
| | Bizim model | **0.837±0.021** | **0.814±0.032** | **0.226±0.034** | **0.270±0.031** |
| Franka Kitchen* | LAPA | 0.690±0.002 | 0.532±0.003 | 0.389±0.001 | 0.529±0.001 |
| | Moto (başarısız) | – | – | – | – |
| | AdaWorld(LAM) (başarısız) | – | – | – | – |
| | VQ-VAE ablasyonu | 0.576±0.037 | 0.523±0.038 | 0.385±0.018 | 0.445±0.022 |
| | Bizim model | **0.705±0.004** | **0.551±0.005** | **0.253±0.003** | **0.426±0.003** |

**Tablo 4.** Dağılım-dışı yapı yeniden kullanım görevinde ablasyon modellerinin niceliksel karşılaştırması.

| Model | R ↑ tek-adım | R ↑ otoreg. | SSIM ↑ tek-adım | SSIM ↑ otoreg. | LPIPS ↓ tek-adım | LPIPS ↓ otoreg. |
| :-- | --: | --: | --: | --: | --: | --: |
| Birleşik örtük uzaylı modelimiz | 2.054±0.521 | 1.542±0.246 | 0.901±0.007 | 0.886±0.008 | 0.126±0.008 | 0.179±0.008 |
| CANN'sız modelimiz | 2.403±0.553 | 1.859±0.396 | 0.894±0.022 | 0.888±0.009 | 0.149±0.009 | 0.177±0.010 |
| VQ-VAE ablasyonu | 2.035±0.229 | 1.796±0.173 | 0.892±0.009 | 0.883±0.009 | 0.158±0.009 | 0.177±0.009 |
| Bizim model | **3.201±0.435** | **2.482±0.460** | **0.902±0.010** | **0.891±0.009** | **0.120±0.008** | **0.156±0.008** |

**Tablo 5.** Farklı modellerin örtük geçişleri kullanılarak eylem çözme doğruluğunun niceliksel karşılaştırması.

| Model | AdaWorld(LAM) | LAPA | Moto | VQ-VAE ablasyonu | CANN'sız modelimiz | Bizim model |
| :-- | --: | --: | --: | --: | --: | --: |
| Doğruluk ↑ | 0.6395±0.0192 | 0.8259±0.0155 | 0.7190±0.0120 | 0.8523±0.0247 | 0.8768±0.0117 | **0.9064±0.0145** |

### 5.4 Ablasyon Çalışması

Başarımımızı güdüleyen bileşenleri yalıtmak için ablasyon varyantlarını dağılım-dışı yapı yeniden kullanım görevinde değerlendiririz (Tablo 4). Başarılı yeniden kullanım, üretilen çerçevelerin örtük geçişi çıkarmak için kullanılan kaynak diziyle değil hedef diziyle hizalanmasını gerektirir. Bunu önceden eğitilmiş bir DINOv2 kodlayıcısı $E$'nin özelliklerini kullanan bir benzerlik oranı tanımlayarak nicelleriz. $R = \mathbb{E}\left[ \frac{\cos(E(\mathbf{o}_t^{\text{gen}}), E(\mathbf{o}_t^{\text{content}}))}{\cos(E(\mathbf{o}_t^{\text{gen}}), E(\mathbf{o}_t^{\text{action}}))} \right]$ oranı, üretilen nesnenin hedef içeriğe mi kaynak içeriğe mi daha yakın olduğunu ölçer. Daha yüksek R, içerik dizisiyle daha güçlü hizalamayı ve dolayısıyla daha iyi örtük geçiş yeniden kullanımını gösterir. Her çekirdek bileşenin etkililiğini üç farklı ablasyon varyantıyla gösteririz:

**Hiyerarşik HPC–MEC ayrımı.** Ayrıştırılmış mimarimizin gerekliliğini sınamak için MEC katmanını çıkararak birleşik uzay varyantı kurarız ("Birleşik örtük uzaylı modelimiz"). Ters modeli ve CANN modülünü doğrudan tek, yüksek boyutlu HPC katmanına bağlayarak ters model $\boldsymbol{z_t}$'yi ardışık HPC gömmelerinden ($\boldsymbol{p}_{t}^{\text{inf}}$, $\boldsymbol{p}_{t+1}^{\text{inf}}$) çıkarır. Sonuçta CANN'ın yol bütünlemesi bu içerik-iç içe durumlar üzerinde işler. Bu varyant kaynak videodan belirgin "doku sızıntısı" sergiler; bu hiyerarşik ayrımın saf dinamikleri yalıtmak ve örtük geçişlerin nesneye özgü içerikle iç içe geçmesini önlemek için gerekli olduğunu gösterir.

**CANN tabanlı MEC dinamikleri.** MEC'in iç dinamiklerini, CANN modülümüzü eşdeğer kapasiteli standart bir MLP ile değiştirerek ablate ederiz ("CANN'sız modelimiz"). Bu varyant "durumdan-duruma" öngörü yapar; sonraki durumu birleştirilmiş mevcut durum ve örtük geçişten doğrudan hesaplar: $\boldsymbol{g}_{t+1}^{\text{gen}} = \text{MLP}([\boldsymbol{g}_{t}^{\text{gen}}, \boldsymbol{z_t}])$. Buna karşılık CANN modülümüz göreli geçişi $\Delta \boldsymbol{g}_{t}$'yi öngörür (Bölüm 3.2). Bu geçiş-merkezli tasarım kritiktir: $\boldsymbol{z_t}$'yi tam durum yeniden-kurmasından kurtarır ve onu saf içerikten-bağımsız dinamikleri kodlamaya zorlar. Sonuç olarak MLP değişikliği dağılım-dışı aktarım görevlerinde tümüyle başarısız olur; bu, öğrenilen dinamiklerin yeni sahnelere genellenmesi için CANN yapısının mutlak gerekliliğini gösterir.

**Yapı önceden eğitilmiş kodlayıcıdan gelmiyor.** Soyut yapılarımızın yalnızca görsel kodlayıcıdan miras alınmadığını, HPC-MEC modülü tarafından güdüldüğünü doğrulamak için hiyerarşik mimariden tümüyle yoksun bir "VQ-VAE ablasyonu" değerlendiririz. Bu varyant aynı önceden eğitilmiş VQ-VAE'yi, $\boldsymbol{z_t}$'yi doğrudan ardışık gömmelerden ($\boldsymbol{s}_t^{\text{inf}}, \boldsymbol{s}_{t+1}^{\text{inf}}$) çıkaran bir ters modeli ve $\boldsymbol{s}_{t+1}^{\text{gen}} = \text{MLP}([\boldsymbol{s}_t^{\text{gen}}, \boldsymbol{z_t}])$ öngören bir MLP ileri modeli kullanır. HPC-MEC'in yapısal tecriti olmadan bu varyant aşırı kaynak bilgisini tutar ve daha kötü aktarım öngörüleri verir (Tablo 4). Bu, içerikten-bağımsız tecritlerin sağlam çıkarımının önceden eğitilmiş kodlayıcıdan değil temelde hiyerarşik tasarımımızdan güdüldüğünü doğrular.

### 5.5 Örtük Geçiş Çözme

Örtük geçişlerin kalitesini taban çizgileri ve ablasyonlara karşı değerlendirmek için dağılım-dışı 3B-nesne geçiş görevini (Bölüm 4.2) yeniden ele alırız. Özetle bu, çeşitli görülmemiş nesnelerin tek bir dönüşümden (dönüş, öteleme veya ölçekleme) geçtiği dizileri içerir. LAPO'yu [lapo] izleyerek, her modelin ürettiği örtük geçişlerden bu dönüşüm türlerini doğrudan sınıflandırmak için bir MLP sondası eğitiriz. Tablo 5'te görüldüğü gibi modelimiz bütün taban çizgilerini ve ablasyonları belirgin biçimde geçer. Bu sonuçlar, örtük geçişleri hiyerarşik model aracılığıyla MEC uzayında öğrenmenin, içerik ayrıntılarından girişime yatkın birleşik uzaylı mimarilerden (örn. bütün taban çizgileri ve VQ-VAE ablasyonu) daha soyut anlambilim yakaladığını gösterir. Dahası tam modelimiz ile "CANN'sız" ablasyon arasındaki başarım farkı, CANN modülünün içeriğe özgü ayrıntıları bastırmadaki ve altta yatan dinamikleri daha iyi yansıtan geçişler vermedeki kritik rolünü vurgular. Bu, yapılı MEC-uzayı geçişlerinin HPC-uzayı olanlardan anlamsal olarak daha çözülebilir olduğuna dair Bölüm 4.2'deki önceki bulgumuzla tutarlıdır.

## 6. Tartışma ve Sınırlamalar

Bulgumuz, soyut yapıların anlamlı hiyerarşik örtük uzayları korurken gerçek-dünya video dizilerinden nasıl etkili çıkarılabileceğini gösterir. Ters modelin HPC-MEC esinli dünya modeliyle birleşimi, soyut yapıları belirli içeriklerden verimli çıkarmayı mümkün kılar ve sağlam aktarım yeteneklerini kolaylaştırır. HPC ve MEC temsillerinin çözümlemesi, nöro-esinli modellerin gerçek-dünya geçiş dinamiklerinden soyut yapıları kodlama ve yeniden kullanma potansiyelini daha da vurgular. Modelimizin bu örtük geçişleri çeşitli bağlamlarda yeniden kullanma yeteneği, yapısal genellemenin kritik rolünün altını çizer.

**Sınırlamalar.** Modelimizin birkaç sınırlaması vardır. Birincisi, bir bellek bankası eklenerek potansiyel olarak hafifletilebilecek otoregresif bileşik hatalara yatkındır. İkincisi, eğitim verisinden (insan videoları) önemli dağılımsal kayma sergileyen ölçütlerde başarım bozulur. Ayrıca birden çok bağımsız varlığı eşgüdümlemek önemli bir güçlük olarak kalır. Gelecek çalışma bu sorunu ele almak için hiyerarşik HPC-MEC yapılarını veya nesne-merkezli temsilleri araştıracaktır.

## Etki Beyanı

Bu makale, hedefi Makine Öğrenmesi alanını ilerletmek olan bir çalışma sunar. Çalışmamızın birçok olası toplumsal sonucu vardır; bunlardan hiçbirinin özellikle vurgulanması gerektiğini düşünmüyoruz.

*(Teşekkürler: Çin Ulusal Doğa Bilimleri Vakfı ve Ulusal Anahtar Ar-Ge Programı fonları; çevrilmemiştir.)*

## Ek A. Model Ayrıntıları

### A.1 Model tasarım güdüsü

Modelimiz sinirbilimle yönlendirilen ve en gelişkin derin öğrenme modülleriyle gerçeklenen, beyinden esinli bir çerçevedir.

İçerik yolunun (HPC) yapı yolundan (MEC) hiyerarşik ayrımı doğrudan hesaplamalı sinirbilimdeki yerleşik kuramlardan esinlenir. Etiketsiz videodan öğrenme için ters dinamik modeliyle öğrenilmiş bir örtük geçiş uzayı kullanmak, bu alandaki birçok taban çizgisinin benimsediği yaygın ve etkili bir çerçevedir. Çalışmamız bu sağlam temel üzerine kurulur. Bu çerçeve içinde bileşen seçimlerimiz kasıtlıdır. MEC'in yol bütünleme rolü, ızgara hücrelerinin klasik bir hesaplamalı modeli olan Sürekli Çekici Sinir Ağı (CANN) ile gerçeklenir [gardnerToroidalTopologyPopulation2022, mcnaughtonPathIntegrationNeural2006a, fuhsSpinGlassModel2006a, burgessOscillatoryInterferenceModel2007a]. Örtük geçişler, beyincik kuramlarında kökleşmiş standart bir yaklaşım olan ters dinamik modeliyle çıkarılır [wolpertInternalModelsCerebellum1998].

Son olarak bu işlevsel roller için yüksek başarımı sağlamak üzere belirli en gelişkin gerçeklemeleri seçeriz. Önceden eğitilmiş görsel çok-ölçekli VQ-VAE [tianVisualAutoregressiveModeling2024] görme korteksinden işlenmiş girdiye benzer, kararlı ve yüksek kaliteli bir görsel temsil sağlar. Uzay-zaman Transformer [bruceGenieGenerativeInteractive2024, yeLatentActionPretraining2024] uzay ve zaman boyunca karmaşık bağımlılıkları modeller; gelecek durumları öngörmek için içerik ve yapı işaretlerini bütünleştirmek için tam gereken budur.

### A.2 Model parametreleri

Deneylerimizde kullanılan model parametreleri Tablo 6'da verilmiştir.

**Tablo 6.** Model parametreleri.

| Bileşen / Parametre | Değer |
| :-- | --: |
| **Girdi parametreleri** | |
| Girdi Kanalları | 3 |
| Girdi Görüntü Yüksekliği / Genişliği | 256 / 256 |
| VQ-VAE Kodlayıcı Derinliği | 16 |
| VQ-VAE Kodlayıcı Özellik Haritası Kanalları | 32 |
| VQ-VAE Kodlayıcı Özellik Haritası Yükseklik / Genişlik | 16 / 16 |
| Yama Boyutu (yükseklik, genişlik) | 4 (4, 4) |
| **HPC Modeli** | |
| HPC Gizli Boyutu (toplam) | 8192 |
| Yama Başına Gizli Boyut | 512 |
| Uzamsal / Zamansal Transformer Derinliği | 4 / 4 |
| **MEC Modeli** | |
| MEC Gizli Boyutu (toplam) | 4096 |
| Yama Başına Gizli Boyut | 256 |
| Uzamsal / Zamansal Transformer Derinliği | 4 / 4 |
| **Ters Dünya Modeli** | |
| Geçiş Boyutu | 2048 |
| Yama Başına Geçiş Boyutu | 128 |
| $f_{\text{inverse}}$ Artık Blokları | 2 |
| $f_{\text{forward}}$ Artık Blokları | 4 |

### A.3 Önceden eğitilmiş kodlayıcı ayrıntıları

Görsel özellikleri çıkarmak için VAR modelinden önceden eğitilmiş çok-ölçekli VQ-VAE'yi (derinlik=16) kullanırız. Kullandığımız özellik haritası $\hat{f}$ çok-ölçekli vektör nicemleme katmanlarının çıktılarının toplamıdır. Bu özellik haritası doğrudan modelimize beslenir. Bu tasarım kasıtlıdır: HPC-MEC devresinin görme korteksinden ön-işlenmiş bilgiyi nasıl aldığını benzetir ve görevi tümüyle örtük uzay içinde bir öngörü problemi olarak çerçeveler (JEPA'ya [lecunPathAutonomousMachine] benzer); yani modelimiz piksel düzeyinde yeniden-kurma yapmaz.

### A.4 CANN Dinamikleri ve Yol Bütünleme

MEC'teki ızgara hücrelerinin rolünden esinlenerek geçiş dinamiklerini sürekli çekici sinir ağıyla (CANN) modelleriz. CANN, bilgiyi etkinlik örüntüsünde kararlı, sürekli bir temsilde tutmak için tasarlanmış özel bir tekrarlayan sinir ağı türüdür. Ayrık, yapısız örüntüleri saklayan klasik çekici ağların aksine CANN'lar metrik ilişkilerle örgütlenmiş yapılı örüntüleri kodlama yetenekleriyle ayrışır. Bu geometrik yapı CANN'ın bir sistemin durumunu kararlı, yerelleşmiş bir "etkinlik yumrusu" olarak sürdürmesini sağlar. Yol bütünleme, çıkarılan örtük geçişi bu yumruyu ağın metrik eksenleri boyunca denetimli biçimde kaydıran bir hız işleci olarak kullanarak sağlanır. Kararlı bir durumu sürdürme ve onu bir hız girdisiyle sistematik dönüştürme yeteneği, CANN'ın bir yolu bütünlemesini ve sonraki durumun yapısını öngörmesini sağlar.

Modelimizde MEC gömmeleri $\boldsymbol{g}$ yüksek boyutlu uzayda soyut yapıları temsil eder [klukas2020efficient]. Birden çok bir-boyutlu CANN birleştirildiğinde ortak durum uzayları $N$-boyutlu sürekli bir manifold oluşturur [burgess2014controlling]. Bu modüler temsil, her modülün örtük geçiş girdileriyle sürüldüğü uzamsal dinamiklerin ayrışımını mümkün kılar.

MEC modülümüzde soyut temsilleri kodlamak ve yol bütünleme yapmak için gerçeklenen CANN dinamiklerini biçimselleştiririz. Özellikle CANN'ların klasik diferansiyel denklem tabanlı formülasyonu ile ayrık-zamanlı, öğrenilebilir gerçeklememiz arasında bağlantı kurarız.

Bir-boyutlu CANN'ın kanonik dinamiği şu birinci-derece diferansiyel denklemle tarif edilir:

$$\tau \frac{d\mathbf{u}(t)}{dt} = -\mathbf{u}(t) + \mathbf{W}_r \mathbf{r}(t) + \mathbf{W}_{\text{in}} \mathbf{v}(t) \tag{A1}$$

Burada: $\mathbf{u}(t)$ ağın gizli durumu; $\mathbf{r}(t)$ doğrusal olmayan bir etkinleştirme fonksiyonuyla gizli durumdan türetilen anlık sinirsel ateşleme hızı $\mathbf{r}(t)=H(\mathbf{u}(t))$; $\mathbf{v}(t)$ dış hareket girdisi (örn. hız); $\mathbf{W}_r$ ve $\mathbf{W}_{\text{in}}$ sırasıyla tekrarlayan ve girdi ağırlık matrisleri; $\tau$ bir zaman sabitidir. Bu formülasyon hem tekrarlayan geri bildirimle kendini-sürdüren etkinliği hem dış hareket ipuçlarıyla bozulmayı destekler. Sayısal modellemeyi mümkün kılmak için Denklem A1 ileri Euler bütünlemesiyle ayrıklaştırılır:

$$\mathbf{u}_{t+1} = (1 - \alpha)\mathbf{u}_t + \alpha \left( \mathbf{W}_r \mathbf{r}_t + \mathbf{W}_{\text{in}} \mathbf{v}_t \right) \tag{A2}$$

burada $\alpha = \Delta t / \tau$. Basitlik için Gauss yumru profillerinin açık modellemesini atlar ve yumru merkezlerini çıkarmak için doğrusal olmayan bir fonksiyon kullanırız: $\mathbf{g}(t) = \sigma(\mathbf{r}(t))$. $\mathbf{W}_r$'yi açıkça tasarlamak yerine sürekli çekici dinamiklerini bir zamansal dikkat mekanizmasıyla öğreniriz ve $\mathbf{g}$ üzerinde ikinci-derece zamansal yumuşatma kaybıyla yapısal düzenlilik getiririz. Bu kayıp örtük uzayda yüksek ivmeyi cezalandırır:

$$\mathcal{L}_{\text{smooth}} = \frac{1}{B(T - 2)} \sum_{b=1}^{B} \sum_{t=1}^{T-2} \left\| \mathbf{g}_{b,t+2} - 2\mathbf{g}_{b,t+1} + \mathbf{g}_{b,t} \right\|^2 \tag{A3}$$

Burada $B$ yığın boyutu ve $T$ dizi uzunluğudur. Nedensel maskeli zamansal dikkat geçmiş bilgiyi mevcut duruma bütünleştirir ve ızgara yörüngesinde düşük eğriliği teşvik eder; uzayda sürekli hareketin iç durumda yumuşak değişimlere yol açması gerektiği fiziksel sezgisini yansıtır. Ateşleme hızları yerine yumru merkezlerinin evrimine odaklanarak yol bütünleme güncellemesini şöyle gerçekleriz:

$$\mathbf{g}_{t+1} = \mathbf{g}_t \oplus f(\mathbf{g}_t, \mathbf{z}_t) \tag{A4}$$

Burada $\mathbf{z}_t$ örtük geçişi, $f(\cdot)$ ise $\mathbf{z}_t$'nin doğurduğu dinamiği modelleyen öğrenilebilir bir fonksiyonu gösterir. $\mathbf{g}$'nin tekrarlayan dinamikleri, zaman boyunca sürekliliği sürdürmek ve çekici manifold yapısını korumak için zamansal dikkat yapısına gömülüdür.

### A.5 Duyarlılık çözümlemesi

CANN modül sayısı (MEC boyutu) için mevcut modelimiz 4096 modül kullanır (yama başına 256). Bunu 2048'e indirmek yine sahneye özgü dinamikleri kodlamaya izin verir ama ayrıntı kaybı ve üretilen görüntülerde bulanıklık gözle görülür biçimde artar. 1024'e daha ileri indirme bu sorunu ağırlaştırır ve eğitim sırasında yakınsama güçlüklerine yol açar.

Örtük geçiş boyutu için şu anda 2048 boyut kullanırız. Modelin 1024 boyutla hâlâ bir sonraki çerçeveyi öngörebildiğini ama üretim kalitesinin bozulduğunu buluruz. Örtük geçiş boyutunu daha da sıkıştırmak yakınsamayı çok güçleştirir ve çoğu zaman modelin sadece önceki çerçeveyi öngörü olarak verdiği önemsiz bir çözümü öğrenmesine yol açar.

### A.6 Görsel geri bildirim ayrıntıları

Yol bütünleme tek başına zamanla hata biriktirdiğinden, görsel çıkarım yolu kaymayı hafifletmek için düzeltici geri bildirim sağlar. Özellikle görsel geri bildirim yokluğunda model sonraki durumu mevcut öngörü $\boldsymbol{g}^{gen}_t$'ye dayalı yol bütünlemeyle öngörür: $\boldsymbol{g}^{gen}_{t+1} = \boldsymbol{g}^{gen}_{t} \oplus f_{\text{forward}}(\boldsymbol{z}_t, \boldsymbol{g}^{gen}_{t})$. Görsel girdi mevcut olduğunda model, sonraki durumu öngörmek için mevcut durumu gözlemden çıkarılan MEC gömmesi $\boldsymbol{g}_t^{inf}$ ile düzeltir: $\boldsymbol{g}^{gen}_{t+1} = \boldsymbol{g}^{inf}_{t} \oplus f_{\text{forward}}(\boldsymbol{z}_t, \boldsymbol{g}^{inf}_{t})$. Bu güncelleme kararsızlık getirmez; çünkü $\boldsymbol{g}_t^{inf}$ ve $\boldsymbol{g}_t^{gen}$ aynı örtük uzaydadır. Hizalama kaybı $\mathcal{L}_{\text{alignment}}(\boldsymbol{g}_{2:T}^{\text{inf}}, \boldsymbol{g}_{2:T}^{\text{gen}})$ yalnızca ters modeli eğitmekle kalmaz, geri bildirim sırasında $\boldsymbol{g}_t^{gen}$'i $\boldsymbol{g}_t^{inf}$ ile değiştirmenin kararlı kalmasını da sağlar. Dahası görsel geri bildirim yalnızca model yeterince eğitildikten sonra, iki gömme iyi hizalıyken kullanılır. Sonuç olarak, model uzun dizilerde eğitilmemiş olsa bile düzeltme mekanizması zamanla otoregresif olarak doğru öngörüler üretmesine izin verir.

## Ek B. Model Eğitim Ayrıntıları

### B.1 Kayıp fonksiyonları

Her eğitim aşaması için tasarlanan kayıp fonksiyonlarını ayrıntılı ele alırız:

- **Yeniden-kurma kaybı:** Öğrenmeyi hızlandırmak için gözlem gömmeleri ile üç farklı üretken model öngörüsü arasında kayıplar ekleriz. Yeniden kurulan gözlem gömmeleri $\boldsymbol{s}^{\text{recon}}$ doğrudan çıkarılan $\boldsymbol{p}^{\text{inf}}$ veya $\boldsymbol{g}^{\text{inf}}$ gömmelerinden üretilebilir; $\boldsymbol{s}^{\text{gen}}$ ise üretken yoldan üretilir. Aşama 1'de yeniden-kurma kaybını hesaplamak için $\boldsymbol{p}_{1:T}^{\text{inf}} \rightarrow \boldsymbol{s}_{1:T}^{\text{recon}}$ ve $\boldsymbol{g}_{1:T}^{\text{inf}} \rightarrow \boldsymbol{p}_{1:T}^{\text{inf}} \rightarrow \boldsymbol{s}_{1:T}^{\text{recon}}$ kullanırız. Aşama 2 ve 3'te modelin geçiş dinamikleri bir sonraki üretilen gözlem gömmelerini $\boldsymbol{g}_{2:T}^{\text{gen}} \rightarrow \boldsymbol{p}_{2:T}^{\text{gen}} \rightarrow \boldsymbol{s}_{2:T}^{\text{gen}}$ öngörür ve yeniden-kurma kaybını hesaplamak için $\boldsymbol{s}_{2:T}^{\text{gen}}$'i kullanırız.
- **Hizalama kaybı:** $\mathcal{L}_{\text{alignment}}$, çıkarım ve üretimden gelen örtük temsilleri hizalamak için kullanılır. Bu kayıp TEM'den [TolmanEichenbaumMachineUnifying2020] esinlenir; çıkarılan HPC gömmeleri $\boldsymbol{p}^{\text{inf}}$ üretilen HPC gömmeleri $\boldsymbol{p}^{\text{gen}}$ ile, çıkarılan MEC gömmeleri $\boldsymbol{g}^{\text{inf}}$ üretilen MEC gömmeleri $\boldsymbol{g}^{\text{gen}}$ ile hizalanır.
- **Geçiş kaybı:** $\mathcal{L}_{\text{transition}}$, öngörülen $\Delta \boldsymbol{g}_t^{\text{gen}} = f_{\text{forward}}(\boldsymbol{z}_t, \boldsymbol{g}_t^{\text{gen}})$ yer değiştirme vektörünü $t$ zaman adımındaki gerçek yer değiştirme vektörü $\Delta \boldsymbol{g}_t^{\text{inf}}$'e yakın olmaya kısıtlar. Geçiş kaybı, öngörülen ve gerçek yer değiştirme vektörleri arasındaki ortalama kare hatasıyla (MSE) hesaplanır. Öngörülen yer değiştirme vektörünün gerçekle hizalı olmasını sağlamak için kosinüs benzerliği de kullanılır. Eğitim sırasında $\boldsymbol{g}$ hizalama kaybının öngörülen $\boldsymbol{g}_{t+1}^{\text{gen}}$'i $\boldsymbol{g}_{t+1}^{\text{inf}}$'ten çok $\boldsymbol{g}_{t}^{\text{inf}}$'e yaklaştırabileceği yerel bir minimuma düşmesini önlemek için, öngörülen $\boldsymbol{g}_{t+1}^{\text{gen}}$ ile $\boldsymbol{g}_{t}^{\text{inf}}$ arasındaki mesafeyi kısıtlayan ek bir karşıtsal kayıp terimi ekleriz. Bu kosinüs benzerliğiyle gerçeklenir. Kaybın genel biçimi:
$$\mathcal{L}_{\text{transition}} = \text{MSE}(\Delta \boldsymbol{g}_{1:T-1}^{\text{gen}}, \Delta \boldsymbol{g}_{1:T-1}^{\text{inf}}) + \alpha \cdot \left( 1 - \text{CosSim}(\Delta \boldsymbol{g}_{1:T-1}^{\text{gen}}, \Delta \boldsymbol{g}_{1:T-1}^{\text{inf}}) \right) + \beta \cdot \text{CosSim}(\boldsymbol{g}_{1:T}^{\text{gen}}, \boldsymbol{g}_{0:T-1}^{\text{inf}})$$
burada $\alpha$ ve $\beta$ kosinüs benzerliği terimlerinin göreli önemini denetleyen hiperparametrelerdir.
- **Düzenlileştirme kaybı:** Çöküşü önlemek için $\boldsymbol{p}_t^{\text{inf}}$ ve $\boldsymbol{g}_t^{\text{inf}}$'i düzenlileştirmek üzere VICReg amaçlarını [bardes2022vicreg] kullanırız. Varyans kaybı modeli örtük uzayda yığınlar boyunca belirli bir varyans düzeyi korumaya teşvik eder; kovaryans kaybı örtük uzayın farklı boyutları arasında yüksek kovaryansı cezalandırır. Düzenlileştirme kaybının genel biçimi:
$$\mathcal{L}_{\text{var}}(Z, \gamma) = \frac{1}{TD} \sum_{t=0}^{T} \sum_{j=0}^{D} \max\left(0, \gamma - \sqrt{\text{Var}(Z_{:,t,j}) + \varepsilon} \right)$$
$$\mathcal{L}_{\text{variance}} = \mathcal{L}_{\text{var}}(\boldsymbol{g}^{\text{inf}}, \gamma=0.5) + \mathcal{L}_{\text{var}}(\boldsymbol{p}^{\text{inf}}, \gamma=0.5)$$
$$\mathcal{L}_{\text{cov}}(Z) = \frac{1}{D(D-1)} \sum_{i \neq j} (\text{Cov}(Z)_{ij})^2, \quad \mathcal{L}_{\text{covariance}} = \mathcal{L}_{\text{cov}}(\boldsymbol{g}^{\text{inf}}) + \mathcal{L}_{\text{cov}}(\boldsymbol{p}^{\text{inf}})$$
$$\mathcal{L}_{\text{regularization}} = \phi \cdot \mathcal{L}_{\text{variance}} + \psi \cdot \mathcal{L}_{\text{covariance}} + \omega \cdot \mathcal{L}_{\text{smooth}}$$
burada $\phi$, $\psi$ ve $\omega$ sırasıyla varyans, kovaryans ve yumuşatma (Denk. A3) kayıplarının göreli önemini denetleyen hiperparametrelerdir.

### B.2 Eğitim hiperparametreleri

Deneylerimizde kullanılan eğitim hiperparametreleri Tablo 7'de verilmiştir.

**Tablo 7.** Eğitim hiperparametreleri.

| Aşama | Parametre | Değer |
| :-- | :-- | --: |
| Sabit | Öğrenme Oranı | 1e-4 |
| | Eniyileyici | AdamW |
| | Ağırlık Sönümü | 1e-4 |
| | Beta'lar | (0.9, 0.999) |
| | Gradyan Kırpma | 0.1 |
| | Öğrenme oranı çizelgeleyici | CosineAnnealingLR |
| | Dönem | 10 |
| Aşama 1 | Yığın Boyutu | 32 |
| | Dizi Uzunluğu | 8 |
| | $\mathcal{L}_{\text{recon}}^{\boldsymbol{p}^{\text{inf}}\rightarrow \boldsymbol{s}^{\text{rec}}}$ Ağırlığı | 5.0 |
| | $\mathcal{L}_{\text{recon}}^{\boldsymbol{g}^{\text{inf}}\rightarrow \boldsymbol{s}^{\text{rec}}}$ Ağırlığı | 5.0 |
| | $\mathcal{L}_{\text{alignment}}^{\boldsymbol{p}}$ Ağırlığı | 0.22 |
| | $\phi$ (varyans kaybı) / $\psi$ (kovaryans kaybı) / $\omega$ (yumuşatma kaybı) | 0.01 / 0.01 / 0.01 |
| Aşama 2/3 | Yığın Boyutu | 224/32 |
| | Dizi Uzunluğu | 2/8 |
| | $\mathcal{L}_{\text{recon}}^{\boldsymbol{p}^{\text{inf}}\rightarrow \boldsymbol{s}^{\text{rec}}}$ / $\mathcal{L}_{\text{recon}}^{\boldsymbol{g}^{\text{inf}}\rightarrow \boldsymbol{s}^{\text{rec}}}$ Ağırlığı | 5.0 / 5.0 |
| | $\mathcal{L}_{\text{gen}}^{\boldsymbol{g}^{\text{gen}}\rightarrow \boldsymbol{s}^{\text{gen}}}$ Ağırlığı | 3.0 |
| | $\mathcal{L}_{\text{alignment}}^{\boldsymbol{p}}$ / $\mathcal{L}_{\text{alignment}}^{\boldsymbol{g}}$ Ağırlığı | 1.0 / 5.0 |
| | $\alpha$ (geçiş kaybı) / $\beta$ (karşıtsal kayıp) | 1 / 1 |
| | $\phi$ (varyans kaybı) / $\psi$ (kovaryans kaybı) | 0.05 / 0.05 |

### B.3 Hesaplama gereksinimleri

Model büyük bir veri kümesinde (SSv2, 220.000 video) eğitilir; eğitim 6-8 saat gerektirir (10 dönem, 3 A100 GPU ile paralel eğitim). Görece küçük uzay-zaman Transformer ve çok-ölçekli VQ-VAE nedeniyle çıkarım süresi çok hızlıdır; asgarî yük doğar. Şimdiye kadar model boyutunu artırmak önemli zaman artışlarına yol açmamıştır.

## Ek C. Veri Kümesi Ayrıntıları

Gerçek-dünya videolarından soyut örtük geçişler öğrenmeyi hedefleriz. 2B oyunlardan veya robot gösterimlerinden farklı olarak gerçek-dünya insan videoları açık eylem etiketleri olmaksızın çeşitli geçişler sergiler. Büyük ölçekli insan video veri kümelerinde ön-eğitimin modelimizin görülmemiş veriye genelleşen çok yönlü örtük geçişler öğrenmesini mümkün kılıp kılmadığını araştırırız. Şu veri kümelerini kullanırız.

### C.1 Something-Something V2

Something-Something V2 (SSv2) [DBLP:journals/corr/GoyalKMMWKHFYMH17], insanların gündelik nesnelerle eylemler yaptığı 220.847 video klip içerir. Bu büyük ölçekli gerçek-dünya insan videolarını modelimizi eğitmek için kullanır ve [DBLP:journals/corr/GoyalKMMWKHFYMH17]'de kurulan aynı eğitim/doğrulama/test bölünmelerini koruruz.

### C.2 3B nesne ilkel dönüşüm veri kümeleri

**Dönüş veri kümeleri.** Modeli değerlendirmek ve çözümlemek için üç farklı dönüş veri kümesi kullanırız. COIL-100 [nene1996columbia], farklı açılardan görülen 100 nesnenin görüntülerini içerir. MIRO [kanezaki2018rotationnet], farklı bir eksen boyunca 3B nesne dönüşlerinin başka bir veri kümesidir.

Ayrıca günlük 216 kategoriden 5911 nesne, nesne başına 72 farklı görünümlü sentetik bir 3B nesne dönüş veri kümesi yaratırız. Yüksek kaliteli gerçek-taranmış ağların bir veri kümesi olan OmniObject3D'den [wu2023omniobject3d] ağları 3B dönüş nesneleri yaratmak için render etmek üzere Blender kullanırız. Her nesne ağı 0°'de başlatılır ve dikey eksen etrafında 5° artışlarla 360° döndürülür; nesne başına 72 render edilmiş görünüm verir. Veri kümemiz uzun-kuyruklu bir dağılımla 216 kategoriyi kapsar ve günlük nesne âlemlerinin çoğunu içerir. Resmî web sitesinde sağlanan bütün ham taramaları dahil ederiz; kategori ve nesne sayıları özgün OmniObject3D makalesinde bildirilenlerden biraz farklı olabilir. Render kodu [deitke2023objaverse] tarafından sağlanan gerçeklemeden uyarlanmıştır.

**İlkel dönüşüm veri kümeleri.** OmniObject3D kullanarak farklı ilkel dönüşümler (dönüş, yatay/dikey öteleme ve ölçekleme) içeren dizilerle yeni bir veri kümesi kurarız. Her dizi, kategorisi, başlangıç konumu, yönelimi ve boyutu rastgele seçilmiş bir nesne içerir.

### C.3 Simüle ölçütler

Modelimizi, gerçek-dünya verisinde eğitilmiş modelin sanal ortamlara aktarılıp aktarılamayacağını araştırmak için simüle ölçütlerde de değerlendiririz. Dört farklı simüle veri kümesi kullanırız: Franka Kitchen [gupta2019relay], Block Pushing [florence2022implicit], Push-T [chi2023diffusion] ve LIBERO Goal [liu2023libero].

### C.4 3B nesne dönüş veri kümelerinden dizi kurma

Model tek nesne görünümleri yerine görüntü dizileri girdisi aldığından, 3B nesne dönüş veri kümelerindeki görüntüleri kullanarak diziler kurmamız gerekir. Üç 3B nesne dönüş veri kümesi kullanırız. Burada bu veri kümelerindeki farklı nesne görünümlerinden dizilerin nasıl kurulduğunu tarif ederiz.

Her dizi tek bir nesnenin çerçevelerinden oluşur. Herhangi iki bitişik çerçeve arasında ikincisi birincinin döndürülmüş sürümüdür. Buradaki geçiş dönüş açısına karşılık gelir: pozitif değer saat yönünde, negatif değer saat yönünün tersine dönüşü gösterir. Dolayısıyla bir başlangıç çerçevesi ve bir dönüş geçişleri dizisi tanımlayıp karşılık gelen görüntüleri dönüş veri kümelerinden alarak bir dizi kurarız.

Bazı deneylerin dizi kurma ayarları:
- Bölüm 5.1 Şekil 4(C)'de göreli dönüş geçişleri $5^{\circ}$'ye sabitlenir; COIL-100'deki nesneler çerçeve başına dikey eksen etrafında saat yönünde $5^{\circ}$ döndürülür.
- Bölüm 5.2'de farklı sabit parametreler kullanırız: Şekil 5(B), (C) ve (F) sırasıyla adım başına $30^{\circ}$, $20^{\circ}$ ve $30^{\circ}$ dönüş açıları kullanır; Şekil 5(G) adım başına $0.85$ sabit ölçekleme kullanır.
- Bölüm 5.3 Tablo 3'te göreli dönüş geçişleri $-90^{\circ}$ ile $90^{\circ}$ arasından rastgele örneklenir.
- Bölüm 5.4 Tablo 4'te göreli dönüş geçişleri $-30^{\circ}$ ile $30^{\circ}$ arasından rastgele örneklenir.

## Ek D. Taban Çizgisi Ek Sonuçları

### D.1 Hesaplama ve duvar-saati süresi karşılaştırması

**Tablo 8.** Farklı modeller arasında Çıkarım FPS'i ve yığın başına ortalama sürenin niceliksel karşılaştırması.

| Model | LAPA | Moto | AdaWorld(LAM) | Bizim model |
| :-- | --: | --: | --: | --: |
| Çıkarım FPS | 205.33 | 55.22 | 35.60 | 84.00 |
| Yığın başına ort. süre (s) | 0.623 | 2.318 | 3.595 | 1.523 |

Çıkarım verimini adil karşılaştırmak için tek bir NVIDIA A100 GPU üzerinde bir dizi deney yürütürüz. Tutarlı 16 yığın boyutu ve 8 dizi uzunluğu kullanırız; Çıkarım FPS'ini (yüksek daha iyi) ve Yığın Başına Ortalama Süreyi (düşük daha iyi) hesaplamak için sonuçları 100 yığın üzerinden ortalarız. HPC-MEC modülümüz neredeyse hiç hesaplama yükü eklemez. Bu yüksek verimin nedeni modülümüzün tümüyle VQ-VAE kodlayıcısı ile kod çözücüsü arasındaki örtük uzayda işlemesidir. Ayrıca tam modelimizin çıkarım hızı Moto ve AdaWorld(LAM)'dan hızlıdır. Bu çözümlemenin modelimizin avantajlarının makul olmayan bir hesaplama cezası getirmeden elde edildiğini gösterdiğine inanırız.

## Ek E. Ablasyon Çalışması Ek Sonuçları

### E.1 Örtük geçiş geçerliliği deneyi

Örtük geçişlerin geçiş dinamiklerini yönetmedeki rolünü incelemek için başka bir ablasyon çalışması yaparız. Modelimizde geçiş dinamiklerinin şöyle tanımlandığını hatırlayalım: $\mathbf{g}_{t+1} = \mathbf{g}_t \oplus f_{\text{forward}}(\mathbf{z}_t, \mathbf{g}_t)$; burada $\mathbf{z}_t$ örtük geçişi gösterir ve $f_{\text{forward}}$ yer değiştirme vektörü $\Delta \mathbf{g}_t$'yi üretmek için içerik bilgisini $\mathbf{z}_t$'ye bütünleştirir. Ablasyon çalışmamız iki yönde odaklanır: örtük geçiş ve içerik bağlama. Birincisi, ters modelin girdisini sıfıra ayarlayarak bozar, sonra hem tek-adımlı hem otoregresif öngörüleri yaparız (Şekil 6(A, B)). Tek-adımlı öngörüde modelin önceki çerçeveyi basitçe kopyalamaya çöktüğünü, otoregresif ayarda yalnızca ilk çerçevenin korunduğunu ve dizinin anlamlı geçiş göstermediğini gözleriz. İkincisi, $\mathbf{z}_t$'nin yalnızca sıfır girdiyle birleştirilerek $\Delta \mathbf{g}_t$ üretmesine izin vererek içerik bağlamayı bozarız (Şekil 6(C, D)). Bu durumda tek-adımlı öngörü genel olarak genel geçiş dinamiklerini korur ama üretilen ayrıntılar bozulur; karşılaştırıldığında otoregresif öngörü daha da kötü sonuç verir. Bu bulgular, örtük geçişin esas olarak ana geçişleri sürdüğünü, içerik bağlamanın ise ayrıntılı, sahneye özgü bilgiyi yeniden kurmak için gerekli olduğunu gösterir.

**Şekil 6.** **Örtük geçiş geçerliliği deneyi.** (A) Ters model sıfır girdi alır; tek-adımlı öngörü için anlamsız örtük geçişler doğar. (B) Otoregresyon için anlamsız örtük geçiş. (C) $f_{\text{forward}}$ örtük geçişleri anlamsız içerik bilgisiyle birleştirir ve tek-adımlı öngörü yapar. (D) Anlamsız içerik bilgisi örtük geçişlere bağlanır ve otoregresyon yapar.

## Ek F. Ek Sonuçlar

### F.1 Öngörü sonuçları

**Dağılım-dışı dönüş veri kümelerinde tek-adımlı öngörü.** Modelin birkaç dönüş veri kümesindeki öngörüsünün daha çok görselleştirmesini sunarız. Sonuçlar Şekil 7'de gösterilmiştir.

**Şekil 7.** **Dönüş veri kümelerinde tek-adımlı öngörü.** (A, B) COIL-100 veri kümesinde değerlendirilen tek-adımlı öngörü. (C, D) MIRO veri kümesinde değerlendirilen tek-adımlı öngörü.

**Dağılım-dışı simüle ortamlarda tek-adımlı öngörü.** İnsan videolarından önemli dağılımsal kaymaları olan simüle ölçütlerde tek-adımlı öngörü sonuçlarını Şekil 8'de sunarız. Model daha doğal Franka Kitchen'da [gupta2019relay] sağlam, Push-T [chi2023diffusion] ve Block Pushing [florence2022implicit] gibi yapay ortamlarda daha az etkili çalışır.

**Şekil 8.** **Simüle ortamlarda tek-adımlı öngörü.** (A) Franka Kitchen'da değerlendirilen tek-adımlı öngörü. (B) LIBERO Goal. (C) Block Pushing. (D) Push-T.

### F.2 Örtük geçiş yeniden kullanımı sonuçları

**Görülmemiş 3B dönüş veri kümesinde tek-adımlı ve otoregresif örtük geçiş yeniden kullanımı.** Sağlamlığı doğrulamak için dağılım-dışı 3B dönüş veri kümesindeki ek sonuçları Şekil 9'da sunarız. Burada kübik nesneleri inceleriz; bir kaynak diziden gelen örtük geçişler başka bir nesnenin çerçevelerini etkili dönüştürür ve kaynağın dönüş dinamikleriyle iyi hizalanır.

**Şekil 9.** **OmniRotation'da örtük geçiş aktarımı.** (A, B) OmniRotation veri kümesinde kübik nesneler için örtük geçişlerin tek-adımlı ve otoregresif yeniden kullanımını gösteren iki örnek.

**Görülmemiş yapay ortam Franka Kitchen'da tek-adımlı ve otoregresif örtük geçiş yeniden kullanımı.** Bölüm 4'te modelin yapay ortamlarda değişen bağlamlarda yapılan aynı eylemin dizilerinden paylaşılan örtük geçişleri çıkarma yeteneğini gösteririz. Burada Franka Kitchen'da örtük geçişlerin tek-adımlı ve otoregresif yeniden kullanımının sonuçlarını sunarız (Şekil 10). Modelin eğitim veri kümesine kıyasla dağılım-dışı olan ortamlarda bile örtük geçişleri farklı bağlamlardaki farklı sahneler arasında etkili aktarabildiğini gözleriz. Ayrıca bu sonuçlar modelin yapay ortamlardan içerikten-bağımsız yapıları çıkarabildiğini düşündürür ve iyileştirilmiş bir kod çözücüyle üretim ve yeniden kullanım görevlerinde iyi başarım göstermesi potansiyeline inanırız.

**Şekil 10.** **Yapay ortamlarda örtük geçiş aktarımı.** (A) Franka Kitchen'da ardışık örtük geçişleri aktararak tek-adımlı öngörü. (B) Franka Kitchen'da ardışık örtük geçişleri aktararak otoregresif öngörü.

### F.3 Taban çizgisi karşılaştırmasının görselleştirilmesi

LAPA, Moto, AdaWorld(LAM) ve modelimizi kullanan tek-adımlı öngörünün ek görselleştirmesini sunarız. Sonuçlar Şekil 11'de gösterilmiştir. LAPA doğrudan piksel düzeyinde eniyilenir; yerel ayrıntıların daha güvenilir üretimiyle sonuçlanır. Buna karşılık modelimiz örtük temsil uzayında eniyilenir; büyük eylem kaynaklı değişimler altında bile genel üretim kalitesini daha iyi korumayı mümkün kılar. Bu gibi senaryolarda LAPA'nın üretim kalitesi bozulma eğilimi gösterirken modelimiz sağlam kalır. Moto ve AdaWorld(LAM) Franka Kitchen veri kümesinde genellemede başarısız olur.

**Şekil 11.** **Taban çizgileri ve modelimiz arasında üretim kalitesi karşılaştırması.** (A) SSv2 veri kümesinde tek-adımlı öngörü görselleştirmesi. (B) Franka Kitchen veri kümesinde tek-adımlı öngörü görselleştirmesi.

**Şekil 12–14.** **Taban çizgileri ve modelimiz arasında örtük geçiş aktarımı karşılaştırması.** (12) SSv2'de farklı sahneler arasında tek-adımlı örtük geçiş aktarımı, Şekil 5(A)'daki aynı örnekler. (13) Ardışık örtük geçişleri aktararak tek-adımlı ve otoregresif öngörü, Şekil 5(B, C)'deki aynı örnekler. (14) (A)(B) SSv2'de örtük geçişlerin otoregresif yeniden kullanımı, Şekil 5(D, E)'deki aynı örnekler; (C)(D) nesne kategorileri arasında dönüş ve ölçekleme dinamiklerinde örtük geçişlerin otoregresif yeniden kullanımı, Şekil 5(F, G)'deki aynı örnekler.

## Ek G. Öğrenilmiş Örtük Uzay Ayrıntıları

### G.1 Boyut indirgeme deneyi

Bölüm 4.1 Şekil 3(A, D)'de her UMAP görselleştirmesi tek bir nesnenin gömmelerini gösterir. Şekil 3(B)'de her UMAP şekli 10 kabak, 7 kırmızı elma ve 3 sarı elmanın gömmelerini içerir. Şekil 3(A, B, D)'de geçiş adım başına $5^{\circ}$'ye sabitlenmiştir. Nesneler dikey eksen etrafında saat yönünde döner; (A)'daki diziler iki tam dönüşü, (B, D)'dekiler her biri bir tam dönüşü tamamlar.

### G.2 Kategori sınıflandırma kod çözücüsü

Şekil 3(C)'de gösterilen kod çözücü sınıf-içi yapısal paylaşım deneyinde, OmniObject3D'den [wu2023omniobject3d] render edilen 3B nesne dönüş veri kümesinden 50 kategori rastgele seçip her kategoriden 10 nesne rastgele örnekleyerek 500 nesnelik bir alt küme kurarız. Sonra bu alt kümeyi kullanarak deneyi beş kez tekrarlarız. Her koşuda her kategorideki nesneleri %80 eğitim ve %20 test olarak bölerek hiçbir nesnenin her iki kümede de görünmemesini sağlarız. Eğitim ve test örnekleri, bu eğitim ve test nesnelerinin dizilerinden çıkarılan zaman adımı başına gömmelerdir.

Her nesne bir dönüş dizisi kurmak için kullanılır. Özellikle nesneyi rastgele bir görünümde başlatır ve adım başına $5^\circ$ sabit geçiş uygularız; yani nesne her zaman adımında dikey eksen etrafında saat yönünde $5^\circ$ döndürülür, tam $360^\circ$ dönüş tamamlanana dek. Bu nesne başına 72 çerçevelik dizi verir. Dizi, kod çözücü eğitimi için girdi olarak hizmet eden $\mathbf{p}$ ve $\mathbf{g}$ gömmelerini çıkarmak için Hipokampal-Entorinal-Esinli Eşleme Modelimizden geçirilir.

Kod çözücü, [yeLatentActionPretraining2024]'te kullanılan basit örtük geçiş kod çözücüsünden uyarlanmıştır. ReLU etkinleştirmeli 128 birimli iki gizli katmandan oluşan bir MLP'dir. PyTorch'un öntanımlı parametreleriyle AdamW eniyileyicisiyle eğitilir. Çapraz-entropi kaybı, 128 yığın boyutu ve 30 dönem eğitim kullanırız. Şekil 3(C), beş koşu üzerinden ortalama eğitim ve test doğruluğunu bildirir; gölgeli alan standart hatayı gösterir.

### G.3 Örtük geçiş çözme ayrıntıları

OmniObject3D kullanarak farklı dönüşümler (dönüş, yatay/dikey öteleme ve ölçekleme) içeren dizilerle yeni bir veri kümesi kurarız. Her dizi kategorisi, başlangıç konumu, yönelimi ve boyutu rastgele seçilmiş bir nesne içerir. Bu veri kümesini örtük geçişten dönüşüm türünü çözmek için kullanırız.

Örtük geçiş çözmede yaygın kullanılan eylem çözme paradigmasını [lapo] kullanırız. Önce modeli video dizisinden örtük geçiş temsilini çıkarmak için kullanır, sonra örtük geçişi $t$ zamanındaki mevcut geçişin türünü temsil eden $a_t$ dönüşüm türünü çözmek için kod çözücüye (MLP) besleriz. Her sınanan model için LAPO'yu [lapo] izleyerek bir örtük geçiş kod çözücüsü eğitiriz. Her kod çözücü 128 ve 128 gizli boyutlu tam bağlı bir ağ olarak gerçeklenir.

### G.4 Geçiş terkibi çözümlemesi

Burada ayrıca bir geçiş terkibi çözümlemesi sunarız. Çapraz bir hareketi (sağ-aşağı 45° hareket) bileşenleri olan yatay ve dikey ötelemelerin toplamına ayrıştırarak geçiş terkibini niceliksel sınarız. Kabak ve elma veri kümesini (Şekil 5(B)'den) kullanarak özgün çapraz örtük geçişten üretilen çerçeveleri, yatay ve dikey örtük geçiş gömmelerinin vektörel toplamından üretilen çerçevelerle karşılaştırırız. Şekil 15, terkibî örtük geçişlerle sürülen çerçevelerin gerçek örtük geçişlerle karşılaştırılabilir makul sonuçlar ürettiğini gösterir. Tablo 9'daki sonuçlar güçlü görsel ve niceliksel benzerliği gösterir:

**Tablo 9.** Gerçek örtük geçişleri terkip edilmiş örtük geçişlerle karşılaştıran geçiş terkibi sonuçları.

| Geçiş türü | SSIM ↑ | LPIPS ↓ |
| :-- | --: | --: |
| Gerçek örtük geçiş | 0.946 ± 0.021 | 0.076 ± 0.032 |
| Örtük geçiş $A + B$ | 0.944 ± 0.023 | 0.073 ± 0.032 |

Ölçüler istatistiksel olarak karşılaştırılabilirdir (t-testi: SSIM p=0.417, LPIPS p=0.402, n=160); bu, örtük geçiş uzayımızın yol bütünleme dinamikleri aracılığıyla doğrusal terkibi desteklediğine dair güçlü delil sağlar.

**Şekil 15.** **Geçiş terkibi sonuçları.** (A) Gerçek örtük geçişlerle sürülen tek-adımlı öngörü çerçeveleri. (B) İlgili dizilerden çıkarılan sağa ve aşağı örtük geçişlerin toplamıyla elde edilen terkibî örtük geçişlerle sürülen tek-adımlı öngörü çerçeveleri.

---

Kaynakça: orijinal `.bib` dosyası `orijinal/` dizinindedir; çevrilmemiştir.
