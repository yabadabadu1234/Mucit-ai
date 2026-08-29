# KÜTÜK — verilen hükümlerin birikimli kaydı

Bu dosya bir tasarım belgesi değildir; **hüküm kütüğüdür**. Konuşma boyunca
verilen hükümler burada sıra sıra durur. Yeni bir hüküm eskisini silmez;
eskisi ancak açıkça *nakzedilirse* düşer ve nakzi de buraya yazılır.

Sebebi şudur: hükümleri yalnız en sonuncusunu tutup öncekileri atarak
işlemek, hâkimin karşısındaki aptalın hâlidir. Kütük bunun önündeki settir.

---

## H1 — Ana icra hattı `nefs/akis.py`'dir

`idrak/` bir **ARC denemesidir**, ana döngü değildir. Bir modülün "bağlı"
sayılması için `nefs/akis.py`'deki `AKIS` sırasında koşan bir melekenin
uzvu olması gerekir. Ölçüt: `𝒪ₙ`'in **gerçek bir uzvu** mu var, yoksa
yerine bir **vekil skaler** mi konmuş.

## H2 — 41 meleke asıl modeldir

`nefs/`'teki 41 meleke yardımcı değil, modelin kendisidir.

## H3 — Ana döngüde gradyan ve kayıp yoktur

Öğrenme:

* ağırlık = parametrize lifleşmenin kesiti, `w ∈ ℳ` (`kesit_tipi`, `agirlikta_lif`),
* doğrusalsızlık = kip/kesme/yerelleştirme funktoru,
* uydurma = RKHS kapalı formu / KAN sembolik kapanışı / FNO spektrali,
* uç değer = `RCrit(f)` + tıkızlaştırma (Alexandroff, zorlayıcılık, barriyer),
* akış = hacim akışı (MCF / Fokker–Planck / Liouville), tek boyutlu gradyan oku değil.

NFL ve tıkızlaştırılamayan fonksiyonlar **gizlenmez**, ölçülür ve raporlanır.

## H4 — Uzvun cinsi melekenin tabiatından çıkar

Sayısal meleke sayısal uzuv alır; **hüküm veren meleke sembolik kalır** —
ispat, hüküm, kaide üretir; float üretmez. "Hepsi torch olsun" hükmü
mülgadır (o cevap, benim bozuk çerçevem içinde alınmıştı).

## H5 — ARC zaten metindir

Tek dil yolu. Model neyi verirsen onu konuşur. "İki başlı ARC + metin"
planı mülgadır. Beyan melekeleri (`𝒪₃₇–𝒪₄₁`) ARC üzerinde de tanımlıdır.

## H6 — ARC'ye has tek yenilik: **şahitlik**

Bir bulmacanın her gösterim çifti bir **şahittir**. "Hepsi aynı kurala
tâbidir" bilgisi modele **bayrakla bildirilmez**; organlarla sezilir ve
sınanır:

```
şahit bölütlemesi → şahit başına kaide (𝒪₁₈ Kıyas)
   → nakz: tek karşı örnek küllî kaideyi düşürür (𝒪₂₃ Mantık)
   → tevafuk + fazla sayma: müteber şahit sayısı (𝒪₂₉ Teyit)
   → küllî kaide + taklit ayırımı (𝒪₃₀ Tahkik)
   → istikrâ (ardışıklık kaidesi) → makam (𝒪₃₂)
   → makam Şek ise **sükût** (𝒪₃₇–𝒪₄₁)
```

## H7 — Nizamnamenin beş kademesi

1. envanter ve arayüz akdi (`nefs/akit.py`)
2. bağımlılık DAG'ı (`sira_gecerli_mi`)
3. merkezî durum veri yolu + kayıpsız intibak (`Durum`)
4. ana orkestra hattı (`AKIS`, melekelerin `yazar` akitleri)
5. icra izi + hassasiyet + hata izolasyonu (`nefs/tesir.py`)

## H8 — İlerleme ölçüsü

Düşürüldüğünde neticeyi hiç değiştirmeyen meleke sayısı.

Ölçü **bileşiktir** ve öyle olmak zorundadır: yalnız `‖ΔN‖` bakmak,
hüküm üreten melekeleri (nakz, makam, mühür) görmez — çünkü onlar sayı
değil hüküm üretir (H4). `nefs/tesir.py` şunların herhangi birine bakar:

```
‖ΔN‖ ∨ makam değişti ∨ sükût değişti ∨ nakz değişti ∨ mühür değişti ∨ ΔP
```

Ölçülen (`python -m nefs.tesir`, yapılandırılmış şahitli girdi):

| ölçüm | tesirsiz |
|---|---|
| başlangıç (yalnız `‖ΔN‖`, rastgele girdi) | **27 / 40** |
| şimdi (bileşik ölçü, kurallı girdi) | **20 / 41** |

Bunun 8'i **yapısal zaruret**tir (düşürülünce akış kırılır), 13'ü
tesirlidir. Ayrıca `nefs/akit.py`: veri yoluna hiçbir şey yazmayan
meleke sayısı **20 → 10**, vekil kalan **3** (𝒪₁₆, 𝒪₁₉, 𝒪₂₀).

**Rastgele gürültüde ölçüm yanıltır ve öyle raporlanır.** O girdide
model doğru olarak **susar** (makam Şek → sükût), `N` zaten sıfırdır ve
`‖ΔN‖` hiçbir melekeyi ayırt edemez. `tesir.py` asıl ölçümü kurallı
girdide yapar, rastgeleyi bu kayıtla ikinci sırada verir.

## H9 — Mevcut modüller silinmez

Bağlanır. Uzuv olarak takılır. torch'a taşıma yalnız `idrak` uzvu için
düşünülebilir, hüküm veren uzuvlar için asla.

## H10 — Sükût hakkı

