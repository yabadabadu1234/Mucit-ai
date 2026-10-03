# Program-Sentezi Ajanlarında Hiyerarşik Planlama İçin Tecritleri Öğrenmek (TheoryCoder-2)

Yazarlar: Zergham Ahmed, Kazuki Irie, Joshua B. Tenenbaum, Christopher J. Bates, Samuel J. Gershman — Harvard / MIT / IHMC / Kempner Enstitüsü — arXiv:2602.00929 — 31 Ocak 2026 (ICML 2026 şablonu)

> Tercüme notu: İngilizce LaTeX kaynağından çevrilmiştir. Formüller aynen; `[anahtar]` atıflardır. Şekil dosyaları depoda yoktur, yalnız başlıkları çevrilmiştir. LLM istemlerinin (Ek A) ve öğrenilmiş programların (Ek B) ham metni kod/model girdisi olduğu için çevrilmemiş, yalnız işlevleri Türkçe özetlenmiş ve kısa PDDL örnekleri aynen alınmıştır; tam metin `orijinal/main.tex`'te. "Abstraction" = tecrit; "operator" = işleç; "predicate" = yüklem (belirli bir durumun doğru/yanlış sınıflandırıcısı).

## Özet

İnsanlar tecritleri öğrenir ve görevler arası hızla genelleyecek biçimde verimli plan yapmak için onları kullanır; bu yetenek en gelişkin büyük dil modeli (LLM) ajanları ve derin pekiştirmeli öğrenme (RL) sistemleri için zor kalmaktadır. İnsanların tecritleri ve dünya bilgilerine dair sezgisel kuramları nasıl oluşturduğuna dair bilişsel bilimden esinlenen, TheoryCoder gibi Kurama Dayalı RL (TBRL) sistemleri, tecritlerin etkili kullanımıyla güçlü genelleme sergiler. Ancak insan tarafından sağlanan tecritlere büyük ölçüde dayanır ve tecrit öğrenme problemini yan geçerler. LLM'lerin bağlam-içi öğrenme yeteneğinden, elle belirtilmiş tecritlere dayanmak yerine, deneyimden tecritler sentezleyip bunları hiyerarşik bir planlama sürecine bütünleştirerek yeniden kullanılabilir tecritleri aktif olarak öğrenmek için yararlanan yeni bir TBRL ajanı olan TheoryCoder-2'yi tanıtıyoruz. BabyAI, Minihack ve Sokoban gibi VGDL oyunları dahil çeşitli ortamlarda deney yaparız. TheoryCoder-2'nin, klasik planlama alanı kurma, muhakeme tabanlı planlama ile artırılmış taban çizgisi LLM ajanlarından ve WorldCoder gibi önceki program-sentezi ajanlarından belirgin biçimde daha örnek-verimli olduğunu buluruz. TheoryCoder-2, önceki TBRL sistemlerinin aksine yalnızca asgarî insan istemleri gerektirirken taban çizgilerinin başarısız olduğu karmaşık görevleri çözebilir.

## 1. Giriş

İnsan zekâsının ayırt edici özelliği, soyut temsilleri düşük seviyeli bir dünya modeliyle birleştirerek hiyerarşik plan yapma yeteneğidir [koedinger1990abstract, balaguer2016neural, tomov2020discovery, correa2023humans]. Erken yaşta bebekler içerme ve destek gibi soyut yüklemleri anlar [casasola2002infant]; bu temsiller, insanların karmaşık alanlarda öngörme, işleme ve plan yapmasını sağlayan sonraki beceri gelişiminin temelini oluşturur. Örneğin içerme temsili, bir bardağa meyve suyu dökmek için soyut bir plan kurmak açısından esastır; bu plan fiziksel dünyaya dayalı somut bir plan kurmak için biyomekanik ve fiziğin düşük seviyeli bir modeliyle birleştirilebilir.

Etkileyici ilerlemeye rağmen modern yapay zekâ (AI) sistemleri soyut planlamada karşılaştırılabilir akıcılığa erişmekte hâlâ zorlanır. Bilişsel bilimden [gopnik1997words, gerstenberg17, lake2017building] esinlenen "kurama dayalı pekiştirmeli öğrenme" (TBRL) sistemleri üzerine son çalışmalar, AI ajanlarına nesne yönelimli, ilişkisel ve nedensel insan-benzeri dünya modelleri ("kuramlar") vererek bu boşluğu kapatmaya çalışmıştır [tsividis2021human, tang2024worldcoder]. Bu türün en gelişkin sistemi olan TheoryCoder [ahmed2025synthesizing], hiyerarşik planlamayı desteklemek için yüksek seviyeli tecritlerle birleştirilen düşük seviyeli bir dünya modeli öğrenir. TheoryCoder'ın karmaşık video oyunlarındaki başarımı ve örnek-verimliliği hem derin pekiştirmeli öğrenmeyi hem büyük dil modeli (LLM) ajanlarını dramatik biçimde aşar. TheoryCoder mimarisinin anahtar bileşeni olarak dil modellerini, geçmiş deneyimi çıkarılmış dünya modellerine çevirmek için kullanır. LLM'lerden bu yolla yararlanarak çağrışımsal bellek ve analojik erişim yeteneklerinden faydalanır. Sonuç olarak ya saf LLM ajanlarından ya geleneksel hiyerarşik planlayıcılardan tek başına çok daha yüksek sağlamlık ve hesaplama verimliliği elde eder. Sonrasında TheoryCoder, onları uçtan uca ajanlar olarak kullanmak yerine hiyerarşik planlama için sembolik modeller kurar.

TheoryCoder'ın ana sınırlaması elle kodlanmış tecritlere dayanmasıdır; bu uygulama kapsamını belirgin biçimde sınırlar. Örneğin yeni bir alanı ele almak için bir insanın önce ona ilgili tecritleri düşünmesi ve onlar için kod yazması gerekir. Soyut planlar olmadan TheoryCoder, düşük seviyeli dünya modelini kurmak için büyük ölçüde rastgele eylemlere dayanmak zorunda kalır; bu, tecritlerin ve aktarılabilirliklerinin sağladığı verimliliği azaltır. Burada bu temel sınırlamayı soyut kavramların otomatik öğrenmesini gerçekleyerek ele alırız. Yaklaşımımız ajanın yalnızca tecritleri kurup işlemesine değil, onları yeni alanlara aktarıp etkili ve anında temellendirmesine, alan uyarlaması gerekmeksizin, izin verir. Bu, sistemin *genelleyen* bir hiyerarşik planlama kapasitesi öğrenmesini ve böylece insan öğrenmesinin ve tecritinin temel algoritmik yönlerini taklit ederek karmaşık, yeni görevleri hızla çözmesini sağlar [tomov2020discovery]. Ortaya çıkan yöntem TheoryCoder-2, ilk istemler ve örnekler biçiminde asgarî insan rehberliği gerektirerek "planlama alanı tanım dili" (PDDL; [ghallab1998pddl]) işleçleri biçiminde yüksek seviyeli tecritleri sentezleyebilen bir TBRL ajanıdır.

Sokoban dahil birkaç yakından ilişkili video oyunu tanım dili (VGDL) oyunu [schaul2013video], ayrıca BabyAI [babyai_iclr19] ve Minihack [samvelyan2021minihack] ortamlarında deney yaparız. Yöntemimizi, klasik planlama alanı kurmayla [liu2023llm+, guan2023leveraging, smirnov2024generating] ve muhakeme tabanlı planlamayla [yao2023react, wei2022chain, yao2023tree] artırılmış LLM'lere dayalı birkaç taban çizgisiyle ve WorldCoder [tang2024worldcoder] gibi önceden önerilmiş program-sentezi ajanlarıyla karşılaştırırız.

