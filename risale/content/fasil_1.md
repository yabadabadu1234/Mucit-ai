# Fasıl I — El-Vücûd

## Notasyon

```
κ     kıstas            ⟺ₜ   Nakzeyn-tükenmişlik        ⊢  mühürlü
⊳     alt-dal           ⋉    tatbik                      ⊬  mühürsüz
≔     tarif             ∵ ∴  çünkü / dolayısıyla         ≺  öncelik
```

## 1. Vücûb Taksimi

```
Tasdik(Vücûb) = { vâcib, mümkün, mümteni }
  κ₁ = muhal(yokluk)?           → evet: vâcib
  ¬κ₁ ∧ κ₂ = muhal(varlık)?     → evet: mümteni  [∉ Mevcûd]
  ¬κ₁ ∧ ¬κ₂                     → mümkün
```

```
                    ┌───────────────┐
                    │   x mevcûd    │
                    └───────┬───────┘
                            │
                κ₁: yokluk(x) muhal mi?
                    ┌───────┴───────┐
                  evet             hayır
                    │                │
                    ▼                ▼
              ┌──────────┐   κ₂: varlık(x) muhal mi?
              │  VÂCİB   │      ┌───────┴───────┐
              └──────────┘    evet             hayır
                                 │                │
                                 ▼                ▼
                           ┌──────────┐    ┌──────────┐
                           │ MÜMTENİ  │    │  MÜMKİN  │
                           │ (∉Mevcûd)│    └──────────┘
                           └──────────┘
```

| Netice | (T) |
| :-- | :-- |
| Mevcûd(Vücûb) = {Vâcib, Mümkin} ⟺ₜ | burhânî |

## 2. Müreccih Zarureti — Silsilenin Nihayeti

```
Mümkinü'l-Vücûd(Şart) = { müreccih-i hâricî }
  ⟸ ¬(tereccüh bilâ müreccih)      [Nakzeyn ihlâli]

Silsile-i Esbâb(Nihayet) = { Vâcibü'l-Vücûd }
  devir:    A≺B≺A  ⟹  A≺A                      (muhal)
  teselsül: ∀cüz mümkin ⟹ küll mümkin ⟹ küll ⋉ (Şart)   [erteler, gidermez]

∴  ∃! Vâcibü'l-Vücûd
```

```
┌─────────┐  müreccih?  ┌─────────┐  devir/teselsül?  ┌───────────────┐
│ Mümkin  │────yok─────▶│  muhal  │        →          │ zincir kapanmaz│
│ (var)   │             └─────────┘                   └───────┬───────┘
└─────────┘                                                    │ zarurî nihayet
                                                                 ▼
                                                        ┌──────────────────┐
                                                        │ Vâcibü'l-Vücûd   │
                                                        └──────────────────┘
```

| Netice | (T) |
| :-- | :-- |
| ∃! Vâcibü'l-Vücûd | burhânî |

## 3. Zâtî Sıfatlar

| Sıfat | Formül | Çelişki (nakz) |
| :-- | :-- | :-- |
| Basitlik | mürekkeb(V) ⟹ ictimâʻ-i-ecza ⋉ (2) ⟹ muhtâc | ¬muhtâc(Vâcib) |
| Vahdâniyet | ∃x≠y(ikisi Vâcib) ⟹ temayüz ⟹ terkib(cins,fasıl) | ¬(4) Basitlik |
| Ezelî/Ebedî | bidâyet∨nihâyet ⟹ tagayyür ⟹ ⋉(2)-muhtaçlık | Vâcib'e münâfî |
| Kıyam bi-nefsihî | ⋉ Makûlât.Cevher | — (en tam mertebe) |
| Muhalefetü'l-havâdis | Vâcib∩Mümkin=∅ ; havâdis⊂Mümkin | (1)'in doğrudan neticesi |

