# Büyük Dil Modellerinde Terkibî Muhakeme İçin Özyinelemeli Kavram Evrimi (Recursive Concept Evolution, RCE)

Yazar: Sarim Chaudhry — arXiv:2602.15725 — 17 Şubat 2026

> Tercüme notu: İngilizce LaTeX kaynağından satır satır çevrilmiştir. Formüller aynen bırakılmıştır. `\cite{...}` atıfları `[anahtar]` olarak korunmuştur. Tablolar sayılarıyla aynen taşınmıştır.

## Özet

Büyük dil modelleri birçok karmaşık muhakeme görevinde güçlü başarım gösterir; ancak terkibî (compositional) muhakeme isteyen ölçütlerde (ARC-AGI-2, GPQA, MATH, BBH, HLE) doğrulukları keskin biçimde düşer. Mevcut yöntemler, düşünce zinciri (chain-of-thought) istemi, öz-tutarlılık (self-consistency) veya pekiştirmeli öğrenme yoluyla belirteç (token) düzeyindeki aramayı genişleterek muhakemeyi iyileştirir; fakat modelin örtük (latent) temsil uzayını sabit bırakırlar. Gereken tecrit (abstraction) bu uzayda önceden kodlanmış değilse başarım çöker. Biz, önceden eğitilmiş dil modellerinin çıkarım sırasında kendi iç temsil geometrisini değiştirmesini sağlayan **Özyinelemeli Kavram Evrimi (RCE)** çerçevesini öneriyoruz. RCE, temsilî yetersizlik tespit edildiğinde doğurulan, asgarî tarif uzunluğu (MDL) ölçütüyle seçilen, birbirini tamamladığında birleştirilen ve kararlılığı korumak için kısıtlı eniyileme ile pekiştirilen, dinamik olarak üretilmiş düşük ranklı kavram alt uzayları getirir. Bu süreç, modelin mevcut tecritleri yeniden birleştirmek yerine yeni tecritler kurmasını sağlar. RCE'yi Mistral-7B ile bütünleştirip terkibî muhakeme ölçütlerinde değerlendiriyoruz. RCE, ARC-AGI-2'de 12–18 puan, GPQA ve BBH'de 8–14 puan kazanç sağlar; MATH ve HLE'de derinliğe bağlı hatada tutarlı azalma verir.

## 1. Giriş

Güncel büyük dil modelleri geniş bir görev yelpazesinde güçlü başarım gösterir; fakat çıkarım sırasında yeni tecritler kurmayı gerektiren problemlerde sistematik biçimde başarısız olur. ARC-AGI-2 [chollet2019measure], MATH [hendrycks2021math], Big-Bench Hard [suzgun2023bbh], GPQA [rein2024gpqa] ve HLE [phan2025hle] gibi ölçütlerde bu modeller, iç temsillerini görevin gereklerine uyacak şekilde yeniden yapılandıramazlar. Bir ARC ızgarasındaki gizli simetriyi keşfetmesi ya da çok adımlı mantıksal çıkarımdaki iç içe kısıtları izlemesi istenen bir model, önceden eğitilmiş temsil uzayında hiçbir yerde bulunmayabilecek ara kavramsal yapıyı kurmak zorundadır. Bunu yapacak bir mekanizma olmadan model, zaten kodladığı en yakın örüntüler arasında aradeğerleme yapmaya yönelir ve makul görünen fakat yapısal olarak yanlış cevaplar üretir.

Bu sınırlama mimarîdir: bir transformatörün gizli durumları, anlamlı yönleri ön-eğitim sırasında belirlenmiş sabit boyutlu bir uzayda vektörlerdir. Muhakeme, onu tetikleyen yöntem ne olursa olsun, bu donmuş geometri içinde cereyan eder. Düşünce zinciri istemi [wei2022cot], düşünce ağacı araması [yao2023tot] ve öz-tutarlı kod çözme [wang2023selfconsistency] modele mevcut temsil uzayını dolaşmak için daha fazla fırsat verir, ama hiçbiri uzayın kendisini değiştirmez. Belirli bir değişmezi (invariant) veya tecriti temsil etmek için gereken yönler ön-eğitimde öğrenilmemişse, ne kadar ek belirteç üretilirse üretilsin onları yaratamaz. Model, yanlış haritayla daha titiz arama yapmaktadır.

Biz, donmuş önceden eğitilmiş bir dil modeline yeni temsilî yapı yaratma, değerlendirme ve birleştirme kabiliyeti veren **Özyinelemeli Kavram Evrimi (RCE)** çerçevesini öneriyoruz. RCE, her biri $B_i \in \mathbb{R}^{d \times r}$ ($r \ll d$) düşük ranklı taban matrisiyle tanımlı ve kavramın ne zaman etkinleşeceğini belirleyen öğrenilmiş bir kapı fonksiyonu $g_i(x) \in [0,1]$ ile eşlenmiş bir **kavram alt uzayları kütüphanesi** tutarak işler. Bu alt uzaylar, tek bir kod çözücü katmanında artık akıma (residual stream) şu güncellemeyle enjekte edilir: $h' = h + \sum_{i \in A(x)} g_i(x)\, B_i B_i^\top h$; burada $A(x)$, top-$k$ seyrek kapı tarafından seçilen etkin kavramlar kümesidir. Temel modelin ağırlıkları tamamen donuk kalır; RCE yalnızca sonraki katmanların aldığı ara temsili değiştirir.

Kavram kütüphanesi, insanda tecrit oluşumunun temel yönlerini yansıtan dört mekanizmayla evrilir. **Birincisi**, bir yetersizlik işareti modelin iç güven geometrisini izler; tahminî entropi yüksek ve en üst belirteç marjı düşük olduğunda kavram doğurmayı tetikler (mevcut temsil tabanı girdi için yetersizdir). **İkincisi**, enjeksiyon katmanındaki gizli duruma koşullu küçük bir çok katmanlı algılayıcı (MLP) olarak gerçeklenen öğrenilmiş bir kavram üretici, belirli temsilî başarısızlığa göre biçilmiş aday düşük ranklı tabanlar sentezler. Bu üretici, gizli durumlardan taban matrislerine sürekli bir fonksiyondur; sabit bir envanterden seçmek yerine yeni alt uzaylar üretir. **Üçüncüsü**, adaylar, görevle ilgili kayıp azalmasını bir Asgarî Tarif Uzunluğu (MDL) maliyetiyle [rissanen1978mdl] dengeleyen bir puanlama ölçütü altında yarışır; yalnızca görev temsilini, model karmaşıklığını artırdığından daha fazla sıkıştıran kavramlar kütüphaneye kabul edilir. **Dördüncüsü**, tutarlı biçimde birlikte etkinleşen ve ortak katkısı her birinin tek tek katkısını aşan kavramlar, kırpılmış SVD ile daha yüksek mertebeli tecritlere birleştirilir ve terkibî bir hiyerarşi kurulur.

Birkaç düzenlileştirme mekanizması dejenere kütüphane büyümesini önler. Kavramlar-arası diklik cezası $\sum_{i \neq j} \|B_i^\top B_j\|_F^2$ gereksiz alt uzayları caydırır. Kavram-içi örtüşme cezası her tabanın sütunlarının dikonormal olmasını teşvik ederek boyutsal çöküşü önler. Kapı entropisi cezası dağınık yönlendirme yerine seyrek ve belirli etkinleşme örüntülerini destekler. Üstel hareketli ortalamayla kullanıma dayalı budama, tutarlı etkinleşme kazanamayan kavramları kaldırarak kütüphaneyi derli toplu tutar. Bütün bunlar temsil düzeyinde bir Occam baskısı kurar: sistem yalnızca basit, ayrık, kararlı ve geniş çapta yararlı tecritleri tutar.

RCE'yi Mistral-7B [jiang2023mistral] üzerinde gerçekleyip bütün boru hattını doğruluyoruz: kavram doğurma, MDL tabanlı kabul, seyrek kapılama, diklik düzenlileştirmesi, sinerji güdümlü birleştirme ve kullanım tabanlı budama. Kontrollü eğitim koşularında sistem beklenen davranış profilini gösterir: kavramlar her girdide değil yalnızca gerçek temsilî güçlük karşısında doğar; kütüphane doğrusal-altı büyür ve kararlılaşır; düzenlileştirme kayıpları asıl eğitim amacına kıyasla küçük kalır; birleştirilmiş kavramlar çeşitli girdilerde kalıcıdır. Her kavram yaklaşık 65 536 parametre ekler ($4096 \times 16$ taban matrisi); 128 kavramlık tam kütüphane yaklaşık 33 MB ek depolama tutar; bu, temel modelin parametre sayısının %0,25'inden azdır. Çıkarımda hesaplama yükü, belirteç başına tek bir kapı MLP ileri geçişi ile iki rank-16 matris izdüşümünden ibarettir; temel modelin dikkat ve ileri-besleme hesabına kıyasla ihmal edilebilir gecikme ekler.

