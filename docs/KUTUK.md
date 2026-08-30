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

---

# ÜÇÜNCÜ CERİDE — melekelerin mimariye tek tek bağlanması

*Kullanıcı hükmü: "Kurduğum kuantum mimarisiyle melekeleri zaten hiç
barıştırmadık; senin bana teker teker hangi melekenin ne formülü
olacağını, mimariye nasıl entegre edileceğini tek tek sorman lazım."*
Bu ceride o suallerin ve hükümlerin yeridir. Her meleke ayrı zabıttır.

## H55 — 𝒪₁ Müşahede **iki kademelidir**

* **Hissî müşahede (1. mertebe): KLASİK.** Hücre, renk, bitişiklik,
  sınır. Göz bir ölçüm aletidir (CPTP kanalı); süperpozisyona girmez,
  hüküm vermez, kanal üretir. `nefs/mubser.py` budur.
* **Aklî müşahede (2. mertebe): ÜNİTER.** Nesneler arası emsal,
  aykırılık, küllî nizam. Ağaç üzerinde kapı olarak koşar.

İbnü'l-Heysem'in *Kitâbü'l-Menâzır*'daki **mücerred his** / **kıyas-ı
hafî** ayrımına birebir oturur. Kıyas (𝒪₁₈) ise ancak hükmü bir
nesneden ötekine **taşıdığında** başlar; emsali görmek hâlâ müşahededir.

## H56 — **ÜÇ AĞAÇ**: her şahit + test girdisi + çıktı

ARC'de 2-4 gösterim çifti vardır ve her biri bir **şahittir** (H6).
Mimari şudur:

    [şahit₁ girdi ağacı] [şahit₁ çıktı ağacı]   ← ikisi de KİLİTLİ
    [şahit₂ girdi ağacı] [şahit₂ çıktı ağacı]   ← ikisi de KİLİTLİ
    ...
    [test girdi ağacı]   ← KİLİTLİ
    [ÇIKTI ağacı]        ← bütün ihtimallerde AÇIK (süperpozisyon)

Melekeler şahit ağaçlarından çıktı ağacına kapı vurur: şahitlerde
müşahede edilen münasebet, çıktı ağacındaki ihtimalleri söndürür.
Kıyas (𝒪₁₈) ve nakz (𝒪₂₃) ancak böyle fiilen işleyebilir -- tek ağaçta
şahitlik diye bir şey olamaz.

## H57 — Vasıf-kademe tasnifini **ölçüm koyar, ajan değil**

Hangi mübser vasfın ağacın hangi kademesinde yaşayacağı elle
tayin edilmeyecek. Her vasıf her kademede hesaplanıp, hangi
``(vasıf, kademe)`` çiftinin ARC kaidesini en çok ayırt ettiği
**ölçülecek**. Sebebi: 22 kanalın 19'unun zararlı çıkması (H46) gibi bir
sürpriz burada da olabilir ve ajanın tasnif sezgisi bir kere daha
yanılabilir.

## H62 — Çıktının **boyutu aklın işidir**, müşahedenin değil

Kullanıcı hükmü, **üç defa** tekrarlanmıştır:

> *"Bu dağarcıkla çözülecek bir şey değil, bizzat kuantum zihni o boyutun
> neden öyle olduğuna karar vermeli. Müşahede o boyutu görür ve işi
> biter; o boyutun neden öyle değiştiği aklın işidir."*
> *"Çünkü boyut girdi çıktı arasında değişiyorsa bu kaideye göre
> değişmiştir, aklın işidir, müşahedenin değil."*

Bunun neticeleri:

* `nefs/boyut.py`'deki 22 elle yazılmış kaide **mekanizma değildir**;
  yalnızca bir **taban ölçümüdür** (H48: sınama kümesinde **+0,0**).
  Ana yolda kullanılmaz.
* Çıktı ağacı (H56) **bütün muhtemel boyutlarda** açılır; boyut da
  ihtimal uzayının bir parçasıdır, dışarıdan verilen bir çerçeve değil.
* Boyutu daraltan şey melekelerin çıktı ağacına vurduğu kapılardır:
  şahitlerde görülen münasebet yanlış boyutları **söndürür**.
* Müşahedenin boyutla tek işi vardır: girdinin ve şahit çıktılarının
  boyutunu **görmek**. Tahmin etmek onun salahiyetinde değildir.

## H58 — 𝒪₂ Hayal: **sabit değil, çok katmanlı ve destekli depo**

Kullanıcı hükmü:

> *"Hayal bir depodur evet ama sadece o ağaçların deposu mudur
> bilmiyorum, ve bu depo sabit değildir; sabit tarafları da vardır,
> anlık olanı vardır, sürekli olanı vardır, yenilenebileni vardır.
> Bunlar zihnin diğer melekeleri ile irtibat halindedir; neyi tutacaklarına,
> neyi yenileyeceklerine, anlık olarak ne depo açıp nereye aktaracaklarına
> **kendi karar vermez, destek alır**."*

