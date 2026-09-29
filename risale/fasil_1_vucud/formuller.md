# Fasıl I — Vücûd Formülleri

(Çekirdek `mimari/FORMULLER.md`den aktarıldı; risale bahsinde geliştirilen yeni formüller —Hakk-ı Vücûd, Burhân-ı Tatbik, Devam-ı Hudûs (deizm ve İbn Sînâ'nın cüz'iyyat iddiasının reddi), Burhân-ı Tahsis, Burhân-ı Temânu', Burhân-ı Tesviye, Fâil-i Muhtar/Mûcib bi'z-Zât, Hudûs Delili, Sıfât-ı Sübûtiyye'nin tamamı— yalnız burada, risale/fasil_1_vucud/ altında mühürlüdür.)

## Notasyon

```
κ            kıstas (tasnif ölçütü, bir vasıf/sual)
⟺ₜ           Nakzeyn'le tükenmişlik: ∀x (κ(x) ∨ ¬κ(x))
⊢            mühürlü (sabit)
⊬            mühürsüz / nakzedildi / reddedildi
⊳            X, Y'nin kısmı/dalıdır (X ⊂ Y, alt-dal)
⋉            tatbik (bir usulün/kümenin başka mevzua uygulanışı)
≔            tarif (tanım)
↯            çelişki (nakz noktası)
∵ ∴          çünkü / dolayısıyla
≺            öncelik (zaman/illiyet sırası, "A, B'den önce")
X ─sebeb→ Y  X, Y'nin var oluşunun (vücûda gelişinin) illetidir; X, Y'yi var eder
```

**Parantez kaidesi:** `(...)` yalnız, hemen önündeki adı zaten tarif edilmiş bir işlevin/yüklemin gerçek parametreleri için kullanılır (mesela `muhal(x)`, `İlim(Vâcib,x,t)`, `Sebeb(A,B)`). Bir formül maddesine atıf (mesela "2. maddeye bakınız") veya kısa bir izah/hüküm kelimesi (mesela "muhal", "çelişki") hiçbir zaman `(...)` içine yazılmaz — bunlar köşeli parantez `[...]` içine veya tire ile (`—`) ayrılmış bir ibareye konur. Bu ayrım gözetilmezse okuyucu parametre ile izahı birbirine karıştırır.

## Evveliyyât (Akıl Kaideleri) — İstisnasız Her Şeye Şâmil Dört Kaide

```
Ayniyet:           A ≡ A                    ∀x (x = x)
Nakzeyn:           ¬(P ∧ ¬P)                ∀x ¬(Mevcud(x) ∧ ¬Mevcud(x))
Üçüncü-Hâl-İmtinâ: P ∨ ¬P                   ∀x (Mevcud(x) XOR ¬Mevcud(x))
Kâfi-Sebep:        Mümkin(x) ∧ Hudûs(x)  ⟹  ∃y (y≠x ∧ İllet(y,x))
```

[⊬ "Gayelilik" burada beşinci evveliyyât DEĞİLDİR — yalnız şuurlu/muhtar faillere hastır, istisnasız her şeye şâmil değildir; kendi yerinde (Hakîm—Gaye—Şer) işlenir]

Kâfi-Sebep'in Nakzeyn'e irca'ı — "tereccüh bilâ müreccih" keyfî bir varsayım değildir:
```
Sebepsiz-tercih(x,H₁,H₂) ≔ Fark(H₁,H₂)=∅ ∧ Vaki(H₁)≠Vaki(H₂)
↯ — "fark yok" ile "netice farklı" aynı anda doğru olamaz [Nakzeyn ihlâli]
```

Burhân-ı İmtinâ-ı Nakz-ı Zâtî (evveliyyâtın hiçbir keşifle çürütülemezliğinin ispatı):
```
∀ iddia T: T anlamlı ⟹ T ≠ ¬T                          [Ayniyet ∧ Nakzeyn]
T ∧ ¬T kabul edilirse ⟹ patlama-ilkesi: her önerme ispatlanır ⟹ "T"nin de mânâsı kalmaz
∴ Nakzeyn'i inkâr etmek, inkârı söylemek için dahi Nakzeyn'i doğru kabul etmeyi gerektirir
```

Tatbik — kuantum mekaniği evveliyyâtı nakzetmez (kategori hatası reddi):
```
Kavânîn-i Tabîiyye (yerçekimi, Schrödinger denklemi, vb.) ≔ âdetullah, zıddı aklen mümkin
Mebâdi-i Akliyye (Ayniyet, Nakzeyn, …)                    ≔ varlığın var-olma şartı, zıddı aklen muhal

Süperpozisyon: |ψ⟩=α|c⟩+β|ö⟩ ≔ ihtimal genliği (vektör toplamı), MANTIKSAL ∧ değil
  ⟹ ölçüm ânında ya c ya ö [Nakzeyn'e dokunmaz]

∴ Mebâdi-i Akliyye ≻ Kavânîn-i Tabîiyye
  ∀ Teori Θ (kuantum dâhil): Θ vaz'olunabilmesi (P(Θ)∧¬P(Θ) ⟹ Butlân) şartına bağlıdır
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

## Basitlik (Lemma — Sıfat Adı Değil)

```
Basitlik(çeşit) = { basit, mürekkep }     κ = tek-cüz(x)?
```
[⊬ müstakil sıfat olarak; ⊢ yalnız Vahdâniyet ispatında ara-basamak — bkz. §Selbiyye]

## Makûlât (yalnız Cevher kanadı)

```
Mevcûd = Cevher ⊔ Araz                    κ = kâim-bi-nefsihî(x)?
```
(Cevher: kendi başına, bir mevzuya muhtaç olmaksızın duran. Vâcibü'l-Vücûd(Kıyam) bu tarifin en tam mertebesidir.)

## Taksim-i Aklî (Mâhiyet Taksimi)

```
Taksim(Mâhiyet) = { vâcib, mümkün, mümteni }
  κ₁ = muhal(hâriçte-bulunmaması)?      → evet: vâcib
  ¬κ₁ ∧ κ₂ = muhal(hâriçte-bulunması)?  → evet: mümteni  [∉ Mevcûd]
  ¬κ₁ ∧ ¬κ₂                             → mümkün
```

**NAKZ (F 2-Y):** Bu formül, eski `Tasdik(Vücûb) = {vâcib,mümkün,mümteni}, κ₁=muhal(yokluk)?...` formülünün yerine geçer. Eski formül `x mevcûd mu?` ile başlıyordu; bu, mümteniyi (hâriçte hiç bulunamayan mâhiyeti) taksimden önce "mevcûd" sayıp sonra dışlamayı gerektiriyordu — usul hatası. Yeni formül taksimi zihindeki mâhiyete tatbik eder, mevcûdiyeti önceden varsaymaz.

## Hakk-ı Vücûd (Mâhiyet-Vücûd Ayrımı)

```
Mümkinde:  Mâhiyet(x) ≠ Vücûd(x)                 [vücûd, mâhiyete zâiddir]
Vâcib'de:  Mâhiyet(Vâcibü'l-Vücûd) = Vücûd(Vâcibü'l-Vücûd)   [ayniyet]

Mâhiyet(x)≠Vücûd(x) ⟹ hârice-çıkış(x) = ilave ⟹ müreccih-i-hâricî(x) lâzım   [§İmkân'ın temeli]
```

## Vâcibü'l-Vücûd — Burhân-ı İmkân (Burhan-ı Sıddîkîn)

⊳ Burhan(çeşit) [mimari/FORMULLER.md § Burhan]: istikametli.innî.eserden-müessire.fâiliye
  [⊬ açık: bazı İslam filozofları Sıddîkîn'i üçüncü, müstakil bir tür sayar — bkz. izahat/burhan/genel.md]
  — maddede içteki devir/teselsül/tatbik kapatmaları (3, 3-B) kendi başlarına birer HULF'tur

```
1)  Taksim(Mâhiyet) = { Vâcib, Mümkin, Mümteni }        [mümteni ∉ Mevcûd]

2)  Mümkinü'l-Vücûd(Şart) = { müreccih-i hâricî }
    ⟸ ¬(tereccüh bilâ müreccih)     [sebepsiz tercih = nakz]
    ⟸ ⋉ Hakk-ı Vücûd [mâhiyet≠vücûd ⟹ ilave ⟹ müreccih]