Katkılarımız: 1) Terkibî muhakeme için dinamik temsil evrimini, büyük dil modellerinde eksik temel bir mimarî bileşen olarak belirliyor ve sabit örtük geometrilerin getirdiği sınırlamaları biçimselleştiriyoruz. 2) Önceden eğitilmiş modeller içinde düşük ranklı örtük alt uzayların çıkarım zamanında kavram doğurmasını, sıkıştırma tabanlı seçimini, hiyerarşik birleştirilmesini ve kararlı pekiştirilmesini sağlayan RCE'yi tanıtıyor, böylece muhakemeyi belirteç düzeyinde yörünge eniyilemesinden temsil düzeyinde uyarlanmaya dönüştürüyoruz. 3) RCE'yi Mistral-7B ile bütünleştirip ARC-AGI-2, GPQA, MATH, BBH ve İnsan-Düzeyi Değerlendirmede tutarlı iyileşmeler gösteriyor; daha güçlü terkibî genelleme, muhakeme derinliğinde artan dayanıklılık ve aramaya dayalı istem stratejilerine daha az bağımlılık sergiliyoruz.

## 2. İlgili Çalışmalar

### 2.1 Muhakeme İçin Pekiştirmeli Öğrenme

Son çalışmalar büyük dil modellerinde muhakemeyi iyileştirmek için pekiştirmeli öğrenmeyi araştırmıştır. DeepSeek-R1'deki kullanımıyla yaygınlaşan Grup Göreli Politika Eniyilemesi (GRPO) [shao2024deepseekmath], örneklenmiş cevapları bir grup taban çizgisine göre puanlayarak muhakeme yörüngelerini eniyiler. Zhang vd. [zhang2025disco], GRPO'nun grup-göreli avantaj fonksiyonunda doğuştan bir zorluk yanlılığı tespit edip DisCO'yu önerirler: grup-göreli amaçları ayırt edici öğrenmeye dayanan puanlama fonksiyonlarıyla değiştiren ayırt edici kısıtlı bir eniyileme çerçevesi; matematiksel muhakeme ölçütlerinde GRPO ve DAPO'ya göre %6–7 kazanç. Ye vd. [ye2025enigmata], çok görevli RLVR eğitimi için üreteçleri ve doğrulayıcıları olan 36 bulmaca görevinden oluşan ENIGMATA'yı tanıtır; bulmaca tabanlı pekiştirmeli öğrenmenin ARC-AGI ve matematik problemi çözme dahil alan-dışı muhakeme ölçütlerine aktarıldığını gösterir. Qu vd. [qu2025raif], karmaşık kısıt yapılarında sade düşünce zincirinden doğan yüzeysel muhakeme örüntülerini ele alan, kural merkezli ödül işaretleri ve örnek-bazlı karşıtlıkla talimat izlemede muhakemeyi özendiren RAIF'i önerir.

Bu yöntemler ortak bir yapısal sınırlamayı paylaşır: üretilmiş cevap dizileri uzayı üzerinde eniyileme yaparlar; doğru çıktılara götüren yörüngeleri seçer veya pekiştirirler. Bu yörüngelerin içinde üretildiği temsil geometrisi sabit kalır. GRPO veya RLVR ile eğitilmiş bir model mevcut örtük uzayı içinde daha etkili muhakeme yapar; ancak görev ön-eğitimde bulunmayan tecritler istediğinde yeni temsil eksenleri kuramaz. RCE bu boşluğu, çıktı dağılımı yerine temsilin kendisi üzerinde işleyerek ele alır; yörünge düzeyi eniyilemenin üretemeyeceği yeni kavramsal yapının oluşmasını sağlar.

### 2.2 Sembolik ve Modüler Muhakeme

Paralel bir çalışma hattı, dil modellerini model çıktılarına biçimsel mantık kuralları uygulayan yapılı muhakeme modülleriyle destekler. Wang vd. [wang2025muslr], çıkarımı algı ve mantık safhalarına ayrıştıran, önermeler, yüklemler ve birinci derece mantık dahil biçimsel kuralları çok kipli girdilere uygulayan çok kipli sembolik mantıksal muhakeme çerçevesi MuSLR'yi tanıtır. Değerlendirmeleri, GPT-4.1 gibi öncü modellerin bile sembolik muhakeme görevlerinde yalnızca %46,8'e eriştiğini, başarısızlıkların yaklaşık %70'inin kipler arası mantıksal uyumsuzluğa atfedilebileceğini gösterir. İlgili yaklaşımlar arasında model çıktılarına katı mantıksal kısıtlar koyan nörosembolik doğrulama çerçeveleri [nye2021scratchpad] ve muhakemeyi yürütülebilir koda dışsallaştıran program sentezi yöntemleri [chen2021codex] vardır.

Bu yaklaşımların ortak sınırı, muhakeme modüllerinin tasarım zamanında sabitlenmiş olmasıdır. Mantıksal işlemler kümesi, ayrıştırma yapısı ve algı ile muhakeme arasındaki arayüz sistem mimarı tarafından önceden belirlenir. Bir görev modül tasarımının öngörmediği bir muhakeme biçimi gerektirdiğinde sistem uyum sağlayamaz. RCE'de ise kavram kütüphanesi temsilî talebe karşılık organik olarak büyür: mevcut alt uzaylar yetmediğinde yenileri doğar; hiyerarşik tecritler elle belirlenmiş terkip kuralları yerine veriye dayalı birleştirmeyle oluşur.

### 2.3 Yapılı Temsil Öğrenmesi

Öz-denetimli öğrenme yöntemleri, sahneleri veya girdileri anlamlı bileşenlere ayrıştıran yapılı temsilleri araştırmıştır. Huang vd. [huang2025cgssl], yama özellikleriyle çapraz dikkat yoluyla öğrenilen kavram belirteçleriyle standart öz-denetimli öğrenmeyi zenginleştiren CG-SSL'yi önerirler; maskeli damıtma ve artırılmış görünümler arası geometrik hizalama ile görsel kavramlar keşfeder. Slot Attention [locatello2020slotattention] ve SAVi [kipf2022savi] gibi nesne merkezli yaklaşımlar, yinelemeli dikkat tabanlı bağlamayla görsel sahneleri nesne düzeyinde temsillere ayrıştırmayı öğrenir. Dil alanında sözlük öğrenmesi ve seyrek otokodlayıcılar [bricken2023monosemanticity], transformatör gizli durumlarını yorumlanabilir özelliklere ayrıştırmak için kullanılmıştır.

Bu yöntemler temsilleri eğitim zamanında yapılandırır ama çıkarım sırasında temsilî evrimi desteklemez. Kavram belirteçleri veya nesne yuvaları kümesi eğitimden sonra sabittir; model eğitimde görülmemiş ayrıştırmalar gerektiren girdilerle karşılaştığında yeni yapısal ilkeller doğamaz. RCE, kavram kütüphanesinin hem eğitim hem de çıkarım zamanında genişlemesine izin vererek bu boşluğu kapatır; MDL tabanlı seçim, yeni kavramların tekil örneklere aşırı uymak yerine genellemesini sağlar.

### 2.4 Düşünce Zinciri ve Test-Zamanı Hesaplama Ölçekleme

Düşünce zinciri istemi [wei2022cot] ve uzantıları (düşünce ağacı [yao2023tot], öz-tutarlılık [wang2023selfconsistency], adım düzeyi ışın araması [lightman2023prm]) birden çok muhakeme yörüngesi üretip değerlendirerek test zamanındaki etkin hesaplama bütçesini artırır. Bu yöntemler, modele doğru ara sonuçlara varmak için daha fazla fırsat sunarak çok adımlı görevlerde başarımı artırır ve örneklenen yörünge sayısıyla öngörülebilir biçimde ölçeklenir.

Bu yaklaşımların temel kısıtı, bütün muhakemenin modelin sabit örtük geometrisi içinde cereyan etmesidir. Her ek düşünce zinciri adımı veya ağaç dalı aynı temsil uzayına gürültü ekler ve bu gürültü muhakeme derinliğiyle birikir. Beş veya daha fazla terkibî adım isteyen görevlerde başarım, model bilgiden yoksun olduğu için değil, donmuş temsildeki işaret-gürültü oranı alt katmanların ilgili yapıyı güvenilir biçimde çıkarabileceği eşiğin altına düştüğü için bozulur. RCE bunu doğrudan ele alır: kavram izdüşümü ilgisiz boyutları bastırırken göreve ilgili yönleri güçlendirir ve belirteç düzeyi muhakeme yöntemlerinin derinlik ölçeklemesini sınırlayan gürültü birikimini önler.

## 3. Problemin Kurulumu

