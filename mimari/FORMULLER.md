# FORMÜLLER

Bu dosya mimarî müzakerede mühürlenen bütün formülleri tutar. İzahat (şerh) burada değildir — `izahat/*`tedir; bu dosya yalnız formüldür.

## Notasyon

```
κ            kıstas (tasnif ölçütü, bir vasıf/sual)
⟺ₜ           Nakzeyn'le tükenmişlik: ∀x (κ(x) ∨ ¬κ(x))
⊢            mühürlü (sabit)
⊬            mühürsüz / nakzedildi / reddedildi
⊳            X, Y'nin kısmı/dalıdır (X ⊂ Y, alt-dal)
⋉            tatbik (bir usulün/kümenin başka mevzua uygulanışı)
≔            tarif (tanım)
∵ ∴          çünkü / dolayısıyla
≺            öncelik (zaman/illiyet sırası, "A, B'den önce")
```

**Kural-1:** `Küme(Başlık)` — Başlık = sual (parametre), Küme = özne. Başlık hiçbir yerde özne olmaz.
**Kural-2:** `X = a×b×c` ⟹ ∀i∈{a,b,c}: `i(başlığı)` kendi başlığı altında ayrı blokta birikir.
**Kural-3:** `⊬ (taslak)` = tasdik bekliyor.

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

```
Şart(çeşit) = { vazʻî-şerʻî, caʻlî-irâdî, aklî-âdî }
  κ = vâzıʻ(x)                      [şeriat / kul-iradesi / akıl-tabiat]
  Lisânî ∉ küme  ∵ κ(Lisânî) = ifade-sûreti ≠ vâzıʻ

Vazʻî-Şerʻî(çeşit) = { vücûb-şartı, merâtib-i-akd }
  merâtib-i-akd ≔ İnikad→Sıhhat→Nifaz→Lüzum   [⊢ ayrıca, bkz. § merhale]
  vücûb-şartı ⊥ merâtib-i-akd   ∵ κ(vücûb)=teklif-tevcihi ≠ κ(merâtib)=akdin-tekâmülü
  misal: (nisap ∧ havelân-ı-havl) → vücûb(zekât) ; istitâʻa → vücûb(hac)

Caʻlî-İrâdî(çeşit) = { taʻlîkî, takyîdî, fâsih }
  taʻlîkî(H)  ≔ doğuş(H) ⟸ vukûʻ(hâdise-i-müşekkek)
  takyîdî(H)  ≔ H ⊃ vazife(k)
  fâsih(H)    ≔ vukûʻ(şart) → ¬nâfiz(H)

Aklî-Âdî(çeşit) ⊇ { hayat, kudret }        [misal kümesi, tahdit değil]
  hayat → şart(ilim) ;  kudret → şart(teklif ∧ fiil)

Tasavvur(çeşit) = { bedihî, nazarî }        κ = muhtâc(tarif)
Tasdik(çeşit)   = { bedihî, nazarî }        κ = muhtâc(delil ∨ kıyas)

Tavassut(çeşit) = { burhânî, cedelî, hitâbî, şiirî, safsatavî }
  κ₁=yakînî(öncül)            → burhânî
  ¬κ₁ ∧ κ₂=müsellem            → cedelî
  ¬κ₁∧¬κ₂ ∧ κ₃=maznûn          → hitâbî
  ¬κ₁∧¬κ₂∧¬κ₃ ∧ κ₄=muhayyel    → şiirî
  ¬κ₁∧¬κ₂∧¬κ₃∧¬κ₄             → safsatavî
  ⋉ Muhakeme(Rükün).tavassut, Muhakeme(Lüzum), Şek-Zan-Yakîn İdraki
```

---

## levazım

İcat(levazım) = { tecrit, temsil ve tenazur, ilga ve ihtilal, tasarruf ve terkip, muhakeme }

---

## merhale

Muhakeme(merhale) = İnikad × Rükün × Sıhhat × Nifaz × Lüzum

