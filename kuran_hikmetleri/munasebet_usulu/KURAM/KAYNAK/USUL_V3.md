# Kur'ân-ı Kerîm İçin Üstten Bakış Lisanı: Biçimsel Mantık, İleri Matematik ve İşlem Cebiri Usûlü (Sürüm 3.0)

Bu belge, Kur'ân-ı Kerîm metnini mevzu özetlerine indirmek yerine **kayıpsız, geri-açılabilir, tümevarımsal bir biçimsel mantık ve denklem sistemine** dönüştüren lisanın bütünleşik şartnamesidir. Mimari üç katmandan oluşur:
* **Katman I (Bölüm 1–7 — Mantık Çekirdeği):** Önermesel, çok tipli yüklem, deontik, modal, zamansal mantık, 16 kalıp, 8 geçiş bağı ve 6 temel faktörleme kuralı.
* **Katman II (Bölüm 8–14 — İleri Matematiksel Modelleme):** Yalnızca Katman I'in ifade edemediği dinamik, çok boyutlu, doğrusal olmayan veya topolojik yapılar metinde mevcutsa çağrılan saf kaideler.
* **Katman III (Bölüm 15 — İşlem, Çıkarım ve İndirgeme Cebiri):** Beş çekirdek kural, düzeltilmiş yeniden yazım cebiri, geri alınabilir (*istishâb*) çıkarım, deontik evleviyet aksiyomları, zâhirî çelişki çözümleme algoritması, kesin katlama grameri ve tip-güvenli çapraz birleştirme.

---

## Önceki Taslakta Tespit Edilen Hatalar ve Sürüm 3.0 İlaveleri

| # | Tespit Edilen Kusur / Eksik | Sürüm 3.0 Düzeltmesi ve İlavesi |
| :--- | :--- | :--- |
| **1** | **Yapısal Tekrar ve Sembol Uyuşmazlığı:** Önceki metinde Katman II (Bölüm 8–14) iki kez art arda yapıştırılmıştı; 10.4'te operatör başlıkta $\mathcal{T}$, formülde $\mathcal{R}$ yazılmıştı. | Tekrarlanan Katman II temizlendi; geçmiş dönüştürme operatörü metin boyunca tek biçimde $\mathcal{R}$ (`R_sil`, `R_çevir`) olarak sabitlendi. |
| **2** | **Ç1 (Nakil Kapsamı) Mantık Hatası:** *"s ilâhî söyleyen değilse ayrıca $B_s(\varphi)$"* kuralı yanlıştır; yalancı veya münafık bir söyleyen inanmadığı sözü söyleyebilir ($\neg B_s(\varphi)$). | `Aktar[s](φ)` yalnızca `Söz_s(φ)` çıkarır; içsel inanç (`B_s`) veya samimiyetsizlik (`¬B_s`) ancak metnin ayrıca bildirmesiyle eklenir. |
| **3** | **Ç4 (Sebep–Şart–Mâni) ve Eksik Rükün/İstishâb:** `H(φ) ⟺ Sbb ∧ Şrt ∧ ¬Mni` ifadesi rüknü dışarıda bırakıyor ve mâni zikredilmeyen âyetlerde `¬Mni` varsayımını belirsiz bırakıyordu. | **Rükün–Şart–Sebep–Mâni** ayrımı netleştirildi ve **Varsayılan/Geri Alınabilir Mantık (*İstishâb*, `⊢_d`)** eklendi: aksine âyet gelmedikçe `¬Mni` varsayılan olarak geçerlidir. |
| **4** | **15.2 #2 Sonlanma Ölçüsü Hatası:** *"μ'yü aynı bırakıp izi uzatır"* kuralı sonsuz döngüyü (`A ⟼ B ⟼ A...`) engellemez; matematiksel olarak geçersizdir. | İyi sıralı (*well-founded*) sözlük düzeninde **kesin azalma** (`μ(R) < μ(L)`) şartı kondu; eşdeğerlik dönüşümleri ayrı yönlü olmayan (`≡`) sınıfa alındı. |
| **5** | **15.2 #4 Mübah–İzin (Deontik Mantık) Hatası:** `P(φ) ⟼ ¬O(¬φ)` yalnızca *zayıf izin*dir (farzı da kapsar), *mübah* değildir; ayrıca normal biçim $L_0$'ın belâgat farkını siliyordu. | Zayıf izin (`P_zayıf := ¬F(φ)`) ile **mübah** (`P_mübah := ¬O(φ) ∧ ¬F(φ)`) ayrıldı; `NB(E)` yalnızca salt-okunur karşılaştırma motoru (`≡_NB`) olarak sınırlandı. |
| **6** | **15.3 #14 Nesh Oklarının Ters Yazılması:** Önceki metinde `H₂ ▷ H₁` (*H₂ önce gelir*) ve `H₂ ⤏[nesh] H₁` yazılmıştı; oysa 3.4 ve 3.6'ya göre yönler tam tersidir. | `H₁ ▷ H₂` ($H_1$ önce, $H_2$ sonra) ve `H₁ ⤏[nesh] H₂` ($H_2$, $H_1$'i nesheder) biçiminde düzeltildi; çözüm sırasına **Adım 0 (Katman/Nakil)** ve **Derece/İtibar Ayrımı** eklendi. |
| **7** | **15.2 #3 ve 15.5 #22 Kontrolsüz Birleşme:** Birleşme testi eksen gözetmiyor, `mgu` ise tip ve kanonik ayrıklık denetimi yapmıyordu. | Birleşme testi izdüşüm eksenine (`proj_U`) bağlandı; `mgu` **tip-güvenli ve kanonik-korumalı (`mgu_T`)** kurala çevrildi. |
| **8** | **Yeni Çıkarım Gücü (Deontik Evleviyet & Mukaddime):** Usûl-i Fıkıh'ın temel çıkarım aksiyomları eksikti. | **Mefhûm-ı Muvâfakat (Evleviyet)** (`a ≺ b ∧ F(a) ⊢ F(b)`) ve **Vâcibin Mukaddimesi** (`O(φ) ∧ (φ → ψ) ⊢ O(ψ)`) biçimsel çıkarım kuralları olarak eklendi. |

---

# KATMAN I — MANTIK ÇEKİRDEĞİ

## 1. Temel Aksiyomlar

