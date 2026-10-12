# MANA · MEFHUM · MASADAK -- İNSANDA ÇALIŞAN MATEMATİK (F 3-I 303, 290)

Bütün "matematik" satırları Claude çıkarımıdır [Ç]; kaynak cümleleri [K] ile işaretlidir. Hüküm değildir.

## 1. Kaynak cümleler [K]
| # | Cümle | Kaynak |
| :-- | :-- | :-- |
| K1 | Kelime mana ifade eden her şeydir; lisan-ı kâl (lafız) ve lisan-ı hâl (ahvâl) | yapıştırılan metin (Nursî alıntısı) |
| K2 | Dört vücut: hâricî, ilmî (zihnî misal), lafzî, harfî | aynı |
| K3 | Mana = kelimenin zihindeki misale delâleti; nisbîdir, kişiye göre değişir | aynı |
| K4 | Mefhum = delâletin hâricî hakikate varması; müşahhastan alınır; daima aynıdır | aynı |
| K5 | Dağ misali: çocuğun manası küçük, bilenin manası büyük, hakikat büyük; tahkik manadan mefhuma götürür | aynı |
| K6 | Lügat anlamı, kullanılan anlam, hakikî anlam ayrı üçtür | aynı |
| K7 | Masadak = mananın ferdi; mananın/mefhumun yerini tutmaz; bir manaya çok masadak; bir fert bulunmazsa mana inkâr edilmez | aynı |
| K8 | Müevvil iki yönde yanıldı: masadakı mana yerine koydu; caiz masadakı mefhum yerine koydu | aynı (Muhâkemât) |
| K9 | Sıdk-kizb ilk manada (maânî-i ûlâ) değil maksatta (maânî-i sânevî) | aynı (Muhâkemât) |
| K10 | Mefhum-u muvafık / muhalif | aynı |
| K11 | Gözün yanlışını akıl, aklın yanlışını iman, itikad, kalb, vicdan düzeltir | aynı |
| K12 | Tasavvur: lafız, imaj, hayal değil; soyutlama, genelleme, düzenleme sonucu; unsurları ayırt edip mümkün bir konuya bağlar | İzmirli |
| K13 | concept/idea → tasavvur, mefhum, suret-i zihniye; notion → ma'kûl, ma'nâ | İzmirli dipnot |
| K14 | Sadık = zıddını içermeyen; kâzib = zıddını içeren | İzmirli |
| K15 | Üçgen tasavvuru üçgen olmak için zorunlu olan her şeyi içerir, tesadüfî olanı (demir, boy) içermez | İzmirli |