```
¬İnikad → bâtıl
¬Sıhhat → fasid
¬Nifaz  → mevkuf
Lüzum: burhânî → lâzım  ;  zannî → gayr-ı lâzım
```

---

## kuvvet

Nefis(kuvvet) = { muharrike, müdrike }

Aklı Ameli(kuvvet) = { tedbir, … }  ⊬ (dökümü tamamlanmadı)

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

```
Bünye = Mevki × Zaruret

Bünye(dâhil,zarurî)        = Rükün
Bünye(dâhil,gayr-i-zarurî) = Araz
Bünye(hâriç,zarurî)        = Şart
Bünye(hâriç,gayr-i-zarurî) = Karîne

Rükün(x,W)  ≔ x∈dâhil(W) ∧ zarurî(x,W)     [¬x → ¬W, mutlak adem]
Şart(x,W)   ≔ x∈hâriç(W) ∧ zarurî(x,W)     [¬x → ¬W, ama W ara-hâlde kalabilir: bâtıl/fasid/mevkuf/gayr-i-lâzım]
Araz(x,W)   ≔ x∈dâhil(W) ∧ ¬zarurî(x,W)    [¬x ↛ ¬W]
Karîne(x,W) ≔ x∈hâriç(W) ∧ ¬zarurî(x,W)    [x, W'ya ne vücûden ne fiilen tesir eder]
```

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

Terkip(Şart) = { ??? }  ⊬ (açık)

---

## Rükün

Terkip(Rükün) = { ??? }  ⊬ (açık)

Muhakeme(Rükün) = { sual (saik), mevzu (mahkûmun fîh), tavassut (hadd-i evsat), mizan, hüküm (mahkûmun bih) }

Sual(Rükün) = ⟨ sâil, mes'ûlün anh, matlûb ⟩

Mizan(Rükün) = { kıstas, teaddüdü ihtimal, sükun kabiliyeti }  ⊬ (taslak)

Tedbir(Rükün) = { mebde, intikal usulü, gaye }  ⊬ (taslak)

```
Nakz [F 3-C/13, kat'î, itiraz yok]:
  Muhakeme(Rükün) += sual
  ⟹ epistemik-yarık ∉ Muhakeme(İnikad)         [mükerrerlik-ademi]
  ⟹ Merak ve Sual Tevcihi(Vâcib) → Muhakeme     [şebekede bağlandı]

⊬ (reddedildi): Şart(Muhakeme)ᵈüz , Şart(Sual)ᵈüz
  ∵ {ehliyet-i-müdrike, liyakat-i-mizan, münasebet-i-hadd-i-evsat, selâmet-ani'l-muarız}
      ⊂ İnikad ∪ Sıhhat ∪ Lüzum                 [mükerrer]
  ∵ {teaddüd-i-ihtimal, adem-i-müsâdere} ⊂ Sual(Sıhhat)   [mükerrer]
```

---

## Mahiyet

Terkip(Mahiyet) = Madde × Kanun

İzahat: `izahat/mahiyet/`

---

## Madde

Mahiyet(Madde) = { maddî, manevî }

```
Hafıza(Madde) = { maddî, manevî }  ⊬ (taslak)
  maddî ≈ Kuvve-i-Hayâl(sûret)
  manevî ≈ Kuvve-i-Hâfıza(mana)
```

---

## Kanun

Mahiyet(Kanun) = { fizikî, gayr-i fizikî }

---

## İnikad

Muhakeme(İnikad) = { ehliyet-i müdrike, mahallin kabîliyeti }

