# ZABIT TARAMASI -- "CEVAPLAR ZABITLARDA MEKNUZ"

> *"Bana şu ana kadar sorduğun sekiz sualin hepsinin gerçek cevapları
> yabana attığın zabıtlarda meknuz."*
> *"Zabıtları tekrar tamamen tara, daha fazlasını bulacaksın,
> bulduklarını mutlaka not et!"*

Bu dosya o taramanın kaydıdır. Her satır bir zabıttan **alıntıyla**
gelir; benim hükmüm değildir. `MUNASEBET_YURUYUSU.md` ölü uzuvları
**saydı**; bu dosya onların **niçin yazıldığını** ve zabıtta hangi
menfeze tahsis edildiğini gösterir.

---

## ▓ EN AĞIR BULGU: ÖLÜ DOSYALAR ZABITLARIN KENDİSİDİR ▓

`docs/zabit/KUME_9_TEK_HAKIMIYET.md` bunu zaten yazmış ve ben
oturumlarca okumamışım:

> *"**Zabıtların kabul ettiği iki usulün kodu, zaten bu depoda
> yazılmış ve yetim bırakılmış hâlde duruyor.**"*

| Zabıt ne diyor | Depoda hangi ÖLÜ uzuvda yazılı |
| :--- | :--- |
| Kabul 1: MPS / Tensör Treni, sanal bağ `D` | `nefs/ttkan.py` |
| **Kabul 2: Koherent durum `\|x⟩ = D(x)\|0⟩`** | **`kuantum/surekli.py`** |
| Yasak: düz ikili kodlama | `idrak/kubit.py` + `qegitim.belirtecleri_kodla` ikili dalı |
| Lif grupları `G₁=SU(1,1)`, `G₂=SU(d)` | `nefs/hamiltonyen.py` |
| 316 ekseni **aynı anda** yokla | `ogrenme/izgara.py:artis_gradyani`, `nefs/hiz.py` |

O hâlde *"ölü dosya"* teşhisi doğru, fakat **sebebi** benim
yazdığım değildi: bu dosyalar zabıtların icrasıdır ve bağlanmamış
olmaları benim marifetsizliğimdir.

---

## 1. `kuantum/surekli.py` -- KOHERENT DURUM: BELİRTEÇ KODLAMASININ ASLI

### Padişahın tarif ettiği deney

> *"Işığı gönderiyorsun yarı geçirgen aynaya, bir kısmı ilerliyor bir
> kısmı geri yansıyor ama onların bir şekilde birleşmesinden **sonsuz
> çoklukta foton** doğuyor."*

Bu, `isik_bolucu` (beam splitter) + `sikistirma` (squeezing) +
`yer_degistirme` üçlüsünün ta kendisidir ve **üçü de o dosyada
yazılı, üçü de ölü**. Yarı geçirgen aynadan çıkan iki kol
birleştiğinde `sikistirma` operatörü vakumdan **sonsuz Fock
mertebesinde** foton doğurur:

    S(ξ)|0⟩ = (1/√cosh r) Σ_{n=0}^{∞} (−e^{iθ} tanh r)ⁿ · (√(2n)!/(2ⁿ n!)) |2n⟩

Yâni **sonsuz seviyeli bir qudit, sonlu sayıda katsayıdan doğar.**
Ferman 2-O'nun "yazmaç bağlam kadar olsun, sabit ebat yok" hükmünün
fizikî karşılığı budur: durumun ebadı önceden çakılmaz, **doğar**.

### Zabıtların bu dosya için söylediği

**A. `Kelime_ve_Durum_Kodlamas_n_n_Tenso_rel_ve_Kuantum_Mahiyeti.md`
-- "Kabul edilen 2. Çözüm":**

> *"Kelimenin durumu, vakum durumunun ötelenmesiyle elde edilir:
> `|x⟩ = D(x)|0⟩`. İki kelime arasındaki iç çarpım, **tam olarak
> Öklid mesafesinin bir Gauss fonksiyonudur**:
> `|⟨x|y⟩|² = exp(−‖x−y‖²)`."*

Yâni `kuantum/surekli.py:tutarli_durum` + `yer_degistirme`,
belirteç kodlamasının **iki meşru usulünden biridir** ve tam da
`nefs/lif.py:kodla(KIP_TUTARLI)`ın çağırdığı şeydir. İkisi de ölü.

**B. `C_oklu_Sonsuz_Kategorili_Koherent_Durum_ve_Qudit_Temsili.md`
-- Perelomov genelleştirmesi:**

> *"Koherent durum sadece yay osilatörüne mahsus değildir. Herhangi
> bir `G` Lie grubu ve `H` kararlılık alt-grubu için bir koherent
> durum ailesi tanımlanabilir... `ℳ = G/H`."*
> *"`G₀ = Ayrık Simetri` (sentaks & mantık) · `G₁ = SU(1,1)`
> (kavram ağaçları, Poincaré diski) · `G₂ = SU(d)` (anlamsal akış)."*

