# ŞERHLİ OSMANLICA TERCÜME USULÜ — `خلق` (tek dosya üzerinde çalışma)

Bu klasör `خلق` kökünün bütün çevrilecek satırlarını (kök anlamı, fiil sapı, kelime biçimleri, müştaklar) taşır. Sen bir ajansın; **dosyalar üzerinde çalışırsın** (Read ve Write/Edit araçlarıyla), sohbetle değil.

## Girdi (okuyacakların)
- `KAYNAKLAR/` : kökün **bütün** Arapça ve İngilizce kaynağı (Cebel, Mekâyîs, Vikisözlük, Arabic Ontology, EtymArab, Osmanlıca lügatler, Zemahşerî hakîkat/mecaz, prototip, WordNet dayanağı). Hüküm ve delil **yalnız buradan** çıkar.
- `bolum_NN_<tür>.md` : çalışma bölümleri. Her bölüm şu biçimdedir:

```
durum: bos | tercume-yapiliyor | tercume-tamam | inceleniyor | inceleme-tamam
bolum: <tür> — <başlık>
tercume_eden: -
inceleyen: -

---

## <satır kimliği>
arapça: <Arapça biçim>
bilgi: <tür, bâb, zaman, kalıp, vezin, ingilizce_tanik …>
duz_tercume: <hazır düz Osmanlıca tercüme; git geçmişindeki en iyi sürüm (OVH Qwen3.5-397B-A17B)>
tercüme:
ilave:
```

`duz_tercume:` alanı **hazır esas metindir**; tercüman onu baştan çevirmez, **üstüne şerh yazar**. Alanı kimse değiştirmez.

## Şerhli tercüme biçimi (`tercüme:` satırı — tercüman yazar)
Tercüman `duz_tercume:` değerini esas alır: doğruysa **aynen** kısa tercüme olarak alır, açıkça yanlışsa (kaynakla çelişen mânâ, uydurma, aynı kalıpta tekrar, Türkçe olmayan ifade) kaynaktan düzeltir ve düzeltmenin sebebini şerhte söyler. Tek satır: önce **kısa Osmanlıca tercüme**, sonra **etiketli kısımlar**.