TheoryCoder-2'nin taban çizgilerine göre hem örnek-verimliliğinde hem genellemede önemli iyileşmeler elde ettiğini, taban çizgilerinin zorlandığı görevlerin karmaşık sürümlerini başarıyla çözebildiğini gösteririz. Genel olarak bu, insan gibi öğrenen ve düşünen AI sistemleri kurma uzun vadeli hedefine doğru TBRL yaklaşımının uygulanabilirliği ve genelliğinde önemli bir iyileşmeyi temsil eder.

## 2. Arka Plan

### 2.1 Kurama Dayalı Pekiştirmeli Öğrenme

Kurama Dayalı Pekiştirmeli Öğrenme (TBRL), ajanın planlamak ve problemleri çözmek için ortamının açık, program-benzeri bir modelini ve arama algoritmalarını kullandığı bir paradigmadır. Ortamın dinamiklerini ya tablo geçiş modelleri olarak kodlayan [sutton90, kaelbling1996reinforcement, kaelbling1998planning] ya da derin sinir ağlarıyla yaklaşıklayan [Schmidhuber90diff, schmidhuber2015learning, pascanu2017learning, Weber17, ha2018recurrent, HafnerLB020] geleneksel model-tabanlı RL yöntemlerinin aksine TBRL sistemleri, nesneler arasındaki nedensel etkileşimleri ortamın nasıl işlediğini tarif eden sembolik programlar biçiminde doğrudan temsil eder. TBRL, bu programların insanların planlama ve problem çözme için öğrenip kullandığı soyut sezgisel dünya kuramlarına karşılık gelen *kuramlar* olması anlamında bilişsel kuramdan esinlenir. Bu sistemler modelleri tarafından yakalanmamış nedensel ilişkileri ortaya çıkarmaya çalıştıkları için rastgele keşfe dayanmadan problemleri çözebilir. Daha somut ve biçimsel tarifi sonraki Bölüm 2.2'de veriyoruz.

En eski somut TBRL sistemi olan EMPA ("Keşfeden, Modelleyen ve Planlayan Ajan"; [tsividis2021human]) ortamı bir alana özgü dil olan VGDL [schaul2013video] ile temsil etti ve onları üretmek için Bayesçi çıkarım kullandı. EMPA çıkarım maliyeti nedeniyle hesap bakımından yavaştı; VGDL'in kendisi yalnızca ikili çarpışma kurallarını ifade etmeye izin verdiği için sınırlayıcıydı ve basit Atari tarzı alanların ötesine ölçeklemeyi zorlaştırıyordu.

Daha yakın zamanda TheoryCoder [ahmed2025synthesizing], kuramları büyük dil modelleriyle (LLM'ler; [gpt3]) sentezlenen Python programları, VGDL'in aksine genel amaçlı bir programlama dili, olarak temsil ederek TBRL'nin daha genel bir sürümünü örnekledi. LLM'ler TheoryCoder'da hızlı yaklaşık çıkarımı mümkün kılar ve böylece onu EMPA'dan hızlı kılar. EMPA gibi TheoryCoder program sentezini yönlendirmek için durum geçişlerini toplamak üzere ortamlarla etkileşir. EMPA'dan farklı olarak TheoryCoder, verimli planlamayı ve hızlı aktarım öğrenmesini destekleyecek iki-seviyeli bir dünya modeline sahiptir; her ikisi Baba is You [hempuli2019baba, cloos2024baba] karmaşık bulmaca oyununda ve diğerlerinde gösterilmiştir. TheoryCoder'ın ayrıntıları sonraki Bölüm 2.2'de verilmiştir.

Bu umut verici sonuçlara rağmen TheoryCoder i) yalnızca nesne yönelimli koordinat tabanlı temsillerle kodlanabilen ortamlara uygulanabilir olması ve ii) elle mühendislik yapılmış tecritlere büyük ölçüde dayanarak ölçeklenebilirliği sınırlaması bakımından sınırlıdır.

Yöntemimizin ana teknik katkısı (Bölüm 3), TBRL sistemini tecritleri birkaç-atışla otomatik öğrenebilir kılarak ikincisini ele almaktır. Bu yetenek TBRL ajanlarının kuram repertuvarını tümüyle yeni alanlarda genişletmesine, yani insanların yeniden kullanılabilir yapılı kavramlar kütüphanesini elle müdahale olmaksızın kademeli büyütme yeteneğini yakalamasına izin verir. Yaklaşımımızın mevcut LLM tabanlı ajan taban çizgilerine göre hesaplama verimliliğini (kullanılan belirteçler bakımından) önemli ölçüde iyileştirdiğini ve öğrenme hızını artırdığını, böylece TBRL aracılığıyla ölçeklenebilir, insan-benzeri tecrit öğrenmesi ve problem çözmeye doğru daha güçlü bir adım olduğunu gösteririz.

### 2.2 TheoryCoder

Burada doğrudan üzerine kurduğumuz TheoryCoder'ın [ahmed2025synthesizing] matematiksel ayrıntılarını tarif ederiz. Problem şöyle formüle edilir. Ortam, $\mathcal{S}$ durum uzayı ve $\mathcal{A}$ eylem uzayı üzerinde bir $T: \mathcal{S} \times \mathcal{A} \rightarrow \mathcal{S}$ geçiş fonksiyonuyla modellenir. $K$ pozitif bir tamsayı olsun. Ajanın hedefi, birikimli maliyeti $\sum_{n=1}^N c(s_n, a_n)$'i asgarîleştiren, 1'den $N$'ye her $i$ için $a_i \in \mathcal{A}$ olan bir $\pi = (a_1, \ldots, a_N)$ planı bulmaktır; hedef-olmayan durumlar için $c(s,a) = K$ ve $s^\ast$ hedef durumunda $c(s^\ast,a) = 0$. Dolayısıyla eniyi plan, başlangıç durumundan hedefe en kısa eylem dizisine karşılık gelir.

**Sisteme genel bakış.** TheoryCoder beş bileşenden oluşan bir ajandır: bir LLM, iki planlayıcı (sırasıyla yüksek seviyeli ve düşük seviyeli planlama için), soyut durumlar ve eylemler kütüphanesini temsil eden (yüksek seviyeli planlayıcı tarafından kullanılan) bir PDDL program dosyaları kümesi ve ortamın geçiş fonksiyonunu yaklaşıklayan dünya modelini temsil eden (düşük seviyeli planlayıcı tarafından kullanılan) bir Python program dosyası. LLM ve planlayıcı bileşenleri sistem tanımlanırken önceden belirtilir ve sabit kalır. Esasen TheoryCoder'da öğrenme, ortamla etkileşirken bu program dosyalarını (LLM ile) sentezlemekten ibarettir; planlama ise bu program dosyalarını kullanarak klasik PDDL planlama sistemini ve arama algoritmalarını yürütmekten oluşur. Bu program dosyalarının tamamlayıcı rolleri aşağıda daha ayrıntılı tarif edilmiştir.

