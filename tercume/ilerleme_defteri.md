# Tercüme İş Parçacığının İlerleme Defteri

Bu defter, iş kesilirse kaldığı yerden devam edebilmek için tutulur. Her adımda buraya kayıt düşülür.

## Daimî kaideler (kullanıcının emri)

- Osmanlıca, edebî ve öğretici üslûpla yazılır; kısaltma kullanılmaz.
- Dosyalar grep ile değil, baştan sona okunarak tetkik edilir. İslâm'a aykırı söz söylenmez.
- Dürüst olunur. Uydurma karşılık ve uydurma eser yazılmaz; emin olunmayan yer "şüpheli" diye işaretlenir.
- Telifi düşmüş yahut açık lisanslı nüshalar bulunur ve tam metni tercüme edilir. Nüshalar Internet Archive, Wikisource, Project Gutenberg, PubMed Central'ın açık kısmı ve OpenStax gibi kaynaklarda aranır.
- Istılahta lügat iş parçacığının cedveli esas alınır. Karşılığı olmayan ıstılah çıkarsa lügat iş parçacığına bildirilir.
- Düsturlarda harf kullanılmaz, kemmiyetler kelimeyle yazılır.
- Her tercüme bitince not iş parçacığına haber verilir. Not iş parçacığı henüz açılmadığı için ilk tercüme bitince koordinatöre haber verilecektir.
- Bütün iş parçacıkları aynı depoda, ayrı klasörlerde çalışır ve parça parça kayıt eder.

### Kullanıcının 1 Kasım 2026 tarihli ilâve kaidesi

Kullanıcı şöyle buyurdu: "Telifli telifsiz fark etmez, en şaheseri neyse onlar tercüme edilecek." Buna göre:

- Seçimin ve sıranın ölçüsü telif hâli değil, şaheserlik derecesidir.
- Telifi düşmüş ve açık lisanslı eserler tam metniyle tercüme edilir.
- Telifli eserlerin tam metni çoğaltılmaz ve bire bir tercüme edilmez; çünkü bu, müellifin hakkını çiğnemek olur. Bunların yerine, eserin mefhumlarını, illiyet zincirlerini ve bilgilerini kendi cümlelerimizle, lügat cedveline uygun olarak ve hiçbir bilgiyi eksiltmemeye gayret ederek anlatan müstakil bir Osmanlıca şerh yazılır. Uzun iktibas yapılmaz.
- Cannon'un The Wisdom of the Body eseri de bu usulle, yani şerh olarak ele alınabilir.

### Kullanıcının 1 Kasım 2026 tarihli ikinci ilâve kaidesi

Kullanıcı şöyle buyurdu: "O zaman evvela birebir tercüme etsin, üzerine şerhini sonradan koysun ki metin kaybı yaşanmasın." Buna göre:

- Telifi düşmüş ve açık lisanslı eserlerde usul şudur: evvelâ birebir tam tercüme, sonra ayrı bir dosyada şerh. Metin kaybı olmaz.
- Telifli eserlerde birebir tercüme yine yapılmaz. Şerh, aslın bab bab tertibini takip eder; her babdaki bilgiyi, tarifi, illiyet zincirini ve rakamı kendi cümlelerimizle eksiksiz verir. Her kısmın asıldaki hangi bölüme denk geldiği gösterilir.
- Asıl metne erişilemeden yazılan şerhte, bölüm tertibi ve rakamlar asılla karşılaştırılıncaya kadar "şüpheli" kaydını taşır.

## Çalışma yeri

- Ortak depo: github.com/yabadabadu1234/mucit-ai, klasör: tercume/, dal: tip-piri/tercume.
- Yerel nüsha: /home/claude/mucit-ai/tercume/.
- Ortak proje klasöründe yedek: /mnt/project-files/tercume/.

## Ameliyat notları (engeller)

- 1 Kasım 2026: Bu muhitin ağ siyaseti komut satırından şu adreslere erişimi kapatıyor: archive.org, en.wikisource.org, www.gutenberg.org, openstax.org, pmc.ncbi.nlm.nih.gov, gallica.bnf.fr, biodiversitylibrary.org, wellcomecollection.org. Açık olan yalnız GitHub.
- Web getirme aracı Gutenberg sahifesini açabiliyor; fakat metni kelimesi kelimesine aktarmıyor, yalnız yüz yirmi beş harflik kısa iktibaslar veriyor. Bu sebeple tam metin bu yoldan alınamıyor.
- Tam metin tercümesi, yukarıdaki adreslere erişim açılıncaya kadar bekliyor. Kullanıcıdan ağ izni istendi.