Zabıt:

1. Hayal **en az üç kademelidir**: *sabit* (görev boyunca değişmeyen —
   şahit ağaçları), *sürekli* (yavaş yenilenen — çıkarılmış münasebetler),
   *anlık* (tek bir kapı dizisi boyunca yaşayan — çalışma yazmacı).
2. Depo **yalnız ağaç deposu değildir**; ucu açıktır (kaide, makam, nakz
   izi de hayalde durabilir).
3. **Tahsis kararı hayalin kendisinin değildir.** Neyin tutulacağı,
   neyin yenileneceği, anlık deponun nereye aktarılacağı başka
   melekelerin (𝒪₄ Tertip, 𝒪₅ Tecrit, 𝒪₂₉ Teyit) **desteğiyle** verilir.
   Yani hayal bir *edilgen* uzuvdur; yazma yetkisi dışarıdadır.

Mimarîye bağlanışı: hayal, ağaçların ve yardımcı kübitlerin **tahsis
defteridir**. Anlık kademe, kapı dizisi bitince yardımcı kübitleri
tersinir devreyle **temizler** (Grover usulü); sürekli kademe temizlenmez.

## H59 — 𝒪₃ Muhayyile: **ikisi birden** — hem diriltir hem uzağı bağlar

Muhayyile ne yalnız hafızadan sûret çağırmaktır, ne yalnız uzak
münasebet kurmaktır; **ikisi birden**dir.

* *Diriltme*: hayalde duran (sabit yahut sürekli) bir sûreti anlık
  kademeye geri getirir — ağaç üzerinde bir **alt-ağacın** yeniden
  açılması.
* *Uzağı bağlama*: ağaçta birbirinden uzak iki yaprağı **tek yol**
  üzerinden bağlar (`agac.yol`). Ağacın ``O(log N)`` mesafesi tam da bu
  melekenin ucuzlamasıdır: zincirde 899 adım, ağaçta 20 (H53).

## H60 — 𝒪₄ Tertip: **umumî tertiptir** ve UZAYLARLA çalışır

Kullanıcı hükmü (dikkat: *morfizm* değil, **uzay** dedi):

> *"Tertibin vazifesi umumi olarak bir şeyi tertip etmektir. Gayeyi de
> tertip eder, stratejiyi de, sorduğu bir suali de, aldığı bir cevabı da.
> Bunun için **sonsuz kategoriden türetilebilen çeşitli uzaylar** kullanır
> — uzay diyorum dikkat et, morfizm falan demiyorum: **kapalı devir, açık
> devir, boru hattı, ağaç, katmanlaştırma** ve daha çok **mütedahiliyet**;
> ve bizim bilmediğimiz tertip usulleri daha keşfedebilir, **ucu
> açıktır**."*

Zabıt:

1. Tertibin nesnesi **her şeydir**: gaye, strateji, sual, cevap, kapı
   dizisi. Yalnız meleke sırası değildir.
2. Kullandığı şey **uzaydır**, morfizm değil. Yani tertip bir ok dizisi
   seçmez; içinde tertibin yaşadığı bir **şekil** seçer.
3. Bilinen uzaylar en az şunlardır ve `nefs/mertebe.py`'deki 20 liften
   türetilir: **kapalı devir** (geri besleme), **açık devir** (tek geçiş),
   **boru hattı** (ardışık kademe), **ağaç** (dallanma), **katmanlaştırma**
   (Postnikov kulesi), **mütedahiliyet** (iç içe geçme).
4. **Ucu açıktır**: liste kapalı sayılmaz; tertip yeni bir uzay
   keşfederse mimarî onu kabul etmek zorundadır. Bu yüzden tertip sabit
   bir `AKIS` listesi olarak yazılamaz.

Bu hüküm, mevcut `AKIS` sabit listesini **kusurlu** îlan eder: 41 meleke
sabit sırayla koşuyorsa tertip diye bir meleke fiilen yoktur.

## H61 — 𝒪₅ Tecrit: Mera'dan da dolaşıklık çözücüden de **fazlasıdır**

Kullanıcı hükmü:

> *"Tecrit ikisinden de fazlası olan bir şey. Şu an bilmiyorum ama ne
> sadece Mera'dır, ne sadece dolanıklık çözücüdür; zihnin diğer
> bölümleriyle etkileşimde olan bir şeydir."*

Kullanıcının verdiği **altı kademeli** akış (biyolojik yola koşut) ve
formülleri aynen zabıtlanır:

| kademe | usul | formül |
|---|---|---|
| 1 | **Demet (sheaf)** — mahallî müşahedelerin uyuşması | ``Res_i(X_i) − Res_j(X_j) = 0`` |
| 2 | **Funktor** — küresel hâlden mânâ çıkarma | ``S_ham = F(X_küresel) = W_fonksiyonel · X_küresel`` |
| 3 | **Grassmann** — alâkalı alt uzaya izdüşüm | ``P_G = G_t(G_tᵀG_t)⁻¹G_tᵀ`` |
| 4 | **Dikkat** — izdüşüm üstünde tartma | ``D_t = Softmax((P_G·S_ham·W_d)/√d_k)`` , ``S_t = D_t·S_ham`` |
| 5 | **İlliyet (DAG)** — sebep ağı, çevrimsizlik şartı | ``A_neden = Sigmoid((S_t·W_neden·S_tᵀ)/√d_sem)`` , ``İz(exp(A∘A)) − Boyut = 0`` |
| 6 | **Müdahale + terkip** | ``İllet_Müdahale = Σ_H P(S_hedef\|S_kaynak=z,H)·P(H)`` , ``İ_t = GELU(İllet_Müdahale·W_i + H_t·W_hi)`` |

Devamı 𝒪₄'ün strateji manifoldu (Mutasarrıfa) ve program terkibi +
tasdiktir. **Çevrimsizlik şartı** (``İz(exp(A∘A)) = Boyut``) dikkat
çekicidir: ağacın çevrimsizliğiyle (H53) aynı kaidedir — tesadüf
değildir, tecridin ağaç üstünde yaşamasının sebebidir.

## H63 — 𝒪₈ Tahlil **dört** şeyi ayırır ve dördüncüsü ucu açıktır

Kullanıcı hükmü:

> *"Hem kaideleri alt kaidelere ayırır, hem şahitleri birbirinden ayırır,
> hem boyut değişiminin sebeplerini ayırır, hem de **dinamik olarak sorgu
> üretecek** bu mimaride belli şeyleri."*

1. **Kaideyi alt kaidelere.** Girdi→çıktı dönüşümü birbirinden bağımsız
   daha küçük dönüşümlere ayrılır (önce döndür, sonra boya). Kübitte:
   çıktı ağacına vurulacak kapı dizisinin **çarpanlara** ayrılması.
2. **Şahitleri birbirinden.** Her şahidin hangi kısmı küllî kaideye,
   hangi kısmı o şahide has tesadüfe ait. Nakzın (𝒪₂₃) hammaddesidir.
3. **Boyut değişimini sebeplerine.** H62 gereği boyut aklın işidir;
   tahlil *"boyut niye değişti"* sualini parçalara ayırır.
4. **Dinamik sorgu üretimi.** Tahlil yalnız eldekini bölmez; mimarînin
   içinde **yeni sual üretir**. Bu, tahlili edilgen bir ayrıştırıcı
   olmaktan çıkarır: neyin bölüneceğine bakarken neyin sorulacağını da
   tayin eder. Ucu açıktır ve sabit bir bölme listesiyle yazılamaz --
   H60'taki tertip hükmüyle aynı cinstendir.

Not: müşahedenin (𝒪₁) yaptığı nesne bölütlemesi tahlile **dâhil
değildir**; tekrar edilmeyecektir.

## H64 — Ağaç MPO kapısı kuruldu ve **tam hesapla** sınandı

`nefs/agac.py`. Kullanıcı hükmü: *"Ağaç MPO — operatörü yol boyunca
yay, kübit oynatma."* Aynen yapıldı: ``G = Σₖ Aₖ ⊗ Bₖ`` ayrıştırılır,
``k`` indisi iki yaprak arasındaki **tek yol** boyunca ``T ⊗ δ`` ile
taşınır, zirvede aynı ``δ`` operatörü kapatır. Hiçbir hücre yer
değiştirmez. Kanonik hâl (yapraklardan merkeze QR) eklendi ki kesme
**en iyi** olsun ve raporlanan kesme sayısı yalan olmasın.

Ölçüm (rastgele üniterler, tam dalga vektörüyle birebir karşılaştırma):

| ızgara | renk | χ | kapı | ‖Δψ‖/‖ψ‖ | norm | kesme |
|---|---|---|---|---|---|---|
| 2×2 | 2 | 16 | 6 | 2,780e-15 | 1,000000000 | 0 |
| 2×3 | 2 | 64 | 8 | 2,804e-15 | 1,000000000 | 0 |
| 3×3 | 2 | 64 | 10 | 2,906e-15 | 1,000000000 | 0 |
| 2×3 | 3 | 81 | 6 | 4,345e-15 | 1,000000000 | 0 |

χ kısılınca (aynı devre, 3×3, renk 2):

| χ | ‖Δψ‖/‖ψ‖ | kesme |
|---|---|---|
| 2 | 6,824e-01 | 5,145e-01 |
| 4 | **2,906e-15** | 0 |
| 8 / 16 / 64 | 2,906e-15 | 0 |

Köşe-köşe mesafe (zincir → ağaç): 3×3 8→6, 5×5 24→10, 10×10 99→14,
**30×30 899→18 (49,9 kat)**. (H53'teki tablo *âzamî* mesafeyi veriyordu;
bu tablo *köşe-köşe*yi verir — ikisi ayrı ölçüdür, biri ötekini
nakzetmez.)