**Yüksek seviyeli tecritler.** TheoryCoder'daki PDDL program dosyaları ajanın yüksek seviyeli soyut alan kuramları kütüphanesini içerir. Yapıları hakkında daha özgül olmak gerekirse bu PDDL program dosyaları bir "alan" dosyası ve bir "problem" dosyasından oluşur. Alan dosyası soyut eylemleri ("işleçler" denir, örn. "kapıyı aç") ve onların ön-koşullarını/etkilerini ve göreve ilgili özellikleri yakalayan Boole yüklemleriyle temsil edilen soyut durumları (örn. "kapı kilidi açık") belirtir. Problem dosyası belirli bir görev için başlangıç durumunu ve hedef koşullarını belirtir. Bu dosyalar birlikte, hedefe başlangıç durumundan, varsa, ulaşan bir planı (işleçler yani yüksek seviyeli eylemler dizisi) çıkaran klasik bir planlayıcıya (Fast Downward [helmert2006fast] kullanırız) girdi olarak alınır. Özgün TheoryCoder'da bu PDDL dosyalarının insan mühendis tarafından verildiği varsayılır. Benzer şekilde EMPA, kendisine verilen bir VGDL tecritleri kümesine bağlıydı. İnsan mühendisliği yapılmış tecritlere bu bağımlılık, ele aldığımız sınırlamadır.

**Düşük seviyeli dinamik dünya modeli.** TheoryCoder, ortamın geçiş fonksiyonunu (dünya modelini) temsil eden bir Python programı $\hat{T}$ biçiminde ek bir düşük seviyeli dünya modeli sürdürür. Amacı, ham durum uzayında düşük seviyeli eylemlerin etkilerini tümüyle öngörmektir. Düşük seviyeli dünya modeli, hiçbir eylemin sonucunda durumda değişim öngörmeyen boş bir fonksiyon olarak başlatılır. Ajan yeni bir göreve başladığında düşük seviyeli eylem uzayında (örn. "yukarı", "aşağı", "sol", "sağ") küçük bir miktar rastgele keşfe izin verilir; bu bir başlangıç gözlem kümesi üretir. Dünya modeli boş olduğundan öngörü hataları birikir. Bu öngörü hatası (eylemler ve durum öngörüleri biçiminde) mevcut dünya modeliyle birlikte bir istemde LLM'ye gönderilir. LLM'nin rolü bu öngörü hataları (belirli bir bütçeye dek) giderilene kadar dünya modelini gözden geçirmektir. Bir alanda daha çok görevle karşılaşıldıkça dünya modeli öngörü hataları biriktirecek ve LLM bu hataları düzeltmesi için yönlendirilecektir.

**İki-seviyeli planlama.** PDDL alan ve problem dosyaları üretildikten sonra yüksek seviyeli planlayıcı [Fast Downward; helmert2006fast] soyut işleçler cinsinden sembolik bir plan üretir. Düşük seviyeli planlayıcı (bu durumda genişlik-öncelikli arama) her işleci bir ilkel eylem dizisine eşlemek için öğrenilmiş geçiş fonksiyonu $\hat{T}$'yi kullanır. Köprü kuran bir "denetçi" fonksiyon, düşük seviyeli durumların istenen yüksek seviyeli yüklem etkilerini gerçekten sağladığını doğrulayarak tutarlılığı sağlar. Bu, sistemimizin de öğrendiği Python Boole yüklem sınıflandırıcılarıyla yapılır. Bu hiyerarşik çerçeve insanların nasıl plan yaptığını yansıtır: soyut işleçler (örn. "kapıyı aç") ve yüklemler (örn. "kapı kilidi açık") planlamayı sembolik seviyede yönlendirirken, onları temellendirmek somut motor eylemleri (örn. "yukarı", "sol" vb.) gerektirir.

## 3. Yöntem: TheoryCoder-2

TheoryCoder'ı tecritleri özerk öğrenebilir (yani PDDL dosyalarını sentezleyebilir) ve çeşitli ortamlarla etkileşim bölümleri dizisi boyunca soyut kavramlar/beceriler kütüphanesini büyütebilir kılarak genişletiriz. Bu geliştirilmiş TBRL sistemine TheoryCoder-2 diyoruz. Burada TheoryCoder-2'nin LLM bağlam-içi öğrenmesi yoluyla tecrit öğrenme sürecinin ayrıntılarını (Bölüm 3.1) ve tecrit kütüphanesinin bir müfredat yoluyla kademeli büyütülmesinin genel fikrini (Bölüm 3.2) tarif ederiz. Algoritmik bir tarif Algoritma 1'de sunulmuştur.

**Algoritma 1: TheoryCoder-2.**
Girdi: LLM, başlangıç durumu $s_0$, eylem uzayı $\mathcal{A}$, birkaç-atışlı örnekler $FS$. Çıktı: Düşük seviyeli plan $\pi = \langle a_1, \ldots, a_N \rangle$.
1. $D, \mathcal{P} \gets \text{LLM}(s_0, FS)$ (PDDL alan ve problem dosyaları)
2. $\mathcal{R}_p \gets \emptyset$, $\mathcal{R}_a \gets \emptyset$ (tekrar tamponları)
3. $\mathcal{R}_{\text{random}} \gets$ rastgele eylemlerle geçişler üret
4. $\hat{T} \gets \text{LLM}(s_0, \mathcal{A}, \mathcal{R}_{\text{random}}, D, \mathcal{P})$ (düşük seviyeli dünya modeli)
5. $\mathcal{G} \gets \text{LLM}(s_0, FS, D, \mathcal{P})$ (yüklem sınıflandırıcıları)
6. $\Pi_H \gets \text{Fast-Downward}(D, \mathcal{P})$
7. $\Pi_H$'deki her temellenmiş işleç $\underline{\omega_k}$ için: $\pi_k \gets \mathrm{BFS}(s_0, \hat{T}, \underline{\omega_k})$; $\pi_k$'deki bütün geçişleri $(s, a, s', \underline{\omega_k})$ olarak $\mathcal{R}_p$'ye kaydet; $\pi \gets \pi \cup \pi_k$; $\pi_k$'deki her $a$ için $(s, a, s', \underline{\omega_k})$'yi $\mathcal{R}_a$'ya kaydet.
8. $\pi$ yürütüldükten sonra $s'$'de $\text{EFF}(\underline{\omega_{K-1}})$ sağlanıyorsa $\pi$'yi döndür. Aksi halde: $\mathcal{R}_p \neq \mathcal{R}_a$ ise $\hat{T} \gets \text{LLM}(\hat{T}, \mathcal{R}_p, \mathcal{R}_a)$; değilse $\Pi_E \gets \text{Keşif}(s_0, D)$ ve 6. satıra dön.

### 3.1 Tecritleri Öğrenmek

Soyut işleçleri ve yüklemleri tanımlayan elle mühendislik yapılmış PDDL dosyalarına dayanan özgün TheoryCoder'ın aksine TheoryCoder-2, LLM'lerin bağlam-içi öğrenme yeteneğinden bu tür dosyaları kendi başına sentezlemek için yararlanır. Bu süreçte elle mühendislik yapmamız gereken tek sistem girdisi *ilk istem*dir: ortamın nihai hedefinin doğal dil tarifi ve soyut işleçleri öğrenmenin ne anlama geldiğini bir oyuncak problem üzerinden örnekleyen çok basit örnekler (örn. ön-koşulu *yenmemiş* ve etkisi *yenmiş* olan *ye* işleci); ilgili örnek Ek A Kutu 3'te, tam ilk istem Kutu 1'de bulunabilir.