`makam == "Şek"` iken model **susar**. Ölçü üçlüdür: cevap verilen /
susulan / cevap verince isabet.

## H11 — "~14.500 satır bağlanamaz" hükmü **nakzedilmiştir**

`omega_kategori*`, `hesap`, `kuantum`, `arama`, `yaklasim`, `olcek`
merkezî uzuvlardır; ölü ağırlık değildir.

## H12 — Öngörülen dalgalar (mucit usulü)

* hız → QSVT (`kuantum/qsvt.py`), Grover–Dürr–Høyer (`arama/grover.py`)
* hafıza → Nyström (`ogrenme/rkhs.py`), FNO `k_kesme`, MPS (`hesap/saklama.py`)

Bunlar sonradan yapıştırılacak eklenti değil, gradyanın kaldırılmasının
tabiî dalgalarıdır.

## H13 — Mucit usulü

Bir aksamı değiştir → dalgayı gör → sonraki aksamı düzelt → alet kökten
yenilenene kadar devam. Devamını her defasında sormadan getirmek benim
vazifemdir.

---

## İcra kuyruğu (kütükten çıkan)

| # | iş | yer | hâl |
|---|---|---|---|
| 1 | kütük | `docs/KUTUK.md` | tamam |
| 2 | envanter ve akit | `nefs/akit.py` | tamam |
| 3 | veri yoluna şahit ve sembolik alanlar | `nefs/uzaylar.py` | tamam |
| 4 | şahit uzvu | `nefs/sahit.py` | tamam |
| 5 | vekil skalerlerin yerine uzuv | `nefs/{idrak,akil,murakabe,beyan}.py` | tamam |
| 6 | sükût | `nefs/beyan.py` | tamam |
| 7 | tesir/hassasiyet ölçümü | `nefs/tesir.py` | tamam |

## Kapatılan somut kopukluklar (ölçümle)

| kopukluk | nasıl bulundu | ne yapıldı |
|---|---|---|
| `S_kebîr` bir kere yazılıp hiç güncellenmiyor; 𝒪₇–𝒪₃₂ arasındaki bütün iş kelama ulaşmıyor | 𝒪₂₁, 𝒪₂₈, 𝒪₃₆ düşürülünce `‖ΔN‖ = 0` | 𝒪₃₃ Muhakeme meclisi mevcut `S`ten toplanıyor |
| kaide `S` üzerinde uyduruluyor, 𝒪₁'in öz-dikkati satırları karıştırdığı için hiçbir kaide tutmuyor | kurala tâbi olduğu **bilinen** 4 şahitte nakz 2 şahidi düşürüyordu | kıyas ham duyu (`E`) üzerinde yapılıyor |
| şahit bölütlemesi `Z_hayal` üzerinde; odak penceresi örnek sınırlarını siliyor | kurallı ve bozuk akış aynı bölütlemeyi veriyordu | bölütleme ham `E` üzerinde |
| nakz tek turlu; bir bozuk şahit hepsini suçlu gösteriyor | 4 şahitten 1'i bozukken nakz = [0,1,2,3] | nakz kademeli: en ağır karşı örnek ayrılır, kaide yeniden kurulur |
| çelişki eşiği `δ = 0.5` sabit, `‖S‖²` ile ölçeklenmiyor | girdi iki katına çıkınca "iki kat çelişkili" | `δ = ½·ortalama(−C_ii)` |
| "karar geçmedi" hükmünün hiçbir neticesi yok; program yine uygulanıyor | `muhakeme.karar_geçti = 0` iken `S_kebîr` yine değişiyordu | karar geçmezse meclis dağılır |
| tevafuk, fazla sayma, istikrâ, nakz, yakîn zinciri ana akışta **hiç çağrılmıyor** | sıfır ithal | 𝒪₂₃, 𝒪₂₉, 𝒪₃₂, 𝒪₄₁'e uzuv olarak bağlandı |

---

# İKİNCİ CERİDE — 2026-08-27 celsesi

*İçtihad içtihadı nakzetmez: aşağıdaki hükümler yukarıdakileri kaldırmaz,
onların üzerine biner. Bir hüküm ancak açıkça nakzedilirse düşer.*

## H14 — Nizamnamenin beş kademesi mecburidir (yeniden zabıt)

Envanter/akit → bağımlılık DAG'ı → merkezî veri yolu + kayıpsız intibak →
ana orkestra hattı (pass-through/residual) → icra izi + hassasiyet + hata
izolasyonu. **Kayıpsız intibak**: veri kaybına yol açan kaba sıfırlama ve
tip zorlaması yasaktır.

## H15 — Özerklik: uyaransızlıkta da durum evrilir

`X_t = ∅` iken `dS/dt ≠ 0`. İç tenakuz serbest enerjisi `F_tenakuz`
gayeyi (`G_t`) doğurur; Mutasarrıfa (`R_t`) melekeleri harmanlayıp
strateji operatörü kurar; Teemmül (`M_t`) yürür. Model prompt bekleyen
bir yankı odası değil, kendi yolunu çizen öznedir.

## H16 — Sükût/ifşa **verisiz** karar kaidesidir (H10'un tahkimi)

Üç faz ve üç analitik eşik:

| şart | faz |
|---|---|
| `F_tenakuz ≤ ε_durgun` | **Sükût** — hiç token yok |
| `T ≥ 1−δ` ve `‖S−G‖ < η` | **İfşa-1** — neticeyi söyle |
| `‖dF/dt‖ < ξ` ve `F > ε_durgun` | **İfşa-2** — soru sor |
| aksi | **Teemmül** — içeride düşün |

Sonsuz gevezelik cebren kilitlenir:
`α_kelam(t+1) = α_kelam(t)·exp(−γ[λH(N) − I(N;G)]) → 0`.
`ε_durgun` elle konmaz; topolojik gürültü tabanından türetilir.

