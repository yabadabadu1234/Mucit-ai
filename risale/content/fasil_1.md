# Fasıl I — El-Vücûd

## Bu Fasıl Nasıl Okunur

- Yeni geçen **her işaret**, kullanılmadan önce burada tarif edilir; hiçbir sembol, tanıtılmadan bir formülün içinde çıkmaz.
- Her yabancı kelimenin kökü ve lugat mânâsı, lise seviyesinde, ayrı bir kutuda verilir.
- Açıklamalar **"Çoban için"** satırlarında, en sade misalle, tek-iki cümleyle verilir; birden çok ihtimal varsa cümleyle değil **şema**yla gösterilir.
- Sıra hep aynıdır: **kelime → çoban misali → şema → formül → netice.**

## 0. Alfabe — Kullanılacak İşaretler

| İşaret | Menşe | Bu risalede ne demek |
| :-- | :-- | :-- |
| κ (kappa) | yalnız kısaltma harfi | "hangi suale göre ayırıyoruz?" |
| ⟺ₜ | — | "bu bölüş hiçbir ihtimali dışarda bırakmıyor" |
| ⟹ | — | "―den zorunlu olarak şu çıkar" |
| ↯ | — | "çelişki, burada duvara çarpıyoruz" |
| ∴ | — | "öyleyse, netice olarak" |
| ⊳ | — | "şu başlığın alt kolu" |
| ⋉ | — | "şu kaide, buraya tatbik ediliyor" |

| Kelime | Kök | Lugat mânâsı |
| :-- | :-- | :-- |
| Nakzeyn | ن ق ض (nakz = bozmak, düğüm çözmek) | "iki bozma / iki çelişki" |

**Çoban için:** Elindeki bir koyun ya senindir ya değildir. Aynı koyun için, aynı anda, aynı bakımdan "hem benim hem değil" diyemezsin. Bu risalenin **tamamı**, bu tek ve çok basit kaideyi tekrar tekrar, farklı yerlerde kullanıyor. Buna **Nakzeyn Kanunu** denir.

## 1. Var Olan Bir Şey Üç Hâlden Hangisindedir?

| Kelime | Kök | Lugat mânâsı | Neden bu isim |
| :-- | :-- | :-- | :-- |
| Vâcib | و ج ب (vücûb) | "gerekli, zorunlu düşmüş" | yokluğu imkânsız, varlığı üzerine düşmüş olan |
| Mümkin | م ك ن (imkân) | "güç yetme, olabilme" | var da olabilir, yok da |
| Mümteni | م ن ع (men) | "engellenmiş, alıkonmuş" | varlığı bizatihi imkânsız |
| Mevcûd | و ج د (vücûd) | "bulunan" | var olan, bulunan şey |

**Çoban için:** Elindeki bir şeye şunu sor: "Bu hiç yok olabilir miydi?" Cevap "hayır, asla" ise o şey **Vâcib**dir. Cevap "evet, yok da olabilirdi var da" ise **Mümkin**dir. Bir şeyin baştan var olması zaten imkânsızsa (mesela "kare daire"), o hiç **Mevcûd** olamaz — ona **Mümteni** denir.

```
                 x mevcûd mu?
                      │
      soru 1: yokluğu muhal mi (imkânsız mı)?
            ┌─────────┴─────────┐
          evet                hayır
            │                    │
            ▼                    │
       ┌─────────┐       soru 2: varlığı muhal mi?
       │ VÂCİB   │          ┌─────────┴─────────┐
       └─────────┘        evet                hayır
                             │                    │
                             ▼                    ▼
                       ┌──────────┐        ┌──────────┐
                       │ MÜMTENİ  │        │  MÜMKİN  │
                       │(zaten yok)│       └──────────┘
                       └──────────┘
```

