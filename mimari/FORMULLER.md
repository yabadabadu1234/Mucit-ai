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

---

## ameliye

Tasnif(ameliye) = { tecrit, tecezzi, tefrik ve temyiz, tensip, teşrih }

---

## çeşit

Terkip(çeşit) = NihaiHal × Biçim × Şart × Rükün × Mahiyet

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

---

## Mahiyet

Terkip(Mahiyet) = { maddî, gayr-i maddî, fizikî, gayr-i fizikî }
  (ayrık değil: maddî ⊂ fizikî -- maddî olan her şey fizikîdir, fizikî olan her şey maddî değildir)

---

## İnikad

Muhakeme(İnikad) = { ehliyet-i müdrikeyi hâiz olmak, epistemik yarığın varlığı, mahallin kabil olması }

---

## Sıhhat

Muhakeme(Sıhhat) = { tenakuzsuzluk, kıstasın sıhhati ve liyakati, illiyet rabıtasının sübutu, tahrif ve hileden tecerrüd }

---

## Nifaz

Muhakeme(Nifaz) = { şüphenin galebe çalmaması (itminan hali), vakıaya intibak kabiliyeti }

---

## Lüzum

Muhakeme(Lüzum) = { burhanî / kat'î olma, zannî / ictihadî olma }

---

## İzahat haritası

- ameliye → `izahat/tasnif/`
- çeşit → `izahat/terkip/` (henüz açılmadı)
- levazım → `izahat/icat/`
- merhale, İnikad, Rükün (Muhakeme kanadı), Sıhhat, Nifaz, Lüzum → `izahat/muhakeme/`
- NihaiHal, Biçim, Şart, Rükün (Terkip kanadı), Mahiyet → henüz ayrı izahat dosyası açılmadı; Terkip için müzakere sürüyor (bkz. sohbet geçmişi)