$\theta$ parametreli ve $d$ gizli boyutlu, önceden eğitilmiş özbağlanımlı bir dil modeli $f_\theta$ düşünelim. $x = (x_1, \ldots, x_T)$ girdi dizisi için model her $\ell$ katmanında $h_t \in \mathbb{R}^d$ gizli durumlarını $h_t^{(\ell+1)} = f_\theta^{(\ell)}(h_t^{(\ell)})$ özyinelemesiyle üretir; $f_\theta^{(\ell)}$ öz-dikkat ve ileri-besleme alt katmanlarını içeren $\ell$-inci kod çözücü katmanıdır.

Herhangi bir katmandaki gizli durumlar $\mathbb{R}^d$'nin, asıl yönleri ön-eğitim dağılımınca belirlenen bir alt uzayını gerer. Modelin $\ell$ katmanındaki **etkin temsilî rankını**, $\Sigma^{(\ell)} = \mathbb{E}[h^{(\ell)} {h^{(\ell)}}^\top]$ gizli durum kovaryans matrisinin $\epsilon$ eşiğini aşan tekil değerlerinin sayısı olarak tanımlarız. Sabit bir model için bu rank sınırlıdır ve girdi ne olursa olsun çıkarım zamanında artamaz.

Bu sabit rank yapısal bir darboğaz yaratır. $\mathcal{T}$, modelin $\mathbb{R}^d$'de $k$ dik yönün $\{v_1, \ldots, v_k\}$ doğrusal birleşimi olarak ifade edilebilen gizli bir $s^*$ yapısını temsil etmesini isteyen bir görev olsun. $s^*$'ın $\Sigma^{(\ell)}$'in sütun uzayına izdüşümünün normu, küçük bir $\delta$ için $\delta \|s^*\|$'dan az ise, görevle ilgili yapı, kullanılan kod çözme stratejisi ne olursa olsun, modelin alt katmanlarına fiilen görünmezdir.

RCE'nin amacı, modelin etkin temsil alt uzayını çıkarım sırasında uyarlanabilir biçimde genişletecek, önceden eğitilmiş modelin genelleme ve kararlılık özelliklerini koruyacak bir mekanizma eklemektir. Biçimsel olarak, $P_i = B_i B_i^\top$, $B_i \in \mathbb{R}^{d \times r}$, $r \ll d$ olan düşük ranklı işleçler ailesi $\{P_i\}_{i=1}^N$ ve $|A(x)| \leq k$ olan girdiye bağlı bir seçim mekanizması $A(x) \subset \{1, \ldots, N\}$ ararız; öyle ki artırılmış gizli durum

$$h' = h + \sum_{i \in A(x)} g_i(x)\, B_i B_i^\top h \tag{1}$$

iki şartı sağlar: (i) $s^*$'ın artırılmış temsile izdüşümünün normu en az $(1-\delta')\|s^*\|$'dir ($\delta' \ll \delta$), ve (ii) kavram kütüphanesinin toplam karmaşıklığı $\sum_i \Omega(B_i)$ bir tarif uzunluğu kısıtı altında sınırlı kalır.

## 4. Özyinelemeli Kavram Evrimi

### 4.1 Kavram Alt Uzayı Tanımı

RCE çerçevesinde bir kavram $C_i$ üç bileşenden oluşur: gizli uzayın düşük ranklı bir alt uzayını tanımlayan dikonormal sütunlu $B_i \in \mathbb{R}^{d \times r}$ taban matrisi; belirli bir girdi için kavramın etkinleşme şiddetini belirleyen $g_i: \mathbb{R}^d \to [0,1]$ kapı fonksiyonu; ve gizli durumları kavramın alt uzayına ve geri taşıyan $P_i = B_i B_i^\top$ izdüşüm işleci. $r$ ranki, her kavramın ifade gücünü denetleyen bir hiperparametredir; deneylerimizde $r = 16$ kullanırız: simetri, geçişlilik veya cebirsel değişmezlik gibi tek yapısal ilkelleri yakalamaya yeter, tam gizli boyut $d = 4096$'ya kıyasla hesap bakımından ihmal edilebilir kalır.

Enjeksiyon mekanizması tek bir belirlenmiş kod çözücü katmanı $\ell^*$'da işler. $h \in \mathbb{R}^{B \times T \times d}$ gizli durumları $\ell^*$ katmanından çıkarken RCE modülü bunları ileri kancasıyla (forward hook) yakalar ve Denklem 1'deki güncellemeyi uygular. $A(x)$ kümesi seyrek top-$k$ kapıyla belirlenir: SiLU etkinleştirmeli iki katmanlı bir MLP, dizi-havuzlanmış gizli durumu kütüphanedeki tüm kavramlar üzerinde bir olasılık dağılımına eşler ve en yüksek olasılıklı $k$ kavram seçilir. Kapı ağırlıkları $\sum_{i \in A(x)} g_i(x) = 1$ olacak biçimde normalize edilir; böylece enjekte edilen sapmanın büyüklüğü denetlenir. Değiştirilmiş gizli durumlar $\ell^* + 1$'den $L$'ye katmanlardan donmuş parametreleriyle zenginleşmiş temsili işleyerek geçer.

### 4.2 Doğurma Mekanizması

Kavram doğurma, modelin çıktı logitlerinden hesaplanan bir temsilî yetersizlik işaretiyle tetiklenir. Başarısızlık puanını tahminî entropi ile güven marjının bileşiği olarak tanımlarız:

$$F(x) = \frac{H(\text{logits})}{M(\text{logits}) + \epsilon} \tag{2}$$

Burada $H(\text{logits}) = -\sum_v p_v \log p_v$ sonraki-belirteç dağılımının entropisi, $M(\text{logits}) = p_{(1)} - p_{(2)}$ en yüksek iki belirteç olasılığı arasındaki marj, $\epsilon$ sayısal kararlılık için küçük bir sabittir. Yüksek entropi ile düşük marjın birlikteliği, modelin mevcut temsil tabanı altında girdiyi güvenle çözemediğini gösterir; göreve özgü etiket veya ödül fonksiyonu gerektirmeyen, türevsiz bir işaret sağlar.

$F(x) > \tau$ olduğunda sistem, kavram üreticisi $G$ ile $k_s$ aday alt uzay üretir. Üretici, enjeksiyon katmanındaki havuzlanmış gizli durumu ham bir taban matrisine eşleyen üç katmanlı bir MLP'dir:

$$\hat{B} = G(h_{\text{pool}}) \in \mathbb{R}^{d \times r}, \quad h_{\text{pool}} = \frac{1}{T}\sum_{t=1}^{T} h_t^{(\ell^*)}$$

Tek bir üretici çağrısından $k_s$ çeşitli aday elde etmek için her aday $\sigma = 0.03$ ölçekli eşyönlü Gauss gürültüsüyle bozulur, sonra her taban matrisinin sütunlarının dikonormal olması için QR ayrışımıyla dikleştirilir. Üretici, enjeksiyon mekanizması üzerinden uçtan uca eğitilir: dil modelleme kaybından gelen gradyanlar kancadan, kavram izdüşümünden geçip üreticinin parametrelerine ulaşır; böylece başarısızlık puanı yüksek girdilerde modelin tahmin hatasını azaltan alt uzaylar üretmeyi öğrenir.

### 4.3 Asgarî Tarif Uzunluğu Yoluyla Yarış

Her aday alt uzay kütüphaneye girmemelidir. Bir girdide kaybı marjinal olarak azaltıp diğerlerinde genellemeyi bozan karmaşıklık ekleyen bir kavram, hiç kavram olmamasından kötüdür. Seçimi, kabul edilen her kavramın görev temsilini kütüphanenin kodlama maliyetini artırdığından fazla sıkıştırmasını isteyen bir Asgarî Tarif Uzunluğu ölçütüyle [rissanen1978mdl, grunwald2007mdl] uygularız.

$C_i$ kavramının MDL maliyeti:

$$\Omega(C_i) = \alpha \|B_i\|_* + \beta\, \text{KL}(g_i(x) \| \pi_i) \tag{3}$$

Burada $\|B_i\|_*$ taban matrisinin nükleer normudur (etkin ranki ve büyüklüğü cezalandırır), $\text{KL}(g_i(x) \| \pi_i)$ kapı etkinleşme örüntüsünün düşük etkinleşme olasılıklı seyrek bir önsel $\pi_i$'den sapmasını cezalandırır, $\alpha, \beta$ yapısal sadelik ile etkinleşme seyrekliğinin göreli ağırlığını denetleyen hiperparametrelerdir. Bir aday kütüphaneye ancak ve ancak şu halde kabul edilir:

$$\Delta L - \lambda\, \Omega(C_{\text{new}}) > 0 \tag{4}$$

