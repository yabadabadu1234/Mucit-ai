# Kur'ân-ı Kerîm İçin Biçimsel Mantık ve Kayıpsız Denklem Sistemi Usûlü (Sürüm 1.0)

Bu belge, Kur'ân-ı Kerîm'in metnini mevzu özetlerine indirmek yerine **kayıpsız, geri-açılabilir, tümevarımsal bir biçimsel mantık ve denklem sistemine** dönüştürmek için geliştirilmiş eksiksiz usûl şartnamesidir. Amaç, tek bir âyetin tek bir işlevsel unsurunu dahi dışarıda bırakmadan atomik denklemler kurmak ve bunları cebirsel/mantıksal faktörleme kurallarıyla üst denklemlere yükseltmektir.

---

## 1. Temel Aksiyomlar

1. **Kayıpsızlık (Geri-Açılabilirlik) Aksiyomu:** Hiçbir üst denklem, alt denklemlerdeki bilgiyi özetleyerek silemez. Her üst denklem $F$, altındaki $E_1, \dots, E_n$ denklemlerinin **geri-açılabilir (invertible)** bir katlamasıdır:
   $$\text{Açılım}(F) \equiv \bigoplus_{i=1}^{n} E_i$$
   Bir alt âyette geçen hüküm, şart, istisna, sıfat veya illet üst denklem açıldığında geri elde edilemiyorsa o faktörleme geçersizdir.
2. **Aşağıdan Yukarı (Tümevarımsal) İnşa Aksiyomu:** Önce her âyet tekil olarak atomik denklem ($L_0$) biçiminde yazılır. Üst formüller ($L_1 \to L_4$) önceden belirlenmiş konu başlıklarından değil, yalnızca biriken $L_0$ denklemleri arasındaki **ortak terim, çıkarım, şart–sonuç ve simetri** örüntülerinden çıkarılır.
3. **Açık Metin ile Örtük Delâlet Ayrımı Aksiyomu:** Metinde lafzen geçen unsurlar normal biçimde yazılır; Arapça sözdizimi ve belâgat gereği metinde düşürülmüş (*hazf*) veya zorunlu olarak ima edilmiş (*delâletü'l-iktizâ / delâletü'l-işâre*) unsurlar köşeli açı parantezi `⟨...⟩` içinde gösterilir. Böylece metnin kendisiyle yorum/çıkarım asla birbirine karışmaz.
4. **Sıfır Zamir Aksiyomu:** Atomik denklemlerde hiçbir zamir (*o, onlar, bu, şu*) çıplak bırakılmaz; her zamir kendi merciine açık biçimde bağlanır: `x[Merci]`.
5. **Kanonik Ayrıklık Aksiyomu:** İki farklı Kur'ânî kavram (*hamd* vs. *şükür*, *kâfir* vs. *müşrik* vs. *münafık*, *nebî* vs. *resûl*, *kalp* vs. *fuâd*) asla tek bir gevşek değişken altında eritilmez; her biri ayrı kanonik sembol taşır ve aralarındaki ilişki tanım aksiyomuyla (`:=` veya `⊂`) kurulur.

---

## 2. Matematik ve Mantıktan Alınan 8 Disiplin ve Görev Dağılımı

Kur'ân metni yalnızca önermesel doğru–yanlış yargılarından oluşmaz; içinde varlık ilişkileri, emir–yasak normları, değişmez yasalar, zaman katmanları, temsiller ve âyetler arası bağlar vardır. Bu nedenle tek bir mantık sistemi yetersiz kalır; matematiğin sekiz belirli alt disiplini görev sınırları çizilerek usûle alınır:

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
8. **Te'kîd / Tezyîl (`E_i ↻[Tezyîl] E_{i+1}`):** Önceki bölüm genel bir ilâhî yasa veya esmâ mührüyle kapatılır.

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

## 7. Beş Zorunlu Doğrulama Testi ve Çalışma Protokolü

Herhangi bir $L_1$–$L_3$ üst denklemi kesinleşmeden önce şu beş testten geçmek zorundadır:

1. **Kayıpsızlık (Geri-Açılım) Testi:** Üst denklemdeki her sembol tanımına göre açıldığında, kapsadığı her $L_0$ âyetindeki tüm kavramlar, şartlar ve istisnalar eksiksiz geri dönüyor mu? Tek bir unsur bile eksikse faktörleme reddedilir.
2. **Geri-Okuma (Yabancı Okuyucu) Testi:** Sûreyi daha önce hiç okumamış biri, yalnızca $L_1$ ve $L_2$ denklemleri ile aralarındaki geçiş operatörlerini (`⟸[Ta'lîl]`, `⟹[Tefrî']`, `⤏[Denge]`) okuduğunda, "şimdi neden bu geldi?" sorusunu sormadan akışı kesintisiz izleyebiliyor mu?
3. **Katman Saflığı Testi:** Hasımın iddiası (`B_x`), kesin gerçek (`⊤`/`□`) ile aynı düzleme karışmış mı? Metinde açıkça geçen ile dilsel çıkarım (`⟨...⟩`) birbirinden net ayrılmış mı?
4. **Kanonik Tutarlılık Testi:** Aynı kavram sûre boyunca aynı sembolle mi yazılmış? Farklı incelikli kavramlar (*hamd* vs. *şükür* gibi) yanlışlıkla birleştirilmiş mi?
5. **Kapsama ve Süreklilik Testi:** Sûrenin 1. âyetinden son âyetine kadar hiçbir âyet atlanmadan, çakışmadan ve bağsız bırakılmadan $L_0$ ağacına bağlı mı?

### Uygulama Protokolü (Adım Adım İş Akışı)
1. **Metin ve İrâb Tespiti:** Her âyet önce Arapça aslına göre cümle öğelerine, edatlarına ve zamir mercilerine ayrılır.
2. **$L_0$ Kodlaması:** Bölüm 3–5 kurallarına göre âyetin kayıpsız atomik denklemi yazılır.
3. **Bağ Ataması:** Bir önceki $L_0$ ile arasındaki geçiş operatörü (Bölüm 6.1) zorunlu olarak belirlenir.
4. **Organik Faktörleme:** Biriken $L_0$'lar doğal bir kapanışa ulaştığında Bölüm 6.2 kurallarıyla $L_1$ üst denklemi çıkarılır ve Kayıpsızlık Testi'nden geçirilir.
5. **Yukarı Yükseliş:** $L_1$'ler tamamlandıkça $L_2$ makam denklemleri ve nihayet sûrenin $L_3$ Esas Denklemi kurulur.