(Her iki soru da Nakzeyn Kanunu'nun tatbikidir: cevap ya evet ya hayırdır, üçüncüsü yoktur — bu yüzden bu üçlü bölüş hiçbir dördüncü ihtimal bırakmaz, ⟺ₜ.)

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

## 2. Var Olan Bir "Mümkin", Neden Kendi Kendine Var Olamaz?

| Kelime | Kök | Lugat mânâsı | Neden bu isim |
| :-- | :-- | :-- | :-- |
| Müreccih | ر ج ح (tercih, tartıda ağır basma) | "bir tarafı ağır bastıran" | iki eşit ihtimalden birini seçtiren sebep |
| Silsile | س ل س ل | "zincir" | birbirine bağlı sebep-netice halkaları |
| Devir | د و ر | "dönme" | bir şeyin kendi sebebi olarak kendine dönmesi |
| Teselsül | (silsile kökünden) | "zincirleme" | sebeplerin sonsuza uzaması |

**Çoban için:** Elindeki taş kendi kendine hareket etmez — bir şey (elin, rüzgâr, bir tekme) onu itmiş olmalı. "Var da olabilir yok da olabilir" (**mümkin**) olan her şey böyledir: kendi başına, sebepsiz, "var" tarafına geçemez. Ona var dedirten dıştan bir sebep (**müreccih**) lâzımdır.

**Sonsuz zincir de işe yaramaz — iki yol da denenir, ikisi de kapanır:**

```
YOL 1 — DEVİR (dönerek kapatmayı dene):
    A'nın sebebi B, B'nin sebebi A olsun.
        A ──sebebi──► B ──sebebi──► A
    Bu, A'nın kendi sebebinden ÖNCE var olmuş olmasını gerektirir.
    ↯  imkânsız (bir şey kendinden önce olamaz)

YOL 2 — TESELSÜL (sonsuza uzatmayı dene):
    … ← C ← B ← A ← (aranan şey)
    Zincir ne kadar uzasa da her halka hâlâ "mümkin"dir
    (kendi başına var olamayan).
    Sonsuz sayıda "kendi başına var olamayan" halkanın TOPLAMI da
    hâlâ "kendi başına var olamayan"dır — SAYI değişti, CİNS değişmedi.
    ↯  sorun çözülmedi, yalnızca ertelendi
```

**Netice:** İki yol da kapandığına göre zincir, dıştan sebebe muhtaç olmayan, **kendi kendine var olan** bir noktada durmak zorundadır.

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

## 3. Zâta Ait Sıfatlar — Nefsiyye ve Selbiyye

### Geleneksel Yerleşim

Ehl-i Sünnet kelâmında Allah'ın sıfatları üç grupta sayılır:

| Grup | Sayı | İsimler |
| :-- | :-- | :-- |
| Nefsiyye (zâtın bizzat kendisi) | 1 | Vücud |
| Selbiyye (zâttan gayrısını nefyeden) | 5 | Kıdem, Beka, Vahdâniyet, Kıyâm bi-Nefsihî, Muhâlefetün li'l-Havâdis |
| Sübûtiyye (zâtta sabit mânâlar) | 7-8 | Hayat, İlim, Sem', Basar, Kelâm, İrade, Kudret, (Tekvin) |

**Not:** "Basitlik" (terkipsizlik) bu on üç isimden **biri değildir**. Aşağıda yalnız **Vahdâniyet**i ispatlamak için kullanılan bir **ara-basamak**tır (lemma) — kendi başına bir sıfat adı olarak zikredilmez. Ara-basamağı sıfatla karıştırmamak için ayrıca işaretlenmiştir.

### 3.1 Vücud

Zaten §1-2'de ispat edildi: ∃! Vâcibü'l-Vücûd.

### 3.2 Kıdem ve Beka

| Kelime | Kök | Lugat mânâsı |
| :-- | :-- | :-- |
| Kıdem | ق د م | "en önde olma, hiçbir şeyden sonra gelmeme" |
| Beka | ب ق ي | "kalıcı olma, tükenmeme" |

**Çoban için:** Bir mumun alevinin başı ve sonu vardır — sonradan yanar, sonra söner. Vâcib'in böyle bir başlaması veya bitmesi olsaydı, o an bir değişim geçirmiş olurdu; her değişim ise (§2) dıştan bir sebep ister — ama Vâcib hiçbir şeye muhtaç değildi. Çelişki.

```
Kıdem(x) ≔ ¬∃ bidâyet(x)      [x'in bir başlangıcı yok]
Beka(x)  ≔ ¬∃ nihâyet(x)      [x'in bir sonu yok]

bidâyet∨nihâyet ⟹ tagayyür(değişim) ⟹ ⋉(§2, müreccih zarureti) ⟹ muhtaçlık
                                                            ⟹ ↯ Vâcib tarifiyle çelişki
```

| Netice | (T) |
| :-- | :-- |
| Kıdem, Beka | burhânî |

### 3.3 Vahdâniyet

| Kelime | Kök | Lugat mânâsı |
| :-- | :-- | :-- |
| Vahdâniyet | و ح د (vahd = bir olma) | "teklik, birden başka olmama" |
| (lemma) Basitlik | ب س ط (basît = yayılmış, terkipsiz) | "parçalardan oluşmamışlık" |

**Çoban için:** İki tane "Vâcib" var farz edelim, ikisi de kendiliğinden var, hiçbir şeye muhtaç değil. Ama "iki" dedin mi, aralarında bir **fark** olmalı — yoksa zaten "iki" değil "bir" olurlardı. O fark, birinde bulunup diğerinde bulunmayan bir parça demektir. Parçası olan bir şey ise, o parçaya muhtaçtır — hâlbuki Vâcib hiçbir şeye muhtaç değildi.

```
Basitlik (lemma):
  mürekkeb(x) ⟹ ictimâ-i-ecza (parçaların bir araya gelmesi)
             ⟹ ⋉(§2, müreccih zarureti) ⟹ muhtaç(x)
             ⟹ ↯ Vâcib tarifiyle çelişki
  ∴ Vâcib parçasızdır  [bu netice, isim olarak müstakil bir sıfat DEĞİLDİR]

Vahdâniyet:
  ∃x≠y (ikisi de Vâcib) ⟹ temayüz (fark) lâzım
                        ⟹ fark = terkib(ortak-cins + ayırıcı-fasıl)
                        ⟹ ↯ Basitlik-lemma ile çelişki
  ∴ Vâcibü'l-Vücûd tektir
```

| Netice | (T) |
| :-- | :-- |
| Vahdâniyet | burhânî |

### 3.4 Kıyâm bi-Nefsihî

| Kelime | Kök | Lugat mânâsı |
| :-- | :-- | :-- |
| Kıyâm | ق و م | "ayakta durma, kendi başına duruş" |
| Nefs | ن ف س | "zât, bizzat kendisi" |

**Çoban için:** Bir resim, asılı olduğu duvara muhtaçtır; duvar olmadan havada asılı kalamaz. Vâcib'in böyle bir "duvara" ihtiyacı yoktur — ne bir mevzuya, ne bir şarta.

```
Kıyam-bi-Nefsihî(x) ≔ ¬∃ mevzû(x) ∧ ¬∃ şart(x)
   ⋉ Makûlât.Cevher   [Cevher tarifi: kendi başına, bir mevzuya muhtaç olmaksızın durur]
   — Vâcib bu tarifin en tam mertebesidir: yalnız mevzûsuz değil, şartsız da kaimdir.
```

| Netice | (T) |
| :-- | :-- |
| Kıyâm bi-Nefsihî | burhânî |

### 3.5 Muhâlefetün li'l-Havâdis

| Kelime | Kök | Lugat mânâsı |
| :-- | :-- | :-- |
| Muhâlefet | خ ل ف | "aykırı olma, benzememe" |
| Havâdis | ح د ث (hudûs = sonradan olma) | "sonradan var olanlar" |

**Çoban için:** §1'de gördük: bir şey ya Vâcib'dir ya Mümkin, ikisi aynı anda olamaz. Sonradan var olan (**hâdis**) her şey Mümkin sınıfındandır. Öyleyse Vâcib, hiçbir sonradan-olana, zâtında, benzemez.

```
Vâcib ∩ Mümkin = ∅   [§1'in doğrudan neticesi]
havâdis ⊂ Mümkin
∴ Vâcib ∩ havâdis = ∅  →  Muhâlefetün li'l-havâdis
```

| Netice | (T) |
| :-- | :-- |
| Muhâlefetün li'l-Havâdis | burhânî |

### Netice (Sıfat Değil, Sonuç): Cisim ve Mekân Reddi

**Çoban için:** Cisim olmak, parçalardan (uzunluk-genişlik-derinlik) oluşmuş olmaktır — ama Vâcib parçasızdır (§3.3). "Bir yerde olmak" da bir kategoriye mahkûm olmaktır — bu da bir tür muhtaçlıktır.

```
Cisim(x) ⟹ terkib(madde,suret,eb'ad) ⟹ ↯ Basitlik-lemma
Mekân ∈ Makûlât.İzafî.eyne ⟹ mahkûmiyet-i-kategori ⟹ hâcet ⟹ ↯ Kıyâm-bi-Nefsihî
∴  ¬Cisim(Vâcib) ∧ ¬Mekân(Vâcib)
```

### Fasıl I §3 — Delil-Kuvveti

| Netice | (T) |
| :-- | :-- |
| Vücud, Kıdem, Beka, Vahdâniyet, Kıyâm bi-Nefsihî, Muhâlefetün li'l-Havâdis | burhânî |
| Cisim/mekân reddi (sonuç) | burhânî |

## 4. İsim / Sıfat Farkı, Zâtî / Sübûtî Ayrımı

| Kelime | Kök | Lugat mânâsı |
| :-- | :-- | :-- |
| İsim | س م و (yükselmek) | "bir şeyi işaretleyen çağrı" |
| Sıfat | و ص ف | "vasıflandırma, nitelik" |
| Zâtî | ذ ا ت | "öze ait, bizzat kendinden" |
| Sübûtî | ث ب ت | "sabit olan, delille sonradan sabitlenen" |

**Çoban için:** "İsim" bir kişiyi çağırdığın etikettir ("Ahmed"). "Sıfat" o kişinin bir özelliğidir ("cömert"). Bazı sıfatlar sırf zâttan (kimlikten) çıkar, dışarıya hiç bakmadan bilinir ("Ahmed insandır"). Bazı sıfatlar ise ancak dışarıdaki bir esere bakılarak bilinir ("Ahmed cömerttir" — bunu bilmek için onun bir vermesini görmen lâzım).

```
İsim(Zât,Sıfat) ≔ Makûlât.İzafî tatbiki

Sıfat(çeşit) = { zâtî, sübûtî }     κ = lâzım-ı-zât-mı(sıfat)?
  zâtî   : sıfat ⊳ (§1-3), esere muhtaç değil
  sübûtî : sıfat ⊳ Lime.İllet-i-Fâiliye(âlem), esere muhtaç
```

| Netice | (T) |
| :-- | :-- |
| Sıfat(çeşit) ⟺ₜ ikiliği | burhânî |
| — her sübûtî sıfatın isbatı | ayrı, bkz. §5 |

## 5. Sıfât-ı Sübûtiyye

**Çoban için (genel):** Şimdiye kadarki sıfatların hepsi, sırf "Vâcib" tarifinden, dışarıya hiç bakmadan çıktı. Şimdiki altı sıfat öyle çıkmaz — bunlar âlemde gördüğümüz esere (nizama, harekete, hayata) bakılarak anlaşılır. Bu bir zaaf değildir; §4'teki Sıfat(çeşit) ayrımının kendi tarifi gereği böyle olması gerekiyordu.

### 5.1 Hayat

Kök: ح ي ي (hayy = diri olma).

**Çoban için:** Bilen ve gücü yeten bir şey ölü olamaz — bilmek ve yapabilmek, diri olmayı gerektirir.

```
{İlim,Kudret}(Vâcib) ⟹ Aklî-Âdî("ilim ve kudret için hayat şarttır") ⋉ ⟹ Hayat(Vâcib)
```

### 5.2 İlim (+ Sem' ve Basar)

Kökler: ع ل م (ilim = bilme), س م ع (sem' = işitme), ب ص ر (basar = görme).

**Çoban için:** Bir marangoz, elindeki tahtayı sandalyeye dönüştürürken, sandalyenin şeklini önceden **bilir** — bilmeden yapamaz. Âlemdeki nizam ve hikmeti gören, onu Yapan'ın da bunu bilerek yaptığını anlar.

```
nizam/hikmet(âlem) ⟹ Lime.İllet-i-Gâiye ⟹ gaye-güden-fail ⟹ İlim(Vâcib)

Sem', Basar ≔ İlim'in işitilen/görülen her şeye taalluku
   [Ehl-i Sünnet çoğunluğu: müstakil değil, İlim'in bir yönü — bu risale bunu böyle beyan eder]
```

### 5.3 Kudret

Kök: ق د ر (kadr/kudret = güç yetirme).

**Çoban için:** Yoktan bir şey var etmek, gücü olmayanın yapabileceği bir şey değildir.

```
Hudûs(âlem) [âlemin zaman içinde bir başlangıcı olması] ⟹ îcad-kudreti ⟹ Kudret(Vâcib)
```

### 5.4 Tekvin

Kök: ك و ن (kevn = oluş, varlık bulma). Tekvin = "bizzat var etme fiilinin kendisi".

**Çoban için — Kudret'ten farkı ne?** Bir ustanın elinde çekiç olması ("gücü var") başka şeydir, o çekici fiilen vurması ("bizzat yapıyor") başka şeydir.

```
KARŞILAŞTIRMA
  Kudret : bilkuvve iktidar (yapabilme) — ezelî, değişmez, tek
  Tekvin : bizzat yaratma fiilinin sıfatı — Vâcib'in Hâlıkıyeti
           bizatihi ezelîdir (§3.2, Kıdem ⋉); mahlûkun an-be-an hudûsu,
           yalnız Kudret'in "hep hazır olması" ile açıklanamaz — çünkü
           o zaman "ne zaman yaratılıyor" sorusu cevapsız kalır.
∴ Tekvin(sıfat), Kudret'ten ayrı, müstakil bir sübûtî sıfattır.
```

(Not: bu ayrım Mâturîdî kelâmına aittir; Eş'arî ekolü Tekvin'i müstakil saymaz, Kudret'in bir cüzü sayar. Bu risale Mâturîdî tercihini benimser ve bunu açıkça böyle beyan eder, gizlemez — F 2-Y.)

### 5.5 İrade

Kök: ر و د (arzu etme, isteme).

**Çoban için:** Masada iki tıpatıp aynı elma var, ikisi de eşit derecede alınabilir. Birini almak için elinin kör bir kanunla değil, **seçimle** oraya gitmesi lâzım — eşitlik kendi kendine bir tarafı seçemez.

```
Mümkinü'l-Vücûd(Şart) ⋉ fizik-sâbiteleri
κ = zarurî-bizatihî(değer)?    ¬tenakuz(değer) ⟹ mümkün(değer)
eşit-ihtimal ⟹ TEK tahakkuk ⟹ kanun≠fail ⟹ İrade(Vâcib)
```

### 5.6 Kelâm

⊳ Fasıl II.

### Fasıl I §5 — Delil-Kuvveti

| Netice | (T) |
| :-- | :-- |
| Hayat, İlim (+Sem',Basar), Kudret, Tekvin, İrade | burhânî |
| Kelâm | ⊳ Fasıl II |

## 6. Hakîm — Gaye — Şer(çeşit)

| Kelime | Kök | Lugat mânâsı |
| :-- | :-- | :-- |
| Hakîm | ح ك م | "yerli yerine koyan, hikmetle iş gören" |
| Gaye | غ ا ي | "varılacak son nokta" |
| Şer | ش ر ر | "kötülük" |

**Çoban için:** Akıllı bir çoban sürüsünü boşuna bir yere sürmez — her hareketinin bir sebebi/gayesi vardır. Vâcib de İrade sıfatıyla (§5.5) hareket ettiğine göre, fiillerinin gayesiz (abes) olması Hikmetiyle çelişir.

```
Gaye(çeşit) = { zarurî, ihtiyarî }
  Vâcib(fiil) = ihtiyarî  ⋉ (İrade, §5.5)  ⟹  ¬abesiyet(Hakîm)

Şer(çeşit) = { ademî, izafî }     κ = ayn-ı-vücûd-mu(şer)?
  ademî : şer = adem(hayr)                [bir hayrın yokluğu]
  izafî : şer = bedel-i-cüz'î(küllî-hayr)  [küllî bir hayrın cüz'î bedeli]
```

```
Hakîm ∧ Şer(mevcûd)?
        │
        ├─ (a) mantıkî tenakuz var mı? ──▶ TEK tutarlı senaryo (Şer=ademî∨izafî)
        │                                        ⟹  ¬tenakuz          [burhânî]
        │
        └─ (b) şu belirli şerrin müspet hikmeti ne? ──▶ ⊳ Fasıl III
                                                 adem-i-vücdan ≠ adem-i-vücud
                                                         [cedelî — kasten]
```

| Netice | (T) |
| :-- | :-- |
| 6-a: Hakîm ∧ Şer(mevcûd) çelişmez | burhânî |
| 6-b: şu belirli şerrin müspet hikmeti | cedelî/hitâbî (kasten) |

## Fasıl I — Delil-Kuvveti Tablosu

| # | Netice | (T) |
| :-- | :-- | :-- |
| 1 | Vücûb taksimi ⟺ₜ | burhânî |
| 2 | Müreccih, devir-teselsül reddi, ∃!Vâcib | burhânî |
| 3 | Vücud, Kıdem, Beka, Vahdâniyet, Kıyâm bi-Nefsihî, Muhâlefetün li'l-Havâdis, cisim/mekân reddi | burhânî |
| 4 | Sıfat(çeşit) ikiliği | burhânî |
| 5 | Hayat, İlim(+Sem',Basar), Kudret, Tekvin, İrade | burhânî |
| 6-a | Hakîm ∧ Şer çelişmez | burhânî |
| 6-b | Ferdî şerrin müspet hikmeti | cedelî/hitâbî (kasten) |

## Ek — Risale-i Nur Delilleri (Tamamlayıcı, Burhânî Çekirdeğin Yerine Değil)

| Delil | Bağlandığı madde | Mahiyet | (T) |
| :-- | :-- | :-- | :-- |
| Nizam ve Mizan | §5 İrade/İlim | Şart(Mümkinü'l-Vücûd) ⋉ (küllî ölçek) | hitâbî/cedelî |
| Teâvün | §5 İlim | Lime.İllet-i-Gâiye ⋉ (âlem, müşahede) | hitâbî/cedelî |
| Esbâbın Acziyeti | §5 İlim/Kudret | "kanun≠fail" ⋉ (tek tek misal) | hitâbî/cedelî |
| Cüz'iyattaki İntizam | §5 İlim | nizam ⋉ (en küçük ölçek) | hitâbî/cedelî |
| İsimlerin Tecellisi | §4 İsim(Zât,Sıfat) | ⋉ (müşahede dili) | hitâbî/cedelî |
| Vahdet-i Rububiyet / Kanun-u Vahdet | §3.3 Vahdâniyet | ⋉ (kozmolojik ikiz) | hitâbî/cedelî |