## H17 — Hata payı elle tayin edilmez, irtibat çöpe atılmaz

`F_irtibat < 1−ε` diye müşahedeyi atmak fıtrata zıttır. Kanalın
kirliliği değil **taşıdığı bilginin keyfiyeti** mühimdir: karşılıklı
bilgi `I > 0` olduğu müddetçe kanaldan mana akar; önsel intizar
(`ρ_prior`) zayıf silüeti tamamlar; Fisher enformasyonu `F_Q > 0` ise
irtibat asla feshedilmez, kıymeti nispetinde tartılır.

## H18 — Meşhûd token değildir

Meşhûd; ışık akışı, ritim, ilham, hatıra — varlığın her tezahürüdür.
Token, bu sonsuz meşhûdun en dar arazlarından biridir.

## H19 — Matrise çevirmek kuantum yapmaz

Klasik formüldeki skaleri matrisle değiştirmek "kuantum avantajı"
vermez. Hakiki kuantum üç şarttır: (1) genlik kodlaması, (2) üniter
evrim/faz oracle, (3) **yıkıcı girişim**. Bunlar yoksa kuantum
denmez — ve bu proje bunu iddia etmez, ölçer.

## H20 — Grover tipi tekil arama dilde çöker

`f(x) ∈ {0,1}` tek doğru diziliş varsayar; her yeni cümlede evvelki
faz ayarı anlamsızlaşır, öğrenme iptal olur. Yerine **öğrenilebilir
enerji yüzeyi** `H_θ|x⟩ = E_θ(x)|x⟩` konur: aynı manayı veren bütün
dizilişler aynı faz havuzunda buluşur.

## H21 — Mertebeler toplanmaz

`αH₀ + βH₁ + γH₂` **batıldır**; nokta ile ok toplanmaz. Mertebeler ayrı
liflerde yaşar ve dalgayı **ayrı eksenlerde** çevirir:
`U_küllî = U₀ ⊗ U₁ ⊗ … ⊗ U₉ ⊗ U_{d₁} ⊗ … ⊗ U_{d₁₀}`.
Mertebeler arası geçiş toplama ile değil **Sol Kan Uzantısı** ile olur.

## H22 — 10 sabit + 10 dinamik uzay

Sabit blok `k ∈ {0,…,9}` — ardışık ve değişmez zemin.
Dinamik blok **ardışık değildir**; sonsuz spektrumdan seçilmiş keyfî on
mertebedir, meselâ `[13, 17, 20, 30, 55, 1000, 58383, 19, 1009, 60000]`.
Aradaki mertebeler için bellek açılmaz — **seyrek Kan sıçraması**.

## H23 — Sheaf/homotopi/Betti/kohomoloji katman değildir

Bunlar mertebe numarası değil, 20 lifi **enine kesen zırhtır**; her uzayda
o uzaya mahsus işletilir. Katman listesine karıştırılmaları hatadır.

## H24 — MERA katman değil, kübitlerin bizzat kendisidir

Kübitler kopyalanmaz (no-cloning). Tek bir dalga havuzu vardır. MERA,
o kübitlerin kendi hâlidir; dolanıklık ve süperpozisyonu o üretir.
20 mertebe ise dalganın üzerinden geçtiği Hamiltonyen uzaylarıdır.
Akış: **MERA → 20 uzaya fırlat → her uzayda H_m + zırh → esas uzaya
geri mühürle**.

## H25 — Kübitler tek uzaydan değildir

Yapraklar tekdüze `ℂ²` değil; sonsuz kategoriden türeyen ayrı ontolojik
liflerde (`ℋ_α`) doğar. Dolanıklık çözücüler funktöryel köprülerdir.

## H26 — Tensör treni yerine ağaç/MERA

MPS 1 boyutludur; 1. kelime ile 1.000.000. kelime arası bağ bütün
vagonlardan geçmek zorundadır. Ağaç/MERA'da mesafe `O(log N)`e iner,
`D` şişmez. Bellek `O(N·D²)` — lineer.

## H27 — Çoklu GPU'da "toplayıcı GPU 0" mimarisi yasaktır

`DataParallel` sahtekârlığı ve gizli tensör kopyaları GPU 0'ı şişirip
OOM fırlatır. Nizam: her GPU ayrı **süreç**, `set_device(rank)`,
`gather` YOK, sınır aktarımı **P2P** ve yalnız `[D,D]` (≈2 KB).

## H28 — Eğitim: çift motor

* **Sürekli motor**: Active Subspaces (`C = 1/N Σ g gᵀ`, `d→r`) →
  Nyström kuantum AS-GEK vekil yüzeyi (hedef bilgisi sızdırılmış:
  `V_toplam = V_GEK + λ‖𝒢(u) − y_hedef‖²`) → **sanal zamanlı dalga
  yayılımı** (`∂ψ/∂τ = ∇²ψ − V ψ`) ile küresel minimuma spektral çöküş.
* **Ayrık motor**: Postnikov k-invaryantı (`k^{n+1} ∈ H^{n+1}(X;π_n)`)
  dinamik mertebenin adresini **analitik** verir; tersine tavlama ayrık
  `D*` vektörünü seçer; kalıcı homoloji barkodları (Wasserstein) Betti'yi
  diferansiyellenebilir kılar.
* GE-RKHS **kullanılmayacaktır**; vekil model **AS-GEK**tir.
* Yaylı boncuk (SQA) değil **bizzat dalga**: spektral süzme + girişim.

## H29 — Tünelleme melekelere kilitlenir

Başıboş tünelleme hezeyandır. Vana: Tenakuz + Şek tıkanmayı teşhis eder →
Merak `Γ`yı yükseltir → Hads sıçrar → Tahkik ve İspat mühürler.

## H30 — BEC boca edilmez, tepeye konur