**Etiketlerin sırası ve sayısı serbesttir.** Hangi yerde hangi etiket gerekiyorsa o konur, hâlin iktizası neyse; ⟨Neden⟩ yüz tane de olabilir, sırayı da hâl belirler. Sabit bir sıra veya sabit bir etiket kümesi yoktur. Tek şart: **her kısım yalnız kendi sualinin cevabını taşır** ve etiketi o suali bildirir (sonradan otomatik derlenecek). Kullanılan başlıca etiketler:
- **⟨Ne⟩** bu biçim/müştak ne demektir, tarif. **⟨Nasıl⟩** kökteki asıl mânâdan bu mânâya (varsa mecâza) nasıl gelindi; vezin, ek, ön ek, zamir mânâyı nasıl doğurdu.
- **⟨Neden⟩** bu mânâya geldiği neden ve nasıl biliniyor, yani delil: **KAYNAKLAR'daki hangi madde söylüyor** (kaynağı ve ilgili cümleyi/kelimeyi anarak). İki ayrı mânâ yazdıysan her biri için ayrı ⟨Neden⟩.
- **Nedene tekrar neden sor:** her sebebin sebebi ⟨Neden 2⟩, ⟨Neden 3⟩ … diye sürer; zincir, daha geriye gidilemeyen ilk kabul edilen esâsa (kök mânâsı, lügatin kendisi, Arap kullanımı, sarf kaidesi) varınca ⟨Esas⟩ ile kapanır. Sebep dalları birden çoksa her dal kendi zincirini taşır.
- **⟨Niçin⟩** bu mânâ/kalıp/ek ne gaye ile var, ne işe yarar.
- Dosyada dayanağı olmayan hüküm **⟨Çıkarım⟩** etiketiyle ve çıkarım olduğu söylenerek yazılır. Hâl başka bir etiket gerektiriyorsa (ör. ⟨İtiraz ve cevabı⟩, ⟨Misal⟩, ⟨Karşılaştırma⟩, ⟨Mecâz⟩) o yazılır; etiket adı sualini açıkça bildirmelidir.
- **Kitap, müellif, âyet adı uydurma yasak.**
- **EN UMUMÎ SEBEP:** Hangi etikette olursa olsun söylenen sebep, söylenebilecek **en geniş ve en umumî** sebep olmalıdır: dar ve cüz'î bir hâli değil, onu kapsayan en üst kaideyi söyle. (Telefon tablet değil, cihaz; cihaz da değil, eşya; eşya da değil, şey.) Önce kaynaktaki cüz'î delili yaz, sonra aynı etiket zincirinde onu kapsayan **bir üst, bir üst** sebebe çık; en umumî kaideye (ilk kabul edilen esâsa) varınca dur. Cüz'î sebep tek başına bırakılmaz; ona kapsayıcı umumî sebep eklenir. Bir sebep birden çok mânâya/satıra aynı umumî kaideden bağlanıyorsa onu açıkça belirt.
- **HARF KARIŞTIRMA YASAK:** Latin harfli bir Türkçe kelimenin içine Arapça harf, Arapça kelimenin içine Latin harf karıştırma (ör. `bâب`, `تَخْلِecip` gibi bozuk yazımlar kapıdan geçmez); Arapça ibare Arap harfiyle, Türkçe kelime Latin harfle yazılır ve aralarında boşluk bulunur.
- **ETİKET İŞARETİ:** Etiket tam olarak `⟨` (U+27E8) ile açılır, `⟩` (U+27E9) ile kapanır: `⟨Neden⟩`. Kapatırken `﴾`, `)`, `>` veya başka işaret KULLANMA; etiketin hemen ardından boşluk bırak.
- **ARAPÇA ALINTI harfi harfine:** Arapça bir ibare alıntılanacaksa KAYNAKLAR'daki yazıdan **harfi harfine, harekesiyle kopyalanır**; kaynakta aynen bulunmayan, hatırdan yazılmış veya harfi eklenip bozulmuş Arapça YAZILMAZ (emin değilsen alıntıyı koyma, Türkçe özetle). Alıntı sonradan otomatik denetlenecek.

## ÜSLÛP (şerh için KESİN)
Şerhin her etiketli kısmı **Osmanlıca bir roman yazarının nesri gibi** akıcı, canlı, kurulu cümlelerle yazılır (Ömer Seyfettin, Mehmed Âkif, Halid Ziya, Filibeli Ahmed Hilmi nesri); **bir müderris gibi uzun ve ayrıntılı** konuşur: meseleyi açar, birbirine bağlı cümlelerle adım adım izah eder, yeri geldiğinde misal ve mukayese yapar. Kuru madde dökümü, tek cümlelik kısa kısımlar, çeviri kokan kırık cümle yasaktır; her etiketli kısım en az bir paragraf (birkaç tam cümle) olsun. Ama süs uğruna delil uydurulmaz: her hüküm yine KAYNAKLAR'a dayanır, dayanağı olmayan söz ⟨Çıkarım⟩ diye belirtilir. **Kısa tercüme** (satırın ilk kısmı) ise sade ve kısa kalır.