## H65 — Üç ağaç kuruldu; **boyut ihtimal uzayına girdi**

`nefs/ucagac.py`. H56 ve H62 beraber icra edildi.

* Hücrenin hâl sayısı ``renk`` değil **``renk+1``**dir; fazladan hâl
  ``HARİÇ`` = *"bu hücre çıktının dışındadır"*. Düzgün süperpozisyonda
  **bütün boyutlar aynı anda askıdadır**. Ölçüldü: her hücrede
  ``P(dolu) = 0,909 = 10/11``, tam beklenen değer.
* Şahitler ayrı ayrı ``AgacYazmaci`` olamaz — dolaşamazlardı. Hepsi
  **tek** ağacın blokları olarak dizildi:
  ``[ş₀.girdi][ş₀.çıktı][ş₁.girdi][ş₁.çıktı][test.girdi][ÇIKTI]``.
  Kilitli bloklarda ``‖P−δ‖`` sapması **0,00e+00**.
* Şahit hücresiyle çıktı hücresi fiilen dolaştı (ağaç MPO, 10 adımlık
  yol): çıktı (0,0)'da doğru rengin ihtimali **0,0909 → 0,8729**,
  norm 1,000000000, kesme 0.

**KUSUR (ölçüldü, gizlenmiyor):** kanaat açısı ``θ`` tek yönlü bir
"kuvvet" değildir. Başlangıç açısı ``arctan(√10) ≈ 1,26`` rad olduğu
için θ büyüdükçe içerideki doluluk önce 1'e çıkıp sonra **geri düşüyor**
(θ=0,3 → 1,000 ; θ=0,9 → 0,687). Doğrusu, açının hedefe olan **fark**
olarak verilmesidir; sabit θ yanlıştır. Düzeltmesi, açıyı verecek
melekenin formülüne bağlıdır ve o formül henüz kararlaşmamıştır.

**İddia edilmeyen:** `ucagac.py` bir ARC çözücüsü **değildir**. Kurulan
şey zemindir; boyutun ihtimal uzayında olduğu ve kapının onu
söndürebildiği ölçülmüştür, o kadar.

## H66 — 𝒪₂ Hayal kuruldu: üç kademe + tersinir temizlik

`nefs/hayal.py`. H58'in üç şartı da koda geçti:

* Üç kademe (`sabit` / `sürekli` / `anlık`) ayrı defterde durur.
* **Destekçisiz tahsis reddedilir** (`PermissionError`) — hayal kendi
  kendine karar vermez; her tahsis ve her aktarma bir meleke adıyla
  yapılır. Sabit kademe hiç taşınmaz.
* Anlık kademeye vurulan her kapı kaydedilir ve ``U†`` ters sırayla
  vurularak **geri alınır**. Sebebi: ``|ψ⟩|çöp⟩`` hâlinde çöp kübiti
  hangi dalın seçildiğini "bilir" ve dallar bir daha girişemez —
  Grover'ın çalışmamasının klasik sebebi budur.

Ölçüm: 5 kapı vuruldu (anlık hücrelerde sapma 3,262e-01), geri alındı;
**anlık hücre hatası 3,331e-15**, **sabit hücre hatası 3,331e-16**,
norm 1,000000000, kesme 0. `nefs/test_nefs.py`: 41/41 geçiyor.

## H67 — Cevap bekleyen sualler (BORÇ)

Kullanıcı 𝒪₆, 𝒪₇, 𝒪₉ için *"başka / ben tarif edeceğim"* dedi ve
cevapları hazırladığını bildirdi. **Bunlar uydurulmayacaktır**:

* **𝒪₆ Tasavvur** — tecritten gelen mânâyı ne yapar? (sûret kurar mı,
  ihtimal açar mı, ikisi birden mi)
* **𝒪₇ Mânâ** — 𝒪₅ Tecrit'ten nasıl ayrılır? (isimlendirme mi, Vâhime
  gibi hisle alınmayan mânâ mı)
* **𝒪₉ Terkip** — hangi uzayda birleştirir? (𝒪₄'ün verdiği uzay mı,
  daima ağaç mı, program terkibi mi)

Bu üçü cevaplanmadan `ucagac.py`'deki kanaat açısı formülü
yazılmayacaktır; H65'teki θ kusuru da onlara bağlıdır.

---

# DÖRDÜNCÜ CERİDE — modern kompakt temsiller ve GPU'da dalga eniyilemesi

*Kullanıcı iki vesika verdi (NQS / Stabilizer Rank / PTR ve patlamasız
dalga eniyilemesi) ve şunu istedi: "bu dosyaların kodunu yaz ve mimariye
kesin bir surette bağla", "Kaggle'a yani gerçek 21×4 = 84 GB GPU'ya
paralel çalışacak şekilde hazırla", "modelin tüm parametrelerini mümkün
olan hududun en sonuna kadar aç", "en azından CPU'da eğitimin çok kısa
hâli çalışabilmeli".*