Burada $\Delta L$, adayın alt uzayı üzerinden izdüşümle gizli durumda elde edilen yeniden-kurma hatası azalmasıdır, $\lambda$ MDL kapısının sıkılığını ayarlar. Bu ölçüt kavram kütüphanesinin eğitim adımlarıyla doğrusal-altı büyümesini sağlar: kütüphane temsilî değişimin baskın kiplerini kapsayan kavramlar biriktirdikçe ek kavramların marjinal faydası azalır, MDL maliyeti sabit kalır; büyüme kendiliğinden kısılır.

### 4.4 Birleştirme Kuralı

Çeşitli girdilerde tutarlı biçimde birlikte etkinleşen ve ortak katkısı her birinin tek tek katkısını aşan kavramlar, daha yüksek mertebeli bir tecritte birleştirilmeye adaydır. $C_i$ ve $C_j$ arasındaki sinerjiyi şöyle tanımlarız:

$$\text{Syn}(i, j) = L(\mathcal{C} \setminus \{i, j\} \cup \{ij\}) - L(\mathcal{C}) \tag{5}$$

Burada $L(\mathcal{C})$, $\mathcal{C}$ kavram kütüphanesi altında görev kaybıdır; $C_{ij}$ iki tabanın birleştirilip kırpılmış SVD ile sıkıştırılmasıyla elde edilen birleşik kavramdır: $[B_i \mid B_j] \in \mathbb{R}^{d \times 2r}$ en büyük $r$ sol tekil vektör tutularak rank $r$'ye indirilir, ardından QR dikleştirmesi yapılır. Birleştirme şu halde kabul edilir:

$$\text{Syn}(i, j) < -\lambda_m \big(\Omega(C_{ij}) - \Omega(C_i) - \Omega(C_j)\big) \tag{6}$$

yani birleşik kavram başarımı, kodlama maliyetindeki artıştan daha fazla iyileştirmelidir. Bu, sahte birlikte-etkinleşme korelasyonlarına dayalı birleştirmeyi önler: birkaç girdide tesadüfen birlikte ateşlenen fakat birleşimi gerçek sinerji vermeyen iki kavram MDL denetimini geçemez. Başarılı birleştirmeler, ilkel alt uzayların daha yüksek seviyeli tecritlere terkip ettiği bir kavram hiyerarşisi kurar; insan öğrenenlerin temel işlemleri (simetri tespiti, renk eşlemesi) bütünleşik stratejilere (yansıt-ve-yeniden-boya) birleştirmesine benzer.

### 4.5 Billurlaşma (Crystallization)

Kütüphanede birçok eğitim adımı boyunca kalıcı olan, yüksek kullanımı sürdüren, çeşitli görev türlerinde genelleyen ve dağılım-dışı dayanıklılığa katkı yapan kavramlar uzun vadeli yapıya billurlaşmaya adaydır. Mevcut gerçeklemede billurlaşma kontrol noktası (checkpoint) alınarak sağlanır: tüm kavram kütüphanesi, kapı ağı ve üretici düzenli aralıklarla diske serileştirilir; en son kontrol noktası sonraki eğitim veya çıkarım oturumlarının başlangıcı olur.

Temel modelle daha derin bütünleşme için billurlaşma, yüksek değerli kavramları kalıcı LoRA-tarzı adaptörlere [hu2022lora] damıtan kısıtlı eniyilemeyle yürütülebilir. Daha önce billurlaşmış kavramlarla yıkıcı girişimi önlemek için damıtma, Fisher bilgi matrisiyle tanımlı bir güven bölgesiyle kısıtlanır:

$$\min_{\Delta\theta}\; \mathcal{L}_{\text{new}}(\theta + \Delta\theta) \quad \text{s.t.} \quad \Delta\theta^\top F \Delta\theta \leq \epsilon \tag{7}$$

Burada $F$, her mevcut kavram için temsilî görevlerin bir tekrar tamponu üzerinde hesaplanmış deneysel Fisher'dir; $\epsilon$ önceki kavramlar için önemli parametre uzayı bölgelerinde işlevsel değişimi sınırlar. Elastik ağırlık pekiştirmesinden [kirkpatrick2017ewc] yararlanan bu formülasyon, billurlaşmayı kavram kütüphanesinin birikimli doğasını koruyan gerilemeyen bir pekiştirme adımına dönüştürür.

## 5. Eniyileme Çerçevesi

### 5.1 Eğitim Amacı

Toplam eğitim amacı, temel dil modelleme kaybını kavram kütüphanesi sağlığını yöneten düzenlileştirme terimleriyle birleştirir:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{LM}} + \lambda_{\text{orth}} \sum_{i \neq j} \|B_i^\top B_j\|_F^2 + \lambda_{\text{ov}} \frac{1}{N}\sum_{i=1}^N \|B_i^\top B_i - I_r\|_F^2 + \lambda_{\text{gate}} \mathcal{H}(g) \tag{8}$$

Burada $\mathcal{L}_{\text{LM}}$ sonraki-belirteç tahmininde standart çapraz-entropi kaybı, ikinci terim farklı kavram alt uzayları arasındaki örtüşmeyi cezalandırır, üçüncü terim her tabandaki sütunların dikonormalliğini teşvik eder, $\mathcal{H}(g) = -\sum_{i} g_i \log g_i$ kapı dağılımının entropisidir ve seyrek yönlendirme için cezalandırılır. Yalnızca RCE parametreleri (kavram tabanları, kapı ağı, üretici) gradyan alır; temel model parametreleri $\theta$ eğitim boyunca donuktur.

### 5.2 Ayırt Edici Kavram Puanlaması

Zhang vd. [zhang2025disco]'nun önerdiği ayırt edici öğrenme çerçevesinden yararlanarak yarış safhasında kavram değerlendirmesine ayırt edici bir amaç ekleriz. Adayları yalnızca dil modelleme kaybı üzerindeki etkilerine göre puanlamak, kavram kalitesini temel modelin ilgisiz davranış yönleriyle karıştırır; bunun yerine adayları doğru ve yanlış tamamlamaları ayırt edebilme kabiliyetleriyle değerlendiririz:

$$\mathcal{L}_{\text{disc}} = \mathbb{E}\big[\log s(x, y^+)\big] - \mathbb{E}\big[\log s(x, y^-)\big] \tag{9}$$

Burada $s(x, y)$, $x$ girdisinin doğru tamamlaması $y^+$ ve yanlış tamamlaması $y^-$ ile eşlenerek kavramla artırılmış gizli durumlar üzerinde hesaplanan bir puanlama fonksiyonudur. Bu amaç grup-göreli yöntemlerde saptanan zorluk yanlılığından muaftır: puanları grup içinde normalize etmez; böylece her kavramın katkısı mutlak ölçekte değerlendirilir. Ayırt edici puan, doğurma sırasında yeniden-kurmaya dayalı aday değerlendirmesini tamamlar ve denetimli etiketler mevcut olduğunda göreve dayanan bir işaret sağlar.

### 5.3 KL-Kısıtlı Güncellemeler

RCE modülünün eğitim sırasında temel modelin çıktı dağılımından çok uzaklaşmasını önlemek için artırılmış modelin tahminlerine KL ıraksaklığı kısıtı koyarız:

$$\max_{\phi}\; J(\phi) \quad \text{s.t.} \quad \text{KL}\big(\pi_{\theta,\phi}(\cdot | x)\;\|\;\pi_{\theta}(\cdot | x)\big) \leq \epsilon_{\text{KL}} \tag{10}$$

Burada $\phi$ RCE parametrelerini, $\pi_{\theta,\phi}$ artırılmış modelin çıktı dağılımını, $\pi_\theta$ donmuş temel modelin dağılımını gösterir. Uygulamada bunu eğitim amacına eklenen $\lambda_{\text{KL}} \cdot \text{KL}(\pi_{\theta,\phi} \| \pi_\theta)$ ceza terimi olarak gerçekleriz; $\lambda_{\text{KL}}$ kısıtı sürdürmek için ikil gradyan inişiyle ayarlanır. Bu, kavram enjeksiyonunun muhakeme kabiliyetini, mevcut temsilin zaten yeterli olduğu görevlerde temel modelin akıcılığını veya olgusal doğruluğunu bozmadan iyileştirmesini sağlar.

## 6. Kuramsal Çözümleme

### 6.1 Temsil Kapasitesi Genişlemesi

Kavram enjeksiyonunun artırılmış modelin etkin temsilî rankını kesin biçimde artırdığını gösteririz. $\Sigma$ temel model altında $\ell^*$ katmanındaki gizli durumların kovaryansı, $\Sigma'$ RCE artırması altındaki kovaryans olsun.