## Nüsha tahkiki

| Eser | Nüsha | Telif hâli | Not |
|---|---|---|---|
| Harvey, De Motu Cordis | Project Gutenberg, eser numarası 67065: Robert Willis tercümesi, Everyman's Library, J. M. Dent, 1906 | Willis 1878'de vefat etti; tercümesi kamu malı. Ernest Albert Parkyn'in mukaddimesi bu tâbda vardır; Parkyn'in vefat yılı tahkik edilemedi, bu sebeple mukaddime tercüme edilmeyecek, yalnız Harvey'in metni tercüme edilecek. | Latince asıl ile karşılaştırma için Latince nüsha ayrıca aranacak. |

## Tercümelerin hâli

| Sıra | Eser | Usul | Hâli |
|---|---|---|---|
| 1 | Harvey, De Motu Cordis | Tam metin tercüme | Nüsha bulundu; metne erişim bekleniyor |
| 2 | Bernard, Introduction à l'étude de la médecine expérimentale | Tam metin tercüme (Fransızca asıldan) | Sırada |
| 3 | Sherrington, The Integrative Action of the Nervous System | Tam metin tercüme | Sırada |
| 4 | Virchow, Die Cellularpathologie | Tam metin tercüme | Sırada |
| 5 | Cohnheim, Vorlesungen über allgemeine Pathologie | Tam metin tercüme | Sırada |
| 6 | Metchnikoff, Leçons sur la pathologie comparée de l'inflammation | Tam metin tercüme | Sırada |
| 7 | Cannon, The Wisdom of the Body | Şerh (bab bab) | Birinci müsvedde tamam: cannon_bedenin_hikmeti/serh.md. Asıl metne erişilemeden yazıldı; bab tertibi ve rakamlar şüpheli, asılla mukabele bekliyor. |
| 8 | Guyton ile Hall, Textbook of Medical Physiology | Şerh | Sırada |
| 9 | Robbins ile Cotran, Pathologic Basis of Disease | Şerh | Sırada |
| 10 | OpenStax, Anatomy and Physiology | Tam metin tercüme, parça parça | Sırada |

### İkinci cüzden (Kadîm İslâm tıbbı) gelen eserler

İkinci cüz baştan sona okundu. Şaheser iş parçacığının tavsiye ettiği sıra ve nüsha hâli şöyledir; hepsi Internet Archive'e erişim bekliyor:

| Sıra | Eser | Nüsha | Not |
|---|---|---|---|
| 1 | Râzî, Kitâbü'l-Cüderî ve'l-Hasbe | Internet Archive "atreatiseonsmal00unkngoog" (Greenhill, 1848, Arapça ve İngilizce) | Arapça asıldan nakledilecek; Greenhill tercümesi mukabele için. |
| 2 | İbn Sînâ, el-Kânûn, birinci kitap | Internet Archive "QanunAvicennae" (Roma, 1593) | Gruner tercümesi Türkiye'de korunduğu için kullanılmayacak. |
| 3 | Zehrâvî, et-Tasrîf, otuzuncu makale | Internet Archive "b30411427" (Channell, Oxford, 1778) | |
| 4 | Şânîzâde, Mir'âtü'l-Ebdân | Internet Archive "amseinzde01anizuoft" | Lügat iş parçacığıyla beraber yürütülecek. |
| 5 | Sabuncuoğlu, Cerrâhiyyetü'l-Hâniyye | Nüsha bulunmadı | Gallica'da Paris nüshası aranacak. |

Akşemseddin'in Maddetü'l-Hayât'ındaki "görünmez tohum" ibaresi hakkında, yazma nüshadan tahkik edilmeden hüküm yazılmayacak.

Sıra, kullanıcının ilâve kaidesi üzerine şaheserlik derecesine göre yeniden tertip edilecektir; yukarıdaki sıra şimdilik şaheser cüzünün tavsiyesidir.

## Kaldığı yer

Depo kuruldu, ilerleme defteri yazıldı. Harvey nüshası Project Gutenberg'de tespit edildi. Tam metne erişim bekleniyor. Cannon şerhinin birinci müsveddesi yazıldı ve ıstılah cedveli lügat iş parçacığına bildirildi. Şaheser iş parçacığından ikinci cüz (Kadîm İslâm tıbbı) haberi geldi: /mnt/project-files/saheser/cuz_02_kadim_islam_tibbi.md; okunup sıraya alınacak. Sıradaki iş: ağ izni gelirse Harvey birebir tercümesi; gelmezse ikinci cüzün okunması ve şaheserlik sırasına göre bir sonraki şerh.
