# Fasıl I — Vücûd Formülleri

(`mimari/FORMULLER.md`den aktarıldı, orada da durur — bu bir kopyadır, nakil değil.)

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

## Bünye (Rükün/Şart/Araz/Karîne)

```
Bünye = Mevki × Zaruret

Bünye(dâhil,zarurî)        = Rükün
Bünye(dâhil,gayr-i-zarurî) = Araz
Bünye(hâriç,zarurî)        = Şart
Bünye(hâriç,gayr-i-zarurî) = Karîne

Rükün(x,W)  ≔ x∈dâhil(W) ∧ zarurî(x,W)     [¬x → ¬W, mutlak adem]
Şart(x,W)   ≔ x∈hâriç(W) ∧ zarurî(x,W)     [¬x → ¬W, ama W ara-hâlde kalabilir]
Araz(x,W)   ≔ x∈dâhil(W) ∧ ¬zarurî(x,W)    [¬x ↛ ¬W]
Karîne(x,W) ≔ x∈hâriç(W) ∧ ¬zarurî(x,W)    [x, W'ya ne vücûden ne fiilen tesir eder]
```

## Basitlik

Basitlik(çeşit) = { basit, mürekkep }     κ = tek-cüz(x)?

## Makûlât (yalnız Cevher kanadı)

```
Mevcûd = Cevher ⊔ Araz                    κ = kâim-bi-nefsihî(x)?
```
(Cevher: kendi başına, bir mevzuya muhtaç olmaksızın duran. Vâcibü'l-Vücûd(Kıyam) bu tarifin en tam mertebesidir.)

## Vücûb

```
Tasdik(Vücûb) = { vâcib, mümkün, mümteni }
  κ₁=muhal(yokluk)? → vâcib
  ¬κ₁ ∧ κ₂=muhal(varlık)? → mümteni
  ¬κ₁ ∧ ¬κ₂ → mümkün
```

## Vâcibü'l-Vücûd — Burhan-ı Sıddîkîn

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

## Temel usul (Nakzeyn tabanlı tasnif)

Her tasnif dört adım: (1) κ seç, (2) Nakzeyn'le ikiye böl, (3) isimlendir, (4) dehliz sına (üçüncü bir misal ara). Nakzeyn'in kendisi ispat edilemez, yalnız inkârının kendini nakzettiği gösterilir (Aristo, Metafizik Γ) — bu, devir/teselsülün mecburen bittiği yerdir.

İzahat: `mimari/izahat/vacibul_vucud/genel.md`, `mimari/izahat/rukun_sart/genel.md`, `mimari/izahat/tasnif/tefrik_ve_temyiz.md`