## H68 — NQS kuruldu: durum bir **dizi değil, fonksiyondur**

`kuantum/nqs.py`. ``|Ψ⟩ = Σ_x ψ_θ(x)|x⟩``, ``ψ_θ = exp(Σ_k KAN_k(x))``.

* Doğrusalsızlık **kenardadır** (KAN), Chebyshev tabanında açılır --
  kütük H3'ün *"uydurma = KAN sembolik kapanışı"* şartıyla aynıdır.
* Son kat **karmaşıktır**: faz da öğrenilir. Reel bir dalga ile girişim
  olmaz; bu bir tercih değil şarttır.
* Bellek ``2^N`` değil ``dim(θ)`` kadardır.
* `ozellik()` son kattan önceki Chebyshev özelliklerini verir ve
  ``log ψ`` onlarda **doğrusaldır** -- son kat **kapalı formda en küçük
  karelerle** oturur. Gradyan yasağı böylece mahrumiyet değil usul olur.

## H69 — Dalga eniyileyicisi: ``2^N`` hiçbir yerde açılmaz

`kuantum/dalga.py`. Sebebi cebirdir: ``U_L`` köşegen, ``D`` rütbe-bir.
Onun için ``G^k|Ψ₀⟩``ın genliği daima ``ψ₀(x)·P_k(z(x))``tir ve ``P_k``
yalnız **momentlere** bağlıdır. Bütün Grover özyinelemesi ``k+1`` sayı
üzerinde yürür; bellek ``O(k)``, ``N`` hiç girmez.

Eşik orağında polinom uzayı **iki boyuta** çöker ve özyineleme kapalı
formda çözülür (``α, β``); ``k* = round((π/2−θ)/(2θ))``, ``sin θ = √μ``.
Vesikadaki ``(π/4)√(2^N/M)`` bunun ``μ→0`` haddidir.

**AŞIRI İDDİA REDDEDİLDİ.** Klasik GPU'da bu usul ``√`` hızlanma
**vermez**; Grover'ın hızlanması kuantum donanımına aittir. Kazanılan
dört şey ölçülebilir: gradyansızlık, en iyi ``k``nın kapalı formda
bilinmesi, kapalı formda öğrenme, ve tek noktadan değil bütün uzaydan
tartma.

## H70 — Dalga eniyileyicisinin ÜÇ kusuru ölçüldü ve düzeltildi

Hiçbiri tahminle değil, ölçümle bulundu:

1. **Örnekleyici kilitleniyordu.** Yalnız tek bit çevirmeyle kabul oranı
   0,23 → 0,08'e düşüyor, zincirler tek havzada kalıyordu (3-SAT'ta 11'e
   karşı rastgele 12). Düzeltme: çok bitli teklif + elit tohumlama +
   **bağımsız teklif** (öğrenilen kenar dağılımından, MH düzeltmesiyle).
2. **Eşik yükseliyordu.** Eşik her çevrimin kendi niceliğinden alınınca
   dağılım keskinleştikçe eşik de 18'den 19'a çıkıyor, arama duruyordu.
   Düzeltme: Dürr–Høyer eşiği **monoton azalır**.
3. **Unutma ve aşırı keskinleşme.** Girişim çarpanı yalnız son 512
   örneğe oturtulunca Rastrigin'de 12 çevrimde rastgeleyi geçiyor
   (48,7'ye 54,6), **40 çevrimde yeniliyordu** (48,7'ye 35,4).
   Düzeltme: Grover bir **tavlama takvimi** olarak kullanılır --
   ``Δβ = ln R / ΔL``, ``R = (α/β)²`` -- ve hedef, biriken çarpan değil
   mutlak yüzey ``−(β/2)L``dir. Tavlama hızı ``β·σ_L`` biriminde
   sınırlanır; sınırsız bırakılınca Ackley'de ``β = 69,9``a çıkıp dalga
   daha aramayı bitirmeden donuyordu.

**Netice (ikili kodlu sürekli yüzey, 8 parametre × 6 bit = 48 kübit,
40 çevrim × 512 örnek = 20 480 kayıp çağrısı, aynı bütçe):**

| yüzey | dalga | rastgele arama |
|---|---|---|
| Ackley | **3,24** | 4,92 |
| Rastrigin | 37,25 | **35,40** |

**Rastrigin'de rastgele aramaya YENİLİYOR ve bu gizlenmiyor.** Sebebi
ölçüldü: MCMC örnekleri bağımsız değildir; kabul oranı ~0,15 ve
seyreltme 4 iken 20 480 örneğin müessir sayısı çok daha azdır.
Rastgele arama i.i.d. örnek verir. Yani dalga usulünün bedeli
**örnekleyicinin karışma maliyetidir** ve açık bir borçtur.

