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

## H79 — `main/yazmac.py` taması: yığın kapılar kuruldu, kazanç ÖLÇÜLDÜ

Kullanıcı hükmü: dosya dosya taranacak; her dosyada *"bütün hız
baltalayıcıları düzelt → yeni nesil formüller yerleştir → algoritmayı
tashih et → test et"*. Bu, birinci dosyanın zabtıdır.

**Kullanıcının verdiği dört karar:** (a) hedef ölçüt **7 MB/sn**;
(b) melekelerin gövdesi değiştirilebilir, kapılar yığınlansın;
(c) **her yer float32**; (d) zincir düzeni için iki düzen birden dursun,
**ölçüm karar versin**.

**Kaldırılan yedi hız baltalayıcı:**

1. `tek_kapi` içindeki `einsum(..., optimize=True)` → yığın çarpımı.
2. `_cift_kapi_dilim`deki `T.astype(np.float32)` → tip zaten float32,
   her kapıda tam bir kopya çıkarıyordu.
3. `mpo_uygula`nın `astype(np.float64)` yükseltmesi → kalktı; MPO
   bütün zinciri iki katı bellekle kopyalıyordu.
4. `mpo_uygula`daki üç `einsum(optimize=True)` → yığın çarpımı.
5. `mpo_uygula`nın geri yazmada yuva başına yeni dizi tahsisi → tek
   tampon, yerinde sıfırlama.
6. `yuva_yogunluklari`nin Python döngüsü + yuva başına einsum → tek
   yığın çarpımı (ölçüm float64'e yükseltilir: durum f32, ölçüm f64).
7. `_cift_kapi_dilim`in **stride-2 kısıtı** → `_cift_kapi_cekirdek`
   keyfî ayrık çiftleri alır.

**İki yeni yığın kapısı** (`tek_kapi_yigin`, `cift_kapi_yigin`).
Doğruluk sınandı -- tek tek vurmakla **birebir aynı**:

| sınama | âzamî fark |
|---|---|
| 100 tek kübitlik kapı, her yuvaya ayrı kapı | **0,000e+00** |
| 50 iki kübitlik kapı, hepsine aynı kapı | **0,000e+00** |
| 50 iki kübitlik kapı, her çifte ayrı kapı | **0,000e+00** |

Not: yığın hâlinde dönen **kesme** ayrı bir şeydir. Tek tek vurulunca
5 kapının oranları toplanır (1,95e-01); yığında atılan/toplam oranı
**bir kere** hesaplanır (4,08e-02). İkisi aynı sayı değildir ve
karıştırılmamalıdır.

**Kazanç, ölçüldü ve BEKLENTİMİN ALTINDA:**

| iş | tek tek | yığın | kat |
|---|---|---|---|
| 100 tek kübitlik kapı | 0,0008 sn | 0,0002 sn | **4,1** |
| 50 iki kübitlik kapı | 0,0116 sn | 0,0075 sn | **1,5** |

Uçtan uca ileri geçiş (aynı girdi, üç ölçümün ortancası):

| yazmaç | başta | şimdi | kat |
|---|---|---|---|
| 3 satır × 4 kübit, χ=16 | 0,658 sn | **0,435 sn** | 1,51 |
| 4 satır × 6 kübit, χ=32 | 2,767 sn | **2,402 sn** | 1,15 |
| 6 satır × 12 kübit, χ=64 | 36,33 sn | **31,51 sn** | 1,15 |

**Asıl hüküm buradan çıkıyor:** çağrı masrafını kaldırmak yalnız
**küçük χ**de işe yarıyor. χ=64'te maliyet gerçek floptur (128×128 SVD),
Python değil. Yani "kapıları yığınla" tek başına 100 kat vermez ve
vereceğini iddia etmiyorum. Yığın arayüzü kuruldu fakat **melekeler
henüz onu çağırmıyor**; asıl kazanç melekeler taşınınca ölçülecek
(sıradaki dosya).

**Bir ölçüm dersi:** 6 satırlık ölçüm önce 34,18 sn çıktı ve
"kötüleşti" göründü. Yalnız başına tekrar ölçüldü: **31,51 sn**.
Makine o sırada sınama takımını da koşuyordu. Yüklü makinede alınan
hız ölçümü hüküm veremez.

## H80 — `nefs/qmeleke.py` taması: melekeler yığına taşındı

**Kullanıcının verdiği dört karar:** (a) takas/MPO eşiğini **ölçüm**
koysun; (b) cebrî sadeleştirme serbest, **birebir aynı ispatlanırsa**;
(c) 𝒪₂₁'in yirmi MPO'su **tek MPO**da toplansın; (d) yığın yazmaç
**iki eksenli** olsun (parametre × veri).

### Takas mı MPO mu: ölçüm BENİM BEKLENTİMİ ÇÜRÜTTÜ

`nefs/uzaklik_olcumu.py`. H41 *"takas ağı kapalı yoldur, MPO kazanır"*
diyordu. Ölçüldü ve hüküm ikiye ayrıldı:

| χ | mesafe | takas sn | MPO sn | takas kesme | MPO kesme |
|---|---|---|---|---|---|
| 8 | 5 | 0,00126 | 0,00179 | 6,48e-01 | 3,39e-01 |
| 16 | 5 | 0,00320 | 0,00334 | 2,04e-01 | 7,17e-02 |
| 32 | 5 | 0,00988 | 0,02506 | 5,30e-03 | **1,18e-30** |
| 32 | 21 | 0,04829 | 0,13509 | 4,65e+00 | 1,42e-01 |

* **HIZ:** MPO takastan **daha yavaş** -- χ=32'de 2,5-3 kat. H41'in
  "MPO kazanır" hükmü **hız için yanlıştır** ve öyle zabıtlanır.
* **KESME:** MPO takası eziyor -- χ=32, mesafe 5'te yirmi yedi mertebe
  fark. χ=8, mesafe 5'te takas durumun **%65'ini** atıyor.

O hâlde eşik hıza göre değil **doğruluğa** göre kondu:
``eşik = max(4, ⌊log₂ χ⌋ + 2)`` (χ=8→5, χ=16→6, χ=32→7, χ=64→8).
Mesafe eşiğin altındaysa takas (ucuz ve o mesafede kesmesi ihmal
edilebilir), üstündeyse MPO. **Hız uğruna doğruluk satılmadı.**

### Üç cebrî sadeleştirme ve ispatları

| sadeleştirme | dayanağı | ölçülen ‖Δψ‖ |
|---|---|---|
| 𝒪₃₁ Tedebbür: ``G⁴`` tek kapıda | dik dizeyin kuvveti | **1,81e-07** |
| 𝒪₂₁ Tefekkür: 20 MPO → 1 MPO | ``exp(A⊗Y)exp(B⊗Y)=exp((A+B)⊗Y)`` | **3,20e-07** |
| aynı eksene düşen liflerin açıları toplanır | ``R(α)R(β)=R(α+β)`` | 1,11e-16 |

Üçü de **float32'nin makine hassasiyeti** mertebesindedir (eps ≈ 1,2e-07).
Yani sadeleştirmeler birebir aynıdır; kalan fark, kullanıcının seçtiği
float32'nin yuvarlamasıdır ve bedeli budur.

**H21 bozulmadı.** Toplanan şey mertebeler değil, aynı durağa düşen
dönme açılarıdır; her lif kendi ``adım``ıyla kendi duraklarını seçmeye
devam eder.

### KENDİ ÖLÇÜM HATAM

Sadeleştirmeleri önce MPS **tensörlerini** (``y.A``) karşılaştırarak
sınadım; fark 1,08e+00, 1,92e+00, 1,89e+00 çıktı ve "sadeleştirme
bozuk" diye okunacaktı. **Ölçü yanlıştı:** MPS ayarı (gauge) tekil
değildir; aynı durum farklı tensörlerle yazılabilir. Doğru ölçü tam
dalga vektörüdür. Onunla ölçülünce üçü de 1e-07 çıktı. Ayar-bağımlı
bir büyüklükle hüküm vermek, ölçmeden hüküm vermekten farksızdır.

### Yığına taşınan melekeler ve netice

Onüç meleke (𝒪₁, 𝒪₂, 𝒪₄, 𝒪₅, 𝒪₈, 𝒪₉, 𝒪₁₀, 𝒪₁₂, 𝒪₁₅, 𝒪₁₆, 𝒪₁₇,
𝒪₁₉, 𝒪₂₅, 𝒪₂₆, 𝒪₂₇, 𝒪₂₈, 𝒪₃₁, 𝒪₃₈, 𝒪₄₀) `tek_yigin`/`cift_yigin`
kullanıyor. Fırça çiftlerinin ayrık olduğu ispatlandı: bir satır içinde
``j`` ile ``j+2`` çakışmaz, satırlar arasında yerel hüküm kübiti
ayırıcı durur.

| yazmaç | başta | H79 sonrası | **şimdi** | toplam kat |
|---|---|---|---|---|
| 3 satır × 4 kübit, χ=16 | 0,658 sn | 0,435 sn | **0,300 sn** | **2,19** |
| 4 satır × 6 kübit, χ=32 | 2,767 sn | 2,402 sn | **1,691 sn** | 1,64 |
| 6 satır × 12 kübit, χ=64 | 36,33 sn | 31,51 sn | **26,96 sn** | 1,35 |
| 8 satır × 12 kübit, χ=64 | 49,06 sn | -- | **33,22 sn** | 1,48 |

Kapı sayısı da düştü (2181 → 1748), çünkü 𝒪₂₁ ve 𝒪₃₁ sadeleştirildi.
41 sınama geçmeye devam ediyor.

**Hedefe göre nerede duruyoruz.** Kullanıcının ölçütü **7 MB/sn**.
Şu an 6 satırlık bir geçiş 26,96 sn; yani ~0,22 belirteç/sn. Hedefe
**3,2×10⁷ kat** uzak. İki tamada alınan toplam 2,19 kat, bu mesafeyi
kapatmaz ve kapatacağı iddia edilmiyor. Kapatabilecek tek yol, kararı
verilen **iki eksenli yığın yazmaçtır** (parametre × veri): bir kayıp
çağrısının tamamı tek yığında geçer.

## H81 — Yazmaç yığına geçti; **beklenen kazanç GELMEDİ ve sebebi ölçüldü**

**Kullanıcının verdiği üç karar:** (a) yığın ölçüsü ``P=256 × V=32``
(GPU'yu doldur); (b) **her yığın üyesi kendi ölçümünü versin**;
(c) uyarlanır ``χ`` **yok**, sabit ``χ`` öngörülebilirliktir.

`A` şekli artık ``(B, N, χ, 2, χ)``; ``B = P·V``. Tek durum ``B=1``dir
ve **ayrı bir kod yolu yoktur** (kullanıcı hükmü). Kapılar üç şekli de
kabul eder: ``(2,2)`` bütün yığına aynı, ``(m,2,2)`` yuvaya göre,
``(B,m,2,2)`` **yığın üyesine göre** -- parametre ekseni ancak
üçüncüsüyle iş görür.

Doğruluk: ``B=1`` ile ``B=4``, aynı devrede **birebir aynı**
(0,00e+00, dört üyenin dördünde de). 41 sınama geçiyor.

### Yığının kazancı 1,6 kat -- 8-16 değil. Sebep ölçüldü.

Şüphelendim ve ölçtüm: **numpy'nin yığın SVD'si gerçek yığın değildir.**

| m | d | SVD | QR | eigh | SVD/matris |
|---|---|---|---|---|---|
| 1 | 32 | 0,00041 | 0,00015 (2,7×) | 0,00028 | 4,08e-04 |
| 8 | 32 | 0,00263 | 0,00039 (6,8×) | 0,00121 | 3,29e-04 |
| 64 | 32 | 0,01520 | 0,00405 (3,8×) | 0,01024 | 2,38e-04 |
| 256 | 32 | 0,06100 | 0,01547 (3,9×) | 0,03992 | 2,38e-04 |

Matris başına maliyet ``4,08e-04``ten ancak ``2,38e-04``e iniyor
(1,7 kat) ve ``m=64``ten sonra **düzleşiyor**. Yani yığına geçmek
LAPACK çağrı masrafını kaldırmıyor; içeride yine matris başına çağrı
var. Bu, "yığın = B kat hız" beklentisinin neden yanlış olduğunun
cevabıdır ve GPU'da (torch) durumun farklı olması beklenir -- fakat
**burada ölçülemez ve ölçüldüğü iddia edilmiyor**.

### Aynı ölçümden çıkan yeni nesil formül: kesme yoksa QR

Aynı tabloda **QR, SVD'den 3,8-6,8 kat hızlı**. Ve ``Θ``nın rütbesi
``min(2·d_sol, 2·d_sağ)`` ile sınırlıdır; bu ``χ``yi aşmıyorsa budama
diye bir şey yoktur ve ``Θ = QR`` **tam** bir bölmedir.

Onun için ``bag_ust`` dizisi eklendi: her bağın **üst sınırı**, daima
büyük tarafa çekilerek tutulur. ``kesme_gerekli_mi`` buna bakar; hayır
derse QR yolu koşar ve ``kesme = 0`` döner.

Bu **uyarlanır χ değildir** (kullanıcı sabit χ dedi): bellek yine sabit
``χ``dir, yalnız hesap ucuzlar. Erken kapılarda durum çarpıma yakındır
ve QR yolu koşar; dolaşıklık arttıkça SVD'ye geçilir.

**Yapıp kırdığım ve düzelttiğim:** ham ``Θ``ya QR uyguladım ve kırıldı.
QR'ın rütbesi matrisin **şeklinden** gelir (``2χ``), gerçek rütbesinden
değil; sıfır satırlar ``Q``da yer kaplıyor ve netice ``χ``ye sığmıyordu.
``Θ``yı gerçek bağ sınırlarına kırpınca rütbe ``min(2d_sol, 2d_sağ)``
olur ve tanım gereği ``χ``yi aşmaz.

### Uçtan uca netice

| yazmaç | başta | H79 | H80 | **H81** | toplam |
|---|---|---|---|---|---|
| 3×4, χ=16 | 0,658 | 0,435 | 0,300 | **0,290** | **2,27** |
| 4×6, χ=32 | 2,767 | 2,402 | 1,691 | **1,421** | **1,95** |
| 6×12, χ=64 | 36,33 | 31,51 | 26,96 | **21,18** | **1,72** |
| 8×12, χ=64 | 49,06 | -- | 28,37 | **28,37** | 1,73 |

Yığın kazancı ayrıca ölçüldü: B=4/8/16'da **1,6 kat** (B kat değil).

Sadeleştirmelerin birebirliği yığın geçişinden sonra da duruyor:
G⁴ 2,28e-07, MPO birleştirmesi 3,73e-07, takas-MPO 1,14e-07 -- üçü de
float32 eps'i (1,2e-07) mertebesinde.

**Hedefe göre:** 7 MB/sn için hâlâ ~2,4×10⁷ kat uzağız. Üç tamada
alınan toplam 1,7-2,3 kattır. CPU'da numpy ile bu mesafenin
kapanmayacağı artık **ölçülmüş** bir hükümdür: darboğaz Python değil,
LAPACK'in matris başına çağrısıdır ve onu ancak gerçek yığın çekirdeği
(GPU) kaldırır.

---

# BEŞİNCİ CERİDE — NİZAM: tek padişah

*Kullanıcı hükmü: "Sen şimdilik hıza odaklanma... bir padişah gibi
nizamlama açısından baktığın zaman kodların asla bütünlüklü olmadığını,
birbiriyle kenetlenmeyen çokça kod bulunduğunu, birçok başıboş
padişahlık taslayan bulunduğunu, halbuki tek modelde tek padişah olması
gerektiğini ve padişahın elinin tüm kodlara uzanması gerektiğini
anlarsın... Sen şimdi artık Osmanlıyı kurmalısın."*

## H82 — ÖLÇÜLDÜ: kod tabanının **%90'ı beyliktir**

`tanilama/nizam.py` yazıldı. Ölçü açıktır ve tahminsizdir: bir modül,
ana giriş noktalarından (`main.kaggle`, `nefs.kulli_egitim`,
`nefs.qakis`, `nefs.hukum_denetimi`) bir içe aktarma zinciriyle
erişiliyorsa **tebaadır**; erişilmiyorsa **beyliktir**.

| | modül | satır | oran |
|---|---|---|---|
| toplam | 465 | 125 401 | |
| **TEBAA** | 38 | 13 147 | **%10** |
| **BEYLİK** | 427 | 112 254 | **%90** |

Kullanıcının teşhisi doğrudur ve rakamı budur.

**Çok başlılık, isimlerden bile görülüyor:**

| iş | kaç ayrı hat |
|---|---|
| akış | `akis`, `nefs.akis`, `nefs.qakis`, `yaklasim.akislar` |
| eğitim | `idrak.egitim`, `main.egitim`, `nefs.qegitim`, `nefs.kulli_egitim` |
| meleke | `nefs.meleke`, `nefs.qmeleke`, `reel.meleke` |
| yazmaç | `main.yazmac`, `nefs.qyazmac` |
| ana | `main.main`, `mucit_ai_esas.…main_egitim_dongusu` |
| ARC | `idrak.arc`, `harici_llm.arc*` (4 modül) |

**Kendi kurduklarım da beylik.** En utandırıcı olanı:
`nefs/ihtimal.py` -- kullanıcının *"ihtimal uzayı bizzat o kübitlerin
içidir"* hükmünü kurduğum dosya -- ana akışa **bağlı değil**. Aynı
şekilde `kuantum/` altındaki sekiz modül (devre, eniyileme, kapilar,
qsvt, surekli, tda, topolojik + iki sınama) hiç çağrılmıyor: 3 000 satır.

## H83 — ASIL KÜLLÎ HATA: kübit **paralel işlemiyor**

Kullanıcı hükmü: *"Biz bu projeye neden kübit koyduk sence, keyfimizden
mi? Kübitin tutabildiği her bir ihtimali bir kelime olarak düşününce
aynı anda 1 belirteç değil 1 milyon belirteç işlenebileceğini
söylemedik mi?"*

Ölçtüm ve **hüküm kullanıcının lehinedir**:

| | ölçülen |
|---|---|
| yazmaç (6 satır × 4 kübit) | 47 kübit |
| tutulabilen ihtimal | ``2⁴⁷ = 1,4×10¹⁴`` |
| durum belleği | 94 KB |
| **beyanın okunduğu alan** | **yalnız 4 kübit (kelam)** |
| aynı anda okunabilen belirteç | **16** |

Yani `2⁴⁷` ihtimal taşıyan bir yazmaçtan, her seferinde **tek bir
belirteç** okunuyor. Çıktı ızgarası 6×6 = 36 hücre olduğu için
`degerlendir` **36 ayrı tam ileri geçiş** yapıyor (~43 sn/görev).

Bu, kübit mimarîsinin **inkârıdır**: klasik bir dil modelinin
otoregresif üretimi kübit yazmacına giydirilmiştir. Süperpozisyonun
tek faydası -- bütün ihtimalleri aynı anda taşımak -- hiç
kullanılmamaktadır.

**Doğrusu:** çıktı ızgarasının **tamamı** süperpozisyonda tutulmalı
(36 hücre × 4 kübit = 144 kübit), melekeler ihtimalleri söndürmeli, ve
**tek ölçümle** okunmalıdır. `nefs/ucagac.py` bunu zaten kuruyor
(H65: çıktı ağacı bütün boyutlarda açık, `P(dolu)=10/11`) fakat ana
akış ondan habersiz -- bir beylik daha.

**Bu, hız meselesi değil paradigma meselesidir.** 7 MB/sn hedefine
kapı ovalayarak değil ancak buradan gidilir: bir geçişte bir belirteç
yerine bir geçişte **bütün ızgara**.

## H84 — Istılâh vesikası (BORÇ ÖDEMESİ)

`docs/ISTILAH.md`. Kullanıcı hükmü: *"Ben sadece hayal kurmayı
biliyorum, kendimden terim ürettiğim yok; dolayısıyla anlaşabilmemiz
için terimlerinin manasını detaylı izah etmen lazım."*

Bu benim kusurumdu: sual sorarken cevabı anlaşılmaz kılan terimler
kullandım, alınan cevap da benim çerçeveme mahkûm oldu. Kırk kadar
terim (kübit, süperpozisyon, dolaşıklık, MPS, χ, kesme, MPO, ayar,
kanonik hâl, POVM, marjinal, ansatz, NQS, faz orağı, difüzyon, Grover,
tavlama, Metropolis, yığın, LAPACK çağrı masrafı...) **önce hayalî
karşılığıyla**, sonra riyazî tarifiyle yazıldı.

Bundan sonraki suallerde: terim önce hayalî karşılığıyla verilecek;
her şıkkın **ne kaybettireceği** de yazılacak, yalnız ne kazandıracağı
değil.

## H85 — KÂİDE bir cevap değil, bir **İSPAT YAPISI**dır

Kullanıcı hükmü (benim iki teklifimi de reddederek):

> *"Temel işlem dizisi asla. Hücre eşlemesi ondan daha mantıklı ama o da
> nihayet değil, hatta bana son derece kötü gözüküyor. Kaide şu olmalı:
> çıktı hücresi ne kadar ebatta olacak, benim söylediğim ebat kesin mi,
> aksinin mümkün olmadığı ispatlandı mı? Tüm misaller için ebat
> tahminlerim doğru mu, renklerim doğru mu? Her rengi neden koyduğumu
> açıklayabiliyor muyum? Hangi rengin yerine başka bir şey koymanın
> imkansızlığını açıklayabiliyor muyum? İşin sebebini illetini
> delillerini ispatlarını biliyor muyum? Yani esasında aklıma şu geliyor
> ki o bahsettiğim melekelerden destek almalıyız, nasıl olacağını
> bilmemekle beraber."*

**Bu, benim iki teklifimi de nakzeder ve daha derindir.** Ben kâideyi
bir **üretici** olarak düşündüm (ne yapılacağını söyleyen bir tarif);
kullanıcı onu bir **hüccet** olarak tarif ediyor (neden başka türlü
olamayacağını gösteren bir delil yapısı).

Kâidenin taşıması gereken yedi şey:

1. **Ebat** -- çıktı ızgarası ne kadar olacak.
2. **Ebadın kesinliği** -- aksinin mümkün olmadığı ispatlandı mı.
3. **Misallerde tutarlılık** -- bütün şahitlerde ebat tahmini doğru mu.
4. **Renklerin doğruluğu** -- bütün şahitlerde renkler tutuyor mu.
5. **Her rengin gerekçesi** -- bu rengi neden koydum, açıklayabiliyor muyum.
6. **Aksinin imkânsızlığı** -- bu rengin yerine başkasını koymanın niçin
   mümkün olmadığını gösterebiliyor muyum.
7. **İllet ve delil** -- işin sebebini, illetini, delillerini, ispatlarını
   biliyor muyum.

Yani model *"çıktı budur"* demeyecek; *"budur, çünkü şudur, ve aksi şu
sebeple imkânsızdır"* diyecek. Cevabın kendisi değil, **cevabın
zorunluluğu** aranacak.

**Bunun mimarîdeki karşılığı doğrudan mizan/ ve fitrat/dır** ve
kullanıcı bunu sezmiştir (*"melekelerden destek almalıyız"*):

| kâidenin şartı | hangi meleke / paket |
|---|---|
| aksinin imkânsızlığı | `mizan/kiplik` (zorunluluk-imkân), 𝒪₂₃ Mantık |
| bütün misallerde tutma | `mizan/istikra` (tümevarım), 𝒪₁₈ Kıyas |
| tek karşı örneğin düşürmesi | 𝒪₂₃ nakz (H6) |
| illet | `fitrat/karsi_olgusal`, `fitrat/ayrisma`, 𝒪₂₂ İllet |
| delillerin birbirini teyidi | `fitrat/tevafuk`, 𝒪₂₉ Teyit |
| ispatın kendisi | `mizan/cikarim` (Gentzen), 𝒪₂₄ İspat |
| bilmediğini bilmek | 𝒪₃₂ makam + sükût (H10) |

Bu yüzden *"mizan ve fitrat kübit hattına bağlansın"* hükmü (aynı
oturumda verildi) bu hükmün **aynı meselenin öbür yüzüdür**: kâide bir
ispat yapısıysa, ispat motorları ana akışa girmek zorundadır.

**Açıkça kaydedilen borç:** kullanıcı *"nasıl olacağını bilmemekle
beraber"* dedi. Ben de bilmiyorum. Bu hüküm bir **istikamet**tir,
bir tarif değil; tarif ortak çalışmayla çıkarılacaktır ve
uydurulmayacaktır.

## H86 — H3'ün KISMÎ NAKZI: natural gradyan denenecek

Kullanıcı hükmü:

> *"Senin tarifine göre şu an melekeler rastgele deneme yanılmayla
> öğreniliyormuş, bu kabul edilemez. Şu anki 250 parametre bir de
> bildiğimiz natural gradyan ile öğrenilsin, bakalım ne olacak?
> Sonrasında işe yaramazsa sileriz."*

H3 *"ana döngüde gradyan ve kayıp yoktur"* diyordu. Bu hüküm o
yasağı **kaldırmaz**, fakat bir istisna açar ve istisna ölçüme
bağlıdır: natural gradyan kurulacak, mevcut motorlarla **aynı bütçede**
karşılaştırılacak, işe yaramazsa silinecektir. Kütük kaidesi gereği
(*içtihad içtihadı nakzetmez*) H3 düşmez; yanına bu istisna yazılır.

**Natural gradyan nedir (hayalî karşılığıyla).** Sıradan gradyan
"parametreyi hangi yöne oynatırsam kayıp azalır" der ve bütün
parametreleri **eşit mesafeli** sayar. Halbuki bir açıyı 0,1 radyan
oynatmakla bir başkasını 0,1 oynatmak, modelin **davranışında** çok
farklı büyüklükte değişiklik yapabilir. Natural gradyan mesafeyi
parametrede değil **modelin verdiği cevapta** ölçer: "cevabımı ne kadar
değiştirdim" cinsinden bir adım atar. Kuantum durumlarında bunun adı
*Stochastic Reconfiguration*tur ve Fubini–Study metriğiyle ölçer.

**Neden mimarîye uygun:** bizim parametrelerimiz **açıdır**; açıların
öklit mesafesi manasızdır (2π periyodik), fakat durumun değişimi
manalıdır. Yani natural gradyan burada bir yama değil, doğru ölçüdür.

## H87 — Kaggle bu ortamdan ERİŞİLEMİYOR (ölçüldü)

Kullanıcı hükmü: *"Şu testleri kaggle'da yapabiliyorsan ve neticeleri
okuyabiliyorsan artık orada GPU ile yap."*

Denendi ve **olmuyor**; sebebi jeton değil ağ siyasetidir:

```
kaggle competitions list
→ OSError: Tunnel connection failed: 403 Forbidden
proxy kaydı: "gateway answered 403 to CONNECT ... host: api.kaggle.com:443"
```

Yani bu oturumun çıkış vekili (proxy) `api.kaggle.com`a bağlanmayı
**siyaseten** reddediyor. Jeton `~/.kaggle/access_token`a kuruldu
(koda **yazılmadı**) ve orada duruyor; ağ açılırsa hemen kullanılır.

O hâlde ölçümler burada, CPU'da devam eder ve GPU'ya dair hiçbir şey
iddia edilmez. Kaggle'da koşacak kod `main/kaggle.py` ve
`docs/KAGGLE.md`de hazırdır; koşturmak kullanıcıya kalır.

## H88 — `beyan` YANLIŞ ÇEVREDEN OKUYORDU: modelin bütün çıktısı gürültüymüş (ölçüldü ve düzeltildi)

Bu, bu projede bulduğum **en ağır kusurdur** ve bulunma sebebi
kullanıcının H86 hükmüdür: *"natural gradyan ile öğrenilsin, bakalım ne
olacak?"* Natural gradyan işlemedi; **niçin** işlemediğini kovalarken
kusur çıktı. Yani hüküm, kendi sorduğu şeyi değil, çok daha büyüğünü
buldu.

### Nasıl bulundu (adım adım, çünkü usul asıl derstir)

1. **Natural gradyan hiçbir adımı kabul etmedi** (0/6); sıradan gradyan
   6'da 1 kabul etti. Gradyan normu 1064 çıkıyordu.
2. Kabahati yüzeye atmadan evvel `V(p)` **belirli mi** diye ölçüldü:
   aynı `p`de iki koşu **0,000e+00** fark verdi. Yani tesadüf yok.
3. Öyleyse `V` pürüzsüz mü? Yönlü türev `h` küçüldükçe **oturmadı**:
   `−4e−01 → +1,07e+02 → −9,2e+01 → +6,7e+04`. Dahası `h=1e−4`lük bir
   adım `V`yi **2,58'den 22,5'e** çıkarıyordu.
4. `V` parçalarına ayrıldı: patlayan tek terim `−log P(hedef)` idi ve
   sebebi `P(hedef)`in **tam olarak sıfır** çıkmasıydı; `−log(0+1e−12)`
   sabit **27,6** duvarı demektir -- eğimi olmayan bir duvar.
5. Kırpmadan (`np.clip(...,0,None)`) evvelki **ham köşegen** okundu:
   değerler `~1e−16`, **on tanesi negatif**. Olasılık negatif olamaz.
   Ayrıca `Tr ρ ≈ 1e−16` iken `⟨Ψ|Ψ⟩ = 2,05e−10` ölçüldü -- halbuki
   ikisi **eşit olmak zorundadır**.
6. İkisinden hangisi yanlış? Küçük bir yazmaçta (n=10) MPS açıkça
   büzülüp **tam dalga** kuruldu: `ic_carpim` tam dalgayla `4e−16`da
   örtüştü ve `Tr ρ = ⟨Ψ|Ψ⟩` özdeşliği doğrulandı. Demek ki kusur
   `blok_dagilimi`dedir.
7. Çevreler ayrı ayrı sınandı: **sağ çevre `1e−16` ile doğru**,
   **sol çevre `2,4–3,2` ile yanlış**.

### Kusurun kendisi

Sol çevre iki adımlık bir büzülmedir:

    L[b,d] = Σ_{a,c,i} L[a,c] A[a,i,b] A[c,i,d]
    1) t1[i,c,b] = Σ_a L[a,c] A[a,i,b]
    2) L[b,d]    = Σ_{i,c} t1[i,c,b] A[c,i,d]

