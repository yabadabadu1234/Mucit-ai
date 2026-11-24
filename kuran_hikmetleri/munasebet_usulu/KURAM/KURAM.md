# KAYIPSIZ KATLAMA KURAMI
### (çalışma adı) — Kur'ân tertîbinin münâsebet kayıtları için biçimsel usul

## 0. Girizgâh

Bu bahiste cevabını aradığımız sual şudur: **bir sûrenin içindeki hükümleri, bağları ve gayeleri, hiçbirini kaybetmeden ve hiçbirini uydurmadan, kat kat üst katmanlara toplayabilir miyiz; toplanan her üst hüküm, kendisini doğuran alt hükümlere her an geri açılabilir mi?** Bu suali, elimize verilen iki taslak (V1 ve V2; V2 ile V2_2 baytı baytına aynıdır) ortaya koymuştu. Taslakların fikri güzeldi; fakat birçok yerinde sayıldığı gibi sağlam değildi: bazı kurallar yalnız belli şartlarda doğruydu, bazı işaretler iki ayrı mana için kullanılmıştı. Biz fikri tuttuk, kusurları tek tek bulup şartlarını yazdık ve her iddiayı sonlu bir model üzerinde **fiilen koşturarak** sınadık. Koşturulan sınamaların sayısı ve sonucu `KURAM_ZIYADELERI.md` ve `SINAMA.json`da durur: **101 sınama, 101 geçti.**

Okuyan bu bahiste hiçbir ismi ve hiçbir terimi bilmiyor sayılmıştır; terimler ilk geçtiği yerde bir defa açıklanır.

Bu kuram **usûl kuramıdır**, tefsir değildir. Sûre 103 ve 112 için yazılan kayıtlar usulün nasıl çalıştığını gösteren misaldir; tefsir hükmü taşımaz. Gerekçeler **"hikmet ihtimali"** olarak yazılır, murâd-ı ilâhî diye yazılmaz (CLAUDE.md F 3-I 318).

## 1. Kuramın nesneleri

1. **Atom (L0).** Metinden okunan en küçük kayıt: (âyet, bölüm, sıra, ad, biçim, örtük). Atom bir şey **iddia eder**; üstüne bir şey eklemez.
2. **Katman (L1…L4).** Atomların bir **kural** ile toplanmasıyla doğan üst kayıt. Her üst kayıt, kendisini doğuran çocukların listesini ve kuralın adını **iz** olarak taşır.
3. **Katlama.** `Katla(kural, kalan, çocuklar, şahit)`: kural adı, kuralın atladığı kalan, çocuklar ve gerekirse şahit.
4. **Açma.** `ac(t)`: bir terimi yapraklarına kadar geri açar.
5. **Kayıpsızlık.** `ac(katla(x)) = x`; yani açılan, katlananın tam kendisidir. `kayipsizmi(t, kapsanan)` bunu denetler.

**Dil.** Önermeler, `¬ ∧ ∨ ⇒ ⊐ ⋈ ⊢ ⤏ ≅ ↻` ve kip işaretleriyle yazılır; ayrıştırıcı öncelik tablosuyla çalışır ve `tam_parantez` ile her ifadeyi tam parantezli yazar; böylece iki işaret takımı hiçbir zaman karışmaz.

## 2. Taslakların kusurları ve tamiri

| # | Taslakta | Kusur | Tamir |
| :-: | :-- | :-- | :-- |
| 1 | ⊕ ve ⊬ işaretleri | İki ayrı mana için kullanılmış | Her işaret tek manaya bağlandı; ayrıştırıcı iki manayı karıştırırsa reddeder |
| 2 | Kural 1 (ortak çocuk toplama) | Dağılma gerekir | Yan şart: dağılma; toplu (kolektif) yüklemde karşı misal gösterildi |
| 3 | Kural 2 (norm toplama) | İkili (şartlı) emirde geçersiz | Yan şart: yalnız tekli norm; ikili norm sıralamayla kurulur |
| 4 | Kural 3 (olumsuzlama kapanışı) | Dışlanmış üçüncü ister | Heyting karşı modeli bulundu (zincir 3); şart yazıldı |
| 5 | Kural 4 (genelleme) | İstikrâîdir (sayarak kurulur) | Şahit kümesi ve çürütücü (falsifier) birlikte tutulur; iddia katiyet derecesiyle yazılır |
| 6 | Kural 5 (öncelik) | Bozulabilir (defeasible) anlam ister | Öncelik sırası bir yapı olarak ilân edildi |
| 7 | Zaman ölçeği farkı | μ'ye bölünmeden yazılmış | Hilger türevi `Δf = (f(σ)−f)/μ` olarak düzeltildi |
| 8 | Tropikal (max,+) | Aksiyom 3 ile çatışır | (max,min) sıralı zincir; sebep ve sayı Bölüm I'de |
| 9 | ↻ etiketleri | Halka kutbuyla uyuşmuyor | Kutup, kenar işaretlerinin çarpımıdır (`dongu_kutbu`) |
| 10 | Mubah | SDL'deki "P" (izin) ile aynı sayılmış | Mubah ayrı bir kiptir; izinden farklıdır |
| 11 | Sekiz bağ başlığı | Yedi aslî ilişkiye iner | Bağlar yedi ilişkiye indirildi: ⇒ ⊐ ⋈ ⊢ ⤏ ≅ ↻ |
| 12 | Şartlı emir | Chisholm paradoksuna açık | SDL'de tatmin edilemez, ikili norm sıralamasında tatmin edilir (sınama) |

