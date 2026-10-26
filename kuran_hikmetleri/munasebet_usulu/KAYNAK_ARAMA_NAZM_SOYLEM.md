# Nazm ve söylem çalışmaları: gaye ağacına en çok katkı yapacak kaynaklar

Emir: "Nazm ve söylem çalışmaları hakkında modern eski fark etmez, mevcut usulümüze en çok katkı yapacak kaynaklar ne ise bul." ("Namz" = nazm okuması Claude'undur.) Ölçü: katkı, gaye ağacında (`ust`, `onkosul`, `taksim`, `kok_gaye`, sağ sınır, sual yazımı, sınama) bugün elle olan bir şeyi tarife bağlamak ya da sınanabilir kılmaktır.

**Okuma durumu (CLAUDE.md § 3-I 230, 244):** aşağıdaki her satır arama özetine dayanır; birinci el metin bu turda **okunmadı**. Formüller ve tarifler, kitap okunmadıkça "teyitli" sayılmaz. Hafızadan gelen satırlar öyle işaretlidir.

## A. Söylem: gaye ağacının iskeleti

| Sıra | Kaynak | Ağaca katkısı | Durum |
| :-- | :-- | :-- | :-- |
| 1 | Grosz & Sidner 1986, *Attention, Intentions, and the Structure of Discourse*, Computational Linguistics 12(3): 175–204 | Her söz parçasının bir **maksadı** vardır (DSP). İki bağ: **hâkimiyet** (DSP2'yi gerçekleştirmek DSP1'in bir parçasını gerçekleştirmek için niyet edilmişse DSP1, DSP2'ye hâkimdir) ve **tatmin-önceliği** (biri öbürünün ön şartı). Bunlar bizim `ust` ve `onkosul` kenarlarıdır. Ağacın bugünkü iki kenarı bu tarifle sınanır | Arama özeti (ders notu, Cornell/MIT); özgün metin Harvard DASH'te listeli |
| 2 | Moser & Moore 1996, *Toward a Synthesis of Two Accounts of Discourse Structure*, CL 22(3): 409–419 | RST'nin çekirdek-uydu bağı, G&S hâkimiyetine karşılık gelir. Bizim `ust` kenarına **tür** verir (delil, gerekçe, açıklama vb.); bugün kenar türsüzdür | Arama özeti; Marcu 2000 eşlemenin her durumu kapsamadığını söylüyor |
| 3 | Riester 2019 ve Riester vd. 2018 (QUD ağacı kurma); De Kuthy vd. 2018 | Metinden sual ağacı kurma **kuralları**: sual–cevap uygunluğu, sual–verilmişlik, azamî sual göndermesi, köke dönüş. Bizim usulün fiilen yaptığı budur; kurallar hazırdır. Etiketleyiciler arası uyum κ = 0,52 (De Kuthy 2018): bu iş zordur, ölçüsü bellidir | Arama özeti (arXiv:2502.15573 anketi); Riester PDF'si ims.uni-stuttgart.de'de listeli |
| 4 | Ko vd. 2020, 2022 (DCQA); Wu vd. 2023 (QUDEVAL); Wu vd. 2024 | **Çıpa cümle + sual** modeli: her cümle önceki bir cümleye bağlı bir sualin cevabıdır. Wu vd. sual kalitesi için dört ölçü verir: **iyi kurulmuşluk, cevabı odağa alma, bağlama dayanma, çıpaya yakınlık**. Bu, § 3-I 332 için hazır **puanlama cetvelidir**: ürettiğimiz her gaye sualini bu dört ölçüyle notlarız | Arama özeti (anket); veri: DCQA 22 394 sual–cevap, 606 makale; QUDEVAL 2190 sual |
| 5 | Van Kuppevelt 1995, *Discourse structure, topicality and questioning*, Linguistics 31: 109–147 | Söylem yapısını **konu oluşturan sualler** yürütür; açık ya da örtük sual söylemin gidişini kurar. Roberts'ın öncüsüdür. "Besleyen sual" ayrımı hafızadandır, arama onu doğrulamadı | Özet doğrulandı; ayrıntı hafızadan, yoklanamadı |
| 6 | Roberts 2012 (elimizde, okundu) + Büring 2003, *On D-trees, beans, and B-accents*, Linguistics & Philosophy 26(5) | Büring: **sual ağaçları**, stratejiler ve kontrast konu. `ust` ağacının biçimine karşılık gelir. Metni alınamadı | Künye doğrulandı, içerik okunmadı |
| 7 | Asher & Lascarides 2003, *Logics of Conversation* (SDRT) | Türlü söylem bağları (Sual–Cevap Çifti, Devam vb.) ve **sağ sınır** kuralı. `karar_denetle.py`'deki sağ sınır denetimi bu kuralın karşılığıdır; kaynağı artık adlıdır. Hunter & Abrusán 2015, SDRT ile QUD'u birleştirir | Künye ve sual-cevap bağı doğrulandı; sağ sınır tarifi hafızadan |
| 8 | Ginzburg 2012, *The Interactive Stance* (OUP); Groenendijk & Roelofsen (sorgulayıcı anlam) ve Ciardelli–Groenendijk–Roelofsen 2018 | **Alt sual ve cevap, iktiza ile tarif edilemez**: sualler çakışan ihtimal kümeleriyse cevaplık ve alt sualliğin tarifi iktiza ile verilemez. Bu, § 12-A'da yazdığım "alt cevap üst sualin kısmî cevabıdır (iktiza)" satırını **düzeltir** (aşağıda § C) | Arama özeti; kitap okunmadı |

## B. Nazm: sûre içi yapı ve söz seçimi

| Sıra | Kaynak | Ağaca katkısı | Durum |
| :-- | :-- | :-- | :-- |
| 9 | Ferâhî ve Işlâhî (*Nizâmü'l-Kur'ân*, *Tedebbür-i Kur'ân*); Mustansir Mir, *Coherence in the Qur'an* (1986) | Her sûrenin bir **amûdu** (ana mevzu) vardır; sûreler çiftler ve yedi gruba bağlıdır. Bizim `kok_gaye` ile aynı fikirdir; çift ve grup, ağacın **sûre üstü** katmanlarını verir. Mir'in değerlendirmesi: delil güçlü, titizlik Işlâhî'nin dediği kadar değil, cevapsız sualler var; bu tenkit bizim için hazır itiraz listesidir | Arama özeti (Wikipedia, USIM makalesi); kitap okunmadı |
| 10 | Bikâî, *Nazmü'd-Dürer fî Tenâsübi'l-Âyâti ve's-Süver* (22 cilt) | Her sûrenin başında **maksûd** ve besmele ile bağı yazılır. Elimizde 114 sûrenin **elle yazılmış kök gayesi** bulunur; bizim `kok_gaye`lerimizi bunlarla karşılaştırmak dış hakem olur. Padişahın § 3-I 187 kaydı gereği hikmet ihtimalidir, öncül değil | Arama özeti; maksûd cümleleri bu turda alınamadı |
| 11 | Draz, *en-Nebeü'l-Azîm* (İng. *The Qur'an: An Eternal Challenge*) | Sûre = **giriş + asıl maksat + hâtime**; "çokta bir": çeşitli mevzuun altında tek mevzu. Bakara'ya da uygulanmış. Ağaçta sûre şablonu verir (Nebe': 1-5, 6-37, 38-40 ikinci elden) | İkinci el özet; Draz'ın kendi metni görülmedi |
| 12 | Cürcânî, *Delâilü'l-İ'câz* (TDV Meânî ve Nazmü'l-Kur'ân maddeleri; Şensoy 2001 tezi) | Nazm = nahiv mânâlarının **seçimle** yerleştirilmesi; takdim–tehir, hazif, marife–nekire, fasl–vasl. Bu **ikinci devrin** (lafız ve yapı) çekirdeğidir: gaye sabit, ifade seçeneği çoktur; seçim kuralı q-şık odak seçenekleriyle (Roberts 24–29) eşlenir. İhtiyâr ve "mânânın mânâsı" Bartın makalesinde ayrıca incelenmiş | TDV özetleri; eser okunmadı |

## C. Bu aramanın mevcut belgeye düzeltmesi

`USUL_MANA_ONCELIKLI.md` § 12-A'da `ust` kenarını "alt sualin tam cevabı üst sualin kısmî cevabıdır (iktiza)" diye yazdım. Groenendijk–Roelofsen'e göre iktiza ile tarif ancak sualler **bölüntü** olduğunda geçer; sualler çakışan ihtimallerse tutmaz. Gaye sualleri çakışabilir ("Rab kimdir" ve "âlemleri kim yönetir"). Bu yüzden `ust` tarifinin **birinci** dayanağı G&S hâkimiyetidir (niyet), Roberts'ın iktizası değil. § 12-A buna göre düzeltilir.

## D. Sıra önerisi (okuma izni 3-I 230'a tabi)

1. Grosz–Sidner 1986 (makale, 30 sayfa): `ust` ve `onkosul` tarifi.
2. Wu vd. 2023 QUDEVAL ve Ko vd. 2022: sual puanlama cetveli ve veri.
3. Riester 2019: ağaç kurma kuralları.
4. Ferâhî–Işlâhî–Mir ve Bikâî'den sûre amûdu/maksûd örnekleri: Fâtiha ve Bakara için.
5. Cürcânî: ikinci devre girerken.