## H71 — Stabilizer rank: dolaşıklık bedava, magic pahalı

`kuantum/stabilizer.py`. Köşegen Clifford yörüngesi
``|φ⟩ = 2^{−n/2} Σ_y i^{q(y)}|y⟩`` (``q`` kuadratik, mod 4).

| ölçüm | netice |
|---|---|
| 60 Clifford kapısı (CZ+S) sonrası rank | **1** (dolaşıklık rankı hiç büyütmüyor) |
| genlik büyüklüğü sapması | 0,00e+00 |
| T kapısı: t=12 sonrası rank | 4096 (= 2^t, naif ayrışım) |

**Naif budama İFLAS ETTİ ve bu bir kazançtır.** χ 4096→64 inince atılan
``ℓ₂`` ağırlığı **1,607e-03** iken genlik hatası **9,866e-01**. Sebep:
terimler dik değildir, ``ℓ₂`` katsayı ağırlığı hatanın ölçüsü değildir.

**Bravyi–Gosset rastgele seyrekleştirmesi** yazıldı ve haddi altı
satırın **hepsinde** tuttu (``𝔼‖Ψ−Ω‖² ≤ ‖c‖₁²/k``, ``‖c‖₁ = 2,586``):

| k | ayrık terim | ölçülen hata | nazarî had |
|---|---|---|---|
| 16 | 16 | 3,252e-01 | 4,179e-01 |
| 64 | 64 | **6,220e-02** | 1,045e-01 |
| 256 | 253 | 1,955e-02 | 2,612e-02 |
| 1024 | 907 | 4,933e-03 | 6,530e-03 |
| 16384 | 4026 | 3,059e-04 | 4,081e-04 |

Yani χ=64'te naif budama %98,7 hata verirken seyrekleştirme %6,2.

**Temsil edilmeyen:** ``H`` kapısı. Umumî Clifford için CH-formu lazımdır;
**yazılmadı ve yazıldığı iddia edilmiyor.** İhtiyacımız olan devre bu
sınıftadır: referans ``|+⟩^n``, orak köşegen, difüzyon devre değil
rütbe-bir cebir.

## H72 — PTR kuruldu; **kendi tahminim yanlış çıktı**

`kuantum/ptr.py`. Halka ``ψ(x) = Tr(Π G_k[:,x_k,:])``; sürekli
parametrede ``G_k(t) = Σ_p C[k,p] T_p(t)``; uydurma **ALS ile kapalı
formda** (gradyan yok).

Halkanın üstünlüğünü hedefin **döngüselliğine** bağlamıştım. Ölçüm bunu
**doğrulamadı**:

| hedef | halka | zincir |
|---|---|---|
| döngüsel | **0,3547** | 0,5482 |
| uçları açık | **0,3406** | 0,5435 |

Halka her ikisinde de daha iyi. Demek ki kazanç dönemlilikten değil
uçların **serbestliğinden** geliyor: zincirde uç vektörleri ``e₀``a
sabitli, her iki uçta ``χ−1`` boyut boşa gidiyor. Dönemlilik faydası
varsa bu ölçüm onu ayıramadı.

Ayrıca bir kusur bulundu ve düzeltildi: zincir kolunun tasarım dizeyi
iz formülüyle kuruluyordu; o hâliyle mukayese geçersizdi (zincir 1,22
görünüyordu). Düzeltilince 0,548 oldu.

Çevrim bedeli duruyor: halkada kanonik hâl yoktur. Onun için PTR **yüzey**
temsilidir; **durum** temsili ağaçtadır (H53).

## H73 — H54'ün üç borcu KAPANDI, ikisi ölçülü kaldı

**3. borç -- yüksek mertebeler fiilen koşmuyor: KAPANDI.**
Gerçeği ölçümle bulundu: 20 lifin **hepsi** kuruluyor ve koşuyordu,
fakat uzak menzilli kısım ``adim < n_satir`` şartına takılıyordu.
6 satırlık girdide ``adım`` 1000. mertebe için 10, 60 000. mertebe için
17; ikisi de 6'dan büyük olduğu için **yüksek mertebelerin ayırt edici
tarafı hiç ateşlenmiyordu**. Geriye yalnız ``olcek`` kalıyor, o da 1000
ile 60 000 arasında 0,126'ya karşı 0,083. Düzeltme: mesafe satırda değil
**kübit zincirinde** ölçülür (6×12 = 72 kübitlik zincirde 17 adım
pekâlâ tanımlıdır). Şimdi 20 lifin hepsi MPO vuruyor: koşuda MPO sayısı
30, norm hatası 2,22e-16, entropi 2,0794.

**4. borç -- BEC sükûtu boğuyor: KAPANDI.** Ölçüldü:

| | sükût | tasdik | tenakuz | P_Şek |
|---|---|---|---|---|
| BEC yok | 0,7924 | 0,3685 | 0,3305 | 0,1553 |
| BEC (eski, bütün bloğa) | **0,0626** | 0,3499 | **0,5758** | 0,2561 |
| BEC (yeni, yalnız hüküm alanlarına) | **0,7924** | 0,3499 | **0,3305** | 0,2561 |

Yani eski hâl nefsi hem susamaz hem **daha çelişkili** kılıyordu.
Düzeltme kavramîdir: BEC **hükmün ittihadıdır**; sükût bir hüküm
değildir, tenakuz ve nakz da hüküm değil hükmün önündeki engellerdir.
Yoğuşmaya (``YOGUSAN``) yalnız makam, mîzân, tasdik, kelam girer.

**5. borç -- Python döngüsü hamallığı: KISMEN kapandı, ölçüldü.**
Profil çıkarıldı: 3 satırlık minik koşuda ``einsum`` 0,420 sn tutuyor ve
bunun **0,232 sn'si ``einsum_path``**, yani 2×2'lik tensörler için en iyi
büzülme sırasını **aramak**. Sıra zaten sabittir. İki sıcak yol
(``_cift_kapi_dilim``, ``tek_kapi_yuva``) yığın çarpımına çevrildi:

| yazmaç | önce | sonra | kazanç |
|---|---|---|---|
| 3 satır × 4 kübit, χ=16 | 0,658 sn | **0,530 sn** | 1,24× |
| 4 satır × 6 kübit, χ=32 | 2,767 sn | **2,619 sn** | 1,06× |
| 6 satır × 12 kübit, χ=64 | 36,33 sn | **30,92 sn** | 1,17× |

41 sınama geçmeye devam ediyor; ağaç kapısı hatası hâlâ 2,9e-15.
**Kalan borç dürüstçe duruyor:** geri kalan maliyet minik dizeylerde
LAPACK çağrı masrafıdır (SVD 0,324 sn, QR 0,352 sn). Asıl çare, ayrık
çiftleri **yığın hâlinde** işlemektir; şu anki zincir düzeni (veri ile
yerel hüküm kübitlerinin birbirine geçmesi) buna izin vermiyor.
Düzeni değiştirmek ayrı bir hükümdür ve sorulmadan yapılmayacaktır.

**2. borç -- 8 örnekli AS-GEK: yapı olarak kapatıldı, ölçümü Kaggle'da.**
Dalga motorunda örnekler **birikir** (tampon); AS-GEK ise her çevrimde
8 örneğini atıp yüzeyi sıfırdan kuruyordu. `AZAMI_KAGGLE` ayarında
çevrim başına 4 096 örnek, 400 çevrimde ~1,6 milyon değerlendirme --
250 boyut için gereken ``10·d = 2 500`` haddinin çok üstünde.

## H74 — Kaggle: iş bölünür, ağırlık bölünmez

`main/kaggle.py`, `hesap/donanim.py`, `docs/KAGGLE.md`.

Gradyan olmadığı için (H3) cihazlar arası ``all_reduce`` **yoktur**.
Bölünen şey iştir: kübit ileri geçişi süreçlere, NQS genlik ve
örneklemesi cihazlara, Grover özyinelemesi hiç (zaten bedava).

**84 GB'ın çoğu boşta kalır ve bu bir kusur değildir.** ``2^N`` hiçbir
yerde açılmaz; VRAM'i tüketen tek şey yığın büyüklüğüdür. Onun için
azamî ayarda büyütülen şey belleğe sığdırma numarası değil **örnek
sayısıdır** -- yani istatistikî sağlamlık.

**GPU yolu BURADA KOŞMADI ve koştuğu İDDİA EDİLMİYOR:** bu makinede
torch yoktur. ``NQS._ileri_torch`` numpy yoluyla aynı formüldür, fakat
aynı sayıyı verdiği ancak Kaggle'da ölçülebilir. `hesap/donanim.rapor()`
hangi yolda olunduğunu her koşuda açıkça yazar.

## H75 — Bütün parametreler açıldı

`nefs/kulli_egitim.py:EgitimAyari`. Yazmaç ölçüleri (satır kübiti, χ,
MERA kademesi), veri ölçüleri (görev, örnek, pencere, sözlük), kodlama
(bit, yarıçap), dalga ölçüleri (NQS gizli katları, derece, çevrim,
örnek, zincir, oran, kademe, λ) ve donanım (süreç) **tek yerdedir ve
hiçbiri koda gömülü değildir**. Üç hazır ayar: `KISA_CPU`, `ORTA`,
`AZAMI_KAGGLE`.

Parametre kübite **Gri kodla** açılır: komşu tam sayılar tek bit
farkeder (sınandı: ardışıklar arası bit farkı kümesi = {1}), dolayısıyla
Metropolis'in tek bit çevirmesi parametre uzayında küçük bir adımdır.
Düz ikili kodda 31→32 geçişi altı biti birden çevirir ve uzay sunî
olarak uçurumlu görünür.

