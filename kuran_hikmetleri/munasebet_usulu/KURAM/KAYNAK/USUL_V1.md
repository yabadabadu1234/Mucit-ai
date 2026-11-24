# Kur'ân-ı Kerîm İçin Üstten Bakış Lisanı: Biçimsel Mantık, İleri Matematik ve Kayıpsız Denklem Usûlü

Bu belge, Kur'ân-ı Kerîm'in metnini mevzu özetlerine indirmek yerine **kayıpsız, geri-açılabilir, tümevarımsal bir biçimsel mantık ve denklem sistemine** dönüştüren lisanın eksiksiz şartnamesidir. Lisan iki katmandan ve bir ifade kabiliyetleri cetvelinden kurulur: **Katman I (Mantık Çekirdeği)** önermesel, yüklem, deontik, modal ve zamansal mantıkla metni kayıpsız yazar; **Katman II (İleri Matematiksel Modelleme)** yalnızca Katman I'in ifade edemediği dinamik, boyut, eşik ve dönüşümler metinde mevcutsa çağrılır; **Bölüm 15'teki yüz ifade kabiliyeti** lisanın söyleyebildiklerini genişletir. Amaç, tek bir âyetin tek bir işlevsel unsurunu dahi dışarıda bırakmadan atomik denklemler kurmak ve bunları cebirsel/mantıksal faktörleme kurallarıyla üst denklemlere yükseltmektir; üstten bakan, istediği basamakta durur ve istediği âyete iner.

---

## 1. Temel Aksiyomlar

1. **Kayıpsızlık (Geri-Açılabilirlik) Aksiyomu:** Hiçbir üst denklem, alt denklemlerdeki bilgiyi özetleyerek silemez. Her üst denklem $F$, altındaki $E_1, \dots, E_n$ denklemlerinin **geri-açılabilir (invertible)** bir katlamasıdır:
   $$\text{Açılım}(F) \equiv \bigoplus_{i=1}^{n} E_i$$
   Bir alt âyette geçen hüküm, şart, istisna, sıfat veya illet üst denklem açıldığında geri elde edilemiyorsa o faktörleme geçersizdir.
2. **Aşağıdan Yukarı (Tümevarımsal) İnşa Aksiyomu:** Önce her âyet tekil olarak atomik denklem ($L_0$) biçiminde yazılır. Üst formüller ($L_1 \to L_4$) önceden belirlenmiş konu başlıklarından değil, yalnızca biriken $L_0$ denklemleri arasındaki **ortak terim, çıkarım, şart–sonuç ve simetri** örüntülerinden çıkarılır.
3. **Açık Metin ile Örtük Delâlet Ayrımı Aksiyomu:** Metinde lafzen geçen unsurlar normal biçimde yazılır; Arapça sözdizimi ve belâgat gereği metinde düşürülmüş (*hazf*) veya zorunlu olarak ima edilmiş (*delâletü'l-iktizâ / delâletü'l-işâre*) unsurlar köşeli açı parantezi `⟨...⟩` içinde gösterilir. Böylece metnin kendisiyle yorum/çıkarım asla birbirine karışmaz.
4. **Sıfır Zamir Aksiyomu:** Atomik denklemlerde hiçbir zamir (*o, onlar, bu, şu*) çıplak bırakılmaz; her zamir kendi merciine açık biçimde bağlanır: `x[Merci]`.
5. **Kanonik Ayrıklık Aksiyomu:** İki farklı Kur'ânî kavram (*hamd* vs. *şükür*, *kâfir* vs. *müşrik* vs. *münafık*, *nebî* vs. *resûl*, *kalp* vs. *fuâd*) asla tek bir gevşek değişken altında eritilmez; her biri ayrı kanonik sembol taşır ve aralarındaki ilişki tanım aksiyomuyla (`:=` veya `⊂`) kurulur.
6. **Kaide–Misal Ayrımı Aksiyomu:** Hiçbir tekil vaka, özel kavram adı veya tikel içerik, genel usûl kuralının içine sabitlenmez. Usûl yalnızca **soyut yapısal sınıflar** (*değişken rolü, değişim tipi, bağıntı derecesi, etkileşim topolojisi*) üzerinden konuşur; tikel kavramlar ancak uygulama safhasında bu yapılara parametre olarak yerleşir.
7. **En Sade Yeterli Yapı (Occam) Aksiyomu:** Bir âyet veya âyet grubu Katman I'in (önermesel, yüklem, deontik, modal, zamansal mantık) araçlarıyla kayıpsız temsil edilebiliyorsa Katman II çağrılmaz. İleri bir matematiksel yapı **yalnızca** alt katmanın ifade edemediği bir dinamik, boyut, eşik veya dönüşüm metinde mevcutsa devreye alınır.
8. **Nitel–Yapısal Matematik Aksiyomu:** Türevlerin işareti, büyüme rejimi, çekirdek–görüntü ilişkisi, kafes sıralaması ve topolojik kapsama **kesin yapısal bilgilerdir**. Metnin bizzat vermediği yapay reel sayısal katsayılar, keyfî ağırlıklar veya dışsal istatistikler sisteme asla sokulmaz.


---

## 2. Matematik ve Mantıktan Alınan 8 Disiplin ve Görev Dağılımı

Kur'ân metni yalnızca önermesel doğru–yanlış yargılarından oluşmaz; içinde varlık ilişkileri, emir–yasak normları, değişmez yasalar, zaman katmanları, temsiller ve âyetler arası bağlar vardır. Bu nedenle tek bir mantık sistemi yetersiz kalır; matematiğin sekiz belirli alt disiplini görev sınırları çizilerek usûle alınır (Katman II'nin on dört yapısal senaryosu Bölüm 8'dedir):

| # | Alınan Disiplin | Kur'ân Metnindeki Karşılığı | Usûldeki Görevi |
| :--- | :--- | :--- | :--- |
| **1** | **Çok Tipli Yüklem Mantığı (*Many-Sorted FOL/HOL*)** | Zât, sıfat, fiil, fail, mef'ûl, tümel–tikel hükümler | Varlıkları tiplerine göre ayırmak (`İlah`, `Mükellef`, `Âlem`, `Amel`), ilişkileri yüklem/fonksiyon olarak kurmak, niceleyicileri (`∀, ∃, ∃!`) yönetmek. |
| **2** | **Deontik (Normatif) Mantık** | Emir, nehiy, haram, helal, ruhsat, keffaret, şartlı mükellefiyet | Teklifî ve vaz'î hükümleri (`O, F, P, O⁺, F⁻`), şartlı yükümlülükleri (`O(φ \| ψ)`) ve mazeret/ruhsat istisnalarını (`⊘`) çelişkisiz biçimde formülleştirmek. |
| **3** | **Modal ve Epistemik Mantık** | Sünnetullah, imkân/imkânsızlık, ilim, zan, gayb, şehadet, irade | Zorunlu yasaları (`□`), mümkün hâlleri (`◇`), özneye bağlı bilgi/zan farkını (`K_x` vs. `B_x`) ve ilâhî meşîeti (`W_Allah`) ayırmak. |
| **4** | **Zamansal Mantık (*Temporal Logic*)** | Ezelî misak, tarihî kıssalar, dünya imtihanı, kıyamet, ebedî ahiret | Olayları zaman kiplerine (`τ₋, τ₀, τ₊, τ_∞`) yerleştirmek; ardıllık (`▷`) ile tarih boyunca tekrarlanan değişmez döngüleri (`⟳`) ayırmak. |
| **5** | **Küme, Mereoloji ve Kafes Kuramı (*Order/Lattice*)** | İstisna (*illâ*), tahsîs, derece–mertebe farkları, parça–bütün | Grupları (`∈, ⊂`), istisnayı (`∖`), parça–bütün ilişkilerini (`⊑`) ve üstünlük/derece sıralamalarını (`≺, ⪯`) ölçüsüz tahmine düşmeden modellemek. |
| **6** | **Kategori Teorisi (*Functors & Morphisms*)** | Mesel, temsil, teşbih, kıssa–hüküm paralelliği | İki farklı alan arasındaki **yapı koruyan dönüşümü** (`≅`, `≃`) göstermek; benzetmenin yalnızca süs değil, ilişki aktaran bir fonktör olduğunu kaydetmek. |
| **7** | **Cebirsel Faktörleme ve Terim Yeniden Yazımı** | Ardışık âyetlerin ortak ilkeye toplanması, üst denklem kurma | Ortak terim parantezine alma, zincir birleştirme, tanım katlama ve kanonik sadeleştirme kurallarıyla $L_0 \to L_4$ yükselişini yönetmek. |
| **8** | **Yönlü Hiperçizge Kuramı (*Directed Hypergraphs*)** | Âyetler ve sûreler arası illet, delil, mukabele ve çapraz atıf ağı | Tek bir âyetin birden fazla âyetle kurduğu çoklu bağları (*hiperkenar*) temsil etmek ve çizge daraltma (*quotient graph*) ile sûrenin omurgasını çıkarmak. |

**Usûl Dışı Bırakılanlar:** Metinde bulunmayan yapay sayısal ağırlıklar, öznel olasılık skorları veya dışsal istatistiksel katsayılar usûle alınmaz. Sistem **nitel-cebirsel** ve **mantıksal-ilişkisel**dir; nicel sayı yalnızca metnin bizzat zikrettiği yerlerde (*yedi gök, dört şahit, iki pay, üç gün*) sabit değer olarak girilir.

---

## 3. Tam İşaret Alfabesi ve Operatör Öncelik Hiyerarşisi

### 3.1 Ontoloji, Nitelik ve Mahsusluk (Hasr/Kasr) İşaretleri