**Önerme.** Taban $B_i$ ve pozitif ölçülü bir girdi kümesinde pozitif kapı etkinleşmesi $g_i(x) > 0$ olan herhangi bir $C_i$ kavramı için etkin rank $\text{rank}_\epsilon(\Sigma') \geq \text{rank}_\epsilon(\Sigma)$'yı sağlar; $B_i$'nin $\Sigma$'nın sıfır uzayına aşikâr-olmayan izdüşümü varsa eşitsizlik katıdır.

İspat, $h' = h + g_i B_i B_i^\top h$ enjeksiyonunun artırılmış kovaryans $\Sigma'$'ne pozitif yarı-belirli bir bileşen $g_i^2 B_i B_i^\top \Sigma B_i B_i^\top$ eklediği gözleminden çıkar. $B_i$'nin desteği $\Sigma$'nın sütun uzayı dışındaysa bu bileşen yeni sıfırdan farklı özdeğerler getirir ve etkin ranki artırır. Kavramlar arası diklik düzenlileştirmesi, farklı kavramların temsili ayrı yönlerde genişletmesini sağlar ve belirli sayıda kavramdan toplam rank artışını azamîleştirir.

### 6.2 Zorluk Yanlılığından Kaçınma

GRPO gibi grup-göreli yöntemler avantaj kestirimlerini örneklenmiş cevap grubu içinde normalize ederek kolay soruların gradyan işaretine orantısız katkı yaptığı bir zorluk yanlılığı yaratır [zhang2025disco]. RCE, kavram değerlendirmesi çıktı-düzeyi puanlar yerine gizli durum geometrisi üzerinde işlediği için bu yanlılıktan tümüyle kaçınır. MDL kabul ölçütü (Denklem 4) her aday kavramı gizli durumdaki yeniden-kurma iyileşmesiyle değerlendirir; bu, görev zorluğundan bağımsız mutlak bir temsilî fayda ölçüsüdür. Farklı zorlukta görevlerde aynı yeniden-kurma iyileşmesini sağlayan iki kavram aynı MDL puanını alır; yörünge düzeyi eniyilemeyi rahatsız eden grup-göreli çarpıtma ortadan kalkar.

### 6.3 Genelleme Sınırı

Kavram kütüphanesinin tarif uzunluğunu içeren, artırılmış model için bir genelleme sınırı türetiriz. $\mathcal{C} = \{C_1, \ldots, C_N\}$ kavram kütüphanesi, $\Omega(\mathcal{C}) = \sum_{i=1}^N \Omega(C_i)$ toplam MDL maliyeti olsun.

**Teorem.** Standart PAC-Bayes varsayımları altında, herhangi bir $\mathcal{D}$ dağılımı için ve $n$ boyutlu eğitim kümeleri üzerinde en az $1 - \delta$ olasılıkla:

$$\mathbb{E}_{\mathcal{D}}[\mathcal{L}] \leq \hat{\mathbb{E}}_{\text{train}}[\mathcal{L}] + \mathcal{O}\left(\sqrt{\frac{\Omega(\mathcal{C}) + \log(1/\delta)}{n}}\right) \tag{11}$$

Bu sınır MDL kısıtının rolünü açığa çıkarır: nükleer norm cezaları, kapı seyrekliği ve kullanıma dayalı budama yoluyla $\Omega(\mathcal{C})$'yi küçük tutarak RCE genelleme sınırındaki karmaşıklık terimini denetler. MDL kabul ölçütü (Denklem 4) bu sınırı tek tek kavramlar düzeyinde uygulayan olarak yorumlanabilir: bir kavram ancak ampirik kaybı azaltmaya katkısı karmaşıklık terimine katkısını aşarsa kabul edilir.

## 7. Deney Kurulumu

### 7.1 Temel Modeller

RCE'yi farklı ölçek ve mimarideki üç önceden eğitilmiş dil modelinde değerlendiririz: iyi incelenmiş bir temsil geometrisi sağlayan 4096 gizli boyut ve 32 katmanlı kod çözücüsü nedeniyle birincil geliştirme platformu olan Mistral-7B-v0.1 [jiang2023mistral]; benzer ölçekte farklı bir ön-eğitim dağılımı ve belirteçleyiciyle karşılaştırma noktası sunan Llama-3-8B [touvron2023llama]; ve temel modelin kendi temsil kapasitesinin çok daha büyük olduğu daha büyük ölçekte RCE'nin yararlarının sürüp sürmediğini sınayan Qwen-2.5-14B [yang2024qwen]. Bütün modeller bfloat16 kesinliğinde yüklenir, ağırlıklar eğitim ve çıkarım boyunca tümüyle donuktur.

### 7.2 Ölçütler

Terkibî muhakemenin farklı yönlerini zorlamak için seçilmiş beş ölçüt kullanırız. ARC-AGI-2 [chollet2019measure], birkaç girdi-çıktı ızgara çiftinden gizli dönüşüm kurallarının çıkarımını gerektirir; değişmez keşfi ve uzamsal tecrit ister. MATH [hendrycks2021math], çok adımlı cebirsel işlem, ikame keşfi ve ispat kurma gerektiren yarışma düzeyinde matematik problemlerinden oluşur. Big-Bench Hard (BBH) [suzgun2023bbh], BIG-Bench'ten çok adımlı muhakeme, örtük kısıt izleme ve terkibî mantık isteyen 23 zor görevdir. GPQA [rein2024gpqa], fizik, kimya ve biyolojide lisansüstü düzeyde bilimsel problem çözmeyi sınar; alanlar-arası tecrit ve çok katmanlı nedensel muhakeme ister. HLE [phan2025hle], aktarım, nadir örüntülere genelleme ve dağılım kaymasında dayanıklılığı değerlendirir; RCE'nin kavram kütüphanesinin eğitim dağılımının ötesinde yapısal genellemeyi destekleyip desteklemediğinin en doğrudan sınamasını sağlar.

### 7.3 Taban Çizgileri

Muhakeme iyileştirme yöntemlerinin mevcut yelpazesini temsil eden beş taban çizgisiyle karşılaştırırız. Düşünce zinciri (CoT) istemi [wei2022cot], adım adım muhakeme izleriyle az-örnekli örnekler kullanır. Öz-tutarlılık (SC) [wang2023selfconsistency], birden çok muhakeme zinciri örnekler ve çoğunluk oyuyla en yaygın cevabı seçer. Düşünce ağacı (ToT) [yao2023tot], geri izlemeli birden çok muhakeme dalını araştırıp en yüksek puanlı yolu seçer. GRPO [shao2024deepseekmath], doğrulanabilir ödüllü muhakeme görevlerinde grup-göreli politika eniyilemesiyle modeli ince ayarlar. DisCO [zhang2025disco], GRPO'nun grup-göreli amacını ayırt edici puanlama ve kısıtlı eniyilemeyle değiştirir. GRPO ve DisCO için, RCE kavram kütüphanesi gelişimi için kullanılan aynı muhakeme veri kümelerinde eğitim yapılarak yayımlanmış gerçeklemeler önerilen hiperparametreleriyle kullanılır.

### 7.4 RCE Yapılandırması

Kavram kütüphanesi boş başlatılır ve eğitim sırasında evrilir. Enjeksiyon, orta-geç katmanların en göreve-ayırt edici temsilleri içerdiğini gösteren ön deneylere dayanarak $\ell^* = 18$ kod çözücü katmanında (32 katmanlı modellerde yaklaşık %56 derinlik) yapılır. Her kavram rank $r = 16$, top-$k = 2$ seyrek kapılıdır. Kütüphane kapasitesi $N_{\max} = 128$ kavramla sınırlıdır; budama 96 kavramda tetiklenir. Kavram üretici, 512 gizli boyutlu ve SiLU etkinleştirmeli üç katmanlı MLP'dir. Eğitim; $2 \times 10^{-4}$ öğrenme oranı, 0,01 ağırlık sönümü, 1,0'da gradyan kırpması ve 200 ısınma adımlı kosinüs öğrenme oranı çizelgesiyle AdamW kullanır. Doğurma eşiği $\tau = 5.0$, MDL kabul ağırlığı $\lambda = 0.5$, diklik cezası $\lambda_{\text{orth}} = 0.05$, örtüşme cezası $\lambda_{\text{ov}} = 0.02$, kapı entropisi cezası $\lambda_{\text{gate}} = 0.01$'dir. Birleştirme her 800 eğitim adımında, 0,002 sinerji eşiğiyle ve değerlendirme başına en çok 12 birleştirme adayıyla yoklanır.

## 8. Sonuçlar

### 8.1 Ana Ölçüt Sonuçları

Tablo 1 beş terkibî muhakeme ölçütünde doğruluğu bildirir. RCE, ölçütler ve model ölçekleri boyunca bütün taban çizgilerine göre tutarlı kazançlar sağlar. Mistral-7B'de RCE, en güçlü taban çizgisi DisCO'ya göre ARC-AGI-2'de %8,3, MATH'ta %6,1, BBH'de %5,7, GPQA'da %7,2 ve HLE'de %4,9 iyileşme verir. Kazançlar, ön-eğitimli sezgisellere güvenmeyi en çok cezalandıran ve değişmez keşfi ile alanlar-arası tecriti en çok ödüllendiren iki ölçüt olan ARC-AGI-2 ve GPQA'da en büyüktür. 14B ölçeğinde (Qwen-2.5-14B) mutlak iyileşmeler daha küçüktür ama anlamlı kalır; bu, temel modelin temsil kapasitesi çok daha büyük olduğunda bile RCE'nin tamamlayıcı yetenek sağladığını gösterir.

**Tablo 1.** Terkibî muhakeme ölçütlerinde doğruluk (%). RCE sonuçları, karma muhakeme müfredatında eğitilmiş 47 billurlaşmış kavramlı bir kütüphaneyle Mistral-7B'dendir. Llama-3-8B ve Qwen-2.5-14B için "öngörülen" (projected) sonuçlar, Mistral-7B gerçeklemesinden doğrulanmış bileşen düzeyi ölçeklemeye dayanır.

| Yöntem | Model | ARC-AGI-2 | MATH | BBH | GPQA | HLE |
| :-- | :-- | --: | --: | --: | --: | --: |
| Temel | Mistral-7B | 12.4 | 28.6 | 51.3 | 24.1 | 8.2 |
| CoT | Mistral-7B | 15.1 | 34.2 | 57.8 | 28.5 | 10.1 |
| SC ($n$=16) | Mistral-7B | 16.8 | 37.1 | 60.2 | 30.3 | 11.4 |
| ToT | Mistral-7B | 17.3 | 36.8 | 59.5 | 31.0 | 11.9 |
| GRPO | Mistral-7B | 18.2 | 38.9 | 62.1 | 32.4 | 12.6 |
| DisCO | Mistral-7B | 19.7 | 41.3 | 64.8 | 34.2 | 13.8 |
| RCE | Mistral-7B | **28.0** | **47.4** | **70.5** | **41.4** | **18.7** |
| Temel | Llama-3-8B | 14.1 | 31.4 | 54.7 | 27.3 | 9.6 |
| RCE | Llama-3-8B | **29.8** | **49.1** | **72.3** | **43.1** | **20.2** |
| Temel | Qwen-14B | 19.3 | 42.8 | 63.5 | 36.7 | 14.3 |
| RCE | Qwen-14B | **33.6** | **54.2** | **76.1** | **48.9** | **23.1** |

### 8.2 Dağılım-Dışı Dayanıklılık

RCE kavramlarının yüzeysel ipuçlarını değil yapısal değişmezleri yakalayıp yakalamadığını değerlendirmek için ARC-AGI-2 değerlendirme kümesine uygulanan üç sistematik dağılım kaymasında sınama yaparız: renk permütasyonu (renk paletinin rastgele yeniden eşlenmesi), uzamsal dönme (ızgaraların 90 derece döndürülmesi) ve çeldirici ekleme (alttaki dönüşüm kuralını koruyan ilgisiz ızgara öğelerinin eklenmesi). Tablo 2 standart değerlendirmeye göre başarım korunumunu bildirir.

**Tablo 2.** ARC-AGI-2'de dağılım kayması altında başarım korunumu (standart doğruluğun %'si).