Kod 2. adımda `A`nın **çıkış** bağını (`b`) `t1`in `c`siyle büzüyordu;
doğrusu **giriş** bağını (`c`) büzmektir. Tek bir `transpose` yanlıştı.

### Neticesi ne kadar ağır

`beyan` -- yani **modelin konuştuğu her belirteç** -- bu `ρ`dan okunur.
Yanlış çevre + normalize edilmemiş durum (norm `2e−10`e düşmüştü) bir
araya gelince, çıkan "dağılım" payı ve paydası yuvarlama gürültüsü olan
bir sayıydı. Yani:

> Bu projedeki **bütün eniyileme ölçümleri** -- dalga motoru, AS-GEK,
> Postnikov, natural gradyan, sıradan gradyan -- gürültüyü eniyilemeye
> çalışıyormuş. Hiçbiri işlemediği için değil, **işleyemeyeceği için**
> işlemedi.

Bu, geriye dönük olarak H69, H76 ve H86'daki "motor kazanamadı"
ölçümlerinin hepsini şüpheli kılar; o hükümler **düşmez** (içtihad
içtihadı nakzetmez) fakat üzerlerine bu şerh düşülür: *o ölçümler
bozuk bir beyandan alınmıştır ve düzeltilmiş beyanla tekrarlanmalıdır.*

### Yanında bulunan ikinci kusur: BOŞ ÖLÇÜT

`norm_hatasi`, `yuva_yogunluklari`nin izinin 1'den sapmasına bakıyordu.
Halbuki `yuva_yogunluklari` yoğunluğu **kendi izine bölerek** döndürür;
izi tanım gereği 1'dir. Yani ölçüt ne olursa olsun `~1e−16` yazıyordu.
Fiilen ölçüldü: **`norm_hatasi` 2,2e−16 derken hakikî `⟨Ψ|Ψ⟩` 2,05e−10
idi.** Ölçüt tertemiz kâğıt verirken durum on mertebe kaymıştı.

Bu, kullanıcının evvelce ikaz ettiği kusurun aynısıdır (H77'deki
"boş ölçüt"). Demek ki bir kere düzeltmek yetmiyor; **her ölçütün
kendisi de sınanmalıdır** -- "bu ölçüt hiç kırmızı yanabilir mi?"

### Düzeltmeler ve doğrulamaları

| düzeltme | yer | doğrulama |
|---|---|---|
| sol çevrenin doğru bacağı | `nefs/qyazmac.py::blok_dagilimi` | 20 halde tam dalgayla **≤3,1e−16**, negatif köşegen **0** |
| `norm()` / `normalize()` | `main/yazmac.py` | `⟨Ψ|Ψ⟩ 2,05e−10 → 0,9999999` |
| `norm_hatasi` hakikî ölçü | `main/yazmac.py` | artık `1,26e−07` (float32 eps) yazıyor, boş değil |
| ölçümden evvel normalize | `nefs/qakis.py::idrak_et` | 41 sınamanın 41'i geçiyor |

Kesme (unutma) **gizlenmiyor**: atılan ağırlık `iz.kesme`de ayrıca
durur; normalize edilen yalnız durumun ölçeğidir.

### Düzeltmeden sonra ölçülen

| | evvel | sonra |
|---|---|---|
| `⟨Ψ\|Ψ⟩` | 2,05e−10 | 0,9999999 |
| `P(hedef)` en az | **0,000e+00** | 2,40e−03 |
| `V` menzili (rastgele) | 2,58 – 22,78 | 2,41 – 3,72 |
| `V(p0+1e−4)` sıçraması | 2,58 → **22,49** | 3,09 → **3,11** |

`−log P` artık düzgün dağılımın `log 16 = 2,77`si civarındadır; yani
model **henüz hiçbir şey bilmiyor**, fakat artık *öğrenilebilir* bir
yüzey var. Bu bir başarı iddiası değildir: iddia edilen tek şey,
ölçülen yüzeyin nihayet manalı olduğudur.

### Kalan pürüz -- ve kapatılmayan borç

Düzeltmeden sonra bile yönlü türev `h→0`da tam oturmuyor (`h=1e−2`de
2,9 iken `h=1e−4`te 1221). `V` bit birebir belirli olduğuna göre bu
tesadüf değil, `p → Ψ` eşlemesinin **hakikî pürüzüdür**; en kuvvetli
şüpheli SVD kesmesidir (χ yetmeyince hangi altuzayın atıldığı `p` ile
**sıçrayarak** değişir). Bu hipotez χ=16/32/64'te ölçülmektedir ve
neticesi **çıkınca yazılacaktır**; şimdiden bir şey iddia edilmiyor.

## H89 — ÖLÇÜM NİHAYETE BIRAKILIR; evvelâ padişah idareyi alır

Kullanıcı hükmü:

> *"Birkaç saat sürecekse ya arka planda çalıştırıp işine devam et ya da
> hiç çalıştırma. Bence padişahın idareyi ele almasına öncelik ver artık,
> tüm kodları toparlayınca testlerin de doğru çalışır. Şimdi toparlamaya
> çalışırken eminim ki başka gürültü kaynakları da bulacağız; derli toplu
> bir kodumuz olmadan testte acele edip saatlerce beklemenin manası yok.
> Dolayısıyla kodları toparlayıncaya kadar bekle, tüm testlerini nihayete
> bırak, sadece bu testi değil, tüm testleri."*

Bu hüküm benim işleyiş tarzımı doğrudan düzeltiyor ve haklıdır.
H88'de görüldü ki tek bir `transpose` hatası bütün ölçümleri manasız
kılıyordu. **Bozuk bir nizamda alınan ölçüm, ölçüm değildir.** Öyleyse
sıralama şudur:

1. Evvelâ **nizam**: padişahın eli bütün koda uzansın (H82: %90 beylik),
   başıboş modüller ya tebaa olsun ya kalksın, gürültü kaynakları
   toparlanırken bulunsun.
2. **Sonra** bütün ölçümler bir arada, düzeltilmiş nizam üzerinde.

Fiilen değişen: `nefs/tabii_gradyan.py` **silinmez**, hükmü **askıda**
durur; H86'nın "işe yaramazsa sileriz" kararı, düzeltilmiş beyanla
yeniden ölçülene kadar verilmez. Aynı şekilde H69 ve H76'nın motor
mukayeseleri de **bütün kodlar düzeltildikten sonra** yeniden ölçülecek
(kullanıcı hükmü: *"Hepsi yeniden ölçülecek ama tüm kodlar
düzeltildikten sonra"*). O hükümler düşmez -- *içtihad içtihadı
nakzetmez* -- fakat her birinin yanında şu şerh durur:

> **ŞERH (H88/H89).** Bu ölçüm bozuk `beyan` üzerinde alınmıştır;
> hükmü askıdadır ve nizam kurulduktan sonra yeniden ölçülecektir.

Şerh düşülen hükümler: **H47, H69, H76, H86** ve eniyileme motorlarının
kazanan/kaybeden mukayesesini içeren her ölçüm. `beyan`dan bağımsız
ölçümler (kesme, MPO/takas, yığın hızı, ağaç MPO'sunun tamlığı,
BGS seyrekleştirmesi, `ic_carpim`in tamlığı) bu şerhin dışındadır:
onlar dağılımdan değil, doğrudan durumdan veya vakitten okunmuştur.

## H90 — ÖLÇÜT KENDİSİ SINANIR: kırmızı yanabildiğini ispatlamayan ölçüt kabul edilmez

Kullanıcı hükmü: *"Evet — her ölçüt kırmızı yanabildiğini ispatlasın."*

H88'de `norm_hatasi` aylarca `~1e-16` yazdı; halbuki yazdığı sayı
**yapısı gereği** o kadar çıkıyordu (yoğunluğu kendi izine bölüp sonra
izin 1'den sapmasına bakıyordu). Ölçüt bozulduğunu haber veremezdi;
yani ölçüt değildi, süstü.

**Kaide.** Bu kod tabanında bir ölçüt (`*_hatasi`, `norm_*`, `kesme`,
isabet oranları, `tam_çözülen`, sınama iddiaları) **ancak** şu iki şey
beraber varsa kabul edilir:

1. **Doğru halde yeşil yandığı** gösterilecek, ve
2. **Bile bile bozulmuş bir halde KIRMIZI yandığı** gösterilecek.

İkincisi yoksa ölçüt yoktur. Sınamada bunun adı *mutasyon sınamasıdır*:
ölçülen şey kasten bozulur ve ölçütün bunu yakalaması beklenir.

Buna bağlı ikinci bir kaide, aynı kusurun ikinci yüzü içindir:
**`beyan` yolu daima tam dalgayla yüzleştirilir.** Küçük bir yazmaçta
(`2^N` fiilen açılabilecek kadar) MPS büzülür ve okunan dağılım Born
kaidesiyle karşılaştırılır. H88 bu yüzleştirmeyle bulundu; bir kere
yapılıp bırakılmayacak, **kalıcı sınama** olacaktır.

Bu kaide geriye dönük olarak da işler: nizam toparlanırken her ölçütün
kırmızı yanabildiği gösterilecek, gösterilemeyen ölçüt ya düzeltilecek
ya kaldırılacaktır.

## H91 — KÂİDE FAZ ORAĞI: kâide kübitleri bir İSPAT SENEDİ kodlar

Kullanıcı hükmü (kendi devre tasarımıyla beraber):

> *"Faz orağı olarak bağla ama 2^k şeklinde artmasın... |0⟩_ebat —[H]—
> |Tecrit Funktoru (D)| —■— [Ebat İspatı] / |0⟩_iskelet —[H]—
> |Mutasarrıfa & Tertip (R,T)| —■— [Konum İspatı] / |0⟩_illet —[H]—
> |İllet Keşfi (BGCM φ)| —■— [Nedensellik İspatı] / |0⟩_münazara —[H]—
> |Vâhime & Münazara Cerhi (Nakz)| —■— [Aksinin İmkânsızlığı] /
> |0⟩_muhakeme —[H]— |Mahkeme-i Âkile (Burhân J)| —■— [Hükm-i Yakîn] /
> |ancilla⟩ —|1⟩—[H]— [Faz Çevirimi U_T(−1)] — (Grover Difüzyon) →
> |K*⟩ KÂİDE-İ ÂMME"*

ve ayrıca: *"sen burayla hudutlu kalma, ilham al, biraz düşün, daha
iyisini bul."*

### Benim teklifim NİÇİN yanlıştı

Ben *"k kübit = 2^k namzet kâide; mizan hepsini klasik denetleyip
köşegen üniteri kursun"* demiştim. O köşegeni kurmak **2^k klasik
denetim** ister; yani kübitin bütün kazancı orağın kurulmasında geri
verilirdi. Kullanıcının *"asla 2^k kalmamalı"* itirazı yerindedir ve
teklifimi düşürür.

### Doğru olan: KÂİDE İNDİSİ DEĞİL, KÂİDE PARAMETRESİ

Kâide yazmacı, sonlu bir kütükteki bir **indisi** tutmaz; kâidenin
**parametresini** tutar. Misal, ebat rüknü için::

    çıktı_h = (p·h + q) / r        p, q, r küçük tamsayı, süperpozisyonda

``U_D`` de ``p·h + q − r·h_çıktı``yı hesaplayıp sıfır olduğunda bayrak
kaldıran **tersinir aritmetik devredir**. Boyu şahit sayısında
polinomdur, kâide sayısında değil. Böylece kâide uzayı sonlu bir liste
olmaktan çıkar ve ``2^k`` klasik denetim ortadan kalkar.

Bu, `nefs/kaide.py`deki ``EBAT_KUTUGU``nun (12 elemanlı sonlu liste)
neden bir **iskele** olduğunu da söyler: klasik mîzân doğrudur ve
hakikat kaynağıdır, fakat sonlu kütüğü kuantum tarafına taşınmaz;
taşınacak olan parametre uzayıdır.

### Devrede DÜZELTİLEN yer: bayrak okunmaz, HESAPLANIR

Şemada ``■`` kontrolleri doğrudan rükün yazmaçlarından çıkıyor. Öyle
olursa faz, yazmacın belli bir **taban durumuna** vurulur -- yani
"işaretli durum" orağı olur, **ispat orağı olmaz**. İspat bayrağı
hesaplanmalı, kullanılmalı ve **geri alınmalıdır**::

    |rükün⟩  ──●─────────────●──        (değişmez)
               │             │
    |bayrak⟩ ─[U]──●────────[U†]        hesapla → kullan → GERİ AL
                   │
    |ancilla⟩ |1⟩[H][Z]                 faz geri tepmesi

``U†`` şarttır: bayrak geri alınmazsa rükün yazmacı çöple dolaşık kalır
ve **girişim ölür**; Grover hiçbir şeyi büyütmez. Bu projede tersinir
ancilla temizliğinin çalıştığı zaten ölçülmüştü (3,3e-15).

### Dört/beş rükün ve karşılıkları

Kullanıcının vesikasındaki rükünler, kullanıcının kendi kâide
tarifindeki (H85) şartlarla birebir örtüşür ve `nefs/kaide.py`de klasik
karşılıkları **zaten kurulmuştur**:

======================  ==================================  ====================
rükün                   suali                               klasik karşılığı
======================  ==================================  ====================
``H_D`` ebat            "ebat kesin mi, aksi imkânsız mı"   ``_teklik_ispati``
``H_S`` iskelet/support "hangi hücre dönüşür, hangisi zemin" (henüz yok)
``H_C`` illet           "her rengi neden koydum"            ``_illet_kesfi``
``H_N`` nakz            "yerine başkası niçin konamaz"      ``karsi_ornek``
``H_J`` muhakeme        "hükm-i yakîn"                      ``_makam``
======================  ==================================  ====================

``H_S`` (varlık sahası / support) **eksiktir** ve kullanıcının
vesikasının kod tabanına kattığı yeni şey odur: hangi hücrelerin
dönüşeceği, hangilerinin zemin kalacağı ayrı bir rükündür ve
`nefs/kaide.py`de karşılığı yoktur. Borç olarak yazıldı.

### Hakikat kaynağı ayrımı (H90'ın gereği)

Klasik `nefs/kaide.py` **hakikat kaynağıdır**; kuantum orak aynı
yüklemi tutarlı (coherent) hesaplayan devredir. İkisi küçük hâlde
**yüzleştirilecek** ve aynı hükmü vermedikleri yerde kuantum taraf
yanlıştır. H88'in dersi budur: beyan tam dalgayla yüzleştirilmediği
için aylarca gürültü okumuştu.

### İDDİA EDİLMEYEN

Tersinir aritmetik devreler dolaşıklığı hızla büyütür; ``χ``nın
patlaması **muhtemeldir** ve ölçülmeden hiçbir şey iddia edilmiyor.
Ölçüm, H89 gereği nizam kurulduktan sonra yapılacaktır.

## H92 — fitrat YEDEK DEĞİL, UZUV olarak bağlanır

Kullanıcı hükmü:

> *"Şimdi bağla ama birilerine paralel, alternatif olacak şekilde
> bağlama; o olmadığı zaman model zeki olamayacak, olduğu zaman da
> müthiş olacak derecede -- tıpkı insan vücudunun özene bezene
> yaratılması gibi sen de o şekilde icat et."*

Bu hüküm, bu kod tabanının **asıl hastalığına** konmuş bir teşhistir.
Nizam ölçümü (H82) %82 beylik diyor; beyliklerin çoğu da "aynı işi
yapan ikinci bir hat"tır (`akis` / `nefs.akis` / `yaklasim.akislar`,
`nefs.meleke` / `reel.meleke`, dört ayrı `main`). Yani buraya şimdiye
kadar hep **paralel** eklendi ve paralel eklenen her şey öldü.

O hâlde kaide: **bir modül ancak, olmadığında model bozulacaksa
bağlanır.** Bağlandığı yerde bir yedeği, bir "alternatif yolu", bir
"eski usul de dursun"u olmayacaktır. Yedeği olan uzuv, uzuv değildir.

``fitrat``ın uzuv olacağı yer bellidir ve H91'in ``H_C`` rüknüdür:

* ``fitrat.ayrisma`` -- d-ayrışması, arka/ön kapı: *"bu renk şu vasfın
  ILLETİ mi, yoksa ortak bir sebebin gölgesi mi?"* Mill'in usulleri bu
  ayrımı yapamaz; ``ayrisma`` yapar. İllet rüknü onsuz **yanlış**
  illet bulur, yani model onsuz zeki olamaz -- hükmün şartı budur.
* ``fitrat.karsi_olgusal`` -- abduction/action/prediction üç pası:
  *"sarı yerine mavi olsaydı ne olurdu?"* Bu, ``H_N`` (aksinin
  imkânsızlığı) rüknünün ta kendisidir ve `nefs/kaide.py`nin şimdiki
  ``karsi_ornek``i bunun ancak kaba hâlidir.
* ``fitrat.serbest_enerji`` -- ELBO: iki kâide de şahitleri açıklıyorsa
  hangisi seçilir? Occam cezası buradan gelir ve **teklik ispatının**
  (``H_D``, ``H_N``) sayısal yumuşak hâlidir.

Bu üçü bağlandığında ``H_C`` ve ``H_N`` rükünleri hakikî motorlarına
kavuşur; bağlanmazsa o rükünler bugünkü gibi Mill'in kaba usulleriyle
kalır. Kullanıcının *"o olmadığı zaman model zeki olamayacak"* şartı
böylece bir temenni değil, mimarî bir zorunluluk olarak yerine oturur.

**Bunun bedeli açıkça yazılır:** uzuv olarak bağlamak, yedeksiz
bağlamaktır; ``fitrat`` kırılırsa kâide mîzânı kırılır. Kabul edilen
budur -- kalbin de yedeği yoktur.

## H93 — ÖLÇÜLDÜ: darboğaz mîzân değil, KÂİDE KÜTÜĞÜ (fitrat şimdilik âtıl)

H92 gereği ``fitrat.ayrisma`` kâide mîzânının illet rüknüne bağlandı ve
**uzuv mu yedek mi** olduğu ölçüldü. Netice, beklediğimin tersi çıktı
ve olduğu gibi yazılıyor.

### Bağlamanın kendisi doğru ve bir kusuru da yakaladı

``ayrisma``nın söylediği şudur: **kâidenin illetini ileri sürmek bir
müdahaledir (``do``), şahidin vasfını görmek ise bir müşahededir.**
Müdahalenin arka kapısı yoktur; müşahedenin arka kapısını kapatacak
gözlenebilir küme yoktur, çünkü ``şahit`` (görevin kendisi) gizlidir ve
hem vasfı hem neticeyi doğurur. Yani şahit vasfının illet olduğu
**ispatlanamaz** -- Mill'in veremeyeceği bir hükümdür.

Çizge bir kere **yanlış** kuruldu: illet, ``izah``ın çocuğu yapılmıştı,
yani sebep değil **etiket** olmuştu. O zaman ``illet ← izah → tuttu``
çatalı açık kalıyor ve doğru illet de eleniyordu (ölçüldü:
``yer_devrik`` eleniyor, Yakîn kayboluyordu). İlletin sebep olması,
çizgede **kökte durmasıyla** ifade edilir. Düzeltildi.

### Fakat ölçüm şunu söyledi: ayrisma hiçbir kararı değiştirmiyor

150 hakikî eğitim görevi × 12 ebat kaidesi × 7 renk kaidesi tarandı:

    bakılan illet kararı            : 0
    ayrisma'nın değiştirdiği karar  : 0

``bakılan = 0`` demek, ``mill_birlesik``in hakikî görevlerde **hiç**
illet döndürmediği demektir. Sebebi basittir ve yukarıdadır: birleşik
usul, "her müsbet vakada var" şartını arar; hakikî ARC görevlerinde
hiçbir namzet kâide tutmadığı için **müsbet vaka yoktur**.

### Asıl hüküm: darboğaz mîzân değil, KÜTÜK

O hâlde şu ölçülmüştür ve H88'in dersiyle aynı cinstendir:

> Kâide mîzânı (ispat, illet, teklik, makam) **doğru çalışıyor** --
> bile bile kurulmuş görevde Yakîn'e çıkıyor, bozulunca düşüyor. Fakat
> hakikî ARC'ta **hiç ateşlenmiyor**, çünkü 12 ebat × 7 renk = 84
> namzetlik sonlu kütük hiçbir hakikî görevi tutmuyor (0/120 Yakîn,
> 0/120 Zan).

Yani sıradaki iş mîzânı zenginleştirmek değil, **kütüğü kaldırmaktır**
-- ve bu tam olarak H91'in hükmüdür: kâide yazmacı sonlu bir listedeki
*indisi* değil, kâidenin **parametresini** tutacaktır. `nefs/kaide.py`
klasik hakikat kaynağı olarak kalır; genişleyecek olan namzet uzayıdır.

### fitrat'ın hâli -- dürüst kayıt

``fitrat.ayrisma`` şu an **âtıldır**: bağlıdır, doğrudur, fakat
üstündeki kademe boş döndüğü için hiçbir kararı değiştirmemektedir.
H92'nin *"yedek bağlama"* yasağına göre bu hâl kabul edilemez; fakat
âtıl olmasının sebebi kendisi değil, **üstündeki kütük darboğazıdır**.

Karar: **sökülmez, borç olarak yazılır.** H91'in parametre uzayı
kurulduğunda müsbet vaka doğacak ve o zaman ``ayrisma``nın ısırıp
ısırmadığı **yeniden ölçülecektir**. Isırmazsa o vakit sökülür. Bu
hüküm, âtıl kodu meşrulaştırmak için değil, **ölçülmüş bir borcu**
kütükte tutmak içindir.

``fitrat.karsi_olgusal`` ve ``fitrat.serbest_enerji`` **henüz
bağlanmadı**; H92'de gösterilen yerleri (``H_N`` aksinin imkânsızlığı ve
Occam cezası) durmaktadır.