3)  Silsile-i Esbâb(Nihayet) = { Vâcibü'l-Vücûd }

    devir:    A ─sebeb→ B ─sebeb→ A
              A, B'yi var ediyor; B, A'yı var ediyor ⟹ A kendi kendini var ediyor
              ⟹ A, kendi vücûdundan ÖNCE var olmuş olmalı
              ↯ muhal — bir şey kendi vücûdundan önce var olamaz

    teselsül: silsile = A₁ ─sebeb→ A₂ ─sebeb→ A₃ ─sebeb→ … (sonsuza)
              ∀i: Mümkin(Aᵢ)                      [her halka tek başına mümkin]
              Küll = bütün silsile (A₁,A₂,A₃,…)
              cüzlerin hiçbiri Vâcib değilse Küll de bizatihi Vâcib OLAMAZ
                [sonsuz da olsa, mümkinlerin toplamı yeni bir vücûd-kaynağı üretmez]
              ⟹ Mümkin(Küll) ⟹ Küll de ⋉[2]: müreccih-i hâriciye muhtaç
              ↯ — erteler, müreccih ihtiyacını gidermez

3-B) Burhân-ı Tatbik — devir/teselsülden bağımsız üçüncü kapatma, "terkib mugalatası" itirazına zırh:
    K = bütün mümkinler kümesi.  sebeb(K) ∈ K  ∨  sebeb(K) ∉ K     [Nakzeyn]
      sebeb(K) ∈ K  ⟹  K'nin bir elemanı kendi ve K'nin sebebi  ⟹  ↯ [devir ile aynı muhal]
      sebeb(K) ∉ K  ⟹  K = bütün mümkinler ⟹ K-dışı = Mümkin-olmayan = Vâcib
    ∴ bu tatbik "parçanın vasfı bütüne geçer" öncülünü hiç kullanmaz