Bu örnekler asgarî olacak şekilde tasarlanmıştır; ajanın fiilen etkileştiği ortamla ilişkisizdirler ve yalnızca tecritlerin nasıl temsil edilebileceğine dair şablon olarak hizmet ederler. LLM'yi tecritleri uygun düzeyde, ne çok ayrıntılı ne çok kaba, sentezlemeye yönlendirmek için çok önemlidirler (tam özerklik verildiğinde mevcut LLM'ler için bir güçlüktür).

### 3.2 Tecrit Kütüphanesini Yeniden Kullanmak ve Büyütmek

Deneylerimiz TheoryCoder-2'nin farklı ortamlarla etkileşen bir "bölümler" dizisi boyunca yeniden kullanılabilir soyut kavramlar kütüphanesi kurma yeteneğini sınadı. Bunun için benzerliğe göre birlikte gruplanan ve zorluğa göre sıralanan bir veya daha çok ortam içeren bölümler tasarladık. Müfredatın sıralamasını karıştırarak ablasyonlar da kurduk.

Her bölüm içinde ajan işleçleri (sıfır-atışlı) öğrendiğinde, özgün TheoryCoder'daki gibi (Bölüm 2.2) bir Python dünya modelini öğrenir. TheoryCoder'dan farklı olarak verili bir ortamda yüklemlerin anlambilimini temellendirmek için Python fonksiyonlarını da öğrenir. (Daha önce bunlar PDDL tecritleriyle birlikte veriliyordu.) Yani ajan yüklem sınıflandırıcılarını Python programları üreterek öğrenir. Bu sınıflandırıcılar ham durum üzerinde işler ve yüklemin doğru olup olmadığını gösteren bir Boole döndürür. Bir bölüm içinde ikinci ortamdan itibaren ajanlar önceden öğrenilmiş tecritleri yeniden kullanmayı dener ve gerektikçe onlara ekler.

**Şekil 1.** Yöntemler arasında ajan–ortam etkileşiminin karşılaştırması. WorldCoder ve LLM + P ikisi de LLM + Planlayıcı kategorisine girer.

## 4. Deneyler

Deneylerimiz şu soruları cevaplamayı hedefler: TheoryCoder-2 soyut durumları ve eylemleri başarıyla öğrenebilir mi? Öğrenilen tecritler farklı ortamlarda yeniden kullanılabilir mi? Yeniden kullanım yeni problemlerde örnek-verimliliğini artırır mı? Ortaya çıkan sistem mevcut LLM ajanları için önemsiz olmayan zor görevlerde ne kadar iyi başarım gösterir?

Bunları cevaplamak için TheoryCoder-2'nin ve diğer ajanların çeşitli özelliklerini VGDL tabanlı Labirent ve Maze'de ve Sokoban'da (Bölüm 4.1), BabyAI ortamlarında ve son olarak Minihack'te (Bölüm 4.2) değerlendiririz.

**Değerlendirme ölçüleri.** Ajanları değerlendirmek için şu ölçüleri kullanırız: *belirteç maliyeti* (her ajanın tükettiği belirteç sayısı, örnek-verimliliğini ölçer), *hesaplama süresi* (duvar-saati hesaplama süresi, her ajanın pratik çalışma süresini ölçer) ve *çözüm oranı* (ilk denemede başarıyla çözülen görevlerin (oyun seviyelerinin) oranı, ajan başarımını ölçer).

TheoryCoder-2'yi, TheoryCoder-2'nin belirli bileşenleri ablate edilmiş varyasyonları dahil şu taban çizgileriyle karşılaştırırız. Bu ajanların hepsi LLM'leri bir ölçüde kullanır (ya muhakemesiz 4o ya da muhakemeli o4-mini modelini).

**LLM + $\pi$.** Açık tecritler veya çalıştırılabilir dünya modeli olmaksızın doğrudan ilkel eylemler cinsinden planlar üreten yalnız-muhakeme modeli. Burada yüksek, orta ve düşük muhakeme çabasıyla o4-mini [openai_o4mini_system_card_2025] sınarız (belirtilmediğinde 'yüksek' sürümü kullanırız). Ayrıca muhakemesiz bir model olan GPT-4o'yu da sınarız.

**LLM + P** [liu2023llm+]. Her görev için mevcut gözlem ve birkaç-atışlı bir istem verildiğinde PDDL alan ve problem dosyaları üretmek için bir LLM kullanır. Bir planlayıcı bir plan üretir; LLM bunu sonra ortamda yürütülebilir bir eylem dizisine çevirir. PDDL sentezleyici model olarak yüksek muhakeme çabalı o4-mini'yi kullanırız; çünkü düşük çabalı kipler erken seviyelerde bile zorlandı, muhtemelen LLM'lerin PDDL üretiminde Python koduna göre daha az güvenilir olmasından.

**WorldCoder** [tang2024worldcoder]. Ajan geçiş fonksiyonunu temsil eden bir Python programı sentezler. Bu program düşük seviyeli bir planlayıcıca eylemler üretmek için kullanılır. TheoryCoder-2'de olduğu gibi sentezleyici olarak GPT-4o'yu ve planlayıcı olarak BFS'yi kullanırız. WorldCoder TheoryCoder-2'den planlama ve dünya modellemenin hiyerarşik yapılmaması bakımından ayrılır. WorldCoder bu yönden LLM + P'ye daha çok benzer; çünkü LLM + P de dünyayı yalnızca düşük seviyede modeller.

**TheoryCoder-2.** Yüksek seviyeli planlama için GPT-4o ile PDDL işleçlerini, düşük seviyeli dinamikler için yüklemlerin Python sürümlerini ve bir Python geçiş fonksiyonunu sentezleyen, ortamlar arasında temellenmiş tecrit öğrenmesini ve yeniden kullanımını mümkün kılan tam sistemimiz. TheoryCoder-2 diğer ajanlardan, dünyayı PDDL'de yüksek seviyeli tecritler ve düşük seviyeli bir Python geçiş modeli sentezleyerek hiyerarşik modellemesi bakımından farklıdır. Yüksek seviyeli planlama için PDDL işleçlerini, düşük seviyeli planlama için düşük seviyeli modeli kullanır.

**Kâhin (Oracle).** TheoryCoder-2'nin öğrendiği tecritlerin kalitesini karşılaştırmak için bir referans olarak hizmet eden, elle mühendislik yapılmış tecritleri kullanır. Ayrıca iki ablasyonlu varyasyonu da değerlendiririz:

**TC − P.** Çalıştırılabilir tecritleri ve Python dünya modelini çıkarır. LLM doğrudan tecritleri ve yüksek seviyeli planları üretir, sonra yüksek seviyeli planını eylemlere çevirmesi istenir. Bu, LLM'yi önce yüksek seviyede düşünüp sonra düşük seviyeli plan çıkarmaya teşvik eden bir düşünce zinciri istemi [wei2022chain] biçimidir.

**TC − C.** Müfredat öğrenmesini çıkarır. Her bölüme boş tecritler ve geçiş fonksiyonuyla başlar. Mevcut seviye için bütün tecritleri ve bir geçiş fonksiyonunu sentezlemek zorundadır.

**Şekil 2.** Deneylerimizde kullanılan müfredatın bir resmi. Müfredat, her bölümün bir veya daha çok ortam/oyun içerdiği bölümler dizisidir. İlk bölüm (Labirent) ve ikincisi (Maze ve Sokoban) dizisi Deney 1'de (Bölüm 4.1) incelenir; Deney 2'de dizinin tamamı kullanılır (Bölüm 4.2). Deney 3'te (Minihack) ayrı bir müfredat kullanırız. Mavi oklar TheoryCoder-2'nin öğrendiği tecritleri gösterir.