| Yöntem | Renk Perm. | Uzamsal Dön. | Çeldirici |
| :-- | --: | --: | --: |
| CoT | 71.2 | 68.4 | 74.1 |
| DisCO | 78.5 | 73.9 | 80.2 |
| RCE | **94.3** | **91.7** | **95.8** |

RCE, taban çizgilerinin %68–80'ine karşılık, üç kayma türünde de standart doğruluğunun %91'inden fazlasını korur. Bu, kavram kütüphanesinin dağılım kaymasında bozulan yüzey özelliklerini (belirli renkler, mutlak konumlar) değil yapısal değişmezleri (uzamsal ilişkiler, dönüşüm kuralları) kodladığını doğrular. Diklik düzenlileştirmesi ve MDL tabanlı seçim bu dayanıklılık için kritiktir: yüzey ipuçlarına bağlı kavramlar müfredatın ortamsal artırmaları boyunca genelleyemez ve billurlaşmadan önce budanır.

### 8.3 Kavram Kütüphanesi Çözümlemesi

Karma muhakeme müfredatında 10 000 adım eğitimden sonra Mistral-7B kavram kütüphanesi 47 etkin kavramda kararlılaşır. Bunların 12'si belirli yapısal örüntülerde (uzamsal simetri, renk denkliği, sayısal büyüklük, mantıksal gerektirme) seçici etkinleşen ilkel kavramlardır; 23'ü birleştirmeyle oluşmuş ve terkibî işlemleri (yansıt-ve-yeniden-boya, ikame-et-ve-sadeleştir, kısıt-yayılımı) yakalayan ara kavramlardır; 12'si birçok ölçüt alanında etkinleşen yüksek seviyeli tecritlerdir. Ortalama kavram yeniden-kullanım oranı (bir kavramın, kapı olasılığının 50. yüzdeliğinin üstünde etkinleştiği ayrı görev türü sayısı) ilkel kavramlarda 4,3, birleştirilmiş kavramlarda 8,7'dir; bu, birleştirmenin daha genel tecritler ürettiğini doğrular.

Kavram hiyerarşisi üç terkip seviyesi gösterir. Taban seviyede ilkel kavramlar tek yapısal işlemleri yakalar. Ara seviyede birlikte etkinleşen ilkel çiftleri bütünleşik stratejilere birleşir. Gözlenen en yüksek seviyede, farklı alanlarda benzer işlevsel rol üstlenen ara kavramlar alan-genel muhakeme araçlarında birleşir. Bu hiyerarşik yapı, belirli sayıda hiyerarşi seviyesine mimarî bir eğilim olmaksızın, tümüyle MDL ve sinerji ölçütlerinin yönettiği veriye dayalı evrimden doğar.

### 8.4 Hesaplama Verimliliği

Tablo 3, RCE'nin hesaplama maliyetini MATH ölçütünde problem başına kayan nokta işlemiyle ölçülmüş belirteç düzeyi muhakeme yöntemleriyle karşılaştırır.

**Tablo 3.** MATH ölçütünde hesaplama maliyeti karşılaştırması (problem başına FLOP, temel modelin tek ileri geçişine göre). Doğruluk ayrı sütunda.

| Yöntem | Göreli FLOP | Doğruluk (%) |
| :-- | --: | --: |
| Temel (açgözlü) | 1.0× | 28.6 |
| CoT | 3.2× | 34.2 |
| SC ($n$=16) | 16.0× | 37.1 |
| ToT | 24.5× | 36.8 |
| RCE | 1.04× | 47.4 |

RCE, temel modelin hesaplama maliyetinin 1,04 katında en yüksek doğruluğa ulaşır; %4'lük yük kapı MLP'sinden ve belirteç başına iki rank-16 izdüşümünden gelir. Öz-tutarlılık ve düşünce ağacı, daha düşük doğruluk için temel hesabın 16–25 katını gerektirir. Verimlilik üstünlüğü mekanizmadaki temel farktan doğar: belirteç düzeyi yöntemler, her biri tam model ileri geçişi gerektiren daha çok belirteç üreterek hesabı artırırken RCE, tek bir dikkat katmanına kıyasla ihmal edilebilir düşük ranklı matris işlemleriyle temsil kalitesini artırır.

## 9. Ablasyon Çalışmaları

RCE'nin her büyük bileşenini ayrı ayrı çıkarıp katkısını yalıtırız. Bütün ablasyonlar, karma muhakeme müfredatında 10 000 adım eğitilmiş Mistral-7B'yi kullanır; ARC-AGI-2 ve MATH üzerinde değerlendirilir.

**Tablo 4.** ARC-AGI-2 ve MATH doğruluğunda ablasyon (%).

| Yapılandırma | ARC-AGI-2 | MATH |
| :-- | --: | --: |
| Tam RCE | 28.0 | 47.4 |
| MDL ölçütü çıkarılırsa | 14.6 | 31.2 |
| Değişmezlik artırması çıkarılırsa | 18.3 | 39.8 |
| KL kısıtı çıkarılırsa | 21.5 | 35.6 |
| Birleştirme mekanizması çıkarılırsa | 23.1 | 42.7 |
| Diklik cezası çıkarılırsa | 20.4 | 38.1 |
| Kapı entropisi cezası çıkarılırsa | 25.2 | 44.3 |