## 3. Kurallar ve yan şartları

Altı katlama kuralı vardır. Her kuralın bir **yan şartı** ve bir **cebirsel dayanağı** vardır; yan şart tutmuyorsa kural uygulanmaz ve uygulanmadığı sayılır (sessiz ikame yoktur):

1. **Ortak toplama** — dağılma şartıyla.
2. **Norm toplama** — tekli kip, KD (tutarlı emir) modelinde.
3. **Olumsuzlama kapanışı** — Boole şartıyla; yoksa Heyting hükmü ile sınırlanır.
4. **İstikrâî genelleme** — şahit kümesi + çürütücü; katiyet derecesi "zan" tavanında kalır.
5. **Öncelik** — sıralı yapı; birbiriyle çelişen iki emirden öncelikli olan kalır.
6. **Nitel türev** — {−,0,+,?} işaret cebiri; "?" yalnız sıfırla çarpılınca yutulur.

## 4. İspatlanan ve sınanan teoremler (özet; satır satır `KURAM_ZIYADELERI.md`de)

- **Kayıpsızlık:** her katlama açılınca aynı atomları verir; iz birbirini tutar.
- **İşaret cebiri:** kapalı, değişmeli, birleşmeli; dağılma yalnız **alt-dağılmadır** (tam eşitlik bozulan üçlüler sayıldı).
- **Standart dışı sayı (ε):** ℝ(ε) sıralı halkadır; ε, her 1/n'den küçüktür; ε≠0 iken standart kısım 0'dır; yani limit sonsuz küçüğü yutar, kuram yutmaz.
- **Lineer cebir (GF(2)):** rank bazdan bağımsızdır; rank–sıfırlık teoremi 512 matrisin hepsinde doğrulandı.
- **Tensör daraltma:** ∀∃ ile ∃∀ değişmez; ∃j∀i ⇒ ∀i∃j doğru, tersi yanlış.
- **Tropikal ve sıralı cebir:** (max,min) altında sonuç yalnız sıraya bağlıdır; (max,+) altında etiketlemeye bağlıdır.
- **Heyting kafesi:** Alexandrov yukarı-kümeleri Heyting cebridir; dışlanmış üçüncü ve çifte olumsuzlama kapanışı 3-zincirde çöker.
- **Ultrametrik ağaç:** her üçgen ikizkenardır; ortak ata simetriktir.
- **Dinamik:** Goodwin n=3 eşiği 8; Tarski sabit noktası; potansiyel oyunda en-iyi-cevap dizisi sonlanır.
- **Zaman ölçeği:** temel teorem `∫Δf = f(b)−f(a)`.
- **Üst kuram:** tutarlılık, mutasyon (yanlış iddia aynı denetimden reddedilerek döner), aksiyom bağımsızlığı, karar verilebilirlik, doğrusal zamanlı ayrıştırma.

## 5. Yanlışlanabilirlik (kuramın hangi sınamada çökeceği)

- Bir katlamada `ac(katla(x)) ≠ x` çıkarsa kuram çöker.
- Bir kuralın yan şartı tutmadığı hâlde kural uygulanıp sessizce geçilirse ölçü kırmızı yanar.
- Sınama setinden bir kontrol kapatılırsa sayı 101'in altına düşer; bu sayı raporda her zaman görünür.

## 6. Sınırlar ve dürüst ayrım

- Sınamalar **sonlu modeller** üzerindedir: bütün küçük modeller taranmıştır, ama bu sonsuz bir modelin doğruluğunu ispatlamaz; sonlu modelde bulunan **karşı örnek** ise kesin delildir.
- Bazı kontroller **tanım gereğidir** (örneğin işaret cebirinin tablosu); bunlar kuramın ispatı değil, gerçeklemesidir. Gerçek içerik karşı modellerde ve ayırt eden mutasyon sınamalarındadır (Bölüm L).
- Sûre 103 ve 112 kayıtları usul misalidir; tefsir hükmü yoktur.
- Dış kaynaklara (Soulé, Kuipers, Tarski, Monderer–Shapley, Hilger) dayanılan yerler okunup doğrulanmıştır; Robinson, Heyting, Lewis, Chisholm, Hansson, Goodwin ve Bohner–Peterson atıfları **yoklanmadı**, hafızadandır ve öyle işaretlidir.

## 7. Yeniden üretmek

```
cd kuran_hikmetleri/munasebet_usulu/KURAM
python3 kuram_sina.py        # SINAMA.json ve KURAM_ZIYADELERI.md'yi üretir
```