| İşaret | Adı | Biçimsel Anlamı | Dil / Belâgat Karşılığı |
| :--- | :--- | :--- | :--- |
| `↦!` | **Mutlak Mahsusluk (Hasr)** | `X ↦! Y` := $X$ yalnızca $Y$'ye aittir; $\forall z \neq Y,\ \neg(X \mapsto z)$ | *Kasr / Hasr* (`إيّاك نعبد`, `إنّما`, `لِلّٰهِ` tahsisi) |
| `↦` | **Yönelim / Aidiyet** | `X ↦ Y` := $X$, $Y$'ye yönelir veya aittir (münhasırlık iddiası olmadan) | Müteaddî yönelim, izafet, *lâm-ı temlîk/istihkak* |
| `X{...}` | **Nitelik / Sıfat Demeti** | $X$ varlığı, küme içi sıfat/ilişkilerle nitelenmiştir | Sıfat terkibi, esmâ dizimi (`Allah{Rabb → Âlemler}`) |
| `::` | **Tip Bildirimi** | `x :: T` := $x$, $T$ ontolojik tipindendir | Varlık sınıfı ayrımı (`Mûsâ :: Resûl`) |
| `:=` | **Mahiyet Tanımı** | Sol taraf sağdaki bileşenlerle tanımlanır (katlama/açılım) | *Hadd / Tarif* (özsel tanım) |
| `≡` | **Mantıksal Özdeşlik** | İki denklem veya kavram her bağlamda eşdeğerdir | *Tekâfü' / Ayniyet* |
| `≇` | **Mutlak Tenzih / Benzemezlik** | `X ≇ Y` := $X$, $Y$ ile hiçbir ortak benzerlik taşımaz | *Tenzih* (`ليس كمثله شيء`) |

### 3.2 Önermesel ve Niceleyici İşaretler

| İşaret | Adı | Biçimsel Anlamı | Kullanım Kuralı |
| :--- | :--- | :--- | :--- |
| `∧` | **Birlikte (Ve)** | İki unsurun aynı anda geçerli olması | Atıf (`و`), hal cümlesi, eşzamanlı şartlar |
| `∨` | **Kapsayıcı Veya** | En az birinin geçerli olması | Seçenekli hükümler (`أو`) |
| `⊕` | **Dışlayıcı Ya–Ya da** | İkisinin aynı anda olamaması | Kesin iki kutuplu ayrım (`إمّا ... وإمّا`) |
| `¬` | **Değilleme** | Önermenin veya niteliğin olumsuzlanması | *Nefy* (`لا، ما، ليس، لن، لم`) |
| `→` | **Koşullu Gerektirme** | `φ → ψ` (gerçek/genel şart) | `إن / إذا / من` şart–cezâ yapıları |
| `⇒` | **Mantıksal Çıkarım / Tefrî'** | Önceki önermeden zorunlu olarak doğan hüküm veya sonuç | `فَـ` (fâ-i tefrîiyye), akıl yürütme adımı |
| `↔` | **Gerek ve Yeter Şart** | İki yönlü eşdeğer şart | Çift yönlü bağlılık |
| `⊬` | **Karşı-Olgusal Şart** | `φ ⊬ ψ` := Eğer $\varphi$ olsaydı $\psi$ olurdu (ama $\varphi$ gerçekleşmedi) | `لو` (harf-i imtinâ' li-imtinâ') |
| `∀, ∃, ∃!, ∄` | **Niceleyiciler** | Tümü / En az biri / Yalnızca tek biri / Hiçbiri | Umum (`كلّ`), husus, tevhid (`إلٰه واحد`), cins nefyi (`لا ريب`) |

### 3.3 Nedensellik, Delil ve Gaye İşaretleri

| İşaret | Adı | Biçimsel Anlamı | Dil / Belâgat Karşılığı |
| :--- | :--- | :--- | :--- |
| `⊢` | **Delil / Burhan** | `D ⊢ H` := $D$, $H$ hükmünün veya iddiasının kanıtıdır | Kâinat âyeti, tarihî ibret, aklî burhan |
| `∵` | **İllet / Gerekçe** | `H ∵ C` := $H$'nin sebebi/illeti $C$'dir | *Ta'lîl* (`إنّ` ta'lîliyye, `بما كانوا`, `لأنّ`) |
| `⇝` | **Gaye / Hikmet** | `E ⇝ G` := $E$ eylemi $G$ maksadıyla gerçekleştirilir | *Lâm-ı ta'lîl* (`لـِ، كي، لعلّ`) |
| `⊥` | **Çelişki / Bâtıl / Hüsran** | Mantıksal çöküş, geçersizlik veya mutlak kayıp | *Bâtıl, dalâl, hüsran* |
| `⊤` | **Hak / Sabit Gerçek** | Mutlak doğruluk, sarsılmaz hakikat | *Hak, sıdk, yakîn* |

### 3.4 Deontik (Hüküm ve Mükellefiyet) İşaretleri