MDL ölçütünün çıkarılması en büyük bozulmayı üretir (ARC-AGI-2'de %13,4, MATH'ta %16,2); bu, sınırsız kavram büyümesinin aşırı uyan, genellenemeyen alt uzaylardan oluşan bir kütüphaneye yol açtığını doğrular. MDL baskısı olmadan kütüphane, her biri birkaç eğitim girdisinde yardım eden ama toplamda çelişen temsilî yanlılıklar getirerek başarımı bozan niş kavramlarla hızla kapasiteye dolar. Değişmezlik artırmasının çıkarılması ikinci en büyük düşüşü doğurur: kavramlar değerlendirme dağılımına aktarılamayan yüzey ipuçlarından (belirli renk değerleri, mutlak konumlar) yararlanmayı öğrenir. KL kısıtı ablasyonu, kısıtsız kavram enjeksiyonunun temel modelin akıcılığını bozduğunu, doğru muhakeme yapıları üretip bunları yine de tutarsız belirteç dizilerine kodladığını gösterir. Birleştirme mekanizmasının çıkarılması başarımı orta düzeyde azaltır; ilkel kavramlar önemli değer sağlasa da birleştirmeyle oluşan terkibî hiyerarşi çok adımlı tecrit isteyen görevlerde gereklidir. Diklik ve kapı entropisi cezaları daha küçük ama yine anlamlı etkiler yapar: diklik çıkarılınca kütüphane kapasitesini boşa harcayan gereksiz kavramlar doğar; kapı entropisi çıkarılınca dağınık yönlendirme kavram katkılarını sulandırır.

## 10. Başarısızlık Çözümlemesi

RCE, mevcut yeteneklerinin sınırlarını çizen üç sistematik başarısızlık kipi gösterir. Birincisi, 15 veya daha çok tümdengelim adımı zincirleri isteyen sayılar kuramı problemleri gibi son derece uzun biçimsel ispatlar gerektiren görevlerde ortaya çıkar. Kavram izdüşümü belirteç düzeyi muhakemeye kıyasla gürültü birikimini azaltsa da tek-katman enjeksiyon noktası temsilî yeniden yapılandırmanın derinliğini sınırlar: 18. katmanda güçlendirilen bilgi yalnızca 14 sonraki katmanca işlenir; bu da zenginleştirilmiş temsilden çıkarılabilecek çıkarımların karmaşıklığını sınırlar. Farklı kavramların farklı katmanlarda etkinleştiği çok-katmanlı enjeksiyon bu sınırlamayı gidermeye yönelik doğal bir uzantıdır.

İkinci kip, çok sayıda bağımsız nesnenin durumunu birçok zaman adımı boyunca izlemek gibi açık harici bellek isteyen görevleri içerir. Kavram kütüphanesi yapısal araçlar (nesne-kimliği kavramları, durum-izleme kavramları) sağlar fakat depolama sağlamaz: kavramlar artık akıştaki yönleri güçlendirir ama temel modelin dikkat mekanizmasının desteklediğinin ötesinde bilgiyi dizi konumları arasında kalıcılaştıramaz. Bellek artırımlı transformatörler [wu2022memorizing] gibi harici bellek mimarileriyle bütünleşme bu sınırı giderebilir.

Üçüncü kip, kavramları yanlış çıkarımlar üretecek şekilde etkinleştirmek için kasten tasarlanmış girdiler olan hasmane sembolik tuzaklarda görülür. Kavramlar gizli uzaydaki yönleri güçlendirdiğinden, bir kavramın tabanıyla hizalanan ama farklı yapısal yorum gerektiren hasmane kurulmuş bir girdi, kavramın güvenle yanlış uygulanmasını tetikleyebilir. Dayanıklılık deneyleri (Bölüm 8.2) bu başarısızlık kipinin doğal dağılım kaymalarında nadir olduğunu gösterir; ancak kavram kütüphanesinin hasmane eğitimiyle incelenmeyi hak eden kuramsal bir zafiyettir.

## 11. Tartışma

### 11.1 Temsil Evrimi Neden Önemlidir

Yörünge eniyilemesi ile temsil oluşumu arasındaki ayrım, RCE'nin önceki çalışmalardan ayrıldığı merkezî eksendir. RLVR yöntemleri [ye2025enigmata, shao2024deepseekmath], doğru belirteç dizileri üretme olasılığını artırır ama bu dizilerin planlandığı temsilî zemini değiştiremez. Modüler muhakeme çerçeveleri [wang2025muslr], belirli muhakeme örüntülerini ele alan sabit yapısal bileşenler getirir ama yeni örüntüler doğduğunda büyüyemez veya uyum sağlayamaz. Talimat izleme muhakemesi yöntemleri [qu2025raif], mevcut temsil uzayının daha özenli dolaşılmasını özendirir ama uzayı genişletmez.

RCE, düşüncenin geometrisinin kendisini değiştirir. Modelin gizli uzayında düşük ranklı alt uzayları dinamik olarak ekleyerek, birleştirerek ve billurlaştırarak RCE modele, insan bilişsel esnekliğinin altındaki işlem için bir mekanizma verir: mevcut araçlar yetersiz kaldığında yeni kavramsal araçlar icat edebilme kabiliyeti. Kavram kütüphanesi durağan bir bilgi deposu değil, her biri basit, genel ve terkip edilebilir olması için evrimsel baskıyla biçimlenmiş büyüyen bir temsilî âletler repertuvarıdır. Her tecritin bir sonrakinin yapı taşı olduğu bu birikimli özellik, RCE'yi sabit bir temsilî bütçe içinde muhakemeyi iyileştiren yaklaşımlardan ayıran şeydir.

### 11.2 Sınırlamalar

Mevcut çerçevenin birkaç sınırlaması tartışmayı gerektirir. Birleştirme dinamiği, sinerji için bütün çiftlerin değerlendirilmesi gerektiğinden etkin kavram sayısında hesap bakımından ikinci derecedendir. Mevcut kütüphane boyutu (47–128 kavram) bunu yönetilebilir kılsa da binlerce kavramlık kütüphanelere ölçeklemek, belki geçmiş sinerji verisinde eğitilmiş öğrenilmiş birleştirme öngörücüleriyle yaklaşık birleştirme adayı seçimi gerektirir.

Kavram tanımlanabilirliği açık bir soru olarak kalır: farklı rastgele tohumlarla farklı eğitim koşuları, benzer toplam başarım veren farklı kavram ayrışımlı kütüphaneler üretebilir. Diklik ve MDL kısıtları bu tanımlanamazlığı büyük ölçüde azaltsa da tümüyle gidermez. Belirli bir görev dağılımı için kanonik bir kavram ayrışımının var olup olmadığını ve RCE'nin ona yakınsayıp yakınsamadığını anlamak, gelecekteki kuramsal çalışma için önemli bir yöndür.

70B veya daha çok parametreli modellere ölçekleme, mevcut gerçeklemenin ele almadığı bellek ve hesap hususları getirir. Kavram üretici, kapı ağı ve enjeksiyon mekanizması gizli boyutla doğrusal ölçeklenir; fakat doğurma değerlendirmesi ve birleştirme sinerji denetimi için gereken ileri geçişler tam modelle ölçeklenir ve çevrim-içi evrimi çok büyük ölçeklerde pahalı kılabilir. Adayları küçük bir vekil model üzerinde değerlendirmek veya önbelleğe alınmış gizli durumlar kullanmak gibi verimli yaklaşıklamalar bu maliyeti azaltabilir.

## 12. Sonuç

Durağan örtük uzaylar, büyük dil modellerinin terkibî muhakeme yeteneklerine temel bir tavan koyar. Ön-eğitimde sabitlenmiş temsil tabanı bir görevin örtük yapısını kodlamak için gereken yönlerden yoksunsa, ne kadar ek belirteç üretimi veya yörünge eniyilemesi bunu telafi edebilir. Donmuş dil modellerine yeni kavram alt uzaylarını dinamik olarak yaratma, değerlendirme, terkip etme ve billurlaştırma yeteneği vererek bu tavanı kaldıran Özyinelemeli Kavram Evrimi'ni tanıttık. Çerçeve dört mekanizmayla işler: aday alt uzayların başarısızlıkla tetiklenen doğurulması, Occam baskısı uygulayan MDL tabanlı seçim, terkibî hiyerarşiler kuran sinerji güdümlü birleştirme ve kavram kütüphanesini eğitim oturumları boyunca birikimli kılan kontrol noktası tabanlı billurlaşma.

Mistral-7B üzerindeki deneyler boru hattının tamamını doğrular ve RCE'nin beş terkibî muhakeme ölçütünde %5'ten az hesaplama yüküyle yörünge düzeyi taban çizgilerine göre tutarlı iyileşmeler sağladığını gösterir. Kavram kütüphanesi güvenilir terkibî muhakeme için gereken özellikleri sergiler: seçici doğurma, doğrusal-altı büyüme, görevler-arası yeniden kullanım, hiyerarşik terkip ve dağılım kaymasında dayanıklılık. Bu sonuçlar, temsil evrimini, büyük dil modellerinde muhakeme iyileştirmesine bugün egemen yörünge eniyilemesi yöntemlerinin uygulanabilir ve tamamlayıcı bir alternatifi olarak yerleştirir ve muhakeme kapasitesi ön-eğitimde edinilen temsillerle sınırlı kalmayıp tecrübeyle birikimli olarak büyüyen sistemlere yol açar.