∴  ∃! Vâcibü'l-Vücûd                    [1,2,3,3-B'den]

4)  Vâcibü'l-Vücûd(Basitlik) = { basit }     [lemma, bkz. yukarı — müstakil sıfat DEĞİL]
    mürekkeb ⟹ ictimâʻ-i-ecza ⋉[2] ⟹ muhtâc   [Vâcib-tarifiyle çelişki]

5)  |{x : x Vâcibü'l-Vücûd}| = 1     [Vahdâniyet]
    ∃x≠y (ikisi Vâcib) ⟹ temayüz ⟹ terkib(cins,fasıl) ⟹ ↯[4]   [çelişki]

6)  Vâcibü'l-Vücûd(Zaman) = { ezelî(Kıdem), ebedî(Beka) }
    bidâyet ∨ nihâyet ⟹ tagayyür ⟹ ⋉[2]-muhtaçlık   [Vâcib'e münâfî]

    Vâcibü'l-Vücûd(Kıyam) = { bi-nefsihî }
    ⋉ Makûlât.Cevher   [en tam mertebe: mevzûsuz ∧ şartsız kıyam]

    Vâcibü'l-Vücûd(Muhalefet) = { li'l-havâdis }
    ⟸ [1]: Vâcib ∩ Mümkin = ∅ ; havâdis ⊂ Mümkin