Her yere BEC uygulamak süperpozisyonu öldürür, sistem felç olur. BEC
yalnız **nihai tasdik makamında** faz kilidi olarak işler
(Gross–Pitaevskii); netice süper-akışkan, sarsılmaz hüküm.

## H31 — Ölçüm sert değildir

Von Neumann çöküşü bağlamı siler. Usul: kök tensörde kısmî iz →
`ρ_kök` → POVM zayıf ölçüm → `P(x) = Tr(E_x ρ_kök)` **dağılımı**
belleğe yazılır; dalga diri kalır.

## H32 — Tecrit mimarisi AYRI bir modeldir

Bu mimari (`main/`) ana modelle (`nefs/`) karıştırılmaz. Bağımsız
kurulur, eğitim verisiyle sınanır, iddiaları (kaç token aynı anda,
değerlendirmede kaç soru) **ölçülür**.

## H33 — Bağlanmadık `𝒪_x` bırakılmaz

41 melekenin tamamı ana icra akışında fiilen tesirli olacaktır.

---

## H34 — Kule: uzun pencereyi **ana modelin kendisi** tutar

`main/`'in icadı ana modele nakledildi. Nakledilen şey kübit, dalga veya
faz değil; **hiyerarşik taşıyıcıdır** (`nefs/kule.py`).

Ana modelin karesel olduğu **on yer** ölçümle bulundu ve kule üzerinden
geçirildi: 𝒪₁ öz-dikkat, 𝒪₄ permütasyon dizeyi, 𝒪₅ komşuluk çizgesi,
𝒪₇ bağlam dikkati, 𝒪₈ HSIC Gram dizeyleri, 𝒪₉ kosinüs dizeyi,
𝒪₁₀ tezat dizeyi + özayrışım, 𝒪₁₁/𝒪₂₁/𝒪₂₈/𝒪₃₆ çelişki dizeyi,
𝒪₂₂ nedensellik çizgesi, 𝒪₂₅ 200 turluk dikkat, 𝒪₃₅ siyak-sibak dikkati.

Ölçülen (tek çekirdek, `d_in=12`):

| satır | evvel | şimdi |
|---|---|---|
| 1.024 | 12,52 sn | **0,38 sn** (33×) |
| 4.096 | ölçülemedi | **0,96 sn** |
| 16.384 | çöktü (32 GiB) | **10,6 sn** |

**Kalan.** Hâlâ tam doğrusal değil (4× satır ≈ 11× zaman); en az bir
karesel yer daha var ve bulunmadı. Bu gizlenmiyor.

**Bedeli de gizlenmiyor.** Kaba taneleme ortalamadır; `kule.kayıp`
ölçülür (1.024 satırda 0,85). İnce eksen silinmez — kaba netice ona
**artık** olarak yayılır (nizamname Kademe 4). Şahit bölütlemesi ham `E`
üzerinde kalır, kuleden etkilenmez.

---

## H35 — Okuma usulü: `grep` yasaktır

Dosyalar **baştan sona** okunur. Parça avlamak (grep/diff/sed ile
kesit almak) okumak değildir; metnin hükmünü değil, aranan kelimenin
etrafını gösterir. Bu kütükteki bütün hükümler, tam okunmamış metinden
çıkarılan yarım hükümlerin bedeliyle yazıldı.

## H36 — 6 milyon kübit **ölçüldü**, iddia edilmedi

`main/yazmac.py`, tek çekirdek, `χ = 8`, `float32`:

| iş | ölçüm |
|---|---|
| yazmaç kurulumu (6.000.000 kübit) | 19,8 sn — durum **2,86 GB**, kübit başına **512 B** |
| Hadamard (süperpozisyon) | 15,0 sn — entropi **−0,000000** |
| MERA(2) (dolaşıklık) | 459,4 sn — **S = 1,5405**, Schmidt = 8 |
| norm hatası | **0,0e+00** |
| âzamî yerleşik bellek | **3,37 GB** |

Hüküm: süperpozisyon dolaşıklık değildir; Hadamard sonrası 2^6000000
taban durumunun hepsi eşit genliktedir ama entropi sıfırdır. Dolaşıklığı
**MERA üretir** (H24) ve entropi ancak orada sıfırdan kalkar.

## H37 — Bellek şişmesi durumda değil, **geçici dizilerdedir**

Ölçülen: 1.000.000 kübitte durum 0,48 GB iken zirve RSS 4,42 GB;
6.000.000'da durum 2,86 GB iken tam dizi üzerinde `einsum` zirveyi
8,62 GB'a çıkarıp süreci öldürdü. Çare `χ`yi kısmak değil, kapıları
**öbekleyip yerinde** uygulamaktır (`Yazmac.obek`, `out=` ile). Düzeltme
sonrası 6.000.000 kübitte zirve 3,37 GB — durumun yalnız 1,18 katı.

## H38 — `omega_kategori_nbe` çağrılmayan modül olmaktan çıktı

20 uzayın her biri `turetimler.morfizm_tipi(A, n)` ile **kurulur** ve
`denetleyici.denetle_t` ile **makine denetiminden geçer**; tıkanıklık
`iliskiler.tikanma_postulati`, kesit ağırlığı `iliskiler.kesit_tipi` +
`evrensel_demet` ile alınır. Ölçülen: 20/20 uzay tip denetiminden geçti,
14'ü tam mertebede kuruldu (0–9, 13, 17, 19, 20); daha yüksek mertebeler
`kutuphane.dongu_uzayi_n` temsilcisiyle tutulur — ve bu **gizlenmez**,
`Uzay.tam_kuruldu` alanında yazar.

## H39 — Hamiltonyen parametreleri **yuvaya** bağlanır, mertebeye değil