Nakz: epistemik-yarık ∉ (→ Rükün'e nakl, bkz. § Rükün)

---

## Sıhhat

Muhakeme(Sıhhat) = { tenakuzsuzluk, kıstasın sıhhati ∧ liyakati, illiyet rabıtasının sübutu, tahrif ∧ hileden tecerrüd }

Sual(Sıhhat) = { teaddüd-i ihtimal, ¬musâdere-ale'l-matlub, tahayyüz-i hadd }

```
Nakz [F 2-Y]: { boşluk-tespiti, gaye } ⊬
  ∵ ≡ Muhakeme(İnikad).epistemik-yarık   [mükerrer, İnikad seviyesi]
```

---

## Nifaz

Muhakeme(Nifaz) = { vâkıaya mutâbakat, ¬mâni(aklî ∨ amelî) }

Nakz: itminan ⊬ (buradan) → Lüzum'a nakl

---

## Lüzum

Muhakeme(Lüzum) = { ¬muârız-ı râcih, tahakkuk-i itminan }

```
netice-taksimi (şart değil, sonucun kuvvet derecesi):
  burhânî → lâzım        (zihin cayamaz)
  zannî   → gayr-ı lâzım (nakzolunabilir)
```

---

## Teşrih

```
∀X: X(Teşrih) = X(Vürûd) × X(Sudûr)
Muhakeme(Teşrih) = Muhakeme(Vürûd) × Muhakeme(Sudûr)
```

41-meleke şebekesinin tamamı aynı şemaya tâbidir (§ Vürûd, § Sudûr); her düğüm için ayrı ayrı yazılmaz, tekrar olur.

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

Vürûd(Cerh) = Sudûr(Cerh) = ∅ (tanımsız) — aynen Mukayese, Zâtî Melekeleşme

---

## Metâlib

```
Metâlib(çeşit) = { hel-i basit, mâ, hel-i mürekkebe, lime }

kaziyye ≔ (mevzu, mahmul)
⟺ₜ: κ=sırf-mevzu(sual)? → {hel-i-basit,mâ} ; ¬κ=mevzu+mahmul → {hel-i-mürekkebe,lime}
  hel-i-basit ≔ var(mevzu)?
  mâ          ≔ mahiyet(mevzu)?
  hel-i-mürekkebe ≔ sâbit(mevzu,mahmul)?
  lime        ≔ illet(sübut)?

⊢ yalnız Şekil'de ; Muhteva ⊳ Makûlât (kısmî ⊢, bkz. § Makûlât)

⊬ (reddedildi): Rükün ≟ Madde×Suret
  ∵ manevî-varlıkta madde=∅, "suret"(=notasyon) değişken → araz, rükün değil

⊬ (nakz): Nispet(çeşit) müstakil-küme  → bkz. § Mâlum
```

---

## Makûlât

```
Mevcûd = Cevher ⊔ Araz                    κ = kâim-bi-nefsihî(x)?
Araz(çeşit) = { zâtî, izafî }             κ = nazar-ilâ-zâtihî(x)?
Zâtî(çeşit) = { kemiyet, keyfiyet }       κ = münkasım-bi'l-mıkdâr(x)?
  [not: bu kemiyet/keyfiyet ≠ Tasdik(Kemiyet)/Tasdik(Keyfiyet); kök bir, mevzu ayrı]

İzafî(çeşit) = { izafet, eyne, metâ, vazʻ, mülk, fiʻl, infiʻal }   ⊬ (yalnız enümere, tükenmişlik ispatsız)

Makûlât(çeşit) = Cevher ⊔ Zâtî ⊔ İzafî
  = { cevher, kemiyet, keyfiyet, izafet, eyne, metâ, vazʻ, mülk, fiʻl, infiʻal }

⊢: {Cevher/Araz, Zâtî/İzafî, Kemiyet/Keyfiyet}   [her biri κ+Nakzeyn]
⊬: İzafî'nin 7'si arası kesim   [enümere, zincir yok]
```

---

## Mâlum

```
Mâlum = Tasavvur ⊔ Tasdik          κ = hüküm-taşır(idrak)?
  κ(x) → Tasdik(x) ; ¬κ(x) → Tasavvur(x)

Tasavvur(Metâlib) = { mâ }
Tasdik(Metâlib)   = { hel-i basit, hel-i mürekkebe, lime }
Mâ(çeşit) = Makûlât(çeşit)

Dayanak: ⟺ₜ(Mâlum) ⟸ Nakzeyn
  Nakzeyn ⊬ (doğrudan ispat) ; ⊢ yalnız (inkâr → kendini-nakz)   [Aristo, Metafizik Γ]
  κ-seçimi ≠ mutlak ; κ ⋉ maksad(insan.müdrike → mekanikleştirme)

Yer: Mâlum ⊂ Nefis(kuvvet).Müdrike ; Nefis(kuvvet).Muharrike ⊬ (zaruret-isbatsız)

⊬ (nakz) Nispet(çeşit):
  zâtî      ⊳ Mâ
  vücûdî    ⊳ Hel-i-basit
  zamanî    ⊳ Hel-i-mürekkebe   [= Veche/Merhale: İnikad→Sıhhat→Nifaz→Lüzum]
  fâilî     ⊳ Lime.İllet-i-Fâiliye
  râbıtalı  ⊳ Lime.İllet-i-Fâiliye ⋉ şebeke (Vürûd/Sudûr)
  gaî       ⊳ Lime.İllet-i-Gâiye
  eksik: Lime.İllet-i-Mâddiye, Lime.İllet-i-Sûriyye ∉ Nispet   [sorulmamış, reddedilmemiş]
```

İzahat: `izahat/malum/`

---

## Tarif

```
Tarif = Kemal × Unsur
Kemal = { tam, nakıs }
Unsur = { zâtî → Hadd, arazî → Resm }      ⋉ Bünye
```

---

## Vücûb

```
Tasdik(Vücûb) = { vâcib, mümkün, mümteni }
  κ₁=muhal(yokluk)? → vâcib
  ¬κ₁ ∧ κ₂=muhal(varlık)? → mümteni
  ¬κ₁ ∧ ¬κ₂ → mümkün

Teşrih(Vücûb) = { Vâcib, Mümkün } = Tasdik(Vücûb) ⋉ kenar
  [mümteni ∉ kenar: listede-yok zaten yok demektir]

kural: varsayılan=Mümkün (etiketsiz) ; Vâcib=(Vâcib)
```

---

## Vâcibü'l-Vücûd

```
1)  Mevcûd(Vücûb) = { Vâcibü'l-Vücûd, Mümkinü'l-Vücûd }        [mümteni ∉ Mevcûd]
    κ = zarurî-bizatihî(vücûd)?

2)  Mümkinü'l-Vücûd(Şart) = { müreccih-i hâricî }
    ⟸ ¬(tereccüh bilâ müreccih)     [sebepsiz tercih = nakz]

3)  Silsile-i Esbâb(Nihayet) = { Vâcibü'l-Vücûd }
    devir:    A≺B≺A  ⟹  A≺A            (muhal)
    teselsül: ∀cüz mümkin ⟹ küll mümkin ⟹ küll ⋉ (2)   [erteler, gidermez]

∴  ∃! Vâcibü'l-Vücûd                    [1,2,3'ten]

4)  Vâcibü'l-Vücûd(Basitlik) = { basit }
    mürekkeb ⟹ ictimâʻ-i-ecza ⋉ (2) ⟹ muhtâc   [Vâcib-tarifiyle çelişki]

5)  |{x : x Vâcibü'l-Vücûd}| = 1
    ∃x≠y (ikisi Vâcib) ⟹ temayüz ⟹ terkib(cins,fasıl) ⟹ ¬(4)   [çelişki]

6)  Vâcibü'l-Vücûd(Zaman) = { ezelî, ebedî }
    bidâyet ∨ nihâyet ⟹ tagayyür ⟹ ⋉(2)-muhtaçlık   [Vâcib'e münâfî]

    Vâcibü'l-Vücûd(Kıyam) = { bi-nefsihî }
    ⋉ Makûlât.Cevher   [en tam mertebe: mevzûsuz ∧ şartsız kıyam]

    Vâcibü'l-Vücûd(Muhalefet) = { li'l-havâdis }
    ⟸ (1): Vâcib ∩ Mümkin = ∅ ; havâdis ⊂ Mümkin
```

İzahat: `izahat/vacibul_vucud/genel.md`

---

## Kemiyet

Tasdik(Kemiyet) = { küllî, cüz'î }        κ = şümul(bütün-fert)?

---

## Keyfiyet

```
Tasdik(Keyfiyet) = { mûcibe, sâlibe }     κ = isbat(x)?
Kemiyet × Keyfiyet = { küllî-mûcibe, küllî-sâlibe, cüz'î-mûcibe, cüz'î-sâlibe }   [Aristo kıyas tabanı]
```

---

## Basitlik

Basitlik(çeşit) = { basit, mürekkep }     κ = tek-cüz(x)?  ⋉ { Tasavvur, Tasdik }

---

## Menşe

```
Tasavvur(Menşe) = { hissî, hayalî, vehmî, aklî }
  κ₁=maʻa'l-madde(ân)? → hissî
  ¬κ₁ ∧ κ₂=sırf-suret?  → hayalî
  ¬κ₁∧¬κ₂: küllî(mana)? → aklî : vehmî
  ⋉ Nefis(Hissi-müşterek, Hafıza/Mütehayyile, Vahime, Akıl)
```

---

## İzahat haritası

- ameliye → `izahat/tasnif/`
- çeşit (Terkip kanadı) → `izahat/terkip/` ⊬ (henüz açılmadı)
- çeşit (Sual, Nefis, Akıl, İşlemci kanatları) ⊬
- levazım → `izahat/icat/`
- merhale, İnikad, Rükün (Muhakeme kanadı), Sıhhat (Muhakeme kanadı), Nifaz, Lüzum → `izahat/muhakeme/`
- Rükün (Mizan, Tedbir — ⊬ taslak), Sıhhat (Sual kanadı — ⊬ taslak)
- kuvvet, hayvani, insani → `CLAUDE.md` § 4-I (İbn Sînâ Nefs Şeması), mimarî küme-dosyası ⊬
- Mahiyet, Madde, Kanun → `izahat/mahiyet/`
- Teşrih, Vürûd, Sudûr, Vücûb → `izahat/tesrih/sebeke.md`
- Şart (çeşit + 3 kol) ⊬
- Sual(Rükün) ⊬
- Bünye, Mevki, Zaruret → `izahat/rukun_sart/genel.md`
- Metâlib, Makûlât, Cevher/Araz/Zâtî/İzafî ⊬
- Vâcibü'l-Vücûd → `izahat/vacibul_vucud/genel.md`
- Mâlum → `izahat/malum/genel.md`
- Tasavvur(çeşit), Tasdik(çeşit), Tarif, Tavassut(çeşit), Tasavvur(Menşe), Tasdik(Vücûb/Kemiyet/Keyfiyet), Basitlik(çeşit) ⊬ — temel usul (κ+Nakzeyn+isim+dehliz) `izahat/tasnif/tefrik_ve_temyiz.md`'de

## Açık notlar (41-meleke şebekesi)

```
Vürûd(X) ≔ { Y : X ∈ Sudûr(Y) }     [inşa gereği simetrik, asimetri çıkamaz]

Düzeltilen 2: Tenkit(Sudûr)∋Tecrit (yanlış silinmişti, geri) ; Sanat(Sudûr)∋Belâgat (19. gözden kaçan asimetri)

Vâcib-kenar: ilk taramada 6, +1 (Merak ve Sual Tevcihi→Muhakeme, Rükün kararıyla) = 7
  ⊬ (açık): Tasavvur→Terkip "rükün şüphesi" (henüz taşınmadı)

∀X≠Muhakeme: X(Teşrih) yazılmadı ; şema otomatik ⋉ edilir

Mukayese = 42. meleke, Vürûd/Sudûr ⊬
Cerh: tek taraflı, genişletilmedi
```

`izahat/tesrih/sebeke.md` ikincil/anlatı dosyasıdır; kanonik formüller burada.