| Netice | (T) |
| :-- | :-- |
| {Basitlik, Vahdâniyet, Ezelî, Ebedî, Kıyam bi-nefsihî, Muhalefetü'l-havâdis} | burhânî |

## 4. Sıfât-ı Selbiye

```
Cisim(x) ⟹ terkib(madde,suret,eb'ad) ⟹ ¬Basitlik(x)
Mekân ∈ Makûlât.İzafî.eyne  ⟹  mahkûmiyet-i-kategori ⟹ hâcet ⟹ ¬Vâcib(x)

∴  ¬Cisim(Vâcib) ∧ ¬Mekân(Vâcib)
```

| Netice | (T) |
| :-- | :-- |
| Cisim değil, mekândan münezzeh | burhânî |

## 5. İsim / Sıfat(çeşit)

```
İsim(Zât,Sıfat) ≔ Makûlât.İzafî tatbiki

Sıfat(çeşit) = { zâtî, sübûtî }     κ = lâzım-ı-zât-mı(sıfat)?
  zâtî   : sıfat ⊳ (1)-(3), esere muhtaç değil
  sübûtî : sıfat ⊳ Lime.İllet-i-Fâiliye(âlem), esere muhtaç
```

| Netice | (T) |
| :-- | :-- |
| Sıfat(çeşit) ⟺ₜ ikiliği | burhânî |
| — her sübûtî sıfatın isbatı | ayrı, bkz. §6 |

## 6. Sübûtî Sıfatlar

| Sıfat | Formül |
| :-- | :-- |
| İrade | Mümkinü'l-Vücûd(Şart) ⋉ fizik-sâbiteleri; κ=zarurî-bizatihî(değer)? ¬tenakuz(değer) ⟹ mümkün(değer); eşit-ihtimal ⟹ TEK tahakkuk ⟹ kanun≠fail ⟹ İrade |
| İlim | nizam/hikmet(âlem) ⟹ Lime.İllet-i-Gâiye ⟹ gaye-güden-fail ⟹ İlim |
| Kudret | Hudûs(âlem) ⟹ îcad-kudreti |
| Hayat | {İlim,Kudret} ⟹ Aklî-Âdî("ilim→hayat şarttır") ⋉ |
| Kelâm | ⊳ Fasıl II |

| Netice | (T) |
| :-- | :-- |
| {İrade, İlim, Kudret, Hayat} | burhânî |
| Kelâm | ⊳ Fasıl II |

## 7. Hakîm — Gaye — Şer(çeşit)

```
Gaye(çeşit) = { zarurî, ihtiyarî }
  Vâcib(fiil) = ihtiyarî  ⋉ (İrade, §6)  ⟹  ¬abesiyet(Hakîm)

Şer(çeşit) = { ademî, izafî }     κ = ayn-ı-vücûd-mu(şer)?
  ademî : şer = adem(hayr)
  izafî : şer = bedel-i-cüz'î(küllî-hayr)
```

```
Hakîm ∧ Şer(mevcûd)?
        │
        ├─ (a) mantıkî tenakuz var mı? ──▶ TEK tutarlı senaryo (Şer=ademî∨izafî)
        │                                        ⟹  ¬tenakuz          [burhânî]
        │
        └─ (b) şu belirli şerrin müspet hikmeti ne? ──▶ ⊳ §15 (Fasıl III)
                                                 adem-i-vücdan ≠ adem-i-vücud
                                                         [cedelî — kasten]
```

| Netice | (T) |
| :-- | :-- |
| 7-a: Hakîm ∧ Şer(mevcûd) çelişmez | burhânî |
| 7-b: şu belirli şerrin müspet hikmeti | cedelî/hitâbî (kasten) |

## Fasıl I — Delil-Kuvveti Tablosu

| # | Netice | (T) |
| :-- | :-- | :-- |
| 1 | Vücûb taksimi ⟺ₜ | burhânî |
| 2 | Müreccih, devir-teselsül reddi, ∃!Vâcib | burhânî |
| 3 | Basitlik…Muhalefetü'l-havâdis | burhânî |
| 4 | Cisim değil, mekândan münezzeh | burhânî |
| 5 | Sıfat(çeşit) ikiliği | burhânî |
| 6 | İrade, İlim, Kudret, Hayat | burhânî |
| 7-a | Hakîm ∧ Şer çelişmez | burhânî |
| 7-b | Ferdî şerrin müspet hikmeti | cedelî/hitâbî (kasten) |

## Ek — Risale-i Nur Delilleri (Tamamlayıcı, Burhânî Çekirdeğin Yerine Değil)

| Delil | Bağlandığı madde | Mahiyet | (T) |
| :-- | :-- | :-- | :-- |
| Nizam ve Mizan | §6 İrade/İlim | Şart(Mümkinü'l-Vücûd) ⋉ (küllî ölçek) | hitâbî/cedelî |
| Teâvün | §6 İlim | Lime.İllet-i-Gâiye ⋉ (âlem, müşahede) | hitâbî/cedelî |
| Esbâbın Acziyeti | §6 İlim/Kudret | "kanun≠fail" ⋉ (tek tek misal) | hitâbî/cedelî |
| Cüz'iyattaki İntizam | §6 İlim | nizam ⋉ (en küçük ölçek) | hitâbî/cedelî |
| İsimlerin Tecellisi | §5 İsim(Zât,Sıfat) | ⋉ (müşahede dili) | hitâbî/cedelî |
| Vahdet-i Rububiyet / Kanun-u Vahdet | §3 Vahdâniyet | ⋉ (kozmolojik ikiz) | hitâbî/cedelî |