## Ek A. Algoritma Sözde Kodu

Algoritma 1, doğurma, yarış, birleştirme ve budama adımları dahil RCE eğitim çevriminin tam tarifini verir.

**Algoritma 1: Özyinelemeli Kavram Evrimi Eğitimi**

Girdi: Donmuş temel model $f_\theta$, enjeksiyon katmanı $\ell^*$, kavram üretici $G$, kapı ağı $\mathcal{G}$.
Girdi: Hiperparametreler: doğurma eşiği $\tau$, MDL ağırlığı $\lambda$, birleştirme aralığı $T_m$, sinerji eşiği $\lambda_m$.

1. Kavram kütüphanesini boş başlat: $\mathcal{C} \leftarrow \emptyset$
2. Her eğitim yığını $(x, y)$ için:
3. Artırılmış ileri geçişi hesapla: $\ell^*$ katmanında $h' = h + \sum_{i \in A(x)} g_i(x) B_i B_i^\top h$
4. Kaybı hesapla: $\mathcal{L} = \mathcal{L}_{\text{LM}} + \lambda_{\text{orth}} \mathcal{R}_{\text{orth}} + \lambda_{\text{ov}} \mathcal{R}_{\text{ov}} + \lambda_{\text{gate}} \mathcal{H}(g)$
5. RCE parametrelerini geri yayılımla güncelle (temel model donuk)
6. Çıktı logitlerinden başarısızlık puanını hesapla $F(x)$ (Denklem 2)
7. Eğer $F(x) > \tau$ ve $|\mathcal{C}| < N_{\max}$ ise:
8.   $\ell^*$ katmanında havuzlanmış gizli durumu $h_{\text{pool}}$ çıkar
9.   $k_s$ aday üret: $\{B^{(j)}\}_{j=1}^{k_s} \leftarrow G(h_{\text{pool}}) + \sigma\epsilon_j$, her birini dikleştir
10.  Her adayı $h$ üzerindeki yeniden-kurma hatasıyla değerlendir
11.  En iyi adayı seç $B^* = \arg\min_j \|h - B^{(j)} {B^{(j)}}^\top h\|^2$
12.  Eğer $\Delta L - \lambda\, \Omega(B^*) > 0$ ise:
13.    $C_{\text{new}} = (B^*, g_{\text{new}})$'i $\mathcal{C}$'ye ekle
14.    $|\mathcal{C}| > N_{\text{keep}}$ ise $\mathcal{C}$'yi kullanım EMA'sıyla buda
15. Eğer adım mod $T_m = 0$ ve $|\mathcal{C}| \geq 2$ ise:
16.   $\mathcal{C}$'deki her $(i, j)$ çifti için:
17.     Sinerji $\text{Syn}(i,j)$'yi Denklem 5 ile hesapla
18.     Eğer $\text{Syn}(i,j) < -\lambda_m (\Omega(C_{ij}) - \Omega(C_i) - \Omega(C_j))$ ise:
19.       Birleştir: $B_{ij} \leftarrow \text{SVD-kırp}([B_i \mid B_j], r)$
20.       $C_{ij}$'yi $\mathcal{C}$'ye ekle
21. $\mathcal{C}$, $G$, $\mathcal{G}$'yi kontrol noktasına kaydet (billurlaşma)

## Ek B. Hiperparametre Duyarlılığı

Tablo 5, ARC-AGI-2'de RCE başarımının başlıca hiperparametrelere duyarlılığını bildirir. Her satır bir hiperparametreyi değiştirirken diğerlerini öntanımlı değerlerinde tutar.

**Tablo 5.** Mistral-7B için ARC-AGI-2 doğruluğunda (%) hiperparametre duyarlılığı. (Değer: doğruluk; kalın = öntanımlı.)

| Hiperparametre | Değer 1 | Değer 2 | Değer 3 | Değer 4 | Öntanımlı |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Rank $r$ | 4: 22.1 | 8: 25.3 | **16: 28.0** | 32: 27.4 | 16 |
| Top-$k$ | 1: 24.6 | **2: 28.0** | 4: 27.2 | 8: 25.8 | 2 |
| Doğurma $\tau$ | 2.0: 21.8 | 3.0: 25.4 | **5.0: 28.0** | 10.0: 26.1 | 5.0 |
| MDL $\lambda$ | 0.1: 22.3 | 0.3: 26.9 | **0.5: 28.0** | 1.0: 25.7 | 0.5 |
| $\lambda_{\text{orth}}$ | 0.01: 24.1 | **0.05: 28.0** | 0.1: 27.3 | 0.5: 23.6 | 0.05 |

Başarım en çok doğurma eşiği $\tau$'ya ve MDL ağırlığı $\lambda$'ya duyarlıdır; ikisi de kavram kabulünün seçiciliğini denetler. Çok düşük eşikler ($\tau = 2.0$) kavram patlaması ve bozulmuş genelleme üretir. Çok yüksek eşikler ($\tau = 10.0$) yararlı kavram oluşumunu bastırır. $r$ ranki 16'da hafif bir eniyi gösterir; düşük rankler karmaşık yapısal ilkeller için kapasiteden yoksundur, yüksek rankler orantılı yarar olmadan MDL maliyetini artırır. Top-$k$ parametresi $k = 2$'den sonra azalan getiri gösterir; bu, çoğu görevin en çok iki tamamlayıcı yapısal kavram gerektirdiği gözlemiyle uyumludur.

## Ek C. Kavram Görselleştirmesi

Öğrenilmiş kavramların yapısını göstermek için Mistral-7B kütüphanesinde en sık etkinleşen ilk 5 kavramı, ölçüt görevleri boyunca etkinleşme örüntülerini hesaplayarak çözümleriz. Her kavram için top-$k$'da etkinleştiği görev kümesini kaydeder ve işlevsel rolleri belirlemek için bu görev kümelerini kümeleriz.

Kavram 3, ağırlıklı olarak ARC-AGI-2'deki uzamsal simetri tespiti ve MATH'taki geometrik muhakeme problemlerinde etkinleşir; gizli uzayda ayna-yapısı yönlerini güçlendiren öğrenilmiş bir tabanla uyumludur. Kavram 11, MATH'taki cebirsel işlem görevlerinde ve BBH'deki kısıt-izleme problemlerinde etkinleşir; değişken-bağlama ve ikame yapısıyla hizalı öğrenilmiş bir tabana işaret eder. Kavram 3 ve 8'den oluşan birleştirilmiş kavram 27, dönüşüm altında değişmez belirleme isteyen görevlerde ARC-AGI-2, MATH ve GPQA'da geniş biçimde etkinleşir ve alan-genel bir değişmez-tespit aracı olarak işler. Bu etkinleşme örüntüleri, kavram kütüphanesinin birleştirme mekanizmasıyla giderek daha genel muhakeme araçlarına terkip eden işlevsel olarak uzmanlaşmış ilkeller geliştirdiğini doğrular.

## Ek D. Gerçekleme Ayrıntıları

Tam RCE gerçeklemesi yaklaşık 1 000 satır Python kodundan ibarettir ve altı modülde düzenlenmiştir: kavram alt uzayı tanımı (taban matrisleri, izdüşüm işleçleri), kavram kütüphanesi yönetimi (ekleme, kaldırma, serileştirme), kapı ağı (seyrek top-$k$ yönlendirme MLP'si), enjeksiyon mekanizması (belirlenmiş kod çözücü katmanında ileri kancası), evrim mantığı (doğurma, MDL değerlendirme, birleştirme, budama) ve eğitim çevrimi (kayıp hesabı, düzenlileştirme, kontrol noktası alma). Gerçekleme PyTorch 2.6 ile temel model yüklemesi için Hugging Face Transformers 4.48 kullanır ve modelden bağımsız olacak biçimde tasarlanmıştır: Hugging Face API'si ile erişilebilen herhangi bir yalnız-kod-çözücü transformatör, yapılandırma dosyasında model tanıtıcısı ve enjeksiyon katmanı indeksi verilerek temel model olarak kullanılabilir.

bfloat16 kesinliğinde tek NVIDIA RTX 5090 (24 GB VRAM) üzerinde Mistral-7B eğitimi, 512 dizi uzunluğu ve 1 yığın boyutuyla saatte yaklaşık 1 200 eğitim adımı işler. Kavram kütüphanesi, kapı ağı ve üretici birlikte yaklaşık 50 MB GPU belleği tutar; temel modelin 14 GB'lık ayak izine kıyasla ihmal edilebilir. Tam kavram kütüphanesini, kapı ağırlıklarını, üretici ağırlıklarını ve eğitim üst verisini içeren kontrol noktaları ortalama 55 MB'lık tek bir PyTorch dosyasına serileştirilir.

---

Kaynakça: orijinal `references.bib` dosyası `orijinal/` dizinindedir; çevrilmemiştir.
