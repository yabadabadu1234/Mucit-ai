# Fasıl I — Vücûd Formülleri

(Çekirdek `mimari/FORMULLER.md`den aktarıldı; risale bahsinde geliştirilen yeni formüller —Hakk-ı Vücûd, Burhân-ı Tatbik, Burhân-ı Tahsis, Burhân-ı Temânu', Burhân-ı Tesviye, Fâil-i Muhtar/Mûcib bi'z-Zât, Hudûs Delili, Sıfât-ı Sübûtiyye'nin tamamı— yalnız burada, risale/fasil_1_vucud/ altında mühürlüdür.)

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

```
1)  Taksim(Mâhiyet) = { Vâcib, Mümkin, Mümteni }        [mümteni ∉ Mevcûd]

2)  Mümkinü'l-Vücûd(Şart) = { müreccih-i hâricî }
    ⟸ ¬(tereccüh bilâ müreccih)     [sebepsiz tercih = nakz]
    ⟸ ⋉ Hakk-ı Vücûd [mâhiyet≠vücûd ⟹ ilave ⟹ müreccih]

3)  Silsile-i Esbâb(Nihayet) = { Vâcibü'l-Vücûd }
    devir:    A≺B≺A  ⟹  A≺A            (muhal)
    teselsül: ∀cüz mümkin ⟹ küll mümkin ⟹ küll ⋉ (2)   [erteler, gidermez]

3-B) Burhân-ı Tatbik (devir/teselsülden bağımsız üçüncü kapatma — "terkib mugalatası" itirazına zırh):
    K = bütün mümkinler kümesi.  sebeb(K) ∈ K  ∨  sebeb(K) ∉ K     [Nakzeyn]
      sebeb(K) ∈ K  ⟹  K'nin bir elemanı kendi ve K'nin sebebi  ⟹  devir (3)
      sebeb(K) ∉ K  ⟹  K = bütün mümkinler ⟹ K-dışı = Mümkin-olmayan = Vâcib
    ∴ bu tatbik "parçanın vasfı bütüne geçer" öncülünü hiç kullanmaz

∴  ∃! Vâcibü'l-Vücûd                    [1,2,3,3-B'den]

4)  Vâcibü'l-Vücûd(Basitlik) = { basit }     [lemma, bkz. yukarı — müstakil sıfat DEĞİL]
    mürekkeb ⟹ ictimâʻ-i-ecza ⋉ (2) ⟹ muhtâc   [Vâcib-tarifiyle çelişki]

5)  |{x : x Vâcibü'l-Vücûd}| = 1     [Vahdâniyet]
    ∃x≠y (ikisi Vâcib) ⟹ temayüz ⟹ terkib(cins,fasıl) ⟹ ¬(4)   [çelişki]

6)  Vâcibü'l-Vücûd(Zaman) = { ezelî(Kıdem), ebedî(Beka) }
    bidâyet ∨ nihâyet ⟹ tagayyür ⟹ ⋉(2)-muhtaçlık   [Vâcib'e münâfî]

    Vâcibü'l-Vücûd(Kıyam) = { bi-nefsihî }
    ⋉ Makûlât.Cevher   [en tam mertebe: mevzûsuz ∧ şartsız kıyam]

    Vâcibü'l-Vücûd(Muhalefet) = { li'l-havâdis }
    ⟸ (1): Vâcib ∩ Mümkin = ∅ ; havâdis ⊂ Mümkin

7)  Netice (sıfat değil, sonuç): ¬Cisim(Vâcib) ∧ ¬Mekân(Vâcib)
    Cisim(x) ⟹ terkib(madde,suret,eb'ad) ⟹ ↯(4)
    Mekân ∈ Makûlât.İzafî.eyne ⟹ mahkûmiyet-i-kategori ⟹ hâcet ⟹ ↯(Kıyam)
```

## Sıfât-ı İlâhiyye — Geleneksel Yerleşim (13 İsim)

```
Sıfat(İlâhiyye) = Nefsiyye(1) ⊔ Selbiyye(5) ⊔ Sübûtiyye(7-8)
  Nefsiyye  = { Vücud }
  Selbiyye  = { Kıdem, Beka, Vahdâniyet, Kıyâm-bi-Nefsihî, Muhâlefetün-li'l-Havâdis }
  Sübûtiyye = { Hayat, İlim, Sem', Basar, Kelâm, İrade, Kudret, (Tekvin) }
```
[⊬ "Basitlik" bu 13'ün içinde bir isim değildir — yalnız (4)'teki ara-basamaktır]

## Burhân-ı Tahsis (Kur'ânî Usul — Burhân-ı İmkân'a Muhtaç Olmayan Müstakil İkinci Yol)

```
A) Dört İhtimal Taraması (Tûr 35-36):
   İ1) Adem→Vücûd, fail yok         ↯ (2)-müreccih-zarureti
   İ2) A, A'yı kendi var etti        ↯ devir (3)
   İ3) mümkinât birbirini doğurur    ↯ teselsül/tatbik (3,3-B); kanun≠fail
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

```
Faraziye: ∃ A≠B, ikisi de ilâh.  hâdise(h): A murad(hareket,h), B murad(sükûn,h)
  İ1) ikisi de vaki  ⟹ hareket∧sükûn(h)          ↯ Nakzeyn
  İ2) ikisi de yok   ⟹ aciz(A)∧aciz(B)            ↯ aciz≠ilâh
  İ3) biri vaki      ⟹ galip=Vâhid, mağlup=aciz   ↯ aciz≠ilâh, mağlup=mahlûk