## H76 — Nefsin kaybında **AS-GEK, dalga motorunu YENDİ**

Uçtan uca koşuldu (kısa-CPU ayarı, 250 nefs parametresi → 1500 kübit,
4 veri örneği, 4 süreç):

| motor | V_son | kayıp çağrısı | süre |
|---|---|---|---|
| **AS-GEK (eski)** | **2,3889** | 246 | 2065,5 sn |
| DALGA (yeni) | 2,5194 | 144 | 1614,7 sn |

V ilk 2,5860 idi; dalga onu 2,5194'e indirdi (fark 0,0666), AS-GEK ise
2,3889'a. **Yani bu bütçede eski motor daha iyidir ve bu gizlenmez.**
Vesikadaki *"klasik Adam/SGD döngüsü tamamen kaldırılmıştır"* hükmü
kodda icra edildi, fakat **daha iyi netice verdiği ölçülmedi** --
tersi ölçüldü.

Teşhis, seyirden okunur: uydurma artığı çevrimlerle beraber
0,0051 → 0,2082'ye **yükseliyor**. Yani ``β`` tavlaması sertleştikçe
NQS hedef yüzeyi (``−(β/2)L``) temsil edemez oluyor. Kusur Grover'da
değil **ansatz sığasında**dır: 1500 kübitlik bir uzayda son kat 288
özellikle (48×6) uyduruyor. Sığayı büyütmek ayrı bir ölçüm ister.

İkinci teşhis: 144 çağrı, 250 boyutlu bir uzay için zaten azdır
(H54/2. borç ``10·d = 2 500`` diyordu). İki motor da o haddin çok
altındadır; bu koşu ikisinin de hükmünü vermez, yalnız **bu bütçede**
hangisinin önde olduğunu söyler.

## H77 — İki ölçüm kusuru: biri boş ölçüt, biri iplik çakışması

**1. Ölçüt boştu, sıfır değil.** Değerlendirmede üretilecek belirteç
sayısına had konmuş, hadde takılan görev ``kesilen`` diye sayılıp yine
de ``deneme``ye dâhil ediliyordu. Netice: 4 görevin **4'ü de** kesildi
ve rapor *"tam çözülen 0/4"* dedi -- oysa hiçbir görev sonuna kadar
denenmemişti. **Sıfır gibi görünen boş bir ölçüt, sıfırdan kötüdür.**
Düzeltme: hadde sığmayan görev **hiç denenmez**, atlanır ve atlandığı
ayrıca yazılır; ``azami`` artık "kaç görev taranır" değil "kaç görev
fiilen denenir" demektir. Ölçüldü: doğrulama görevlerinin hedef
uzunluğu ortanca **111** belirteç; ``≤32`` olan yalnız **18/100**.
Yani had, ölçütü küçük ızgaralara **taraflı** kılar ve bu da yazılır.

**2. Paralellik tek başına yetmiyor.** Kayıp 4 sürece bölünüyordu, fakat
her süreç kendi BLAS'ını da çok iplikli açıyordu: 4 çekirdekli makinede
4 süreç × 4 iplik = 16 iplik, çekirdekler birbirini bekliyor. Ölçüldü
(16 kayıp çağrısı, 4 süreç):

| | süre | çağrı başına |
|---|---|---|
| çok iplikli | 41,7 sn | 2,61 sn |
| **tek iplikli** | **19,4 sn** | **1,22 sn** (2,14 kat) |

Düzeltme: `hesap/donanim.tek_iplik_zorla()`, **numpy'dan önce** çağrılır
ve fiilen tesir edip etmediğini döner -- sessizce "oldu" demez.

**3. Mukayese eşit bütçeli değildi.** AS-GEK 246, dalga 144 kayıp
çağırıyordu; o hâlde tablo hüküm veremez. Artık bütçe **kayıp çağrısı
cinsinden** eşitlenir.

## H78 — İleri geçişin maliyeti ölçüldü; darboğaz LAPACK çağrı masrafı

Yazmaç ölçüsüne göre bir ileri geçiş (χ=16, satır kübiti 4):

| pencere | kübit | kapı | süre |
|---|---|---|---|
| 3 satır | 32 | 675 | 0,535 sn |
| 4 satır | 37 | 820 | 0,748 sn |
| 8 satır | 57 | 1379 | 1,201 sn |

Bir kayıp çağrısı 4 veri örneği demektir → ~4,7 sn (tek süreç, çok
iplikli) yahut ~1,2 sn (4 süreç, tek iplikli). Geri kalan maliyet
minik dizeylerde SVD/QR çağrı masrafıdır ve asıl çare ayrık çiftleri
yığın hâlinde işlemektir; mevcut zincir düzeni (veri ile yerel hüküm
kübitlerinin iç içe geçmesi) buna izin vermiyor. **Düzeni değiştirmek
H40'ı nakzetmek olur ve sorulmadan yapılmayacaktır.**