## 2. Tek model: formal bağlam
Taşıyıcı: nesneler E (masadak adayları), nitelikler A, ilişki R ⊆ E×A (x, a'ya sahip).
Türevler: X′ = X'in bütün elemanlarının ortak nitelikleri; I′ = I'deki bütün nitelikleri taşıyan nesneler.
**Kapalı çift (I, X)** : X = I′ ve I = X′ (Galois bağlantısı, Wille). Bu bir **kavramdır**; bütün kavramlar kafes oluşturur, kavram kanonik ve tektir.

| Terim | Matematik | Neden |
| :-- | :-- | :-- |
| Masadak | bir nesne x ∈ X | K7: ferd |
| Mananın kaplamı | X | K7: bir manaya çok masadak |
| Mananın içlemi | I | K15: zorunlu nitelikler |
| **Mefhum (yapıştırılan metin, K4)** | tam bağlamda (E, A, R) kapalı çift; kanonik, kişiden bağımsız | "daima aynı" = kafeste tek eleman |
| **Mana (K3)** | kişi p'nin alt bağlamında (E_p ⊂ E, A_p ⊂ A) kurduğu çift (I_p, X_p) | nisbî = alt bağlam kişiye göre |
| Tahkik (K5) | bağlamı genişletmek ve kapanışı yeniden almak (E_p→E, A_p→A) | mana → mefhum |
| Dağ misali | çocukta "küçük" ∈ I_p fakat ∉ I (algı kanalı yanlış); bilende I_p = I | K5 |
| Lügat/kullanılan/hakikî (K6) | toplumun ortalama çifti · kişinin çifti · kanonik çift | üç seviye; ortalama hakikate yakınsar yalnız hatalar ortak yanlı değilse |

## 3. Masadak neden yerini tutmaz (K7)
Bir nesnenin kendi içlemi x′ çok büyüktür (bütün nitelikleri); onun kavramı γ(x) = (x″, x′) en özel kavramdır. Genel kavram C=(I,X) için x ∈ X ⇔ γ(x) ≤ C. Yani **masadak, kavramın altındaki en özel noktadır**; kavramın kendisi değildir. Bir x'ten C belirlenmez (aynı x birçok kavramın içindedir): **eksik belirlenmişlik**.
Müevvil hataları (K8):
- masadakı mana yerine koymak: I := x′ (aşırı özel, genelliği kaybeder; ezberleme)
- masadakı (mümkün bir ferdi) mefhum yerine koymak: bir noktayı kavram sanmak (aşırı genelleme)
"Bir fert bulunmazsa mana inkâr edilmez": kavram X = ∅ iken de tanımlıdır (kafesin alt elemanı); **anlamlılık (I tutarlı) ile doluluk (X boş değil) ayrı şeydir.**
İki kurma yönü: nesnelerden niteliğe (X→I, tümevarım, öğrenilen kavram) ve metinden nesneye (I→X, verilmiş mana, tefsir). Nass/ayet için içlem verilir, kaplam türer; ferdin bulunması manayı belirlemez.

## 4. Dört vücut ve delâlet (K2)
Zincir: E →(r) Z →(n) W →(k) K (hâricî → zihnî → lafzî → harfî). Her halka kayıplı kanal. Veri işleme eşitsizliği:
I(E;K) ≤ I(E;W) ≤ I(E;Z) ≤ H(E).
Delâlet ters yönde okumadır; metinden hakikate dönüş, zincirin kaybettiğini **dışarıdan bilgiyle** (tahkik) tamamlar. Kelime lisan-ı hâli de kapsar (K1): hâl (durum) de bir işaret olabilir. [Ç, ARC bağı: ızgara hâli lisan-ı hâl kelimesidir.]

## 5. Maksat ve sıdk (K9)
Konuşan bir hâl s'yi kastederek w seçer; dinleyen s'yi çıkarır: L(s|w) ∝ S(w|s)·P(s) (pragmatik Bayes). Sıdk/kizb **s üzerinde** ölçülür, ilk manada değil. Kinaye: lafzî mana yanlış veya imkânsız olabilir, maksat doğru olabilir. Mana iki kat: ilk (lafzî harita) ve ikinci (maksat).

## 6. Mefhum-u muvafık/muhalif (K10)
- Muvafık: aynı yönde sıralı genişleme (daha ağır olan, aynı hükümde) -- monoton çıkarım.
- Muhalif: "P, S'ye söylendi, S dışına değil" çıkarımı -- tümdengelim **değil**, bağlama bağlı kapalı-dünya/münhasırlık çıkarımı (gayri monoton). Klasik mantıkta öncülü inkâr etmek geçersizdir; bu bir **zannî** çıkarımdır.
- Yoklama [web, ikincil kaynak, birincil usul eseri okunmadı]: Hanefîler genel olarak şer'î metinde mefhum-ı muhalefeti delil saymaz; Şâfiî, Mâlikî, Hanbelî kabul eder; çoğunluğa göre delaleti zannîdir; kaynaklar Hanefî sınırı üzerinde ayrışır.

## 7. İzmirli ile yapıştırılan metnin çatışması ve çözümü
- Çatışma: İzmirli mefhumu **zihnî** (tasavvur, suret-i zihniye) yanına koyar (K13); yapıştırılan metin mefhumu **hâricî hakikate** koyar (K4).
- Çözüm [Ç]: iki ayrı nesne. İzmirli'nin mefhumu = **kavram** (I,X) olarak zihindeki kapalı çift; metnin mefhumu = **tam bağlamdaki kanonik** çift. Aynı matematik nesnenin iki katı: zihindeki tahmin ve hakikî kanonik değer. Terimler çakışmasın diye: *mefhum-zihnî* (İzmirli) ve *mefhum-hakikî* (metin).
- Tasavvur (K12): kapalı, ayırt edilmiş, düzenli, **mümkün bir konuya bağlı** çifttir. "Mümkün konu" = I tutarlı.
- **Sadık/kâzib (K14) çözümü [Ç]:** tasavvurda sadık = I tutarlı (zıddını içermez, bir model olabilir); kâzib = I çelişik (alt kavram, X her dünyada boş). Tasdikteki doğruluk ise vakıaya mutabakattır (M ⊨ φ, nefsu'l-emr). **İki ayrı doğruluk: tutarlılık ve mutabakat.** Önceki Ç1 (tasavvurda doğruluk var mı) bu ayrımla kapanır.
- K11 (yanlış düzeltme katmanları): göz → akıl → iman/kalb/vicdan. Matematik: katmanlı çıkarım, üst katman alt katmanın çıkardığına önsel koyar veya veto eder. Kalb katmanı F 3-I 177 gereği ertelenmiştir; burada yalnız metnin iddiası olarak yazıldı.

## 8. Padişahın önceki sözleriyle bağ
- Padişahın mana tarifi (his → düşünme nesnesi) = Z'nin elemanı, metnin "zihnî misali" ile aynı kat. Uyuşuyor.
- Padişahın "tasavvur mana değil, manaların birleşimi değil": K12'ye göre **tasavvur = ayırt eden, düzenleyen, konuya bağlayan kapalı çift**; mana = tek bir zihnî misal (I_p,X_p) yahut Z elemanı. Fark **kapanış ve tutarlılıktır** (örnek §3: kapalılık). Bu önceki "ilişki" iddiamı (nakz edilmişti) değiştirir; çünkü ilişki mananın içindedir. [Ç, teyit bekler]

## 9. ARC'a tek satır bağ (ARC askıda, yalnız not)
Bulmaca örnekleri = masadaklar; kaide cümlesi = içlem I; test girdisi = yeni masadak adayı. Bütün örneklerin geçmesi gerekli, yeter değil (K7 eksik belirlenmişlik); örnekleri ezberlemek = I := x′ hatası.

## 10. Açık sualler
| # | Sual |
| :-- | :-- |
| S-ARC-27 | Mefhum için hangi kullanım esas: zihnî (İzmirli) mi, hâricî (metin) mi; iki kat ayrı tutulacak mı |
| S-ARC-28 | Yapıştırılan açıklayıcı metnin yazarı |
| S-ARC-29 | Tasavvur = kapalı ve tutarlı çift kabulü |
