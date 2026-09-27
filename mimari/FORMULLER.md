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

Muhakeme(Rükün) = { mevzu (mahkûmun fîh), tavassut (hadd-i evsat), mizan, hüküm (mahkûmun bih) }

Mizan(Rükün) = { kıstas, teaddüdü ihtimal, sükun kabiliyeti }  -- taslak, tasdik bekliyor

Tedbir(Rükün) = { mebde, intikal usulü, gaye }  -- taslak, tasdik bekliyor

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

Muhakeme(İnikad) = { ehliyet-i müdrikeyi hâiz olmak, epistemik yarığın varlığı, mahallin kabil olması }

---

## Sıhhat

Muhakeme(Sıhhat) = { tenakuzsuzluk, kıstasın sıhhati ve liyakati, illiyet rabıtasının sübutu, tahrif ve hileden tecerrüd }

Sual(Sıhhat) = { mevcut-hedef boşluk tespiti, teaddüdü ihtimal, gaye }  -- taslak, tasdik bekliyor

---

## Nifaz

Muhakeme(Nifaz) = { şüphenin galebe çalmaması (itminan hali), vakıaya intibak kabiliyeti }

---

## Lüzum

Muhakeme(Lüzum) = { burhanî / kat'î olma, zannî / ictihadî olma }

---

## Teşrih

X(Teşrih) = Vürûd(X) × Sudûr(X)   -- her X için genel şema; Teşrih başlık kalır, hiçbir yerde özne olmaz

Muhakeme(Teşrih) = Vürûd(Muhakeme) × Sudûr(Muhakeme)

---

## Vürûd

Vürûd(Muhakeme) = { Tasavvur, Tenakuz Bulma, Tenkit, Tasdik, Gaye Belirleme,
                     Mantık Yürütme, İspat, Temkin, Tahkik, Tedebbür,
                     Şek-Zan-Yakîn İdraki, İhtimal Hesabı(Vâcib) }
                     -- diğer 11 unsurun vücûb derecesi henüz tayin edilmedi

---

## Sudûr

Sudûr(Muhakeme) = { Gaye Belirleme, Teemmül, Tetkik, Tedebbür, Tafsil,
                     Tefsir, Tevil, Belâgat, Teyit }

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

## Açık notlar (41-meleke şebekesi)

- Tam düzeltilmiş Sudûr/Vürûd tablosu ve Vücûb (Vâcib/Mümkün) taraması `izahat/tesrih/sebeke.md`'de: 43 düğüm, ~200 kenar tarandı, yalnız 6 kenar Vâcib çıktı, bunlardan yalnız **Tasavvur → Terkip** güçlü bir "rükün şüphesi" taşıyor (henüz taşınmadı, padişah kararını bekliyor).
- Bu şebeke, Muhakeme dışındaki hiçbir düğüm için henüz kendi `X(Teşrih)` formülüne dökülmedi (yalnız Muhakeme(Teşrih) FORMULLER.md'de sealed).
- **Mukayese** = 42. meleke olarak kabul edildi; kendi Girdi/Çıktı listesi henüz verilmedi, açık.
- **Cerh**, Tenakuz Bulma'nın tek taraflı çıktısı olarak yerinde bırakıldı, genişletilmedi.