### 4.1 Basit Ortamlarda Tecrit Öğrenmesini ve Yeniden Kullanımını Değerlendirmek

Bu deneyin amacı, ajanımızda tecrit öğrenmesinin uygulanabilirliğini ve yeniden kullanılabilirliğini değerlendirmektir. Burada ajanları **Labirent**, **Maze** ve **Sokoban** kullanarak değerlendiririz. Şekil 2'nin ilk bölümü bu ortamı gösterir. Bu görevler esas olarak belirli bir konuma "git" tecritlerini öğrenmeyi ve yeniden kullanmayı içeren seyrüsefer tarzı VGDL oyunlarıdır.

Tablo 1'in üst kısmındaki sonuçlar belirteç maliyetini ve ajanların her problemi başarıyla çözüp çözmediğini gösterir. Birincisi, TheoryCoder-2'nin $\mathtt{move\_to}$ anahtar tecritini öğrenip görevi çözebildiğini gözleriz. (LLM'nin bu işleci $\mathtt{moveontop}$ olarak adlandırdığını ve tecrit kodunun aşağıdaki Kutu'da gösterildiğini not edin.) İkincisi, TheoryCoder-2'nin bu işleci Maze ve Sokoban iki yeni ortamda yeniden kullanabildiğini gözleriz. Verimlilik bakımından basit LLM + $\pi$ taban çizgisi bu basit ortamlarda en verimli ajandır; ikinci en iyisi, iki gelişkin LLM ajanı LLM + P ve WorldCoder'dan daha iyi olan TheoryCoder-2'dir. Son olarak bütün sistemlerin bu basit problemleri çözebildiğini not ederiz.

**Öğrenilmiş bir tecrit örneği:**
```
(:action moveontop
    :parameters (?obj1 - object ?obj2 - object)
    :precondition (not (ontop ?obj1 ?obj2))
    :effect (ontop ?obj1 ?obj2)
)
```

**Tablo 1.** Modeller arasında belirteç maliyeti (düşük daha iyi). İlgili ajan görevi çözmeyi **başaramadığında** hücre mavi vurgulanır (aşağıda başarısızlar `✗` ile işaretlenmiştir).

| Görev (Oyun) | TC-2 Tam | TC − P | TC − C | LLM + π | LLM + P | WorldCoder |
| :-- | --: | --: | --: | --: | --: | --: |
| Labirent | 21,378 | 24,510 | 21,378 | 5,173 | 28,931 | 56,360 |
| Maze | 19,737 | 23,186 | 21,236 | 3,518 | 24,396 | 56,085 |
| Sokoban | 7,171 | 10,373 | 8,441 | 2,608 | 25,919 | 19,684 |
| **BabyAI** | | | | | | |
| BabyAI (Pickup) | 8,588 | 6,660 | 8,588 | 2,405 | 20,589 | 18,013 |
| BabyAI (Unlock) | 33,116 | 41,734 | 33,116 | 5,705 | 50,071 | 97,938 |
| BabyAI (Combine Skills 1) | 1,961 | 54,277 | 44,725 | 40,960 ✗ | 41,515 ✗ | 119,330 ✗ |
| BabyAI (Combined Skills 2) | 2,528 ✗ | 53,376 ✗ | 45,175 ✗ | 49,973 ✗ | 59,003 ✗ | 120,200 ✗ |
| BabyAI (Combined Skills 3) | 2,454 | 53,064 | 45,017 | 29,791 | 55,078 ✗ | 120,375 ✗ |
| **Minihack** | | | | | | |
| Minihack-5x5 | 5,163 | 7,671 | 5,163 | 1,115 | 12,595 | 8,144 |
| Minihack-15x15 | 0 | 9,815 | 4,837 | 1,402 | 12,124 | 0 |
| Minihack-Traps | 0 | 14,326 ✗ | 5,007 | 9,110 | 29,712 ✗ | 0 |
| Minihack-Monster | 0 | 21,189 ✗ | 6,125 | 1,290 | 30,940 ✗ | 0 |
| Minihack-WoD | 19,433 | 21,932 | 19,433 | 4,176 | 52,434 ✗ | 62,165 ✗ |
| **Bütün Görevler Toplamı** | **121,529** | 267,180 | 268,241 | 157,206 | 443,307 | 437,719 |

