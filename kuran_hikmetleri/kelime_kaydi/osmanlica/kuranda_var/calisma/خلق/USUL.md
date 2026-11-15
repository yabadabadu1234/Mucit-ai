# ŞERHLİ OSMANLICA TERCÜME USULÜ — `خلق` (tek dosya üzerinde çalışma)

Bu klasör `خلق` kökünün bütün çevrilecek satırlarını (kök anlamı, fiil sapı, kelime biçimleri, müştaklar) taşır. Sen bir ajansın; **dosyalar üzerinde çalışırsın** (Read ve Write/Edit araçlarıyla), sohbetle değil.

## Girdi (okuyacakların)
- `KAYNAKLAR/` : kökün **bütün** Arapça ve İngilizce kaynağı (Cebel, Mekâyîs, Vikisözlük, Arabic Ontology, EtymArab, Osmanlıca lügatler, Zemahşerî hakîkat/mecaz, prototip, WordNet dayanağı). Bunlar **bilgi malzemesidir**: mânânın ne olduğunu, hangi mânâların bulunduğunu buradan **tespit edersin**. Fakat şerhte sebep olarak kaynak anılmaz (aşağıda).
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

**Etiketlerin sırası ve sayısı serbesttir.** Hangi yerde hangi etiket gerekiyorsa o konur, hâlin iktizası neyse; ⟨Neden⟩ yüz tane de olabilir. Tek şart: **her kısım yalnız kendi sualinin cevabını taşır** ve etiketi o suali bildirir (sonradan otomatik derlenecek). Başlıca etiketler:
- **⟨Ne⟩** bu biçim/müştak ne demektir, tarif. **⟨Nasıl⟩** kökteki asıl mânâdan bu mânâya (varsa mecâza) nasıl gelindi; vezin, ek, ön ek, zamir mânâyı nasıl doğurdu.
- **⟨Neden⟩** **MANTIKÎ SEBEP.** Bu mânâya neden gelindi, neden böyle olmak zorunda veya böyle olmaya elverişli? Cevap **bir aklî çıkarım ve sezgi** olsun: okuyucu bu kısmı okuyunca kitaba, lügata, kimseye bakmadan **kendi aklıyla bu mânâyı yeniden icat edebilmeli**. Soru şudur: *Bu kelimeyi ilk icat eden sen olsaydın, bu işi/mânâyı bu söze neden bağlardın?* İnsanın bedeniyle, gözüyle, eliyle yaşadığı hâllerden, günlük tecrübeden ve zorunlu mantık bağlarından yürü ("bir şeyi yapmak için önce ölçmek gerekir; ölçmeden biçilmez; biçilmeden şekil olmaz…").
- **Nedene tekrar neden sor:** her sebebin sebebi ⟨Neden 2⟩, ⟨Neden 3⟩ … diye sürer; zincir, daha geriye gidilemeyen ve **her insanın sezgisiyle kabul ettiği ilk esasa** varınca ⟨Esas⟩ ile kapanır. Sebep dalları birden çoksa her dal kendi zincirini taşır. Zincirde iki ayrı mânâ yazdıysan her mânânın ayrı zinciri olur; bir mânânın kökteki asıl mânâdan **neden ve nasıl** mecâza geçtiği (benzetme, genişleme, daralma, sebep-netice, mekân-zaman geçişi gibi) mantıkla gösterilir.
- **⟨Niçin⟩** bu mânâ/kalıp/ek ne gaye ile var, ne işe yarar; bu gayeyi de insan ihtiyacından türet.
- Aklî çıkarımın dayandığı bir **olgu** dosyadan geliyorsa onu düz olgu olarak söyle ("kökün asıl mânâsı ölçüp biçmektir"), kaynağı **sebep diye göstermeden**. Dosyada hiç dayanağı olmayıp yalnız mantıkla ulaştığın hüküm **⟨Çıkarım⟩** etiketiyle yazılır.
- **ATIF YIĞINI YASAK:** "Cebel şöyle der, Mekâyîs şöyle der, Kubbe Altı şöyle der" gibi alıntı ve atıf dizileri **sebep değildir** ve yazılmaz; sebep, kaynağın söylemesi değil, **mantığın gerektirmesidir**. Bir satırda kaynak adı en çok **bir kere** ve yalnız mânânın tespitini bildirmek için (⟨Mesnet⟩ etiketiyle, bir cümle) anılabilir; Arapça alıntı en çok **üç kelime** olabilir (kelimenin kendisini göstermek için); uzun Arapça ibare YAZILMAZ. Kitap, müellif, âyet adı uydurma yasak.
- **EN UMUMÎ SEBEP:** Söylenen sebep, söylenebilecek **en geniş ve en umumî** sebep olmalıdır: dar ve cüz'î bir hâli değil, onu kapsayan en üst kaideyi söyle. (Telefon tablet değil, cihaz; cihaz da değil, eşya; eşya da değil, şey.) Cüz'î sebebi yazdıktan sonra zincirde **bir üst, bir üst** kapsayıcı sebebe çık; en umumî ilk esasa varınca dur. Bir sebep birden çok mânâya/satıra aynı umumî kaideden bağlanıyorsa onu açıkça belirt.
- **HARF KARIŞTIRMA YASAK:** Latin harfli bir Türkçe kelimenin içine Arapça harf, Arapça kelimenin içine Latin harf karıştırma (ör. `bâب`, `تَخْلِecip` gibi bozuk yazımlar kapıdan geçmez); Arapça ibare Arap harfiyle, Türkçe kelime Latin harfle yazılır ve aralarında boşluk bulunur.
- **ETİKET İŞARETİ:** Etiket tam olarak `⟨` (U+27E8) ile açılır, `⟩` (U+27E9) ile kapanır: `⟨Neden⟩`. Kapatırken `﴾`, `)`, `>` veya başka işaret KULLANMA; etiketin hemen ardından boşluk bırak.
- **ARAPÇA İBARE:** Şerhte Arapça yalnız kelimenin/ibarenin kendisini göstermek içindir, en çok üç kelime; harekesiyle ve harfi harfine doğru yazılır (kaynakta olan biçimden), hatırdan yazılmaz.