Ayrık motor bir mertebeyi sıçrattığında sıçrayan şey lifin **adresidir**,
lifin kendisi değil. Parametreler mertebe değerine anahtarlanırsa
(`F.50` gibi) motor kendi öğrendiğini siler. Anahtar `0…19` yuvasıdır.

## H40 — Ana model H32 mimarisinin **tamamını** kullanır

*"Bir şeyi nakzetmene gerek yok; ana model tamamen H32'yi kullanmaya
başlayacak, bir eksik dahi olmadan."*

H32 (tecrit mimarisi ayrı bir modeldir) **nakzedilmemiştir**: `main/`
müstakil model olarak durur. Nakledilen şey mimarinin kendisidir ve
tamamıdır: kübit yazmacı, MERA, 20 ∞-kategori uzayı, Hamiltonyen, enine
zırh, tünelleme, BEC, POVM, AS-GEK, hedef güdümü, Postnikov, tersine
tavlama. İki model aynı fiziği **tek nüshadan** çağırır (`main.yazmac`,
`main.optimize`); tekrar yoktur.

**`S` diye ayrı bir reel hâl yoktur** (kullanıcı hükmü). Nefsin bir
andaki bütün hâli tek bir kuantum durumudur.

**41 melekenin hepsi üniterdir** ve hiçbiri okumaz (kullanıcı hükmü:
"hiç reel görüş alınmasın"). Hüküm de üniterdir: makam iki kübite
(`00=Şek, 01=Zan, 10=Yakîn, 11=Vehim`) kodlanır, kontrollü dönmelerle
çevrilir. Hükmün sayısı ancak en sonda, POVM zayıf ölçümüyle doğar --
ve bir sayı değil **dağılımdır**.

Zincir düzeni: her satırın veri kübitlerinin dibinde kendi yerel hüküm
kübiti; zincirin sonunda küllî hüküm bloğu (makam 2, mîzân 4, tenakuz 2,
tasdik 2, sükût 1, nakz 2, kelam 4).

`nefs/akis.py` (reel akış) **yerinde durur** ve 41 sınaması geçmeye
devam eder; kübit akışı yanına kuruldu, karşılaştırılabilsin diye.

## H41 — Takas ağı kapalı yoldur; **operatör yürür, kübit oynamaz**

Uzak iki kübite kapı vurmak için onları yan yana getirmek (takas ağı),
geçilen her kesitte hakiki dolaşıklığı **sürükler**. Ölçüldü ve `χ` ile
kapanmadı:

| χ | takas ağı, kapı başına kesme | dolaşıklık S |
|---|---|---|
| 8 | 4,0e-02 | 1,93 → 1,44 |
| 32 | 7,4e-02 | 2,50 → 1,87 |
| 128 | 4,4e-02 | 2,61 → 2,34 |

Sebep `χ`nin darlığı değil, MPS'in bir boyutlu oluşudur (H26).

Çare veriyi taşımak yerine **operatörü yürütmektir**: Matris Çarpım
Operatörü (`Yazmac.mpo_uygula`) bütün zincire aynı anda etki eder,
hiçbir kübit yer değiştirmez. Aynı işte ölçülen:

| χ | MPO kesmesi | dolaşıklık S | süre |
|---|---|---|---|
| 8 | 1,1e-01 | 1,93 → **2,08** | 0,03 sn |
| 64 | **2,7e-03** | 2,61 → **4,09** | 0,99 sn |

χ=64'te kesme **7600 kat** azdır, süre yarıdır ve dolaşıklık artar
(takas ağı ise yok ediyordu).

**Doğruluğu ispatlandı**, iddia edilmedi: kayıpsız şartlarda (χ=512,
kesme 1e-30) MPO ile takas ağı arasındaki fark 5,8e-08 ile 4,3e-07
arası, MPO'nun normu tam **1,000000**.

**MPO bağı yalnız 2'dir** ve sebebi cebridir: `R(Σφ) = Π R(φ)`, yani
zincirde taşınması gereken şey sayaç değil (o `N+1` bağ isterdi), iki
boyutlu dönme cebrinin elemanıdır.

## H42 — Yazmacın üniterliğini bozan ölçek kusuru

`_cift_kapi_dilim`, iki-yuva güncellemesinde tekil değerleri "norm koru"
niyetiyle birim yapıyordu (`sk /= ‖sk‖`). MPS kanonik biçimde değilken
`‖sk‖` durumun normu değil, o bağdaki **ayar** büyüklüğüdür.

Ölçüldü (χ=128, kesme 0, float64, genlikler üzerinden): tek TAKAS
git-gel `‖Δgenlik‖/‖genlik‖ = 2,52e-01`; en iyi ölçek çıkarıldığında
kalan 6,5e-08 ve ölçek **0,748**. Yani hata saf bir büzülmeydi: yön
doğru, şiddet kayıp. Satır kalkınca aynı ölçüm **1,57e-15** verir.

Bütün okumalar normalize olduğu için (`ρ/iz`, `P/Σ`) gizlenmişti; fakat
yazmaç o hâliyle **üniter değildi** ve H19'un üç şartından biri budur.
Dolaşıklık ölçümleri değişmedi (4096 kübit MERA(6): S=1,979102).

## H43 — Kelam ayrı bir alandır; birikim açısı **durak sayısına bölünür**

İki ölçüm, iki hüküm:

1. 41 meleke koştuktan sonra bir satırın dört veri kübitinin ortak
   dağılımı **tam düzgün** çıkıyor (16 durumun her biri 0,0625). Bu bir
   kusur değil, dolaşıklığın tabiatıdır: her şey her şeyle dolaştığında
   küçük bloğun marjinali âzamî karışıktır. Model o kübitlerden
   **konuşamaz**. Onun için kelam, `|0⟩`da başlayan ve yalnız beyan
   melekelerinin (𝒪₃₇–𝒪₄₁) yazdığı ayrı bir alandır.

