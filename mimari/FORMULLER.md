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
  eksik: Lime.İllet-i-Mâddiye, Lime.İllet-i-Sûriyye ∉ Nispet [F 179: nakzedilmedi,
    kapatıldı — bkz. § Burhan, İllet(çeşit) dördü de orada tüketici olarak yer alır]
```

İzahat: `izahat/malum/`

---

## Mücerred (Maddî/Manevî Ayrımı — Burhan'ın Ön-Şartı)

**Nakz (F 179):** Önceki `İllet(çeşit) = {mâddiye, sûriyye, fâiliye, gâiye}` formülü (bkz. eski § Burhan) yanlıştı — dört illeti EVRENSEL ve PARALEL saydı; hâlbuki mâddiye ve sûriyye yalnız madde+suretten MÜREKKEB (cismânî) mevcûda tatbik edilebilir, mücerred (gayr-i maddî) bir mevcûda hiç tatbik edilemez (zaten Vâcibü'l-Vücûd(Basitlik) bunu ispat etmişti: Vâcib'de terkip yok, dolayısıyla madde de suret de yok). Fâiliye ve Gâiye ise mücerrede de, maddîye de tatbik edilir. Bu asimetri görülmeden dördü paralel yazmak, örtük bir maddeci (materyalist) önvarsayımdır — her mevcûdun madde+suretten mürekkep olduğunu baştan kabul eder. Düzeltme, önce maddî/mücerred ayrımını bizzat ispat eder, sonra İllet(çeşit)'i buna göre şartlandırır.

```
Mevcûd(Maddiyet) = { maddî, mücerred }     κ = mürekkeb-min-madde-ve-suret(x)?

Boş bir tasnif olmaması için: ∃x mücerred(x) ispatı şart — aksi hâlde "mücerred"
kutusu adı var cismi yok bir kelime kalır.

Burhan-ı Tâirü'l-Havâ (İbn Sînâ, "Uçan Adam"):
  Faraziye: bir insan, hiçbir duyu girdisi almadan (havada, azasına dokunmadan,
    hiçbir uzvunu hissetmeden) yaratılsın — bedenine dair HER bilgi tahayyülen çıkarılsın.
  Müşahede: bu hâlde dahi kendi vücûdunu ("ben varım") şüphesiz bilir/hisseder.
  ⟹ beden(bilgisi) çıkarılırken "ben" şuuru KALIR
  ⟹ çıkarılan kalırken kalan, çıkarılana ayn olamaz   [Nakzeyn: aynı şey hem
     mevcûd hem madum olamaz aynı anda, aynı cihetten]
  ∴ nefs (zât, "ben" şuuru) bedenden/maddeden ayrı bir hakikattir ⟹ mücerreddir