1. **Kayıpsızlık (Geri-Açılabilirlik) Aksiyomu:** Hiçbir üst denklem, alt denklemlerdeki bilgiyi özetleyerek silemez. Her üst denklem $F$, altındaki $E_1, \dots, E_n$ denklemlerinin **geri-açılabilir (invertible)** bir katlamasıdır:
   $$\text{Açılım}(F) \equiv \bigoplus_{i=1}^{n} E_i$$
   Bir alt âyette geçen hüküm, şart, istisna, sıfat veya illet üst denklem açıldığında geri elde edilemiyorsa o faktörleme geçersizdir.
2. **Aşağıdan Yukarı (Tümevarımsal) İnşa Aksiyomu:** Önce her âyet tekil olarak atomik denklem ($L_0$) biçiminde yazılır. Üst formüller ($L_1 \to L_4$) önceden belirlenmiş konu başlıklarından değil, yalnızca biriken $L_0$ denklemleri arasındaki **ortak terim, çıkarım, şart–sonuç ve simetri** örüntülerinden çıkarılır.
3. **Açık Metin ile Örtük Delâlet Ayrımı Aksiyomu:** Metinde lafzen geçen unsurlar normal biçimde yazılır; Arapça sözdizimi ve belâgat gereği metinde düşürülmüş (*hazf*) veya zorunlu olarak ima edilmiş (*delâletü'l-iktizâ / delâletü'l-işâre*) unsurlar köşeli açı parantezi `⟨...⟩` içinde gösterilir.
4. **Sıfır Zamir Aksiyomu:** Atomik denklemlerde hiçbir zamir (*o, onlar, bu, şu*) çıplak bırakılmaz; her zamir kendi merciine açık biçimde bağlanır: `x[Merci]`.
5. **Kanonik Ayrıklık Aksiyomu:** Farklı incelik taşıyan kavramlar asla tek bir gevşek değişken altında eritilmez; her biri ayrı kanonik sembol taşır ve aralarındaki ilişki tanım aksiyomuyla (`:=` veya `⊂`) kurulur.
6. **Kaide–Misal Ayrımı Aksiyomu:** Hiçbir tekil vaka, özel kavram adı veya tikel içerik, genel usûl kuralının içine sabitlenmez. Usûl yalnızca **soyut yapısal sınıflar** üzerinden konuşur; tikel kavramlar uygulama safhasında parametre olarak yerleşir.
7. **En Sade Yeterli Yapı (Occam) Aksiyomu:** Bir âyet veya âyet grubu Katman I ile kayıpsız temsil edilebiliyorsa Katman II çağrılmaz. İleri bir matematiksel yapı **yalnızca** alt katmanın ifade edemediği bir dinamik, boyut, eşik veya dönüşüm metinde mevcutsa devreye alınır.
8. **Nitel–Yapısal Matematik Aksiyomu:** Türevlerin işareti, büyüme rejimi, çekirdek–görüntü ilişkisi, kafes sıralaması ve topolojik kapsama kesin yapısal bilgilerdir; metnin vermediği yapay sayısal katsayılar ve öznel ağırlıklar sisteme sokulmaz.

---

## 2. Katman I'in Dayandığı 8 Mantık–Matematik Disiplini

| # | Disiplin | Usûldeki Görevi |
| :--- | :--- | :--- |
| **1** | **Çok Tipli Yüklem Mantığı (*Many-Sorted FOL/HOL*)** | Varlıkları tiplerine göre ayırmak (`x :: T`), ilişkileri yüklem/fonksiyon olarak kurmak, niceleyicileri (`∀, ∃, ∃!, ∄`) yönetmek. |
| **2** | **Deontik (Normatif) Mantık** | Teklifî ve vaz'î hükümleri (`O, F, P_mübah, P_zayıf, O⁺, F⁻`), şartlı yükümlülükleri (`O(φ \| ψ)`) ve mazeret/ruhsat istisnalarını (`⊘`) çelişkisiz formülleştirmek. |
| **3** | **Modal ve Epistemik Mantık** | Zorunlu yasaları (`□`), mümkün hâlleri (`◇`), özneye bağlı bilgi/zan farkını (`K_x` vs. `B_x`) ve iradeyi (`W_x`) ayırmak. |
| **4** | **Zamansal Mantık (*Temporal Logic*)** | Olayları zaman katmanlarına (`τ₋, τ₀, τ₊, τ_∞`) yerleştirmek; ardıllık (`▷`) ile tekrarlanan döngüleri (`⟳`) ayırmak. |
| **5** | **Küme, Mereoloji ve Kafes Kuramı** | Grupları (`∈, ⊂`), istisnayı (`∖`), parça–bütün ilişkilerini (`⊑`) ve derece sıralamalarını (`≺, ⪯`) modellemek. |
| **6** | **Kategori Teorisi** | İki alan arasındaki yapı koruyan dönüşümleri (`≅`, $F: \mathcal{C} \to \mathcal{D}$) ve değişmeli diyagramları kurmak. |
| **7** | **Cebirsel Faktörleme ve Yeniden Yazım** | Ortak terim parantezine alma, iz koruyan zincirleme, tanım katlama ve geri-açılabilir indirgemeyi yönetmek. |
| **8** | **Yönlü Hiperçizge Kuramı** | Çoklu âyet bağlarını (*hiperkenar*) temsil etmek ve çizge daraltma ile omurga çıkarmak. |

---

## 3. Tam İşaret Alfabesi ve Operatör Öncelik Hiyerarşisi

### 3.1 Ontoloji, Nitelik ve Mahsusluk
* `↦!` : **Mutlak Mahsusluk (Hasr)** — `X ↦! Y` := $X$ yalnızca $Y$'ye aittir ($\forall z \neq Y,\ \neg(X \mapsto z)$).
* `↦` : **Yönelim / Aidiyet** — münhasırlık iddiası olmaksızın yönelim.
* `X{...}` : **Nitelik / Sıfat Demeti** — $X$ varlığına bağlı sıfat/bağıntı kümesi.
* `::` : **Tip Bildirimi** (`x :: T`), `:=` : **Mahiyet Tanımı**, `≡` : **Mantıksal Özdeşlik**, `≇` : **Mutlak Tenzih / Benzemezlik**.