## Tercüme kuralları
1. Dil Osmanlı Türkçesi, Latin harfli; Ömer Seyfettin ve Mehmed Âkif nesri; yerleşik Arapça-Fârisî asıllı kelimeler; **cevap Türkçe ifade olsun**, Arapça okunuş (naḍada gibi), bilimsel işaret (ḥ, ʿ), uydurma Arapça kalıp yazma.
2. **AYIRT ET:** aynı kalıp adı altındaki satırlar farklı vezinlerdir (fa'l, fi'l, fu'l, fa'al…). Hiçbirinin **kısa tercümesi** aynı kalıptaki bir başkasınınkiyle aynı olamaz; vezinin kendine has inceliği (hâl, mübalağa, tekrar, mef'ûl mânâlı masdar, isim-i hey'et, hacim, âlet, mekân, tasğîr, çokluk…) tercümenin içine tabiî yedirilir.
3. **ÇOK MÂNÂ:** bir biçim gerçekten birden çok farklı mânâya geliyorsa bütün mânâlar ` / ` ile ayrılır; eş anlamlı iki kelime ` / ` ile ayrılmaz.
4. Her mânâ o satırın Arapça biçiminden, vezninden ve kaynaklardan çıkmalı; komşu satırın mânâsını doldurma amacıyla taşıma.
5. Kök anlamı satırı: başlıkları (Halk: … gibi Latin başlıklar) aynen koru, mânâları Osmanlıca yaz; fiil sapı tek mastar olur.

## İnceleyici görevi (doğrudan kaynağında düzeltme)
- İnceleyici `tercüme:` satırını **doğrudan düzeltir ve zenginleştirir**; ayrı bir "tashih" notu, itiraz kısmı veya ⟨Tashih⟩ etiketi **YAZILMAZ**. Bir yanlış gördüğün yerde (yanlış mânâ, uydurma/yanlış kaynak, kayma, aynı kalıpta tekrar, Türkçe olmayan ifade) hatayı **yazıldığı yerde** düzelt: kısa tercümeyi ya da ilgili ⟨Ne⟩/⟨Nasıl⟩/⟨Neden⟩ cümlesini doğrusuyla değiştir.
- **İlave sebepler** de aynı şekilde tercümenin içine girer: tercümenin ⟨Neden⟩ zincirinde olmayan ek deliller, başka kaynaklardan (KAYNAKLAR'ı taray) teyit, eksik ⟨Neden k⟩ halkaları, atlanmış mânâlar için ⟨Ne⟩/⟨Nasıl⟩/⟨Neden⟩/⟨Esas⟩/⟨Niçin⟩ kısımları; etiketler hâlin iktizasına göre serbesttir; yalnız her kısım kendi sualinin cevabını taşır.
- **SİLME:** Satırda var olan etiketli kısımları (⟨Niçin⟩, ⟨Neden k⟩, ⟨Esas⟩ …) ve delilleri SİLME veya kısaltma; yalnız yanlışı düzelt, eksiği ekle. Bölümü yeniden yazarken öncekinden daha zayıf bir metin bırakma.
- Yeni delil yalnız KAYNAKLAR'dan; alıntı kısa ve doğru. Tercümedeki sebepler en umumî sebebe çıkarılmamışsa (cüz'î kalmışsa) yukarı çıkar; bozuk veya kaynakta olmayan Arapça alıntıyı KAYNAKLAR'daki doğru yazıyla değiştir. Tekrar etme, şişirme. `duz_tercume:` alanına ve `ilave:` alanına dokunma (`ilave:` boş kalır).

## Durum protokolü (dosyaları çakıştırmamak için KESİN)
- Bir bölüm dosyasını **aynı anda yalnız bir ajan** yazar. Tercüman yalnız `durum: bos` bölümü alır: `tercume-yapiliyor` yap, bitirince `tercume-tamam`; `tercume_eden: tercüman`.
- İnceleyici yalnız **kendine atanmış** ve `durum: tercume-tamam` olan bölümü alır: `inceleniyor` yap (`inceleyen: <adın>`), bitirince `inceleme-tamam`.
- Bölümü **Write ile bütün hâliyle** yaz: başlık satırlarını, `---` ayracını, her satırın `##`, `arapça:`, `bilgi:` alanlarını **aynen koru**; yalnız kendi alanını doldur.
- Hazır bölüm yoksa `until grep -l "durum: tercume-tamam" ...; do sleep 20; done` türü bir bekleme döngüsüyle bekle (en çok 8 dakikalık turlar).