*(Okuyucu notu: Tablo "Combined Skills 3" satırında kaynaktaki mavi vurgu işaretlerine göre LLM+π'nin hücresi (29,791) vurgusuzdur; yani çözmüştür. Metin "yalnız TheoryCoder-2 hem 1 hem 3'ü çözdü" der; tablo LLM+π'nin Combined Skills 3'ü çözdüğünü gösterir — metin ile tablo burada uyuşmaz. Ayrıca "Combined Skills 2" satırında TheoryCoder-2'nin kendisi de ✗ olduğundan 2,528 belirteç başarısız bir koşunun maliyetidir.)*

### 4.2 Tecritleri Daha Zor Problemlere Aktarmak

Bu deneyin amacı, TheoryCoder-2'nin yeni tecritleri kademeli öğrenip yeni ortamlarda yeniden kullanıp kullanamayacağını ve bunun örnek-verimliliği sağlayıp sağlamadığını sınamaktır.

Önce ajanımızı Bölüm 4.1'in müfredatında değerlendiririz; sırayla üç **BabyAI** seviyesi ekleriz: *Pickup* (tek anahtar), *Unlock* (anahtar + kapı) ve *Boss* seviyesi. İlk iki ortam ilgili görevi çözmek için gereken soyut becerilerle adlandırılmıştır; sonuncusu hem alma hem kilit açma becerilerini isteyen çok-odalı bir görevdir. Boss seviyesi için nihai birleşik-beceri ortamlarının çeşitliliğini artırmak üzere (üç farklı tohuma dayalı) farklı yerleşimli üç örnekleme üretiriz. Şekil 2 bu müfredatın bir resmini verir.

Tablo 1 (orta) sonuçları gösterir. Bütün ajanlar basit *Pickup* ve *Unlock* ortamlarını çözerken birçoğu karmaşık Boss seviyesinde başarısız olur: daha özgül olarak bütün ajanlar "Combined Skills 2"de başarısız oldu; yalnızca TheoryCoder-2 hem "Combined Skills 1" hem "3"te başarılı oldu. TheoryCoder-2 ilk iki seviyeden tecritleri ($\mathtt{Pickup}$ ve $\mathtt{Unlock}$) başarıyla öğrenir ve sonra ikisini birden gerektiren daha karmaşık Boss seviyesi görevlerini çözmek için onları terkip eder.

**Şekil 3.** Bütün oyunlar üzerinden ortalanan, hesaplama süresinin fonksiyonu olarak başarı oranı. TC Ailesi TheoryCoder-2'yi ve varyantlarını temsil eder. TheoryCoder ve ablasyonları yüksek muhakeme çabasını kullanan muhakeme modellerinden daha az hesaplama süresiyle daha çok görev çözebilir. LLM + $\pi$ üç farklı muhakeme çabasıyla gösterilmiştir.

Örnek-verimliliği bakımından TheoryCoder-2 tecritleri öğrenmek için birinci ve ikinci seviyelerde yüksek hesaplama ayırır; ancak belirteç tüketimi Boss seviyesinde (yaklaşık 8500 ve 33000'den yaklaşık 2000'e) dramatik düşer; çünkü önceki seviyede öğrenilenleri yeniden kullanırsa artık yeni tecrit öğrenmesi gerekmez. Ayrıca TheoryCoder-2'nin bu ilkel tecritleri farklı kazanma koşulları olan Boss seviyelerinin farklı varyasyonlarını çözmek için terkip edebildiğini gösterir.

Son olarak tecrit öğrenme yöntemimizi beş **Minihack** ortamında değerlendiririz. Tablo 1'in alt kısmı tecrit aktarımının etkililiğini gösterir. TheoryCoder-2, `Minihack-5x5`te `move_to` soyut becerisini öğrenir ve sonraki üç ortamı çözmek için yeniden kullanır. Sonuç olarak `Minihack-15x15`, `Minihack-Traps` ve `Minihack-Monster` için 0 belirteç tüketimi vardır. WorldCoder de bu eğilimi sergiler ama en zor görev olan `Minihack-WoD`'de başarısız olur. `Minihack-WoD` ortamında TheoryCoder-2, bir asayı ateşleyip düşmanı öldürmesine izin veren `attack` tecritini öğrenir. Bu tecrit, birden çok kavramı kapsayan kompakt işleçlerin nasıl öğrenilebileceğini gösterir: asayı almak, düşmana nişan almak ve ateşlemek. Minihack deneyleri, tecritlerin sıfır-atışlı aktarımının etkililiğini ve farklı eylemleri kapsayan tek kompakt tecritleri öğrenme yeteneğini gösterir.

Dikkat çekici biçimde müfredat veya planlayıcılar çıkarıldığında bile TheoryCoder-2 görevi çözebilir; yani iki bileşen de başarıma değil örnek-verimliliğini artırmaya önemli katkı yapar. Tablo 1'de müfredat öğrenmesi çıkarıldığında ve tecrit dosyaları boş dosyalarla başlatıldığında bile TheoryCoder-2'nin diğer dünya modelleme yaklaşımları WorldCoder ve LLM + P'den daha hesaplama-verimli kaldığını görürüz. Buna karşılık WorldCoder çok maliyetlidir; ham LLM yaklaşımından daha çok belirteç tüketir. Daha zor ortamlarda LLM + P'nin ürettiği PDDL programlarının sıklıkla hatalar içerdiğini, geçersiz veya çözülemez planlara yol açtığını da gözlemledik.

Ayrıca bu ajanların çalışma sürelerini karşılaştırırız. Şekil 3, müfredattaki bütün oyunlarda ortalanan başarı oranını ve ortalama hesaplama süresini gösterir. En hızlı ajanların düşük çabalı LLM + $\pi$ taban çizgisi ile müfredat ve planlayıcılı tam TheoryCoder-2 olduğunu gözleriz. Dikkat çekici biçimde müfredat öğrenmesi çıkarılıp TheoryCoder-2 boş dosyalarla başlatıldığında bile, tecritleri sentezlemede ve seviyeleri çözmede o4-mini varyantlarından hızlı kalır.

## 5. Tartışma

**Sonuçların özeti.** Sonuçlar TheoryCoder-2'nin taban çizgilerine göre birkaç anahtar avantajını vurgular. Şekil 3'te gösterildiği gibi TheoryCoder-2 ve ablasyonları en yüksek başarı oranını elde eder. Bu, yalnız-muhakeme LLM'lerine kıyasla planlama hatası olasılığını azaltan temellendirilmiş tecritlerin kullanımından kaynaklanır. Yüksek muhakeme çabalı LLM + $\pi$ bazen karşılaştırılabilir çözüm oranlarına ulaşsa da bunu daha yüksek belirteç maliyetiyle ve çok daha büyük hesaplama süresi maliyetiyle yapar; bu da ölçeklenebilir veya gerçek-zamanlı kullanım için pratik dışı kılar. BabyAI Boss seviyesinde yüksek muhakeme çabalı o4-mini bir cevap döndürmek için çoğunlukla yaklaşık 3 dakika gerektirdi. Buna karşılık TheoryCoder-2, hiyerarşik dünya modellerinin yeniden kullanılabilir bileşenlerini öğrenmek için basit seviyelere hesaplama yatırır; bu daha zor ortamlarda öğrenmeyi ve planlamayı hızlandırır. Dahası sembolik tecritler üreterek ajanlarımız son derece verimli klasik planlama algoritmalarını çalıştırabilir. Sonuç hem belirteç maliyetinde hem çalışma süresinde verimlilik kazanımlarıdır: sembolik planlayıcılar burada araştırdığımız alanlarda tipik olarak bir saniye içinde sonlanır.

Hem tecritleri üreten hem kod yerine doğal dilde planlayan TC-P ablasyonunda tam modelle niteliksel farklar gözledik. Örneğin yüksek muhakeme çabalı o4-mini, sistemimizden farklı bir ayrıntı düzeyinde tecritler üretti; çoğunlukla yüksek seviyeli işleçleri gereksiz düşük seviyeli ayrıntılarla iç içe geçirdi. Dolayısıyla dünya modelinin düzeyleri arasında kod belirtimleriyle işlev ayrımını daha sıkı uygulamak, LLM ajanlarında sistematik düşünmeyi üretmek için daha genel faydalar sağlayabilir.

Sonuçlarımız, düşük seviyeli ayrıntının karışmasının TC-P'nin planları haritalamak için neden daha uzun sürdüğünün nedeni olabileceğini, TheoryCoder-2'nin ise uygun bir dünya modelini sentezlemek için başta tam yeterli hesaplamayı yatırdığını düşündürür. Bu model "doğru" tecritleri yakaladığında, ajanın duruma bağlı olarak hızlı, tepkisel muhakeme ile daha yavaş, kasıtlı planlamayı esnek dengelemesine izin veren uyarlanabilir bir hesaplama kaynağı olarak hizmet edebilir.

Genel olarak TheoryCoder-2'nin öğrenilmiş tecritlerinin kalitesini elle tasarlanmış tecritler olan Kâhin'e benzer buluyoruz. Öğrenilen tecritlerin kalitesini sistematik nicel değerlendirmenin bir yolu olmasa da (örneğin programların dize uzunluğu ölçülüp belirli bir tecritin ne kadar sıkıştırdığı sorulabilir), niteliksel olarak Şekil 3'te Kâhin'e benzer başarım sağladıklarını ve benzer ön-koşullara ve etkilere sahip olduklarını buluruz.

**Sınırlamalar ve gelecek yönler.** Önemli ilerlemelere rağmen TheoryCoder-2'nin gelecek çalışmamızda ele almayı planladığımız sınırlamaları vardır. Birincisi, yaklaşımımız nesne yönelimli, metin tabanlı bir durum temsiline erişim varsayar. Görsel-dil modelleri planlama için karışık sonuçlar gösterse de basit ortamlarda bu tür temsilleri çıkarmak için algı modülleri olarak hizmet edebilir. Daha karmaşık ortamlara ölçeklemek nesne keşfi, izleme ve özellik çıkarımı için sağlam yöntemler gerektirecektir. İkincisi, ayrık alanların ötesinde sürekli alanlara genişlemek yeni güçlükler getirir (örn. sürekli yörüngelerin veya çarpışma dinamiklerinin öngörülmesi). Üçüncüsü, planlayıcıda yüksek ve düşük seviyeli temsilleri bağlamak için kritik olan yüklem sınıflandırıcılarını öğrenirken kırılganlık sorunları fark ettik. Özellikle bazı sembolik durum temsillerinin sorunlara yol açtığını fark ettik. Örneğin BabyAI'de açık kapıları başta "open_door" ve kapalı kapıları "closed_door" olarak temsil ettik. Bu durumda yöntemimiz yanlış varsayımlar yapan yüklem fonksiyonları sentezledi; örneğin açık kapıların durum sözlüğünden kaldırılacağını varsaydı. Bunun yerine kapıları kapalı ve kilitli için Boole özelliklere sahip bir nesne olarak temsil ettiğimizde yöntemimiz tutarlı biçimde doğru yüklem sınıflandırıcıları üretti.

Son olarak LLM'lerin burada kullandığımız bütün ortamlar için yalnızca ilk gözlem verildiğinde yeterli tecritler üretebildiğini not etsek de daha zorlayıcı veya daha az tanıdık ortamların PDDL temsilleri için deneme-yanılma öğrenmesini destekleyecek ek mekanizmalar gerektirmesi olasıdır. Bu, gelecek çalışmanın odağı olacaktır.

## 6. İlgili Çalışmalar

**Planlama ve politika sentezleme için LLM'ler.** Birçok yakın çalışma LLM'lerin planlama için nasıl kullanılabileceğini araştırmıştır [yao2023react, hao2023reasoning, zhao2024large, liu2023reason, wang2023voyager]. Yaygın bir yaklaşım LLM'ye ortam durumunun metin tabanlı tarifini girdi olarak vermek ve sonra bir eylem üretmesi için sorgulamaktır. Eylem yürütüldükten sonra ortaya çıkan metin tabanlı durum modele geri beslenir ve etkileşimli bir çevrim oluşturur. Görsel-dil modelleri de benzer biçimde uygulanmıştır [waytowich2024atari, paglieri2024balrog, ruoss2025lmact, cloos2024baba]; yalnız metin tabanlı tarifler yerine ortam durumunun görüntüleriyle istemlenir.

Bu ilerlemelere rağmen birçok öncü LLM uzamsal muhakemede hâlâ zorlanır ve halüsinasyona eğilimlidir. Bu sorunları hafifletmek için bazı yaklaşımlar LLM ajanlarını harici modüller veya araçlarla [cao2025large] güçlendirir, modelleri yörünge verisinde ince ayarlar [gaven2024sac], bellek modülleri ekler veya ajanın muhakemesini zamanla daha iyi yapılandırmasını sağlayan istem teknikleri kullanır. TheoryCoder-2'yi LLM'yi örtük planlayıcı olarak kullanan ajanlarla karşılaştırdık [yao2023react, wei2022chain, yao2023tree]. Bu yöntemler muhakemeyi iyileştirebilse de muhakeme modelleri cevap üretmek için hatırı sayılır zaman aldığından çoğunlukla yüksek hesaplama maliyetinden zarar görür [hassid2025don].

**Program sentezi.** Birçok çalışma ortamın açık dünya modellerini kurmak için program sentezini kullanmış [tang2024worldcoder, ahmed2025synthesizing, piriyakulkij2025poe, liu2025interactive], standart büyük dil modellerine kıyasla iyileşmiş muhakeme yetenekleri göstermiştir [gupta2023visual]. EMPA [tsividis2021human] de program sentezi kullanır, ancak ortamı genel amaçlı programlama dili yerine VGDL ile temsil etti. Wong vd. [wong2024learning], LLM'lerin basit dil-talimatı alanları için işleçleri öğrenmek için kullanılabildiğini gösterdi. Liu vd. [liu2023llm+] PDDL dosyaları üretmek için LLM'ler kullandı ve kaliteli üretim için bağlam-içi öğrenme örneklerinin önemli olduğunu gösterdi. Diğer çalışmalar yüklemleri öğrenmek için görsel-dil modellerini araştırmıştır [liang2025visualpredicator]; ancak bu yöntemler nesne belirlemeyi yönlendirmek için etiketli görüntülere dayanıyordu ve özerkliklerini sınırlıyordu. Buna karşılık yaklaşımımız hiyerarşik planlama için gereken hem hedefleri hem tecritleri üretmenin (ortamın çerçevesinin metin tabanlı gözlemine erişim varsayarak) uçtan uca problemini hedefler.

**RL'de tecrit öğrenmesi.** Odağımız program-sentezi ajanları ve doğrudan karşılaştırılabilir LLM tabanlı ajanlar olsa da, tecrit öğrenmesi ve hiyerarşik planlama genel pekiştirmeli öğrenmede de uzun süreli bir araştırma konusudur. Seçenekler çerçevesinde [sutton1999between, bacon2017option], Feodal RL'de [DayanH92, VezhnevetsOSHJS17] ve alt-hedef üretiminde [schmidhuber1992subgoalplanning, bakker2004hierarchical] getirilen anahtar kavramlar, çevrim-dışı taklit öğrenmesi ortamı dahil [shiarlis18taco, kipf2019compile, lu2021ompn, gopalakrishnan2023unsupervised] modern derin RL araştırmasında merkezî kalmaktadır. Benzer şekilde birçok yakın yöntem saf sinir ağı model-tabanlı RL'nin örnek-verimliliğini zorlamıştır [schrittwieser2020mastering, hafner2023mastering]; belirli alanlarda insan öğrenenlerin verimliliğine eşlemiştir [YeLKAG21]. Ancak genel olarak derin RL yöntemleri önceki çalışmalarca bildirildiği gibi nörosembolik ve program sentezi tabanlı ajanlara kıyasla çok daha az örnek-verimli ve daha düşük genelleme yeteneğine sahip kalır [tang2024worldcoder, tsividis2021human]. Burada katkımız böyle bir nörosembolik yaklaşımın mevcut sınırlamasını zorlamaktı.

## 7. Sonuç

Tecrit indüksiyonunu ve yeniden kullanımını mümkün kılarak TBRL'nin kapsamını ve verimliliğini genişlettik; bu, TBRL'yi insan mühendisliğinden bağımsız kılma yolunda kritik bir adımdır. Yeni bir TBRL sistemi olan TheoryCoder-2'nin kademeli yeniden kullanılabilir tecritler öğrenebildiğini, LLM'lere dayalı birçok taban çizgisi LLM ajanına göre hem iyileşmiş örnek-verimliliği hem çözüm oranları verdiğini deneysel gösterdik. Gelecek çalışma, TBRL'yi nesne yönelimli, metin tabanlı durum temsilli ortamların ötesindeki ortamlara uygulanabilir kılacak biçimde genişletecektir.

**Yazılım ve Veri.** Kodumuz şu adrestedir: https://github.com/ZerghamAhmed/TheoryCoder

*(Etki beyanı ve teşekkürler çevrilmemiştir: standart ICML metni ve fon bilgisi.)*

## Ek A. Dil Modeli İstemleri (Özet)

Burada deneylerimizde kullanılan bütün istemler verilir. *Ham metin `orijinal/main.tex`'tedir; çeviri yapılmamıştır (modelin gördüğü İngilizce girdidir).* İstemlerin işlevi ve içeriği:

- **Kutu 1: PDDL Dosyaları Üretme İstemi.** LLM'ye 2B ızgara oyunu oynayan bir ajan olduğu, ham durumun aşağıda verildiği söylenir ve ajanın oyunu kazanmasına izin verecek *asgarî* bir PDDL alan ve problem dosyası istenir ("mümkün olan en asgarî soyut dosyalar cinsinden düşün"). Problem dosyasındaki her nesne yalnızca ham durum sözlüğünün anahtarlarıyla adlandırılır; uzamsal ilişkiyi ima eden yüklemler (from/to gibi) ÖNERİLMEZ; yapılandırma özellikleri nesne olarak temsil edilmez (örn. `unopened_black_jar` → `black_jar`); birden çok işleç ve yüklem önerilebilir ve problem dosyasında iki hedef olabilir; ham durum sözlüğü anahtarları gezilebilir sayılır; kod blokları ```pddl ``` etiketleriyle döndürülür; yüklem adlarında "-" ve Python anahtar kelimeleri kullanılmaz; işleç adları küçük harf; yüklem adları tek kelime, alt çizgisiz; birkaç-atışlı PDDL örnekleri, ham durum ve şimdiye dek sentezlenmiş alan dosyası eklenir.
- **Kutu 2–4: Birkaç-Atışlı PDDL Örnekleri.** Üç oyuncak örnek: (1) `ontop` yüklemi ve `placeontopof` işleci (masa/kupa durumu); (2) `eaten` yüklemi ve `eat` işleci (ajan/elma/sarmaşık/balta/kavanoz durumu; nesne adından yapılandırma özelliği atılır: `unopened_black_jar` → `black_jar`); (3) `unblocked` yüklemi ve `clear` işleci (ajan/pencere durumu; `blocked_gold_window` → `gold_window`). Her örnek `(define (domain toy-domain) ...)` ve `(define (problem toy-problem) ...)` olmak üzere iki PDDL dosyası içerir. Örnek 2'nin içeriği (ilk istem için kritik): alan dosyasında `(:predicates (eaten ?x - object ?y - object))` ve `(:action eat :parameters (?obj1 - object ?obj2 - object) :precondition (not (eaten ?obj1 ?obj2)) :effect (eaten ?obj1 ?obj2))`; problem dosyasında `(:init (not (eaten agent apple)))` ve `(:goal (eaten agent apple))`.
- **Kutu 5: Python Yüklemi Üretme İstemi.** LLM'den PDDL işleçlerinin Python sürümleri olan, durumu ve argümanları alıp Doğru/Yanlış döndüren Python yüklemleri yazması istenir; alan dosyasındaki bütün yüklemler için, aynı adla; alan dosyası, problem dosyası, ham durum, mevcut Python düşük seviyeli dünya modeli ve oyun tarifi verilir. Örnek: `isLeftOf(state, arg1, arg2)`: iki nesnenin x-koordinatlarını karşılaştırır, nesne yoksa Yanlış döndürür; `state` her zaman argümanlardan biri olmalıdır.
- **Kutu 6: Tecrit Aktarımı (yalnız problem dosyası üretme).** Verilen bir PDDL alan dosyası için ajanın oyunu kazanmasına izin verecek bir PDDL problem dosyası istenir; birden çok :goal belirtmesine izin verilir ("tek bir görev var diye tek hedef varsaymayın; görevi başarmak için alt-hedef gerekebilir"); alan dosyası, ham durum, görev (mission) ve alan tarifi verilir.
- **Kutu 7: Düşük Seviyeli Dünya Modeli Üretme.** LLM'den oynadığı oyunun bir geçiş modelini bulması istenir; bir BFS düşük seviyeli planlayıcı bu modeli seviyeleri kazandıracak düşük seviyeli eylemleri bulmak için kullanır; rastgele eylemlerden sonraki durum geçişleri yardım için verilir ("bir eylem sonrası değişiklik dönmüyorsa hareketin bir engelle önlendiği anlamına gelir"); alan tarifi, mevcut durum, eylem uzayı, tekrar tamponu (son rastgele eylem geçişleri), araçlar verilir; sözlük erişiminde `.get()` kullanılması ve `from utils import directions` içe aktarılması istenir; çıktı `transition_model(state, action)` Python fonksiyonudur.
- **Alan tarifleri.** Sokoban: "Kutuları deliklere iterek kazanırsınız. Kutu deliğe itilirse kaybolur." BabyAI: ajan labirentte gezinerek kazanır; ajan bir anahtara bakıyorsa onu alabilir; kapıların kilidini açabilir (durumda `open_RENK_door` olur); `agent_carrying` ajanın taşıdığı nesne adları listesidir; kapalı kapılar `toggle` ile açılır, kilitli olanlar ilgili RENK_key ile; kapalı kapılar gri duvarlar gibi engeldir; nesnelerle üst üste gelinemez, anahtarı almak için ona bitişik ve ona bakıyor olunmalıdır. Labirent ve Maze: avatarı kontrol edip hedefe ulaşın; bir tuzağa dokunursanız ölürsünüz. Minihack gezinti: ajanı aşağı merdivene götürün. Minihack Ölüm Asası: Minotor'u öldürerek kazanın; asayı kullanmak için `zap`, sonra `select_f` ve nihayet istediğiniz yönde `shoot`; bu bir eylem dizisidir (zap → select_f → yön); Minotor'u zap ile öldürmek için yaklaşık 5 kare uzakta olunmalıdır.

## Ek B. Sonuçlar ve Çıktılar

Burada TheoryCoder-2'nin öğrenilmiş tecritleri ve düşük seviyeli dünya modeli için bazı sonuç ve çıktılar verilir. Ayrıca elle tasarlanmış Kâhin tecritleri de verilir. Öğrenilen ve elle tasarlanan tecritlerin ön-koşullarda ve etkilerde benzer olduğu not edilmelidir.

**Kutu: Elle Tasarlanmış (Kâhin) BabyAI Tecritleri** (aynen):
```
(:action pickup
    :parameters (?key - object)
    :precondition (not (holding ?key))
    :effect (holding ?key))
(:action unlock
    :parameters (?door - object ?key - object)
    :precondition (and (holding ?key) (not (unlocked ?door)) (unlocks ?key ?door))
    :effect (unlocked ?door))
```

**Kutu: TheoryCoder-2'nin Öğrendiği BabyAI Tecritleri** (aynen):
```
(:action pickup
    :parameters (?agent - object ?item - object)
    :precondition (not (holding ?agent ?item))
    :effect (holding ?agent ?item))
(:action unlock
    :parameters (?agent - object ?door - object ?key - object)
    :precondition (and (holding ?agent ?key) (not (unlocked ?door)))
    :effect (unlocked ?door))
```
*(Okuyucu notu: öğrenilen `unlock` işlecinde Kâhin'deki `(unlocks ?key ?door)` ön-koşulu yoktur; yani "hangi anahtar hangi kapıyı açar" eşleşmesi düşmüştür; ajan ve nesne parametresi eklenmiştir. "Benzer ön-koşul ve etki" ifadesi bu fark yüzünden gevşektir.)*

**Kutu: TheoryCoder-2'nin Öğrendiği Düşük Seviyeli BabyAI Dünya Modeli.** Python fonksiyonu `transition_model(state, action)`: ajan konumunu, yönünü ve taşıdığı nesneleri alır; `left`/`right` eylemlerinde yönü saat yönünün tersine/yönünde döndürür; `forward` eyleminde hedef kare gri duvar veya kapalı/kilitli kapı değilse ajanı ileri taşır; `pickup` eyleminde önündeki karede anahtar varsa onu taşınanlara ekleyip durumdan çıkarır; `toggle` eyleminde önündeki kapalı/kilitli kapıyı (kilitliyse ilgili renk anahtarı taşınıyorsa) `open_RENK_door` olarak açar; `drop` eyleminde taşınan son nesneyi önündeki kareye bırakır. (Tam kod: `orijinal/main.tex`.)

---

Kaynakça: orijinal `.bib` dosyası `orijinal/` dizinindedir; çevrilmemiştir.