## ÜSLÛP (şerh için KESİN)
Şerhin her etiketli kısmı **Osmanlıca bir roman yazarının nesri gibi** akıcı, canlı, kurulu cümlelerle yazılır (Ömer Seyfettin, Mehmed Âkif, Halid Ziya, Filibeli Ahmed Hilmi nesri); **bir müderris gibi uzun ve ayrıntılı** konuşur: meseleyi açar, birbirine bağlı cümlelerle adım adım izah eder, yeri geldiğinde misal ve mukayese yapar. Kuru madde dökümü, tek cümlelik kısa kısımlar, çeviri kokan kırık cümle yasaktır; her etiketli kısım en az bir paragraf (birkaç tam cümle) olsun. Ama süs uğruna hüküm uydurulmaz: şerh bir **mantık yürütme**dir; her halka bir öncekinden aklen çıkar, olgu dosyadan alınır, yalnız mantıkla varılan söz ⟨Çıkarım⟩ diye belirtilir. **Kısa tercüme** (satırın ilk kısmı) ise sade ve kısa kalır.

## Tercüme kuralları
1. Dil Osmanlı Türkçesi, Latin harfli; Ömer Seyfettin ve Mehmed Âkif nesri; yerleşik Arapça-Fârisî asıllı kelimeler; **cevap Türkçe ifade olsun**, Arapça okunuş (naḍada gibi), bilimsel işaret (ḥ, ʿ), uydurma Arapça kalıp yazma.
2. **AYIRT ET:** aynı kalıp adı altındaki satırlar farklı vezinlerdir (fa'l, fi'l, fu'l, fa'al…). Hiçbirinin **kısa tercümesi** aynı kalıptaki bir başkasınınkiyle aynı olamaz; vezinin kendine has inceliği (hâl, mübalağa, tekrar, mef'ûl mânâlı masdar, isim-i hey'et, hacim, âlet, mekân, tasğîr, çokluk…) tercümenin içine tabiî yedirilir.
3. **ÇOK MÂNÂ:** bir biçim gerçekten birden çok farklı mânâya geliyorsa bütün mânâlar ` / ` ile ayrılır; eş anlamlı iki kelime ` / ` ile ayrılmaz.
4. Her mânâ o satırın Arapça biçiminden, vezninden ve kaynaklardan çıkmalı; komşu satırın mânâsını doldurma amacıyla taşıma.
5. Kök anlamı satırı: başlıkları (Halk: … gibi Latin başlıklar) aynen koru, mânâları Osmanlıca yaz; fiil sapı tek mastar olur.

## İnceleyici görevi (doğrudan kaynağında düzeltme)
- İnceleyici `tercüme:` satırını **doğrudan düzeltir ve zenginleştirir**; ayrı bir "tashih" notu, itiraz kısmı veya ⟨Tashih⟩ etiketi **YAZILMAZ**. Yanlış gördüğün yerde hatayı **yazıldığı yerde** düzelt.
- **Sınav:** Her ⟨Neden⟩ zincirini oku ve şunu sor: *Bu kısmı okuyan bir insan kitaba bakmadan, kendi aklıyla bu mânâyı yeniden icat edebilir mi?* Edemezse: atlanmış mantık halkasını ekle, sezgiye dayanmayan sebebi sezgiye bağla, zinciri ilk esasa kadar tamamla, cüz'î sebebi umumîye çıkar, ayrı mânâlara ayrı zincir yaz.
- **Atıf yığını gördüğünde** ("X lügati der, Y der" dizilerini) onları **mantıklı sebebe çevir**: kaynağın söylediği olgudan aklî bir çıkarım kur, atıf cümlelerini kaldır (satırda en çok bir kısa ⟨Mesnet⟩ kalabilir). Uzun Arapça alıntıyı kaldır.
- Atıf yığınından başka **hiçbir etiketli kısmı SİLME veya kısaltma**; atıf yığınını mantıkla **değiştirirken** o kısmın bilgisi kaybolmasın, tersine zenginleşsin. Bölümü öncekinden zayıf bırakma.
- Mantık, mânâ ve Türkçe hatalarını, harf karışmasını ve bozuk etiket kapanışlarını düzelt. `duz_tercume:` ve `ilave:` alanlarına dokunma (`ilave:` boş kalır).

## Durum protokolü (dosyaları çakıştırmamak için KESİN)
- Bir bölüm dosyasını **aynı anda yalnız bir ajan** yazar. Tercüman yalnız `durum: bos` bölümü alır: `tercume-yapiliyor` yap, bitirince `tercume-tamam`; `tercume_eden: tercüman`.
- İnceleyici yalnız **kendine atanmış** ve `durum: tercume-tamam` olan bölümü alır: `inceleniyor` yap (`inceleyen: <adın>`), bitirince `inceleme-tamam`.
- Bölümü **Write ile bütün hâliyle** yaz: başlık satırlarını, `---` ayracını, her satırın `##`, `arapça:`, `bilgi:` alanlarını **aynen koru**; yalnız kendi alanını doldur.
- Hazır bölüm yoksa `until grep -l "durum: tercume-tamam" ...; do sleep 20; done` türü bir bekleme döngüsüyle bekle (en çok 8 dakikalık turlar).
