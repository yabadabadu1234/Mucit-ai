# FORMÜLLER

Bu dosya mimarî müzakerede mühürlenen bütün formülleri tutar. Kaide: **tek başlıkta tek sualin cevabı**. Farklı sualin cevabı, aynı ismi taşısa da (mesela "tecrit" hem Tasnif'te hem İcat'ta geçer), kendi başlığından çıkmaz.

İzahatlar bu dosyada değil, `izahat/` altındaki ayrı dosyalardadır. Bu dosya yalnız küme formülünü taşır.

---

## Tasnif(ameliye)

Tasnif(ameliye) = { tecrit, tecezzi, tefrik ve temyiz, tensip, teşrih }

İzahat: `izahat/tasnif/`

---

## Terkip(çeşit)

Terkip = NihaiHal × Biçim × Şart × Rükün × Mahiyet

NihaiHal = { cem'î, imtizâcî }

Biçim = { tahsisli, hattî, denklikli, devirli, ağlı }

Şart = { ??? }  -- açık, tarif bekliyor

Rükün = { ??? }  -- açık, tarif bekliyor

Mahiyet = { maddî, gayr-i maddî, fizikî, gayr-i fizikî }
  (ayrık değil: maddî ⊂ fizikî -- maddî olan her şey fizikîdir, fizikî olan her şey maddî değildir)

---

## İcat(levazım)

İcat(levazım) = { tecrit, temsil ve tenazur, ilga ve ihtilal, tasarruf ve terkip, muhakeme }

İzahat: `izahat/icat/`

Not: İcat'taki `muhakeme` maddesinin kendi başına açılımı, aşağıdaki `Muhakeme(merhale)` kümesidir.

---

## Muhakeme(merhale)

Fıkıh usulünün in'ikad · rükün · sıhhat · nifaz · lüzum hiyerarşisinin muhakeme nazariyesine tatbikidir. Beş nesnenin çarpımıdır (n × m × … 5 tane):

Muhakeme = İnikad × Rükün × Sıhhat × Nifaz × Lüzum

İnikad = { ehliyet-i müdrikeyi hâiz olmak, epistemik yarığın varlığı, mahallin kabil olması }

Rükün = { mevzu (mahkûmun fîh), tavassut (hadd-i evsat), mizan, hüküm (mahkûmun bih) }

Sıhhat = { tenakuzsuzluk, kıstasın sıhhati ve liyakati, illiyet rabıtasının sübutu, tahrif ve hileden tecerrüd }

Nifaz = { şüphenin galebe çalmaması (itminan hali), vakıaya intibak kabiliyeti }

Lüzum = { burhanî / kat'î olma, zannî / ictihadî olma }

Merhale eksikliğinin hükmü (bkz. `izahat/muhakeme/genel.md`):
  İnikad eksik → bâtıl (hiç doğmamış)
  Sıhhat eksik → fasid (doğmuş, sakat)
  Nifaz eksik → mevkuf (askıda, amel doğurmaz)
  Lüzum: burhanî → lâzım (bağlayıcı) · zannî → gayr-ı lâzım (nakzolunabilir)

İzahat: `izahat/muhakeme/`