7)  Netice (sıfat değil, sonuç): ¬Cisim(Vâcib) ∧ ¬Mekân(Vâcib)
    Cisim(x) ⟹ terkib(madde,suret,eb'ad) ⟹ ↯[4]
    Mekân ∈ Makûlât.İzafî.eyne ⟹ mahkûmiyet-i-kategori ⟹ hâcet ⟹ ↯[Kıyam]
```

## Devam-ı Hudûs — İstimrar-ı Halk (Deizmin ve İbn Sînâ'nın Cüz'iyyat İddiasının Reddi)

⊳ Burhan(çeşit): hulf   [deizm faraziyesi kurulur, Nakzeyn ihlâline götürülür, red edilir]

```
A) İstimrar-ı Halk (deizmin reddi):
   Faraziye (ibtal edilecek): ∃t, ∃mümkin(x): bağımsız(x,t)              ["deizm"]
     bağımsız(x,t) ⟹ ¬muhtaç(x,müreccih,t) ⟹ Mâhiyet(x)=Vücûd(x)  [o an]
     ⟹ ↯ Hakk-ı Vücûd: Mâhiyet(x)≠Vücûd(x), mümkin-mâhiyetin SABİT vasfıdır
   ∴ ¬∃t: bağımsız(mümkin,t)
   ∴ ∀t: muhtaç(mümkin, Vâcibü'l-Vücûd, t)
   ∴ Halk : T → Vücûd   [ân değil, kesintisiz bir fonksiyon]

B) Cüz'iyyatın Bilinmesi (İbn Sînâ'nın "yalnız küllî bilgi" iddiasının reddi):
   İbn Sînâ (iddia):  Bilgi(Vâcib, cüz'î) = ∅
     gerekçe: cüz'iyyat-bilgisi ⟹ zamanla-değişen-bilgi ⟹ tagayyür(Zât) ⟹ ↯[Kıdem]

   Reddiye (A ⋉): ∀t: Halk(mümkin, t)
     Halk(x,t) ⟹ İlim(fâil,x,t) zarurîdir   [bir fail, yarattığını yaratırken bilmeden yaratamaz]
     ∀t: Halk(mümkin,t) ⟹ ∀t: İlim(Vâcib, mümkin, t)
   ∴ İlim(Vâcib) cüz'iyyatı ihtiva eder — İbn Sînâ'nın iddiası düşer

   İtiraza cevap (tagayyür şüphesi):
     değişen = TAALLUK (izafî nispet, ⋉ Makûlât.İzafî), değişen ≠ Zât'taki sıfat
   ∴ Kıdem ile mutlak-cüz'î-ilim arasında tenakuz yoktur
```

## İsim / Sıfat(çeşit)

```
İsim(Zât,Sıfat) ≔ Makûlât.İzafî tatbiki

Sıfat(çeşit) = { zâtî, sübûtî }     κ = lâzım-ı-zât-mı(sıfat)?
  zâtî   : sıfat ⊳ Taksim-i Aklî, Hakk-ı Vücûd, Burhân-ı İmkân, Sıfât-ı Selbiyye — esere muhtaç değil
  sübûtî : sıfat ⊳ Lime.İllet-i-Fâiliye(âlem) — esere muhtaç
```

## Sıfât-ı İlâhiyye — Geleneksel Yerleşim (13 İsim)

```
Sıfat(İlâhiyye) = Nefsiyye(1) ⊔ Selbiyye(5) ⊔ Sübûtiyye(7-8)
  Nefsiyye  = { Vücud }
  Selbiyye  = { Kıdem, Beka, Vahdâniyet, Kıyâm-bi-Nefsihî, Muhâlefetün-li'l-Havâdis }
  Sübûtiyye = { Hayat, İlim, Sem', Basar, Kelâm, İrade, Kudret, (Tekvin) }
```
⊬ "Basitlik" bu 13'ün içinde bir isim değildir — yalnız Burhân-ı İmkân[4]'teki ara-basamaktır.

## Burhân-ı Tahsis (Kur'ânî Usul — Burhân-ı İmkân'a Muhtaç Olmayan Müstakil İkinci Yol)

⊳ Burhan(çeşit): istikametli.innî.eserden-müessire.fâiliye   [tahsis=eser, muhassis=müessir]

```
A) Dört İhtimal Taraması (Tûr 35-36):
   İ1) Adem→Vücûd, fail yok         ↯ müreccih-zarureti [2]
   İ2) A, A'yı kendi var etti        ↯ devir [3]
   İ3) mümkinât birbirini doğurur    ↯ teselsül/tatbik [3,3-B]; kanun≠fail
   İ4) Fâil-i Muhtar, Âlim, Kadîr    — yalnız bu ayakta kalır

B) Tahsis (Kamer 49):
   İmkân-ı-Zâtî(x) ≔ x sonsuz alternatif sûretten birini alabilirdi
   Tahsis(x)       ≔ x bilfiil TEK bir sûrete tatbik edilmiş  ["kader"]
   κ: muhassis(x) = ?
     kör-madde/tabiat ⟹ şuursuz, bilemez, gaye-gütmez  ↯
     kanun            ⟹ oluş-tarzı, fail değil, tahsisin NETİCESİ  ↯
   ∴ muhassis(x) = Fâil-i Muhtar ∧ Âlim ∧ Mürîd ∧ Kadîr