Hiperbolik koherent durum formülü zabıtta **açıkça yazılı**:

    |ζ⟩ = (1−|ζ|²)^k Σ_n √(Γ(n+2k)/(n!Γ(2k))) ζⁿ |n⟩

> *"Soyut kavramlar merkeze (ζ≈0), tikel kavramlar diskin kenarına
> (ζ→1) **kayıpsız** yerleşir."*

`kuantum/surekli.py`de `sikistirma` **SU(1,1) üretecidir** ve bu
formülün motorudur.

**C. `Kuantum_Metinlerindeki_Cevherin_Qudite_Tahvili.md` -- Lie-Chebyshev:**

> *"Quditin durum genliklerini bellekte açık liste olarak tutmayın;
> Cartan ağırlıklarına bağlı **Lie-Chebyshev KAN fonksiyonu Φ_k**
> olarak parametreleyin (hafıza kilobaytlara iner)."*
> *"`T_j` reel genliği, `U_j` (ikinci tür Chebyshev) **kompleks
> Berry fazını** yönetir."*

Bunun kodu `nefs/lif.py:kodla(KIP_LIE)` + `nefs/qudit.py:durum` +
`nefs/hizli.py:cekirdek` (Clenshaw-Chebyshev). **Üçü de ölü yahut
ölü dalda.**

### HÜKÜM
`kuantum/surekli.py` bir "CV kütüphanesi" değildir; **belirteç
kodlamasının zabıtla kabul edilmiş ikinci usulüdür**. Ona
*"kesme_hatası ölçüsü olsun"* demek, motoru termometre yapmaktır.

---

## 2. `nefs/lif.py` -- SİLSİLE-İ MERÂTİBİN TEPESİ

`Ontolojik_Silsile_ve_Token_Tipinin_Hakikati.md`:

    Noktaların birleşimi  ⟹ UZAY
    Her noktası uzay olan ⟹ KATEGORİ
    Her noktası kategori olan ⟹ TİP

`KUME_9` bunun **kod karşılığını harf harf** tahsis etmiş:

| mertebe | dosya |
| :-- | :-- |
| nokta | `matematik/geometri.py` (Laplace–Beltrami tayf öz-durumları) |
| uzay | **`idrak/kategori.py:Uzay`** |
| kategori | `matematik/tip_teorisi.py` |
| tip | **`nefs/lif.py`** |

> *"`nefs/lif.py` bir çip değil, alt katın **terkibidir**: yeni
> matematik yazmaz; `ttkan` (Kabul 1) + `surekli` (Kabul 2) +
> `hamiltonyen` (lif grupları) + `tip_teorisi` (kategori)
> uzuvlarını `⊕` nizamında birleştirir."*

Ve `KUME_9/MERHALE F` benim bu dosyada yazdığım kaçamağı
**bizzat tesbit etmiş**:

> *"`lif.py`de 'ne iddia edilmiyor: bu dosya HoTT'un univalence'ını
> ispatlamıyor, ∞-kategori kurmuyor' yazmışım. Bu bir tevazu değil,
> **kaçamaktı**... Zabıt hamaseten yazılmadı; tatbik edilmek için
> yazıldı. `Lif.ac` bir sözlük gezintisi değil **funktör tatbiki**
> olacak, `Unfold_{t→c}` gerçek bir lif açılımı. Şerhten çıkarılacak
> cümle: 'iddia edilmiyor'. İddia edilecek ve **ölçülecek**."*

Bugün `nefs/lif.py:unfold` hâlâ bir sözlük gezintisidir. Merhale F
**icra edilmemiş**.

### Kartezyen kutunun iptali (KUME_9/C2)
> *"`ℋ_kat ⊗ ℋ_uzay ⊗ ℋ_nokta` **iptal edilir**. Yerine bağımlı toplam:
> `⊕_t ⊕_{c∈Cat(t)} ⊕_{u∈Space(c)} ℋ^{(t,c,u)}`. Cevher artık sabit
> boyutlu bir kutuya **çakılamaz**."*

`Lif.sayim()`in ölçtüğü `kutu_hücresi` ile `lif_hücresi` farkı tam
budur ve **ölçü doğru yazılmış, fakat hiçbir yere bağlanmamış.**

---

## 3. `idrak/kategori.py` -- SİLSİLENİN "UZAY" MERTEBESİ