### 3.2 Önermesel, Niceleyici, Nedensel ve Delil İşaretleri
* `∧` (ve), `∨` (kapsayıcı veya), `⊕` (dışlayıcı ya–ya da), `¬` (değil), `→` (gerçek/genel şart), `⇒` (mantıksal çıkarım / tefrî'), `↔` (gerek ve yeter şart), `⊬` (karşı-olgusal şart: *olsaydı olurdu*).
* `∀` (tümü), `∃` (en az biri), `∃!` (tekillik), `∄` (yokluk / cins nefyi).
* `⊢` (delil/burhan), `⊢_d` (varsayılan/geri alınabilir çıkarım — *istishâb*), `∵` (illet/gerekçe), `⇝` (gaye/hikmet), `⊥` (çelişki/bâtıl), `⊤` (hak/sabit gerçek).

### 3.3 Deontik, Modal, Epistemik ve İrade İşaretleri
* `O(φ)` (zorunlu emir), `F(φ)` (kesin yasak), `P_mübah(φ)` (`¬O(φ) ∧ ¬F(φ)` — serbestlik), `P_zayıf(φ)` (`¬F(φ)` — yasak olmama), `O⁺(φ)` (teşvik/mendup), `F⁻(φ)` (sakındırma/mekruh).
* `O(φ | ψ)` (şartlı yükümlülük), `⊘(φ | γ)` (ruhsat/istisna), `H₁ ⤏[tür] H₂` ($H_2$, $H_1$'i takyîd, tahsîs veya nesh eder).
* `□(φ)` (zorunluluk / değişmez yasa), `◇(φ)` (imkân), `K_x(φ)` (kesin bilgi), `B_x(φ)` (zan/kanaat), `Söz_x(φ)` (beyan/iddia), `W_x(φ)` (irade), `G(φ)` (gayb), `Req(x ↦ y, φ)` (yakarış/talep).

### 3.4 Zamansal, Küme, Kapsam ve Belâgat İşaretleri
* `τ₋ / τ₀ / τ₊ / τ_∞` (mâzî / hâl / geçiş-hesap / ebedî son), `▷` (kronolojik ardıllık: $e_1$ önce, $e_2$ sonra), `∥` (eşzamanlılık), `⟳` (tekrarlanan döngü).
* `⟐(A) ⊢ B` (kasem/yemin), `≅` (yapı koruyan temsil), `⋈` (mukabele/zıt simetri), `∖` (küme farkı/istisna), `⊑` (parça–bütün), `≺` (derece sıralaması), `↑! / ↑!!` (te'kid derecesi), `?⊥ / ?⊤` (retorik red/onay).
* `Aktar[s](φ)` (nakil kapsamı), `⟦ψ⟧` (ara cümle / itirâz parantezi), `⌘[A B B′ A′]` (ayna/kiazm yapısı).

### 3.5 Operatör Öncelik Sırası (Yüksekten Düşüğe)
1. Parantez, Kapsam ve Nitelik: `X{...}`, `x[Merci]`, `x :: T`, `⟨...⟩`, `⟦...⟧`, `Aktar[s](...)`
2. Tekil Operatörler: `¬`, `□`, `◇`, `O`, `F`, `P_*`, `K_x`, `B_x`, `Söz_x`, `W_x`, `G`, `τ_*`, `↑!`
3. Küme, Derece ve Yönelim: `∈`, `⊂`, `∖`, `⊑`, `≺`, `↦`, `↦!`, `≅`, `≇`
4. Mantıksal Bağlaçlar: `∧` → `∨`, `⊕` → `→`, `⊬`, `↔`
5. Çıkarım, Gerekçe ve Yapısal Bağlar: `∵`, `⇝`, `▷`, `∥` → `⊢`, `⊢_d`, `⇒`, `⋈`, `⤏`, `:=`, `≡`, `⟼`

---

## 4. Değişken / Sabit / Operatör Ayrımı (Dört Sınıf Kuralı)

1. **Sınıf I — Ontolojik Sabitler:** Temel varlık türleri, özel şahıs/topluluk sabitleri ve değer kökleri kendi kanonik adlarıyla büyük harfle yazılır.
2. **Sınıf II — Bağıntı ve Eylem Yüklemleri:** Tekli nitelikler (`P(x)` veya `X{...}`) ve çoklu yönlü ilişkiler (`R(x → y)`) olarak kurulur; tek başına yüzen kelime bırakılmaz.
3. **Sınıf III — Yapısal Edatlar ve Kipler:** Tahsis, şart, gerekçe, amaç, istisna, yemin, emir–nehiy–ruhsat, te'kid ve retorik sorular bütünüyle Bölüm 3 operatörlerine çevrilir.
4. **Sınıf IV — Kanonik Sözlük ve Ayrıklık:** Her kavram metin boyunca tek bir kanonik adla anılır; ince anlam farkı taşıyan yakın kavramlar asla tek değişkende birleştirilmez, aralarındaki ilişki `⊂` veya `:=` ile kaydedilir.

---

## 5. On Altı Yapısal Kalıp Şablonu

| # | Kalıp | Biçimsel Şablon | Kural |
| :--- | :--- | :--- | :--- |
| **1** | Hasr / Mahsusluk | `A ↦! B` | Dışlanan alternatifler zımnen `¬` alır. |
| **2** | Esmâ / Nitelik Mühürlemesi (*Tezyîl*) | `E_i ∵ X{N₁, N₂}` | Son fâsıla, hükmün ontolojik gerekçesi olarak bağlanır. |
| **3** | Şartlı Hüküm | `O(φ \| ψ)` veya `F(φ \| ψ)` | Şart hükümden koparılmaz. |
| **4** | Ruhsat ve İkame | `O(φ) ∧ ⊘(φ \| γ) ∧ O(φ' \| γ)` | Genel emir, mazeret ve ikame tek kapalı formdadır. |
| **5** | İstisnâ (Muttasıl / Munkatı') | `∀x ∈ (A ∖ B) : P(x)` / `E₁ ∧ [Lâkin] E₂` | Muttasılda $B \subset A$ şartı aranır. |
| **6** | Kasem (Yemin) | `⟐(A₁…Aₙ) ⊢ ↑!(B)` | Müksemün-bih ile cevâbü'l-kasem delil bağıyla bağlanır. |
| **7** | Mesel / Temsil | `Yapı(Alan₁) ≅ Yapı(Alan₂)` | Nesne değil bağıntı ağı fonktör olarak taşınır. |
| **8** | Tarihî Anlatı (Kıssa) | `τ₋: (e₁ ▷ … ▷ eₙ) ⊢ □(İlke)` | Olay zinciri kayıpsız yazılır; çıkan yasa bağlanır. |
| **9** | İtiraz ve Reddiye (*Cedel*) | `Aktar[Hasım](φ) ⊢[Red] ¬φ ∧ (D ⊢ ψ)` | Hasımın sözü nakil kapsamından dışarı sızmaz. |
| **10** | Retorik İstifham | `?⊥(φ) ⇒ ¬φ` / `?⊤(φ) ⇒ φ` | Hem soru biçimi hem kesin hüküm korunur. |
| **11** | Mukabele (Zıt Simetri) | `[G₁ : V₁ → R₁] ⋈ [G₂ : V₂ → R₂]` | Eksik simetri `⟨örtük⟩` ile işaretlenir. |
| **12** | Olgusal Delil | `OlgusalDüzen(x) ⊢ Hüküm` | Betimleme değil istidlâl bağı kurulur. |
| **13** | Talep / Dua | `Req(x ↦ y, φ) ∵ Gerekçe` | Yönelim ve vesile birlikte kaydedilir. |
| **14** | Eylem–Karşılık (Zaman Sıçraması) | `τ₀: Eylem(x) → τ_∞: Karşılık(x)` | İki farklı zaman katmanı açık işaretlenir. |
| **15** | İltifat (Hitap Kayması) | `Hitap(k₁ → k₂) : E` | Şahıs/hitap değişimi kayda alınır. |
| **16** | Çapraz Tahsîs / Takyîd | `E(S₁:a₁) ⤏[tür] E(S₂:a₂)` | Sûre içi veya sûreler arası güncelleme bağı. |

---

## 6. Bağlantı Operatörleri, Faktörleme Kuralları ve Beş Katman ($L_0 \to L_4$)

### 6.1 Sekiz Zorunlu Geçiş Bağı
Her ardışık denklem çifti ($E_i, E_{i+1}$) arasında en az biri atanır:
1. `⟸[Ta'lîl]` (gerekçelendirme)
2. `⟹[Tefrî']` (zorunlu sonuç/hüküm)
3. `⊐[Tafsîl]` / `⊏[İcmâl]` (açılım / toplama)
4. `⋈[Mukâbele]` (zıt kutup)
5. `⊢[İstidlâl]` (delil–iddia)
6. `⤏[Denge]` (takyîd/ruhsat/dengeleme)
7. `≅[Temsîl]` (mesel/kıssa ile somutlama)
8. `⟲[Tezyîl]` (genel yasa veya nitelikle mühürleme)

### 6.2 Yedi Cebirsel Faktörleme Kuralı
1. **Ortak Terim Parantezine Alma:** $P(a_1) \wedge \dots \wedge P(a_n) \;\Longrightarrow\; P(\{a_1, \dots, a_n\})$.
2. **İz Koruyan Zincirleme:** $(A \to B) \wedge (B \to C) \;\Longrightarrow\; A \xrightarrow{[B]} C$.
3. **Bölünme / Kutuplaşma Katlaması:** $(\psi \to R_1) \wedge (\neg\psi \to R_2) \;\Longrightarrow\; \text{Ayrım}(\psi : R_1 \bowtie \neg\psi : R_2)$.
4. **Fonktörel Yasa Çıkarma:** $\bigwedge_{k \in K} \text{Vaka}_k(X_k \to Y_k) \;\Longrightarrow\; \square(\forall x \in K : X(x) \to Y(x))\ [\text{Şahitler: } K]$.
5. **Şart–İstisna Kapalı Formu:** $O(\varphi) \wedge \oslash(\varphi \mid \gamma) \wedge O(\varphi' \mid \gamma) \;\Longrightarrow\; O_{\text{tam}}(\varphi \mid \neg\gamma ;\ \varphi' \mid \gamma)$.
6. **Tanım Katlaması:** $X := \{v_1 \wedge \dots \wedge v_m\}$ ve $(\{v_1 \wedge \dots \wedge v_m\} \to R) \;\Longrightarrow\; X \to R$.
7. **Halka ve Ayna (Kiazm) Katlaması (Ç3):** $\sigma(A)=A',\ \sigma(B)=B'$ olmak üzere $A \cdot B \cdot B' \cdot A' \;\Longrightarrow\; \text{Ayna}(\sigma;\ \text{Eksen}(B,B');\ A)$; halka için $A \cdot \text{İç} \cdot A' \;\Longrightarrow\; \text{Çerçeve}(\sigma;\ \text{İç})$.

### 6.3 Beş Katmanlı Denklem Mimarisi
* **$L_0$ (Atomik Âyet):** Tek âyetin kayıpsız formülü + zamir çözümü + `⟨örtük⟩`.
* **$L_1$ (Yerel Mantık Bloğu):** 2–8 âyetin ilk faktörlemesi ve geçiş bağları.
* **$L_2$ (Makam Denklemi):** Bir argüman, hüküm veya anlatı bütünlüğünün kapalı denklemi.
* **$L_3$ (Sûre Esas Denklemi):** Sûrenin tüm $L_2$ makamlarını, baz eksenlerini ve dinamik sistemini toplayan tek omurga.
* **$L_4$ (Mushaf Denklem Ağı):** Sûreler arası çapraz tahsîs, ortak yasa ve tensör kesitlerinin birleşimi.

---

## 7. Sekiz Zorunlu Doğrulama Testi

1. **Kayıpsızlık (Geri-Açılım) Testi:** Üst denklem açıldığında alt $L_0$'lardaki tüm kavram, şart, istisna ve kalanlar eksiksiz geri dönmelidir.
2. **Geri-Okuma Testi:** Metne yabancı biri yalnızca $L_1$–$L_2$ denklemleri ve geçiş operatörleriyle akışı kopukluk hissetmeden izleyebilmelidir.
3. **Katman ve Nakil Saflığı Testi:** `Aktar[s](φ)` içindeki söz dışarı sızmamış; `⟨örtük⟩` ile açık metin karışmamış olmalıdır.
4. **Kanonik Tutarlılık Testi:** Aynı kavram aynı sembolle yazılmalı, ince fark taşıyan kavramlar birleştirilmemelidir.
5. **Kapsama ve Süreklilik Testi:** 1. âyetten son âyete kadar boşluk, çakışma ve bağsız düğüm bulunmamalıdır.
6. **Yapısal Zorunluluk (Occam) Testi:** Katman II sembolü kaldırıldığında gerçek bir dinamik, boyut veya kısıt kaybolmuyorsa o sembol çıkarılır.
7. **Kaide Saflığı Testi:** Hiçbir tikel örnek genel kaide yerine konulmamış olmalıdır.
8. **Çelişkisizlik ve Sonlanma Testi:** Kullanılan yazım kuralları kesin azalan sonlanma ölçüsüne uymalı, zâhirî çatışmalar Bölüm 15.4 protokolünden geçirilmiş olmalıdır.

---

# KATMAN II — İLERİ MATEMATİKSEL MODELLEME

## 8. En Umumi Senaryolar İçin Matematiksel Seçim Matrisi

| # | Genel Yapısal Senaryo | Çağrılacak Matematik Dalı | Temel Operatör / Yapı |
| :--- | :--- | :--- | :--- |
| **1** | Statik varlık, sıfat, hüküm, şart, delil veya zıtlık ilişkisi | **Katman I (Mantık Çekirdeği)** | `↦!`, `→`, `O/F/P`, `□`, `⊢`, `⋈` |
| **2** | Bir durumun sürekli **veya** kesikli sıçramayla artması/azalması | **Zaman Ölçekleri Kalkülüsü** ($\mathbb{T}$) | $f^\Delta(t) \gtrless 0$, $f^{\Delta\Delta}$ |
| **3** | Çok etkenli bir çıktının tek girdideki değişime duyarlılığı | **Çok Değişkenli Analiz (Kısmî Türev)** | $\frac{\partial y}{\partial u_i}$ |
| **4** | İhmal edilemeyecek en küçük birimin kesin korunumu | **Standart Dışı Analiz** (${}^*\mathbb{R}$) | $d\alpha \neq 0 \Rightarrow \Phi(d\alpha) \neq 0$ |
| **5** | Aralık boyunca ağırlıklı toplam, sıfırlanma veya geçmiş dönüşümü | **Ölçü ve İntegral Operatörleri** | $\int_{\mathbb{T}} \mathcal{W}\cdot \phi\,\Delta t$, $\mathcal{R}[\int]$ |
| **6** | Bağımsız eksenler, aynı etkinin zıt sonuçları, boşa düşenler kümesi | **Lineer Cebir** | $\{\vec{e}_k\}$, $\perp$, $\lambda_x$, $\ker(T)$, $\text{proj}_U$, $\text{rank}$ |
| **7** | Üç veya daha fazla bağımsız eksenin ($n \ge 3$) aynı ilişkide kesişmesi | **Çoklu Lineer Cebir (Tensörler)** | $\mathcal{T}^{i_1\dots i_p}_{j_1\dots j_q}$, `Kesit`, `Daralt` |
| **8** | En baskın tek koşul ve sıralı eşik zincirlerinin doğrusallaştırılması | **Tropikal Cebir (*Max/Min-Plus*)** | $(\oplus_T=\max/\min,\ \otimes_T=+)$ |
| **9** | İki veya daha fazla durumun birbirini karşılıklı değiştirmesi | **Birleşik Dinamik Sistemler** | $\{ s_1^\Delta = F_1(\cdot),\ s_2^\Delta = F_2(\cdot) \}$ |
| **10** | Süperpozisyon kırılması, geri besleme, eşik, geri dönüşsüzlük, dallanma | **Gayrı Lineer Dinamikler** | `↻⁺ / ↻⁻ / ↻⁰`, $s > s_{\text{kr}}$, `⋔` |
| **11** | İç içe kapsam bölgeleri veya sıralı dereceli üyelik | **Bölge Cebiri (*Locale*) ve Kafes-Bulanık Mantık** | Heyting kafesi $L$, $\mu_A(x) \in L$ |
| **12** | Hiyerarşik yakınlık ölçümü ve farklı katmanlarda yapı tekrarı | **Ultrametrik (*p-Adik*) ve Öz-Benzerlik** | $d_p(x,y)$, $L_k \simeq L_{k+m}$ |
| **13** | İki alan arasında yapı koruyan aktarım ve denklik indirgemesi | **Kategori Teorisi ve Bölüm Yapıları** | $F: \mathcal{C} \to \mathcal{D}$, $S / \sim$ |
| **14** | Çoklu aktör etkileşimi ve kısıt altında denge yörüngesi | **Oyun Teorisi ve Varyasyonel Kısıt** | $\Omega(x)$, $\delta S = 0$, $u_i^* \leftrightarrow \bar{s}$ |

---

## 9. Değişken Rolleri, Uzaylar ve Sınır Kaideleri

Katman II'ye geçilen her denklemde terimler altı rolden birine atanır:
* **Mutlak Sabitler ($C$):** Hiçbir değişkenle değişmeyen ontolojik dayanaklar ($\Delta C \equiv 0$).
* **Kontrol / Bağımsız Değişkenleri ($u$):** Özgür irade veya karar merciince belirlenen girdiler.
* **Durum Değişkenleri ($s(t)$):** Sistemin $t$ anındaki birikimli iç hâli.
* **Bağımlı Çıktılar ($y$):** $y = f(u, s; \theta)$.
* **Bağlam Parametreleri ($\theta$):** Zaman, mekân, mazeret, bilgi erişimi gibi dış koşullar.
* **Başlangıç ve Sınır Koşulları ($s(t_0),\ \Omega$):** Başlangıç hâli ve geçerli imkân/kısıt uzayı.

---

## 10. Analitik ve Dinamik Kaideler

* **10.1 Zaman Ölçekleri Kalkülüsü ($\mathbb{T},\ f^\Delta$):** Sürekli aralıkta $f^\Delta = \frac{df}{dt}$, kesikli adımda $f^\Delta(t_k) = f(t_{k+1}) - f(t_k)$; ikinci mertebe $f^{\Delta\Delta}$ ivmelenmeyi kaydeder.
* **10.2 Kısmî Türev ($\frac{\partial y}{\partial x_i}$):** Diğer etkenler sabitken tek girdinin marjinal etkisi ($\frac{\partial y}{\partial x_i} > 0$: pozitif etki; $= 0$: duyarsızlaşma).
* **10.3 Standart Dışı Analiz ($d\alpha \in {}^*\mathbb{R}$):** $\forall d\alpha \neq 0 \Rightarrow \text{Ölçü}(d\alpha) \neq 0$ (en küçük birimin ihmal edilememesi).
* **10.4 Ağırlıklı Birikim İntegrali ve Dönüşüm Operatörü ($\mathcal{R}$):**
  $$I_{[t_a, t_b]} = \int_{t_a}^{t_b} \mathcal{W}(\vec{c}(t)) \cdot \phi(t)\,\Delta t$$
  Geçerlilik ağırlığı $\mathcal{W}=0$ olduğunda birikim sıfırlanır; geçmiş bölgeyi dönüştüren operatörler $\mathcal{R}_{\text{sil}}$ ve $\mathcal{R}_{\text{çevir}}$ integralin önüne yazılır; etkisi süren birikimlerde üst sınır açık bırakılır.

---

## 11. Cebirsel ve Çok Boyutlu Kaideler

* **11.1 Lineer Cebir:** Bağımsız baz eksenleri ($\{\vec{e}_k\}$), ikame edilemezlik için dikgenlik ($\perp$), aynı etkenin farklı özne tiplerinde zıt sonuç vermesi için özdeğer işareti ($T(\vec{v}_k) = \lambda_k \vec{v}_k$), boşa düşenler kümesi için çekirdek ($\ker(T)$), inşa alanı için görüntü ($\text{Im}(T)$), tek eksen çekimi için dik izdüşüm ($\text{proj}_U$), bağımsız yeni ilke denetimi için $\text{rank}$.
* **11.2 Genel $(p,q)$-Tensör ($\mathcal{T}^{i_1\dots i_p}_{j_1\dots j_q}$):** Alt indeksler koşul/girdi, üst indeksler hüküm/çıktı eksenleridir. `Kesit` sabit koşuldaki tikel denklemi çeker; `Daralt` bir indeks üzerinden ortaklaştırma yaparak derece düşürür ve değişmez üst ilke üretir.
* **11.3 Tropikal Cebir:** Baskın tek şart ve eşik zincirleri için $a \oplus_T b := \max(a,b)$ (veya $\min$), $a \otimes_T b := a + b$.
* **11.4 Soyut Cebir ve Bölüm Yapısı ($S / \sim$):** Değişmelilik, tersinirlik ve etkisiz eleman kontrol edilir; aynı yapısal işlevi gören denklik sınıfları kayıpsız biçimde bölüm elemanına indirgenir.

---

## 12. Gayrı Lineer Dinamikler ve Etkileşim Sistemleri

* **12.1 Birleşik Sistemler:** Karşılıklı etkileşen durumlar $\{s_1^\Delta = F_1(\cdot),\ \dots,\ s_k^\Delta = F_k(\cdot)\}$ tek sistemde tutulur.
* **12.2 Ölçeklenme ve Asimetri:** $f(a+b) \neq f(a)+f(b)$ (süperlineer katlanma) ve $f^+ \neq -f^-$ (işaret asimetrisi) açıkça işaretlenir.
* **12.3 Geri Besleme:** `↻⁺` (yükselten pozitif), `↻⁻` (yıkıcı pozitif), `↻⁰` (dengeleyici negatif).
* **12.4 Eşik, Histerezis ve Çatallanma:** $s > s_{\text{kr}}$ faz geçişi; $t \ge t_{\text{kapı}}$ noktasında $\mathcal{R}^{-1}$'in kapanması (geri dönüşsüzlük); kontrol parametresi $\beta > \beta_c$ eşiğinde çatallanma (`⋔`): $X \xrightarrow{\beta > \beta_c} X_1 \bowtie X_2$.
* **12.5 Aktör–Topluluk Etkileşimi:** Bireysel karar $u_i$ ile topluluk durumu $\bar{s}$ arasındaki çift yönlü stratejik bağlılık.

---

## 13. Topolojik, Dereceli, Hiyerarşik, Kategorik ve Varyasyonel Kaideler

* **13.1 Bölge Cebiri (*Locale / Heyting*):** Noktasal sınır yerine kapsam ($U \le V$), kesişim ($U \wedge V$), birleşim ($U \vee V$) ve göreli tümleme ($U \Rightarrow V$).
* **13.2 Kafes-Değerli Dereceli Üyelik:** Yapay sayı atamadan sıralı soyut kafes $(L, \preceq)$ üzerinde $\mu_A(x) \in L$.
* **13.3 Ultrametrik Yakınlık ve Öz-Benzerlik:** Ağaçta en derin ortak üst-düğüm mesafesi $d_p(x,z) \le \max(d_p(x,y), d_p(y,z))$; farklı katmanlarda aynı yapının tekrarı $L_k \simeq L_{k+m}$.
* **13.4 Kategori Teorisi:** İlişki ağı aktarımı $F: \mathcal{C} \to \mathcal{D}$, $F(g \circ f) = F(g) \circ F(f)$ ve değişmeli diyagramlar.
* **13.5 Kısıt Uzayı ve Varyasyonel Denge:** $\varphi \in \Omega(x)$; sınır zorlandığında kısıt gevşetme $\Omega \to \Omega'$; iki uç arasında denge yörüngesi $\delta S = 0$.

---

## 14. Katman II Operatör Özeti ve Yükseltme

| Sembol | Görevi |
| :--- | :--- |
| `C / u / s / y / θ / Ω` | Sabit / kontrol / durum / çıktı / bağlam / kısıt uzayı |
| `f^Δ, f^{ΔΔ}`, `∂y/∂x_i`, `dα ∈ *ℝ` | Zaman ölçeği türevi, kısmî duyarlılık, sonsuz küçük |
| `∫_T W·φ Δt`, `R_sil / R_çevir` | Ağırlıklı birikim ve geçmiş dönüşüm operatörleri |
| `{e_k}, ⟂, λ_x, ker, Im, proj_U, rank` | Lineer cebir ayrıştırma ve bağımsızlık araçları |
| `T^{i...}_{j...}`, `Kesit`, `Daralt` | Genel $(p,q)$-tensör ve derece düşürme |
| `(⊕_T, ⊗_T)`, `S / ~`, `F: C → D` | Tropikal cebir, bölüm yapısı ve fonktör |
| `↻⁺ / ↻⁻ / ↻⁰`, `s > s_kr`, `⋔` | Geri besleme, eşik/faz geçişi ve çatallanma |
| `μ_A(x) ∈ L`, `d_p`, `δS = 0` | Kafes üyeliği, ultrametrik yakınlık ve kısıtlı denge |

---

# KATMAN III — İŞLEM, ÇIKARIM VE İNDİRGEME CEBİRİ

## 15. İşlem, Çıkarım ve Çözümleme Kaideleri

Bu katmandaki her madde bir **çıkarım, indirgeme veya çelişki çözümleme kuralıdır**; adlandırma veya etiket yoktur. Tek yönlü yazım oku `⟼` her adımda tersinir bir iz (`⊳ iz`) bırakır.

### 15.1 Beş Çekirdek Kural (Düzeltilmiş)

**Ç1. Nakil Kapsamı (`Aktar[s](φ)`).** Bir söyleyenin aktarılan sözünü dış doğruluk katmanından yalıtan kapsam operatörüdür:
* **Sızmama:** `Aktar[s](φ) ⊬ φ` (kapsam içi önerme dışarıda kesin gerçek olarak okunmaz).
* **Beyan Çıkarımı (İnanç Varsayımı Yok):** `Aktar[s](φ) ⊢ Söz_s(φ)`. Söyleyenin buna gerçekten inanıp inanmadığı (`B_s(φ)` veya `¬B_s(φ)`) **otomatik çıkarılmaz**; ancak metinde ayrıca kanıtlanırsa eklenir.
* **İlâhî Takrîr ile Kapsamdan Çıkış:** `Aktar[s](φ) ∧ Takrîr(Allah, φ) ⟼ φ ⊳ onay`.
* **İç İçe Derinlik:** `Aktar[s₁](Aktar[s₂](φ))` derinliği 2'dir; her katman kendi doğruluk sınırını korur ve onaysız dışarı çıkmaz.

**Ç2. Ara Cümle Parantezi (`⟦ψ⟧`).** `A ⟦ψ⟧ ⇒ B` ifadesi `(A ⇒ B) ∧ ψ` olarak ayrıştırılır; `ψ` ana çıkarım zincirinin öncülü olmaz (`Zincir(A ⟦ψ⟧ B) = Zincir(A B) ⊎ {ψ}`). Açılımda `ψ` tam konumuna geri döner.

**Ç3. Halka ve Ayna (Kiazm) Katlaması.** $\sigma$ yapısal eşleme olmak üzere `σ(A) = A′`, `σ(B) = B′` ise:
* `A · B · B′ · A′ ⟼ Ayna(σ; Eksen(B, B′); A) ⊳ sıra`
* `A · İç · A′ ⟼ Çerçeve(σ; İç) ⊳ sıra`

**Ç4. Vaz'î Hüküm Dörtlüsü (Rükün – Sebep – Şart – Mâni) ve Varsayılan Geçerlilik (*İstishâb*).**
* Bir normatif hükmün doğuşu ve geçerliliği dört ayrı bileşene ayrılır:
  * **Sebep (`Sbb`):** Hükmü tetikleyen durum.
  * **Şart (`Şrt`):** Hükmün dışsal ön koşulu.
  * **Rükün (`Rkn`):** Fiilin özsel iç bileşeni (eksikse fiil *bâtıl* olur).
  * **Mâni (`Mni`):** Hükmün doğuşunu baştan engelleyen durum (`Mni ⇒ ¬H`; ruhsattan farklıdır, ruhsatta hüküm doğar ama ağırlığı `⊘(φ | γ)` ile kalkar).
* **Kapalı Norm Kuralı:** `O(φ | Sbb ∧ Şrt ∧ ¬Mni)` ve fiilin geçerliliği `Sahîh(φ) ↔ Rkn(φ) ∧ Şrt(φ) ∧ ¬Mni`.
* **Varsayılan Çıkarım (*İstishâb* — `⊢_d`):** Bir âyette mâni veya tahsîs zikredilmemişse `⊢_d ¬Mni` varsayılan olarak yürür; başka bir âyet açık bir `Mni` veya `γ` getirdiğinde geri alınabilir (*defeasible*) biçimde güncellenir (`⤏`).

**Ç5. Usûlî Daraltma ve Deontik Çıkarım Aksiyomları.**
* **Âmm–Hâss (Tahsîs):** `P(K) ∧ ¬P(K′)` ve `K′ ⊂ K` `⟼ P(K ∖ K′) ⊳ tahsîs`.
* **Mutlak–Mukayyed (Takyîd):** `H(x) ∧ H(x | k)` ve sebep ile hüküm aynı ise `⟼ H(x | k) ⊳ takyîd`. Sebep veya hüküm farklıysa indirgeme yapılmaz.
* **Evleviyet (*Mefhûm-ı Muvâfakat*):** `(a ≺ b) ∧ F(a) ⊢ F(b)` (daha hafifi yasaksa ağırı evleviyetle yasaktır) ve `(a ≺ b) ∧ P_zayıf(b) ⊢ P_zayıf(a)`.
* **Vâcibin Mukaddimesi:** `O(φ) ∧ □(φ → ψ) ⊢ O(ψ)` (zorunlu bir fiilin tek zorunlu ön şartı da zorunludur).

### 15.2 Düzeltilmiş Yeniden Yazım Cebiri (1–8)

| # | Kural | Biçim | Kesin Şart ve Etki |
| :--- | :--- | :--- | :--- |
| **1** | **Yazım Biçimi** | `L ⟼[ad; şart] R ⊳ iz` | Her indirgeme açık şartlı ve tersinir izlidir. |
| **2** | **Kesin Sonlanma Ölçüsü** | `μ(E) = (kural_ağırlığı, atom_sayısı, derinlik)` | Her tek yönlü `⟼` adımı iyi sıralı sözlük düzeninde `μ`'yü **kesin olarak azaltır** (`μ(R) < μ(L)`). `μ`'yü azaltmayan biçimsel dönüşümler `⟼` ile değil, yönsüz eşdeğerlik (`≡`) ile yazılır; böylece sonsuz döngü imkânsızdır. |
| **3** | **İzdüşüm-Kapsamlı Birleşme** | `E ⟼ E₁, E ⟼ E₂ ⇒ proj_U(E₁) ⟼* F, proj_U(E₂) ⟼* F` | Aynı eksen (`proj_U`) içinde birleşmeyen kural çifti reddedilir; farklı eksenlerdeki paralel okumalar korunur. |
| **4** | **Salt-Okunur Normal Biçim** | `E₁ ≡_NB E₂` | Yalnızca iki denklemin mantıksal eşdeğerliğini veya çatışmasını sınamak için kullanılır; $L_0$'ın üzerine yazılmaz. `F(φ) ≡_NB O(¬φ)`, `P_zayıf(φ) ≡_NB ¬F(φ)`, `P_mübah(φ) ≡_NB ¬O(φ) ∧ ¬F(φ)`. |
| **5** | **Tersinir İz Monoidi** | `iz(E ⟼ E′) = r · iz(E)` | İz, uygulanan kural adlarının ve düşülen parametrelerin kelimesidir; ters fonksiyon için yeterli bilgiyi taşır. |
| **6** | **Enjektif Ters Yazım** | `R ⟻[ad; iz] L` | `Aç(Katla(L), iz) = L` şartı sağlanmıyorsa o yazım kuralı yasaktır. |
| **7** | **Bağlama Bağlı Yazım** | `L ⟼_θ R` | Kural yalnızca geçerli bağlam kümesi `θ ∈ Θ(kural)` içinde yürür. |
| **8** | **Bileşke Kuralı** | `(⟼₁ ; ⟼₂)` | İki kesin azalan ve tersinir adımın bileşkesi de kesin azalan ve tersinirdir. |

### 15.3 Sekiz Adımlı Zâhirî Çelişki Çözümleme Protokolü (9–16)

İki denklem ($E_1, E_2$) normal biçimde çatışır görünürse (`E₁ ∧ E₂ ⊢_NB ⊥`), çözüm **değişmez şu sırayla** yürür:

| # | Adım | Denetim Sorusu | Sonuç |
| :--- | :--- | :--- | :--- |
| **9** | **Adım 0 — Katman / Nakil** | Biri `Aktar[s](φ)` içinde veya `⟨örtük⟩` iken diğeri açık hüküm mü? | Evetse doğruluk katmanları ayrıdır; çatışma yoktur. |
| **10** | **Adım 1 — Tahsîs** | Ç5 Âmm–Hâss (`K′ ⊂ K`) uygulanabiliyor mu? | Evetse `P(K ∖ K′)` tek denkleme iner. |
| **11** | **Adım 2 — Takyîd** | Ç5 Mutlak–Mukayyed (aynı sebep ve hüküm) uygulanabiliyor mu? | Evetse `H(x \| k)` tek denkleme iner. |
| **12** | **Adım 3 — İtibar / Derece** | Biri farklı eksende (`proj_{U₁}` vs `proj_{U₂}`) veya farklı derecede (`O` vs `O⁺`, `F` vs `F⁻`) mi? | Evetse eksen/derece ayrıştırılır; çatışma kalkar. |
| **13** | **Adım 4 — Bağlam ($\theta$)** | `θ₁ ≠ θ₂` ve `Θ₁ ∩ Θ₂ = ∅` (ör. hazar/sefer, barış/savaş, zaruret) mi? | Evetse iki denklem ayrık bağlamlarda birlikte geçerlidir. |
| **14** | **Adım 5 — Zaman / Tedrîc ($\tau$)** | `τ₁ ≠ τ₂` (dünya–ahiret veya tedrîcî aşamalar) mı? | Evetse iki denklem zaman ekseninde ardışıktır (`▷`). |
| **15** | **Adım 6 — Nesh** | `H₁ ▷ H₂` ($H_1$ önce, $H_2$ sonra) ve açık kaldırma delili var mı? | Evetse `H₁ ⤏[nesh] H₂` kaydı düşülür. |
| **16** | **Adım 7 — Tevakkuf** | Hiçbir adım çözmedi mi? | `Çat*(E₁, E₂)` işaretlenir; iki denklem de **silinmeden** muhafaza edilir. |

### 15.4 Kesin Katlama Grameri (17–22)

| # | Kural | Biçim ve Şart |
| :--- | :--- | :--- |
| **17** | **Düğüm Grameri** | `Düğüm ::= Atom ∣ (kural, çocuklar, kalan, iz)` ve `çocuklar ::= Düğüm⁺`. |
| **18** | **Tek Kural Şartı** | Her katlama düğümünde tek kural uygulanır; iki kuralın kaynaşması yasaktır. |
| **19** | **Kalan Cebiri** | `x = üst ⊎ kalan`; kuralın kapsamadığı her unsur `kalan` alanına yazılır, `Aç(Katla(x)) = x` tam sağlanır. |
| **20** | **Katman Disiplini** | `L_k` düğümünün çocukları kural olarak `L_{k-1}`dendir; tek bir alt birimin doğrudan üst katmana taşınması yalnızca açık `Yükselt(L_{k-1} → L_k)` kimlik düğümüyle yapılır. |
| **21** | **Yorum Yasağı** | `Atom(üst) ⊆ ⋃ Atom(çocuk)`; yeni sembol yalnızca `:=` tanım katlamasıyla ve tam açılımıyla girebilir. |
| **22** | **Kanonik Katlama Denetimi** | Aynı atom kümesi için iki farklı geçerli katlama ağacı kurulursa her ikisi de saklanır ve aralarındaki dönüşüm (`≡_NB` veya farklı `proj_U`) açıkça yazılır. |

### 15.5 Tip-Güvenli Çapraz Birleştirme ve Hiperkenar İndirgemesi (23–26)

| # | Kural | Biçim | Etki |
| :--- | :--- | :--- | :--- |
| **23** | **Tip-Güvenli Birleştirme** | `σ = mgu_T(t₁, t₂)` | Yalnızca uyumlu tipteki (`T₁ ⊑ T₂`) değişkenler birleştirilir; iki farklı kanonik sabit (Aksiyom 5) asla birleştirilemez. |
| **24** | **α-Denklik** | `E ≡_α E′` | Bağlı değişken adları kanonik sözlüğe göre standardize edilir. |
| **25** | **Hiperkenar Daraltma** | `{E₁, …, Eₙ} ⇉ F` | Tüm öncüller sağlandığında tek düğüme iner; tek öncül eksikse daraltma kilitlenir. |
| **26** | **Asgarî Destek** | `Destek(F) = min {S ⊆ Atom : S ⊢ F}` | Her üst denklemin dayandığı en küçük zorunlu atom kümesi izde tutulur; gereksiz öncül yığılması önlenir. |