```

## Vahdâniyet — Burhân-ı Temânu' (Enbiyâ 22, Hâricî Te'kid)

⊳ Burhan(çeşit): hulf   [iki-ilah faraziyesi kurulur, üç ihtimalin hepsi muhale götürülür]

```
Faraziye: ∃ A≠B, ikisi de ilâh.  hâdise(h): A murad(hareket,h), B murad(sükûn,h)
  İ1) ikisi de vaki  ⟹ hareket∧sükûn(h)          ↯ Nakzeyn
  İ2) ikisi de yok   ⟹ aciz(A)∧aciz(B)            ↯ aciz≠ilâh
  İ3) biri vaki      ⟹ galip=Vâhid, mağlup=aciz   ↯ aciz≠ilâh, mağlup=mahlûk
∴ nizam(âlem) bilfiil kâim, fesad yok ⟹ ∃! Fâil-i Mutlak
```

## Sıfât-ı Selbiyye — Tam Liste (5)

```
Vahdâniyet             ⊢ [5, mantıkî] ∧ Burhân-ı Temânu' [Kur'ânî]  — iki müstakil yol
Kıdem, Beka            ⊢ [6]
Kıyâm-bi-Nefsihî        ⊢ [6]
Muhâlefetün-li'l-Havâdis ⊢ [6]
```

## Fâil-i Muhtar / Mûcib bi'z-Zât (Sübûtiyyeye Mukaddime — Sudûr İtirazının Reddi)

```
Mûcib-bi'z-Zât(x)  ≔  şart-tamam(x) ⟹ eser(ânî,hep-aynı,kayıtsız-şartsız)     [ateş]
Fâil-i-Muhtar(x)   ≔  şart-tamam(x) olsa dahi ⟹ eser(x) tahsis∧tehir-edilebilir

İrade(Vâcib) ⟹ Fâil-i-Muhtar(Vâcib)
∴ ¬(Vâcib = illet-i-tâmme-mûcibe)
∴ sudûr(âlem|Vâcib) = ihtiyârî, ¬mecbûrî
∴ ¬zarurî(kıdem(âlem))     [felâsifenin sudûr-itirazı düşer]
```

## Sıfât-ı Sübûtiyye

```
Hayat  ≔ {İlim,Kudret} ⋉ Aklî-Âdî("ilim∧kudret→hayat şarttır")