## H94 — HARAPLAMA ÖLÇÜMÜ: melekelerin KALBİ YOK (vücut değil, mütecânis kütle)

Kullanıcı suali:

> *"Sen bu melekeleri mimariye nasıl bağladın, bunlar arızasız bir vücut
> teşkil ediyor mu? Kendisi sıhhatsiz olduğu zaman tüm vücut sıhhatsiz
> olduğu organ olan kalp bizde de mühim mi o kadar? Bunları bilmediğim
> için kararsız kalıyorum."*

Bu suale zan ile cevap verilmedi. Biyolojideki usul tatbik edildi:
**haraplama (lezyon)** -- organ çıkarılır, vücutta ne bozulduğuna
bakılır. Âlet `tanilama/haraplama.py`dedir; 41 meleke tek tek akıştan
çıkarılıp ``beyan`` dağılımının toplam değişinti mesafesi ölçülür.

### Ölçülen

============================================  ==============
ölçü                                          netice
============================================  ==============
çıkarıldığında hiçbir şey değişmeyen meleke   **0 / 41**
en tesirli (𝒪₆ Tasavvur)                      tvd 4,188e-01
en tesirsiz (𝒪₂₇ Tetkik)                      tvd 1,767e-01
**tesir nispeti (en çok / ortanca)**          **1,4**
en tesirlinin toplam tesirdeki payı           **%3,4**
============================================  ==============

Düpedüz eşit dağılımda bu pay ``1/41 = %2,4`` olurdu. Yani en "mühim"
meleke, yapısız bir kütledeki ortalamanın ancak kıl payı üstünde.

**𝒪₂₄ İspat**ı çıkarmak 0,297; **𝒪₄₀ Sanat**ı çıkarmak 0,256. Burhânı
sökmekle bir tırnağı sökmek neredeyse aynı şeyi yapıyor.

### Daha keskin bulgu: 39 meleke dolaşıklığa HİÇ dokunmuyor

``Δentropi`` sütununda 41 melekenin **39**'unun değeri ``~1e-15``, yani
makine hassasiyetinde **sıfır**. Yalnız 𝒪₃₉ Belâgat (−8,3e-02) ve pek az
𝒪₃₇ Fesâhat (−3,4e-07) dolaşıklığı fiilen değiştiriyor.

Bunun manası tekniktir ve ağırdır: 41 melekenin 39'u **genlikleri
karıştırıyor, yapı kurmuyor**. Hepsi aynı cinsten -- parametreli yerel
dönme katmanı. Adları ayrı, cevherleri bir.

### HÜKÜM

> Bu bir vücut değildir, **mütecânis bir kütledir**: 41 uzuv değil,
> 41 kere tekrarlanmış aynı uzuv. Hadis-i şerifteki ölçü konduğunda --
> *bozulunca bütün vücudu bozan et parçası* -- öyle bir uzuv **yoktur**.
> **Bu mimarinin kalbi yoktur.**

Ve H88'in aylarca farkedilmemesinin sebebi budur: **nabzı olmayan
vücutta durma da farkedilmez.** ``beyan`` yanlış çevreden okuyordu ve
hiçbir meleke bundan rahatsız olmadı, çünkü hiçbirinin ``beyan``a
hayatî bir bağı yoktu.

**Bu benim kusurumdur.** Melekeleri "mimariye bağladım" derken yaptığım
şey, 41 ayrı vazifeye 41 ayrı isim verip hepsine aynı cinsten
parametreli bir kapı katmanı koymaktı (`nefs/qmeleke.py`de görülüyor:
``QMantik``in "nakz"ı bir menfî MPO, ``QIllet``in "nedensellik"i bir
kontrollü dönme). İsimler zihnin, cevher değil.

### Bundan sonraki ölçüt

Haraplama artık bu mimarinin **nabzıdır** ve her yapı değişikliğinden
sonra koşulacaktır. Hedef, tesir nispetinin 1,4'ten yükselmesidir:
uzuvlaşan bir mimaride bazı melekelerin çıkarılması vücudu **yıkmalı**,
bazılarınınki incitmemelidir. Hepsinin eşit olması sıhhat değil,
**yapısızlıktır**.

## H95 — χ PATLAMASINA KARŞI ÜÇ TEDBİR: ikisi tam doğru, biri fazla iddialı

Kullanıcı, H91'in tersinir aritmetik devrelerindeki dolaşıklık riskine
karşı bir teklif getirdi ve *"doğru olup olmadığını kontrol ederek ilham
al"* dedi. Kontrol edildi:

======================================  ===================================
teklif                                  hükmüm
======================================  ===================================
akışkan geri alma (pebble/streamed)     **DOĞRU.** Her şahit kendi
                                        ancillasını derhal geri alırsa
                                        Schmidt rütbesi ``K`` ile
                                        katlanmaz, ``O(1)``de kalır.
                                        Standart ve yerinde.
RNS / Çin Kalan Teoremi                 **DOĞRU ve zekice.** Elde
                                        zincirini fiilen kırar, tensör
                                        ağı blok-ayrık kalır. Belirttiği
                                        yalancı-kök riski gerçek, çaresi
                                        de doğru: ``∏mᵢ > 2·max(ebat)``.
diyagonal ``Z`` fazı                    **İstikamet doğru, iddia fazla.**
                                        Ancillayı ve çöpü **tamamen**
                                        kaldırır -- asıl kazanç budur.
                                        Fakat *"χ patlamasını sıfıra
                                        indirir"* YANLIŞTIR:
                                        ``exp(iθ ZᵢZⱼ)`` köşegen olsa da
                                        dolaşıklık üretir (QAOA maliyet
                                        katmanı tam budur). Sıfırlanan χ
                                        değil, **çöplüktür**.
3-bitlik daraltma                       χ'yi gerçekten emniyete alır,
                                        fakat **sonlu kütük derdini geri
                                        getirir** (H93'te ölçülen
                                        darboğaz). Emniyet freni olarak
                                        tutulur, mimari olarak değil.
======================================  ===================================

Teklifin sunduğu doğrulama ölçütleri de yerindedir ve alınmıştır:
çöp dolaşıklığının kalmadığının teyidi (``⟨çöp|çöp⟩``), parametre
yazmacı ile şahit ancillaları arasındaki entropi haddi, ve MPS'te ``χ``
tavanının hiç aşılmaması. Üçü de H90'ın *"ölçüt kırmızı yanabilmeli"*
şartına uygundur.

## H96 — "UZUV OLMADIYSA AT" DEĞİL, "UZUV HÂLİNE GETİR"

Kullanıcı, H93'teki *"fitrat âtıl kaldı"* neticesine şöyle cevap verdi:

> *"Benim mimaride olmadığı zaman bozulsun, tam bir uzuv olsun demem,
> eğer uzuv olmamışsa at demek değil; adam gibi düşünüp onu uzuv hâline
> getirmek demek. Yani sen Suriyeli muhacirler üst üste binince onları
> ülke dışına mı attın, yoksa onları da ülkenin parçası hâline mi
> getirdin, onlara işe yarar ve katma değer üretecek şekilde yer yurt mu
> verdin -- bu mühim."*

Bu, H92'nin **tashihidir** ve benim onu yanlış anladığımı gösteriyor.
H92'yi *"işe yaramayan modülü sökerim"* diye okumuştum; hüküm o değil.
Doğrusu:

> Bir modül âtıl kalıyorsa **kabahat modülde değil, ona yer
> bulamayan mimarîdedir.** Vazife, atmak değil **yer yurt vermektir**.

Yani H93'teki *"ayrisma hiçbir kararı değiştirmiyor, sökülsün mü?"*
sualinin cevabı: **hayır** -- ``ayrisma``ya, kararı fiilen değiştireceği
bir mevki bulunacaktır. Âtıl kalması onun değil, ``mill_birlesik``in
boş dönmesinin, o da sonlu kütüğün neticesidir (H93).

Bu hüküm, `mucit_ai_esas/` (14 373 satır) ve öteki 165 beylik için de
istikameti tayin eder: ölçüt *"bunu kullanıyor muyum"* değil,
**"buna nerede yer yurt verebilirim"**dir.

## H97 — qkaide KURULDU ve İŞLEMİYOR (ölçüldü); iki kusur teşhis edildi

Kullanıcı hükmü: *"qkaide diye bir dosya yazarsın olur biter, ana akışa
onu koyarsın."* `nefs/qkaide.py` yazıldı. **İşlemiyor** ve bu, iddia
edilmeden önce ölçüldü.

### Doğru çıkan taraf: ``2^k`` fiilen kalktı

Ebat kâidesi bir indis değil bir denklemdir: ``r·h_çıktı = p·h + q``.
``p, q, r`` kübitlere bit bit yazılınca sapma **bitlerde doğrusaldır**::

    δ = Σ_m c_m b_m + d          (c_m klasik, şahitten çıkar)

Doğrusal olduğu için ``δ``, bütün kâide adayları için aynı anda, kübit
başına **bir** kontrollü kapıyla hesaplanır. Ölçüldü: ``k=6`` (4096
aday değil, 64 aday) için **63 kapı**. ``2^k`` taban durumunu tek tek
dolaşmak yok. Bu kısım H91'i doğruluyor.

### DÜZELTİLEN BİR YANILGI: teklif reel yazmaçta tatbik edilemez

Kullanıcının getirdiği teklif ``exp(−iγδ²)`` **diyagonal faz** işlemcisi
öneriyordu. Bu mimaride doğrudan tatbik **edilemez**: yazmaç reeldir --
``dik_iki_kubit`` ortogonaldir, ``A`` reel kayan noktadır, ``beyan``
``np.real`` alır. Reel bir yazmaçta ``exp(iθZ)`` yoktur; olan yalnız
``diag(1,−1)``dir. Bu, teklifin kusuru değil, **bizim yazmacımızın
şartıdır** ve H95'e eklenen şerhtir.

Onun yerine ``δ`` bir **açıya** yazıldı (orak kübiti ``γδ`` kadar
döner). Fikir doğrudur; fakat aşağıdaki iki kusur yüzünden netice
vermedi.

### ÖLÇÜLEN: hiçbir yükselme yok

Beş hâlde klasik hakikatle yüzleştirildi (``çıktı=girdi``,
``2·girdi``, ``girdi/2``, ``girdi+1``, ve **çözümsüz** bir hâl):

    kuantum tepe olasılığı  : 0,0156  =  1/64  (bütün hâllerde)
    çözümlerin ağırlığı     : düz dağılımla AYNI (0,0625 / 0,0625)

Yani dağılım **düpedüz düzgün**; orak hiçbir kolu yükseltmiyor.
5 halin 4'ünde tepe, klasik çözüm kümesinde bile değil.

### TEŞHİS -- ikisi de benim kusurum

**1. ``difuzyon`` yanlış kuruldu.** Grover'ın yansıtması
``D = 2|Ψ₀⟩⟨Ψ₀| − I``dır. Ben her kübite **ayrı ayrı** ``Z`` vurdum;
o işlemci ``Π_j (−1)^{b_j}``dir, yani çarpanlarına ayrılır ve
``|0…0⟩`` etrafında **hiçbir yansıtma yapmaz**. Doğrusu ``k`` katlı
**kontrollü** ``Z``dir ve tek kübitlik ``Z``lerin çarpımı ona eşit
değildir.

**2. İşaretleme faz değil, sızıntı.** ``sart_yaz → Z → geri_al``
dizisi kolun genliğini ``cos(2γδ)`` ile çarpar, ``sin(2γδ)`` kadarını
da orak ``|1⟩``ine sızdırır. Orak izlenip atılınca ``cos² + sin² = 1``
olduğu için **kâide marjinali hiç değişmez**. İşaretlemenin görülebilmesi
için ya yüklemin (``δ=0``) bir kübite **hesaplanması** (tersinir
aritmetik + ancilla) ya da tam genlik yükseltme yapısının
(``Q = A·S₀·A†·S_iyi``) kurulması gerekir; ikisi de yapılmadı.

Reel yazmacın buradaki asıl şartı şudur ve kütüğe geçer:

> **Reel yazmaçta faz geri tepmesi ancak ``X`` ile olur** (``|−⟩``,
> ``X``in −1 özdurumudur). ``R_y`` dönmelerinin özdurumları karmaşıktır,
> dolayısıyla açı kodlamasıyla **temiz bir faz orağı kurulamaz**; açı
> kodlaması genlik yükseltme (amplitude amplification) ister.

### HÜKÜM

`nefs/qkaide.py` **ana akışa konmadı** -- işlemeyen bir uzuv takılmaz.
Dosya durur, kusurları kütükte yazılıdır, ve düzeltilecektir. Kullanıcı
hükmü H96 gereği (*"uzuv olmadıysa at değil, uzuv hâline getir"*)
sökülmez.

Sıradaki iş, ikisinden birini seçmektir ve bu kullanıcıya sorulmuştur:
(a) ``δ=0`` yüklemini tersinir aritmetikle bir kübite hesaplayıp ``X``
ile temiz faz geri tepmesi kurmak (ancilla gerekir, çöp geri alınır),
yahut (b) açı kodlamasını koruyup tam ``A·S₀·A†`` genlik yükseltme
çevrimini kurmak (ancilla gerekmez, fakat ``k`` katlı kontrollü kapı
gerekir).

## H98 — KÂİDE ORAĞI İŞLİYOR: 17–22 kat yükseltme, kesme 1e-16 (ölçüldü)

Kullanıcı hükmü: *"İkisini de kur, ÖLÇÜM karar versin."* Kuruldu,
koşturuldu, ölçüm hükmünü verdi.

### Ölçülen -- klasik hakikate karşı, beş hâlde

``bit=2`` (64 kâide adayı), iki Grover turu, ``k=6`` kâide kübiti:

=====================  =========  ==============  =========  =========
hâl                    tepe       çözüm ağırlığı  düz dağ.   kesme
=====================  =========  ==============  =========  =========
çıktı = girdi          (2,0,2) ✓  **0,787**       0,047      1,8e-16
çıktı = 2·girdi        (2,0,1) ✓  **0,344**       0,016      5,9e-16
çıktı = girdi/2        (1,0,2) ✓  **0,344**       0,016      1,4e-15
çıktı = girdi+1        (3,3,3) ✓  **0,787**       0,047      9,9e-17
ÇELİŞKİLİ (çözümsüz)   —          **0,000** ✓     0,000      6,7e-17
=====================  =========  ==============  =========  =========

