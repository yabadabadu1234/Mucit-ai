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