İlim   ≔ nizam(âlem) ⋉ Lime.İllet-i-Gâiye ⟹ gaye-güden-fail
       + Burhân-ı Tesviye (A'lâ 2-3): asıl(basit,şuursuz) ↝ netice(müntazam,ahenkli)
         kaide: fâkıdü'ş-şey' lâ yu'tîh ⟹ Musavvir-Hakîm zarurî
         ⊳ Burhan(çeşit): istikametli.innî.eserden-müessire.{fâiliye,sûriyye}
           [tesviye/ölçü bizzat SÛRETe işaret eder — İllet-i-Sûriyye köşesini dolduran ilk burhan]
       + cüz'iyyatı da ihtiva eder — bkz. Devam-ı Hudûs.B (İbn Sînâ reddi)

İrade  ≔ Mümkinü'l-Vücûd(Şart) ⋉ fizik-sâbiteleri
       κ=zarurî-bizatihî(değer)? ¬tenakuz(değer)⟹mümkün(değer)
       eşit-ihtimal ⟹ TEK-tahakkuk ⟹ kanun≠fail ⟹ İrade

Kudret ≔ Burhân-ı Tahsis ∧ Devam-ı Hudûs ⟹ îcad-kudreti   [NAKZ: önceki "Hudûs(âlem) ⟹ Kudret" bağı kesildi — Hudûs Delili ayrı ek delil, cedelî-yüksek]
  Hudûs Delili (muhtasar):
    cisim(x) ⟹ ¬hâlî(a'râz,x)          [her cisim dâimâ bir hâl üzere]
    hâl(araz) ⟹ hâdis(araz)             [her hâl öncekinin yerini alır]
    ¬hâlî(havâdis,x) ⟹ hâdis(x)          [kaide: mâ lâ yahlû ani'l-havâdis fe-huve hâdis]
    ∴ hâdis(âlem) — sonsuz geçmiş-hâdis zinciri, teselsül-burhanıyla [3] aynı yapıda muhaldir

Tekvin ≔ Kudret(bilkuvve,ezelî,değişmez) ≠ Tekvin(bizzat-fiil, Hâlıkıyet)
       Kıdem(Vâcib) ⋉ ⟹ Hâlıkıyet ezelî; mahlûkun an-be-an hudûsu Kudret'in
       "hep hazır olması" ile açıklanamaz ⟹ Tekvin müstakil sıfattır
       [Mâturîdî tercihi; Eş'arî: Tekvin ⊂ Kudret — açıkça beyan edilir, F 2-Y]

Sem', Basar ≔ İlim'den AYRI, zâtta kâim, müstakil iki sıfat
       [Ehl-i Sünnet cumhuru — Eş'arî ∧ Mâturîdî; İlim'e irca Mu'tezile/felâsifeye aittir]

Kelâm  ⊳ Fasıl II
```

## Hakîm — Gaye — Şer

```
Gaye(çeşit) = { zarurî, ihtiyarî }
  Vâcib(fiil)=ihtiyarî ⋉[İrade] ⟹ ¬abesiyet(Hakîm)

Şer(çeşit) = { ademî, izafî }     κ = ayn-ı-vücûd-mu(şer)?
  ademî: şer=adem(hayr)          izafî: şer=bedel-i-cüz'î(küllî-hayr)

Hakîm∧Şer(mevcûd)?
  (a) mantıkî tenakuz? TEK tutarlı senaryo (ademî∨izafî) ⟹ ¬tenakuz     [burhânî]
  (b) şu-şerrin müspet hikmeti? adem-i-vücdan≠adem-i-vücud ⊳ Fasıl III  [cedelî — kasten]
```

## Ateizm, Mümteni, Hudûs/Zaman/Entropi, Aklın Usulü, Çürütülebilirlik  (şerh: content/fasil_1.md §10-14)

```
NAKZ (F 2-Y): "Kudret'in ispatı için âlemin zamanî başlangıcı şart" ⊬
  Kudret ⟸ Burhân-ı Tahsis ∧ Devam-ı Hudûs  — âlem ezelî de olsa geçerli
  Hudûs Delili ≔ AYRI ek delil ; (T) = cedelî-yüksek
    ∵ "sonsuz geçmiş = tamamlanmış sonsuz" adımı zamanın akışına (A-teorisi) bağlı ; B-teorisi kabul edenler reddeder

Ateizm(çeşit) = { kesin, şüphe }   κ = "Allah yoktur" hükmü veriyor mu?
  kesin ≔ ¬∃x Vâcib(x) ⟹ ∀x Mümkin(x) ⟹ Mümkin(K) ⟹ sebeb(K) ∈ K ↯ devir ∨ sebeb(K) ∉ K ⟹ Vâcib  ⟹ ↯   [burhânî]
  şüphe ≔ iddia yok ; halka gösterilir
  çıkışlar: kanun-kendini-seçti | multiverse | brute-fact  ⟹ tahsis-suâli üst kata taşınır (silinmez)      [burhânî]

Mümteni:  "kaldıramayacağı taş" ≔ taş ∧ kaldırılabilir ∧ ¬kaldırılabilir ↯ ⟹ mümteni bi'z-zât
  Kudret ⋉ Mümkin(şey) ; mümteni ∉ şey ⟹ Kudret noksanlaşmaz
  mümteni(çeşit) = { bi'z-zât, bi'l-gayr }

Zaman = { mutlak-kap (Newton), değişimin-ölçüsü (Aristo, Eş'arî, Gazâlî), donmuş-blok (B-teorisi) }
  risale: değişimin-ölçüsü ; ∵ mutlak-kap ⟹ ezelî ikinci şey ⟹ ↯ Vâcib'in tekliği  [tercih, beyan edildi]
Entropi ⊳ Kavânîn-i Tabîiyye ⟹ Mebâdi ≻ Kavânîn : mantıkî zaruret ÇIKMAZ                                  [kendi kaidemiz]
  entropi → hudûs : hitâbî/cedelî destek ; düşük-başlangıç → tahsis-suâli ⟹ Burhân-ı Tahsis'i güçlendirir

Bilgi-Aklı: akıl hükmü = { vâcib, mümkin, mümteni } ; mümkin ⟹ vukuu ∈ { müşahede, haber }
  mümteni ∧ nass-zâhir ⟹ te'vil (nass yanlış okunmuş)
Hüküm(kuvvet) = Sübût{kat'î,zannî} × Delâlet{kat'î,zannî}   ⟺ₜ (iki ikili Nakzeyn)
  akîde ⟸ kat'î×kat'î  (cumhur ; âhâd-akîde ihtilafı: Ahmed/İbn Hazm ≠ cumhur)
  fürû' ⟸ zann-ı gâlib yeter

Çürütülebilirlik: her netice ⟹ ilk öncül ⟹ reddin bedeli (çelişki) — content/fasil_1.md §14 tablosu
  yeni teori ⟹ (1) evveliyyât-çürütme ↯ ; (2) öncül-reddi ⟹ bedeli öde ; (3) cedelî-halka ⟹ çekirdek etkilenmez
```

## Temel Usul (Nakzeyn Tabanlı Tasnif)

Her tasnif dört adım: (1) κ seç, (2) Nakzeyn'le ikiye böl, (3) isimlendir, (4) dehliz sına (üçüncü bir misal ara). Nakzeyn'in kendisi ispat edilemez, yalnız inkârının kendini nakzettiği gösterilir (Aristo, Metafizik Γ) — bu, devir/teselsülün mecburen bittiği yerdir.

İzahat: `mimari/izahat/vacibul_vucud/genel.md`, `mimari/izahat/rukun_sart/genel.md`, `mimari/izahat/tasnif/tefrik_ve_temyiz.md`, `mimari/izahat/burhan/genel.md` (bu fasıldaki bütün burhanların Burhan(çeşit) tasnifindeki yerini gösteren dehliz tablosu), `risale/content/fasil_1.md` (çoban seviyesinden kademeli izahı, kelime kökenleriyle).

## Not: Burhanların Kapalı Üst Kümesi (Burhan(çeşit))

Bu fasıldaki beş burhan (İmkân, Hudûs, Tahsis, Temânu', Tesviye — +Devam-ı Hudûs, +devir/teselsül reddi) birer **isim listesi** değil, `mimari/FORMULLER.md § Burhan`de κ+Nakzeyn ile kapalı olarak inşa edilen **Burhan(çeşit)** tasnifinin örnekleridir: `Sûret={istikametli,hulf} × Nisbet-i-Evsat={limmî,innî} × İnnî-alt-tür × İllet`. Her biri yukarıda kendi maddesinde `⊳ Burhan(çeşit): …` satırıyla etiketlendi.

**Bir nakz ve düzeltme:** İllet ekseni ilk yazılışında `{mâddiye,sûriyye,fâiliye,gâiye}` diye dört EŞİT köşe olarak kurulmuştu — bu, örtük bir maddeci önvarsayım taşıdığı için yanlıştı (mâddiye/sûriyye yalnız madde+suretten mürekkeb, yani cismânî bir esere tatbik edilebilir; mücerred bir esere hiç tatbik edilemez). Düzeltme `mimari/FORMULLER.md § Mücerred`de yapıldı: önce Mevcûd(Maddiyet)={maddî,mücerred} ayrımı kuruldu ve boş olmadığı Vâcib'in Basitlik'i üzerinden gösterildi (Tâirü'l-Havâ burhânî sayılmadı, cedelî tenbihe indirildi), sonra İllet(çeşit) şöyle şartlandırıldı: `Fâiliye ⊔ Gâiye ⊔ [Maddî(eser) ⋉ (Mâddiye ⊔ Sûriyye)]`. Bu fasıldaki dört istikametli-innî burhandan üçünün (İmkân, Hudûs, Tahsis) eseri mücerred bir vasıftır — mâddiye/sûriyye onlara zaten **kapalıdır**, eksik değil imkânsızdır; yalnız Burhan-ı Tesviye'nin eseri (göz, kulak gibi bir bünye) bizzat maddî olduğu için sûriyye köşesini doldurabilir. Açık kalan tek köşe: **İllet-i-Mâddiye** — risalenin hiçbir burhanı, eserin taşıyıcı maddesine (yalnız sûretine/fâiline/gayesine değil) dayanmıyor; bu tasnifin eksiği değil, henüz doldurulmamış bir hânedir (tafsili: `mimari/izahat/burhan/genel.md`, `mimari/izahat/mucerred/genel.md`).