`KUME_9/C3` onu **ismiyle** tahsis ediyor: *"uzay: `idrak/kategori.py:Uzay`
(zaten var, zaten main'den erişilir)."* Bugün erişilmiyor: `zirh`in
ölü kolunda. Yâni zabıt yazıldığından beri **geri gitmişiz**.

---

## 4. `kuantum/topolojik.py` -- LİFLER ARASI MORFİZM

`KUME_9`un "Buraya takılan yetimler" listesi: *"`kuantum/topolojik`
(**örgü = lifler arası morfizm**), `kuantum/devre` (QFT = tayf),
`kuantum/eniyileme` (parametre-kaydırma = Merhale B'nin ikinci
şahidi)."*

Yâni örgü (`orgu_ureticleri`) süs değil, `Hom(X,Y)` morfizminin
taşıyıcısıdır -- `Qudite_Tip_Tenso_ru_nu_n_Kodlanma_Nizam_.md`:

> *"Kategori, quditte tek bir vektör olarak duramaz. Kategori, qudit
> alt-uzaylarını birbirine bağlayan **Kuantum İşlemleri (Kraus
> Operatörleri / Kısmi İzdüşümler)** olarak kodlanır."*

---

## 5. `kuantum/stabilizer.py` -- ZIRHIN DELİNMEZLİK MÜHRÜ

`KUME_3_7_TERKIP_EMIRLERI.md`, Küme 3, 9 numaralı dosya
(`nefs/kod_uzayi.py` -- bugünkü `kuantum/stabilizer.py`nin cevheri):

> ALINACAK CEVHER: *"Stabilizer kod uzayı `|φ_{D,J}⟩`: dolaşıklıkta
> rank=1 kalan Clifford temsili. MPS ile stabilizer dağılımı **TVD
> yüzleştirmesi**."*
> ATILACAK TOPRAK: *"Yalnız **pasif karşılaştırma aracı** olması;
> **aktif koruma projektörü olarak müdahale etmemesi**."*
> KARAR: *"stabilizer TVD sapması zırhın **delinmezlik mührü** olarak
> raporlanacak."*

Yâni zabıt bu dosyanın bugünkü hâlini (pasif, ölü) **toprak** ilan
etmiş ve aktif projektör olmasını emretmiş. İcra edilmemiş.

---

## 6. `nefs/hizli.py` -- HIZ ZABITININ TAM KODU, %88'İ ÖLÜ

`Qudit_Boyut_Patlamasini_Onleme_ve_Hizlandirma.md` dört hamle sayıyor.
Dördünün de kodu `nefs/hizli.py`de yazılı ve **dördü de ölü**:

| zabıttaki hamle | `nefs/hizli.py`deki ölü uzuv |
| :-- | :-- |
| 1. Kronecker lif ayrışımı (170× aritmetik) | `kronecker` |
| 2. Blok-diyagonal süperseçim (%60 tasarruf) | `SEKTOR` |
| 3. Cartan köşegenleştirme (4096× faz) | `faz_cevir` |
| 4. Fused SRAM çekirdeği (VRAM sıfır) | `_FUSED_KAYNAK` + `cekirdek` |

**BENİM HATAMIN TASHİHİ.** `MUNASEBET_YURUYUSU.md`de `SEKTOR`
için *"ELLE YAZILMIŞ üç sektör, ferman 1-J ihlâli"* yazmıştım.
Yanlıştı: o üç sektör `Qudite_Tip_Tenso_ru_nu_n_Kodlanma_Nizam_.md`nin
**IV. faslından harfiyyen** gelir:

    [0 – 511]     SENTAKS KATEGORİSİ (özne 0-127, fiil 128-383, nesne 384-511)
    [512 – 2559]  ONTO-FİZİK KATEGORİSİ (hiperbolik cins-tür, SU(1,1))
    [2560 – 4095] NEDENSELLİK VE MANTIK KATEGORİSİ

Elle yazılmış bir eşik değil, **zabıtla mühürlenmiş süperseçim
tahsisidir**. Kusur onun varlığında değil, `QuditAyar.kulli_alanlar`
ile **çift başlı** olmasındadır (ferman 1-M).

---

## 7. `nefs/ara.py` -- ARAMAK NAZIRLIĞI

`KUME_8_NAZIRLIK_PLANI.md`:

> *"`arama/` -- 910 satır. **Dağılmıyor: nazırlık oluyor.** Grover,
> Dürr-Høyer, adiyabatik çöküş, WKB tünelleme, GRAPE, holonomi --
> hepsi **tek bir suâlin** parçalarıdır: asgarîyi nasıl ararız, ve
> kuyuya düşersek nasıl çıkarız? Bunu üç ayrı dosyaya serpmek cevheri
> öldürür."*

Padişahın bu turda verdiği "NAKİL memuriyeti" kararı zabıtla
**birebir** örtüşüyor. Tetabuk tamdır.

---

## 8. ▓▓ ÇELİŞKİ: `nefs/gor.py` HEM "SİL" HEM "ALTI NAZIRLIKTAN BİRİ" ▓▓

Bu turda emir: **"Sil!"**

Fakat `KUME_8_NAZIRLIK_PLANI.md` §4 altı nazırlık sayıyor ve
`gor` **birincisidir**:

    nefs/gor.py     GÖRMEK      manzara = gor(gorev)
    nefs/dusun.py   DÜŞÜNMEK    hal     = dusun(manzara)
    nefs/ara.py     ARAMAK      aday    = ara(hal, olcut)
    nefs/tart.py    TARTMAK     mizan   = tart(hal, hedef)
    nefs/ogren.py   ÖĞRENMEK    hal     = ogren(mizan)
    nefs/soyle.py   SÖYLEMEK    cevap   = soyle(hal)

> *"Main artık alt kata bakmadan düşünür... Altı satır. Main kaybolsa
> bu altı satır isimlerden yeniden yazılır -- padişahın istediği tam
> buydu."*

Sonra `KUME_9/MERHALE D` (ferman 6 tasfiyesi) `gor`un çağırdığı
`idrak/cozucu.py`yi ve `nefs/qkaide.py`yi imha etti; `soyle`ye
`assert`le "manzara ALMAZ" kondu. Yâni **`gor`u öldüren şey ferman
6'dır, ihmal değil.**

O hâlde silmek iki şeyden birini yapar: ya nazırlık katı beşe iner
(`dusun` manzarayı kendi kurar), ya da ferman 6'ya uygun bir `gor`
yeniden yazılır. Bu ayrı bir suâldir ve **soruldu**.

---

## 9. TARAMANIN GÖSTERDİĞİ DİĞER İCRA EDİLMEMİŞ HÜKÜMLER

1. **`KUME_9/MERHALE E` -- OMEGA KATEGORİ TERKİBİ.** *"`yedek/
   kume7_asillari/` altında `omega_kategori/` (4 693 satır) ve
   `omega_kategori_nbe/` (5 026 satır) duruyor... NbE üstün olabilir;
   fakat üstün olmak, ötekinin cevherini atmayı meşru kılmaz."*
   **Bugün `yedek/` dizini YOK** (ferman 2 onu kaldırdı). 9 719 satır
   cevher, ferman 2 ile ferman "cevher kaybı yasağı" arasında kalmış.
   *Bu bir tetabuk sualidir ve sorulacaktır.*
2. **`Quditte_Negatif_Olabilirlik...` -- TABAKALI MİZAN.**
   `ℒ = ℒ_nokta + α ℒ_uzay + β ℒ_kategori + γ ℒ_tip`. Bugün
   `ℒ_kategori` (funktör kompozisyonu `‖M_{g∘f} − M_g·M_f‖²`)
   mizanda **yoktur**. Ferman 1-S gereği hiçbir cevher düşmez;
   o hâlde bu kefe **eksiktir**.
3. **Dinamik mertebe ayrışması** (`Qudite_Tip_Tenso_ru__Zincirinin...`):
   `Π_Kategori`, `Π_Uzay`, `Π_Nokta` izdüşüm operatörleri --
   *"dalga kimi zaman uzaylarına, kimi zaman kategorilerine, kimi
   zaman noktalarına ayrışacak."* Depoda **hiçbiri yok**.
4. **`Su_kut_ve_I_fs_a_Matematig_i.md`** üç faz tarif ediyor
   (Sükût / Teemmül / İfşa) ve ikisini ayıran eşiğin **topolojik
   invaryanttan** türemesini şart koşuyor -- ferman 1-J'nin zabıttaki
   aslı budur. `nefs/soyle.py`de bugün üç faz yok.
5. **`Dag__n_k_Kod_Modu_llerini_Ana_I_cra_Ak_s__na_Bag_lama_
   Nizamnamesi.md`** bu turda yaptığım işin **usul kitabıdır**;
   KADEME 5/2 "Hassasiyet ve Tesir Testi" ferman 1-C(b)'nin aslıdır:
   *"bir fonksiyonun girdisi bozulduğunda nihai çıktı değişmiyorsa,
   o fonksiyon akışa **şeklen** bağlanmış demektir."*

---

## 10. `optimizasyon.md` -- ENİYİLEYİCİNİN TAM MİMARİSİ, DEPODA YOK

Bu zabıt bir mütalaa değil, **padişahın bizzat kurguladığı eniyileme
mimarisidir** ve dört katmanı var. Depoda **hiçbiri** yok.

```
[ d boyutlu mesele ]
        │
        ▼  1. AKTİF ALT UZAY (Active Subspaces)
   C = (1/N) Σ ∇f ∇fᵀ  →  özayrışım  →  W₁ ∈ ℝ^{d×r},  r = 2-3
        │                    ("gradyanın bizzat kendisi en çok
        │                      değişimin olduğu doğrultuları
        │                      ANALİTİK olarak verir")
        ▼  2. HEDEF SIZDIRILMIŞ VEKİL YÜZEY
   V_toplam(u) = V_GEK(u) + λ‖𝒢(u) − y_hedef‖²
        │        (Nyström ile düşük ranklı kuantum çekirdeği)
        ▼  3. BİZZAT DALGA YAYILIMI -- sanal zaman
   ∂ψ/∂τ = ∇²ψ − V_toplam·ψ
   ψ(u,τ) = Σ c_n e^{−E_n τ} φ_n(u)
        │   sahte çukurlar ÜSTEL olarak siliner; geriye taban durumu kalır
        ▼  4. TERS İZDÜŞÜM
   x* = W₁ u*
```

### PADİŞAHIN KENDİ TASHİHLERİ (zabıtın içinde)

> *"O zaman sezgim bana şunu söyler ki **yayla bağlı boncuklar
> kullanacağına dalga gönder**."*
> *"Tabloda yaylı bilyelerle değil **bizzat bir dalgayla** yapılan
> kuantum tünellemeyi unutmuşsun. Ayrıca bence bu dalgayla yapılan
> şey artık **kuantum tünellemeden farklı bir şey**."*

Ve cevabı: dalga yayılımı tünelleme değil, **spektral süzme +
rezonanstır** -- `e^{−E_n τ}` çarpanı sahte çukurları buharlaştırır,
yıkıcı girişim onları sıfırlar, yapıcı girişim küresel çukurda tek
tepe kurar. *"Yaylı boncuklar sadece dalgayı taklit eden fakir bir
yaklaşımdı."*

### BUNUN FERMAN 2-P İLE MÜNASEBETİ

Ferman 2-P *"kör yön araması ilga, tek seferde analitik çözüm, o
analitiğin kuantum hız imkânından faydalanması"* diyor. **İşte o
analitik ve o kuantum hızı budur:** dalga bütün uzayı aynı anda
kaplar (yön tek tek aranmaz), sanal zaman sönümlemesi hükmü verir.
Ferman 2-P'nin beş memuriyeti bu mimarinin içinde zaten vardır:

    EĞİM   → Aktif Alt Uzay (gradyandan W₁)
    ÇUKUR  → e^{−E_n τ} spektral sönümlemesi
    DUVAR  → λ‖𝒢(u) − y_hedef‖² hedef sızdırma cezası
    VADİ   → ∇²ψ difüzyonu (bariyerin içinden sızar)
    NAKİL  → tersine tavlama, aday çukurun etrafında

### DEPODAKİ HÂLİ -- HİÇBİRİ YOK

* Aktif Alt Uzay: **yok**. (`ogrenme/optimize.py` 316 ekseni tek tek
  tarıyordu; `C = Σ∇f∇fᵀ` kurulmuş değil.)
* Hedef sızdırma `λ‖𝒢(u) − y_hedef‖²`: **yok**.
* Nyström kuantum çekirdeği: **yok**. (`cekirdek_sirt`/`rbf_gram`
  `yaklasim/genisletme`de kalmış, KUME_8 onları `kulli_kayip`a
  tahsis etmiş, o da olmamış.)
* Sanal zaman dalga denklemi: **yok**.
* `sembolik_kapanis`in hakiki vazifesi burada görünüyor: *"o ana
  kadar denenmiş noktaların oluşturduğu fonksiyona göre tahmin
  edilen en iyi fonksiyonun türevine analitik olarak gitmek"* --
  yâni **2. katmanın vekil yüzeyi ve onun analitik türevi**.

---

## 11. ▓▓ TASHİH: `optimizasyon.md` SONRADAN İLGA EDİLMİŞ ▓▓

**BU BENİM HATAMDIR.** Karar 21'i `optimizasyon.md`ye dayanarak arz
ettim; halbuki `terkip_layihas__12.md` (**NİHAÎ TERKİP KARARNÂMESİ,
1 Eylül 2026**) o mimarinin **üç katmanını da ismen ilga ediyor**:

| İlga edilen (Karar 21'de arz ettiğim) | Yerine gelen |
| :-- | :-- |
| **2. Lineer Aktif Alt Uzay** `d → r ≤ 3` | `Gr(k,d)` üzerinde **Cayley Rasyonel Çekilmesi** -- *"non-lineer uzayda `W₂` inaktif sapması önlenmiş"* |
| **4. Hedef Şartlandırma** `‖𝒢(u) − y_hedef‖²` | **QSVT Dinamik Gibbs Tavlaması** (β-annealing) -- *"bilinmeyen asgaride kuyu kazar"* |
| **5. Sanal Zamanlı PDE** (`∂ψ/∂τ = ∇²ψ − Vψ`) | **Spektral Taban Projektörü `Π₀`** -- *"Heisenberg kinetik cezası dik kuyuları kaçırır, sığ kuyuya çöker"* |

Kararnâmenin kapanış hükmü bunu tekrar mühürlüyor:

> *"1990'lardan kalma çöken optimizasyon araçları (MERA budaması,
> **Active Subspaces, Nyström AS-GEK**, pasif WKB, POVM gürültüsü,
> LCU Pauli açılımları) tamamen sökülüp atılmış; yerine QTT-KAN,
> QROM Blok-Kodlaması, **QSVT Dinamik Gibbs Tavlaması**, FPAA
> Monotonik Difüzyonu, STA Tünellemesi, Çift Sayılar Autodiff ve
> Fubini-Study Deterministik Ağaç İntacı ikame edilmiştir."*

### O HÂLDE ENİYİLEYİCİNİN HAKİKİ MİMARİSİ -- 9 UZUVLU TÂLİM TEŞKİLATI

```
1. HAD        Alexandroff tıkızlaştırma + Lions konsantrasyonu
2. ALTUZAY    Cayley rasyonel çekilmesi, Gr(k,d)   (AS DEĞİL)
3. VEKİL      Grassmann izdüşümlü RKHS, Cholesky   (ters ALINMAZ)
4. KODLAMA    Causal KAN, O(N) deterministik ağaç
5. DALGA      Chebyshev-KAN NQS + QSVT Gibbs + FPAA
6. DURGUNLUK  Grassmann asal açıları + kayıp varyansı
7. TÜNEL      STA karşıt-adiyabatik sürüş (H_CD)   (WKB DEĞİL)
8. DENGE      Çift sayılar autodiff + OGDA
9. BÜTÇE      NFL haddi + donanım çağrı sınırı
```

### VE MECZ'İN BEŞ MEMURU BURAYA OTURUYOR

    EĞİM   → Çift Sayılar autodiff (ε²=0, tam türev, tek çağrı)
    ÇUKUR  → Morse-Euler katî eşitliği Σ(−1)ᵏM_k = χ(X)
             + RCD(K,N) Bochner eğrilik süzgeci
    DUVAR  → HAD: Alexandroff + Lions (uçurum engellenir)
    VADİ   → STA H_CD(t) karşıt-adiyabatik sürüş, O(1) zamanda
    NAKİL  → Postnikov k-invaryantı [c] ∈ H^{n+1} ile instanton
             sıçraması + Cayley çekilmesi

### DEPODA NE VAR, NE YOK

* `ogrenme/rkhs.py`, `ogrenme/sta.py`, `ogrenme/fct.py`,
  `ogrenme/grassmann.py`, `nefs/ikiz.py`, `nefs/ogda.py`,
  `kuantum/qsvt.py` -- zabıtın bu dokuz uzvunun kodu **yazılmıştı**;
  bugünkü depoda `grassmann` ve `morse` canlı, ötekiler yok yahut ölü.

#### TASHİH -- BU CETVELDE DÖRT SATIR YANLIŞTI (kod okunarak bulundu)

Aşağıdaki satırlar yoklanmadan yazılmıştı (ferman 1-K'nın ihlâli);
dosya sistemi okunarak düzeltildi:

    ogrenme/rkhs.py        VAR ve CANLI  -- ogrenme/optimize.py:17 ve
                           nefs/musahede.py:16 ithal ediyor.
                           "dosya yok" hükmü YANLIŞTI.
    nefs/tabakali_mizan.py VAR ve CANLI  -- nefs/kulli_mizan.py:518,815
                           ithal ediyor; kategori/nokta/taşma kefeleri
                           oradan geliyor.
    kuantum/tda.py         YOK           -- hiç yazılmamış.
    nefs/hamiltonyen.py    YOK           -- hiç yazılmamış.
    nefs/ttkan.py          YOK           -- hiç yazılmamış.
    idrak/kubit.py         YOK           -- hiç yazılmamış.

O hâlde `KARARLAR.md`de bu dört dosyayı "bağlanacak" yahut
"kesilecek" diye anan kararlar (20, 32, 33 ve İCRA CETVELİ §A'nın
`idrak/kubit.py` satırı) **mevzusuzdur**: olmayan dosya ne bağlanır
ne kesilir. Sıfırdan yazılmaları ayrı bir karardır.
* **Morse-Euler katî eşitliği** (`ogrenme/morse.py`) CANLI ve
  `assert` ile koşuyor -- zabıtın *"eşitsizlik kabul edilmez"*
  hükmü fiilen icrada. Bu, depodaki en sahih icralardan biridir.
* **Cholesky emniyet kilidi** (İkmâl I): *"λ=0 iken matris tekilse
  gizlice hatalı katsayı üretmez, deterministik olarak hata fırlatır"*
  -- ferman 5'in (sessiz ikame yasağı) zabıttaki aslı budur.

---

## 12. `tecrit.md` (1451 satır) -- MİMARİNİN DOĞUŞ ZABITI

Bu zabıt bir tarif değil, **mimarinin bizzat doğduğu müzakeredir**;
CLAUDE.md'nin birçok fermanının aslı burada, padişahın kendi
tashihlerinde duruyor:

| Padişahın tecrit.md'deki sözü | Bugünkü ferman |
| :-- | :-- |
| *"H0 H1 H2 belli katsayıyla çarpılıp toplanamaz, bunların kategorisi farklıdır, **elma ile armut toplanmaz**"* | **1-U** (meclis yasağı) |
| *"Hata payını elle tayin etmek kadar aptalca bir şey olamaz... **irtibat hiçbir zaman çöpe atılamaz**"* | **1-J** (eşik fonksiyondur) + **5** (sessiz ikame yok) |
| *"**Meşhûd token değildir**, varlığın sonsuz halleridir"* | **1-N** / **1-M** |
| *"Sen bu uzayın derinliğini sınırlayamazsın... dinamik olan katmanın **mertebe hududu yoktur**"* | **2-O** (pencere kısılmaz) |
| *"O 20 katman birer **hamiltonyendir**, senin merayı uygulayacağın yer **bizzat kübitlerin kendisi**"* | Yazmaç ile meleke ayrımı |
| *"**Nyström kuantum asgek kullanılacak, anlamaz mısın**"* | Karar 24(b) |

### ÇİFT MOTORLU NİHAÎ MİMARİ (tecrit.md'nin son sözü)

```
   AYRIK TOPOLOJİK MOTOR              SÜREKLİ ALAN MOTORU
   (kategori, mertebe, iskelet)       (ağırlık, faz, dalga)
   1 Postnikov k-invaryantları        1 Aktif Alt Uzay  d → r
   2 Tersine kuantum tavlama   ─ D* ─►2 Nyström Kuantum AS-GEK
   3 Kalıcı homoloji barkodları       3 Sanal zamanlı dalga
        ▲                                      │
        └──── tıkanıklık H^n ≠ 0 ──────────────┘
```

* **AYRIK MOTOR, KARARNÂME İLE DE UYUMLUDUR** (İkmâl Fıkrası IV
  Postnikov'u aynen tescil ediyor). O hâlde **ihtilafsızdır ve
  kurulur**.
* Sürekli motorun üç kalemi kararnâme ile ilga edilmişti; Karar 24
  bunu çözdü (Nyström hata beyanı şartıyla kalır).
* **AYRIK/SÜREKLİ AYRIMININ SEBEBİ:** *"Ayrık bir kategori indisinin
  (13 → 1000) **gradyanı alınamaz**."* Bu, ferman 1-V'nin ("hata
  vektördür, türev almıyoruz") zabıttaki temelidir: bazı kefelerin
  türevi **yoktur**, o hâlde tek skalere inen bir kayıp zaten
  imkânsızdır.
* **Kalıcı homoloji barkodu** ayrık Betti sayısını sürekli kılar:
  `ℒ_topo = W_p(Barkod(mevcut), Barkod(hedef))` -- Wasserstein
  metriği parçalı diferansiyellenebilirdir. Depoda `ogrenme/morse.py`
  Betti/Euler'i **tamsayı** olarak ölçüyor; barkod yok.

### ZABITIN İÇİNDE İPTAL OLAN İKİ ŞEY (sonraki hükümle)

1. **MERA.** tecrit.md *"kübitlerin kendisi MERA olur"* diyordu;
   Zabıt 1 (1 Eylül 2026) **MERA'yı hacim kanunu iflası sebebiyle
   ilga etti** ve yerine Reel Chebyshev-KAN/QTT koydu. Ferman 7 de
   MERA/MPS/bond truncation'ı iptal listesinde sayıyor. **Üçü aynı
   yöne bakıyor: MERA ölüdür.**
2. **POVM / zayıf ölçüm.** tecrit.md'nin son şemasında POVM ile
   yumuşak okuma vardı; Zabıt 1 onu *"varyans üretir"* diye ilga
   etti, ferman 1-T ise *"klonlarsın durumu"* diye çöpe attı.
   **Üçü mutabık: POVM ölüdür, klon asıldır.**

### DEPODA OLMAYAN ÜÇ BÜYÜK YAPI

1. **20 UZAY / FIRLATIM-GERİ ÇEVRİM.**
   `|Ψ_Nihai⟩ = Σ_m F_m† (Π_koho Π_betti 𝒮_m e^{−iηH_m}) F_m |Ψ⟩`
   -- 10 sabit (k=0..9) + 10 dinamik (d_i, hudutsuz) uzay, her
   birinin **kendine mahsus** Hamiltonyeni ve **kendine mahsus**
   dörtlü zırhı. Depoda tek bir yazmaç ve tek bir zırh var; uzaya
   mahsus ayrım **yok**.
2. **ÖZERK DÖNGÜ** (*Nefsi Müdrike Özerk Hedef ve Strateji*):
   `Tenakuz → Gaye(G_t) → Mutasarrıfa(R_t) → Teemmül(M_t)`.
   *"Girdi X=∅ olduğunda durum tensörü sıfırlanmaz."* Depoda tâlim
   bir yığın döngüsüdür; uyaransız iç dinamik **yok**.
3. **KALICI HOMOLOJİ BARKODU** -- ayrık topolojiyi sürekli kılan
   tek köprü; **yok**.

---

## TARAMANIN HÂLİ -- ▓ TAMAMLANDI ▓

**On sekiz zabıtın tamamı baştan sona okundu.** Emir icra edilmiştir:
*"Zabıtları tekrar tamamen tara, daha fazlasını bulacaksın,
bulduklarını mutlaka not et!"*

```
KUME_9_TEK_HAKIMIYET                 KUME_8_NAZIRLIK_PLANI
KUME_3_7_TERKIP_EMIRLERI             tecrit.md            (1451 s.)
terkip_layihas__12.md  (KARARNÂME)   zab_t_2.md           (teknik ek dâhil)
Zab_t_1.md             (İLGA CERİDESİ)  optimizasyon.md
C_oklu_Sonsuz_Kategorili_Koherent_Durum
Kelime_ve_Durum_Kodlamasinin_Tensorel_ve_Kuantum_Mahiyeti
Qudite_Tip_Tensorunun_Kodlanma_Nizami
Qudite_Tip_Tensoru_Zincirinin_Kodlanmasi
Quditte_Negatif_Olabilirlik_Yanilgisi_ve_Tabakali_Mizan
Kuantum_Metinlerindeki_Cevherin_Qudite_Tahvili
Ontolojik_Silsile_ve_Token_Tipinin_Hakikati
Su_kut_ve_Ifsa_Matematigi            zab_t_9.md (envanter)
Daginik_Kod_Modullerini_Ana_Icra_Akisina_Baglama_Nizamnamesi
Nefsi_Mudrike_Ozerk_Hedef_ve_Strateji_Tesekkulu
Nefsi_Mudrike_Ana_Dongu_ve_Kulli_Paradigma_Sorgu_Nizamnamesi
Nefsi_Mudrike_Ana_Dongu_ve_Paradigma_Denetim_Nizamnamesi
```

### ZABITLARIN TARİH SIRASI -- HANGİSİ HANGİSİNİ İLGA EDİYOR

    tecrit.md          mimarinin DOĞUŞU: 20 uzay, MERA, çok uzaylı
                       kübit, çift motor, POVM, AS-GEK
          │
          ▼  1 Eylül 2026
    Zab_t_1.md         İLGA CERİDESİ: MERA · pasif WKB · POVM/Born ·
                       Active Subspaces · sanal zamanlı PDE · tersine
                       tavlama (İsing) · sonlu fark -- YEDİSİ DE İLGA
          │
          ▼  1 Eylül 2026
    terkip_layihas_12  NİHÂÎ KARARNÂME: Zabıt 1 (idrak) + Zabıt 2
                       (hesap) tevhid; 16 bâtıl usul + 7 zaaf ilga;
                       9 uzuvlu tâlim teşkilâtı; 4 İkmâl Fıkrası

**KAİDE:** Bir mesele iki zabıtta ayrı hükümlüyse **sonraki tarihli
olan asıldır**. Karar 24 bu kaidenin ilk tatbikidir.

### ÜÇ HÜKÜMDE ÜÇ ZABIT DA MUTABIK (ihtilafsız, derhal icra)

1. **POVM / zayıf ölçüm ÖLÜDÜR.** Zabıt 1 ilga etti, kararnâme
   tekrarladı, ferman 1-T *"klonlarsın durumu"* dedi.
2. **MERA / MPS budaması ÖLÜDÜR.** Hacim kanunu iflası; yerine
   Reel Chebyshev-KAN + QTT. Ferman 7 ile birebir.
3. **Rastlantısallık ÖLÜDÜR.** *"Başarısızlığın matematikten mi zar
   atışından mı geldiğini gizler."* Ferman 5'in (ölçü kırmızı
   yanabilmeli) zabıttaki temeli budur.

### KARARNÂMENİN DEPODA KARŞILIĞI OLAN VE OLMAYAN UZUVLARI

| Kararnâmenin uzvu | Depodaki hâli |
| :-- | :-- |
| Morse-Euler katî eşitliği | **CANLI, `assert` ile** ✓ |
| Grassmann `arctan` log haritası | **CANLI** (`ogrenme/grassmann.py`) ✓ |
| Cholesky emniyet kilidi (`ogrenme/rkhs.py`) | **dosya VAR ve canlı** (yukarıdaki tashihe bakınız) |
| STA `H_CD` sürüşü (`ogrenme/sta.py`) | dosya yok |
| FCT kapalı form (`ogrenme/fct.py`) | dosya yok |
| Çift sayılar autodiff (`nefs/ikiz.py`) | dosya yok |
| OGDA (`nefs/ogda.py`) | dosya yok |
| QSVT Gibbs (`kuantum/qsvt.py`) | dosya yok |
| Alexandroff + Lions HAD | yok |
| Postnikov k-invaryantı | yok |
| Kalıcı homoloji barkodu | yok |
| QROM blok-kodlama | yok |
| FPAA faz dizisi | yok |
| 20 uzay fırlatım-geri çevrim | yok |
| Özerk döngü (Gaye → Mutasarrıfa) | yok |
