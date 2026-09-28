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

<figure>
<svg viewBox="0 0 640 260" role="img" aria-label="Vücûb taksimi: x mevcûd, κ₁ yokluk-muhal sualiyle vâcibe, hayırsa κ₂ varlık-muhal sualiyle mümteniye veya mümkine ayrılır">
  <defs>
    <marker id="ar1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
    </marker>
  </defs>
  <g fill="none" stroke="currentColor" stroke-width="1.5">
    <rect x="260" y="10" width="120" height="32" rx="4"/>
    <line x1="320" y1="42" x2="320" y2="66" marker-end="url(#ar1)"/>
    <line x1="320" y1="66" x2="150" y2="98" marker-end="url(#ar1)"/>
    <line x1="320" y1="66" x2="490" y2="98" marker-end="url(#ar1)"/>
    <rect x="90" y="122" width="120" height="32" rx="4"/>
    <rect x="400" y="98" width="180" height="32" rx="4"/>
    <line x1="150" y1="110" x2="150" y2="122" marker-end="url(#ar1)"/>
    <line x1="440" y1="130" x2="360" y2="166" marker-end="url(#ar1)"/>
    <line x1="540" y1="130" x2="580" y2="166" marker-end="url(#ar1)"/>
    <rect x="280" y="166" width="160" height="36" rx="4"/>
    <rect x="510" y="166" width="120" height="36" rx="4"/>
  </g>
  <g font-size="12" text-anchor="middle" fill="currentColor" font-family="inherit">
    <text x="320" y="30">x mevcûd</text>
    <text x="320" y="60">κ₁: yokluk(x) muhal mi?</text>
    <text x="225" y="86">evet</text>
    <text x="415" y="86">hayır</text>
    <text x="150" y="142">VÂCİB</text>
    <text x="490" y="118">κ₂: varlık(x) muhal mi?</text>
    <text x="378" y="152">evet</text>
    <text x="572" y="152">hayır</text>
    <text x="360" y="188">MÜMTENİ</text>
    <text x="360" y="200">(∉ Mevcûd)</text>
    <text x="570" y="188">MÜMKİN</text>
  </g>
</svg>
<figcaption>Vücûb taksimi: κ₁ ve κ₂'nin ardışık Nakzeyn tatbikiyle Vâcib/Mümteni/Mümkin ayrımı.</figcaption>
</figure>

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

<figure>
<svg viewBox="0 0 760 120" role="img" aria-label="Mümkinin var oluşundan müreccih yokluğu, devir ve teselsülün ikisinin de muhal olması yoluyla Vâcibü'l-Vücûd'a zarurî nihayet">
  <defs>
    <marker id="ar2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
    </marker>
  </defs>
  <g fill="none" stroke="currentColor" stroke-width="1.5">
    <rect x="10" y="40" width="100" height="40" rx="4"/>
    <line x1="110" y1="60" x2="163" y2="60" marker-end="url(#ar2)"/>
    <rect x="165" y="40" width="110" height="40" rx="4"/>
    <line x1="275" y1="60" x2="328" y2="60" marker-end="url(#ar2)"/>
    <rect x="330" y="18" width="220" height="84" rx="4"/>
    <line x1="550" y1="60" x2="603" y2="60" marker-end="url(#ar2)"/>
    <rect x="605" y="40" width="145" height="40" rx="4" stroke-width="2.5"/>
  </g>
  <g font-size="11" text-anchor="middle" fill="currentColor" font-family="inherit">
    <text x="60" y="57">Mümkin</text>
    <text x="60" y="70">(bilfiil var)</text>
    <text x="134" y="57">müreccih</text>
    <text x="134" y="70">yok</text>
    <text x="220" y="57">muhal</text>
    <text x="220" y="70">(tereccüh bilâ</text>
    <text x="220" y="82">müreccih)</text>
    <text x="440" y="37">devir/teselsül denenir</text>
    <text x="440" y="56">devir: A≺B≺A ⟹ A≺A (muhal)</text>
    <text x="440" y="73">teselsül: küll de mümkin kalır</text>
    <text x="440" y="90">→ erteler, gidermez</text>
    <text x="677" y="57">Vâcibü'l-</text>
    <text x="677" y="70">Vücûd</text>
  </g>
</svg>
<figcaption>Silsile-i esbâbın devir ve teselsülle kapanamaması, zincirin zarurî olarak Vâcibü'l-Vücûd'da nihayet bulmasını gerektirir.</figcaption>
</figure>

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