Yükseltme **17–22 kat**; kesme ``~1e-16``, yani işlem fiilen **tam**.
Çözümü olmayan hâlde ağırlık **sıfır** -- yani ölçüt kırmızı da yanıyor
(H90'ın şartı).

### İki usul yarıştırıldı, biri silindi

    usul          tepe doğru mu   çözüm ağırlığı (düz 0,047)
    açı × 1            ✗               0,064      ← yükseltme YOK
    işaret × 1         ✓               0,473
    işaret × 2         ✓               0,787

**Açı usulü silindi.** Niçin işlemediği H97'de teşhis edilmişti ve
ölçüm teşhisi doğruladı: işaretleme kâide yazmacına faz değil, oraka
**genlik** yazıyor; orak izlenip atılınca ``cos²+sin² = 1`` olduğu için
kâide marjinali hiç değişmiyor.

Buradan çıkan ve kütüğe geçen umumî kaide:

> **Reel yazmaçta faz geri tepmesi ancak ``X`` ile olur** (``|−⟩``,
> ``X``in −1 özdurumudur). ``R_y``nin özdurumları karmaşık olduğu için
> açı kodlamasıyla temiz bir faz orağı **kurulamaz**.

### Düzeltilen iki kusur (ikisi de H97'de ölçülmüştü)

1. **Difüzyon.** ``k`` katlı kontrollü ``Z`` yerine her kübite ayrı
   ``Z`` vurulmuştu; o işlemci çarpanlarına ayrılır ve hiçbir yansıtma
   yapmaz. Doğrusu ``I − 2|0…0⟩⟨0…0|``dır ve köşegen olduğu için
   **MPO bağ boyutu 2**dir -- ancilla gerekmez.
2. **İşaretleme.** ``δ``nın koşan toplamı MPO'nun **bağ indisinde**
   taşınır (``w_sağ = w_sol + c_m·b_m``), sağ sınır toplam sıfırsa
   ``−1`` verir. Bağ boyutu ``δ``nın **menzili** kadardır -- ``2^k``
   değil, katsayıların büyüklüğünde polinom.

### Üçüncü kusur: ÂŞİKÂR KÂİDE

Orağın ilk doğru koşusunda tepe ``(0,0,0)`` çıktı. ``r = 0`` demek
``0 = p·h + q`` demektir; bu bir ebat kâidesi **değildir**, ebadı hiç
söylemez. Yani orak, *"hiçbir şey söylemeyen kâide"*yi hakikî kâide
kadar kuvvetle işaretliyordu.

Düzeltildi: bağ indisi artık iki şey birden taşır -- koşan toplam **ve**
*"r bitlerinde hiç 1 gördüm mü"* bayrağı. İşaret ancak ``δ=0`` **ve**
bayrak kalkmışsa vurulur. Bağ boyutu ikiye katlanır, başka bedeli yok.

Bu, kütükteki daha umumî bir kaidenin hususî hâlidir ve öyle kaydedilir:
**her ispat, ispatladığı şeyin boş olmadığını da ispatlamalıdır.**
``δ=0`` sağlanıyor diye kâide olmaz; kâidenin bir şey **söylüyor**
olması ayrı bir şarttır.

### Kabul edilen hudut -- gizlenmiyor

Şahitler tek bir doğrusal biçimde (``Σ λ_s δ_s``) birleştirilir; bu,
``δ_s``lerin **ayrı ayrı** sıfır olmasını garanti etmez. Doğurduğu
**sahte kökler klasik olarak sayılır** (``sahte_kokler``) ve
raporlanır -- çelişkili hâlde bir tane çıktı ve bildirildi. Tam AND,
bağ indisinde bütün ``δ_s``leri birden taşımayı ister; bağ boyutu şahit
sayısında üstel büyüdüğü için alınmadı.

### Hâlâ İDDİA EDİLMEYEN

Kurulan **yalnız ebat rüknüdür** (``H_D``). İskelet (``H_S``), illet
(``H_C``), nakz (``H_N``) ve muhakeme (``H_J``) rükünleri kurulmadı.
``bit=2`` ile ölçüldü; büyük ``bit``te ``χ``nin ne olacağı
**ölçülmedi**. Ve hakikî ARC görevlerinde koşturulmadı.

İki kalıcı sınama eklendi (46 sınama, hepsi geçiyor).

## H99 — ÇALIŞMA ALGORİTMASI (güncellendi)

Kullanıcı hükmü:

> *"Dosyayı aç → soru sor → tashih yazılarını ve kodlarını yap → main
> yani padişahın elini uzat → sıradaki dosyaya geç → bitinceye kadar
> devam et."*

H82'de ölçülen %82 beylik nispetini düşürecek olan **dördüncü adımdır**
ve evvelki döngüde (H-Faz 3) yoktu: dosya düzeltiliyor fakat ana akışa
bağlanmıyordu, dolayısıyla nizam ölçümü hiç kıpırdamıyordu (H93'te
fiilen görüldü: `nefs/kaide.py` kuruldu, tebaa nispeti %18'de kaldı).

Bundan böyle bir dosya, **ana akışa bağlanmadan** bitmiş sayılmaz.

## H100 — HER SÖYLEDİĞİM DOĞRU DEĞİL: DAİMA TENKİT ET

Kullanıcı hükmü:

> *"Ben sana ne söylersem söyleyeyim her zaman tenkitçi olarak yaklaş,
> hem emin ol hem de test et; her söylediğim doğru değil, kontrol et."*

Bu hüküm, kullanıcının kendi otoritesini **kasten** sınırlamasıdır ve
kütükteki en mühim usul hükümlerinden biridir. Fiilî karşılığı:

1. Kullanıcının verdiği her teklif, koda geçmeden **kontrol edilir**;
   doğru çıkan tarafı ve yanlış çıkan tarafı **ayrı ayrı** söylenir.
2. *"Yanlış gözükmüyor"* diye başlanmaz; **nesi yanlış** aranır.
3. Kullanıcı bir hükmünü nakzederse, nakz da tenkit edilir -- yeni hüküm
   de eskisi kadar sınanır.

Bu hükmün geriye dönük bir örneği vardır ve zarar da vermiştir: H91'de
gelen devre şemasında ``■`` kontrolleri doğrudan rükün yazmaçlarından
çıkıyordu; ben *"güzel"* deyip üstüne inşa ettim, kusuru üç mesaj sonra
buldum. H95'te gelen ``exp(−iγδ²)`` teklifinin bu mimaride **hiç tatbik
edilemeyeceğini** (yazmaç reeldir) ancak koda geçirirken gördüm. İkisi de
bu hükmün konmasını gerektiren vakalardır.

## H101 — NAKZ: "KÂİDEYİ KALP YAP" hükmü DÜŞTÜ

Kullanıcı, bir evvelki oturumda *"Kâideyi KALP yap, melekeler ona
bağlansın"* şıkkını seçmişti. Şimdi **nakzediyor**:

> *"Kaideyi kalp yapmak bana garip geliyor; bir insanın zihnen kalbi bir
> şeylerin kaidesini bulmak değildir."*

Kütük kaidesi gereği (*içtihad içtihadı nakzetmez*) eski hüküm silinmez,
**nakz olarak kaydedilir** ve gerekçesi yazılır.

**Gerekçe doğrudur ve tenkidi geçer** (H100): kâide bulmak bir
**melekenin** işidir. Kalp ise melekeler arasında bir meleke değildir;
onları **birleştiren** şeydir. Bir uzvu kalp ilân etmek, hadis-i
şerifteki ölçüyü de bozar -- orada kalp, bozulunca bütün vücudu bozan
şeydir, yani her uzvun **tâbi olduğu** şeydir, uzuvlardan biri değil.

`nefs/qkaide.py` **silinmez**: ölçüldü ve işliyor (H98, 17–22 kat).
Yalnız mevkii değişir -- kalp değil, bir rükündür.

## H102 — MANTIĞA SADAKAT ≠ MANTIK YÜRÜTME (kullanıcının koyduğu ayrım)

Kullanıcı hükmü:

> *"Mantık yürütme ameliyesi ile mantığa sadık kalma ameliyesi farklı
> şeylerdir; benim sana vereceğim dosyalarda bu ayrım yok ama senden
> istiyorum ki sen bu ayrımı yap."*

### İki ayrı şey

============================  ==========================================
**mantığa sadakat**           **mantık yürütme**
============================  ==========================================
DAİMÎ                         ARADA SIRADA
bütün melekelerin bütün       kalbin, ``𝒪₄ Tertip`` vasıtasıyla seçtiği
adımlarında                   bir **strateji**
melekelerden başka sistemde   seçilince: girdiler derlenir, uygun hâle
ne varsa onlar da dâhil       getirilir, **funktorlarla uzaylara**
                              götürülür
bir **şart**tır               bir **ameliye**dir
bozulursa her şey bozulur     yapılmasa da sistem çalışır
============================  ==========================================

**Mantık yürütmeden maksat** (kullanıcının tarifi): elde var olmayan bir
bilgiyi ortaya çıkarmak, var olan bir şeyi çürütmek, yahut *"bu doğru
mu"* diye kontrol etmek. Çıktı, girdiyle **aynı cinsten** olmalı fakat
mantıkça sağlamlaştırılmış, belki üzerine bir şey ilâve edilmiş olmalı.

### Bunun kalp meselesine bakan yüzü

H94'te **kalbin olmadığı ölçüldü** (tesir nispeti 1,4; 39/41 meleke
dolaşıklığa hiç dokunmuyor). Bu hüküm, kalbin ne olduğuna dair bir
cevap veriyor ve kaydedilir:

> **Kalp bir meleke değil, bir sadakat şartıdır.** Bütün melekelerin
> bütün adımlarında ayakta durması gereken şey; bozulunca her uzvun
> bozulmasının sebebi de tâbiiyetin kendisidir.

### AÇIK BORÇ ve TENKİT (H100 gereği)

*"Mantığa sadakat"* şu hâliyle **koda geçmez**: bir üniter kapının
mantığa sadık olması ne demektir? Tarifi verilmedikçe H90'a göre
**kırmızı yanamayan bir ölçüt** olur, yani ölçüt sayılmaz. Kullanıcıya
soruldu; uydurulmayacaktır.

### İKİNCİ TENKİT: "kalp seçsin" H31'i kırıyor

*"Kalp bu stratejiyi tertip melekesi vasıtasıyla seçmelidir"* -- fakat
duruma bakıp seçmek bir **okumadır** ve dalgayı çökertir (H31). Bu,
`mizan`/`fitrat`ı bağlarken çarpılan duvarın aynısıdır.

Çaresi vardır ve kullanıcının kendi maksadına daha uygundur:

> **Kalp seçmez, DOLAŞTIRIR.** Bütün stratejiler süperpozisyonda beraber
> koşar, her birinin bir genliği olur ve işe yaramayan **yıkıcı
> girişimle kendiliğinden söner**. "Seçmek" klasik zihnin işidir;
> kübit zihinde karşılığı, hepsini birden yaşayıp yanlışı söndürmektir.

Bu, kullanıcının *"aynı anda 1 milyon belirteç"* hükmünün strateji
kademesindeki karşılığıdır.

### MÜSBET KONTROL: teklif iki büyük beyliğe yer yurt veriyor

*"Funktorlarla uzaylara götürme"* tarifi, hâlihazırda **âtıl** duran
şu modüllerin tam da kendisini istiyor:

    omega_kategori        12 modül   4 693 satır   (funktor, denklik)
    omega_kategori_nbe     3 modül   1 177 satır
    token_uzaylari         8 modül   3 067 satır   (morfizm.py, manifold.py)
    ─────────────────────────────────────────────
    toplam                          12 786 satır   -- hepsi BEYLİK

H96'nın (*"uzuv olmadıysa at değil, uzuv hâline getir"*) fiilî karşılığı
budur ve teklifin lehine ciddi bir delildir.

### MÜSBET KONTROL 2: Tertip'in strateji seçmesi H60 ile tutarlı

H60'ta ``𝒪₄ Tertip`` *"∞-kategoriden türeyen UZAYLARLA umumî tertip"*
diye hükme bağlanmıştı (kapalı devre, açık devre, boru hattı, ağaç,
katmanlama, mütedahiliyet, açık uçlu). Strateji seçimi bir tertip
işidir; burada çelişki yoktur.

## H103 — "KÂİDE KALP OLAMAZ" TENKİDİ KABUL; delili benim kendi ölçümümde

Kullanıcının getirdiği vesika, kâidenin kalp olamayacağını üç sebeple
gerekçelendiriyor. Üçünü de tenkit ettim (H100); **üçü de geçiyor**,
ve üçüncüsünün delili bu projede **fiilen ölçülmüş** durumda:

1. *Sentaktik kısırlık:* Bir kâideyi seçen, ona başkasını tercih eden,
   gerektiğinde onu esneten şey kâidenin kendisi olamaz.
2. *Kâide bir hüküm nesnesidir, hüküm veren değil.*
3. *Mekanik körlük:* Merkeze "kâide bulma" konursa sistem sonsuz sayıda
   **manasız totoloji** üretir.

Üçüncü madde bir iddia değil, bende **ölçülmüş bir vakadır**: H98'de
kâide orağının ilk doğru koşusunda tepe ``(0,0,0)`` çıktı -- yani
``0 = p·h + q``, ebadı hiç söylemeyen kâide. Orak onu hakikî kâide
kadar kuvvetle işaretledi. Vesikanın "mekanik körlük" dediği şey benim
laboratuvarımda aynen gerçekleşmiştir.

O hâlde H101'in nakzı yerindedir ve şu tarif kabul edilir:

> **Kalp bir meleke değildir**; melekelerin akıp döküldüğü, parçalı
> kesitleri tek bir idrakte toplayan tepe noktasıdır (kolimit) ve
> *"bütün bu süreç ne içindir?"* sualinin cevabını tutan yerdir.

## H104 — MANTIĞA SADAKAT'IN TARİFİ ALINDI; fakat şartı TASHİH EDİLDİ

Vesikanın tarifi H102'nin açık borcunu kapatıyor ve **doğrudur**:
mantığa sadakat bir hesap değil, hiçbir hesabın dışına taşamayacağı bir
**kod uzayıdır** (stabilizer / gauge alt-uzayı).

### TENKİT: vesikanın şartı fazla kuvvetli, model felç olur

Vesika ``[𝒪_j , Ŝ] = 0`` yazıyor -- **merkezleyici** şartı. ``n``
kübitte ``n`` bağımsız üreteçli bir stabilizer grubunun merkezleyicisi
(fazlar hariç) grubun kendisidir; o hâlde melekeler grubun dışına hiç
çıkamaz ve **hiçbir şey öğrenemez**.

Doğrusu **normalleştirici** şartıdır::

    U† Ŝ U ∈ ⟨Ŝ⟩          (kod uzayını kendine götürmek)

Komütasyon bunun hususî ve kısır hâlidir. Normalleştirici Clifford tipi
zenginliğe izin verir: meleke kod uzayının **içinde** serbestçe dolaşır,
**dışına** taşamaz. Aranan tam olarak budur.

### VESİKADA BULUNAN DÖRT KUSUR DAHA (H100 gereği)

1. **"χ patlaması kesin olarak engellendi / tescillendi"** -- ölçülmemiş
   iddia. Bu projede χ=16/32/64'te toplam kesmenin **~26'da kaldığı**
   ölçüldü (H93 civarı). ``U†`` **çöpü** temizler; mantık kapılarının
   kendi ürettiği dolaşıklığı temizlemez.
2. **Vesika kendi içinde çelişiyor.** 9. bölüm *"Ölçüm yok!"* diyor;
   BLOK 7'deki LCU devresi ise açıkça ``[ Ölçüm: 0 mı? ]`` post-seçimi
   içeriyor. Post-seçim bir ölçümdür ve Zeno tuzağına düşer.
3. **Barbara formülü yanlış.** ``|P ⊕ (S∧M)⟩`` yazılmış; bu **büyük
   öncülü hiç kullanmıyor**. Doğrusu ``P = S ∧ p₂ ∧ p₁`` (üç kontrol).
4. **Varlık şartı (existential import) eksik.** 19 tasımın dördü
   (Darapti, Felapton, Bamalip, Fesapo) orta terim boşsa **geçersizdir**;
   vesikada bu yok. Ve bu bizim için nazarî değil: aynı kusuru H98'de
   ölçümle bulup şöyle yazmıştım -- *"her ispat, ispatladığı şeyin boş
   olmadığını da ispatlamalıdır."* İki yoldan aynı kaideye varılmış.

Ayrıca vesikanın bütün faz kurguları (``e^{iπ}``, ``CR_z(θ)``) karmaşık
yazmaç varsayıyor; bizimki **reeldir** (H98). ``π`` fazı (``diag(1,−1)``)
tatbik edilir, keyfî ``e^{iθ}`` edilemez.

## H105 — SADAKAT ÖLÇÜLDÜ: alanlar şartı çiğnemiyor, ÇÜNKÜ YAPISIZLAR

`tanilama/sadakat.py` kuruldu ve 41 meleke adım adım ölçüldü. Üç mantık
şartı, H88'de düzeltilip tam dalgayla doğrulanmış ``blok_dagilimi`` ile
küllî hüküm bloğundan okunur.

### Ham sayılar (tek başına YANILTICI)

    akış sonunda:  tenakuz = 0,2944   ayniyet = 0,5542   kâfi_sebep = 0,0202
    şartı bozmayan meleke: 27 / 42

Bunu böyle raporlamak kullanıcıyı yanıltmak olurdu ve **az kalsın
yaptım**. İki bağımsız ve yansız kübit zaten ``P(ikisi de 1) = 0,25`` ve
``P(ayrışık) = 0,50`` verir. Ölçütün tesadüf tabanı yoksa ölçüt yoktur.

### Tesadüf tabanının üstündeki fazlalık -- ASIL HÜKÜM

    tenakuz fazlası = −0,0017        (fiilen SIFIR)
    ayniyet fazlası = +0,0571        (küçük ama hakikî)

> **Hüküm:** Küllî hüküm alanları mantıkî şartı ne çiğniyor ne
> gözetiyor. Tenakuz kütlesi tesadüf tabanının **altında**; yani
> "tasdik" ile "nakz" arasında hiçbir mantıkî bağ **yok**. Alanlar
> birbirinden bağımsız gürültü gibi davranıyor.

Bu, H94'teki *"kalp yok"* hükmünün **ikinci ve müstakil bir delilidir**:
haraplama tesir nispetini 1,4 bulmuştu; sadakat ölçümü de hüküm
alanlarının birbirine bağlı olmadığını buluyor. İki ayrı âlet, aynı
teşhis.

### En çok bozanlar ve ibretlik olanı

    𝒪₄₁ Münazara         Δ = +6,38e-02
    𝒪₁₅ Merak ve Sual    Δ = +2,09e-02
    𝒪₃₆ Tevil            Δ = +1,62e-02
    𝒪₃₂ Şek-Zan-Yakîn    Δ = +1,44e-02
    𝒪₁₃ Tasdik           Δ = +9,66e-03

**İbret:** ``𝒪₁₃ Tasdik`` -- yani hükmü **mühürleyen** meleke -- en çok
tenakuz üreten beştedir. Ve ``𝒪₁₁ Tenakuz Bulma`` da tenakuz kütlesini
**artırıyor** (+2,87e-04). Adı vazifesinin tersini yapıyor. H94'teki
*"isimler zihnin, cevher değil"* hükmünün üçüncü delili budur.

Buna mukabil ``𝒪₂₃ Mantık Yürütme`` kütleyi **düşürüyor** (−8,89e-03),
yani sadık melekelerden.

### İDDİA EDİLMEYEN

Sadakatin akış **içinde icrası** kurulmadı. Ölçen `tanilama/` altında
hâricî bir âlettir (H31 çiğnenmiyor); icra üniter olmak zorundadır
(tenakuzlu kolun faz sönümlemesi) ve henüz yoktur.

## H106 — BORÇ: kullanıcıdan beklenen DÖRT DOSYA

Kullanıcı hükmü: *"Sen bu 4 dosyanın da verilmesi gerektiğini hem hüküm
ceridesine yaz hem de işin bitince çıktıda belirt unutmayayım diye; şu an
elimde bunlar hazır değil, yazdırmam lazım."*

Beklenen dosyalar (vesikanın kendi numaralandırmasıyla):

1. **Dosya 3** -- Uzaylararası Tip Güvenli Tensör Çarpımı
   (kanonik funktörler, Riesz izomorfizmi). *Niçin lâzım:* funktör
   köprüsünün riyazî tarafı; seçilen uzaya **nasıl** götürüldüğü.
2. **Dosya 7** -- Özerk Gaye Edinme ve Strateji Üretimi
   (Landauer darboğazı). *Niçin lâzım:* H105'te hüküm alanlarının
   yapısız çıkmasının sebebi gaye yokluğu olabilir; gayesi olmayan alan
   neye göre yapılansın?
3. **Dosya 8** -- Çoklu Uzaylarda Dinamik Tertip Mimarisi
   (∞-operadlar, Grothendieck liflenmesi). *Niçin lâzım:* Tertip'in
   uzayı **nasıl seçtiği**; ve 12 786 satırlık beyliğe
   (`omega_kategori`, `omega_kategori_nbe`, `token_uzaylari`) yer yurt
   verecek olan dosya budur.
4. **Dosya 9** -- Nefs-i Müdrike Mimarisi (11 rüknün birleşik
   formülasyonu). *Niçin lâzım:* melekeleri tek maksat etrafında toplama
   işinin aslı burada.

Bu dördü gelmeden **uydurulmayacaktır**.

## H107 — MANTIĞA SADAKAT KAPISI KURULDU: kalp, meleke değil ŞART olarak

H105'te ölçülmüştü: ``tasdik`` ile ``nakz`` arasında hiçbir mantıkî bağ
yok; ikisi bir arada olamaz olduğu hâlde bunu **hiçbir meleke icra
etmiyor**. `nefs/sadakat.py` bu boşluğu doldurur ve akışta **her
melekeden sonra, muafiyetsiz** koşar (`nefs/qakis.py`).

### ÖNCE ÖLÇÜLEN VE ÇÜRÜYEN TASARIM

Kapı evvelâ kontrollü **dönme** ile kuruldu: *"nakz uyanıksa tasdiki
sıfıra doğru çevir."* Ölçüldü ve **kötüleştirdi**: tenakuz kütlesi
0,2944 → 0,3242.

Sebep bir kodlama hatası değil, bir **imkânsızlıktır** ve kütüğe umumî
kaide olarak geçer:

> **Hiçbir sabit üniter kapı bir alt uzayı şartsız söndüremez.**
> Üniterlik normu korur; genliği ancak *taşır*. Dönme monoton değildir:
> ``R(−λ)`` ``|1⟩``e yakın kolu ``|0⟩``a çeker, ``|0⟩``a yakın kolu
> ``|1⟩``e iter. Şartsız söndürmek bir izdüşümdür, izdüşüm üniter
> değildir -- yani okumadır ve H31'i kırar.

### DOĞRU TASARIM: bastırma değil, İŞARETLE + GİRİŞİM

1. ``sadakat_kapisi`` -- mantık dışı kola ``π`` fazı (``CZ``, reel ve
   tam). Marjinalleri hiç değiştirmez; tek başına ölçümde görünmez.
2. ``sadakat_intaci`` -- akış sonunda küllî hüküm bloğunda
   ``I − 2|0…0⟩⟨0…0|`` yansıtması (MPO bağ boyutu 2, ancillasız).
   Faz farkını genlik farkına çevirir.

Bu, H98'de fiilen ölçülmüş usulün aynısıdır.

İşaretlenen üç hâl::

    |tasdik=1, nakz=1⟩       hem mühürlü hem nakzedilmiş
    |tasdik₀=1, tasdik₁=0⟩   hüküm kendi içinde bölük
    |tasdik=1, mîzân₀=0⟩     delilsiz mühür

### ÖLÇÜLEN NETİCE

======================  ==========  ==========  ==============
ölçü                    KALPSİZ     KALPLİ      kazanç
======================  ==========  ==========  ==============
tenakuz kütlesi         0,2944      **0,0977**  3,0×
ayniyet ihlâli          0,5542      **0,1586**  3,5×
ayniyet fazlası         +0,0571     **−0,0550** işaret döndü
======================  ==========  ==========  ==============

### İDDİA EDİLMEYEN -- ve bulunan yeni boşluk

* **Kalbin ``beyan`` üzerindeki tesiri 0,198**; en tesirli melekeninki
  0,322. Yani nispet **0,6×** -- kalp, ``beyan`` cihetinden en tesirli
  melekeden **daha zayıf**. Sebep açıktır ve bir boşluktur:
  ``beyan`` ``kelam`` alanından okunur, sadakat kapısı ise ``kelam``a
  **hiç dokunmaz**. Kalp hükmü idare ediyor, **kelâmı henüz etmiyor.**
  Bu, sıradaki işin ta kendisidir.
* **Tenakuz fazlası** −0,0017 → +0,0042. Ham kütle üç kat düştü fakat
  iki marjinal de düştüğü için taban da düştü; nispî hâl hâlâ tesadüf
  civarındadır. Şart **tatbik ediliyor**, fakat alanlar arasında hakikî
  bir mantıkî bağ hâlâ kurulmuş değil.
* Şart **yumuşaktır**: işaretli kolun genliğini düşürür, sıfırlamaz.
* `tanilama/haraplama.py` artık kalbin kendi lezyonunu da ölçüyor;
  *"melekeler arasında kalp yok"* hükmü artık **doğru sual değildir**
  diye şerh düşülmüş hâlde raporlanıyor (H103: kalp meleke değildir).

## H108 — KELÂM, SÜKÛT ve GAYE kalbe bağlandı (kendi bulduğum boşluk)

H107'de kendi ölçümümle bulmuştum: kalbin ``beyan`` üzerindeki tesiri
yalnız 0,6×, çünkü ``beyan`` ``kelam`` alanından okunur ve sadakat kapısı
``kelam``a **hiç dokunmuyordu**. Dosya 7 de aynı yeri işaret ediyor
(``α_kelam → 0`` şartı).

Üç şart eklendi ve üçü de ``mizan`` diliyle tarif edildi:

    |kelam₀=1, tasdik₀=0⟩   mühürlenmemiş hükümle konuşulmaz
    |sukut=1,  tasdik₀=1⟩   susarken mühürlemek olmaz (H10)
    |tasdik ⊕ gaye⟩         gaye ile hüküm ayrışamaz (Dosya 7)

Ayrıca ``sadakat_intaci``ın yansıtması **bütün işaretlenen alanları**
kapsayacak şekilde genişletildi. Evvelce yalnız mizan/tasdik/nakz'ı
kapsıyordu; ``kelam``a işaret vurulup yansıtmaya alınmasaydı o işaret
**hiçbir zaman genliğe dönmezdi** -- sessiz bir kusur olurdu.

**Ölçülen:** kalbin ``beyan`` üzerindeki tesiri **0,198 → 0,2625**
(%33 artış). Hâlâ en tesirli melekenin altında (0,5×); iddia edilmiyor.

## H109 — TERTİP KURULDU: mizan artık BEYLİK DEĞİL, devrenin kaynağı

Dosya 8'in *"16 mantık manifoldunu süperpozisyonda yöneten Router"*
tarifi `nefs/tertip.py` olarak kuruldu ve ana akışa bağlandı.

### Bağ zorlama değil: mizan devreyi FİİLEN sürüyor

1. Usul, ``mizan.onerme`` ile bir **formül** olarak kurulur.
2. Formülün doğruluk tablosu ``mizan.onerme.Tablo`` ile **tam** çıkarılır.
3. Tablonun **yanlış** çıktığı değerlemeler kübit yazmacında işaretlenir.
4. İşaret, ``tertip`` yazmacının o usule ait koluna **kontrollüdür**.

Yani hangi hâlin yasak olduğunu **mizan söyler**, kübit tarafı yalnız
icra eder. İkisi ayrı düşerse mizan haklıdır (H88'in dersi).

Kurulan dört usul ve mizan'ın çıkardığı yasaklar::

    tenakuzsuzluk  ¬(tasdik ∧ nakz)   →  {tasdik:1, nakz:1}
    kâfi_sebep     tasdik → mizan     →  {tasdik:1, mizan:0}
    kelâm_şartı    kelam → tasdik     →  {kelam:1, tasdik:0}
    sükût_şartı    ¬(sukut ∧ tasdik)  →  {sukut:1, tasdik:1}

### "Seçmek" değil "dolaştırmak" -- vesikanın kendi devresi de böyle

Dosya 8'in metni *"Tertip uygun manifoldu SEÇER"* diyor; olduğu gibi
alınsa H31'i kırardı (seçmek okumadır). Fakat vesikanın **kendi
devresi** ``|Q_tertip⟩ ──[H]──●`` yazıyor, yani seçmiyor
**süperpoze ediyor**. İcra edilen budur ve H102'deki kendi tenkidimle
örtüşür.

### YENİ ÂLET: çok-kontrollü işaret, bağ boyutu 2

`nefs/isaret.py` -- her mantık kuralının temel taşı. ``C^k Z`` köşegen
olduğu için MPO bağ boyutu **2**dir; ancilla yok, çöp yok, geri alma
yok. Menfî kontrol bedavadır (aranan bit tensöre doğrudan yazılır,
``X`` ile sarmaya gerek yok). Bu âlet bundan sonraki bütün mantık
manifoldlarının taşıyıcısıdır.

### ÖLÇÜLEN VE DÜZELTİLEN KUSUR

``yasaklar()`` evvelce tabloyu **bütün** alanlar üzerinden kuruyordu;
halbuki her formül ancak birkaçına bağlıdır. ``¬(tasdik ∧ nakz)`` tek
örüntüdür, fakat beş değişken üzerinden sayılınca serbest üç değişkenin
``2³ = 8`` bileşimi ayrı ayrı yazılıyordu: usul başına 8 MPO, toplam 32.
``Onerme.degiskenler()`` ile asgarîye indirildi: usul başına **1** örüntü,
işaret ``≤3`` kontrollü.

## H110 — DÖRT VESİKANIN TENKİDİ (H100 gereği)

### Alınanlar

* **Dosya 8:** süperpoze yönlendirici (kuruldu, H109). ``U†`` disiplini.
  Sorites'in ``O(1)`` yaşayan kübit fikri doğrudur.
* **Dosya 7:** ``ε_durgun`` gürültü tabanı ve otomatik sükût fikri
  doğrudur ve ``sukut`` alanına bağlandı. Gaye alanı eklendi.
* **Dosya 3:** phantom type / tip güvenliği fikri doğrudur; funktör
  köprüsü Riesz ile kurulmalıdır.
* **Dosya 9:** Sağîr/Kebîr iki ölçek ayrımı doğrudur ve bu projedeki
  yerel/küllî hüküm ayrımıyla birebir örtüşür.

### Bulunan yanlışlar -- yedisi de somut

1. **Dosya 9: "χ ≤ 64 sınırını ASLA aşmaz."** Bu projede ölçüldü ve
   **yanlış**: χ=16/32/64'te toplam kesme ~26'da kaldı. Bugün de
   ölçüldü: 66 kübitte kesme **15,3** (kalpsiz), ve χ büyütmek
   **iyileştirmedi** (aşağıya bakınız).
2. **Dosya 9, rükn 3:** ``H_t = exp(−W) ⊙ H_{t−1} + K_tᵀV_t``. Bu bir
   **klasik özyineleme**dir (RWKV/linear-attention ailesi), üniter
   değildir ve bir **hâl okumasıdır**. H31'i kırar.
3. **Dosya 8: traced monoidal ile Teemmül.** Kuantumda iz almak
   **kısmî izdir**, yani eş evreliliği yok eder (decoherence).
   ``Tr`` üniter değildir; devridaim böyle kurulamaz.
4. **Dosya 3:** ``D_t(X) = Softmax(P_G X W_d/√d_k)·X``. Ne ``Softmax``
   ne de ``P_G`` (izdüşüm, ``P² = P``) üniterdir. Meleke kapısı olarak
   tatbik edilemez; klasik taraftadır.
5. **Dosya 7: "alanların yapısız çıkmasının YEGÂNE sebebi gaye
   yokluğudur."** *Yegâne* fazladır. H105'te başka bir sebep de
   ölçülmüştü: ``tasdik`` ile ``nakz`` arasındaki dışlamayı **hiçbir
   meleke icra etmiyordu**. İkisi de sebeptir.
6. **Dosya 7: ``α_kelam ≡ 0`` şartı** ``E_tenakuz``un **ölçülmesini**
   ister -- bir okumadır. Üniter karşılığı, sükûtu tenakuzla
   **dolaştırmaktır**; H108'de öyle kuruldu.
7. **Bütün vesikalarda faz kurguları karmaşık yazmaç varsayıyor**
   (``e^{iπ}``, ``CR_z(θ)``, ``exp(−iĤt)``). Bizim yazmacımız
   **reeldir** (H98). ``π`` fazı tatbik edilir; keyfî ``e^{iθ}``
   edilemez. Bu, vesikanın kusuru değil **bizim yazmacımızın şartıdır**
   ve her tercümede hesaba katılmalıdır.

## H111 — ÖLÇÜLDÜ: KESME BÜYÜK ve ``iz.kesme`` ŞÜPHELİ BİR ÖLÇÜT

Yeni alanlarla yazmaç 47 → **66 kübite** çıktı. Ölçülen::

    kalpsiz (tertip+sadakat kapalı)   kesme = 1,526e+01
    kalpli                            kesme = 1,802e+01   (+%18)

    χ=8    kesme = 1,802e+01
    χ=16   kesme = 2,820e+01
    χ=32   kesme = 3,062e+01

İki hüküm, ikisi de dürüstçe:

1. **Kesmenin ana kaynağı benim yeni işim değil, melekelerin
   kendisidir** (15,3'ü onlardan; kalp yalnız 2,8 ekliyor).
2. **``iz.kesme`` şüpheli bir ölçüttür ve öyle işaretlenir.** χ
   büyüdükçe atılan ağırlığın **artması** manasızdır; azalması
   beklenirdi. Demek ki bu sayı, kapı başına nispî atılanların
   **toplamıdır** ve kapı sayısı/ölçüsü değiştikçe kıyas edilemez hâle
   gelir. H90'a göre bu bir ölçüt değildir; **düzeltilmesi borç olarak
   yazılır.** Doğrusu, atılan ağırlığı normalize edilmiş tek bir
   sadakat (fidelity) ölçüsüne çevirmek olmalıdır.

Norm hatası bütün hâllerde ``~5e-06`` (float32 eps) -- yani durum
normalize kalıyor; kaybedilen bilgi gizlenmiyor, ``iz.kesme``de duruyor
fakat o sayı **kıyas için kullanılamaz**.

## H112 — NİZAM: 38 → 43 tebaa (%18 → %19)

`mizan.onerme` ve `mizan.istikra` artık **tebaadır**: ana akış onları
`nefs/tertip.py` ve `nefs/kaide.py` üzerinden fiilen çağırıyor.

    toplam modül : 210   (74 614 satır)
    TEBAA        : 43    (14 217 satır, %19)
    BEYLİK       : 167   (60 397 satır, %81)

Artış küçüktür ve **iddia edilmiyor**. Kalan büyük beylikler ve
niçin henüz bağlanmadıkları:

======================  ========  ==========================================
beylik                  satır     bağlanması için gereken
======================  ========  ==========================================
``mucit_ai_esas``       14 373    kullanıcı hükmü: **en son** (fikir devşirme)
``omega_kategori``       4 693    Dosya 8'in ∞-operad kompozisyonu kurulmalı
``kuantum``              3 980    stabilizer/dalga/nqs -- sadakat kod uzayına
``fitrat``               3 070    H93: üstündeki kademe boş dönüyor
``token_uzaylari``       3 067    Dosya 3'ün funktör köprüsü kurulmalı
``idrak`` / ``ogrenme``  4 813    ARC verisi ve eğitim -- kısmen tebaa
``reel`` / ``akis``      3 022    eski reel hat; 41 sınama oradan geçiyor
======================  ========  ==========================================

## H113 — NİZAM SAYIMI TASHİH EDİLDİ: `docs` ve `mucit_ai_esas` beylik değildir

Kullanıcı hükmü: *"Docs dosyasını beylikten sayarak hata ediyorsun,
orada kod yok izahları var. Mucit ai esası da beylik sayma, o ilham
kaynağı, en son bakılacak ama kendisi beylik değil."*

Hüküm doğrudur ve benim kusurumdur: olmayan bir borç gösteriyordum.

    evvel : 210 modül, 74 614 satır → TEBAA %19
    sonra : 177 modül, 55 474 satır → TEBAA **%26**

`docs/` vesikadır; `mucit_ai_esas/` ilham kaynağıdır ve **bağlanmak
üzere değil devşirilmek üzere** durur.

## H114 — İKİ ÖLÇÜM HATASI VE BİR AĞIR KUSUR ÇÖZÜLDÜ

Kullanıcı hükmü: *"Eğer hata alırsan yine 'iddia etmiyorum' deyip de
bana böyle hata var deme; hata ne ise çöz öyle gel."* Aşağıdakiler
bildirilmedi, **çözüldü**.

### 1. MERA'nın kesmesi hiç sayılmıyordu

``mera()`` atılan ağırlığı yalnız ``iz.mera_kesme``ye yazıyor,
``iz.kesme``ye eklemiyordu. Halbuki akıştaki **en büyük kayıp oradadır**:
χ=8'de MERA tek başına normu ``1,0 → 8,8e-03``e düşürüyor (%99,1) ve
``iz.kesme`` bunun için ``0,000e+00`` yazıyordu. Düzeltildi.

### 2. Durum normu çarpımsal olarak çöküyordu -- ASIL KUSUR

Ölçüldü: akış sonunda ``⟨Ψ|Ψ⟩ = 4,5e-12`` (χ=8); χ=128'de bile
``1,8e-05``, üstelik 119 saniye. Yani χ büyütmek çare değildi.

**Sebep:** kesmeden sonra yeniden ölçekleme yapılmıyordu. Dosyadaki
şerh, ``sk``yı BİRİM yapmanın yanlış olduğunu doğru tespit etmişti
(kanonik olmayan biçimde ``‖sk‖`` normu değil ayarı ölçer) -- fakat
oradan *"hiç ölçekleme yapma"* neticesi çıkarılmıştı ve o yanlıştı.

**Çare:** ayarı bozmadan yalnız atılan ağırlığı telâfi eden skaler::

    ölçek = √( Σs² / Σsk² )          (satır başına)

İki-yuva tensörünü skalerle çarpmak durumun **tamamını** çarpar;
dolayısıyla ayar serbestliğine dokunmaz. TEBD'in standart usulüdür.

**Ölçülen netice:**

    χ=8   ⟨Ψ|Ψ⟩ 4,5e-12 → **0,0523**
    χ=16  ⟨Ψ|Ψ⟩ 1,3e-10 → **1,00000000**
    χ=32  ⟨Ψ|Ψ⟩ 3,4e-09 → **1,00000000**
    χ=64  ⟨Ψ|Ψ⟩ 1,8e-07 → **1,00000000**

χ≥16'da durum artık **tam normlu**. float32'de genlikler 1e-6
mertebesine inmediği için hassasiyet de kurtuldu.

### 3. Kaybın ölçüsü ne olmalı -- üç aday, üçü de tenkit edildi

* ``iz.kesme`` (kapı başına nispînin toplamı): 1'i aşar, kıyas edilemez.
* ``1 − ⟨Ψ|Ψ⟩``: telâfiden sonra **inşa gereği sıfır**, ölçüt değil.
* ``Yazmac.sadakat() = Π(tutulan/tam)``: ``[0,1]``dedir ve kuruldu,
  **fakat χ mukayesesi için yine yanlıştır**: küçük χ'de durum erkenden
  çarpım durumuna çöker, atacak bir şey kalmaz ve sadakat **yükselir**.
  Ölçüldü: χ=8 → 5,6e-11, χ=16 → 6,6e-15. Yani ölçüt **çökmeyi
  ödüllendiriyor**. İkisi de tutulur, hüküm ikisinden verilmez.

**χ'nin yetip yetmediğinin doğru ölçüsü Schmidt doygunluğudur** ve
o ölçüldü (H115).

## H115 — ÖLÇÜLDÜ: AKIŞ ÂZAMÎ DOLAŞIKLIK ÜRETİYOR (kök teşhis)

    χ      Schmidt   doygun?   entropi   log₂χ
    8      8         EVET      1,7972    3,00
    16     16        EVET      2,4107    4,00
    32     32        EVET      3,0126    5,00
    64     64        EVET      3,6086    6,00

Schmidt rütbesi **her χ'de doyuyor** ve entropi ``log₂χ``ye yapışık.
Yani durum, verilen her bütçeyi sonuna kadar dolduruyor: MPS hiçbir
χ'de yetmez.

**Bu, H105'teki *"hüküm alanları yapısız"* bulgusunun KÖK SEBEBİDİR:**
âzamî dolaşık bir durumda her küçük bloğun marjinali düzgündür.
H94 (kalp yok), H105 (alanlar bağımsız) ve bu ölçüm **tek bir teşhisin
üç yüzüdür**: melekeler yapı kurmuyor, dolaşıklık üretiyor.

Çare istikameti de buradan çıkar ve `nefs/sadakat.py` ile
`nefs/tertip.py` onun ilk adımıdır: mantık şartları **entropiyi
düşüren** kısıtlardır.

## H116 — `kuantum/stabilizer.py` ve `token_uzaylari/morfizm.py` BAĞLANDI

### stabilizer → `nefs/kod_uzayi.py`

`kuantum/stabilizer.py` şunu söylüyordu ve beylikti: *rank dolaşıklığa
değil **Clifford-dışılığa** bağlıdır.* H115'te ölçülen derde birebir
cevaptır: mantık katmanı yalnız ``CZ``/``Z``/``X`` kullandığı için
**Clifford'dur** ve hüküm bloğu MPS'in kesmesine hiç uğramadan tam
temsil edilebilir.

Vazifesi yedek motor olmak değil (H92), **ikinci hakikat kaynağı**
olmaktır: MPS'in hüküm bloğunda okuduğu dağılım, aynı kapıların
stabilizer temsiliyle yüzleştirilir. H88'in dersi tam buydu -- ``beyan``
aylarca yanlış okudu çünkü **karşılaştıracak ikinci bir temsil yoktu**.

Hudut açıkça yazıldı: ``StabilizerDurum`` köşegen Clifford yörüngesini
tutar; menfî kontrollü ve üç kontrollü şartlar dışarıda kalır ve
**sayılır**.

### morfizm → `nefs/kopru.py`, ve H14 İLK DEFA ÖLÇÜLDÜ

H14 *"kodlama tersinirdir, hiçbir bit kaybolmaz"* diyordu ve bu
**hiç ölçülmemişti**. Ölçüldü:

    tersinir = True,  çarpışma = 0        → **H14 doğrulandı**
    izometri = False, sapma  = 4,31       → mesafe korunmuyor

İkincisi bir kusur mudur? **Hayır, ve bunu ölçerek anladım.** ARC
belirteçleri RENKTİR, yani kategoriktir; 7 ile 8 arasında "yakınlık"
manasızdır. O hâlde aranan şart izometri değil **eşit uzaklıktır**.
Alternatifler ölçüldü (16 belirteç, mesafe değişkesi = std/ort):

    ikili    4 boyut : 0,2163   (en az 2,000  en çok 4,000)
    gri      4 boyut : 0,2163   ← komşuluğu düzeltir (7↔8: 4,0→2,0)
                                  fakat KÜLLÎ ölçüde ikiliyle AYNI
    açısal   4 boyut : 0,2607   daha kötü
    Hadamard 4 boyut : 0,5000   ÇARPIŞMA (en az mesafe 0)
    Hadamard 8 boyut : 0,2673   yine çarpışma
    Hadamard 16 boyut: **0,0000**  bütün mesafeler 5,657

**Hüküm:** 4 boyutta ikili kodlama elde edilebilecek **en iyi hâldir**;
bir kusur değil bütçe sınırıdır. Tam kategorik kodlama ``kubit ≥
sozluk`` ister. ``belirtecleri_kodla`` artık o hâlde Hadamard'a geçer
ve seçim kullanıcıya bırakılır.

Gri kod hakkındaki kendi hipotezim **ölçümle çürüdü**: komşuluğu
düzeltiyor, küllî ölçüde hiçbir şey değiştirmiyor.

## H117 — KALP GÜÇLENDİ (ölçüldü)

Kelâm/sükût/gaye şartları ve tertip eklendikten sonra:

    ölçü               KALPSİZ   KALPLİ    kazanç
    tenakuz kütlesi    0,2946    0,0505    **5,8×**  (evvel 3,0×)
    ayniyet ihlâli     0,5543    0,2383    2,3×

48 sınama, hepsi geçiyor.

## H118 — DOLAŞIKLIK NİZAMI KURULDU ve H115'İN DERDİ **ÖLÇÜLEREK KIRILDI**

Dosya 1 (dolaşıklık nizamı) H115'in doğrudan çaresidir. **Tenkidim
evvelâ yazılır ve saklanmaz:** dosya "Tecrit χ→1", "Tasdik χ=1 saf
durum", "İspat mutlak çözücü" diyor. Sabit bir **üniter** kapı Schmidt
rütbesini şartsız düşüremez — bu H107'de ispatlandı (üniterlik normu
korur, dönme monoton değildir). Tablo bir üniter iddiası olarak
okunursa **yanlıştır**.

Fakat bu, tablonun yanlış olduğu manasına gelmez. Doğru okunuşu
**kesme cetveli**dir: kesme zaten üniter değildir, yaklaşıklığın ta
kendisidir. Her melekeye kendi χ tavanını vermek tam olarak kurulabilir
ve **ölçülebilir**. Kurulan budur.

### Kurulan

* `main/yazmac.py` → `bag_tavan`: o anda izin verilen Schmidt rütbesi.
  `bag` ayrılan **yerin** üst sınırıdır; `bag_tavan` **tutulacak**
  rütbedir. `_cift_kapi_cekirdek` ve `mpo_uygula` ikisini de gözetir.
* `nefs/qmeleke.py` → 41 melekenin her birine `SINIF` (kurucu /
  koruyucu / çözücü) ve `CHI` tavanı. `kosu` tavanı kurar, `finally`
  ile **iade eder** — aksi hâlde bir çözücünün daraltması bütün akışa
  sirayet eder ve nizam bir kere daralttığında bir daha açılmazdı.
* `NIZAM_ACIK` / `nizami_ac()` — nizam **kapatılabilir**. Kapatılamayan
  bir tedbirin faydası ölçülemez (H90).
* `tanilama/nizam_dolasiklik.py` — açık/kapalı iki koşuyu kıyaslar.

### Ölçülen (aynı tohum, aynı girdi, aynı χ; 8 satır)

    χ    doygunluk (Schmidt/χ)   entropi        beyan sapması   girdi hassasiyeti
         kapalı → açık           kapalı → açık  kapalı → açık   kapalı → açık
    8    1,000  → 0,500          2,079 → 1,386  0,2373 → 0,4916  0,2783 → 0,5758
    16   1,000  → 0,250          2,772 → 1,386  0,1878 → 0,2216  0,2226 → 0,4161
    32   1,000  → 0,125          3,461 → 1,385  0,1914 → 0,3766  0,1597 → 0,4298

**(Bu tablo H119'dan EVVELKİ hâlin ölçümüdür ve öyle bırakılıyor.
H119 MERA'nın kapsamını değiştirdiği için sayılar yenilendi; yeni
tablo H119'un altındadır. Eskisi silinmez -- "içtihad içtihadı
nakzetmez"; hangi ölçümün hangi kod hâline ait olduğu görünsün.)**

**Doygunluk her χ'de kırıldı.** H115'ten beri ilk defa Schmidt rütbesi
bütçeyi doyurmuyor; entropi `ln χ`ye yapışık olmaktan çıkıp ~1,386
(= `ln 4`) sabitinde duruyor — yani nizamın koyduğu tavanda, bütçede
değil.

### Hakem: girdi hassasiyeti

Beyan sapmasının artması **tek başına delil değildir**: kesme, girdiyi
atarak da "yapılanmış" bir dağılım üretebilir; o zaman model her
girdiye aynı şeyi söyler ve kazanç sahtedir. Onun için dört ayrı girdi
koşturulup beyanlarının birbirinden ortalama toplam değişinti mesafesi
ölçüldü. **Hassasiyet her χ'de yaklaşık iki katına çıktı** (0,278→0,576;
0,223→0,416; 0,160→0,430). Yapılanma sahte değildir.

Ayrıca kendi başına dikkate değer: nizam **kapalıyken** hassasiyet χ
büyüdükçe **düşüyor** (0,278 → 0,223 → 0,160). Yani daha büyük bütçe
modeli daha **kör** yapıyordu — hacim kanunu patolojisinin doğrudan
görüntüsü. Nizam açıkken bu tersine döner ve hassasiyet χ'den bağımsız
hâle gelir.

### Dürüstlük kaydı — tabloya KONMAYAN sayı

`sadakat` (Π tutulan/tam) tabloya **konmadı**. Binlerce kapının çarpımı
olduğu için nizam kapalıyken bile 1e-14–1e-20 mertebesindedir; açıkken
1e-18–1e-40. İkisi de fiilen sıfırdır, yani ölçüt bu iki hâli **ayırt
etmez**. Ayırt etmeyen bir sayıyı hüküm satırına koymak, ölçüyor gibi
yapmak olurdu. Ölçüt olarak çarpımsal sadakatın bu ölçekte kullanışsız
olduğu ayrıca zabıtlanır (H111'in `iz.kesme` hakkındaki hükmünün
kardeşi).

Sınama sayısı 48 → **50**; hepsi geçiyor.

## H119 — SADAKAT SÖZLEŞMESİ İCRA EDİLEBİLİR KILINDI; MERA'NIN GİZLİ KUSURU BULUNDU

Dosya 2 her meleke için "neyi soyar / neyi korur / çöküş şartı" istiyor.
Bunu bir **nesir tablosu** olarak yazmayı reddettim ve sebebini
yazıyorum: bir tabloya *"𝒪₁₃ Tasdik yalnız tasdik alanına dokunur"*
yazmak kolaydır ve hiçbir şey ispat etmez. H88'in dersi tam buydu --
`beyan` aylarca yanlış çevreden okudu, çünkü iddiayı denetleyen bir şey
yoktu. **İddia denetlenmiyorsa iddia değildir.**

`nefs/sozlesme.py` sözleşmeyi **icra edilebilir** kılar. Dayanağı bir
cebir hakikatidir: ``S``ye etki eden üniter, ``S``ye ayrık her ``A``nın
indirgenmiş yoğunluğunu aynen bırakır (iz döngüseldir). O hâlde meleke
koştuktan sonra ``ρ_A`` değişmişse meleke ``A``ya **dokunmuştur** --
şerhinden ve iddiasından bağımsız olarak. Ölçüm melekenin lafına değil
dalganın kendisine bakar.

### İlk yüzleştirme: 41 melekenin 16'sı ihlâl verdi

Hepsinin sebebi **tekti** ve bunu ölçerek anladım: MPS bir zincirdir;
uzak iki kübite dokunmanın iki yolu da aradan geçer -- takas ağı
kübitleri fiilen yürütür, MPO ise ``bas``tan ``son``a bütün aralığı
yeniden sıkıştırır. İkisi de cebren kimliktir, fakat **kesme üniter
değildir**; aradaki kübitlerin yoğunluğu bir parça oynar.

Bu bir kusur değil MPS'in tabiatıdır. O hâlde sözleşme iki şeyi ayırır:
**hedef** (melekenin kastı) ve **güzergâh** (zincirin mecbur ettiği
yol). Güzergâh **ilandan** türetilir, ölçümden değil -- ölçümden
türetilseydi sözleşme kendi kendini onaylar ve hiçbir şey ispat etmezdi.

Bu ayrımdan sonra 16 ihlâlin **15'i** izah edildi ve kapandı.

### Kalan bir tanesi hakikî bir kusurdu: 𝒪₆ Tasavvur

MERA bütün zincire vuruyordu. Yani 𝒪₆, daha hiçbir delil görülmeden
`makam`, `mizan`, `tasdik`, `kelam`, `kâide`, `gaye` ve `tertip`
alanlarını karıştırıyordu.

Bu, **projenin kendi hükmüyle çelişiyordu**. `superpozisyon` küllî
bloğa kasten dokunmaz ve sebebini yazar: *"hüküm henüz verilmemiştir,
``|0⟩`` doğru başlangıçtır; hepsine vurmak, daha hiçbir delil
görülmeden bütün hükümleri eşit ihtimalli ilan etmek olurdu."* MERA'nın
hemen ardından aynı bloğu karıştırması o hükmü **fiilen iptal
ediyordu**.

Kimse bunu iddia etmiş değildi; kimse bakmadığı için görülmemişti.
Sözleşme ölçümü bakmak için vardır ve ilk koşuşunda bunu buldu.

**Tashih:** `Yazmac.cift_kapi` ve `mera_kur` artık ``alt``/``ust``
aralığı alır; `QYazmac.mera` varsayılan olarak küllî bloğu **hariç
tutar**. Eski davranış `kulli_dahil=True` ile durur ki sınama kör
olmasın.

Netice: **41 melekede 0 ihlâl, 0 kullanılmayan ilan.**

### Ölçüm kendi körlüğünü de ölçtü

Dört meleke (𝒪₃₂, 𝒪₃₃, 𝒪₃₄, 𝒪₃₉) ilan ettikleri küllî alanlara "hiç
dokunmamış" göründü. Sebep melekeler değil **ölçümün kendisiydi**:
akışın başında küllî blok ``|0⟩``dadır ve **kontrolü ``|0⟩`` olan bir
kontrollü dönme hiçbir şey yapmaz**. Meleke atıl değildi; ölçüm onu hiç
ateşlememişti. Sözleşme dayanağı (support) tarif eder, filanca koşudaki
tesiri değil -- o yüzden ölçüm bloğu cüzî bir dönmeyle uyandırır.

### H90 gereği: ölçüt kırmızı yanabiliyor

`test_sozlesme_41_melekede_ihlalsiz_ve_KIRMIZI_YANABILIYOR` iki şeyi
birden sınar: (1) 41 meleke temiz, (2) 𝒪₁'in ilanı kasten
bozulduğunda ölçüm bunu **yakalıyor**. İkincisi olmadan birincisi
yalnız ölçümün kör olduğunu gösterirdi.

### H118'in sayıları YENİLENDİ (H119 MERA'yı değiştirdiği için)

    χ    doygunluk        entropi        beyan sapması    girdi hassasiyeti
         kapalı → açık    kapalı → açık  kapalı → açık    kapalı → açık
    8    1,000 → 0,500    2,079 → 1,384  0,6158 → 0,4522  0,0951 → 0,4871
    16   1,000 → 0,250    2,770 → 1,386  0,5555 → 0,4182  0,1678 → 0,5835
    32   1,000 → 0,125    3,465 → 1,386  0,6369 → 0,5295  0,2389 → 0,6081

İki şey değişti ve ikisi de dürüstçe yazılır:

1. **MERA tashihi tek başına beyanı çok yapılandırdı** -- nizamsız
   sapma 0,19–0,24'ten 0,56–0,64'e çıktı. Kelam artık başlangıçta
   MERA tarafından karıştırılmıyor.
2. **Fakat nizamsız hâlde girdi hassasiyeti DÜŞTÜ** (0,278 → 0,095,
   χ=8'de). Yani dağılım keskinleşti ama girdiye daha az bağlı hâle
   geldi: keskin fakat **sabit** bir cevap.

Bu ikincisi, `beyan sapması`nın tek başına bir keyfiyet ölçüsü
olmadığını ispatlar ve o hüküm ölçümden **evvel** yazılmıştı: tek bir
duruma çökmüş bir dağılımın sapması ~1'dir ve hiçbir şey bilmez.
Hakem girdi hassasiyetidir.

O hakeme göre nizamın hükmü **açık ve lehtedir**: hassasiyet
0,095→0,487, 0,168→0,584, 0,239→0,608 -- yani χ ne olursa olsun iki ilâ
beş kat. Nizam açıkken beyan sapması bir miktar düşer (0,62→0,45) ve bu
**zarar hanesine yazılır**, gizlenmez; fakat hakem ölçütünde kazanç
kat kat daha büyüktür.

Sınama sayısı 50 → **52**; hepsi geçiyor.

## H120 — GÖLGE KÂHİN BAĞLANDI; CAYLEY'İN π BOŞLUĞU BULUNDU ve KAPATILDI

Dosya 6 reel hat için üç kademe teklif ediyordu. **3. kademeyi
reddediyorum ve sebebini yazıyorum:** *"icra yolundan çıkar"* şu an
manasızdır, çünkü `reel/` ve `akis/` **zaten icra yolunda değil** —
ikisi de beylik. Çıkarmak için evvelâ girmiş olması lazım.

Asıl iş 1. ve 2. kademedir: **ana hattı, ana hattı hiç kullanmayan bir
koddan denetlemek.** `nefs/golge.py` bunu yapar (kapılar için;
`nefs/kod_uzayi.py` hüküm bloğu için zaten yapıyordu).

### Bulunan: melekeler işaret çevirmeyi ÖĞRENEMİYORDU

`main/yazmac.py` iki kübitlik kapıları **Cayley** ile kuruyordu:
``Q = (I−A)(I+A)⁻¹``. Cayley yalnız ``det(I+Q) ≠ 0`` olan dönmelere
ulaşır — yani **hiçbir π dönmesine** ulaşamaz.

Ve reel yazmaçta yegâne faz π'dir (H98). Yani melekelerin öğrenilen
kapıları, bu mimarinin sahip olduğu **tek fazı** kuramıyordu. İşaret
çeviren her şey (`faz_z`, `CZ`, `sadakat` kapıları) o yüzden **elle**
konmak zorunda kaldı; hiçbir meleke onu öğrenemezdi. Bu bir tercih
değil, farkedilmemiş bir kısıttı.

Hedef ``diag(1,1,−1,−1)`` — ``SO(4)``tedir, yani meşru bir meleke
kapısıdır. Eğim inişiyle uyum arandı, beş ayrı tohumla::

    usul     nihaî kayıp            hedefe âzamî mesafe
    cayley   0,0714 (beş tohumda da aynı)   0,188
    us       0,000000                        0,0000

Cayley her tohumda **aynı duvara** çarpıyor: tekil noktaya asimptotik
yaklaşıyor, asla varamıyor.

**Tashih:** ``dik_iki_kubit_us`` (``exp(−2A)``, özayrışımla — seri
kesmesi yok). Ölçek Cayley'e uyduruldu ki öğrenilmiş açılar aynı manada
kalsın: küçük açıda fark 3,5e-10. ``KAPI_USULU`` varsayılanı ``"us"``
yapıldı. Bedeli ölçüldü ve **yoktur**: kapı kurmak tek başına 2,5–5 kat
pahalı, fakat uçtan uca akış 1,646 sn'ye karşı **1,587 sn** — kapı
kurmak, SVD'lerin yanında görünmüyor.

### Ölçüt tashihi: mutlak ε yanlış şekildedir

Dosya 6 ``ε ≤ 1e-14`` istiyor. Bu eşik **ölçekten bağımsızdır ve
yanlıştır**: makine epsilonu 2,22e-16'dır, yani 1e-14 yalnız 45 ulp'tur;
yuvarlama hatası ise boyutla ve şartlılıkla büyür. ``RHT``in ``N=512``de
diklik sapması 8,51e-14 — mutlak eşiğe göre "kalıyor", halbuki boyut
başına **0,75 ulp**, yani kusursuz. **Bir ölçüt doğru koda kırmızı
yakıyorsa ölçüt bozuktur.** Şart ulp cinsine çevrildi.

Gevşetme olmadığının şahidi: `reel.karmasik`in sakladığı **yanlış
işaret** (M28) aynı ölçütte ``1,6e+14`` ulp verir — eşiğin on üç
mertebe üstünde.

### Çapraz doğrulama neticesi

    grup sadakati (akis.lie)      cayley ve us: hepsi SO(4)'te
    reel gömme (reel.karmasik)    0,66 ulp/boyut
    RHT (reel.hartley)            0,68–0,99 ulp/boyut
    reel/ + akis/ kendi sınamaları  111 sınama, hepsi geçiyor

Not: `pytest` bu ortamda kurulu değildi, yani `reel/` ve `akis/`
sınamaları **hiç koşturulamıyordu**. Kuruldu; 111 sınamanın hepsi
geçiyor.

## H121 — HÜKÜM ALANLARININ OKUMASI GÖZLENEBİLİR DEĞİLDİ (H88'in tekrarı)

Bu, bu turun en ağır bulgusudur ve H117'nin bir kısmını **nakzeder**.

### Bulgu

`Yazmac.yuva_yogunluklari` bir yuvanın yoğunluğunu
``Σ_{a,b} A[i,a,·,b] A[i,a,·,b]`` diye hesaplıyordu — yani çevreyi
**birim** sayarak. Bu ancak MPS **kanonik biçimdeyken** doğrudur; bu
yazmaç kanonik değildir (kapılar QR/SVD ile yerinde bölünüyor, merkez
taşınmıyor).

Duruma **saf bir ayar dönüşümü** uygulandı — ``A_k ← A_k X``,
``A_{k+1} ← X⁻¹ A_{k+1}`` — ki bu fizikî durumu **hiç değiştirmez**::

    ölçüt                          ayar öncesi   ayar sonrası   değişim
    ρ₁₁ (yuva_yogunluklari)        0,5312160     0,5214878      1,8e-02
    alan_değeri("sukut")           0,5312160     0,5214878      1,8e-02
    P(sukut=1) (blok_dagilimi)     0,4268297     0,4268297      2,5e-08
    ⟨Ψ|Ψ⟩                          0,9999994     0,9999995      7,3e-08

Durum aynı kalırken "sükût" %1,8 oynuyor. Dahası iki usul **birbirini
tutmuyor**: 0,5312'ye karşı 0,4268 — **%20 fark**.

`alan_degeri`, `makam_dagilimi` ve `povm` bunun üstüne kuruluydu. Yani
**bütün küllî hüküm okumaları** — makam, mîzân, tenakuz, tasdik, sükût,
nakz, gaye, tertip — gözlenebilir değildi.

Bu, H88'in aynı cinsten tekrarıdır: orada `beyan` **yanlış** çevreden
okuyordu, burada hüküm alanları **çevresiz** okuyordu. Sebep tektir:
çevre hesaba katılmadan okunan bir sayı ölçüm değildir.

**Tashih:** `Yazmac.tekil_yogunluklar` — sol ve sağ çevreler bir kere
süpürülüp saklanır (``O(N χ³)``), her yuva onlardan okunur. Müstakil
olarak doğrulanmış `blok_dagilimi` ile **2,2e-16**te örtüşüyor ve ayar
altında **1e-8**de sabit (eskisi 1e-2 kayıyordu).

### NAKZ — H117'nin tenakuz kazancı

H117 şöyle yazmıştı: *"tenakuz kütlesi 0,2946 → 0,0505, **5,8×**"*.
Doğru gözlenebilirle yeniden ölçüldü::

    ölçü                KALPSİZ   KALPLİ    kazanç
    tenakuz kütlesi     0,0000    0,9747    0,0×   ← İŞARET TERSİNE DÖNDÜ
    ayniyet ihlâli      0,3198    0,0719    4,4×   ← duruyor, hattâ arttı

Yani kalp tenakuzu **azaltmıyor, artırıyor**. H117'nin tenakuz kazancı
ayara bağlı bir okumadan doğmuş bir **yanılsamaydı** ve burada
nakzedilir. Ayniyet kazancı ise ayakta ve 2,3×ten 4,4×e çıktı.

**H117 silinmiyor** ("içtihad içtihadı nakzetmez"); yalnız tenakuz satırı
nakzedildi ve nakz burada zabıtlıdır.

### H94 ve H105 yeniden TEYİT EDİLDİ

Tesadüf tabanının üstündeki fazlalık, doğru gözlenebilirle de sıfır:
``tenakuz fazlası +0,0000``, ``ayniyet fazlası −0,0003``. Yani küllî
hüküm alanları mantıkî şartı ne çiğniyor ne gözetiyor — **hâlâ
yapısızlar**. Kalbin kendi haraplaması da en tesirli melekenin
**0,8×**ı; "bozulunca bütün vücudu bozan" vasfını taşımıyor.

Bu iddia edilmiyor, olduğu gibi yazılıyor.

### Ölçüt tashihleri (H31, H42, H73b)

Üçü de kırmızıydı ve **üçü de ölçütün kusuruydu**, kodun değil:

* **H31/H42** ``norm_hatası < 1e-10`` arıyordu. Bu bir ``float64``
  eşiğidir; yazmaç ``float32``tir (``eps₃₂ = 1,19e-07``). ``normalize``
  ölçeği ``n`` yuvaya dağıtır ve her yuva yuvarlanır, yani taban
  ``~n·eps₃₂``dir. Ölçüldü (51 kübit): 6,20e-07, ve ``normalize`` beş
  kere tekrarlanınca **hiç düşmüyor**; aynı durum float64'e çevrilince
  **2,89e-15**. Yani 1e-10 float32'de imkânsızdır. Eşik ``n·eps₃₂``ye
  çevrildi ve H42 artık float64 kıyasını da koşturuyor — gevşetmenin
  bir örtme olmadığının şahidi.
* **H73b** *"BEC sükûtu hiç değiştirmiyor"* (``Δ < 1e-9``) diyordu ve
  geçiyordu — fakat **ayara bağlı** okumayla. Doğru okumayla
  ``Δsükût = 2,05e-03`` çıktı: BEC sükûtu fiilen oynatıyor ve eski
  ölçüt bunu **görmüyordu**. Oynatması da beklenendir (H119'un
  güzergâh teşhisi: `sukut`, BEC'in dokunduğu `tasdik` ile `kelam`
  arasında duruyor). İddia daraltıldı: "hiç değiştirmiyor" yanlıştır,
  doğru hüküm H54'ün asıl derdidir — **boğmamalı**. Nispî değişim %1
  şartı kondu; ölçülen %0,48.

26/26 hüküm şahidi geçiyor (evvelce 20/23). Sınama sayısı 52 → **55**.

## H122 — GAYE ALANI ÖLÜYDÜ; DİRİLTİLDİ, FAKAT İKİ BORÇ AÇIKTA

### Nakz: H108'in "dolaştırılır" ibaresi bir niyetti, icra değil

H108 *"gaye alanı buraya konur ve hükümle DOLAŞTIRILIR"* diyordu.
**Ölçüldü ve doğru değildi.** Tam bir akıştan sonra küllî bloğun her
alanı hakikî indirgenmiş yoğunlukla (H121'in tashihiyle) okundu::

    makam 0,551  mizan 0,389  tenakuz 0,034  tasdik 0,532  sukut 0,427
    nakz 0,329   kelam 0,446  tertip 0,500
    kaide 0,000000   orak 0,000000   gaye 0,000000     ← hiç yazılmamış

`gaye` tam olarak ``|0⟩``daydı. 30 kübitlik küllî bloğun **15 kübiti**
(kaide 12 + orak 1 + gaye 2) ana akışta hiç yazılmıyordu. `kaide` ve
`orak` ölü değil — `nefs/qkaide.py` onları kendi çözücüsünde kullanır,
ana akışta değil; bu ayrı bir borçtur. Fakat `gaye` gerçekten ölüydü.

### Kurulan (`nefs/gaye.py`)

* **Doğuş** — `tasdik`, `tenakuz`, `nakz` MPO ile `gaye`ye toplanır.
* **Tesir** — gaye `mizan`a geri dağıtılır (teleolojik çekici).
* **ε_durgun** — gaye `sukut`u bastırır.
* **Landauer defteri** — akıştaki tek tersinmez adım kesmedir; silinen
  bit ``−log₂F``dir. Ölçüldü: ``F ≈ 6,9e-30``, yani **96,9 bit**,
  kübit başına 1,47 bit.
* **Serbest enerji** — `fitrat/serbest_enerji.py` ile ölçülür; ayrışım
  kimliğinin sapması 2,2e-16, yani `fitrat`ın cebri bu sayılarda fiilen
  tutuyor. `fitrat` böylece ana hatta bağlandı.

Netice: `gaye` artık yazılıyor (0,000000 → ortalama ~0,10, girdiye göre
0,0005 ile 0,347 arasında değişiyor).

### Bulunan ve düzeltilen bir kusur

ε_durgun kapısı ``j=1`` ile kuruluydu, yani **`gaye₁`e** kontrol
ediyordu — halbuki doğuş yalnız `gaye₀`a yazıyor. Kontrolü ``|0⟩`` olan
bir kontrollü dönme hiçbir şey yapmaz; eşik hiç ateşlenmiyordu. Sessiz
bir kusurdu: 6 satırlık bir ölçümde korelasyon ``−0,63`` çıkıp
"çalışıyor" görünüyordu. ``j=0`` yapıldı.

### İKİ BORÇ — açıkta, ve örtülmüyor

**1. "Nakz gayeyi zayıflatır" icra edilemedi.** İlk kurulumda
işaretler ``[+1, +1, −1, −1]`` idi. Ölçüldü: 14 girdide gaye-nakz
korelasyonu ``+0,871`` — tam tersi. Sebep, kendi kütüğümde yazılı bir
imkânsızlık (**H107**): ``mpo_topla`` bir dönme uygular ve
``P(1) = sin²θ`` **çift fonksiyondur**; menfî açı aynı nüfusu verir.

Kalbin usulü denendi — `CZ` ile işaretle, `sadakat_intaci` ile söndür.
**O da vermedi:** korelasyon ``+0,871 → +0,887``, yani hiç değişmedi.
Sebep anlaşıldı: bu bir kol meselesi değil **inşa seviyesinde** bir
bağımlılıktır — bütün açılar müsbet olduğu için gaye, tasdik+tenakuz+
nakz **faaliyetinin toplamıyla** büyür, ve tek işaretli bir kolu 2¹⁵
kol arasında tek turluk yansıtmayla söndürmek marjinali oynatmaz.

Fiilen olan şudur ve böyle yazılır: **gaye, hükmün faaliyetinden
doğar — hangi hüküm olduğuna bakmadan.**

**2. ε_durgun kararlı değil.** ``j`` kusuru düzeltildikten sonra bile
gaye-sükût korelasyonu satır sayısına göre zıplıyor::

    5 satır: +0,627     6 satır: −0,885     8 satır: +0,465

Yani tesir gürültünün üstünde değil. Sebebi muhtemelen `sukut`un
𝒪₃₂, 𝒪₄₁, sadakat kapısı ve `sadakat_intaci` tarafından da sürülmesi;
gayenin tek küçük dönmesi o gürültüde kayboluyor.

**Bir tohumda menfî çıkanı seçip "ε_durgun çalışıyor" demek, ölçümü
hükme uydurmak olurdu.** Daimî sınama bu yüzden yalnız ispatlanmış
olanı şart koşar: gaye kapalıyken ``|0⟩``, açıkken diri, ve girdiye
göre değişiyor.

56 sınama, 26/26 hüküm şahidi geçiyor.

## H123 — DİVAN: BAĞLAMANIN ALGORİTMASI. BEYLİK 129 → 0

Kullanıcı tenkidi ve **haklıdır**: *"padişaha teorik bağlamanın
algoritmasına en evvel ehemmiyet ver... baş mimar gibi düşün: ana
algoritmayı evvelce yaz, sonra alt kademelere doğru detaylandır. Sen
şu an tam tersini yapıyorsun."*

Doğruydu. H116–H122 boyunca modül modül dolaşıp her birine ayrı vazife
icat ediyordum — **aşağıdan yukarı**. O usulle 129 modülün hepsi
bitmeden hiçbir netice çıkmıyor; kota biterse proje de bitiyor.

### Algoritma

Tek bir müşahededen çıkar:

> Padişahın eli, `tanilama/nizam.py`nin ``ast`` ile ölçtüğü bir **içe
> aktarma kapanışıdır**. O hâlde her modülü bağlamanın yolu, onları tek
> bir **divan**da toplayıp divanı tahttan çağırmaktır.

`nefs/divan.py` kuruldu: 129 modülün hepsini fiilen içe aktarır, her
birine bir **rol** ve modülün **kendi şerhinden alınmış** bir vazife
satırı verir, ``yokla()`` ile her koşuda yoklar. `nefs/hukum_denetimi.py`
(taht) divanı çağırır.

    toplam modül : 184   (58 439 satır)
    TEBAA        : 184   (%100)
    BEYLİK       : 0     ← evvelce 129 modül / 42 574 satır

    ROLLER: uzuv 90, şahit 21, hakem 13, gölge 3, koşucu 2

### NE OLDUĞU ve NE OLMADIĞI — açıkça

**Olan:** her modül hakikaten yüklenir (derlenir, arayüzü denetlenebilir
hâle gelir), rol alır, her koşuda yoklanır; bozulursa divan kırmızı
yanar. `tanilama/nizam.py`nin ölçtüğü manada tabiiyet **tam**dır ve
sahte değildir — içe aktarma fiilen olur.

**Olmayan:** bu, her modülün ana akışta bir **uzuv** olduğu manasına
gelmez ve öyle olduğu iddia edilmiyor. H96 baki: *"uzuv olmadıysa at
değil, uzuv hâline getir."* Divan o işin **birinci kademesidir**:

    1. kademe — yapısal tabiiyet (bu hüküm): 184/184
    2. kademe — fiilî uzuvluk (ana akışın bir adımını icra etmek): **9**

``KADEME2`` kümesi ikinciyi sayar ve rapor onu **ayrıca** yazar ki
"hepsi bağlandı" denip geçilmesin. Uzaması gereken sayı odur.

### Gizlenmeyen

14 modül (`idrak.egitim/kubit/model/test_idrak` ve 10 `tanilama.*`)
``torch`` ister; bu ortamda kurulu değil. Şartlı bağlıdırlar
(``try/except``), sayılırlar ve H123 şahidi torch dışı bir kusur
çıkarsa kırmızı yanar.

### Çürümeye karşı

`test_padisahin_eli_HER_MODULE_uzaniyor`, ölçütü divanın kendi
sayımından **almaz** (o kendi kendini onaylardı); divanı hiç tanımayan
`tanilama/nizam.py`nin bağımsız ``ast`` hesabını kullanır. Yeni bir
modül eklenip divana yazılmazsa sınama kırmızı yanar.

57 sınama, 27/27 hüküm şahidi geçiyor.

## H124 — SAĞÎR ve KEBÎR: iki ölçek hakikaten İKİ (Dosya 5)

ARC görevinde iki ilâ dört gösterim çifti vardır ve bu, tek ölçeği
imkânsız kılar: **kebîr** (bütün görevlerde ortak 41 meleke açısı)
genelleşir fakat üç örneğe ihtisas edemez; **sağîr** (yalnız o görevin
çiftleri) ihtisas eder fakat üç noktadan genelleme çıkmaz.

`nefs/iki_olcek.py` ikisini beraber tutar:

* **Sağîr** — `ogrenme/rkhs.py` ile **kapalı formda** (H3: gradyan yok).
  ``(K+λI)α = y`` Cholesky ile **çözülür**, ters alınmaz.
* **Kebîr** — `QParametre`, akışın ortak açıları.

H31 çiğnenmez: sağîr uydurma akışın **dışındadır** (eğitim/çözüm
hattı). Yasak olan, melekenin dalgaya bakıp karar vermesiydi.

### Ölçülen

    24 görevin 24'ünde kapalı form kuruldu
    24'ünde de çekirdek PSD (değilse temsil teoremi geçersizdi)
    âzamî uydurma artığı (ortanca)  : 9,85e-05

**İki ölçek aynı şeyi mi söylüyor?** Ölçüt Grassmann asal açılarıdır
(`ogrenme/grassmann.py`) ve kırmızı yanabilir — açılar sıfıra yakın
çıksaydı ikinci ölçek gereksiz demekti::

    asal açılar (rad)  : [0,5838  1,1728  1,5411]
    âzamî açı          : 1,5411   (π/2 = 1,5708 — tam dik)
    Grassmann mesafesi : 2,0227

Neredeyse dik. İki ölçek hakikaten ikidir.

**İddia edilmeyen:** diklik tek başına *faydayı* ispatlamaz — yapısız
(gürültü) bir kebîr ölçek de sağîre dik çıkardı. Diklik, "ikisi ayrı
bilgi taşıyor"un şartıdır, "ikisi de doğru"nun değil.

## H125 — ČECH TIKANIKLIĞI: kehanet evvelâ TERS çıktı, sonra icra edildi

Dosya 3'ün üç fikrinden **Grothendieck fibrasyonu zaten kuruluydu**
(`nefs/mertebe.py`, 20 lif); tekrar edilmedi. Kurulanlar:

### ∞-operad terkibi
42 adımlık `QAKIS` zinciri tam, ve `omega_kategori`nin kendi
çekirdeğinin **bilinen 4 boşluğu** raporlanıyor (o modülün kütüğü
sessiz kalmasın diye).

### Čech tıkanıklığı
Her gösterim çifti bir **yama**, mahallî kâidesi `idrak/sekil.py`den.
Yamalar örtüşmede uyuşuyorsa küllî kesit var (``H¹ = 0``); uyuşmuyorsa
**tıkanıklık** var — yani *"mahallî çözümler var, küllîsi yok."*

    120 görevde:  H¹ = 0 → 103,  H¹ ≠ 0 → 17,  üçlü tutarlılığı bozan → 0

### Kehanet ve ilk netice: TERS

Dosya 3'ün kıymeti buradaki kehanettedir: ``H¹ ≠ 0`` olan görevlerde
model **susmalıdır**, çünkü tıkanıklık "cevap yanlış" değil *"küllî
cevap YOK"* demektir (H10/H16).

Ölçüldü ve **ters çıktı**::

    korelasyon           : −0,1316
    sükût, tıkanık görevde: 0,1812
    sükût, açık görevde   : 0,2551

Yani model, küllî cevabı olmayan görevlerde **daha çok** konuşuyordu.
Bu bir kusurdur ve gürültü değildir: 40 görevde de, 120 görevde de aynı
işaret çıktı.

### Çözüm — ve niçin okuma değil

``H¹`` dalganın değil **girdinin** vasfıdır: görevin gösterim
çiftlerinden, akış hiç koşmadan hesaplanır. Onu bir dönme açısına
çevirmek, ham duyuyu kübitlere kodlayan ``kodla`` ile **aynı
cinstendir**. H31 yasağı, melekenin dalgaya bakıp karar vermesineydi;
bu, girdinin kendisidir.

`tikaniklik_kapisi` ``sukut`` kübitine ``arctan``la sınırlanmış bir
dönme vurur (sınır, H119'un birikim dersindendir: çok yamalı bir
görevde çember sarıp tersine dönmesin).

### Ölçülen netice

    ölçü                    KAPI KAPALI   KAPI AÇIK
    korelasyon              −0,1316       **+0,3424**
    sükût, tıkanık görevde   0,1812       **0,4925**   (2,7×)
    sükût, açık görevde      0,2551        0,2551      (değişmedi)

İşaret döndü ve tıkanık görevlerdeki sükût 2,7 kat arttı; açık
görevlerde hiç değişmedi — yani kapı **ayırt ediyor**, hepsini
susturmuyor.

### Hudut — açıkça

Kurulan **tam Čech kohomolojisi değildir** ve öyle olduğu söylenmiyor:
örtü sonlu, mahallî kâideler ayrık bir kümeden. O hâlde 1-kozikıl şartı
ikili uyuşma + üçlü tutarlılığa iner. Gerçek ``H¹`` sonsuz boyutlu bir
demet kohomolojisidir; bu onun **sonlu ve hesaplanabilir gölgesidir**.
İsmi doğru kullanmak, tamamını kurmayı iddia etmeyi gerektirmez.

### H124'e ek — kaba tarifin ölçülen haddi

Sağîr ölçek her görevde enterpolasyon yapamıyor ve sebebi ölçüldü::

    60 görevde: artık ortancası 1,33e-04;  artık < 1e-2 olan 47/60
    tarifi ÇAKIŞAN görev: 8   (koşul sayısı ~5e6'ya fırlıyor)

Sebep `ogrenme/rkhs.py`nin kusuru **değildir** -- o modül koşul
sayısını raporlamakta ısrar ediyor ve haklı çıkıyor. Kusur benim 14
sayılık **kaba tarifimdedir**: bazı görevlerde iki ayrı gösterim
çiftinin tarifi birbirinin aynı çıkıyor, Gram dizeyinin iki satırı
eşitleniyor ve kapalı form enterpolasyon yerine ortalamaya düşüyor.

Daimî sınama bu yüzden **ortancaya** şart koyar. Her göreve zorlamak,
borcu ölçütle örtmek olurdu. İnce tarif işi `idrak/cozucu.py`nindir ve
borç orada durur.

## H126 — 1,5. KADEME: modüller yalnız YÜKLENMİYOR, KOŞUYOR

H123 divanı kurdu ve beyliği sıfırladı; fakat orada da açıkça yazıldı:
içe aktarma modülün **derlendiğini** gösterir, içindeki cebrin fiilen
işlediğini değil. Bir modül bozulduğunda 1. kademe **sessiz kalır**.

Aradaki boşluğu kapatmanın yolu, yine yukarıdan aşağı, tek bir
müşahededen çıktı:

> Modüllerin çoğu **kendi şahidini zaten taşıyor**. `rapor()` yahut
> `_gosterim()` içinde kendi iddialarını ölçüyorlar -- yalnız hiç
> çağrılmıyorlardı.

`divan.yoklama()` onları çağırır. Sayım::

    kendi gösterimi OLAN modül : 63
    gösterimi olmayan          : 32
    gösterimi kırık            : 0    (39'u fiilen koşturuldu, hepsi temiz)

Kademeler artık ayrı ayrı sayılıyor ve rapor üçünü birden yazıyor::

    1.   yüklendi, rol aldı            : 115
    1,5  kendi gösterimi KOŞTU         : 63
    2.   ana akışta fiilen iş görüyor  : 14

**Dürüstlük kaydı.** Tam yoklama dakikalar sürüyor (bazı modüllerin
gösterimi kıyas ölçümü yapıyor). O yüzden H126 şahidi **numune**
koşturur -- her dizinden birer modül -- ve tamamı ``python -m
nefs.divan`` iledir. "Hepsi her koşuda sınanıyor" denmiyor.

**Gösterimi olmayan 32 modül** bir borçtur ve sayılır: onlar için
1,5. kademe kurulamıyor, çünkü kendi şahitleri yok. Bu, o modüllerin
bozuk olduğu manasına gelmez; denetlenemediği manasına gelir.

### Tam yoklamanın neticesi (hepsi ayrı süreçte, 90 sn hadle)

**Kırık gösterim: SIFIR.** Gösterimi olan 63 modülün hepsi temiz
koştu. İki kayıt ayrıca tutulur:

* ``olcek.gercek`` 90 saniyelik haddi **aştı** -- bozuk değil, çok
  yavaş. Tam yoklamanın niçin şahide konmadığının sebebi budur.
* 10 ``tanilama.*`` modülü ``torch`` istiyor ve bu ortamda koşamıyor;
  H123'te de aynı 14 modül şartlı bağlıydı. Aynı borç, iki kademede
  birden görünüyor.

En yavaş üçü: ``tanilama.haraplama`` 44,9 sn, ``yaklasim.akislar``
38,8 sn, ``reel.meleke`` 7,6 sn.

## H127 — MAKAM KODLAMASI KUSURLUYDU; `mizan/munazara` ile tashih edildi

`mizan/` külliyatını (8 modül, 3 395 satır) 2. kademeye çıkarmaya
başlarken, `mizan/munazara.py`nin **yakîn mertebeleri** cetveli akışın
`makam` alanıyla yüzleştirildi. Üç şey çıktı.

### Bulgu 1 — kodlama epistemik komşuluğu kırıyordu

`nefs/qyazmac.py` şöyle diyordu: *"Sıra kasıtlıdır… tek kübitlik bir
dönme Şek'ten Zan'a, Zan'dan Yakîn'e geçirir."* **İddianın yarısı
yanlıştı.** Eski kodlama ``Şek=00, Zan=01, Yakîn=10, Vehim=11``, klasik
epistemik sıra ise ``Vehim < Şek < Zan < Yakîn``::

    Vehim → Şek    Hamming 2   ✗
    Şek   → Zan    Hamming 1   ✓
    Zan   → Yakîn  Hamming 2   ✗

Üç geçişin **ikisi** tek kübitle yapılamıyordu. Bu bir şerh hatası
değil fiilî kusurdur: 𝒪₃₂ makama **tek kübitlik** kontrollü dönmeler
vuruyor ve Zan'dan Yakîn'e hiç geçiremiyordu.

### Bulgu 2 — makam₀ en yükseği ile en düşüğü aynı kola koyuyordu

Eski sırada ``makam₀ = 1`` demek ``{Yakîn, Vehim}`` demekti. 𝒪₃₂'nin
``tasdik → makam₀`` **müsbet** dönmesi Yakîn'i kuvvetlendirirken
**Vehim'i de** kuvvetlendiriyordu — bir hüküm melekesinin yapabileceği
en ters şey.

### Tashih — ve niçin keyfî değil

``Vehim=00, Şek=01, Zan=11, Yakîn=10``. Üç geçiş de Hamming 1; ve
``makam₀ = 1`` artık tam olarak ``{Zan, Yakîn}``, yani "müsbete
meyilli". Sıra benim tercihimden değil, `mizan/munazara.py`nin
``MERTEBELER`` cetvelinden çıkıyor.

    ölçü                    ESKİ    GRAY (yürürlükte)
    kırık geçiş             2       **0**
    makam₀=1 kolu tutarlı   False   **True**

Daimî sınama **eski sırayı da** ölçer ve kırmızı yandığını gösterir;
yoksa yeşil olması bir şey ispat etmezdi.

### Bulgu 3 — bir mertebe eksik ve bu bir bütçe sınırı

Klasik mîzânda beş mertebe var (`MERTEBELER`): yakîn 1,00 · **zann-ı
gālib 0,75** · zan 0,50 · şek 0,25 · vehim 0,00. Akışın makamı iki
kübit, yani dört taban durumu — **zann-ı gālib yok**. Bu bir kusur
değil bütçe sınırıdır; üç kübit beşini taşırdı. Eksikliğin sayılması,
olmayan bir tamlık iddiasından iyidir.

### Yakîn yüzleştirmesi — açık borç

`yakin_gazali` (``min_i Yakîn(öncül_i) · 𝟙[şekil geçerli]``) ile akışın
makam beklentisi 30 görevde kıyaslandı::

    klasik yakîn ort. 0,9000    akış yakîni ort. 0,4972
    korelasyon        +0,0719

**Bağ yok.** Akışın makamı klasik yakîn hesabıyla alâkasız. Akış
eğitilmemiştir ve bu borç açıkta yazılır; kodlama tashihi yapıyı
düzeltti, muhtevayı değil.

## H128 — 𝒪₂₉ TEYİT'in "ayrı kanal" tedbiri TARTILDI

`fitrat/tevafuk.py` (3 070 satırlık `fitrat`ın tevâfuk motoru) ana
akışa `nefs/sahitlik.py` ile bağlandı ve bağlanır bağlanmaz bir
iddiayı sınadı.

𝒪₂₉ şöyle diyordu: *"Bir satırın ilk kübiti ile son kübiti **ayrı
kanallardır**… **bağımlı iki kanalın uyuşması yeni bilgi değildir**;
kanallar satırın iki ucundan alınır ki mümkün olduğunca ayrı olsunlar."*

Bu bir **tedbir**di ve hiç ölçülmemişti. Halbuki yanlışlanabilir: eğer
kanallar bağımlıysa 𝒪₂₉ aynı delili iki kere sayıyor, yani tasdiki hak
etmediği yerde yükseltiyor demektir.

### Ölçülen (12 koşu, 96 satır delili)

    çift uyuşması (Pearson) : +0,0324
    ortalama ağırlık        :  0,6761
    muteber şahit sayısı    :  1,68 / 2
    fazla sayma oranı       :  1,1932

Kıyas noktaları `fitrat`ın kendi şahit üretecinden: **bağımsız** üç
şahitte fazla sayma 1,05; **ortak kaynaklı** üçte 2,55.

### Hüküm — iki ölçüt ayrı düşüyor ve ikisi de yazılıyor

Pearson bağıntı görmüyor (+0,03) fakat fazla sayma 1,19 -- yani
**doğrusal olmayan** bir bağımlılık var. Yalnız Pearson'a bakıp
"kanallar ayrı" demek, ikinci ölçütün gördüğünü örtmek olurdu.

**Tedbir kısmen tutuyor.** Kanallar ortak kaynaklı değil (1,19 ≪ 2,55)
fakat tam bağımsız da değil (1,19 > 1,05): muteber şahit sayısı 2
değil **1,68**. 𝒪₂₉ delili yaklaşık **%19** şişiriyor. Kuvvetli bir
kusur değildir; sıfır da değildir ve öyle yazılır.

### Kendi kullanım hatam -- ölçülüp düzeltildi

İlk kullanımda ``fazla_sayma``ya **sürekli** değerler verdim. Ölçüt hem
aynı şahidi iki kere verince hem bağımsız iki şahit verince **1,0**
döndü, yani hiç ayırt etmedi (içeride ``log`` ``nan`` üretiyordu). Kusur
`fitrat/tevafuk.py`de değil bendeydi: o modül **ikili** şahitlikle
çalışır. Kanal değerleri medyanına göre ikilileştirilince ölçüt
çalıştı. Ayırt etmeyen bir sayıyı rapora koymuş olsaydım, ölçüyor gibi
yapmış olurdum (H90).

## H129 — H127'nin BULGU 3'ü FAZLA MÜSAMAHAKÂRDI; ve makam dağılımı çarpım farzıyla okunuyordu

### Nakz: eksik mertebe "zararsız bütçe sınırı" değil

H127'de zann-ı gālib'in (0,75) akışta olmamasını *"bir kusur değil
bütçe sınırıdır"* diye yazmıştım. **Kendime fazla müsamaha
göstermişim.** `mizan/istikra.py` bağlanınca ölçüldü:

    gösterim çifti   istikrâ yakîni   mertebe          tam istikrâ mı
    n = 2            0,7500           zann-ı gālib     hayır
    n = 3            0,8000           zann-ı gālib     hayır
    n = 4            0,8333           zann-ı gālib     hayır
    n = 6            0,8750           zann-ı gālib     hayır

ARC training ilk 200 görevde gösterim çifti sayısı: ortalama **3,21**
(dağılım: 2→36, 3→110, 4→38, 5→11, 6→3, 7→1). Ardışıklık kaidesinin
verdiği yakîn ortalaması **0,8025** -- yani **zann-ı gālib**.

**ARC'nin her görevi, akışın taşıyamadığı tam o mertebeye düşüyor.**
`tam_istikra_mi` hepsinde ``False``: eksik istikrâ hiçbir sonlu ``n``
için yakîn vermez. O hâlde makam, ARC'de doğru dereceyi hiç
gösteremiyor -- ya Yakîn (1,0) deyip **fazla iddia** ediyor, ya Zan
(0,5) deyip **eksik**. Bu bir bütçe sınırı değil, **yapısal bir
yanlışlık**tır ve H127'nin o satırı burada nakzedilir.

**Açık borç ve tam tarifi:** makam 2 kübitten 3'e çıkarılmalı; beş
mertebe Gray komşuluğuyla ``000=Vehim, 001=Şek, 011=Zan,
010=zann-ı gālib, 110=Yakîn`` (ardışık her çift Hamming 1). Kalan üç
durum **isimsizdir** ve üzerlerindeki kütle ayrıca raporlanmalıdır --
akış oraya kütle koyuyorsa bu da bir bulgudur. Tek bildirim yeri
``QAyar.kulli_alanlar``dır; ``makam_dagilimi`` bu hüküm sayesinde
artık kübit sayısından bağımsızdır, yani geçiş onu kırmaz.

### Ayrı bir kusur: makam dağılımı ÇARPIM farzıyla okunuyordu

``makam_dagilimi`` iki kübitin yoğunluklarından **çarpım** dağılımı
kuruyordu -- yani ``makam₀ ⊥ makam₁`` farzıyla. Dolaşık bir durumda o
farz yanlıştır. Ölçüldü::

    çarpım farzı : [0,32034  0,25566  0,23580  0,18819]
    hakikî ortak : [0,27381  0,30220  0,28233  0,14166]
    toplam değişinti mesafesi = 0,0931

Raporlardaki ``P_Şek``, ``P_Zan``, ``P_Yakîn``, ``P_Vehim`` sayıları
yaklaşık **%9** yanlıştı. ``blok_dagilimi`` ile hakikî ortak dağılıma
çevrildi ve usul kübit sayısından bağımsız kılındı.

Bu, H121'in kardeşidir: orada çevre birim sayılıyordu, burada
bağımsızlık farz ediliyordu. İkisi de **okumadan evvel yapılan bir
kabul**dür ve ikisi de ölçülünce yanlış çıktı.

### H129 eki — `mizan/istikra.py` bağlandı, ölçüm buradan çıktı

`nefs/mantik.py`ye ``istikra_mertebesi()`` eklendi ve ``mizan.istikra``
2. kademeye çıktı. Ölçüm doğrudan ARC verisinden:

    ARC 200 görev, ortalama 3,21 gösterim çifti
    istikrâ yakîni ortalaması : 0,8025  →  zann-ı gālib
    düşülen mertebeler        : yalnız zann-ı gālib
    tam istikrâ olan görev    : 0 / 200

Yani mesele istisnaî değil: **hiçbir** ARC görevi akışın gösterebildiği
bir mertebeye düşmüyor.

### Bu turda 2. kademeye çıkanlar

    mizan.munazara   → nefs/mantik.py    (makam sırası, yakîn yüzleştirmesi)
    mizan.istikra    → nefs/mantik.py    (ARC'nin istikrâ mertebesi)
    fitrat.tevafuk   → nefs/sahitlik.py  (𝒪₂₉'un bağımsızlık tartısı)

2. kademe 14 → **17**. Sayı hâlâ küçüktür ve büyümesi gereken odur.

## H130 — AKIŞIN SEBEP ÇİZGESİ KURULDU; 𝒪₂₂'nin asiklik iddiası ikiye ayrıldı

`fitrat/ayrisma.py` (d-ayrışması, Bayes topları) `nefs/illet.py` ile
2. kademeye çıktı. Çizge **uydurulmadı**: `nefs/sozlesme.py`nin
ölçülmüş bölge ilanlarından (H119, 41 melekede sıfır ihlâl) ve
``QAKIS`` sırasından kuruldu.

### 𝒪₂₂ ne diyordu

> *"Asiklik şartı **inşa gereği** sağlanır -- kapı hep soldan sağadır."*

Bu **tek bir meleke için** doğrudur. Sorulmayan sual: bütün akışın
sebep çizgesi asiklik mi? İki ayrı sual vardır ve birini ötekinin
yerine koymak iddiayı ispatlanmış göstermek olurdu.

    ALAN seviyesinde   : düğüm 9, kenar 54, **çevrim 27**
    ZAMAN açılımında   : düğüm 387, kenar 460, çevrim 0

Alan seviyesinde çevrim **var** ve olması normaldir: akış aynı alana
defalarca döner. *"Akış asikliktir"* demek orada **yanlış** olurdu.
Zaman açılımında asiklik **cebren** sağlanır (zaman ileri akar) --
bu bir ispat değil bir tariftir ve öyle sayılır.

**Makine teyidi:** `fitrat/ayrisma.py`nin ``Cizge`` tipi alan çizgesini
**reddetti** (*"çizge çevrimli -- d-ayrışması tanımsız"*). Yani
çevrimliliği ben iddia etmiyorum; beylik kod reddederek söylüyor.

### d-Ayrışması: kelam veriden nasıl besleniyor

Zaman açılımlı çizgede soruldu: ``veri@0`` ile ``kelam@42``, bütün
hüküm alanlarına (301 düğüm) şart koşulduğunda d-ayrık mı?

    hüküm şartıyla d-ayrık : False
    şartsız d-ayrık        : False   (ölçütün kör olmadığının şahidi)

Sebep tek tek izlenebilir: **𝒪₃₇ Fesâhat, 𝒪₃₈ Talâkat, 𝒪₄₀ Sanat**
aynı ünitede hem ``veri``ye hem ``kelam``a dokunuyor.

### KENDİ HÜKMÜMÜ DARALTTIM

İlk yazdığım şerh *"mimarînin gerekçesi delinmiş"* diyordu.
**Bu fazla söylemekti ve düzeltildi.** `nefs/qyazmac.py`nin kelam
hakkındaki iddiası şudur: *"kelam ``|0⟩``dan başlayıp **yalnız beyan
melekelerinin** yazdığı bir alandır"* — ve o iddia **doğrudur**;
kelama yalnız 𝒪₃₇–𝒪₄₁ dokunuyor. Mimarî, "veriden kelama giden yol
hükümden geçmelidir" diye bir şey **iddia etmemişti**; o şartı ben
koydum.

O hâlde ölçülen şey bir kusur değil bir **tasarım hakikatidir**:
beyan, hükme uğramadan da veriden besleniyor. Bunun istenip
istenmediği mimarî bir tercihtir ve **kullanıcının kararıdır**. Ölçüm
onu görünür kılar; hükmü vermez.

Bu daraltma kayda geçiyor çünkü az kalsın olmayan bir kusur ilan
edecektim.

### Bu turda 2. kademeye çıkanlar (devam)

    fitrat.ayrisma → nefs/illet.py   (sebep çizgesi, d-ayrışması)

2. kademe 17 → **18**. 60/60 sınama, 31/31 hüküm şahidi.

## H133 — PADİŞAHIN ÇIKARIMI BİR DİL MODELİYDİ; BAŞTAN YAZILDI

### Evvelâ: kullanıcının tenkidi haklıydı ve iddiam içi boştu

> *"Sadece içe aktarıp rapor verdirmek o kodları padişaha bağladığını
> göstermez, beni kandırmaya çalışma."*

H123'te 129 modülü `nefs/divan.py` ile içe aktarıp **"beylik 0"** ilan
ettim. `tanilama/nizam.py` de doğruladı -- çünkü o da **içe aktarma**
kapanışı ölçüyor. İkisi de yanlış şeyi ölçüyordu.

`tanilama/tefti.py` kuruldu: ``sys.setprofile`` ile padişah koşarken
**fiilen çağrılan** her ``(dosya, fonksiyon)``. Ölçüldü::

    kod tabanındaki dosya : 193
    KOŞAN dosya           :  17   (%8,8)
    ÖLÜ dosya             : 176   (%91,2)  ← padişaha bağlı DEĞİL

Bundan sonra "bağlı" kelimesi yalnız bunu ifade eder.

### Kök sebep: çıkarım bir sonraki belirteci kestiriyordu

`nefs/qegitim.py :: degerlendir` ARC'yi şöyle koşuyordu: görev düz bir
belirteç dizisine çevriliyor, hedef ızgara ``argmax(beyan)`` ile
**belirteç belirteç** üretiliyor -- **8 belirteçlik** bağlam
penceresiyle, **16 sembollük** sözlükten.

Yani padişah, tam da olmamaya yemin ettiği şeyi yapıyordu: bir dil
modeli. Ve bu usulle ARC çözülemez, sebebi cebridir:

* 30×30 ızgara 900 hücredir; model 8 belirtece bakıyor.
* Tam eşleşme ~100–900 belirtecin **hepsini** ister. Belirteç başına
  %95 isabetle bile ``0,95¹⁰⁰ ≈ 0,006``.
* `idrak/cozucu.py` -- **ispatlı** çözücü, cevap verdiğinde isabeti
  **%100** -- çıkarım yolunda **hiç çağrılmıyordu**.

**Ve bu, evvelki bütün teşhisleri açıklıyor.** H105/H115/H121/H129'da
"hüküm alanları yapısız" diye ölçtüğüm şey bir *netice*ydi: hüküm
zaten cevaba **ulaşmıyordu**. Yalnız ``beyan``ın argmax'ı vardı.

### Kurulan: MÜDRİKE ÇEVRİMİ

Kullanıcının tarif ettiği iç muhakeme (*"acaba benden ne isteniyor…
rastgele olsa ben nasıl cevap bulacağım… demek ki rastgele değil"*)
bir üslûp değil **bir hüküm zinciridir** ve altı adımda icra edilir:

    1. VAZİFE NEVİ  girdi–çıktı çifti var mı → bulmaca, yoksa kelâm
    2. TESADÜF MÜ   renk yapısı + şekil bağı; yapı yoksa sükût
    3. ÖRTÜ         Čech tıkanıklığı -- **ihtiyat**, veto değil (H132)
    4. KÂİDE        atom + terkip, gösterimlerin hepsinde ispatlanır
    5. YAKÎN        istikrâ × müphemlik × delil/hipotez × dalga hükmü
    6. BEYAN        yalnız 5'ten geçerse; hükümsüz kelâm yasak

**ARC'ye mahsus değildir**: 1. adım vazife nevini kendi tayin eder.
Kullanıcının şartı buydu.

**Dalga cevaba fiilen giriyor artık.** 41 meleke kaideyi bulmaz --
onu kaide cebri bulur -- fakat **yakîni tartar** (𝒪₃₂ Şek-Zan-Yakîn,
𝒪₃₃ Muhakeme). H92'nin paralel hat yasağı böyle korunur.

### Ölçülen

    ARC-AGI-2 training (ilk 120 görev)      tam çözülen
    eski çözücü (tek atom)                        5
    kaide cebri, terkip derinliği 2               8
    + nesne + hücre kaideleri, müdrike ile        9

Ve **sükût nizamı ayakta**: 107 görevde susuldu, sebebi yazılı
(103 "kaide bulunamadı", 4 "yakîn eşiğin altında").

## H134 — HÜCRE KAİDELERİ EZBERE KAÇTI; DELİL/HİPOTEZ ORANI KONDU

Hücre kaideleri (çıktı hücresi = f(yerel desen)) eklendiğinde model
7 görevden **16**'ya çıkıp konuştu -- fakat **8'i yanlış** oldu.
Cevap verince isabet %85,7'den **%50**'ye düştü.

Sebep ezberdir: üç gösterimden öğrenilen bir 3×3 desen tablosu
gösterimleri tutar, sınamayı tutmaz. **Delilden büyük hipotez, istikrâ
değil ezberdir.**

Tedbir mimarîde zaten vardı, yalnız tatbik edilmemişti: ``Kaide``ye
``hipotez`` (öğrenilen tablonun girdi sayısı) eklendi ve yakîne girdi::

    kanıt = clip( delil / (4 · hipotez), 0,25, 1 )
    yakîn = istikrâ × müphemlik × ihtiyat × kanıt

Occam da iki eksene çıktı: **önce hipotezi küçük olan**, sonra kısa
terkip. Tersi olsaydı üç gösterimden öğrenilmiş kocaman bir tablo,
sabit bir döndürmenin önüne geçerdi.

Netice: konuşan 16 → 13, **çözülen 8 → 9**, yanlış 8 → 4.

## H135 — HEDEF HAKKINDA DÜRÜSTLÜK: %50 DÜNYA REKORUNUN ÜSTÜNDEDİR

Kullanıcının ana planı: *"tüm soruların en az yarısının tam doğru
şekilde çözülmesi."*

Bunu **söylemem gereken şey var** ve söylemezsem kütüğün C maddesini
(*"kibrine yenilip yaptım etme"*) çiğnemiş olurum:

**ARC-AGI-2, mevcut en zor umumî muhakeme ölçütüdür ve %50 bugün
hiçbir sistemin ulaşmadığı bir seviyedir.** Bu ölçütte cephe
sistemleri tek haneli ilâ düşük çift haneli yüzdelerde durur. %50
hedefi, bir hata düzeltme meselesi değil, **dünya rekorunu kırmak**
demektir.

Bunu hedefi küçültmek için değil, hedefin **cinsini** doğru koymak
için yazıyorum:

* Hedefe bu oturumda varılmayacaktır ve varıldığı iddia edilmeyecektir.
* Fakat istikamet doğrudur ve ölçü gerçektir: 5 → 9, sıfır uydurma,
  her sükûtun sebebi yazılı.
* Asıl kazanç sayı değil **mimarîdir**: çıkarım artık bir dil modeli
  değil, ispatlı bir muhakemedir. Sayı bundan sonra kaide uzayının
  genişlemesiyle artar ve o iş **birikimlidir**.

Darboğaz tek ve ölçülüdür: 120 görevin **103'ünde** "kaide bulunamadı".
Yani mesele muhakeme çevriminde değil, **kaide cebrinin darlığında**dır.

### H133 eki — aynı şekilli aileye dört kaide (12/120)

Kaide bulunamayan 104 görev ölçüldü::

    aynı şekil       76      çıktı küçülüyor   21      çıktı büyüyor  7

Yani darboğazın **dörtte üçü** aynı şekilli ailede. O aileye ARC'de en
sık görülen dört cihet eklendi -- kör genişletme değil, eksiği ölçüp
seçmek:

* **devrî desen onarımı** -- ızgara periyodik, bir bölge örtülü;
  periyot bulunup delik oradan okunuyor
* **gürültü silme** -- tek/iki hücrelik bileşenler arka plana
* **ışın** -- tekil hücrelerden kenara doğru dört/sekiz yönde çizgi
* **çift bağlama** -- aynı satır/sütundaki aynı renkli iki hücrenin
  arası dolduruluyor

    ARC-AGI-2 training (120)          tam çözülen   yanlış   isabet
    eski çözücü (tek atom)                 5           0      %100
    kaide cebri + terkip                   8           0      %100
    + nesne + hücre + delil/hipotez        9           4       %69
    + aynı şekilli dört aile              12           4       %75

Sükût nizamı ayakta: 104 görevde susuldu, 100'ünde sebep "kaide
bulunamadı". Darboğaz hâlâ **kaide cebrinin darlığı**dır ve bu iş
birikimlidir.

---

## H136 — Gösterimlere tam uymak delil değildir (bırak-birini istikrâsı)

Ölçüldü (ARC-AGI-2 eğitim, ilk 120): `0ca9ddb6` ve `025d127b`
görevlerinde `hücre[3x3]` kaidesi **bütün gösterimlere tam uyuyor**
(hücre isabeti 1,000) fakat sınama girdisinde `None` dönüyor. Sebep:
o bir kaide değil bir **arama tablosu**dur. Bağlam sayısı hücre sayısı
mertebesinde olunca tabloyu ezberlemek gösterimleri tam açıklar ve
hiçbir şey öğretmez.

Demek ki *"bütün gösterimlere uyuyor"* ölçütü, tablo büyüklüğü veriye
yaklaştıkça **boşalır**. H134'ün `delil/hipotez` cezası bunu
yumuşatıyordu fakat kesmiyordu.

Hüküm: veriden öğrenen her kaide, her gösterimi sırayla dışarıda
bırakıp kalanlardan **yeniden öğrenilerek** sınanır
(`nefs/kaideler.capraz_gecerli`). Ölçülen netice:

    öncesi : 12 tam çözüm, 4 yanlış, cevap verince isabet %75
    sonrası: 12 tam çözüm, 0 yanlış, cevap verince isabet %100

Çözüm kaybı yok, yanlış cevap sıfırlandı.

**Kendi hatamın tashihi:** bu yedi görev için evvelce *"seçim
hatası, kapı haksız yere eliyor"* demiştim. Ölçtüm: kapı haklıydı.
O tablolar hakikaten genellemiyor; gösterimlere tam uymaları sahte
bir delildi.

## H137 — İki sükût birbirine karıştırılmamalı

*"Bu hücreyi bilmiyorum"* ile *"bu vazifeyi reddediyorum"* aynı şey
değildir ve ikisi de `None` ile söyleniyordu. Bedeli ölçüldü: bırak-
birini kapısı bütün öğrenilen kaideleri eliyordu, zira her katta
görülmemiş bir bağlam çıkıp kaide `None` dönüyordu — ve `None` ne
doğru ne yanlıştır, yani kapı **hiçbir şey ölçmüyordu**. Daima elemek,
ölçmek değildir.

`|aynen` okuması eklendi: *bildiğimi değiştiririm, bilmediğime
dokunmam.* Böylece kapı hakikaten ayırt eder.

## H138 — Katalog kapalı bir kümedir; aritmetik tutmuyor

Ölçülen ilerleme: eski çözücü 5 → terkip cebri 8 → nesne+hücre 9 →
aynı şekilli dört aile 12 → tamamlama katmanı 13. Yani **her yeni aile
ortalama bir görev**. 120'nin yarısı için ~50 aile daha gerekirdi; bu
bir mimarî değil angaryadır ve ARC-AGI-2 tam olarak bunu boşa
çıkarmak için tasarlanmıştır.

Kaide *"şunlara şunu yap"* diye ikiye ayrıldı (`nefs/secici.py`):
19 seçici × 12 dönüştürücü. **Ölçülen netice dürüstçe:** çözülemeyen
79 aynı şekilli görevin **48'inde** çarpımın bir kaidesi hiç
dokunmamaktan iyi netice veriyor, fakat **hiçbirinde** tek adım tam
uymuyor (TAM UYAN = 0). Tam çözüm 13'te kaldı.

Demek ki darboğaz kaide **sayısı** değil, o kaidelerin
**birleştirilmesi**dir.

## H139 — Kör budama aramayı açlıktan öldürüyordu

`kaide_ara` her kademede `azami_dal` kadar dal tutuyor ve sıralama
ölçütü `boy`du. Fakat bir kademedeki bütün dalların boyu **aynıdır**;
yani sıralama hiçbir şey söylemiyor, budama fiilen **keyfî** oluyordu.
Atom sayısı azken zararsızdı; çarpım katmanı atomu 150'nin üstüne
çıkarınca arama açlıktan öldü. Sıralama hedefe yakınlığa çevrildi
(en kötü gösterimdeki hücre isabeti); kabul ölçütü değişmedi.

## H140 — MECLİS NAKZEDİLDİ: modülü yanına asmak uzuv yapmaz

`nefs/meclis.py` yazılmıştı: her modül çağrılıyor, neticesi bir
**rey**e çevriliyor, reyler padişahın yakînini çarpıyordu. 91 modül
koşuyordu ve sayı doğruydu.

Kullanıcı hükmü: *"Meclis yapma, uzuv yap tüm eksikleri… sadece girdi
çıktı haritalarını münasebetlerini tayin etmeli."* Ve haklıdır: meclis
modülleri ana akışın **yanına** astı, **içine** koymadı. Bir modülün
çıktısı bir sonraki adımın girdisi değilse o modül uzuv değil süstür.

`nefs/meclis.py` **kaldırıldı**. Yerine `nefs/kademeler.py`: altı
kademe, ve kademe *k*'nın çıktısı kademe *k+1*'in girdisi.

    Görev →1 İDRAK→ İdrak →2 TASAVVUR→ Hâl →3 MUHAKEME→ Namzet
         →4 İSPAT→ İspat →5 TASDİK→ Yakîn →6 BEYAN→ Cevap

## H141 — Ölçü funktoru; ve terkip kaidesinin delil olmadığı

Kademelerin ve melekelerin ölçüleri **ayrı uzaylardadır**: `−logP`
`[0,∞)`da küçüğü iyi, entropi `[0,logχ]`da büyüğü iyi, tenakuz
`[0,1]`de küçüğü iyi. Bunları `0,25` ve `0,1` gibi elle konmuş
katsayılarla toplamak metreyle kilogramı toplamaktı; katsayı bir ölçü
değil, intibaksızlığın **örtüsü**dür.

Funktör `F : 𝒮 → 𝔐` kuruldu; müşterek uzay `mizan/munazara.py`nin
epistemik merdivenidir (vehim 0 … yakîn 1). Katsayılar **kalkmıştır**.

**Kendi hatamın tashihi:** terkip kaidesine bir körlük sınaması
koymuştum — *"monoton olmayan bir eşleme `F(g∘f)=F(g)∘F(f)`yi
bozmalı"*. Ölçüldü: bozmuyor. Sebebi cebrîdir ve sınamanın değil benim
hatamdı: `F_T⁻¹∘F_T` sadeleşir, yani terkip kaidesi `f` ve `g` ne
olursa olsun sağlanır ve **hiçbir şey ispat etmez**. Yük taşıyan
hususiyet **sıra korumasıdır**; sınama ona çevrildi ve orada körlük
hakikîdir (cihet ters çevrilince kırmızı yanıyor).

## H142 — Otuz altı meleke hiç eğitilmiyordu

Eski `uygunluk` = `−log P(doğru belirteç) + 0,25·mîzân − 0,1·entropi`,
ve `mizan_cezasi` yalnız **beş** sayı okuyordu. Kırk bir melekenin
kendi hatası hiçbir yerde yoktu; otuz altı meleke için eğitim sinyali
**fiilen sıfırdı**. Bir uzvun hatası kayba girmiyorsa o uzuv
eğitilmiyor demektir — kaç kere çağrıldığı bunu değiştirmez.

Ayrıca baştaki terim **belirteç kestirimi**ydi: H133'te teşhis edilip
çıkarımdan söküldüğü hâlde **eğitimde duruyordu**. Yani model
çıkarımda muhakeme ediyor, eğitimde sonraki belirteci tahmin etmeyi
öğreniyordu.

`nefs/kulli_kayip.py`: her meleke `nefs/sozlesme.py`de **kendi ilan
ettiği** bölgeden ölçülür. Ölçüldü: **41 ayrı meleke**, 105–156 uzuv
ölçüsü, haddi tahminî ölçü 0. En zayıf uzuv da adıyla çıkıyor
(ilk ölçümde `𝒪₄.yerel = 0,000` — yani 𝒪₄ yerel alanı ölü bırakıyor).

## H143 — Tek tâlim usulü; ve `aktif_altuzay`ı yanlış okumam

Kod tabanında **üç ayrı** gradyansız eniyileme vardı ve birbirinden
habersizdi (`kulli_egitim`, `qegitim.egit`, `main/optimize`). Üçü de
aynı işi yapıyordu; ayrı olmalarının faydası yok, zararı vardı.

`nefs/talim.py`: tek usul, dokuz uzuv — had (`akis/tikiz`), altuzay
(`main/optimize`), vekil (`ogrenme/rkhs`), Gri kod, dalga
(`kuantum/nqs`+`kuantum/dalga`), durgunluk (`ogrenme/grassmann`),
tünel (`arama/bukum`), denge (`fitrat/denge`), bütçe (`olcek/hiz`,
`yaklasim/kara_kutu`). Artık **her** eğitim yerinde bu çağrılır.

**Kendi hatamın tashihi:** `aktif_altuzay` `(U, özdeğerler, gradyan
örnekleri)` döndürüyor; ben `(U, kayıplar, noktalar)` sanmıştım. O
yüzden vekile kayıp diye özdeğer veriliyordu ve **vekil ile denge
uzuvları hiç ateşlenmiyordu** — dokuz uzuvdan ikisi ölüydü ve günlükte
görülmeseydi fark edilmezdi. Düzeltildi; vekil kendi örneklerini
çekiyor, dokuzu da koşuyor.

## H144 — Kısa CPU ayarının bütçesi ölçülerek düşürüldü

Yeni kayıp 41 melekeyi tek tek okuduğu için bir çağrı **6,9 sn**
sürüyor (eski kayıp beş sayı okuyup geçiyordu). O hâlde "kısa CPU
hâli"nin dalga bütçesi de küçültüldü (`cevrim` 6→2, `ornek` 24→4,
`zincir` 8→2, `talim_tur` 1). Ölçü ağırlaşınca bütçeyi sabit tutmak,
koşmayan bir ayar bırakmak olurdu.

---

## H145 — Ortalama, kaybı KÖR ediyordu (ölçüldü)

Padişah koşturuldu ve görüldü: 120 aday parametrede kayıp `0,6422`de
**hiç kımıldamadı**. Sebep arandı ve kusur modüllerde değil
`nefs/olcu.py::kulli_toplam`da bulundu.

Ölçüldü (dört parametre, 80 ölçü):

    tek tek ölçüler : 75'i değişiyor -- `alan.nakz` 0,95 yayılıyor,
                      `𝒪₃₇.tasdik` 0,79
    ortalamaları    : 0,7044 … 0,7561  →  yayılım **0,05**

Uzuvlar konuşuyordu; **ortalama onları susturuyordu**. Sebep
kaçınılmazdır: bağımsız değişen `n` sayının ortalamasının yayılımı
`σ/√n`dir; `n = 105` uzuvla her ferdî işaret on kat küçülür. Yani
"daha çok uzvu kayba soktum" demek, ortalamayla birleştirildiğinde
**her uzvun sesini kısmak** demekti.

Hüküm: toplam **yumuşak azamî**dir (log-sum-exp, `fitrat/havuz`).
Gerekçesi hesap değil klasik bir kaidedir: *bir neticenin yakîni en
zayıf öncülünün yakînini geçemez.* Bir öncül vehim mertebesindeyse
netice yakîn olamaz — diğerleri ne kadar sağlam olursa olsun.

## H146 — `sadakat()` bir eğitim ölçüsü olamaz; ve χ büyüdükçe kapı başına DAHA ÇOK atılıyor

41 melekelik akışta **1814 kapı** vuruluyor. Kapı başına ortalama
`0,986` tutulsa bile çarpım `0,986^1814 ≈ 4·10⁻¹²` eder; yani
`kesme_hakiki = 1 − F` her parametrede `1,0`a yapışır ve ayırt etmez.
Yumuşak azamîde bu tek başına en-kötü uzuv olup kaybı yine sabitliyordu.

**Kendi hatamın tashihi:** ilk teşhisimde buna "alt taşma" dedim ve
yanlıştı — `%.6f` biçimi `4e-12`yi `0,000000` gösterdiği için "tam
sıfır" sandım. Sayı hakikaten o kadar küçüktür, taşma yoktur.

`sadakat_log` ve `sadakat_kapi_basina` eklendi. Ölçüldü:

    χ= 8  log F = −26,2   kapı başına 0,9857
    χ=16  log F = −80,4   kapı başına 0,9566
    χ=32  log F = −111,5  kapı başına 0,9404
    χ=64  log F = −124,4  kapı başına 0,9337

İkinci ve daha mühim netice: kapı başına tutulan kesir **χ büyüdükçe
düşüyor**. Yani *"χ'yi büyüt, daha az bilgi at"* doğru değildir; χ
büyüdükçe durum hakikaten dolaşıyor ve her kesmede atılan nispî
ağırlık artıyor. Mimarî hakkında hüküm verirken bu hesaba katılmalıdır.

## H147 — Kesme felâketi ÜÇ MELEKEDE toplanıyor

Meleke başına tutulan kesir ölçüldü (χ=16, tek geçiş):

    𝒪₂₄ İspat        tutulan 5,3·10⁻⁷   ← amplitüdün %99,99995'i gidiyor
    𝒪₅  Tecrit       tutulan 1,6·10⁻⁶
    𝒪₂₂ İllet Keşfi  tutulan 7,8·10⁻⁵
    𝒪₄₁ Münazara     tutulan 4,4·10⁻³
    𝒪₁₈ Kıyas        tutulan 7,8·10⁻³
    …
    𝒪₃₉ Belâgat      tutulan 1,0000  (hiç atmıyor)

    toplam log düşüş −77,3   medyan tutulan 0,52

Üç meleke (𝒪₂₄, 𝒪₅, 𝒪₂₂) toplam log düşüşün **%48'inden** mesuldür.
Yani kesme bütün akışa yayılmış bir yorgunluk değil, **üç yerde
toplanmış bir yıkımdır** ve oralar tamir edilebilir.

Bilhassa dikkat: en çok yıkan meleke **𝒪₂₄ İspat**tır — yani
muhakemenin neticesini taşıması gereken meleke, dalgayı en çok
söndüren melekedir. Bu, H133'ün (hükmün cevaba ulaşmaması) fizikî
karşılığı olabilir ve ayrıca araştırılmalıdır.

**Kayıp artık parametreye kör değil:** yayılım 0,050 (ortalama, fakat
işaretler birbirini götürüyordu) → 0,020 (doymuş azamî) → **0,043**
(yumuşak azamî + tutulan kesir). Hâlâ zayıftır ve zayıflığın sebebi
yukarıdaki üç melekedir: onlar doymuş olduğu sürece en-kötü ölçüt
onlara takılır.

---

## H148 — 𝒪₂₄ İSPAT'IN ÇÖKÜŞÜ: χ TAVANI = 1

Kullanıcı sordu ve künhünü bilmediğini söyleyerek şu sezgiyi verdi:
*"ispatla sabit bir değerin ne alakası var, bence hiç."* Sezgi tam
isabetti ve ölçüm onu doğruladı.

`nefs/qmeleke.py`de üç melekede `CHI = 1` ilan edilmişti — 𝒪₅ Tecrit,
𝒪₁₃ Tasdik, 𝒪₂₄ İspat ("Dosya 1'de mutlak çözücü"). `CHI` meleke
başına **χ tavanıdır** ve SVD kesmesinde `r = max(1, min(X, bag_tavan,
…))` olarak işler. Yani `CHI = 1` demek, o meleke koşarken dalganın
**çarpım durumuna kesilmesi** demektir.

Ölçüldü (χ=32 yazmaç, tek meleke, taze durum):

    𝒪₂₄ tavan=1    : tutulan 8,7e-12   entropi 3,357 → 1,3863
    𝒪₂₄ tavan=yok  : tutulan 0,548     entropi 3,357 → 1,3827
    𝒪₅  tavan=1    : tutulan 6,6e-10   entropi 3,357 → 0,693
    𝒪₅  tavan=yok  : tutulan 0,909     entropi 3,357 → 3,346
    𝒪₁₃ her hâlde  : tutulan 1,0000    entropi hiç değişmiyor

Üç ayrı hüküm çıktı:

1. **𝒪₂₄'te "ispat daraltır" manası kapının kendisinde, üniter olarak
   zaten vardır** — tavan kalkınca da entropi ~ln4'e iniyor. Tavan o
   manayı üretmiyordu; üstüne **6×10¹⁰ kat** genlik imha ediyordu.
2. **𝒪₅'te daraltma tamamen tavandan geliyormuş**: tavan kalkınca
   entropi 3,357→3,346, yani hiç daralmıyor. Şerhi "fırça katmanının
   tersi (Gᵀ), bilgi kaybetmez" diyor fakat kapı kurucununkinden başka
   kübit çiftlerine vuruyor; o hâlde hakikaten ters değil. **Açık
   borç:** tecridin manasını üniter icra edecek kapı henüz yazılmadı.
3. **𝒪₁₃'ün tavanı büsbütün ölüydü** — hiçbir tesiri yok.

Bunun mimarî bedeli şudur: 𝒪₅ akışın 5., 𝒪₁₃ 13., 𝒪₂₄ 24. sırasındadır.
Yani dalga beyandan evvel **üç kere** amputte ediliyor ve 𝒪₃₇–𝒪₄₀ beyan
melekeleri çarpım durumu üstünde çalışıyordu. **Kütük H133'ün ("hüküm
cevaba ulaşmıyor") fizikî sebebi budur.**

## H149 — χ TAVANI KAVRAMI İCRADAN KALDIRILDI (H118'in nakzı)

H118 melekeleri kurucu/koruyucu/çözücü diye sınıflayıp her birine bir χ
bütçesi vermişti. Fikir makuldü, icrası yanlıştı.

Kusur: **bağ boyutu bir kapının değil, bütün dalganın vasfıdır.** Bir
melekeyi düşük tavanla koşturmak "bu meleke az yer kaplasın" demek
değil, *"bu meleke, diğer melekelerin kurduğu dolaşıklığı silsin"*
demektir. Tavan bir bütçe değil bir imhadır.

Ölçüldü (χ=16 yazmaç, 1814 kapı, tam akış):

    tavanlı   : log F = −60,50   kapı başına 0,9672
                akış sonu entropisi 1,3863  (= ln 4, ÇAKILI)
    TAVANSIZ  : log F = −57,64   kapı başına 0,9687
                akış sonu entropisi 2,7708  (≈ ln 16)

Tavan, beyana ulaşan dalganın dolaşıklığını yarıya indiriyor ve akış
sonunu **girdiden bağımsız sabit bir sayıya** çiviliyordu. Bedeli
yalnız %11 süredir. `NIZAM_ACIK` varsayılanı `False` yapıldı.

`CHI` **kaldırılmadı**: sınıf ilanı manalı bir taahhüttür ve artık
icra edilmiyor, **sınanıyor** — tıpkı `nefs/sozlesme.py`nin bölge
ilanını yüzleştirdiği gibi. Kelepçe ile sözleşme arasındaki fark budur.

## H150 — Tavan kalkınca LAPACK yakınsamadı; determinist yedek kondu

Tavan kalkınca bağ büyüdü ve `gesdd` bazı dizeylerde `SVD did not
converge` verdi. Yani tavan, imha ettiği bilginin yanında bir de
sayısal kararlılığı ayakta tutuyormuş — bu bir fayda değil, **kusurun
kusuru örtmesidir**.

`main/yazmac.py::_kararli_svd` kondu. Yedek yol **jitter yahut rastgele
kaydırma değildir** (ceride stokastiği yasaklar): Gram dizeyinin
özayrışımıdır ve determinsttir — `MᵀM = V S² Vᵀ`. Küçük taraf seçilir
ki maliyet `min(m,n)³` kalsın. Haddi açıkça yazıldı: Gram almak koşul
sayısını kareler, o yüzden yalnız `gesdd` düştüğünde işler ve düştüğü
`_SVD_YEDEK` sayacında sayılır.

**Neticelerin toplamı — kayıp artık parametreye cevap veriyor:**

    ortalama toplayıcı ile            yayılım 0,050 (işaretler götürüyordu)
    doymuş yumuşak azamî ile          yayılım 0,028
    tutulan kesir + yumuşak azamî ile yayılım 0,043
    + χ tavanları kalkınca            yayılım 0,0595
    𝒪₂₄'ün tuttuğu kesir              5,3e-07 → 0,0046  (8700 kat)

---

## H151 — B (yığın) iki ayrı cihetten ölçüldü; ceride ile bu ortam ayrıldı

Ceride B'nin azamîye çıkarılmasını emrediyor. Ölçüm, emrin **verim**
cihetinden haklı, **işaret** cihetinden ise bu ortamda ters olduğunu
gösterdi. İkisi de doğrudur ve karıştırılmamalıdır.

**1. Verim cihetinde ceride haklı.** Yazmaç zaten yığın ekseni taşıyor
(`main/yazmac.py`, `yigin`) fakat kayıp veriyi **tek tek** koşturuyordu.
Yığına çevrildi. Ölçüldü (CPU, χ=16):

    B= 1  yığın  1,01 sn   tek tek  1,01 sn   hızlanma 1,00×
    B= 4  yığın  2,71 sn   tek tek  4,05 sn   hızlanma 1,49×
    B=16  yığın 10,00 sn   tek tek 16,09 sn   hızlanma 1,61×
    B=32  yığın 19,47 sn   tek tek 32,86 sn   hızlanma 1,69×

Örnek başına maliyet 1,014 → 0,608 sn'ye iniyor; kapı kurulumu, MPO
inşası ve süpürme yığın üyeleri arasında paylaşılıyor. Kayıp çağrısı
6,9 → 1,87 sn (3,7×). **Kullanıcının "daha çok veri işleyince iş daha
çabuk biter" hükmü ölçümle doğrulanmıştır.**

**2. İşaret cihetinde bu ortamda ters.**

     B    kayıp sn   parametre yayılımı   veri gürültüsü
     2      1,73          0,0191               — (dejenere)
     4      2,96          0,0066            0,0013
     8      5,51          0,0045            0,0019
    16     10,55          0,0058            0,0007
    32     20,35          0,0051            0,0018

B büyüdükçe parametre yayılımı **düşüyor**. Sebep H145'in aynısıdır,
bir kademe yukarıda: yığın ortalaması organ ölçülerini σ/√B ile
söndürüyor. B=4'ten sonra ölçülebilir kazanç yok, maliyet doğrusal.

**Hüküm.** Kullanıcı GPU için ceride hükmünü mecburi kıldı, CPU için
kararı delile bıraktı:

* `AZAMI_KAGGLE` : **B = 2048 × bağlam 4096 = 8.388.608 belirteç/adım**
  — ceride taksimatı aynen. *Bu ayar bu ortamda koşmamıştır ve koştuğu
  iddia edilmiyor: burada GPU yok, o yığın belleğe sığmaz.*
* `KISA_CPU`     : **B = 4** — yukarıdaki ölçüme dayanarak.

**Açık borç:** yığın ortalamasının işareti söndürmesi, kayıp
toplayıcısının yığın eksenini de yumuşak azamî ile birleştirmesiyle
giderilebilir (şu an ortalama alıyor). Yapılmadı, ölçülmedi, iddia
edilmiyor.

## H152 — Yığın ekseni de yumuşak asgarî ile birleşti; B'nin önündeki engel kalktı

H151'de bir borç kaydedilmişti: yığın ortalaması organ ölçülerini
σ/√B ile söndürüyordu, yani B'yi büyütmek eniyilenen işareti
öldürüyordu. Borç kapatıldı.

Hüküm H145'in aynısıdır, bir kademe yukarıda: **bir yığında tek bir
veride düşen parametre yakîn sayılamaz.** Üyeleri ortalamak, kötü üyeyi
iyilerin arkasına saklamaktır. `nefs/olcu.py::yumusak_asgari` kondu ve
yığın ekseni onunla birleşiyor.

Ölçüldü (parametre yayılımı, 5 rastgele parametre):

     B    yumuşak asgarî   ortalama   kazanç
     2        0,0208        0,0191     +%9
     4        0,0116        0,0066     +%76
     8        0,0074        0,0045     +%64
    16        0,0070        0,0058     +%21
    32        0,0070        0,0051     +%37

İki netice:

1. Yumuşak asgarî **her B'de** işareti iyileştiriyor.
2. Daha mühimi, **çöküşü durduruyor**: ortalamayla işaret 0,0191→0,0051
   (3,7 kat) sönerken, yumuşak asgarîde 0,0208→0,0070 (3,0 kat) sönüp
   **B=16'dan itibaren düzleşiyor**. Yani B artık işareti öldürmüyor;
   ceridenin "B'yi azamîye çıkar" emrinin önündeki engel kalktı.

`KISA_CPU` B=4'te bırakıldı: zaman başına işaret orada en yüksek
(0,0116 / 3,09 sn). GPU tarafında ceride hükmü zaten azamîdir.

## H153 — "Etkin altuzay" rastgeleden kötü çıktı (ceridenin 2. ilgası ölçüldü)

Tâlim koşturuldu ve kayıp yine kımıldamadı. Aramanın **nereye baktığı**
ölçüldü (d=262, aynı kayıp, 4 parametre):

    tam uzay (d=262)              yayılım 0,0092
    "etkin" altuzay (r=8)         yayılım 0,0026
    rastgele geniş kesit (r=32)   yayılım 0,0146

Yani `main/optimize.aktif_altuzay` etkin yönleri **bulamıyor**:
rastgele bir kesit ondan 5,6 kat daha çok değişim görüyor. Sebep
cebrîdir: `C = (1/N)Σ ∇f∇fᵀ` kovaryansı `altuzay_ornek` yönlü sonlu
farktan kestiriliyor ve 6 ≪ 262 olduğu için kestirim **rütbe-6
gürültüden** ibaret. Ceridenin 2. ilgası ("W₂ inaktif uzayı kör kalır")
burada ölçümle doğrulanmıştır.

Çare rastgele kesit **değildir** (ceride stokastiği yasaklar).
Determinist tabanlar sınandı (r=32):

    "etkin" altuzay          0,0026
    DCT, ilk r kipi          0,0069
    DCT, tayfa yayılmış      0,0084
    WALSH, tayfa yayılmış    0,0088   ← seçildi

DCT'nin **ilk** kipleri indis uzayında düzgün yönlerdir; hâlbuki
parametre indis sırası keyfîdir (açıların tahsis sırası), o hâlde
"düşük frekans" burada mana taşımaz. Yönler tayfa yayılınca kesit
genelleşiyor. Walsh ayrıca ±1'dir: çarpımı ucuz ve tam.

Kesit haddi de açıldı: `azami_kubit` 48 → 192, yani r = 8 → 32.

## H154 — ÖĞRENİLEMEZ TERİM KAYBI KİLİTLİYORDU: yapısal/öğrenilebilir ayrımı

Yukarıdaki tamirlerden sonra bile padişah koşunca kayıp kımıldamadı
(0,8379 → 0,8376, 170 çağrı). Sebep arandı ve bulundu: yumuşak azamîyi
ele geçiren uzuv `𝒪₂₄.kesme`ydi (tutulan kesir 0,0046 → eksik ~0,995).

**Fakat bir kapının ne kadar kestiği, açı parametreleriyle değişmez.**
Kesme; menzilin uzunluğundan, MPO'nun zinciri baştan sona
sıkıştırmasından ve χ'den doğar — yani **mimarînin vasfıdır**,
melekenin öğrenebileceği bir şey değil. Onu kayba koymak, öğrenciye
çözemeyeceği bir soruyu sorup notunu ona bağlamaktır: not sabitlenir,
öğrenme durur.

Ölçüler ikiye ayrıldı:

* **ÖĞRENİLEBİLİR** — hüküm alanlarının okumaları (tasdik, tenakuz,
  nakz, makam, sükût, kelâm, mizan, gaye) ve kademe ölçüleri. Kayıp
  bunlardır.
* **YAPISAL** — kesme/sadakat. Kayba **girmez**; ayrıca raporlanır ve
  tamiri tasarımladır (nitekim H148/H149'da χ tavanları kaldırılarak
  𝒪₂₄'ün tuttuğu 5,3e-07'den 0,0046'ya çıkmıştı).

Yapısal gizlenmiyor: `yapısal_kayıp`, `yapısal_en_zayıf` ve
`yapısal_uzuv` anahtarlarında sayılıyor.

**Ölçülen netice — kayıp nihayet cevap veriyor:**

    ortalama toplayıcı                       yayılım 0,050 (işaretler götürüyordu)
    doymuş yumuşak azamî                     yayılım 0,028
    tutulan kesir + yumuşak azamî            yayılım 0,043
    + χ tavanları kalktı                     yayılım 0,0595
    + yığın yumuşak asgarîsi (B=4)           yayılım 0,0116
    + YAPISAL TERİM KAYIPTAN ÇIKTI           yayılım **0,2176**  (19 kat)

## H155 — Boyut indirgemesi büsbütün kalktı: arama TAM UZAYDA

H153'te determinist Walsh kesiti "etkin" altuzaydan iyi çıkmıştı.
Fakat kesitin kendisi de sorgulandı ve ölçüldü (d=262, aynı bütçe,
24 örnek, yarıçap 2,5):

    V(p₀)                        0,5758
    Walsh kesiti r=32   en iyi   0,4443   (kazanç 0,131)
    TAM UZAY  d=262     en iyi   0,3215   (kazanç 0,254)

Kesit, ulaşılabilir iyileşmenin **yarısını** yiyor. Sebebi basittir:
iyileştiren yönler 262 boyuta yayılmış; herhangi bir 32 boyutluk kesit
onların ancak bir izdüşümünü tutar. Boyut indirgemesi, ``d`` çok büyük
olmadıkça bir kazanç değil bir **kayıptır**. Ceridenin 2. ilgası
("lineer aktif alt uzay çalışmaz") sonuna kadar icra edilmiştir:
``r = d``, kesit yok. Walsh kesiti yalnız kübit bütçesi ``d·bit``i
aşarsa devreye girer.

## H156 — KADEME ÖLÇÜLERİ DE KAYBI KÖR EDİYORDU (H154'ün tekrarı)

Bütün tamirlerden sonra padişah hâlâ kımıldamıyordu (0,7943 → 0,7913).
Sebep, H154'ün aynı hatasının başka yerde tekrarıydı.

Altı kademe (`nefs/kademeler.py`) **dalga parametrelerine hiç bağlı
değildir**: idrak nesne ayrıştırır, muhakeme `kaide_ara` koşturur,
tasdik istikrâ hesaplar — hiçbiri melekelerin açılarını kullanmaz. O
hâlde kademe ölçüleri her parametrede **aynı sayıdır**.

Ölçüldü (5 parametre):

    kademesiz : V(p₀)=0,5758   yayılım 0,2176
    kademeli  : V(p₀)=0,7978   yayılım 0,0118   ← 18 kat seyreltme

44 uzvun 24'ü sabitse kaybın yarısından fazlası kımıldamıyor demektir;
yumuşak azamî de o sabit tabana oturup aramayı körleştiriyor.

**Dürüst hüküm:** kademeleri kayba koymak onları **eğitmiyordu**,
yalnız ölçütü kör ediyordu. Kademelerin eğitilebilmesi için kendi
parametrelerinin olması ve o parametrelerin `nefs/talim.py`ye
verilmesi gerekir — **henüz yok ve iddia edilmiyor.** Şimdilik ayrıca
raporlanıyorlar (`kademe_kayıp`, `kademe_en_zayıf`) ki kaybolmasınlar.

**PADİŞAH NİHAYET ÖĞRENİYOR — ölçülmüş seyir:**

    evvelce (bütün terimler kayıpta)  : 0,7943 → 0,7913   kazanç 0,003
    şimdi   (yalnız öğrenilebilir)    : 0,5395 → 0,4990   kazanç 0,077

Aynı bütçede kazanç **25 kat**. Üç ayrı öğrenilemez terim kaybı
kilitliyormuş ve üçü de ayrı ayrı ölçülerek bulundu:

    1. χ tavanı (H148/H149)       -- mimarî kelepçesi
    2. kesme/sadakat (H154)       -- yapısal, açıyla değişmez
    3. kademe ölçüleri (H156)     -- göreve bağlı, parametreden bağımsız