| İşaret | Adı | Biçimsel Anlamı | Fıkhî / Usûlî Karşılık |
| :--- | :--- | :--- | :--- |
| `O(φ)` | **Zorunlu Emir** | $\varphi$'nin yerine getirilmesi yükümlüdür | Farz / Vâcip (kesin emir) |
| `F(φ)` | **Kesin Yasak** | $\varphi$'nin terk edilmesi zorunludur (`O(¬φ)`) | Haram (kesin nehiy) |
| `P(φ)` | **İzin / Serbestlik** | $\varphi$'nin yapılması da terk edilmesi de serbesttir | Mübah / Helal |
| `O⁺(φ)` | **Teşvik / Üstün Tercih** | Yapılması övülen, terki günah olmayan fiil | Mendup / Müstehap / İhsan |
| `F⁻(φ)` | **Sakındırma** | Terki övülen, hoş görülmeyen fiil | Mekruh / Kerahet |
| `O(φ \| ψ)` | **Şartlı Yükümlülük** | $\psi$ şartı oluştuğunda $\varphi$ zorunludur | Sebebe/şarta bağlı hüküm (*vücûb-ı mukayyed*) |
| `⊘(φ \| γ)` | **Ruhsat / İstisna** | $\gamma$ mazereti (zaruret, hastalık, yolculuk, ikrah) altında $\varphi$ yükümlülüğü kalkar veya hafifler | *Ruhsat, ref'-i harac, teklîf-i mâ lâ yutâkın nefyi* |
| `⤏` | **Hüküm Güncelleme / Tahsis** | `H₁ ⤏[tür] H₂` ($H_2$, $H_1$'i takyîd, tahsîs veya nesh eder) | *Takyîd, tahsîs, nesh, beyân* |

### 3.5 Modal, Epistemik ve İrade İşaretleri

| İşaret | Adı | Biçimsel Anlamı | Kur'ânî Karşılık |
| :--- | :--- | :--- | :--- |
| `□(φ)` | **Zorunluluk / Sünnetullah** | Her zaman ve koşulda değişmez ilâhî yasa | *Sünnetullah* (`لن تجد لسنّة الله تبديلاً`) |
| `◇(φ)` | **İmkân** | Gerçekleşmesi aklen/ontolojik olarak mümkün olan | *Cevâz-ı aklî / imkân* |
| `K_x(φ)` | **Kesin Bilgi** | $x$ öznesi $\varphi$'yi yakînen bilir | *İlim, yakîn* (`يعلمون`, `عليم`) |
| `B_x(φ)` | **Zan / İddia** | $x$ öznesi $\varphi$'yi sanır veya iddia eder (doğruluğu garanti değil) | *Zan, zann-ı bâtıl, iddia* (`يزعمون`, `يظنّون`) |
| `W_x(φ)` | **İrade / Meşîet** | $x$ öznesi $\varphi$'yi diler | *Meşîet* (`إن يشاء الله`) veya kulun tercihi |
| `G(φ)` | **Gayb Alanı** | Beşerî duyularla doğrudan erişilemeyen hakikat | *Gayb* |
| `Req(x ↦ y, φ)` | **Yakarış / Talep** | $x$'in $y$'den $\varphi$'yi istemesi | *Dua, istiğfar, istiane* |

### 3.6 Zamansal, Küme ve Belâgat İşaretleri

| İşaret | Adı | Biçimsel Anlamı | Kur'ânî Karşılık |
| :--- | :--- | :--- | :--- |
| `τ₋ / τ₀ / τ₊ / τ_∞` | **Zaman Katmanları** | Ezel–Mâzî / Dünya Hâli / Kıyamet–Hesap / Ebedî Âhiret | Kıssa, dünya imtihanı, haşir, cennet–cehennem |
| `▷` | **Kronolojik Ardıllık** | `e₁ ▷ e₂` := $e_1$ olayı $e_2$'den önce gelir | `ثمّ`, kıssa akışı |
| `⟳` | **Tekrarlanan Döngü** | Aynı yapının tarih boyunca yinelenmesi | Kavim kıssalarının ortak döngüsü |
| `⟐(A) ⊢ B` | **Kasem (Yemin)** | $A$ (müksemün-bih) tanık gösterilerek $B$ (cevâbü'l-kasem) pekiştirilir | `والعصر`, `والشمس`, `والتين` |
| `≅` | **Yapı Koruyan Temsil** | `Alan₁ ≅ Alan₂` (ilişki yapısını koruyan fonktör) | *Mesel / Temsîl* |
| `⋈` | **Mukabele (Zıt Simetri)** | İki zıt tablonun birebir karşılaştırılması | Mümin ⋈ Kâfir, Cennet ⋈ Cehennem |
| `∖` | **İstisna / Dışlama** | `A ∖ B` := $A$ kümesinden $B$'nin çıkarılması | *İstisnâ-i muttasıl* (`إلّا الذين آمنوا`) |
| `⊑ / ≺` | **Parça-Bütün / Derece** | `a ⊑ b` ($a$, $b$'nin parçası); `a ≺ b` ($b$, $a$'dan üstün) | Mertebe, derece, *efdal* |
| `↑! / ↑!!` | **Te'kid Derecesi** | Pekiştirme şiddeti (`إنّ`, `لَـ`, `قد`, yemin + `إنّ`) | Belâgatte *haber-i talebî* ve *haber-i inkârî* |
| `?⊥(φ) / ?⊤(φ)` | **Retorik İstifham** | `?⊥`: soru yoluyla kesin red (`≡ ¬φ`); `?⊤`: soru yoluyla kesin onay (`≡ φ`) | *İstifham-ı inkârî* ve *istifham-ı takrîrî* |

### 3.7 Operatör Öncelik Sırası (Yüksekten Düşüğe)

Parantez karmaşasını önlemek için bağlama gücü kesin sıraya bağlanır:
1. Nitelik/Tip ve Parantezleme: `X{...}`, `x[Merci]`, `x :: T`, `⟨...⟩`
2. Tekil Operatörler: `¬`, `□`, `◇`, `O`, `F`, `P`, `K_x`, `B_x`, `W_x`, `G`, `τ_*`, `↑!`
3. Küme, Derece ve Yönelim: `∈`, `⊂`, `∖`, `⊑`, `≺`, `↦`, `↦!`, `≅`, `≇`
4. Mantıksal Bağlaçlar: `∧` → `∨`, `⊕` → `→`, `⊬`, `↔`
5. Çıkarım, Gerekçe ve Yapısal Bağlar: `∵`, `⇝`, `▷` → `⊢`, `⇒`, `⋈`, `⤏`, `:=`, `≡`

---

## 4. Ne İsmiyle Değişken/Sabit Kalır, Ne Operatöre Dönüştürülür?

Her kelimeyi sembole boğmak metni okunmaz kılar; her şeyi düzyazı bırakmak ise cebiri yok eder. Bu sınırı çizen **Dört Sınıflı Dönüşüm Kuralı** uygulanır:

### Sınıf I — Ontolojik Sabitler (İsmiyle ve Büyük Harfle Kalır)
Dönüştürülmez; sistemin temel yapı taşlarıdır:
* **Mutlak Sabit:** `Allah` (zâtı temsil eder; esmâsı ise `{...}` nitelik kümesinde taşınır).
* **Temel Varlık Türleri (Tipler):** `Âlemler`, `İnsan`, `Cin`, `Melek`, `Şeytan`, `Resûl`, `Nebî`, `Kitap`, `Gökler`, `Yer`, `Nefis`, `Kalp`, `Amel`, `Dünya`, `Âhiret`.
* **Tarihî Şahıs ve Topluluk Sabitleri:** `Âdem`, `Nûh`, `İbrâhîm`, `Mûsâ`, `Îsâ`, `Firavun`, `Kârûn`, `İsrâîloğulları`, `Âd`, `Semûd`, `Kureyş`.
* **Değer ve Kavram Sabitleri:** `Hamd`, `Tevhid`, `Şirk`, `Hidayet`, `Dalâlet`, `Takvâ`, `Adalet`, `Zulüm`, `Rızık`, `Rahmet`, `Azap`, `Sabır`, `Şükür`, `İnfak`, `Mîzan`, `Ahit`.

### Sınıf II — Bağıntı, Sıfat ve Eylem Yüklemleri (İlişkisel Forma Çevrilir)
Tek başına yüzen kelimeler olarak bırakılmaz; **kimin kime / neye etki ettiği** açıkça yazılır:
* **Tekli Nitelik (Vasıf):** `Müttakî(x)`, `Sâlih(x)`, `Zâlim(x)` veya varlık içine gömülü `Allah{Rahmân, Rahîm}`.
* **İkili/Üçlü İlişki (Morfizma):** `Rabb(Allah → Âlemler)`, `Yarat(Allah → x)`, `İndir(Allah → Kitap → Resûl)`, `Mâlik(Allah → DinGünü)`.
* **Bileşik Vasıf (Katlanabilir Küme):** Bir grubun âyetlerde sayılan vasıfları küme tanımı olarak tutulur: `Müttakî(x) := {v₁(x) ∧ v₂(x) ∧ ... ∧ vₙ(x)}`.

### Sınıf III — Yapısal Edatlar, Kipler ve Sözdizimsel İşlevler (Tamamen Operatöre Çevrilir)
Hiçbir edat veya kip düz kelime olarak bırakılmaz; tamamı Bölüm 3'teki operatörlere dönüştürülür:
* Tahsis ve takdim–tehir → `↦!`
* Şart edatları (`إن، إذا، من، ما`) → `→`; imkânsız/geçmiş şart (`لو`) → `⊬`
* Gerekçe edatları (`إنّ` ta'lîliyye, `بما`) → `∵`; amaç (`لـِ، كي`) → `⇝`
* İstisna (`إلّا، غير`) → küme çıkarımı (`∖`) veya hasr (`↦!`)
* Yemin edatları (`و، ت، ب`) → `⟐(...) ⊢`
* Emir/Nehiy/Ruhsat sigaları → `O`, `F`, `P`, `O⁺`, `F⁻`, `⊘`
* Pekiştirme (`إنّ، لَـ، قد، نون التوكيد`) → `↑!` / `↑!!`
* Retorik sorular (`أليس، أفلا، هل`) → `?⊤` veya `?⊥`

### Sınıf IV — Kanonik Sözlük ve Kök Tutarlılığı Kuralı
* Bütün $L_0$ formülleri tek bir **Kanonik Kavram Sözlüğü** üzerinden yazılır; aynı Arapça kavram farklı sûrelerde farklı Türkçe adlarla anılmaz (örneğin bir yerde *hidayet*, başka yerde *doğru yol* denip bağlantı koparılmaz; tek kanonik isim seçilir).
* Yakın anlamlı ama farklı incelikli kelimeler (*hamd* vs. *şükür*; *hasene* vs. *birr* vs. *ma'rûf*; *kâfir* vs. *fâsık* vs. *mücrim*) **asla aynı değişkene indirgenmez**; her biri kendi adını korur, aralarındaki kapsama ilişkisi `⊂` ile ayrıca kaydedilir.

---

## 5. Karşımıza Çıkacak 16 Kur'ânî Kalıp ve Biçimsel Karşılıkları

Herhangi bir âyeti okurken karşılaşılan yapı aşağıdaki karar tablosuna göre kodlanır:

| # | Karşılaşılan Kalıp | Biçimsel Şablon | Metodolojik Not |
| :--- | :--- | :--- | :--- |
| **1** | **Hasr / Mahsusluk** | `A ↦! B` | Sıradan aidiyet (`↦`) ile karıştırılmaz; dışlanan tüm alternatifler zımnen `¬` alır. |
| **2** | **Esmâ-i Hüsnâ Fâsılası (*Tezyîl*)** | `E_i ∵ Allah{Esmâ₁, Esmâ₂}` | Âyet sonundaki isimler süs değildir; o âyetteki hükmün **ontolojik gerekçesi** (`∵`) olarak bağlanır. |
| **3** | **Şartlı Emir / Yasak** | `O(φ \| ψ)` veya `F(φ \| ψ)` | Şart ($\psi$) yoksa `O(φ)` yazılır; şart varsa asla ayrı cümle gibi koparılmaz. |
| **4** | **Ruhsat ve Mazeret** | `O(φ) ∧ ⊘(φ \| γ) ∧ [Alternatif]` | Genel emir, mazeret şartı ($\gamma$) ve ikame fiil (örn. teyemmüm, fidye) tek denklemde birleşir. |
| **5** | **İstisnâ (Muttasıl / Munkatı')** | Muttasıl: `∀x ∈ (A ∖ B) : P(x)` <br> Munkatı': `E₁ ∧ [Lâkin] E₂` | Muttasıl istisnada $B \subset A$ şartı aranır; munkatı' istisnada küme farkı değil zıt hüküm bağlacı konur. |
| **6** | **Kasem (Yemin)** | `⟐(A₁, …, Aₙ) ⊢ ↑!(B)` | Müksemün-bih ($A_i$) ile cevâbü'l-kasem ($B$) arasındaki **delil ilişkisi** (`⊢`) açıkça kurulur. |
| **7** | **Mesel / Temsil** | `Yapı(Somut) ≅ Yapı(Manevî)` | Somut nesneler değil, nesneler arası **bağıntı ağı** hedef alana fonktör olarak taşınır. |
| **8** | **Kıssa (Tarihî Anlatı)** | `τ₋: (e₁ ▷ e₂ ▷ … ▷ eₙ) ⊢ □(İlke)` | Kıssa olay zinciri (`▷`) olarak kayıpsız yazılır; sonunda çıkardığı evrensel yasa (`□`) ayrı düğümle bağlanır. |
| **9** | **İtiraz ve Reddiye (*Cedel*)** | `B_Hasım(φ) ⊢[Red] ¬φ ∧ (D ⊢ ψ)` | Hasımın iddiası `B_x` (zan/iddia) içine alınır; böylece Allah'ın hükmüyle asla aynı doğruluk katmanında görünmez. |
| **10** | **Retorik Soru (*İstifham*)** | `?⊥(φ) ⇒ ¬φ` veya `?⊤(φ) ⇒ φ` | Hem soru biçimi (`?⊥/?⊤`) hem de ürettiği kesin hüküm birlikte kaydedilir; soru tonu kaybolmaz. |
| **11** | **Mukabele (Zıt Tablo)** | `[Grup₁ : Vasıf₁ → Akıbet₁] ⋈ [Grup₂ : Vasıf₂ → Akıbet₂]` | Simetrik her unsur karşısındaki zıddıyla hizalanır; eksik bırakılan simetri varsa `⟨örtük⟩` ile işaretlenir. |
| **12** | **Kâinat Âyeti (Kozmik Delil)** | `OlgusalDüzen(x) ⊢ Tevhid ∨ Diriliş` | Tabiat olgusu tek başına doğa betimlemesi olarak bırakılmaz; işaret ettiği itikadî sonuca `⊢` ile bağlanır. |
| **13** | **Dua / Yakarış** | `Req(Kul ↦ Allah, φ) ∵ Gerekçe` | Duanın hem yönelimi hem de duada öne sürülen vesile/gerekçe (rahmet, acziyet) kaydedilir. |
| **14** | **Vaad ve Vaîd (Ödül/Ceza)** | `τ₀: Amel(x) → τ_∞: Karşılık(x)` | Dünya eylemi (`τ₀`) ile ahiret karşılığı (`τ_∞`) arasındaki zaman sıçraması açıkça işaretlenir. |
| **15** | **İltifat (Hitap Kayması)** | `Hitap(k₁ → k₂) : E` | Üçüncü şahıstan ikinci şahsa (veya tersine) geçiş kayda alınır; hitap değişimi mantıksal yakınlaşma/uzaklaşma göstergesidir. |
| **16** | **Tahsîs / Takyîd / Çapraz Bağ** | `E(S₁:a₁) ⤏[takyîd] E(S₂:a₂)` | Bir âyetin mutlak hükmü başka bir âyetle sınırlandığında çapraz referans (`Sûre:Âyet`) bağı kurulur. |

---

## 6. Denklemleri Bağlama ve Üst Denklem (Faktör) Çıkarma Kuralları

Atomik $L_0$ denklemleri biriktikçe, "buradan buraya nasıl geçildi?" ve "bu beş âyet aslında hangi tek denklemin açılımı?" sorularını çözen iki mekanizma devreye girer: **Bağlantı Operatörleri** ve **Cebirsel Faktörleme Kuralları**.

### 6.1 Âyetten Âyete Zorunlu Geçiş (Bağlantı) Tipleri

İki ardışık denklem ($E_i$ ve $E_{i+1}$) arasına mutlaka şu 8 yönlü bağdan en az biri atanır; bağsız yan yana dizilim kabul edilmez:

1. **Ta'lîl (`E_i ⟸[Ta'lîl] E_{i+1}`):** Sonraki denklem öncekinin sebebini/illetini verir.
2. **Tefrî' (`E_i ⟹[Tefrî'] E_{i+1}`):** Sonraki denklem öncekinin zorunlu amelî veya mantıksal sonucudur.
3. **Tafsîl / İcmâl (`E_i ⊐[Tafsîl] {E_{i+1}…E_k}`):** Önceki özlü ilke sonraki denklemlerde madde madde açılır (veya tersi: `⊏[İcmâl]`).
4. **Mukâbele (`E_i ⋈[Mukâbele] E_{i+1}`):** Önceki tablonun zıt kutbu kurulur.
5. **İstidlâl (`E_i ⊢[İstidlâl] E_{i+1}`):** Önceki olgu/kıssa/yemin sonraki hükmün kanıtıdır (veya tersi: hüküm önce, delil sonra).
6. **Takyîd / Dengeleme (`E_i ⤏[Denge] E_{i+1}`):** Önceki ağır veya mutlak hüküm, sonraki istisna/ruhsat/rahmet ilkesiyle dengelenir.
7. **Temsîl / Misal (`E_i ≅[Temsîl] E_{i+1}`):** Önceki soyut hüküm somut bir mesel veya tarihî kıssayla yapısal olarak canlandırılır.
8. **Te'kîd / Tezyîl (`E_i ⟲[Tezyîl] E_{i+1}`):** Önceki bölüm genel bir ilâhî yasa veya esmâ mührüyle kapatılır.

### 6.2 Altı Cebirsel Üst-Denklem (Faktörleme) Kuralı

Biriken $L_0$ denklemleri şu 6 kuraldan biri sağlandığında **üst denkleme** katlanır:

1. **Ortak Terim Parantezine Alma (*Distributive Factoring*):**
   $$P(a_1) \wedge P(a_2) \wedge \dots \wedge P(a_n) \;\Longrightarrow\; P(\{a_1, a_2, \dots, a_n\})$$
   Aynı hüküm, aynı sıfat veya aynı akıbet birden çok ögeye bağlandığında ortak yüklem dışarı alınır; alt ögeler küme olarak içeride saklanır (sıfır kayıp).
2. **İz Koruyan Zincirleme (*Trace-Preserving Transitivity*):**
   $$(A \to B) \wedge (B \to C) \;\Longrightarrow\; A \xrightarrow{[B]} C$$
   Ara halka $B$ silinmez; okun üzerinde iz olarak tutulur. Böylece üst katmanda doğrudan $A \to C$ okunur, derinleşince $[B]$ açılır.
3. **Bölünme / Kutuplaşma Katlaması (*Partition Factoring*):**
   $$(\psi \to R_1) \wedge (\neg\psi \to R_2) \;\Longrightarrow\; \text{Ayrım}(\psi : R_1 \;\bowtie\; \neg\psi : R_2)$$
   Bir imtihan veya ölçü karşısında insanlığın iki veya üç sınıfa ayrıldığı bloklar tek bir parçalanma denkleminde toplanır.
4. **Fonktörel Yasa Çıkarma (*Invariant Extraction*):**
   $$\bigwedge_{k \in K} \big(\text{Vaka}_k(X_k \to Y_k)\big) \;\Longrightarrow\; \square\big(\forall x \in K : X(x) \to Y(x)\big) \;\Big[\text{Şahitler: } K\Big]$$
   Birden fazla peygamber kıssası veya kâinat delili aynı değişmez yasayı (*sünnetullah*) tekrarladığında, ortak yasa üst denklem olur; tekil kıssalar onun şahit kümesine yerleşir.
5. **Şart–İstisna Kapalı Formu (*Scoped Override*):**
   $$O(\varphi) \wedge \oslash(\varphi \mid \gamma) \wedge O(\varphi' \mid \gamma) \;\Longrightarrow\; O_{\text{tam}}(\varphi \mid \neg\gamma ;\;\; \varphi' \mid \gamma)$$
   Ana hükümle sonradan gelen ruhsat/istisna tek bir eksiksiz karar denkleminde birleştirilir.
6. **Tanım Katlaması (*Definitional Folding*):**
   $$X := \{v_1 \wedge v_2 \wedge \dots \wedge v_m\} \quad \text{ve} \quad (\{v_1 \wedge \dots \wedge v_m\} \to R) \;\Longrightarrow\; X \to R$$
   Uzun vasıf zincirleri (örneğin bir grubun 8 özelliği) tek bir tanımlı terime ($X$) katlanır; üst denklem sadeleşirken $X$'in tanımı bütün alt maddeleri korur.

### 6.3 Beş Katmanlı Denklem Mimarisi ($L_0 \to L_4$)

| Katman | Adı | Kapsam | Çıktı Biçimi |
| :--- | :--- | :--- | :--- |
| **$L_0$** | **Atomik Âyet Denklemi** | Tek âyet (gerekirse cümle parçaları `a, b, c`) | Kayıpsız biçimsel formül + zamir çözümü + `⟨örtük⟩` işaretleri |
| **$L_1$** | **Yerel Mantık Bloğu** | 2–8 âyet | İlk faktörleme: $L_0$ denklemlerinin Kural 1–6 ile birleştirilmesi ve geçiş bağları |
| **$L_2$** | **Makam Denklemi** | Bir argüman, hüküm veya kıssa bütünlüğü | $L_1$ bloklarının nedensel/diyalektik denklemi |
| **$L_3$** | **Sûre Esas Denklemi** | Tek sûrenin tamamı | Sûrenin tüm $L_2$ makamlarını tek omurgada toplayan kapalı denklem sistemi |
| **$L_4$** | **Mushaf Denklem Ağı** | Sûreler arası bütün | Çapraz tahsîs (`⤏`), ortak yasa (`□`) ve sûreler arası münâsebet hiperçizgesi |

---

## 7. Yedi Zorunlu Doğrulama Testi ve Çalışma Protokolü

Herhangi bir $L_1$–$L_3$ üst denklemi kesinleşmeden önce şu yedi testten geçmek zorundadır:

1. **Kayıpsızlık (Geri-Açılım) Testi:** Üst denklemdeki her sembol tanımına göre açıldığında, kapsadığı her $L_0$ âyetindeki tüm kavramlar, şartlar ve istisnalar eksiksiz geri dönüyor mu? Tek bir unsur bile eksikse faktörleme reddedilir.
2. **Geri-Okuma (Yabancı Okuyucu) Testi:** Sûreyi daha önce hiç okumamış biri, yalnızca $L_1$ ve $L_2$ denklemleri ile aralarındaki geçiş operatörlerini (`⟸[Ta'lîl]`, `⟹[Tefrî']`, `⤏[Denge]`) okuduğunda, "şimdi neden bu geldi?" sorusunu sormadan akışı kesintisiz izleyebiliyor mu?
3. **Katman Saflığı Testi:** Hasımın iddiası (`B_x`), kesin gerçek (`⊤`/`□`) ile aynı düzleme karışmış mı? Metinde açıkça geçen ile dilsel çıkarım (`⟨...⟩`) birbirinden net ayrılmış mı?
4. **Kanonik Tutarlılık Testi:** Aynı kavram sûre boyunca aynı sembolle mi yazılmış? Farklı incelikli kavramlar (*hamd* vs. *şükür* gibi) yanlışlıkla birleştirilmiş mi?
5. **Kapsama ve Süreklilik Testi:** Sûrenin 1. âyetinden son âyetine kadar hiçbir âyet atlanmadan, çakışmadan ve bağsız bırakılmadan $L_0$ ağacına bağlı mı?
6. **Yapısal Zorunluluk (Occam) Testi:** Kullanılan her Katman II sembolü için *"Bunu kaldırıp Katman I ile yazsam metindeki gerçek bir dinamik, boyut veya kısıt kaybolur mu?"* sorusu sorulur; cevap "hayır" ise sembol derhal çıkarılır.
7. **Kaide Saflığı Testi:** Üst denklemlerde türetilen her kural, tikel örneklerden bağımsız ve geri-açılabilir midir; yoksa bir örnek yanlışlıkla genel kaide yerine mi konulmuştur?

### Uygulama Protokolü (Adım Adım İş Akışı)
1. **Metin ve İrâb Tespiti:** Her âyet önce Arapça aslına göre cümle öğelerine, edatlarına ve zamir mercilerine ayrılır.
2. **$L_0$ Kodlaması:** Bölüm 3–5 kurallarına göre âyetin kayıpsız atomik denklemi yazılır.
3. **Bağ Ataması:** Bir önceki $L_0$ ile arasındaki geçiş operatörü (Bölüm 6.1) zorunlu olarak belirlenir.
4. **Organik Faktörleme:** Biriken $L_0$'lar doğal bir kapanışa ulaştığında Bölüm 6.2 kurallarıyla $L_1$ üst denklemi çıkarılır ve Kayıpsızlık Testi'nden geçirilir.
5. **Yukarı Yükseliş:** $L_1$'ler tamamlandıkça $L_2$ makam denklemleri ve nihayet sûrenin $L_3$ Esas Denklemi kurulur.


---

# KATMAN II — İLERİ MATEMATİKSEL MODELLEME

## 8. En Umumi Senaryolar İçin Matematiksel Seçim Matrisi

Herhangi bir âyet ($L_0$) veya âyet grubu ($L_1$–$L_4$) incelenirken, karşılaşılan **soyut yapısal senaryoya** göre hangi matematik dalının çağrılacağı aşağıdaki karar tablosuyla belirlenir:

| # | Karşılaşılan Genel Yapısal Senaryo | Çağrılacak Matematik Dalı | Temel Operatör / Yapı |
| :--- | :--- | :--- | :--- |
| **1** | Statik varlık, sıfat, hüküm, şart, delil veya zıtlık ilişkisi | **Katman I (Mantık Çekirdeği)** | `↦!`, `→`, `O/F/P`, `□`, `⊢`, `⋈` |
| **2** | Bir durumun zaman içinde sürekli **veya** kesikli sıçramayla artması/azalması | **Zaman Ölçekleri Kalkülüsü** ($\mathbb{T}$) | $f^\Delta(t) \gtrless 0$, $\Delta^2 f$ |
| **3** | Çok etkenli bir çıktının tek bir girdideki değişime marjinal duyarlılığı | **Çok Değişkenli Analiz (Kısmî Türev)** | $\frac{\partial y}{\partial u_i}$ |
| **4** | İhmal edilemeyecek en küçük birimlerin kesin hesap korunumu | **Standart Dışı Analiz** (${}^*\mathbb{R}$) | $d\alpha \neq 0 \Rightarrow \Phi(d\alpha) \neq 0$ |
| **5** | Aralık/süreç boyunca ağırlıklı toplam, sıfırlanma veya geçmiş dönüşümü | **Ölçü ve İntegral Operatörleri** | $\int_{\mathbb{T}} \mathcal{W}\cdot f\,\Delta t$, $\mathcal{R}[\int]$ |
| **6** | Bağımsız eksenlerin ayrıştırılması, aynı etkinin farklı öznede zıt sonuç vermesi, boşa düşenler kümesi | **Lineer Cebir** | $\{\vec{e}_k\}$, ⟂, $\lambda_x$, $\ker(T)$, $\text{proj}_U$, $\text{rank}$ |
| **7** | Üç veya daha fazla bağımsız eksenin ($n \ge 3$) aynı ilişkide kesişmesi | **Çoklu Lineer Cebir (Tensörler)** | $\mathcal{T}^{i_1\dots i_p}_{j_1\dots j_q}$, `Kesit`, `Daralt` |
| **8** | En yüksek/en düşük baskın koşul ve sıralı eşik zincirlerinin doğrusallaştırılması | **Tropikal Cebir (*Max-Plus / Min-Plus*)** | $(\oplus_T=\max/\min,\ \otimes_T=+)$ |
| **9** | İki veya daha fazla durumun birbirini karşılıklı değiştirmesi | **Birleşik Dinamik Sistemler** | $\{ \Delta s_1 = F_1(\cdot),\ \Delta s_2 = F_2(\cdot) \}$ |
| **10** | Süperpozisyonun bozulması, geri besleme, kritik eşik aşımı, geri dönüşsüzlük, dallanma | **Gayrı Lineer Dinamikler** | `↻⁺ / ↻⁻ / ↻⁰`, $s > s_{\text{kr}}$, `⋔` |
| **11** | Kesin noktasal sınır yerine iç içe kapsam bölgeleri veya sıralı dereceli üyelik | **Bölge Cebiri (*Locale*) ve Kafes-Bulanık Mantık** | Heyting kafesi $L$, $\mu_A(x) \in L$ |
| **12** | Hiyerarşik yakınlık ölçümü ve farklı katmanlarda aynı yapının tekrarı | **Ultrametrik (*p-Adik*) ve Öz-Benzerlik** | $d_p(x,y)$, $L_k \simeq L_{k+m}$ |
| **13** | İki ayrı alan arasında ilişki yapısını koruyan aktarım ve denklik indirgemesi | **Kategori Teorisi ve Bölüm Yapıları** | $F: \mathcal{C} \to \mathcal{D}$, $G/N$ |
| **14** | Çoklu aktörlerin karşılıklı stratejik etkileşimi ve kısıt altında denge yörüngesi | **Oyun Teorisi ve Varyasyonel Kısıt Yapısı** | $\Omega(x)$, $\delta S = 0$, $u_i^* \leftrightarrow \bar{s}$ |
---

## 9. Değişken Rolleri, Uzaylar ve Sınır Kaideleri

Katman II'ye geçilen her denklemde terimler düz sembol olarak bırakılmaz; **altı işlevsel rol**den birine atanır:

* **Mutlak Sabitler ($C$):** Sistemin hiçbir değişkeniyle değişmeyen ontolojik dayanaklar ve değişmez yasalar ($\Delta C \equiv 0$).
* **Bağımsız / Kontrol Değişkenleri ($u$):** Özgür irade veya dışsal karar merciince belirlenen girdiler.
* **Durum Değişkenleri ($s(t)$):** Sistemin $t$ anındaki birikimli iç hâli; geçmiş kontrol kararlarının izini taşır.
* **Bağımlı Çıktı Değişkenleri ($y$):** Kontrol, durum ve parametrelerin fonksiyonu olarak doğan sonuçlar: $y = f(u, s; \theta)$.
* **Bağlam Parametreleri ($\theta$):** İlişkinin veya hükmün geçerli olduğu zaman, mekân, mazeret, bilgi erişimi gibi dış koşullar.
* **Başlangıç ve Sınır Koşulları ($s(t_0),\ \Omega$):** Sürecin başlangıç hâli ve geçerli çözüm/yükümlülük uzayının sınırları.

**Ayrıştırma Kaidesi:** Bir denklemde $u$ (kontrol) ile $C$ (sabit) ve $\theta$ (bağlam) ayrıştırılmadan üst denkleme çıkılmaz; böylece **değişmez yasa**, **iradî tercih** ve **bağlamsal şart** hiçbir katmanda birbirine karışmaz.
---

## 10. Analitik ve Dinamik Kaideler (Değişim, Duyarlılık ve Birikim)

### 10.1 Zaman Ölçekleri Kalkülüsü ($\mathbb{T},\ f^\Delta$)
Metinlerdeki süreçler kimi zaman **sürekli** bir gelişim, kimi zaman da **ani/kesikli** bir hâl değişimi gösterir. Yapay süreklilik varsaymamak için zaman ekseni genel bir zaman ölçeği $\mathbb{T}$ olarak tanımlanır ve tek bir **delta türevi** ($f^\Delta$) kullanılır:
* Sürekli aralıkta: $f^\Delta(t) = \frac{df}{dt}$ (yön ve değişim hızı: $>0$ artış, $<0$ azalış, $=0$ durağanlık).
* Kesikli adımda ($t_k \to t_{k+1}$): $f^\Delta(t_k) = f(t_{k+1}) - f(t_k)$ (hâl sıçraması).
* İkinci mertebe değişim ($f^{\Delta\Delta}$): Artışın veya çözülmenin **ivmelenmesini** (hızlanarak derinleşmesini veya yavaşlayarak sönümlenmesini) kaydeder.

### 10.2 Kısmî Türev / Marjinal Duyarlılık ($\frac{\partial y}{\partial x_i}$)
Bir çıktı $y = f(x_1, \dots, x_n)$ birden fazla değişkene bağlıyken metin özellikle tek bir etkenin bağımsız etkisini vurguluyorsa, diğer değişkenler sabit tutularak kısmî türev yazılır:
* $\frac{\partial y}{\partial x_i} > 0$: Pozitif marjinal etki.
* $\frac{\partial y}{\partial x_i} = 0$: İlgili değişkenin (veya dış uyaranın) mevcut durumda çıktı üzerinde **etkisiz kalması** (duyarsızlaşma).

### 10.3 Standart Dışı Analiz / Sonsuz Küçük Hassasiyet ($d\alpha \in {}^*\mathbb{R}$)
Bir ölçekte "ne kadar küçük olursa olsun sıfırlanamayacak" bir unsur ifade edildiğinde, klasik limit yaklaşımıyla ihmal yapmak yerine **hiperreel sonsuz küçük ($d\alpha \neq 0$)** kullanılır:
$$\forall\, d\alpha \in {}^*\mathbb{R}\setminus\{0\} : \quad \text{Ölçü}(d\alpha) \neq 0$$

### 10.4 Ağırlıklı Birikim İntegrali ve Dönüşüm Operatörleri
Tekil eylemlerin bir aralık $[t_a, t_b] \subset \mathbb{T}$ boyunca toplanması gerektiğinde **ağırlıklı integral** kullanılır:
$$I_{[t_a, t_b]} = \int_{t_a}^{t_b} \mathcal{W}(\vec{c}(t)) \cdot \phi(t)\,\Delta t$$
* **Geçerlilik Ağırlığı ($\mathcal{W}$):** Bir eylemin değerini belirleyen içsel şartlar vektörü $\vec{c}(t)$ sıfırlayıcı koşula düşerse ($\mathcal{W} = 0$), $\phi(t) \neq 0$ olsa bile birikim sıfırlanır.
* **Geçmiş Dönüştürme Operatörü ($\mathcal{T}$):** Belirli bir aralıktaki negatif birikimi silen ($\mathcal{R}_{\text{sil}}$) veya işaretini tersine çeviren ($\mathcal{R}_{\text{çevir}}$) üst operatörler doğrudan integralin önüne yazılır.
* **Açık Üst Sınır ($t_b \to t_{\text{son}}$):** Etkisi öznenin doğrudan eylem anından sonra da süren birikimler için üst sınır açık/uzatılmış olarak işaretlenir.
---

## 11. Cebirsel ve Çok Boyutlu Kaideler

### 11.1 Lineer Cebir Kaideleri (Vektör Uzayı, Baz, Operatör, Özdeğer, Çekirdek, İzdüşüm)
* **Baz Ayrıştırması ($\{\vec{e}_1, \dots, \vec{e}_m\}$):** Bir bölümde veya sûrede birbirine indirgenemeyen temel eksenler **lineer bağımsız baz vektörleri** olarak belirlenir.
* **Dikgenlik ($\vec{e}_i \;\text{⟂}\; \vec{e}_j$):** Bir eksendeki artışın diğer eksendeki eksikliği telafi edemediği (ikame edilemez) iki ayrı sorumluluk veya nitelik dikgen olarak kodlanır.
* **Operatör ve Özdeğer İşareti ($T(\vec{v}_k) = \lambda_k \vec{v}_k$):** Aynı dışsal etken/mesaj ($T$), farklı özne tiplerine ($\vec{v}_1, \vec{v}_2$) etki ettiğinde farklı yönlü sonuç doğuruyorsa, bu ayrım özdeğer işaretleriyle ($\lambda_1 > 0,\ \lambda_2 < 0$) tek bir operatör denkleminde toplanır.
* **Çekirdek ve Görüntü ($\ker(T),\ \text{Im}(T)$):** Bir değerlendirme/kabul operatörü $T$ altında sıfıra düşen (geçersizleşen) unsurlar kümesi $\ker(T)$, geçerli sonuç üreten alan $\text{Im}(T)$ olarak tanımlanır.
* **Dik İzdüşüm ($\text{proj}_U(E)$):** Birden fazla boyuta dokunan bir denklem $E$'den yalnızca seçili bir alt-uzay $U$'daki saf bileşeni çekmek için kullanılır; asıl denklem bozulmaz.
* **Bağımsızlık / Rank Testi ($\text{rank}$):** $L_1 \to L_3$ yükseltmesinde bir yeni denklemin mevcut bazların doğrusal bileşimi (pekiştirme/tekrar) mi, yoksa **rank'ı artıran bağımsız yeni bir eksen** mi olduğu denetlenir.

### 11.2 Genel $(p,q)$-Tensör ve Daraltma Kaideleri
Üç veya daha fazla bağımsız eksenin aynı anda etkileştiği herhangi bir ilişkide, iki boyutlu tablo veya düz önerme bilgi kaybına yol açtığından **genel $(p,q)$-tensör** kurulur:
$$\mathcal{T}^{i_1 \dots i_p}_{j_1 \dots j_q}$$
* Alt indeksler ($j_1, \dots, j_q$): **Koşul / bağlam / girdi eksenleri**.
* Üst indeksler ($i_1, \dots, i_p$): **Hüküm / sonuç / çıktı eksenleri**.
* **Kesit Alma (*Slicing*):** Bir veya birkaç indeks sabitlendiğinde ($j_k = c_0$) o özel koşula ait tikel denklem kayıpsız çekilir.
* **Tensör Daraltması (*Contraction* — $\text{Daralt}_{j_k}(\mathcal{T})$):** Bir eksen üzerinden tüm örnekler ortaklaştırıldığında tensörün derecesi bir azalır ve o eksenden bağımsız **evrensel değişmez üst denklem** ($L_2/L_3$) elde edilir.

### 11.3 Tropikal Cebir (*Max-Plus / Min-Plus*) Kaideleri
Bir sonucun toplamayla değil **en baskın/en ağır/en zayıf tek şartla** belirlendiği veya ardışık eşiklerin senkronize edildiği doğrusal olmayan yapılarda Tropikal Yarı-Halka kullanılır:
$$a \oplus_T b := \max(a, b) \;\; (\text{veya } \min(a,b)), \qquad a \otimes_T b := a + b$$
Bu dönüşümle karmaşık sıralama–öncelik–engel zincirleri **doğrusal cebir formuna** indirgenerek sadeleştirilir.

### 11.4 Soyut Cebir, İşlem Özellikleri ve Bölüm Yapıları ($G/N$)
* **İşlem Özellikleri:** Birleşmelerin değişmeli olup olmadığı ($a \circ b \stackrel{?}{=} b \circ a$), tersinir olup olmadığı ($a^{-1}$ var mı?) ve etkisiz eleman ($e$) açıkça kontrol edilir.
* **Bölüm Yapısı (*Quotient Structure* — $S / \sim$):** Alt katmanda aynı yapısal işlevi gören denklik sınıfları ($\sim$) tek bir **bölüm elemanına** indirgenir. Üst denklem bu bölüm yapısı üzerinde kurulur; her bölüm elemanının temsil ettiği denklik sınıfı saklı kaldığından işlem **tamamen kayıpsızdır**.
---

## 12. Gayrı Lineer Dinamikler ve Etkileşim Sistemleri Kaideleri

### 12.1 Birleşik (Coupled) Denklem Sistemleri
İki veya daha fazla durum değişkeni ($s_1, s_2, \dots, s_k$) birbirinin değişim oranına girdi oluyorsa, bunlar ayrı ayrı satırlara bölünmez; **tek birleşik sistem** olarak yazılır:
$$\begin{cases} s_1^\Delta = F_1(s_1, \dots, s_k;\, u_1, \theta) \\ \vdots \\ s_k^\Delta = F_k(s_1, \dots, s_k;\, u_k, \theta) \end{cases}$$

### 12.2 Doğrusal Olmayan Ölçeklenme ve Asimetri
$f(a + b) \neq f(a) + f(b)$ veya $f(-a) \neq -f(a)$ koşulu görüldüğünde sistem açıkça **gayrı lineer** olarak etiketlenir:
* **Süperlineer Katlanma:** $f(\alpha) \gg c\cdot \alpha$.
* **İşaret Asimetrisi:** Pozitif ve negatif bölgelerde farklı çarpan/kural uygulanması ($f^+ \neq -f^-$).

### 12.3 Geri Besleme Döngüleri (`↻⁺`, `↻⁻`, `↻⁰`)
Bir sürecin çıktısı tekrar kendi girdisine bağlanıyorsa kapalı çevrim türü belirtilir:
* **Yükselten Pozitif Geri Besleme (`↻⁺`):** Durumdaki pozitif artışın aynı yönde daha güçlü artışı tetiklemesi.
* **Yıkıcı Pozitif Geri Besleme (`↻⁻`):** Sapmanın kendi kendini büyüterek sistemi hızla uzaklaştırması.
* **Dengeleyici Negatif Geri Besleme (`↻⁰`):** Sapma algılandığında sistemi denge noktasına geri çeken düzeltici mekanizma.

### 12.4 Eşik, Faz Geçişi, Histerezis ve Çatallanma (`⋔`)
* **Kritik Eşik ve Faz Geçişi ($s > s_{\text{kr}}$):** Bir durum değişkeni kritik eşiği aştığında sistemin tepki kuralı niteliksel olarak değişir ($F_{\text{öncesi}} \to F_{\text{sonrası}}$).
* **Geri Dönüşsüzlük / Histerezis:** Belirli bir zaman veya eşik duvarı ($t \ge t_{\text{kapı}}$) geçildikten sonra ters operatörün ($\mathcal{R}^{-1}$) tanımlı olmaktan çıkması.
* **Çatallanma (*Bifurcation* — `⋔`):** Bir dış kontrol/imtihan parametresi $\beta$ kritik değer $\beta_c$'yi aştığında tek görünen bir kümenin veya yörüngenin iki ya da daha fazla ayrık dala bölünmesi: $X \xrightarrow{\;\beta > \beta_c\;} X_1 \bowtie X_2$.
* **Kararlılık ve Çekiciler (*Attractors*):** Küçük bozucu etkilere rağmen korunan denge **kararlı**, küçük sarsıntıda dağılan denge **kararsız**, uzun vadede tüm yörüngelerin toplandığı nihai bölgeler **çekici** olarak işaretlenir.

### 12.5 Çoklu Aktör / Stratejik Etkileşim (Oyun ve Ortalama Alan)
Bireysel karar değişkeni $u_i$ ile topluluğun ortalama durumu $\bar{s}$ arasında çift yönlü etkileşim bulunduğunda (birey topluluğa bakarak karar verir, bireylerin toplamı topluluğu değiştirir), yapı **çift yönlü aktör–topluluk sistemi** olarak kodlanır.
---

## 13. Topolojik, Dereceli, Hiyerarşik, Kategorik ve Varyasyonel Kaideler

### 13.1 Sabit Noktasız Kapsam Cebiri (*Locale / Heyting Cebiri*)
Keskin tekil noktalarla değil, **genişlik, kapsama ve kesişim bölgeleriyle** tanımlanan kavram veya hükümlerde noktasal küme yerine bölge kafesi kullanılır:
* Kapsama ($U \le V$), kesişim ($U \wedge V$), birleşim ($U \vee V$) ve göreli tümleme ($U \Rightarrow V$).

### 13.2 Kafes-Değerli Dereceli Üyelik (*Lattice-Valued Fuzzy Logic*)
İkili (`0/1`) sınıflamanın yetersiz kaldığı ama metinde sayısal yüzde de verilmediği dereceli hâllerde, keyfî $[0,1]$ sayısı atamak yerine **sıralı soyut kafes** $(L, \preceq)$ üzerinde üyelik tanımlanır:
$$\mu_A(x) \in L, \qquad \bot_L \prec l_1 \prec l_2 \prec \dots \prec \top_L$$

### 13.3 Ultrametrik Hiyerarşi (*p-Adik Yakınlık*) ve Öz-Benzerlik (*Self-Similarity*)
* **Ultrametrik Yakınlık:** İki kavramın veya iki hükmün yapısal yakınlığı doğrusal metin mesafesiyle değil, denklem ağacındaki **en derin ortak üst-düğüm** ile ölçülür: $d(x, z) \le \max\big(d(x, y),\, d(y, z)\big)$.
* **Ölçek Değişmezliği / Öz-Benzerlik ($L_k \simeq L_{k+m}$):** Aynı biçimsel denklem yapısı farklı ölçeklerde (küçük birim ↔ büyük birim) yapısal olarak kendini tekrarlıyorsa, bu tekrar ayrı kurallar gibi çoğaltılmaz; **ölçek-değişmez tek denklem** olarak işaretlenir.

### 13.4 Kategori Teorisi ve Değişmeli Diyagramlar
İki farklı alan ($\mathcal{C}$ ve $\mathcal{D}$) arasında yalnızca tekil nesne benzetmesi değil **ilişki ağı aktarımı** yapıldığında, yapı **fonktör** $F: \mathcal{C} \to \mathcal{D}$ ile kodlanır:
$$f: A \to B \text{ in } \mathcal{C} \;\Longrightarrow\; F(f): F(A) \to F(B) \text{ in } \mathcal{D}, \qquad F(g \circ f) = F(g) \circ F(f)$$
İki farklı çıkarım yolunun aynı sonuca ulaşması **değişmeli diyagram** (*commutative diagram*) ile tescil edilir.

### 13.5 Kısıt Uzayı ve Varyasyonel Denge ($\Omega,\ \delta S = 0$)
* **Kısıt Uzayı ($\Omega$):** Her deontik yükümlülük veya eylem kuralı, geçerli imkân/kısıt kümesi $\Omega$ içinde tanımlanır: $\varphi \in \Omega$.
* **Kısıt Gevşetme (*Constraint Relaxation*):** Dış parametre $\theta$ sınır koşulunu zorladığında $\Omega \to \Omega'$ genişlemesi (ruhsat/istisna) otomatik işlenir.
* **Varyasyonel Denge ($\delta S = 0$):** İki karşıt aşırılık arasında tanımlanan ideal yörünge, kısıtlar altında denge/ekstremum koşulu olarak formülleştirilir.
---

## 14. Katman II Genişletilmiş Operatör Özeti ve Yükseltme Kuralları

### 14.1 Katman II Sembol Özeti (Katman I Alfabesine Ek)

| Sembol | Adı | Genel Kullanım Koşulu |
| :--- | :--- | :--- |
| `C / u / s / y / θ / Ω` | **Rol Etiketleri** | Sabit / kontrol / durum / çıktı / bağlam / kısıt uzayı ayrımı |
| `f^Δ`, `f^{ΔΔ}` | **Zaman Ölçeği Türevi** | Sürekli veya kesikli değişim yönü, hızı ve ivmesi |
| `∂y / ∂x_i` | **Kısmî Türev** | Çok etkenli çıktıda tek girdinin bağımsız duyarlılığı |
| `dα ∈ *ℝ` | **Sonsuz Küçük** | İhmal edilemeyen en küçük birimin korunumu |
| `∫_T W·φ Δt`, `R[∫]` | **Ağırlıklı Birikim** | Aralık içi toplam, geçerlilik ağırlığı ve geçmiş dönüşümü |
| `{ s₁^Δ=F₁, s₂^Δ=F₂ }` | **Birleşik Sistem** | Karşılıklı etkileşen çoklu durum değişkenleri |
| `{e_k}, ⟂, λ_x, ker, Im, proj_U, rank` | **Lineer Cebir** | Baz, dikgenlik, özdeğer işareti, çekirdek–görüntü, izdüşüm, bağımsızlık |
| `T^{i...}_{j...}`, `Kesit`, `Daralt` | **Tensör Cebiri** | $n \ge 3$ eksenli ilişki, özel durum çekme ve indeks daraltma |
| `(⊕_T, ⊗_T)` | **Tropikal Cebir** | Max/min-plus baskın koşul ve eşik zinciri doğrusallaştırması |
| `S / ~`, `F: C → D` | **Bölüm ve Fonktör** | Denklik sınıfına indirgeme ve alanlar arası yapı koruyan aktarım |
| `↻⁺ / ↻⁻ / ↻⁰`, `s > s_kr`, `⋔` | **Gayrı Lineer Yapılar** | Geri besleme türleri, eşik/faz geçişi ve parametre çatallanması |
| `μ_A(x) ∈ L`, `d_p`, `δS = 0` | **Kafes, Ultrametrik, Denge** | Dereceli üyelik, hiyerarşik yakınlık ve kısıtlı denge yörüngesi |

### 14.2 $L_0 \to L_4$ Yükseltme

Katman II araçları, Bölüm 6.3'teki 5 katmanlı mimariye ($L_0 \to L_4$) şu kurallarla eklemlenir:
* **$L_0$ (Atomik Düzey):** Önce Katman I ile kayıpsız kodlanır; yalnızca metinde açık yapısal karşılığı bulunan Katman II operatörleri (rol etiketi, $f^\Delta$, $\partial$, $d\alpha$, $\mu_A \in L$) eklenir.
* **$L_1$ (Yerel Birleşim):** Ardışık $L_0$'lar 8 geçiş bağıyla bağlanır; karşılıklı etkileşenler **birleşik sisteme**, kapalı döngüler **geri beslemeye**, çok eksenliler **tensöre** toplanır.
* **$L_2$ (Faktörleme ve İndirgeme):** Bölüm 6.2'nin 6 cebirsel faktörleme kuralına ek olarak **Tensör Daraltması (`Daralt`)**, **Bölüm Yapısı ($S/\sim$)** ve **Rank Testi** ile gereksiz tekrarlar ayıklanmadan *izleri korunarak* üst denkleme katlanır.
* **$L_3$ ve $L_4$ (Sûre ve Bütün Ağı):** Sûrenin bağımsız baz vektörleri ($\{\vec{e}_k\}$), ana dinamik sistemi, çatallanma/denge noktaları ve sûreler arası fonktörel/hiperçizge bağları kurulur.

---

## 15. Yüz İfade Kabiliyeti

Aşağıdaki kabiliyetler lisanın söyleyebildiği şeyleri genişletir. Hepsi **yapısal**dır: tikel bir âyete, kavrama veya vakaya bağlı değildir; her biri herhangi bir metin parçasında karşılaşılabilecek genel bir durumu söyler. Bir kabiliyet ancak metinde karşılığı varsa kullanılır; karşılığı olmayan yerde yazılmaz (Occam Testi).

### 15.A Söyleyen ve Muhatap (1–10)

| # | Kabiliyet | Şablon | İfade Ettiği |
| :-- | :-- | :-- | :-- |
| 1 | Söyleyen etiketi | `Söz[s](E)` | Cümleyi kimin söylediği: Allah, peygamber, melek, bir kişi veya topluluk |
| 2 | Nakil katmanı | `Aktar[s₁→s₂](E)` | Söyleyenin başkasının sözünü aktarması |
| 3 | İç içe nakil derinliği | `Aktar^n(E)` | Nakil içinde nakil; kaç basamak içeride konuşulduğu |
| 4 | Muhatap tayini | `Muh(E) = M` | Sözün kime yöneldiği; `M` bir tiptir |
| 5 | Muhatap kapsamı kayması | `Muh(E₁) ⊂ Muh(E₂)` | Hitabın dar muhatabdan geniş muhataba (veya tersine) kayması |
| 6 | Hitap cinsi | `Hitap[doğrudan/genel/gıyâbî]` | Karşıya, herkese veya bir yokluğa konuşulduğu |
| 7 | İltifat sebebi | `Hitap(k₁ ⇢ k₂) ∵ C` | Hitap kaymasının hangi sebeple yapıldığı |
| 8 | Belirsiz söyleyen | `Söz[?](E)` | Söyleyenin metinde açık olmadığı hâl; çıkarım `⟨…⟩` ile ayrı yazılır |
| 9 | Dinleyen şahit | `Şahit(E) = d` | Hitap edilmeyen ama sözü duyan ikinci taraf |
| 10 | Dönüşlü söz | `Söz[s→s](E)` | Söyleyenin kendine yönelttiği söz (tefekkür, nefs muhasebesi) |

### 15.B Nazm ve Metin Yapısı (11–22)

| # | Kabiliyet | Şablon | İfade Ettiği |
| :-- | :-- | :-- | :-- |
| 11 | Fâsıla sınıfı | `Fasıla(Eᵢ) = f` | Âyet sonunun ses/vezin sınıfı |
| 12 | Fâsıla kayması | `Fasıla(Eᵢ) ⇥ Fasıla(Eᵢ₊₁)` | Sonun sınıf değiştirmesi |
| 13 | Çerçeve (halka) yapısı | `Çerçeve(E_a … E_b)` | Baş ile sonun karşılıklı kapanması |
| 14 | Ayna (kiazm) yapısı | `⌘[A B B′ A′]` | Ögelerin ortaya göre ters simetrik dizilmesi |
| 15 | Nakarat | `Nakarat(E) × n` | Aynı ifadenin bölümler boyunca dönmesi ve sayısı |
| 16 | Tekrarda fark | `Tekrar(E₁, E₂; Δ)` | Aynı ifadenin iki yerinde bağlam ve eklerin farkı |
| 17 | Bölüm evresi | `Bölüm[açılış/gelişme/kapanış]` | Bir bölümün yapısal rolü |
| 18 | Açılış harfleri | `Açılış[h₁ … hₖ]` | Sûre başındaki, lafzı okunan harf dizisi ve sayısı |
| 19 | Ara cümle | `⟦E⟧` | Akışı kesen itirâz cümlesi; ana akış `⟦ ⟧`ın dışından okunur |
| 20 | Konu geçişi | `Geçiş(Bᵢ ⇒ Bᵢ₊₁; sinyal)` | Konu değişirken kullanılan işaret |
| 21 | Hacim | `Hacim(B) = (âyet, kelime)` | Bölümün yapısal ölçüsü; ağırlık değil sayımdır |
| 22 | Süreklilik | `Süreklilik(Eᵢ, Eᵢ₊₁) ∈ {devam, kesinti, dönüş}` | Konunun sürmesi, kesilmesi veya geri dönmesi |

### 15.C Anlam ve Delâlet (23–34)

| # | Kabiliyet | Şablon | İfade Ettiği |
| :-- | :-- | :-- | :-- |
| 23 | Delâlet yolu | `Del(E) ∈ {ibâre, işâret, delâlet, iktizâ}` | Hükmün metinden hangi yolla alındığı |
| 24 | Açıklık derecesi | `Açıklık(E): zâhir ≺ nass ≺ müfesser ≺ muhkem` | Metnin tek manaya yakınlığı |
| 25 | Kapalılık derecesi | `Kapalılık(E): hafî ≺ müşkil ≺ mücmel ≺ müteşâbih` | Manayı kapatan sebebin derecesi |
| 26 | Hakîkat–mecâz | `Mana[hakîkî/mecâzî](e)` | Kelimenin asıl mı aktarılmış manada mı olduğu |
| 27 | Mecâz alâkası | `Mecâz(e; alâka)` | Aktarmayı sağlayan bağ: cüz-küll, sebep-müsebbep, mekân-hâl, benzerlik |
| 28 | Kinâye | `Kin(E) ⇒ Asıl` | Lâzımın söylenip melzûmun kastedilmesi |
| 29 | İstiâre | `İst(Müşebbeh → Müşebbehün-bih; vecih)` | Benzetilenin benzetene devredilmesi |
| 30 | Teşbih | `Teş(X ~ Y; vecih; edat)` | Benzetme ve benzetme yönü |
| 31 | Müşterek kelime | `Müşterek(e) = {m₁ … mₖ}`, `Seç(e) = mᵢ ∵ C` | Çok manalı kelimede seçilen mana ve gerekçesi |
| 32 | Âmm–hâss | `Âmm(E) ⊃ Hâss(E′)` | Genel lafız ve onun sınırlı dilimi |
| 33 | Mutlak–mukayyed | `Mutlak(E)`, `Mukayyed(E; kayıt)` | Kayıtsız hüküm ve kayıtla daralmış hâli |
| 34 | Mefhûm | `Mef[muvâfık/muhâlif](E) = E′` | Söylenmeyip metnin delâlet ettiği hüküm |

### 15.D Kip, Haber ve İnşâ (35–44)

| # | Kabiliyet | Şablon | İfade Ettiği |
| :-- | :-- | :-- | :-- |
| 35 | Haber–inşâ | `Cümle[haber/inşâ]` | Doğru–yanlışla ölçülen cümle ile talep cümlesi ayrımı |
| 36 | Haber derecesi | `Haber[ibtidâî/talebî/inkârî]` | Muhatabın tereddüdüne göre pekiştirme derecesi |
| 37 | İnşâ türü | `İnşâ[emir/nehiy/istifham/temennî/nidâ]` | Talep cümlesinin cinsi |
| 38 | Emir sigasının manası | `Siga(E) ⇒ {vücûb, nedb, ibâha, tehdit, ta'cîz}` | Emir kalıbının hangi hükmü taşıdığı |
| 39 | İstifhamın manası | `İstif(E) ⇒ {inkâr, takrîr, tevbîh, taaccüb, tehdit}` | Soru kalıbının asıl maksadı |
| 40 | Nidânın maksadı | `Nidâ(k; maksat)` | Seslenmenin tenbih, tazim, şefkat veya azar oluşu |
| 41 | Temennî ve terecci | `Temennî(φ)`, `Terecci(φ)` | Olması istenen ihtimalsiz şey ile umulan ihtimalli şey |
| 42 | Tehdit | `Tehdit(x ⇒ Akıbet)` | Kötü akıbetin ihtarı |
| 43 | Kasr çeşidi | `Kasr[sıfat/mevsûf; hakîkî/izâfî]` | Hasrın nesneye mi sıfata mı, mutlak mı göreli mi olduğu |
| 44 | Fasıl–vasl | `Vasl(Eᵢ, Eᵢ₊₁)` / `Fasıl(Eᵢ, Eᵢ₊₁)` | İki cümle arasında bağlaç olması ve olmaması |

### 15.E Zaman, Mekân ve Sayı (45–54)

| # | Kabiliyet | Şablon | İfade Ettiği |
| :-- | :-- | :-- | :-- |
| 45 | Kip–zaman kayması | `τ(E) ⇢ τ′` | Fiil kalıbının zamanının bağlamdan farklı okunması |
| 46 | Anlık hâl | `Anlık(E)` | Zamanı genişlemeyen, o anda biten olay |
| 47 | Mekân etiketi | `Mek(E) = m` | Olayın veya hükmün yeri |
| 48 | Zaman–mekân koordinatı | `Yer(E) = (τ, m)` | Olayın tam konumu |
| 49 | Metindeki sayı | `#(x) = n` | Metnin açıkça verdiği sabit sayı |
| 50 | Sayı kullanımı | `#[hakîkî/çokluk](x)` | Sayının kesin mi, çokluk işareti mi olduğu |
| 51 | Süre | `Süre(e) = d` | Metnin söylediği süre |
| 52 | Eşzamanlılık | `e₁ ∥ e₂` | İki olayın aynı anda geçmesi (`▷`nın tamamlayıcısı) |
| 53 | Fiil hâli | `Hâl[ânî/sürekli/tekrarlı](e)` | Olayın bir defa mı, sürerek mi, tekrarlanarak mı olduğu |
| 54 | Zamandan bağımsızlık | `τ_Ø(E)` | Hükmün hiçbir zaman dilimine bağlı olmaması |

### 15.F İlişki ve Bağ Ağı (55–66)

| # | Kabiliyet | Şablon | İfade Ettiği |
| :-- | :-- | :-- | :-- |
| 55 | Bağ yönü | `Eᵢ →[B] Eⱼ` | Bağın hangi âyetten hangisine aktığı |
| 56 | Bağ uzaklığı | `d(Eᵢ, Eⱼ)` | İki âyetin ağaçtaki ultrametrik uzaklığı |
| 57 | Çoklu bağ | `Eᵢ ⇉ {Eⱼ, Eₖ}` | Bir âyetin birden çok âyetle kurduğu tek hiperkenar |
| 58 | Çapraz sûre bağı | `S₁:a ∼ S₂:b` | İki sûre arasındaki âyet bağı |
| 59 | Karşılıklı atıf | `Eᵢ ⇄ Eⱼ` | İki âyetin birbirine atıf yapması |
| 60 | Bağ derecesi | `Bağ[zayıf ≺ orta ≺ güçlü]` | Bağın nitel gücü; sayıya çevrilmez |
| 61 | Bağ yokluğu | `Bağ[∅](Eᵢ, Eᵢ₊₁)` | Bağın bulunmadığının açıkça yazılması |
| 62 | Bağ gerekçesi | `Bağ ∵ C` | İki parçanın neden yan yana durduğu |
| 63 | Kavram zinciri | `Zincir(k) = (Eᵢ, Eⱼ, …)` | Bir kavramın metinde geçtiği yerlerin zinciri |
| 64 | Kavram sayımı | `İz(k) = n` | Kavramın metindeki geçiş sayısı |
| 65 | Kavram yakınlığı | `Yakın(k₁, k₂)` | İki kavramın ortak bağlam ağı |
| 66 | Zıt çifti | `Zıt(k₁, k₂)` | Metinde karşılıklı konan iki kavram |

### 15.G Hüküm İncelikleri (67–78)

| # | Kabiliyet | Şablon | İfade Ettiği |
| :-- | :-- | :-- | :-- |
| 67 | Hüküm kapsamı | `Kap(H) = (kim, ne zaman, nerede)` | Hükmün geçerli olduğu üç boyut |
| 68 | Şart ve mâni | `Şart(H)`, `Mâni(H)` | Hükmün doğması için gereken ve engelleyen durum |
| 69 | Sebep–şart–mâni | `(Sbb, Şrt, Mni)(H)` | Üçlü bir arada |
| 70 | Hüküm illeti | `H ∵ İllet`, `İllet-Alan(H)` | Hükmün sebebi ve sebebin yayıldığı alan |
| 71 | Tedrîc | `H₁ ▷ H₂ ▷ H₃` | Hükmün aşama aşama konması |
| 72 | Nesih | `H₂ ⤏[nesh] H₁` | Sonraki hükmün öncekini kaldırması |
| 73 | İkame | `H ⇝ İkame` | Yapılamayan hüküm yerine konan hüküm |
| 74 | Hak ilişkisi | `Hak(x ↦ y)` | Bir tarafın ötekinde sahip olduğu hak |
| 75 | Mükellef şartı | `Mük(x)` | Hükmün muhatabında aranan şartlar (akıl, bülûğ) |
| 76 | Hüküm genişliği | `Dar ≺ Geniş` | Hükmün kapsayıcılık derecesi |
| 77 | Hafifletme | `Hafif(H; sebep)` | Ağırlığın indirilmesi |
| 78 | Yaptırım türü | `Yaptırım[dünyevî/uhrevî](H)` | Hükmün karşılığının dünyada veya âhirette olması |

### 15.H Kıssa, Mesel ve İlke (79–86)

| # | Kabiliyet | Şablon | İfade Ettiği |
| :-- | :-- | :-- | :-- |
| 79 | Kıssa rolü | `Rol(x) ∈ {resûl, hasım, tâbi, şahit}` | Kıssadaki kişinin yeri |
| 80 | Kıssa evresi | `Evre[davet/inkâr/ihtâr/akıbet]` | Kıssanın hangi aşamada olduğu |
| 81 | Kıssa tekrarı | `Kıssaₙ(x) ≠ Kıssaₘ(x)` | Aynı kıssanın iki yerde farklı kesiti |
| 82 | Akıbet çifti | `Akıbet(G) ∈ {kurtuluş, helak}` | Topluluğun sonu |
| 83 | Mesel yapısı | `Mesel(K → H; Eşleme)` | Kaynak ile hedefin eşleştirilmesi |
| 84 | Eşleme tamlığı | `Eşleme[tam/kısmî]` | Benzetmenin hangi ölçüde taşındığı |
| 85 | İlke şahitleri | `Şahit(İlke) = K` | İlkeyi doğrulayan kıssalar |
| 86 | İlke alanı | `İlke ∈ Alan` | İlkenin itikat, ahlâk, hüküm veya tarih alanında olması |

### 15.I Üst Bakış (87–100)

| # | Kabiliyet | Şablon | İfade Ettiği |
| :-- | :-- | :-- | :-- |
| 87 | Sûre omurgası | `Omurga(S)` | Sûreyi taşıyan tek bağ hattı |
| 88 | Sûre mihveri | `Mihver(S) = İlke` | Sûrenin etrafında döndüğü esas |
| 89 | Sûre çerçevesi | `Çerçeve(S)` | Sûre başı ile sonunun karşılıklı kapanması |
| 90 | Açılış–kapanış zıtlığı | `Açılış(S) ⋈ Kapanış(S)` | Başın ve sonun karşılıklı kutuplaşması |
| 91 | Bölüm sırası | `Sıra(S) = (B₁ … Bₙ)` | Bölümlerin dizilişi |
| 92 | Bölüm geçişi | `Geç(Bᵢ, Bᵢ₊₁)` | Bölümler arası geçişin türü |
| 93 | Sûre ailesi | `Aile(S₁ … Sₖ) ⊢ Yapı` | Ortak yapıyı paylaşan sûreler |
| 94 | Sûre çifti | `Eş(S₁, S₂)` | İki sûrenin benzer veya zıt yapıda olması |
| 95 | Mushaf tertibi | `M(Sᵢ ▷ Sᵢ₊₁)` | Sûrelerin mushaftaki sırası |
| 96 | Metin dışı bilgi | `⟨dış: …⟩` | İniş sırası gibi metnin kendisinden alınmayan bilgi |
| 97 | Okuma yolu | `Yol(E_a → E_b)` | Üst bakıştan inişte izlenen basamak dizisi |
| 98 | Yakınlaştırma düzeyi | `Yak(n)` | Okuyucunun bulunduğu basamak (0–4) |
| 99 | Sûre hazfı | `Hazf(S; konu)` | Beklenen konunun sûrede bulunmaması |
| 100 | Sûre kapanışı | `Tam(S)` | Her âyetin ağaca bağlı olduğunun işareti |