∴ nizam(âlem) bilfiil kâim, fesad yok ⟹ ∃! Fâil-i Mutlak
```

## Sıfât-ı Selbiyye — Tam Liste (5)

```
Vahdâniyet             ⊢ (5) [mantıkî] ∧ Burhân-ı Temânu' [Kur'ânî]  — iki müstakil yol
Kıdem, Beka            ⊢ (6)
Kıyâm-bi-Nefsihî        ⊢ (6)
Muhâlefetün-li'l-Havâdis ⊢ (6)
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

İrade  ≔ Mümkinü'l-Vücûd(Şart) ⋉ fizik-sâbiteleri
       κ=zarurî-bizatihî(değer)? ¬tenakuz(değer)⟹mümkün(değer)
       eşit-ihtimal ⟹ TEK-tahakkuk ⟹ kanun≠fail ⟹ İrade

Kudret ≔ Hudûs(âlem) ⟹ îcad-kudreti
  Hudûs Delili (muhtasar):
    cisim(x) ⟹ ¬hâlî(a'râz,x)          [her cisim dâimâ bir hâl üzere]
    hâl(araz) ⟹ hâdis(araz)             [her hâl öncekinin yerini alır]
    ¬hâlî(havâdis,x) ⟹ hâdis(x)          [kaide: mâ lâ yahlû ani'l-havâdis fe-huve hâdis]
    ∴ hâdis(âlem) [sonsuz geçmiş-hâdis zinciri = teselsül (3) ile aynı muhal]

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
  Vâcib(fiil)=ihtiyarî ⋉(İrade) ⟹ ¬abesiyet(Hakîm)

Şer(çeşit) = { ademî, izafî }     κ = ayn-ı-vücûd-mu(şer)?
  ademî: şer=adem(hayr)          izafî: şer=bedel-i-cüz'î(küllî-hayr)

Hakîm∧Şer(mevcûd)?
  (a) mantıkî tenakuz? TEK tutarlı senaryo (ademî∨izafî) ⟹ ¬tenakuz     [burhânî]
  (b) şu-şerrin müspet hikmeti? adem-i-vücdan≠adem-i-vücud ⊳ Fasıl III  [cedelî — kasten]
```

## Temel Usul (Nakzeyn Tabanlı Tasnif)

Her tasnif dört adım: (1) κ seç, (2) Nakzeyn'le ikiye böl, (3) isimlendir, (4) dehliz sına (üçüncü bir misal ara). Nakzeyn'in kendisi ispat edilemez, yalnız inkârının kendini nakzettiği gösterilir (Aristo, Metafizik Γ) — bu, devir/teselsülün mecburen bittiği yerdir.

İzahat: `mimari/izahat/vacibul_vucud/genel.md`, `mimari/izahat/rukun_sart/genel.md`, `mimari/izahat/tasnif/tefrik_ve_temyiz.md`, `risale/content/fasil_1.md` (çoban seviyesinden kademeli izahı, kelime kökenleriyle).