2. Birikim açıları doğrudan alınınca 20 duraktan geçen toplam dönme ~10
   radyana çıkıyor; çember sarılıyor ve hedef kübit tamamen faz
   siliniyor. Birikim açısı `θ_i / n` olmalıdır: bir şahidin küllî
   hükme katkısı sınırlı olsun ki yüz şahit çemberi tur atmasın. Böylece
   hüküm, delil çoğaldıkça **keskinleşir**, silinmez.

## H44 — Parametre girdinin uzunluğuna bağlanamaz

Açılar satır sayısı kadar isteniyordu; 4 satırla kurulan model 8 satır
görünce kırılıyordu. Daha kötüsü: parametre sayısı uzunluğa bağlı olsaydı
model uzunluklar arasında hiç genelleyemezdi -- öğrendiği şey "bu
uzunlukta ne yapılır" olurdu. Öğrenilen şey "kaçıncı satırda ne yapılır"
değil, "bir satırın kaçıncı kübitinde ne yapılır"dır (evrişimin ötelemeye
bağışıklığı ile aynı kaide). Fazla durak varsa açılar devrolur.

## H45 — Kübit ana modelinin eğitimi ölçüldü: **netice olumsuz**

55 kübit, 250 açı, 8 çevrim, 1.629 sn. `V_ilk = 3,5162 → V_son = 3,3218`;
potansiyel 2. çevrimden sonra hiç inmedi. Tünelleme 5 çevrimde açıldı
(Γ 0,3'e kadar), **sıçratamadı**.

Değerlendirme (6 hiç görülmemiş bulmaca):

| ölçü | eğitim öncesi | eğitim sonrası |
|---|---|---|
| tam çözülen | **0** | **0** |
| ilk belirteç isabeti | **0** | **0** |
| ortalama hücre isabeti | 0,0641 | **0,0429** |
| sükût | 140 | **0** |

**Eğitim değerlendirmeyi kötüleştirdi.** Gizlenmez. Üç sebep, üçü de
ölçümden çıkar:

1. Potansiyel düştü, isabet düştü — **ölçüt yanlış yeri ödüllendiriyor**.
   Mîzân cezası (tenakuz + nakz + tasdik + sükût) ARC teriminden ağır
   basmış olabilir: model doğru bilmeyi değil, kendini tutarlı
   hissetmeyi öğreniyor.
2. Sükût 140 → 0. Ceza formülünde `0,5·sükût` vardı; model susmamayı
   öğrendi, fakat **bilmeden konuşmayı** öğrendi. Bu H10'a (sükût hakkı)
   doğrudan zarardır ve ceza formülü bu yüzden yeniden yazılmalıdır.
3. 250 parametre / 8 çevrim / 6 örnek ARC için hiçbir şey. Kıyas:
   `main/` modeli 4.305 parametreyle 0,0347 aldı — o da çözemedi.

**Bir soru bile çözülmedi — iki modelde de.** İddia edilecek bir şey
yoktur. Ayakta duran ve ölçülen kısım şudur: 6 milyon kübit MERA,
MPO'nun takas ağına 7600 katlık üstünlüğü, 20 lifin makine denetimi,
üniterlik kusurunun bulunup düzeltilmesi. **Öğrenme kısmı ayakta
değildir.**

## H46 — Göz kuruldu, ölçüldü; **22 vasfın 19'u ARC'de zararlı çıktı**

Modelin gözü yoktu: ham duyu bir satır diliminin ortalaması alınıp
`tanh` ile açıya çevriliyordu. İki boyut, komşuluk, renk, sınır --
hiçbiri yoktu. **0/120 neticesinin sebebi kuantum makinesi değil,
modelin bulmacayı hiç görmemesidir.**

`nefs/mubser.py`: 22 mübser vasıf, çelişkisiz ve tekrarsız 15 kanala
indirildi (6 işaretli eksen + 7 asıl + 2 türev). Çıktı tek tensör
değil, tabakalı kayıttır.

**Ölçülenler (gerçek ARC ızgaraları):**

| ölçü | değer |
|---|---|
| 240 girdi-çıktı çifti | 4,3 sn (kübit modelinin **tek** geçişi 0,54 sn idi) |
| öteleme eş-değişkenliği | **0,00e+00** (tam) |
| ızgara şekli değişen çift | **%28** |
| görev içi / görev dışı imza ayrışması | **AUC 0,8686** |

**Kanal ablasyonu -- acı netice:**

| kanal kümesi | AUC |
|---|---|
| 22 kanalın hepsi | 0,8686 |
| **yalnız 3 kanal** (Δadet · hareket · Δbağlantı) | **0,8981** |
| altı kanal | 0,8856 |
| yalnız Δadet | 0,7232 |

**19 kanal net zararlıdır.** Bu bir normalizasyon artefaktı değildir
(sd tabanı konunca AUC 0,8661→0,8686, değişmedi). ARC'de görev kimliği
üç şeyde yaşıyor: kaç nesne var (**Adet**), ne kadarı değişti
(**Hareket**), neyin neye bitişik olduğu (**İttisal/Teferruk**).

**Ölçüm üç kusuru daha yakaladı ve üçü de düzeltildi:**
1. Tenasüb ızgara başına ölçülüyordu → `Δen_boy` cebren sıfırdı (ölü
   kanal). Nesne başına alındı: |ort| 0,4936.
2. Ziyâ için ARC renklerine uydurma bir parlaklık tablosu dayatılmıştı
   → 0/174 çiftte baskın. Ziyâ ARC'de **varlık/yokluk**tur; öyle
   yapıldı: 14/174.
3. Mukayese, `doku`+`bağlantı`dan türetildiği hâlde 86/174 çiftte
   baskın çıkıyordu -- **çift sayıyordu**. Teşabüh/İhtilaf'ın yeri
   nesneler arasıdır; oraya taşındı.

**Düzelmeyen:** Şeffafiyet kanalı ölü (sıfır oranı 0,99). Kavşak
vekili ARC'de neredeyse hiç ateşlemiyor.

**Yanlış ölçüt uyarısı.** Evvela "değişimin kanallara yoğunlaşması"
ölçülmüştü; yanlıştı. Bir nesneyi kaydırmak bağlantı, ışık, levn,
bu'd'u **hep birden** değiştirir. Kanallar *tasvir* olarak bağımsız
olmalıdır, *dönüşüm* altında değil.

**Aşırı iddia yasağı:** AUC 0,90 ARC'yi çözmek değildir. Görev kimliğini
ayırt etmek, çıktı ızgarasını üretmek demek değildir.

## H47 — Ölçüt İKİDİR ve ikisi de her raporda yan yana yazılır

Kullanıcı hükmü. Ara ölçüt **çıktı boyutu isabeti**, nihai ölçüt **tam
çözüm**. Ara ölçüt ilerlemeyi gösterir, nihai ölçüt hükmü verir. Ara
ölçüt yükselirken tam çözüm sıfır kalıyorsa **bu da bir hükümdür ve
gizlenmez**.

Sebebi: ajan bir mesajda ölçütünü neticeye göre değiştirdi
("yoğunlaşma" yanlış çıkınca "AUC" koydu ve yeni ölçüt onu memnun eden
bir sayı verdi). Ölçütü ölçen koyarsa kendini kandırır; ölçütü **mucit
koyar**.

## H48 — El yazması kaide dağarcığı yabancı görevde **sıfır** getirdi

`nefs/boyut.py`: 22 boyut kaidesi (aynı, devrik, dolu kutu, en büyük
nesne, ×k, ÷k, nesne sayısı, sabit boyut…). Kaide, eğitim çiftlerinin
**hepsini** sağlamazsa reddedilir (H6 nakz); hiçbiri sağlamazsa model
**susar** (H10).

Ölçülen:

| | ahmak taban (hep "aynı boyut") | kaide dağarcığı | kazanç |
|---|---|---|---|
| eğitim (400 görev) | %68,3 | **%89,5** | **+21,2** |
| **değerlendirme (120 görev)** | **%70,0** | **%70,0** | **+0,0** |

Konuşunca isabet %96,6; sükût 33; yanlış 3.

**Hüküm:** öğrenilmiş parametre yoktur, fakat **tasarım aşırı
uydurulmuştur**. Eğitim kümesine bakıp ona göre kaide yazmak, o kümeye
ezber yapmaktır; yabancı görevde ahmak tabana çöker. El yazması kaide
dağarcığı ARC için bir yol değildir -- kaide **yazılmaz, çıkarılır**.

Bu, kullanıcının koyduğu ölçüt sayesinde yakalandı. Ajan kendi ölçütünü
koysaydı %89,5'i rapor edip ilerleme sanacaktı.

## H49 — Şeklin hakiki tarifi yazıldı

Evvelce şekil diye bir şey yoktu: yalnız "maskeler birebir eşit mi" vardı
ve tek hücre farkı emsalliği düşürüyordu. `_sekil_tarifi` sekiz ölçü
verir, hepsi ötelemeden bağımsız: delik sayısı (Betti₁), çevre, tıkızlık
(`çevre²/alan`), doluluk, dihedral simetri mertebesi, ikinci merkezî
momentler (`m20/m02/m11`).

Bilinen şekillerde doğrulandı: dolu kare (delik 0, simetri 8), halka
(delik 1, simetri 8), iki delikli (delik 2, simetri 4), yatay çizgi
(m20=0, m02=0,4), dikey çizgi (m20=0,4, m02=0), L (simetri 2).

## H50 — Şeffafiyet kavşakta değil **süreklilikte** aranır

Kullanıcı hükmü. Kavşakta üçüncü renk araması kanalı öldürmüştü (sıfır
oranı 0,99). Doğru test: bir renkli dizi kesilip **aynı hizada** devam
ediyorsa orada örtme vardır -- kesen ön, kesilen arka katmandır.
Ayrıca şeffafiyet tek ızgarada değil **girdi-çıktı arasında** aranır:
girdide örtülü olan çıktıda ortaya çıkıyorsa örtme çözülmüştür.

## H51 — İhtimal uzayı kübitlerin **bizzat içidir**

Kullanıcı hükmü: *"İhtimal uzayı o ızgaranın olabileceği tüm
ihtimallerdir. 30×30=900, yani 10⁹⁰⁰ ihtimal var; 22 milyon kübitle
2^22milyon olur. İhtimal uzayı bizzat o kübitlerin içidir."*

Hesap doğrulandı (`nefs/ihtimal.py`):

| ızgara | hücre | ihtimal | asgarî kübit | fiilî kübit (4/hücre) | 22M ile |
|---|---|---|---|---|---|
| 3×3 | 9 | 10⁹ | 30 | 36 | 611.111 ızgara |
| 10×10 | 100 | 10¹⁰⁰ | 333 | 400 | 55.000 ızgara |
| **30×30** | 900 | **10⁹⁰⁰** | **2.990** | **3.600** | **6.111 ızgara** |

**Bu, el yazması kaide dağarcığının nakzıdır (H48).** Kaide yazılmaz,
aranmaz bile: bütün ızgaralar zaten süperpozisyondadır; melekelerin işi
kaideye uymayanları yıkıcı girişimle söndürmektir.

Ayrıca kullanıcı ikinci kez şunu hükmetti: **boyut kaidesi dağarcıkla
çözülmez.** Müşahede boyutu görür ve işi biter; o boyutun **neden** öyle
değiştiği aklın işidir. `nefs/boyut.py` bir mekanizma değil, yalnız bir
taban ölçümdür.

## H52 — MPS, iki boyutlu ihtimal uzayı için **YANLIŞ HENDESEDİR**

`nefs/ihtimal.py` kuruldu ve ölçüldü. Üç adım da çalışıyor:
AÇ (18 kübit, 4⁹ = 262.144 ızgara, entropi 0, Schmidt 1 -- süperpozisyon
bedava), SÖNDÜR (kısıt operatörleri üniter), OKU (POVM, çöküş yok).
Kilitleme dört rengin dördünde de doğru (uç sırası kusuru bulunup
düzeltildikten sonra).

**Fakat kısıt uygulandıkça ``χ`` üssel şişiyor:**

| ızgara | χ=16 | χ=64 | χ=256 |
|---|---|---|---|
| 3×3 | 3,41 | **2,75e-03** ✓ | — |
| 4×4 | 10,0 | 8,68 | **1,17e-01** (44 sn) |
| 5×5 | 19,3 | 19,8 | **20,7** ✗ (90 sn) |

**Kanun bulundu ve rakamlar birebir tutuyor:**

    χ_gerekli ≈ renk^w        (w = ızgara genişliği)

4 renkle: 4³=64 → 3×3 tuttu; 4⁴=256 → 4×4 zar zor; 4⁵=1024 > 256 →
5×5 çöktü. Üç ölçüm de tahmini doğruladı.

**ARC için: 30×30, 10 renk → χ ≈ 10³⁰. İMKÂNSIZ.**

Sebebi MPS'in alan kanunudur: tek boyutlu zincire serilen iki boyutlu
bir kısıt ağı, kesitten geçen **kenar uzunluğu** kadar dolaşıklık
taşır. `main/yazmac.py`'nin 6.000.000 kübitlik MPS temeli -- bütün
ölçülmüş başarılarına rağmen -- **ARC için yanlış hendesedir**. Metin
sıralı olduğu için MPS metinde doğrudur; ızgara iki boyutlu olduğu için
ızgarada değildir.

Bu, H26'nın (tensör treni yerine ağaç/MERA) ARC'ye tatbik edilmiş ve
**rakamla ispatlanmış** hâlidir.

## H53 — MERA ile PEPS **barıştırıldı**: ağaçta çevrim yoktur

Kullanıcı hükmü: *"MERA ile PEPS'i barıştırarak yapabiliyorsan yap,
yaklaşıklığı yok etmenin çaresini düşün."* ve *"MPS'i iki boyutlu ağacın
YAPRAKLARINDA kullan."*

Yaklaşıklık nereden geliyordu:

* **MPS**: büzülme tam, hendese yanlış (``χ ≈ renk^w``, H52).
* **PEPS**: hendese doğru, fakat ağda **çevrim** var → büzülme
  ``#P``-zor, ancak yaklaşık, hatası **kontrol edilemez**.
* **AĞAÇ (TTN)**: çevrim **yok** → büzülme MPS gibi **tam**; hendese
  iki boyutlu → ızgara kareye yakın bloklara bölünür.

**Barışma budur ve yaklaşıklığı öldüren şey çevrimsizliktir.**

Ölçülen (`nefs/agac.py`):

| sınama | netice |
|---|---|
| tam büzülme, 1×2 / 2×2 / 2×3 / 3×3 | durum boyutu tam ``d^(h·w)``, ``ΣP = 1,0000000000`` |

| ızgara | zincirde âzamî mesafe | ağaçta | kazanç |
|---|---|---|---|
| 3×3 | 8 | 7 | 1,1 kat |
| 5×5 | 24 | 11 | 2,2 kat |
| 10×10 | 99 | 16 | 6,2 kat |
| **30×30** | **899** | **20** | **45 kat** |

Bölme usulü: her adımda dikdörtgenin **uzun kenarı** kesilir; bloklar
kareye yakın kalır, blok sınırı (dolayısıyla gereken ``χ``) asgarîdir.

**İddia edilmeyen:** ağaç iki boyutlu alan kanununu KALDIRMAZ; hiçbir
tensör ağı kaldıramaz. Kaldırdığı şey PEPS'in büzülme yaklaşıklığı ve
MPS'in mesafe cezasıdır.

## H54 — Ajanın dikkate almadığı iki vesikadaki beş kusur (BORÇ)

Kullanıcı iki teşhis vesikası gönderdi, ajan bunları fiilen dikkate
almadı. Beşi de doğrudur ve dördü hâlâ ayaktadır; borç olarak zabıtlanır:

1. **1 boyutlu pencere** -- ARC iki boyutlu, `pencere=8` bir maskaraydı.
   → H52/H53 ile **kapatıldı** (ağaç kuruldu).
2. **8 örnekli AS-GEK istatistikî olarak imkânsız** -- 250 boyutlu
   uzayda vekil yüzey kurmak için asgarî ``10×d = 2.500`` değerlendirme
   gerekir; ajan 8 çevrim koştu ve 2. çevrimde sığ bir çukura saplandı.
   → **AÇIK BORÇ**.
3. **Ayrık motorun seçtiği yüksek mertebeler fiilen koşmuyor** --
   `D=[13,17,19,20]` dışındakiler (30, 55, 1000…) icra döngüsüne hiç
   girmiyor; Postnikov sıçraması kâğıt üzerinde kalıyor.
   → **AÇIK BORÇ**.
4. **BEC, POVM'yi ve sükûtu boğuyor** -- ``g|Ψ|²`` faz kilidi belirsizlik
   eşiğini sıfırladı; sükût 140 → 0, isabet %6,41 → %4,29.
   → **AÇIK BORÇ**.
5. **Python döngüsü hamallığı** -- 250 parametrenin 8 çevrimi 27 dakika;
   vektörize edilse saniyeler sürmeli.
   → **AÇIK BORÇ**.