∴ ∃x mücerred(x)  [en az nefs/"ben" şuuru]  — Mevcûd(Maddiyet) dolu bir tasnif
```

[Not: bu burhan saf istidlâlîdir, sinirbilime/ampirik zemine muhtaç değildir — PLAN.md'nin "burhânîleştirme stratejisi 5"i, tam işlenişi Fasıl III madde 13'e (Ruhun bekası) aittir; burada yalnız Burhan(çeşit)'in İllet eksenini kurmaya yetecek asgarî hâliyle, erken getirilmiştir]

### Mücerred(çeşit) — İkinci Kademe

```
Mücerred(çeşit) = { nefs, akl-melek, ma'kul-i-sırf }
  κ₁ = müteallik-bi'l-beden(x)?        evet → nefs           [bir bedeni tedbir/idare eden mücerred]
  ¬κ₁ ∧ κ₂ = müstakil-vücûd-hâricî(x)? evet → akl-melek       [bedenden müstağni, hâricî müstakil cevher]
  ¬κ₁ ∧ ¬κ₂                            → ma'kul-i-sırf        [yalnız zihinde, vücûd-i-zihnî: adet, küllî mefhum]

Not (nominalizm beyanı, F 2-Y): "matematik gibi" mevcûdlar (sayı, küllî mefhum) burada
  ma'kul-i-sırf dalına düşer — müstakil bir CEVHER değil, aklın bir MA'LÛMUdur (Eflatuncu
  realizm reddedilir, Meşşâî/İbn Sînâcı çizgi benimsenir). "Ruh, melek, cin" ise nefs veya
  akl-melek dalına düşer; cinin hangi dala düştüğü ihtilaflıdır (bazı ekoller cismânî-latif,
  bazıları mücerred sayar) — bu ihtilaf saklanmaz, tam tahkiki Fasıl III'e bırakılır (F 2-Y)
```

İzahat: `izahat/mucerred/genel.md`

---

## Burhan

```
Burhan(çeşit) ⊳ Tavassut(burhânî)   [Tavassut'un κ₁=yakînî(öncül) dalının kendi içi]

Burhan(Sûret) = { istikametli, hulf }     κ=doğrudan-isbat(netice)?
  istikametli ≔ netice ⟸ öncüller                       [doğrudan]
  hulf        ≔ netice ⟸ ¬(zıd-farz ⟹ muhal)             [kıyas-ı hulf, reductio]

Burhan(Nisbet-i-Evsat) = { limmî, innî }     κ=evsat(had-i-evsat)=illet(fi'l-vücûd)?
  [yalnız istikametli dala tatbik edilir; hulf ayrı bir kanaldan işler]
  limmî ≔ evsat, hem vücutta hem zihinde illettir         [hem "vardır" hem "niçin"]
  innî  ≔ evsat, vücutta illet değil, yalnız zihinde (bilgi bakımından) öncül

İnnî(alt-tür) = { eserden-müessire, müşterek-lazımdan-lazıma }     κ=istidlal-yönü
  eserden-müessire         ≔ eser(malûm) ⟹ müessir(meçhul)         [duman→ateş]
  müşterek-lazımdan-lazıma ≔ lazım₁(malûm) ⟹ ⋉illet-müşterek ⟹ lazım₂(meçhul)

İllet(çeşit) = Fâiliye ⊔ Gâiye ⊔ [Maddî(eser) ⋉ (Mâddiye ⊔ Sûriyye)]
  [⊳ Mücerred(Maddiyet) — Fâiliye/Gâiye evrensel (mücerrede de maddîye de tatbik olunur);
   Mâddiye/Sûriyye yalnız eseri bizzat MADDÎ (madde+suretten mürekkeb) olan burhanlara açıktır,
   çünkü mücerred bir eserde (mesela bir sıfatta) "maddesi/sûreti" diye bir şey yoktur]
  ⋉ her limmî/innî burhan, bu şartlı dörtlüden en az BİRİNE dayanır
  ⋉ Nispet(fâilî,gaî) ⊳ {fâiliye,gâiye} ; Nispet'te sorulmayan {mâddiye,sûriyye}
    burada, şartıyla birlikte, tüketici olarak yer alır

∴ Burhan(çeşit) = Sûret × [istikametli: Nisbet-i-Evsat × [innî: alt-tür] × İllet]
  ⟺ₜ  [Sûret ⊢ ikili-Nakzeyn; Nisbet-i-Evsat ⊢ ikili-Nakzeyn; İnnî-alt-tür ⊢ ikili-Nakzeyn;
        İllet ⊢ Maddiyet-şartlı dörtlü — madde/suret'i evrensel değil, cismâniyete
        mahsus kılarak Mücerred(çeşit)'le tutarlı hâle getirildi]

Dehliz sınaması (risale/fasil_1_vucud burhanları bu tasnife düşüyor mu?):
  Burhan-ı-İmkân     ⊳ istikametli.innî.eserden-müessire.fâiliye
    [eser=Vâcib'in kendisi, mücerred — mâddiye/sûriyye zaten tatbik edilemezdi;
     ⊬ açık: bazı İslam filozofları (Molla Sadra) Sıddîkîn'i ne limmî ne innî,
     üçüncü müstakil tür sayar — bu risale klasik innî tasnifini benimser, saklamaz]
  Hudûs-Delili       ⊳ istikametli.innî.eserden-müessire.fâiliye
  Burhân-ı-Tahsis    ⊳ istikametli.innî.eserden-müessire.fâiliye
  Burhân-ı-Tesviye   ⊳ istikametli.innî.eserden-müessire.{fâiliye,sûriyye}
    [eser=canlı bir bünye (göz,kulak) — bizzat maddîdir, bu yüzden Sûriyye tatbik
     edilebilir; ilk defa Sûriyye köşesi dolu]
  Burhân-ı-Temânu'   ⊳ hulf
  Devir/Teselsül-reddi ⊳ hulf
  Devam-ı-Hudûs      ⊳ hulf   [faraziye → Nakzeyn ihlâli → red]
  ∅ (açık): İllet-i-Mâddiye — risalenin hiçbir burhanı şu ana dek maddeye (taşıyıcı
    cevhere) dayanmıyor, yalnız sûrete; tasnifin eksiği değil, henüz doldurulmamış köşe

Not (Tasavvur(Menşe) ile karıştırılmasın): Tasavvur(Menşe)={hissî,hayalî,vehmî,aklî}
  bir KAVRAMIN kaynağını sorar, bir HÜKMÜN/BURHANIN yapısını değil — kategori ayrı.
  Burhanın öncüllerinin epistemik menşei (Burhan(Öncül-Menşei)) ayrı, isteğe bağlı
  bir ikinci eksendir; Burhan(çeşit) ile ⊥ (ortogonal), yerine geçmez
```

İzahat: `izahat/burhan/genel.md`

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
- Mücerred (Mevcûd(Maddiyet), Tâirü'l-Havâ, Mücerred(çeşit)) → `izahat/mucerred/genel.md`
- Burhan (Sûret, Nisbet-i-Evsat, İnnî alt-tür, İllet) → `izahat/burhan/genel.md`
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
