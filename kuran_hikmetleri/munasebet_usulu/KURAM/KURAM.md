# KAYIPSIZ KATLAMA USULÜ

## Girizgâh

Bir sûrenin içinde hüküm, bağ ve gaye diye üç türlü kayıt bulunur. Bunların sayısı çoktur; çokluk içinde hiçbirini düşürmeden, hiçbirini uydurmadan ve her birine geri dönebilecek hâlde saklamak ister isek elimizde tek yol vardır: kayıtları **kat kat toplamak** ve her toplamada **izi** yanında taşımak. Bu usul o yoldur. Okuyan bu bahiste hiçbir terimi bilmiyor sayılmıştır; her terim ilk geçtiği yerde tarif edilir.

Usulün gayesi iki cümleyle söylenir: **Her üst kayıt, kendisini doğuran alt kayıtlara her an açılabilir. Hiçbir üst kayıt, alt kayıtların söylemediği bir şey söylemez.**

## 1. Nesneler

**Atom.** Metinden okunan en küçük kayıt: `(âyet, bölüm, sıra, ad, biçim, örtük)`. Atom bir şey iddia eder; üstüne bir şey eklemez.

**Katman.** Atomların bir kuralla toplanmasından doğan kayıttır. Birinci katman (L1) atomları, ikinci katman (L2) birinci katman kayıtlarını toplar; bu böyle L4'e kadar gider.

**İz.** Her katman kaydı `(kural, kalan, çocuklar, şahit)` dörtlüsünü taşır: hangi kuralla toplandığı, kuralın dışarıda bıraktığı kalan, çocuk kayıtlar ve gerekiyorsa şahit.

**Açma.** Bir kaydı çocuklarına, çocukları kendi çocuklarına, atomlara varıncaya kadar açan işlemdir.

**Kayıpsızlık.** Açılan, toplananın tam kendisidir: `aç(katla(x)) = x`. Bu eşitlik her kayıtta, her katmanda sağlanır; sağlanmayan toplama usulden sayılmaz.

## 2. Dil

Önermeler `¬ ∧ ∨ ⇒` ile; münâsebetler `⇒ ⊐ ⋈ ⊢ ⤏ ≅ ↻` ile; kipler vâcib, haram, mendûb, mekrûh, mubah ile yazılır. Münâsebetin yedi aslî cinsi şunlardır: gerektirme (⇒), kapsama (⊐), bitişme (⋈), delil gösterme (⊢), geçiş (⤏), denklik (≅), dönüş (↻). Sekiz başlıklı her bağ bu yedi cinse iner. Her işaret tek manaya bağlıdır; ifadeler öncelik tablosuyla ayrıştırılır ve tam parantezli yazılır.

## 3. Altı katlama kuralı

Her kuralın bir **şartı** vardır; şart kuralın tarifidir. Şart tutmayan yerde kural uygulanmaz ve uygulanmadığı sayılır.

1. **Ortak toplama.** Aynı yüklemi taşıyan kayıtlar tek kayıtta toplanır. Şart: yüklem dağılır, yani her ferde ayrı ayrı isnat edilir.
2. **Hüküm toplama.** Aynı kipte, aynı mevzudaki hükümler toplanır. Şart: hüküm tekli emirdir; şartlı emir ikili hüküm sıralamasıyla kurulur.
3. **Olumsuzlama kapanışı.** Bir kaydın olumsuzunun olumsuzu kendisine döner. Şart: dışlanmış üçüncü geçerlidir; geçerli değilse hüküm Heyting seviyesinde kalır ve öyle işaretlenir.
4. **Genelleme.** Şahit kümesinden kural çıkarılır. Şart: şahit kümesi ve çürütücü birlikte tutulur; kural katiyet olarak zanna kadar çıkar, kesine çıkmaz.
5. **Öncelik.** İki hüküm çatışırsa öncelik sırası yüksek olan kalır, ötekisi kalan olarak izde durur.
6. **Nitel türev.** Bir büyüklüğün ötekine tesiri `{−, 0, +, ?}` işaretleriyle yazılır; yalnız sıfırla çarpım belirsizliği yutar.

## 4. Yardımcı yapılar

**İşaret cebiri.** `{−,0,+,?}` üzerinde ⊕ ve ⊗ kapalı, değişmeli ve birleşmelidir; dağılma alt-dağılmadır.

**Zaman ölçeği.** Ayrık ve sürekli zamanı tek hesapta toplar: `Δf(x) = (f(σ(x)) − f(x)) / μ(x)`; temel teorem `∫ₐᵇ Δf = f(b) − f(a)`.

**Sonsuz küçük.** ℝ(ε) sıralı halkadır; ε her `1/n`den küçüktür. Böylece sonsuz küçük tesir limitte yutulmaz, kayıtta durur.

**Sıralı cebir.** Yollar (max,min) altında kıyaslanır; sonuç yalnız sıraya bağlıdır, rakam gerekmez.

**Heyting kafesi.** Kabul kümeleri yukarı-kümelerdir; çıkarım `U ⇒ V`, `W ∩ U ⊆ V ⇔ W ⊆ (U ⇒ V)` ile tarif edilir.

**Ultrametrik ağaç.** Âyet–kısım–sûre ağacında uzaklık ortak atanın derinliğinden okunur; her üçgen ikizkenardır.

**Hiperkenar.** Çok öncüllü delil, öncüllerin hepsi birlikte bulununca sonuç veren tek kenardır.

**GF(2) rank.** Bir yeni hüküm, mevcut hükümlerin XOR bileşimi ise rank artmaz; yani yeni bir şey söylememiştir. Rank artıyorsa yeni bilgi vardır.

## 5. Uygulama sırası

1. Metin atomlara ayrılır (sûre 103 ve 112 için `kuram_ornek.py`).
2. Her bağ yedi münâsebet cinsinden birine yazılır ve katiyet derecesi "hikmet ihtimali" olarak işaretlenir.
3. Altı kuraldan uygulanabilenler, şartları denetlenerek uygulanır; uygulanamayan kural ve sebebi izde durur.
4. Her katmanda `aç(katla(x)) = x` denetlenir.
5. Rank denetimiyle yeni hüküm ile tekrar hüküm ayrılır.
6. Kayıt ağaçta ultrametrik uzaklıkla yerleşir.

## 6. Tarif edilen usulün sınama muhasebesi

Usulün her hükmü sonlu modelde koşturulur ve sayılır: **101 sınama, 101 geçti.** Satırların tamamı `KURAM_ZIYADELERI.md`de, ham sonuç `SINAMA.json`da durur; `python3 kuram_sina.py` ikisini yeniden üretir.

## 7. Dosyalar

`kuram.py` usulün kütüphanesi, `kuram_ornek.py` 103 ve 112. sûre kayıtları, `kuram_sina.py` sınama dizisi, `KAYNAK/` verilen taslaklar.
