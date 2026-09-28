# FORMÜLLER

Bu dosya mimarî müzakerede mühürlenen bütün formülleri tutar.

**Kaide (yeni):** Başlık, küme adı değil, **parametredir** (sual). Bir küme `a × b × c` şeklinde bir çarpım olarak ifade edildiyse, `a`, `b`, `c`'nin her biri kendi başlığını alır; o başlığın altında, o parametreyi taşıyan **bütün kümeler** yan yana durur:

```
başlık1:
  küme1(başlık1) = {...}
  küme2(başlık1) = {...}
```

Tasnifat ilerledikçe her başlık kendi altında birikir; hiçbir başlık iki yerde tekrar tarif edilmez, hiçbir kümenin bir parametresi başka bir başlığın altına sızmaz. Bir kümenin toplam formülü (çarpımın kendisi) da kendi parametresinin başlığı altında, sağ tarafında açık haliyle durur; çarpanların kendi içi ise kendi başlıklarına gider.

İzahatlar bu dosyada değil, `izahat/` altındaki ayrı dosyalardadır (küme bazlı, F 1'deki kural gereği). Bu dosya yalnız formülleri taşır.

**Taslak işareti:** `-- taslak, tasdik bekliyor` etiketi taşıyan satırlar henüz mühürlenmemiştir; müzakerede teyit edilince etiket kalkar.

---

## ameliye

Tasnif(ameliye) = { tecrit, tecezzi, tefrik ve temyiz, tensip, teşrih }

---

## çeşit

Terkip(çeşit) = NihaiHal × Biçim × Şart × Rükün × Mahiyet

Sual(çeşit) = { hakiki, gayrı hakiki }

Nefis(çeşit) = { nebati, hayvani, insani }

Akıl(çeşit) = { nazari, ameli }

İşlemci(çeşit) = { vahime, mutasarrıfa, mütehayyile }

Şart(çeşit) = { vaz'î-şer'î, ca'lî-irâdî, aklî-âdî }
  (kaynağa göre üç asıl çeşit: şeriatın koyduğu, kulun kendi iradesiyle koyduğu, aklın/tabiatın zaruri kıldığı.
   Dördüncü bir "lisanî ve mantıkî şart edatları" şıkkı bilerek dışarıda bırakıldı: o, şartın kaynağı değil,
   şartın dilde/mantıkta hangi surette ifade edildiği sualine cevaptır — ayrı bir sual, aynı başlığa girmez.)

Vaz'î-Şer'î(çeşit) = { vücûb şartı, merâtib-i akd }
  (merâtib-i akd = İnikad → Sıhhat → Nifaz → Lüzum, zaten mühürlü; vücûb şartı bundan ayrıdır,
   akdin kendi tekamülüyle değil, mükellefiyetin failin sırtına yüklenmesiyle alakalıdır — meselâ zekâtta nisap ve havelân-ı havl, hacda istitaat.)

Ca'lî-İrâdî(çeşit) = { ta'lîkî, takyîdî, fâsih }
  (ta'lîkî: hükmü şüpheli bir hadiseye bağlamak — "gemi gelirse sattım"; takyîdî: tasarrufu bir vazifeye bağlamak; fâsih: tahakkukunda bağı hükümsüz kılan şart.)

Aklî-Âdî(çeşit) = { hayat, kudret }
  (misal kümesidir, tahdit değil: ilim için hayat, teklif/fiil için kudret şarttır — şeriatın değil aklın zaruri kıldığı taban şartlarıdır.)

Tasavvur(çeşit) = { bedihî, nazarî }
  (kıstas: hâsıl olmak için bir tarife muhtaç mı, değil mi.)

Tasdik(çeşit) = { bedihî, nazarî }
  (kıstas: hükme varmak için bir delile/kıyasa muhtaç mı, değil mi.)

Tavassut(çeşit) = { burhânî, cedelî, hitâbî, şiirî, safsatavî }
  (dört ardışık ikili Nakzeyn'in ürünü: yakînî mi → burhânî; değilse müsellem mi → cedelî; değilse zannedilen mi → hitâbî; değilse hayalî mi → şiirî, değilse → safsatavî. Muhakeme(Rükün)'ün "tavassut" unsurunun kendi iç tasnifidir; Muhakeme(Lüzum)'daki burhanî/zannî ayrımı ve Şek-Zan-Yakîn İdraki ile aynı köke bağlanır.)

---

## levazım

İcat(levazım) = { tecrit, temsil ve tenazur, ilga ve ihtilal, tasarruf ve terkip, muhakeme }

---

## merhale

Muhakeme(merhale) = İnikad × Rükün × Sıhhat × Nifaz × Lüzum

Merhale eksikliğinin hükmü:
  İnikad eksik → bâtıl (hiç doğmamış)
  Sıhhat eksik → fasid (doğmuş, sakat)
  Nifaz eksik → mevkuf (askıda, amel doğurmaz)
  Lüzum: burhanî → lâzım (bağlayıcı) · zannî → gayr-ı lâzım (nakzolunabilir)

---

## kuvvet

Nefis(kuvvet) = { muharrike, müdrike }

Aklı Ameli(kuvvet) = { tedbir, … }  -- açık, dökümü tamamlanmadı

---

## hayvani

Muharrike(hayvani) = { şehvet, gazap }

Müdrike(hayvani) = { hissi müşterek, hafıza, işlemci }

---

## insani

Muharrike(insani) = { irade } ∪ Muharrike(hayvani)

Müdrike(insani) = Akıl ∪ Müdrike(hayvani)

---

## Bünye

Bünye = Mevki × Zaruret

Bünye(dâhil, zarurî) = Rükün
Bünye(dâhil, gayr-i zarurî) = Araz
Bünye(hâriç, zarurî) = Şart
Bünye(hâriç, gayr-i zarurî) = Karîne

Rükün: bir varlığın bizzat kendi bünyesine, dokusuna dâhil olan kurucu iç cüzdür (dâhilî zaruret).
Şart: varlığın bünyesine dâhil olmayan, lakin varlığın vücut bulması, işlemesi ve netice vermesi için haricen bulunması icap eden kayıttır (hâricî zaruret).
Araz: varlığın bünyesine dâhil olan, lakin bulunması zarurî olmayan (yokluğu varlığı yok etmeyen) niteliktir (dâhilî gayr-i zaruret).
Karîne: varlığın bünyesine dâhil olmayan, hâriçte bulunması da zarurî olmayan, lakin yine de onunla beraber bulunabilen (mukarin olan) haldir (hâricî gayr-i zaruret).

İzahat: `izahat/rukun_sart/genel.md`

---

## Mevki

Bünye(Mevki) = { dâhil, hâriç }

---

## Zaruret

Bünye(Zaruret) = { zarurî, gayr-i zarurî }

---

## NihaiHal

Terkip(NihaiHal) = { cem'î, imtizâcî }

---

## Biçim

Terkip(Biçim) = { tahsisli, hattî, denklikli, devirli, ağlı }

---

## Şart

Terkip(Şart) = { ??? }  -- açık, tarif bekliyor

---

## Rükün

Terkip(Rükün) = { ??? }  -- açık, tarif bekliyor

Muhakeme(Rükün) = { sual (saik), mevzu (mahkûmun fîh), tavassut (hadd-i evsat), mizan, hüküm (mahkûmun bih) }

Sual(Rükün) = ⟨ sâil (talep eden şuur), mes'ûlün anh (hakkında sual edilen malum zemin), matlûb (aranan meçhul/epistemik yarık) ⟩

Mizan(Rükün) = { kıstas, teaddüdü ihtimal, sükun kabiliyeti }  -- taslak, tasdik bekliyor

Tedbir(Rükün) = { mebde, intikal usulü, gaye }  -- taslak, tasdik bekliyor

**Nakz:** Muhakeme(Rükün)'e "sual" beşinci unsur olarak eklendi, padişah fermanıyla kat'î (F 3-C/13, itiraz yok). Bunun mükerrerlik doğurmaması için "epistemik yarığın varlığı" Muhakeme(İnikad)'dan çıkarıldı — aynı unsur artık yalnız Rükün'de, tek yerde duruyor. Şebeke bu karara göre bağlandı (bkz. Vürûd/Sudûr başlıkları): Merak ve Sual Tevcihi → Muhakeme artık Vâcib.

**Reddedilen teklif (kayıt için):** Düz, seviyesiz bir "Şart(Muhakeme)" ve "Şart(Sual)" kümesi (İnikad/Sıhhat/Nifaz/Lüzum merhalelerinin yanına, onlardan ayrı) teklif edildi, kabul edilmedi. Sebep: teklif edilen beş Şart(Muhakeme) unsurundan dördü ("ehliyet-i müdrike" → İnikad'da zaten var; "liyakat-i mizan" → Sıhhat'teki "kıstasın sıhhati ve liyakati"nin aynısı; "münasebet-i hadd-i evsat" → Sıhhat'teki "illiyet rabıtasının sübutu"nun aynısı; "selâmet ani'l-muarız" → Lüzum'daki "muarız-ı râcihin ademi"nin aynısı) zaten merhalelere dağıtılmış unsurların tekrarıdır; aynı hata Şart(Sual)'de de var ("teaddüd-i ihtimal" ve "adem-i müsâdere", Sual(Sıhhat)'te zaten var). Merhaleli tasnifi terk edip düz listeye dönmek, tam da bu tashihatın kendisinin mahkûm ettiği mükerrerliği yeniden üretiyor.

---

## Mahiyet

Terkip(Mahiyet) = Madde × Kanun

İzahat: `izahat/mahiyet/`

---

## Madde

Mahiyet(Madde) = { maddî, manevî }

Hafıza(Madde) = { maddî, manevî }  -- taslak, tasdik bekliyor (bkz. not: Kuvve-i Hayâl/sûret ↔ maddî bölme, Kuvve-i Hâfıza/mana ↔ manevî bölme)

---

## Kanun

Mahiyet(Kanun) = { fizikî, gayr-i fizikî }

---

## İnikad

Muhakeme(İnikad) = { ehliyet-i müdrikeyi hâiz olmak, mahallin kabil olması }

**Nakz:** "Epistemik yarığın varlığı" buradan çıkarıldı — sebebi Rükün'e taşınmasıdır, aşağıya bakınız.

---

## Sıhhat

Muhakeme(Sıhhat) = { tenakuzsuzluk, kıstasın sıhhati ve liyakati, illiyet rabıtasının sübutu, tahrif ve hileden tecerrüd }

Sual(Sıhhat) = { teaddüd-i ihtimal (muhayyer olmaması), musadere ale'l-matlub olmaması (cevabı içinde gizlememesi), tahayyüz-i hadd (aranan meçhulün hudutlarının muayyen olması) }

**Nakz (F 2-Y gereği açık yazılır):** Önceki taslak (`mevcut-hedef boşluk tespiti, teaddüdü ihtimal, gaye`) nakzedildi. Sebep: "boşluk tespiti" ve "gaye", Sıhhat değil İnikad seviyesindedir — Muhakeme(İnikad)'daki "epistemik yarığın varlığı" ile aynı şeydir, iki başlıkta tekrarlanamaz. Sıhhat'te kalan asıl sual: sual doğmuş (mün'akid) olsa dahi, kendi içinde mugalata barındırmadan, hakiki sual sayılması için ne gerekir.

---

## Nifaz

Muhakeme(Nifaz) = { vakıaya mutabakat (harici gerçeklikle örtüşme), mâni-i aklî ve amelînin ademi (tatbikini engelleyen bir mânîin bulunmaması) }

**Nakz:** Önceki taslaktaki "şüphenin galebe çalmaması (itminan hali)" buradan çıkarıldı, Lüzum'a taşındı — itminan, hükmün yürürlüğe girip girmediğiyle değil, ne derece bağlayıcı olduğuyla alakalıdır.

---

## Lüzum

Muhakeme(Lüzum) = { muarız-ı râcihin ademi (daha kuvvetli zıt bir delilin bulunmaması), tahakkuk-i itminan (şüpheden tecerrüd ederek hükme bağlanmış olması) }

Netice taksimi (şart değil, Lüzum hâsıl olunca hükmün kendi kuvvet derecesidir): burhanî/kat'î ise → lâzım (bağlayıcı, zihin cayamaz) · zannî/ictihadî ise → gayr-ı lâzım (yeni delille nakzolunabilir).

---

## Teşrih

X(Teşrih) = X(Vürûd) × X(Sudûr)   -- her X için genel şema; Teşrih, Vürûd, Sudûr hep başlık kalır, hiçbir yerde özne olmaz

Muhakeme(Teşrih) = Muhakeme(Vürûd) × Muhakeme(Sudûr)

(41-meleke şebekesinin tamamı için aynı şema aşağıdaki Vürûd/Sudûr başlıklarında kurulu; her düğümün kendi Teşrih'i, kendi Vürûd × Sudûr çarpımıdır — ayrı ayrı yazılmadı, tekrar olurdu.)

---

## Vürûd

Müşahede(Vürûd) = { Gaye Belirleme, Merak ve Sual Tevcihi, Deneme-Yanılma, Tetkik }
Hayal(Vürûd) = { Müşahede(Vâcib), Hayal Kurma, Temsil, Teşbih }
Hayal Kurma(Vürûd) = { Hayal, Mana, Merak ve Sual Tevcihi, Sanat }
Tertip(Vürûd) = { Hayal, Tahlil, Terkip, Mantık Yürütme, Tedebbür }
Tecrit(Vürûd) = { Müşahede(Vâcib), Tahlil, Tenkit, Teemmül }
Tasavvur(Vürûd) = { Hayal, Hayal Kurma, Tertip, Tecrit(Vâcib), Tefekkür }
Mana(Vürûd) = { Hayal, Tecrit, Tasavvur, Tahlil, Tefsir, Tevil }
Tahlil(Vürûd) = { Müşahede, Tasavvur, Merak ve Sual Tevcihi, Teemmül, Tetkik }
Terkip(Vürûd) = { Hayal Kurma, Tasavvur(Vâcib), Tahlil, Kıyas, Tefekkür, Tashih }
Tezat(Vürûd) = { Hayal, Tahlil, Münazara, Tetkik }
Tenakuz Bulma(Vürûd) = { Müşahede, Tahlil, Tezat, Mantık Yürütme, Tetkik }
Tenkit(Vürûd) = { Tezat, Tenakuz Bulma, Teemmül, Münazara }
Tasdik(Vürûd) = { Tasavvur, Mana, Terkip, Mantık Yürütme, İspat(Vâcib), Teyit }
Gaye Belirleme(Vürûd) = { Mana, Tedebbür, Muhakeme, Tahsil }
Merak ve Sual Tevcihi(Vürûd) = { Tenakuz Bulma(Vâcib), Gaye Belirleme, Teemmül, Şek-Zan-Yakîn İdraki }
Deneme-Yanılma(Vürûd) = { Hayal Kurma, Merak ve Sual Tevcihi, Gaye Belirleme, İhtimal Hesabı }
İhtimal Hesabı(Vürûd) = { Deneme-Yanılma, Kıyas, Mantık Yürütme, Tedebbür }
Kıyas(Vürûd) = { Hayal Kurma, Tertip, Tezat, Temsil, Teşbih }
Temsil(Vürûd) = { Hayal Kurma, Kıyas, Teşbih, Tefekkür, Tafsil, Sanat }
Teşbih(Vürûd) = { Hayal, Temsil, Tefekkür, Sanat }
Tefekkür(Vürûd) = { Mana, Gaye Belirleme, Merak ve Sual Tevcihi, Teemmül, Tahkik }
İllet Keşfi(Vürûd) = { Müşahede, Tecrit, Tasavvur, Deneme-Yanılma, Tefekkür }
Mantık Yürütme(Vürûd) = { Tertip, Tecrit, Tezat, Kıyas, Tefekkür, İllet Keşfi }
İspat(Vürûd) = { Tertip, Tecrit, Terkip, Kıyas, İllet Keşfi, Mantık Yürütme }
Teemmül(Vürûd) = { Merak ve Sual Tevcihi, Tedebbür, Şek-Zan-Yakîn İdraki, Muhakeme }
Temkin(Vürûd) = { Tasdik, Gaye Belirleme, İhtimal Hesabı, Teemmül, Tahkik, Şek-Zan-Yakîn İdraki }
Tetkik(Vürûd) = { Teemmül, Temkin, Tahkik, Muhakeme, Tafsil }
Tashih(Vürûd) = { Tenakuz Bulma, Tenkit, Deneme-Yanılma, Tetkik, Münazara }
Teyit(Vürûd) = { Deneme-Yanılma, İspat, Tetkik, Tashih, Münazara }
Tahkik(Vürûd) = { Müşahede, Tenkit, İllet Keşfi, İspat, Tashih, Teyit, Münazara }
Tedebbür(Vürûd) = { İhtimal Hesabı, Tefekkür, İllet Keşfi, Temkin, Muhakeme }
Şek-Zan-Yakîn İdraki(Vürûd) = { Tenakuz Bulma, Tenkit, Tasdik, İhtimal Hesabı, İspat, Teyit, Tahkik }
Muhakeme(Vürûd) = { Tasavvur, Tenakuz Bulma, Tenkit, Tasdik, Gaye Belirleme, Mantık Yürütme, İspat, Temkin, Tahkik, Tedebbür, Şek-Zan-Yakîn İdraki, İhtimal Hesabı(Vâcib), Merak ve Sual Tevcihi(Vâcib) }
Tafsil(Vürûd) = { Terkip, Tasdik, Muhakeme, Tefsir }
Tefsir(Vürûd) = { Mana, Kıyas, Tahkik, Muhakeme, Tevil }
Tevil(Vürûd) = { Mana, Tezat, Tenakuz Bulma, İllet Keşfi, Şek-Zan-Yakîn İdraki, Tefsir, Muhakeme }
Fesâhat(Vürûd) = { Temkin, Tashih, Tafsil, Sanat, Talim }
Talâkat(Vürûd) = { Tertip, Tafsil, Fesâhat, Belâgat, Tahsil }
Belâgat(Vürûd) = { Mana, Terkip, Gaye Belirleme, Temsil, Teşbih, Tafsil, Tefsir, Tevil, Fesâhat, Talâkat, Muhakeme, Sanat }
Sanat(Vürûd) = { Hayal, Hayal Kurma, Terkip, Teşbih, Fesâhat, Belâgat }
Münazara(Vürûd) = { Merak ve Sual Tevcihi, Kıyas, İspat, Temkin, Tevil, Fesâhat, Talâkat, Belâgat }
Talim(Vürûd) = { Tertip, Tasdik, Temsil, Teyit, Tafsil, Tefsir, Talâkat, Belâgat }
Tahsil(Vürûd) = { Sanat, Talim }

---

## Sudûr

Müşahede(Sudûr) = { Hayal(Vâcib), Tecrit, Tahlil, İllet Keşfi, Tenakuz Bulma, Tahkik }
Hayal(Sudûr) = { Hayal Kurma, Tertip, Tasavvur, Mana, Tezat, Sanat, Teşbih }
Hayal Kurma(Sudûr) = { Hayal, Tasavvur, Kıyas, Temsil, Deneme-Yanılma, Sanat, Terkip }
Tertip(Sudûr) = { Tasavvur, Mantık Yürütme, Kıyas, İspat, Talim, Talâkat }
Tecrit(Sudûr) = { Tasavvur(Vâcib), Mana, İllet Keşfi, Mantık Yürütme, İspat }
Tasavvur(Sudûr) = { Mana, Tahlil, Terkip(Vâcib), Tasdik, İllet Keşfi, Muhakeme }
Mana(Sudûr) = { Hayal Kurma, Tasdik, Tefekkür, Tefsir, Tevil, Belâgat, Gaye Belirleme }
Tahlil(Sudûr) = { Tertip, Tecrit, Mana, Terkip, Tezat, Tenakuz Bulma }
Terkip(Sudûr) = { Tertip, Tasdik, İspat, Sanat, Tafsil, Belâgat }
Tezat(Sudûr) = { Tenakuz Bulma, Tenkit, Mantık Yürütme, Kıyas, Tevil }
Tenakuz Bulma(Sudûr) = { Tenkit, Tashih, Şek-Zan-Yakîn İdraki, Cerh, Tevil, Muhakeme, Merak ve Sual Tevcihi(Vâcib) }
Tenkit(Sudûr) = { Tecrit, Tashih, Tahkik, Şek-Zan-Yakîn İdraki, Muhakeme }
Tasdik(Sudûr) = { Şek-Zan-Yakîn İdraki, Temkin, Muhakeme, Tafsil, Talim }
Gaye Belirleme(Sudûr) = { Müşahede, Merak ve Sual Tevcihi, Tefekkür, Temkin, Muhakeme, Belâgat, Deneme-Yanılma }
Merak ve Sual Tevcihi(Sudûr) = { Müşahede, Hayal Kurma, Tahlil, Deneme-Yanılma, Tefekkür, Münazara, Teemmül, Muhakeme(Vâcib) }
Deneme-Yanılma(Sudûr) = { Müşahede, İhtimal Hesabı, Tashih, Teyit, İllet Keşfi }
İhtimal Hesabı(Sudûr) = { Deneme-Yanılma, Şek-Zan-Yakîn İdraki, Temkin, Tedebbür, Muhakeme(Vâcib) }
Kıyas(Sudûr) = { Terkip, İhtimal Hesabı, Mantık Yürütme, İspat, Tefsir, Münazara }
Temsil(Sudûr) = { Hayal, Kıyas, Teşbih, Belâgat, Talim }
Teşbih(Sudûr) = { Hayal, Kıyas, Temsil, Sanat, Belâgat }
Tefekkür(Sudûr) = { Tasavvur, Terkip, İllet Keşfi, Mantık Yürütme, Tedebbür, Temsil, Teşbih }
İllet Keşfi(Sudûr) = { Mantık Yürütme, İspat, Tahkik, Tedebbür, Tevil }
Mantık Yürütme(Sudûr) = { Tertip, Tenakuz Bulma, Tasdik, İhtimal Hesabı, İspat, Muhakeme }
İspat(Sudûr) = { Tasdik(Vâcib), Teyit, Tahkik, Şek-Zan-Yakîn İdraki, Muhakeme, Münazara }
Teemmül(Sudûr) = { Tecrit, Tahlil, Tenkit, Tefekkür, Tetkik, Temkin, Merak ve Sual Tevcihi }
Temkin(Sudûr) = { Tetkik, Şek-Zan-Yakîn İdraki, Tedebbür, Muhakeme, Fesâhat, Münazara }
Tetkik(Sudûr) = { Müşahede, Tahlil, Tezat, Tenakuz Bulma, Tashih, Teyit }
Tashih(Sudûr) = { Terkip, Teyit, Tahkik, Fesâhat }
Teyit(Sudûr) = { Tasdik, Tahkik, Şek-Zan-Yakîn İdraki, Talim }
Tahkik(Sudûr) = { Tefekkür, Temkin, Tetkik, Şek-Zan-Yakîn İdraki, Muhakeme, Tefsir }
Tedebbür(Sudûr) = { Tertip, Gaye Belirleme, İhtimal Hesabı, Teemmül, Muhakeme }
Şek-Zan-Yakîn İdraki(Sudûr) = { Merak ve Sual Tevcihi, Teemmül, Temkin, Muhakeme, Tevil }
Muhakeme(Sudûr) = { Gaye Belirleme, Teemmül, Tetkik, Tedebbür, Tafsil, Tefsir, Tevil, Belâgat, Teyit }
Tafsil(Sudûr) = { Temsil, Tetkik, Fesâhat, Talâkat, Belâgat, Talim }
Tefsir(Sudûr) = { Mana, Tafsil, Tevil, Belâgat, Talim }
Tevil(Sudûr) = { Mana, Tefsir, Belâgat, Münazara }
Fesâhat(Sudûr) = { Talâkat, Belâgat, Sanat, Münazara }
Talâkat(Sudûr) = { Belâgat, Münazara, Talim }
Belâgat(Sudûr) = { Talâkat, Sanat, Münazara, Talim }
Sanat(Sudûr) = { Hayal Kurma, Temsil, Teşbih, Fesâhat, Belâgat, Tahsil }
Münazara(Sudûr) = { Tezat, Tenkit, Tashih, Teyit, Tahkik }
Talim(Sudûr) = { Fesâhat, Tahsil }
Tahsil(Sudûr) = { Gaye Belirleme, Talâkat, Zâtî Melekeleşme }

(Cerh, Mukayese, Zâtî Melekeleşme kendi Vürûd/Sudûr'u tanımlanmamış uç düğümlerdir — bkz. açık notlar.)

---

## Metâlib

Metâlib(çeşit) = { hel-i basit, mâ, hel-i mürekkebe, lime }

Tükenme isbatı: herhangi bir sual, bir mevzu hakkında ya sırf kendisi (hel-i basit: var mıdır; mâ: nedir) ya da bir mahmul ile birleşimi (hel-i mürekkebe: böyle midir; lime: niçindir) hakkındadır — bir önerme yalnız mevzu ve mahmulden kurulur, üçüncü bir cüzü yoktur, o yüzden bu ikilik tüketicidir.

**Kayıt (F 2-Y gereği, kapsam dar tutulur):** Bu dörtlü yalnız **sualin şeklini** (var mı / nedir / böyle mi / niçin) tüketir; sualin **muhtevasını** (Hel-i mürekkebe veya Lime sorulurken, sorulan vasfın kemiyet mi keyfiyet mi mekân mı zaman mı olduğu — "nasıl", "ne kadar", "nerede", "ne zaman" gibi) tüketmez. O, ayrı bir teoridir (klasik On Makûle: cevher, kemiyet, keyfiyet, izafet, eyne, metâ, vaz', mülk, fiil, infial) ve henüz açılmadı. Bu yüzden "her sual zaruri olarak Metâlib'in dördünden biridir" iddiası yalnız **şekil** seviyesinde doğrudur; muhteva seviyesinde tükenmişlik ayrıca ispatlanmalıdır, şimdilik meçhuldür.

**Reddedilen teklif (kayıt için):** Rükün'ün "madde+suret" ikiliğine indirgenmesi (İllet-i Mâddiye+Sûriyye üzerinden) tekrar gündeme getirilmiş, tekrar reddedilmiştir. Sebep: manevî varlıklarda (mesela bir matematik formülünde) madde yoktur, ve "suret" sanılan şey (formülün yazılışı/notasyonu) aynı formül farklı notasyonlarla ifade edilebildiği için bizzat arazdır, rükün değildir. Madde-suret ikiliği yalnız maddî varlıklara mahsustur, âlemşümul bir Rükün tarifi olamaz.

**Açık bırakılan:** Nispet(çeşit) = {zâtî, vücûdî, fâilî, zamanî, râbıtalı, gaî} taslağı, Metâlib'in altına bir tatbik listesi olarak önerilmişti; bu indirgeme ikna edici bulunmadığı için mühürlenmedi. Nispet, kendi başına ayrı bir müzakere konusu olarak açık kalıyor.

---

## Mâlum

Mâlum = Tasavvur ∪ Tasdik

Kıstas: herhangi bir idrake tek vasıf sorulur — "bu idrak bir hüküm taşıyor mu?" Nakzeyn Kanunu gereği cevap evet ya da hayır, üçüncüsü yoktur; evet ise Tasdik, hayır ise Tasavvur. Mâ (Metâlib) → Tasavvur talebidir; Hel-i basit, Hel-i mürekkebe, Lime → Tasdik talebidir. Makûlât (henüz açılmamış On Makûle), yalnız Tasavvur tarafının kendi iç sınıflamasıdır.

**Kayıt (kapsam ve dayanak açıkça yazılır):** Bu ikiliğin tükenmişliği, Nakzeyn Kanunu'nun kendisine dayanır; Nakzeyn'in kendisi ispat edilemez, yalnız inkârının kendini nakzettiği gösterilebilir (Aristo, Metafizik Γ) — devir/teselsülün mecburen bittiği yerdir. Ayrıca: "hüküm taşıma" kıstasının seçilmesi **mutlak** değil, **maksada nispetle** zarurîdir — bizim maksadımız (insanın idrak/müdrike kanadını çıkarıp mekanikleştirmek) bu kıstası gerektirir; farklı bir maksatla (mesela hissî/vehmî/aklî hâsıl oluş tarzına göre) başka, ona dik bir kesit alınabilirdi, bu kesit onu çürütmez.

**Yeri:** Mâlum, Nefis(kuvvet)'in yalnız **Müdrike** kanadını doldurur. Muharrike kanadının (irade, şehvet, gazap) kendi zaruret isbatı henüz yapılmadı, açık.

İzahat: `izahat/malum/`

---

## Tarif

Tarif = Kemal × Unsur

Kemal = { tam, nakıs }
Unsur = { zâtî (→ Hadd), arazî (→ Resm) }

Nazarî Tasavvur'un (bir tarifle hâsıl olan tasavvurun) kendi iç tasnifidir; Unsur ekseni doğrudan Bünye = Mevki × Zaruret'in bir tatbikidir (zâtî unsurla tarif = Hadd, arazî unsurla tarif = Resm).

---

## Vücûb

Teşrih(Vücûb) = { Vâcib, Mümkün }

Kaide: her Vürûd/Sudûr unsuru bu iki dereceden birini taşır. **Mümkün varsayılandır ve etiketlenmez**; yalnız **Vâcib** olan unsur `(Vâcib)` ile işaretlenir. Bu, hem az başlıkla idare eder hem de yazımı sadeleştirir.

---

## İzahat haritası

- ameliye → `izahat/tasnif/`
- çeşit (Terkip kanadı) → `izahat/terkip/` (henüz açılmadı)
- çeşit (Sual, Nefis, Akıl, İşlemci kanatları) → henüz izahat dosyası açılmadı
- levazım → `izahat/icat/`
- merhale, İnikad, Rükün (Muhakeme kanadı), Sıhhat (Muhakeme kanadı), Nifaz, Lüzum → `izahat/muhakeme/`
- Rükün (Mizan, Tedbir kanatları — taslak), Sıhhat (Sual kanadı — taslak) → henüz izahat dosyası açılmadı, formül de tasdik bekliyor
- kuvvet, hayvani, insani (Nefis hiyerarşisi) → prose izahatı `CLAUDE.md` § 4-I'de (İbn Sînâ Nefs Şeması) mevcut; mimari küme-dosyası olarak henüz ayrılmadı
- Mahiyet, Madde, Kanun → `izahat/mahiyet/`
- Teşrih, Vürûd, Sudûr, Vücûb → `izahat/tesrih/sebeke.md` (41-meleke şebekesinin tam Vücûb taraması)
- Şart (çeşit, Vaz'î-Şer'î, Ca'lî-İrâdî, Aklî-Âdî) → henüz izahat dosyası açılmadı
- Sual(Rükün) → henüz izahat dosyası açılmadı
- Bünye, Mevki, Zaruret (Rükün/Şart/Araz/Karîne dörtlüsü) → `izahat/rukun_sart/genel.md`
- Metâlib → henüz izahat dosyası açılmadı
- Mâlum → `izahat/malum/genel.md`
- Tasavvur(çeşit), Tasdik(çeşit), Tarif, Tavassut(çeşit) → henüz ayrı izahat dosyası açılmadı; temel usul (kıstas+Nakzeyn+isimlendirme+dehliz) `izahat/tasnif/tefrik_ve_temyiz.md`'ye işlendi

## Açık notlar (41-meleke şebekesi)

- Bütün şebeke artık `## Vürûd` ve `## Sudûr` başlıkları altında, her düğüm kendi `X(Vürûd)`/`X(Sudûr)` kümesiyle mühürlendi (43 düğüm, ~200 kenar). Vürûd, Sudûr'un matematiksel tersi olarak (her düğüm için "beni kim çıktısında taşıyor" taraması ile) türetildiği için ikisi **inşa gereği** simetriktir — bir daha asimetri çıkamaz.
- Bu türetme sırasında iki ek hata yakalandı ve düzeltildi: **(1)** Tenkit→Tecrit kenarı, tartışmalı olan ters yönle (Tecrit→Tenkit, o silinmişti) karıştırılıp yanlışlıkla silinmişti — geri eklendi, çünkü kendi başına hiç tartışmasız, tutarlı bir kenardı. **(2)** Sanat→Belâgat kenarı asıl veride Sanat'ın çıktısında vardı ama Belâgat'ın girdisinde hiç yoktu — bu, ilk sweep'te (18 kenarlık listede) gözden kaçmış 19. bir asimetriydi; şimdi eklendi.
- İlk taramada 6 kenar Vâcib çıktı (bkz. `izahat/tesrih/sebeke.md`); yedincisi (Merak ve Sual Tevcihi → Muhakeme) sonradan, Muhakeme(Rükün)'e sual eklenmesi kararıyla Vâcib olarak eklendi. Tasavvur → Terkip hâlâ güçlü bir "rükün şüphesi" taşıyor (henüz taşınmadı, padişah kararını bekliyor).
- Bu şebeke, Muhakeme dışındaki hiçbir düğüm için henüz kendi `X(Teşrih)` formülüne (Vürûd × Sudûr çarpımına) ayrı ayrı dökülmedi — istenirse tek satırlık genel şema (`X(Teşrih) = X(Vürûd) × X(Sudûr)`) zaten her düğüme otomatik uygulanıyor.
- **Mukayese** = 42. meleke olarak kabul edildi; kendi Vürûd/Sudûr'u henüz verilmedi, açık.
- **Cerh**, Tenakuz Bulma'nın tek taraflı çıktısı olarak yerinde bırakıldı, genişletilmedi.
- `izahat/tesrih/sebeke.md` artık ikincil/anlatı dosyasıdır (Vâcib gerekçeleri, rükün-şüphesi tartışması); kanonik formüller burada, FORMULLER.md'dedir.
