# PADİŞAHIN TERTİBAT KARARLARI -- ÖLÜ DOSYALARIN MENFEZLERİ

Ferman 2-D gereği her tertibat kararı sorulur ve cevabı buraya
kaydedilir. Bu dosya `MUNASEBET_YURUYUSU.md`nin hükmünün icra
cetvelidir: orada tesbit edilen her ölü uzvun hangi menfeze
vidalanacağı burada yazılıdır.

**KAT'Î HÜKÜM:** *"Ölü dosyalar senin marifetsizliğinden dolayı ölü,
sakın ola silmeyeceksin!"* -- Ölü olmak bir imha sebebi değildir;
bir tertip vazifesidir (ferman 2-C). İmha ancak padişah bizzat
emrederse olur.

---

## ▓ KAİDE: TEK BELİRTEÇ TAHMİN EDİLMEZ -- QUDİT BÜTÜN İHTİMALİ TAŞIR ▓

> *"Dikkatini çekerim, kuantum mimaride **tek bir belirteç tahmin
> etmiyoruz**! Penceremiz mesela 1 milyon ise ve 200 bin kelimelik
> sözlüğümüz varsa **200.000^1.000.000 kadar ihtimali aynı anda**
> değerlendirebilmek için qudite kodlama yapıyoruz, mimarimiz böyle
> olmasa **kuantum olmasının bir manası kalmazdı**!"*

* Üretim bir "sonraki belirteci seç" ameliyesi **değildir**. Yazmaç
  `sözlük^pencere` mertebesindeki bütün dizileri **aynı anda** taşır;
  bu, tip vektörü (ferman 1-N) ile seviye kodlamasının varlık sebebidir.
* O hâlde arama (`nefs/ara.py`) tek bir belirtecin genliğini aramaz:
  **dizinin tamamının** genliğini arar.
* Bir yerde "en yüksek olasılıklı belirteç" diye tek başına bir seçim
  yapılıyorsa orada kuantum mimari **iptal edilmiş** demektir.

---

## 1. nefs/ara.py -- `ara()`, Grover/Dürr-Høyer

**KARAR: İKİSİ DE.**

1. **NAKİL memuriyeti** (ferman 2-P). `ÇUKUR` "durak" hükmü
   verdiğinde adımın yerine `ara()` geçer; `kuyudan_cik` kuyudan
   çıkarır, `en_iyiyi_ara` Dürr-Høyer asgarîsini bulur.
2. **Belirteçler seçimi** -- fakat yukarıdaki kaide ile: aranan şey
   tek belirteç değil, **dizinin kendisidir**. `soyle` üretim ânında
   ölçüm-çökmesinden evvel Grover ile genliği arar.

## 2. nefs/gor.py -- `Manzara`, `gor`

**KARAR: SİL.** Padişah bizzat emretti. Ferman 6'ya çarpan yolun
mezar taşıdır; ferman 2-B gereği kökünden kesilir. Tek müşterisi
olduğu `musahede.Gorev/ayir/genlige_gom/kaide` de yetim kalır --
onların menfezi ayrıca sorulur.

## 3. nefs/lif.py -- `Lif` defteri, `kodla`, `sadakat`

**KARAR: İKİ ŞIKKIN İKİSİ DE.**

1. **`sadakat` → yeni kefe.** Giriş mesafeleri ile kodlanmış
   mesafelerin sıra bağlılığı mizana **ayrı bir kefe** olarak girer
   (ferman 1-U: meclis yok). Bu, `QuditYazmac.sadakat()`ın daima
   1.0 dönen ölü ölçüsünün yerine geçen, **kırmızı yanabilen** ölçüdür.
2. **`Lif.defter` → münasebet haritası.** Hüküm B.4'ün kusuru budur:
   `Harita` her koşuda sıfırdan kuruluyor ve hazineye konmuyordu, o
   yüzden ferman 1-I'nin "müşterek münasebet haritası" hiç birikmiyordu.
   `Lif.defter`in üç kademesi (tip→kategori→uzay) o kalıcı haritadır;
   hazineye yazılır ve `melekeler.Lif` ile terkip edilir (ferman 3).

## 4. nefs/mantik.py -- istikra, Gray sırası, makam mertebeleri

**KARAR: ÜÇ ŞIKKIN ÜÇÜ DE.**

1. **ÜÇÜNCÜ MANTIKSIZLIK TAŞMASI.** Ferman 2-L mantıksızlığı iki
   taşma sayıyor (parite + belirteç); `eksik_mertebeler` +
   `komsuluk_denetimi` üçüncüsünü verir: makam mertebeleri arasında
   boşluk/atlama var mı. Hem **kendi kefesi** hem **hudut çarpanı**
   olur. `MAKAM_ESIKLERI` ferman 1-J gereği sabit yazılmaz;
   rezonanstan ölçülen bir fonksiyondur.
2. **Gray sırası → tip vektörü.** Belirteç kimliğinin basamak açılımı
   ikili sıra yerine **Gray sırasıyla** yapılır: komşu belirteçler tek
   basamakta ayrışır, `komsuluk_denetimi` bunu ölçer.
3. **`istikra_mertebesi` → tâlim tertibi.** Örnekler tümevarım
   mertebesine göre sıralanır; imleç (ferman 1-Y) kolaydan zora
   ilerler.

---

## ▓ KAİDE: CEVAPLAR ZABITLARDA MEKNUZDUR ▓

> *"Bana şu ana kadar sorduğun sekiz sualin hepsinin gerçek cevapları
> **yabana attığın zabıtlarda meknuz**."*
> *"Bu dosyayla yapman gereken asıl işler daha önce verdiğim
> zabıtların birinde mevcut... Zabıtları tekrar **tamamen tara**,
> daha fazlasını bulacaksın, **bulduklarını mutlaka not et!**"*

Bir uzvun menfezi **evvelâ zabıtta aranır**, sonra teklif edilir.
Zabıt okunmadan verilen tavsiye zayıftır ve bu turda üç kere zayıf
çıktı. Taramanın kaydı `ZABIT_TARAMASI.md`dedir.

---

## 5. nefs/gor.py -- İKİNCİ HÜKÜM (zabıt çelişkisi arz edildikten sonra)

**KARAR: SİL, NAZIRLIK BEŞE İNSİN.**

`KUME_8_NAZIRLIK_PLANI.md`nin altı fiili beşe iner:

    dusun · ara · tart · ogren · soyle

`dusun` manzarayı kendi kurar (`musahede.bak`ı doğrudan çağırır).
`gor.py` kesilir. `musahede.Gorev/ayir/genlige_gom/kaide` yetim
kalır; onların menfezi **ayrıca sorulacaktır**.

## 6. kuantum/surekli.py -- ALTI ŞIKKIN ALTISI DA

> *"Hem evvelkiler hem bu şıkların tamamını kabul ettim!"*

**Bu dosya bir CV kütüphanesi değil, BELİRTEÇ KODLAMASININ ASLIDIR.**

1. **Belirteç kodlamasının aslı.** `tutarli_durum` + `yer_degistirme`:
   tiktoken kimliği → tip vektörü → `D(x)|0⟩`. Örtüşme Gauss
   (`|⟨x|y⟩|² = exp(−‖x−y‖²)`) olduğu için geometri **kayıpsız**
   taşınır. Zabıt: *Kelime_ve_Durum_Kodlaması*, "Kabul edilen 2. Çözüm".
2. **`sikistirma` → SU(1,1) hiperbolik lif.** Poincaré diski:
   soyut kavram merkeze (ζ≈0), tikel kavram kenara (ζ→1).
   Cins-tür ağacı bu lifte yaşar. Zabıt: *Çoklu Sonsuz Kategorili
   Koherent Durum*, §3-A.
3. **Yarı geçirgen ayna → sonsuz seviye.** `isik_bolucu` +
   `sikistirma`: vakumdan sonsuz Fock mertebesi doğar; **sonsuz
   seviyeli qudit sonlu katsayıdan doğar**. Yazmaç ebadı artık
   ayardan değil bu doğuştan gelir (ferman 2-O'nun fizikî motoru).
4. **`ayna.py`nin motoru olsun** -- `vakum`/`sikistir` çift başlılığı
   kalkar, ayna buradan ithal eder.
5. **`kesme_hatasi` + `kuadratur_belirsizligi` → kefe** (ferman 5).
6. **`kerr` + `kubik_faz` → gayri-lineerlik**, ferman 7-D gereği
   Galois otomorfizmine **tercüme** edilir, fark sayıyla yazılır.

## 7. Kaggle üçlüsü -- TAHTA KİP OLARAK KATLANSIN

`main/kaggle_egitim.py` · `main/kaggle_cikarim.py` ·
`ogrenme/kaggle_donanim.py` → `KUME_9/A2`nin hükmü icra edilir:
*"main tek hâkim; `ne="kaggle"` kipine katlanır."* Üç dosya kesilir,
cevherleri (`ayar_sec` donanım yoklaması, `AZAMI_KAGGLE` bütçesi,
teslimat biçimi) tahta taşınır. **Teslimat artık gerçek motordan
gelir, girdiyi geri vermez.**

## 8. idrak/veri/soyutlamalar/ -- VERİ OLARAK KÜLLİYATA GİRSİN

236 dosya, 41 899 satır. Python olarak **hiç koşmazlar** (ferman 6
korunur); **metin olarak tâlime girerler**. Her `solution.py` o
görevin sözlü çözümüdür ve ferman 1-R(a)'nın *"ızgaradan başka sözlü
çözüm varsa onun da çıkması hedeflenir"* hükmüne tam oturur.
İmha yok: 41 899 satır muhakeme verisi motora yem olur.

## 9. nefs/musahede.py yetimleri -- `kaide` KESİLİR

**KARAR: `kaide` kesilsin (ferman 6).** Şahitlerden kâide çıkarmak,
cevabı motorun dışında üretmektir; `KUME_9/MERHALE D` `nefs/qkaide.py`yi
tam bu sebeple imha etmişti. Aynı hüküm buna da tatbik edilir.

`Gorev`, `ayir` ve `genlige_gom` için hüküm **verilmedi** -- tekrar
sorulacaktır.

## 10. nefs/hizli.py -- ÜÇ ŞIK KABUL, İMHA ŞIKKI REDDEDİLDİ

> *"2. imha şıkkı hariç diğer 3'ünü kabul ettim."*

**İMHA REDDEDİLDİ:** `kronecker` ve `cekirdek` **kesilmez**.
(Ferman 2-C: bu safhada çare imha değil tertiptir; `qcekirdek.py`nin
C aslıyla çift başlılık, ikisinden birini kesmekle değil, **menfezini
bulmakla** giderilir.)

1. **`SEKTOR` tek kaynak olur.** Zabıtın üç süperseçim sektörü
   (0-511 sentaks · 512-2559 ontoloji · 2560-4095 mantık,
   *Qudite Tip Tensörünün Kodlanma Nizamı* §IV) **asıldır**;
   `QuditAyar.kulli_alanlar` ondan türer (ferman 1-M: tek kaynak).
   Blok-diyagonal çarpım fiilen koşar (%60 tasarruf).
2. **`cekirdek` yaşar: Lie-Chebyshev motorudur.** Clenshaw-Chebyshev
   özyinelemesi, *Kuantum Metinlerindeki Cevherin Tahvili*nin **1.
   ameliyesidir**: durum genliği bellekte tutulmaz,
   `Φ_k(u) = Σ c_j T_j(u) + i Σ s_j U_j(u)` ile üretilir -- `T_j`
   genliği, `U_j` **Berry fazını** yönetir. `lif.kodla(KIP_LIE)` ve
   `qudit.durum` ile terkip edilir.
3. **`faz_cevir` → Cartan köşegeni.** Zabıt: *"evrimin %90'ı faz
   modülasyonudur; köşegen Hamiltonyenin tesiri matris çarpımı değil
   **noktasal çarpımdır**"* -- O(d²)→O(d), 4096×. `qyazmac.faz`ın
   `Z_m` defteriyle terkip: defter tamsayı biriktirir, `faz_cevir`
   noktasal öder.

## 11. ogrenme/optimize.py + izgara.py -- `bukulme_dizeyi` ADIM BOYU

**KARAR: `bukulme_dizeyi` + `duzenli_uydur` → adım boyu.**
Ferman 2-P yarıçapı `Keyfiyet / √tr(Fubini-Study)` diye tarif ediyor
fakat eğrilik ölçüsü zayıftı; adım boyu artık **eğrilikten** seçilir
(ferman 1-J: eşik bir fonksiyondur).

`sembolik_kapanis`, `artis_gradyani` ve `optimize.py`nin ilga edilmiş
`KulliOptimizer` gövdesi için hüküm **verilmedi** -- tekrar sorulacaktır.

## 12. matematik/ dörtlüsü -- DÖRT ŞIKKIN DÖRDÜ DE

> *"4 şıkkın hepsini de kabul ettim!"*

1. **`tip_teorisi.py` → `lif.py`nin motoru.** `KUME_9/MERHALE F`
   icra edilir: `Lif.ac` bir sözlük gezintisi değil **funktör
   tatbiki**, `Unfold` gerçek bir lif açılımı olur. NbE, Kan
   işlemleri, Glue, univalence fiilen koşar. Şerhten çıkarılacak
   cümle: *"iddia edilmiyor"*. **İddia edilecek ve ölçülecek.**
2. **`mizan.py` → zırhın mantık süpürmesi.** `KUME_3`ün hükmü:
   yasak kâideleri elle tutulmaz, `mizan.onerme`den **otomatik**
   türetilir; tenakuzsuzluk / ayniyet / kâfi sebep tek MPO
   süpürmesinde işaretlenir.
3. **`fitrat.py` → nedensellik kefesi.** *Quditte Negatif
   Olabilirlik* zabıtının şart koştuğu `ℒ_kategori` mizanda **yok**;
   `fitrat`ın Bayes-Ball d-ayrışması + karşıolgusal 3-pas o kefenin
   nedensellik kanadı olur.
4. **`geometri.py` → silsilenin "nokta" mertebesi.** `KUME_9/C3`ün
   harfi: nokta = Laplace–Beltrami tayf öz-durumları. Lif defterinin
   en alt kademesi buradan gelir; Grassmann `Log = U arctan(Σ) Vᵀ`
   mecz'in durgunluk denetimidir.

## 13. musahede.Gorev / ayir / genlige_gom -- ARC'A MAHSUS OLAN ÇÖPE

> *"Sırf ARC ızgarasını çözsün diye oluşturduğun ne kadar kod varsa
> içinde **ana motora zorlama olmayan bir katkısı olmadığı müddetçe**
> at çöpe!"*

Ferman **1-N-C** olarak CLAUDE.md'ye mühürlendi. Ölçü tektir: ana
motora **zorlama olmayan** tabiî bir katkı var mı?

* `kaide` -- kesildi (ferman 6).
* `Gorev`, `ayir` -- yalnız ARC görev çiftini ayırmak için var;
  aynı iş `idrak/arc.py:gorev_dizisi` akışında zaten var (çift
  başlılık). **Kesilir.**
* `genlige_gom` -- ızgarayı genliğe gömüyor; Karar 6 belirteç
  kodlamasının aslını `D(x)|0⟩` yaptı, o hâlde bu **ikinci bir
  kodlamadır**. Tabiî katkısı yok, zorlamadır. **Kesilir.**

## 14. ogrenme/optimize.py -- İKİ ŞIK: `_durgunluk` ve `_yon_asgarisi`

> *"İlk iki şıkkı kabul ettim!"*

1. **`_durgunluk` → ÇUKUR memuru.** Ferman 2-P'nin *"burası minimum
   muymuş bakalım -- dur yahut yürü"* hükmü. Grassmann asal
   açılarıyla ölçer; `matematik/geometri.py`nin `arctan` log
   haritasıyla terkip edilir.
2. **`_yon_asgarisi` → adımın analitik asgarîsi.** Yön analitikten
   geliyor (ferman 2-P), fakat o yön üstünde **ne kadar gidileceği**
   hâlâ kördü. GCL düğümlerinde Chebyshev serisinin analitik
   asgarîsine iner: tarama değil, **kapalı form**. Tek yönde koşar,
   316 eksende değil.

`_had_yaricap`, `_toptan_yon` ve `KulliOptimizer` gövdesi için hüküm
verilmedi; ferman 2-P'nin ilgası yerinde kalır.

## 15. ogrenme/izgara.py -- TASHİH: SEMBOLİK KAPANIŞ RAPORCU DEĞİLDİR

> *"Sembolik kapanışı bir **raporcu olarak bağlamayacaksın**! O ana
> kadar denenmiş noktaların oluşturduğu fonksiyona göre **tahmin
> edilen en iyi fonksiyonun türevine analitik olarak gitmek** için
> var o, ben öyle kurgulamıştım. Artış gradyanı işe yaramaz bir şeye
> benziyor, **sil**."*

**BENİM TEKLİFİM YANLIŞTI.** `sembolik_kapanis` bir yazıcı değil,
bir **vekil yüzey türevcisidir**:

    denenmiş noktalar  →  sembolik fonksiyon uydur  →  O FONKSİYONUN
    ANALİTİK TÜREVİNE GİT

Yâni ferman 2-P'nin analitik eğimiyle **aynı cinsten** bir uzuvdur ve
onun tamamlayıcısıdır: analitik eğim `ψ`den gelir, sembolik kapanış
**tarihçeden** gelir. İkisi de türevdir, ikisi de kör değildir.
Ferman 1-G'nin *"ana koda rapor yazmak yasak"* hükmü zaten bunu
söylüyordu; ben yine rapora çekmişim.

* **`artis_gradyani` → SİL.**

## 16. omega_kategori -- GİT TARİHÇESİNDEN GERİ ÇAĞRILIR

`yedek/` dizini **açılmaz** (ferman 2 muhafaza edilir). İki sürüm
(`omega_kategori/` 4 693 satır, `omega_kategori_nbe/` 5 026 satır)
git tarihçesinden çıkarılıp karşılaştırılır; NbE'de olmayan cevher
(geometri, ilişkiler, kütüphane, denklik, türetimler) doğrudan
`matematik/tip_teorisi.py`ye terkip edilir. **Ara depo yok, doğrudan
menfezine.** (`KUME_9/MERHALE E` böylece kapanır.)

## 17. nefs/qudit.py + kuantum/kapilar.py -- DÖRT ŞIKKIN DÖRDÜ DE

1. **`qudit.durum` + `hizli.cekirdek` terkibi.** Lie-Chebyshev
   üretecinin iki icrası tek kaynağa iner ve **canlı yola** konur:
   durum genliği bellekte açık dizi olarak tutulmaz, `Φ_k` ile
   üretilir (ferman 1-M).
2. **Gelfand-Tsetlin → sızıntı hududu.** Zabıt: *"GT interlacing
   `m_{i,j+1} ≥ m_{i,j} ≥ m_{i+1,j+1}` gereğince üst kategoriden alt
   uzaya meşru olmayan bütün kuantum sızıntıları cebirsel kısıtla
   **zaten sıfırdır**."* Bu, ferman 1-I'nin mantıksızlık huddunun
   **DÖRDÜNCÜ taşmasıdır**: mertebeler arası sızıntı.
   (Ferman 2-L böylece ikiden dörde çıkar: parite · belirteç ·
   makam mertebesi · GT sızıntısı.)
3. **`dik_iki_kubit` → matchgate.** Ferman 2-J'nin **en sıcak**
   aşkın satırı kapanır: `eigh` + `np.exp(−iλ)` dizey üsteli yerine
   `nefs/matchgate.py`nin Majorana kovaryansında SO(2N) Givens
   dönmesi (`χ_stab = 1`, ferman 7-A(1)).
4. **90 ölü kapı → meleke tuğla havuzu.** Her meleke elle seçilmiş
   değil, **kendi vazifesine denk düşen** kapıyı havuzdan alır.

## 18. TABAKALI MİZAN -- ÜÇ ŞIKKIN ÜÇÜ DE

> *"3. şıkkı kesin kabul ettim, ilk ikisinin çelişmediğini
> zannettiğim için hepsi kabul edildi diyorum."*

Üçü çelişmiyor; üçü **tek terkiptir**:

    Π_Kategori, Π_Uzay, Π_Nokta  ──►  her mertebeye izdüşür
                                          │
              ┌───────────────┬───────────┴───┬───────────────┐
              ▼               ▼               ▼               ▼
          ℒ_nokta         ℒ_uzay        ℒ_kategori         ℒ_tip
        (Born izi)   (Fubini-Study)    (funktör)        (Hodge)
          AYRI KEFE     AYRI KEFE       AYRI KEFE       AYRI KEFE

* **Dört mertebe dört ayrı kefedir** (ferman 1-U: meclis yok).
  `α, β, γ` elle yazılmaz, rezonanstan ölçülür (ferman 1-J).
* **`ℒ_kategori` yeni gelen cevherdir:**
  `‖M_{g∘f} − M_g·M_f‖_F²`. Zabıt: *"bu kayıp **dışarıdan bir etiket
  istemez**; sistemin kendi iç mantığının kendi kendini
  denetlemesidir."* Veri gerektirmeyen saf iç kefedir.
* **Üç izdüşüm operatörü kurulur** (`Π_Kategori`, `Π_Uzay`,
  `Π_Nokta`) -- depoda hiçbiri yoktu. Her kefe kendi mertebesine
  izdüşürülmüş durumdan ölçülür; zabıtın *"dalga kimi zaman
  uzaylarına, kimi zaman kategorilerine, kimi zaman noktalarına
  **ayrışacak**"* hükmü budur.

## 19. nefs/soyle.py -- ÜÇ FAZ, ÜÇÜ DE

1. **Üç faz kurulur:** Sükût · Teemmül · İfşa. Tâlimde ve çıkarımda
   aynı motor (ferman 1-H). Eşikler sabit değil, **topolojik
   invaryanttan** türer (ferman 1-J'nin zabıttaki aslı). Mihenk
   suali (ferman 2-F) artık *"cevap verdi mi"* değil **"hangi
   fazdaydı"** diye de okunur.
2. **İfşa-2: SORU SORMA kapısı.** *"Model sonsuz loop'a girmez;
   dışarıya soru sorar: 'kendi iç hafızam ve melekelerimle bu
   tenakuzu çözemiyorum, şu parametre lâzım'."* Ferman 1-I'nin
   kısırdöngü huddunun **çıkış kapısıdır**.
3. **Gevezelik kilidi:**
   `α_kelam(t+1) = α_kelam(t)·exp(−γ[λH(N) − I(N;G)])`.
   Üretilen kelime gayeye katkı vermiyorsa konuşma katsayısı
   cebirsel olarak söner. Belirteç taşması kefesinin kardeşidir.

## 20. nefs/ttkan.py + idrak/kubit.py

> *"3. şık hariç hepsi kabul edildi!"*

1. **`ttkan` → dizi zinciri.** *Qudite Tip Tensörü Zincirinin
   Kodlanması*: *"Tek token hesabı **lağvedilmiştir**; bütün dizi,
   sanal bağlarla (D) kenetlenmiş bir **Tip Tensörü Zinciri**
   hâlinde tek dalga olarak süperpoze edilir."* Ferman 1-N-B'nin
   (tek belirteç tahmin edilmez) taşıyıcısı budur.
2. **`ttkan` bir sıkıştırıcı DEĞİLDİR.** Ferman 7 *"SVD/MPS/bond
   truncation İPTAL, durum TAM tutulur"* diyor. Sanal bağ `D`
   belirteçler arası **funktör / Kan uzantısını** taşır; budama yok,
   **bağlantı** var. (`tt_ayristir`in kesme kolu bu sebeple kapanır.)
3. **`idrak/kubit.py` → KESİLİR.** Zabıt onu açıkça **Tuzak A**
   (düz ikili taban kodlaması, Hamming felaketi) ilan ediyor ve
   ferman 7 *"İkili kübit kodlaması → Qudit seviye kodlaması"* diye
   iptal etmiş. **Bütçe kipi olarak dahi kalmaz** (`KUME_9/C1`in
   *"ikili dal bütçe kipi olarak kalsın"* teklifi **reddedildi**).

## 21. ENİYİLEYİCİ -- ▓ TASHİH EDİLDİ, AŞAĞIDA KARAR 24'E BAKINIZ ▓

**Bu karar eksik bilgiyle arz edilmiştir ve Karar 24 ile
sınırlandırılmıştır.** `optimizasyon.md`ye dayandırılmıştı; halbuki
`terkip_layihas__12.md` (**NİHÂÎ TERKİP KARARNÂMESİ, 1 Eylül 2026**)
üç katmanı ismen ilga ediyordu. Aşağıdaki metin tarihçe olarak
bırakılmıştır; **yürürlükte olan hüküm Karar 24'tür.**

> *"İlk 3 şık kabul edildi!"*

Ferman 2-P'nin *"tek seferde analitik çözüm, o analitiğin kuantum hız
imkânından faydalanması"* hükmünün **aslî icrası** budur.

```
[ d boyutlu mesele ]
        │
        ▼  1. AKTİF ALT UZAY
   C = (1/N) Σ ∇f ∇fᵀ  →  özayrışım  →  W₁ ∈ ℝ^{d×r}
        │
        ▼  2. HEDEF SIZDIRILMIŞ VEKİL YÜZEY
   V_toplam(u) = V_GEK(u) + λ‖𝒢(u) − y_hedef‖²
        │        (Nyström ile düşük ranklı kuantum çekirdeği)
        ▼  3. BİZZAT DALGA YAYILIMI -- sanal zaman
   ∂ψ/∂τ = ∇²ψ − V_toplam·ψ ,   ψ = Σ c_n e^{−E_n τ} φ_n
        │
        ▼  4. TERS İZDÜŞÜM        x* = W₁ u*
```

* **MECZ'İN BEŞ MEMURU BU MİMARİNİN İÇİNDEDİR:**
  EĞİM = `W₁` · ÇUKUR = `e^{−E_n τ}` sönümlemesi · DUVAR = hedef
  cezası · VADİ = `∇²ψ` difüzyonu · NAKİL = tersine tavlama.
* **HEDEF SIZDIRMA = MİZANIN KENDİSİ.** Zabıtın `𝒢(u)` hedef kuralı
  bizde zaten var: **mizanın kefe vektörü**. `λ‖𝒢(u) − y_hedef‖²`
  terimine üç hudut girer (tenakuz / kısırdöngü / mantıksızlık);
  potansiyel yüzeyi böylece "kör kayıp" değil **keyfiyet** olur
  (ferman 1-J).
* **DALGA TÜNELLEME DEĞİL, SPEKTRAL SÜZMEDİR.**
  > *"Bu dalgayla yapılan şey artık kuantum tünellemeden farklı bir
  > şey."*
  `e^{−E_n τ}` sahte çukurları buharlaştırır; yıkıcı girişim onları
  sıfırlar, yapıcı girişim küresel çukurda tek tepe kurar.
  **Yay/boncuk (SQA) kullanılmaz** -- *"yaylı boncuklar sadece
  dalgayı taklit eden fakir bir yaklaşımdı."*
* `r ≤ 3` şartının ayrıca ölçülmesi **kabul edilmedi**.

## 22. FERMAN 2-J LİSTESİ -- HEPSİ AYNI TURDA TERCÜME EDİLİR

> *"Hepsi aynı turda tercüme edilsin."*

Ferman 1-E: yarım iş yasak. Liste yazılmakla kalmaz; on iki aşkın
çağrının **hepsi** aynı turda Galois / Palmer / matchgate karşılığına
çevrilir ve fark **sayıyla** yazılır (ferman 7-D: tercümenin sıhhati
ölçülür).

    kararname (np.fft + np.exp)          mukayese.nesnelestir (np.exp)
    mukayese.bargmann (np.angle/acos)    usul.gedik_bul (arccos)
    tenakuz.dislama_dizeyi (np.exp)      rust.rust_kilidi (math.exp×2)
    qudit.suz (np.cos/np.exp)            zirh.taahhude_yuzlestir (tanh)
    zirh.zirh_kaybi (np.exp/log)         optimize.gaye_kos (np.tanh)
    zihin_durumu.donme (cos/sin)         melekeler.talim_kademesi (np.exp)
    eniyileme.tayf_araligi (eigvalsh×41) soyle (np.exp)
    kulli_mizan.holonomi (math.acos)     kapilar.dik_iki_kubit (Karar 17)

## 23. HÜKÜM B -- İKİ ŞIK

> *"İlk 2 şık kabul edildi."*

1. **`Harita` hazineye yazılır.** Ferman 1-I'nin *"müşterek münasebet
   haritası"* bugün hiç birikmiyordu; her koşu sıfırdan kuruyordu.
   Karar 3 `Lif.defter`i o kalıcı harita yaptı: hazineye konur ve
   ferman 1-Y'nin imleciyle beraber taşınır. **Bu, tâlimin
   hafızasıdır.**
2. **`duraklar` + `j` fiilen kullanılır.** Beş meleke (𝒪7, 𝒪21, 𝒪30,
   𝒪34, 𝒪37) durak ve kanal ayrımı veriyor, hepsi sektörün ortalama
   fazına çöküyordu. Ferman 1-U: her meleke ayrı kategoridir;
   ayrımlarının sessizce yutulması **meclisin ta kendisidir**.

`Tableau`nun işletilmesi Karar 17'de zaten verilmişti (`StabilizerDurum`
onun motoru oldu); `Hizolcer.sert` ve müdrike zinciri için hüküm
verilmedi.

---

## 24. ENİYİLEYİCİNİN NİHAÎ MİMARİSİ -- KARARNÂME İLE TERKİP

> *"İkisi terkip edilsin."*   ·   *"Beş memur dokuz uzva otursun."*

### (a) HANGİSİ ASIL

`terkip_layihas__12.md` (**NİHÂÎ TERKİP KARARNÂMESİ, 1 Eylül 2026**)
**asıldır**. Onun ismen ilga ettiği üç katman **kurulmaz**:

| Karar 21'de arz ettiğim (İLGA) | Kararnâmenin ikamesi |
| :-- | :-- |
| Lineer Aktif Alt Uzay `d → r ≤ 3` | `Gr(k,d)` **Cayley rasyonel çekilmesi** |
| Hedef şartlandırma `‖𝒢(u) − y_hedef‖²` | **QSVT dinamik Gibbs tavlaması** (β-annealing) |
| Sanal zamanlı PDE `∂ψ/∂τ = ∇²ψ − Vψ` | **Spektral taban projektörü `Π₀`** |

### (b) `optimizasyon.md`DEN KORUNAN TEK CEVHER

**Nyström düşük ranklı yaklaşımı** korunur -- çünkü kararnâmenin
kendi **İkmâl Fıkrası I**'i onu *"hata beyanı şartıyla"* kabul eder:

    K̃ = K_{N,m} K_{m,m}⁻¹ K_{m,N}   ,   m ≪ N
    ε_Nyström = ‖K − K̃‖_F           ← RAPORA BASILIR (ferman 5)

Yâni kısaltma yapılır fakat **feda edilen ne kadarsa sayıyla yazılır**.

### (c) 9 UZUVLU TÂLİM TEŞKİLATI -- KURULACAK OLAN

```
1. HAD        Alexandroff tek nokta tıkızlaştırması + Lions
              konsantrasyonu  (uçurumu ve asgarîsizliği engeller)
2. ALTUZAY    Cayley rasyonel çekilmesi, Gr(k,d)      (AS DEĞİL)
3. VEKİL      Grassmann izdüşümlü RKHS, Cholesky LLᵀ  (ters ALINMAZ)
4. KODLAMA    Causal KAN, O(N) deterministik ağaç
5. DALGA      Chebyshev-KAN NQS + QSVT Gibbs + FPAA monotonik difüzyon
6. DURGUNLUK  Grassmann asal açıları + kayıp varyansı (çift kriter)
7. TÜNEL      STA karşıt-adiyabatik sürüş H_CD(t)    (WKB DEĞİL)
8. DENGE      Çift sayılar autodiff (ε²=0) + OGDA
9. BÜTÇE      NFL haddi + ölçülen donanım çağrı sınırı
```

### (d) TETABUK -- BEŞ MEMUR DOKUZ UZVA OTURUR

Mecz (ferman 2-P) **ayrı bir kanat değildir**; dokuz uzvun
okunuşudur. Çift başlılık böylece doğmaz (ferman 1-Z):

    EĞİM   → 8. DENGE: çift sayılar autodiff. `ℝ[ε]/ε²=0` cebri
             SONLU FARK DEĞİL SEMBOLİK türevdir: tek ileri geçiş,
             kesme hatası sıfır. Ferman 1-V'nin türev yasağı yön
             kanadında kalkar; kayıp VEKTÖR kalır (ferman 1-U).
    ÇUKUR  → Morse-Euler KATÎ eşitliği  Σ(−1)ᵏ M_k = χ(X)
             + RCD(K,N) Bochner eğrilik süzgeci.
             Zabıt: *"Eşitsizlik (≥) kabul edilmez; katı eşitlik
             sağlanmadığı müddetçe çözüm eksik sayılır ve intaç
             ONAYLANMAZ."*  → `ogrenme/morse.py` bugün CANLI ve
             `assert` ile koşuyor; depodaki en sahih icralardandır.
    DUVAR  → 1. HAD: Alexandroff + Lions. `max(g, ε)` kırpması
             YASAK (kısıt geometrisini bozar); yerine log-bariyer
             iç nokta homotopisi.
    VADİ   → 7. TÜNEL: STA `H_CD(t)`, O(1) zamanda. Pasif WKB
             beklemesi (6,2×10⁸ deneme, M20) ilga.
    NAKİL  → Postnikov k-invaryantı `[c] ∈ H^{n+1}(X; π_n(Y))` ile
             tıkanan mertebe analitik tesbit edilir, oraya Cayley
             çekilmesiyle **instanton sıçraması** yapılır.
             (Karar 1'in `ara()` NAKİL memuru buraya oturur.)

### (e) CHOLESKY EMNİYET KİLİDİ = FERMAN 5'İN ZABITTAKİ ASLI

> *"Eğer regülarizasyon λ=0 iken matris tekilse, bu algoritma
> **gizlice hatalı katsayı üretmez**; deterministik olarak hata
> fırlatır (fail-safe) ve sistemi uyarır."*

`(K + λI)⁻¹` **açık matris tersi yasaktır**; `LLᵀ = K + λI`
ayrıştırması ve iki kademeli ileri-geri ikame ile çözülür. Koşul
sayısı `κ(K+λI)` sürekli denetlenir ve raporlanır.

---

## 25. AYRIK TOPOLOJİK MOTOR -- ÜÇ UZVU DA KURULUR

> *"3 şık da kabul edildi!"*

`tecrit.md`in **çift motorlu** mimarisinin ayrık kanadı. Kararnâme
ile ihtilafsızdır (İkmâl Fıkrası IV Postnikov'u aynen tescil eder).

1. **Postnikov k-invaryantı `[c] ∈ H^{n+1}(X; π_n(Y))`.**
   Tenakuzun **hangi mertebeye** sıçranacağını **cebirsel adres**
   olarak verir; kör arama yoktur. *"Gradyana gerek kalmaz;
   kohomolojinin kendisi, ihtiyaç duyulan dinamik mertebenin
   indisini hesaplayan bir funktöryel pusula vazifesi görür."*
2. **Tersine kuantum tavlama** ayrık mertebe vektörünü `D*` seçer:
   `ℋ_ayrık = Σ ‖H^{d_i}‖² + λ Σ (β₀^{(d_i)} − 1)²`.
3. **Kalıcı homoloji barkodu → `ogrenme/morse.py`ye.**
   `ℒ_topo = W_p(Barkod(mevcut), Barkod(hedef))` -- Wasserstein
   metriği parçalı diferansiyellenebilirdir. İşbölümü:
   * tamsayı Morse-Euler eşitliği → **hüküm** verir (ÇUKUR memuru),
   * Wasserstein barkodu → **kefe** olur ve öğrenilebilir.
4. **Tenakuz ayrık motora SİNYALDİR.** *"Sürekli dalga topolojik bir
   yırtıkla (`H^n ≠ 0`) karşılaşırsa, bu tıkanıklık ayrık motora
   sinyal olarak döner ve yeni bir dinamik mertebeye tünellenir."*
   Ferman 1-I'nin üç huddu böylece pasif ölçü olmaktan çıkıp **fiil**
   olur.

**FERMAN 1-V'NİN ZEMİNİ BURADADIR.** *"Ayrık bir kategori indisinin
(13 → 1000) **gradyanı alınamaz**."* Bazı kefelerin türevi yoktur;
o hâlde her şeyi tek skalere indiren bir kayıp zaten **imkânsızdır**.

## 26. YİRMİ UZAY VE FIRLATIM-GERİ ÇEVRİM -- ÜÇ ŞIK

> *"İlk 3 şık kabul edildi!"*

```
|Ψ_Nihai⟩ = Σ_m  F_m†  ( Π_koho^(m) · Π_betti^(m) · 𝒮_m · e^{−iηH_m} )  F_m  |Ψ⟩
             m ∈ {0..9} ∪ {d₁..d₁₀}
```

1. **`F_m` fırlatım + `F_m†` geri çevrim.** Dalga tek uzayda kalmaz:
   20 uzaya izometrik funktörle fırlatılır, her uzayda **o uzayın**
   Hamiltonyeni ile evrilir, sonra esas uzaya geri mühürlenir.
   Ferman 1-U'nun aslî manası budur: melekeler tek sandalyede değil,
   **kendi uzaylarında** çalışır.
2. **ZIRH UZAYA MAHSUS OLUR.** Zabıt: *"Sheaf, Homotopi, Betti ve
   Kohomoloji **haricî küresel bir şablon değildir**; her bir k'ıncı
   uzayın kendi iç yapısına mahsus olarak işletilir."* Bugün
   `nefs/zirh.py` tek bir global zırh koşturuyor -- ferman 1-U
   ihlâlinin ta kendisi.
3. **10 DİNAMİK MERTEBE HUDUTSUZDUR.**
   `D = [13, 17, 30, 55, 1000, 58383, 19, 1009, 60000, …]`
   Aradaki boş mertebeler **bellekte açılmaz**; Sparse Kan Extension
   (`Lan`) ile doğrudan sıçranır. Hangi 10 mertebenin açılacağını
   **Postnikov tıkanıklığı söyler**, elle yazılmaz (ferman 1-J).

## 27. ÖZERK DÖNGÜ -- ANA DÖNGÜ VE MUTASARRIFA

> *"1 ve 3. şık kabul edildi."*

1. **ANA DÖNGÜ ÖZERK OLUR.**

   ```
   her turda:
       Tenakuz  = iç çelişki serbest enerjisi (hafıza ↔ vahime ↔ illet)
       Gaye G_t = o tenakuzu sıfırlayacak hedef durum manifoldu
       Mutasarrıfa R_t = gayeye matuf strateji
       Teemmül  = adım
   ```

   *"Girdi `X = ∅` olduğunda durum tensörü **sıfırlanmaz**"* --
   veri varsa girer, yoksa **döngü yine döner**. Ferman 1-I'nin
   *"hata sıfırlanana kadar aynı veride kalınır"* hükmü bunun tabiî
   neticesidir.

2. **MUTASARRIFA = MECZ'İN KENDİSİDİR.** `R_t = Σ α_j 𝒪_j` zabıtta
   softmax ile yazılmıştı; ferman 1-U gereği **bu bir toplam
   olamaz**. Mutasarrıfa, Karar 24(d)'nin beş memurunun **vazife
   dağılımıdır**: hangi memurun o turda konuşacağını **tenakuzun
   cinsi** tayin eder. Ayrı bir kanat açılmaz (ferman 1-Z).

`nefs/gaye.py`nin canlandırılması ve üç fazla terkip için hüküm
verilmedi.

---

## 28. KARARNÂMENİN YEDİ UZVU -- SIFIRDAN YAZILIR

> *"Sıfırdan yazılsın."*

Git tarihçesinden geri çağrılmaz. Sebep açıktır: tarihçedeki eski
sürümler **ferman 7 ve ferman 2-P'den evvel** yazılmıştı ve ilga
edilmiş usuller taşıyorlar (kör hat araması, POVM, MERA budaması,
sürekli Hilbert). Cevher değil, **yük** getirirlerdi.

Dokuz uzvun bugünkü hâli:

    1. HAD        Alexandroff + Lions            YOK  → yazılacak
    2. ALTUZAY    Cayley çekilmesi Gr(k,d)       YOK  → yazılacak
    3. VEKİL      RKHS + Cholesky LLᵀ            YOK  → yazılacak
    4. KODLAMA    Causal KAN O(N) ağaç           YOK  → yazılacak
    5. DALGA      Chebyshev-KAN NQS + QSVT Gibbs YOK  → yazılacak
    6. DURGUNLUK  Grassmann asal açıları         CANLI ✓
    7. TÜNEL      STA H_CD sürüşü                YOK  → yazılacak
    8. DENGE      Çift sayılar ε²=0 + OGDA       YOK  → yazılacak
    9. BÜTÇE      NFL haddi + donanım sınırı     kısmî

    (+ Morse-Euler katî eşitliği `ogrenme/morse.py`   CANLI ✓)

Yazılırken kararnâmenin **dört İkmâl Fıkrası** bağlayıcıdır:
PSD tahkiki ve reel alan mecburiyeti · Cholesky emniyet kilidi
(`(K+λI)⁻¹` **yasak**) · Nyström hata beyanı `ε = ‖K−K̃‖_F` ·
Alexandroff/Lions tıkızlaştırma · Postnikov k-invaryantları ·
Morse-Euler katî eşitliği + RCD(K,N) Bochner.

**USUL:** Ferman 1 -- evvelâ taht, sonra ara kat, en son hususi.
Dokuz uzvun çağrısı `main/egitim.py`ye **yazılmadan** hiçbiri
yazılmaz.

## 29. YİRMİ DÖRT ÇİFT BAŞLI AD -- DÖRT ŞIK, FAKAT İSPAT CEBİRLE

> *"Hepsi kabul edildi fakat terkipte ispat **ölçülerek değil formül
> cebriyle** yapılmalıdır!"*

**FERMAN 3-B OLARAK CLAUDE.md'YE MÜHÜRLENDİ.** Benim
*"ikisi aynı cevabı veriyor mu, ölçülerek gösterilir"* teklifim
yanlıştı: bu bir ölçümdür (ferman 1-C/a ve 1-L yasağı) ve üstelik
ispat değildir -- iki fonksiyon bin girdide aynı çıkıp bin birincide
ayrılabilir.

    YASAK  `assert abs(a(x) − b(x)) < 1e-12` ile terkip ispatı
    ASIL   a'nın cebrinden b'nin cebrine KAPALI FORM türetmek

1. **Ferman 3'ün üç adımı** her ad için işletilir; ispat cebrîdir.
2. **Dört dizey üsteli → matchgate.** `_uexp` · `melekeler._genel_expm`
   · `devre._uexp` · `surekli.expm`. Cebrî indirgeme:
   `exp(−iθ c_p c_q)` Majorana kovaryansında `SO(2N)` Givens
   dönmesidir; `χ_stab = 1` (ferman 7-A/1). `expm` diye bir ad kalmaz.
3. **Üç stabilizer / üç Laplasyen / üç Betti.**
   * Stabilizer: `galois.Tableau` tek kaynak; `kuantum/stabilizer.py`
     onun motoru (Karar 17).
   * Laplasyen ve Betti: `kuantum/tda.py`nin kombinatoryal Hodge
     Laplasyeni `Δ_k = ∂_{k+1}∂_{k+1}ᵀ + ∂_kᵀ∂_k` **tek kaynaktır**;
     `morse.py` ve `zirh.py` ondan okur.
4. **Üç `Lif` → TERKİP DEĞİL, İSİM ISLAHI.** Üçü ayrı mertebedir,
   o hâlde ayrı ad alır (ferman 4):
   * `nefs/lif.py` = **tip** mertebesi (Karar 3),
   * `idrak/kategori.py:Uzay` = **uzay** mertebesi (Karar 12),
   * `melekeler.Lif` = melekenin taşıyıcısı.

## 30. OTUZ SEKİZ `rapor()` + `__main__` -- FERMAN 1-L İCRASI

**KARAR: `__main__` kesilir, `rapor()` tahta bağlanır.**

* `if __name__ == "__main__"` bloğu **35 ölü dosyada da kesilir**;
  yan koşu böylece **imkânsız** olur (ferman 1-L).
* `rapor()` fonksiyonları kalır fakat ancak **o uzuv tahta
  bağlandığında** tahttan çağrılır. Taht yalnız çağırır, metin
  kurmaz (ferman 1-G).
* **NİÇİN.** Bağlanmayan uzvun raporu da koşmaz -- ferman 1-C(b)'nin
  münafıklık kapısı (uzuv bağlanmadan rapor satırı yazmak) böylece
  fizikî olarak kapanır.

---

## 31. DÖRT KIRIK AD -- DÖRT ŞIK DA

> *"4 şık da kabul edildi."*

1. **`gorev_ozellikleri` KESİLİR** (ferman 1-N-C). Göreve mahsus
   öznitelik çıkarmak ferman 6'nın yasağıdır. `kulli_kayip.py:533`
   çağrı satırı **ve** `_dene`'nin çıplak `except`i beraber kesilir;
   `Hal.ozellik` artık **yazmaçtan** okur (ferman 1-M).
   *Bu, canlı yoldaki tek kırıktı: `oz` bileşeni sessizce düşüyordu.*
2. **`tunel_maliyet_cetveli` → TÜNEL uzvu.** `KUME_8`in tahsisi:
   *"`ayar.tunel_acik` kapısının **fiilî hesabı**; şu anda o kapı
   tünelin bedelini bilmiyor."* Karar 28'in 7. uzvu (STA `H_CD`)
   yazılırken beraber yazılır: WKB bedeli **ölçülür** (M20:
   6,2×10⁸ deneme), sonra STA ile `O(1)`e indiği gösterilir.
3. **`isaret_vur` → D=2 MPO çekirdeği.** `KUME_3`ün 7. dosyası:
   çok-kontrollü işaret MPO'su + ancillasız `R₀ = I − 2|0…0⟩⟨0…0|`
   yansıtması. Karar 12(2) `mizan.py`yi zırhın mantık süpürmesi
   yaptı; `isaret_vur` o süpürmenin **çekirdeğidir**.
4. **ON YEDİ ÇIPLAK `except` KESİLİR.** Ferman 5: *"`except` ile
   sessiz ikame yasaktır, yerine **assert**."* Hepsi aynı turda
   `assert`e çevrilir; boş dönen uzuv artık **kırmızı yanar**.

## 32. nefs/hamiltonyen.py -- ÜÇ ŞIK DA

> *"3 şık da kabul edildi."*

1. **YİRMİ UZAYIN HAMİLTONYEN ÜRETECİ.** `H_m(θ) = Σ_a θ_m^a T^a` --
   her uzayın kendi Lie cebri üreteçleri. `UzayHamiltonyeni` zaten
   bu adı taşıyor. 10 sabit uzay simplisiyal enerji matrisi (`H_k`),
   10 dinamik uzay yüksek mertebe Laplasyeni
   (`H_{d_i} = Δ_{d_i} + V_bağlam`). Karar 26'nın taşıyıcısıdır.
2. **`_cayley` → ALTUZAY uzvu.** Karar 28'in 2. uzvu Cayley rasyonel
   çekilmesidir ve kodu burada **zaten yazılı**:
   `R_Y(ξ) = (I − W/2)⁻¹(I + W/2)Y`. Sıfırdan yazılacak ALTUZAY onu
   kendi içine alır.
3. **SU(1,1) → `surekli.py` ile terkip.** Karar 6(2) `sikistirma`yı
   SU(1,1) üreteci yaptı; `hamiltonyen.py` de SU(1,1) lif grubunu
   taşıyor. İkisi **aynı cebirdir** ve ferman 3-B gereği **cebrî
   olarak** indirgenip tek kaynağa iner (ölçülerek değil).

## 33. kuantum/ üçlüsü -- İKİ ŞIK

> *"1 ve 3 kabul edildi!"*

1. **`tda.py` → DÖRTLÜ ZIRHIN MOTORU.** `KUME_3`ün attığı toprak:
   *"Yalnız kütüphane seviyesinde kalıp **zırh akışına MPO/projektör
   olarak bağlanmaması**."* Bundan sonra
   `Π_betti = exp(−λΔ_Hodge)` ve `Π_koho = I − Σ|ω⟩⟨ω|`
   fiilen `tda.py`den türer -- **her uzayda ayrı ayrı** (Karar 26/2).
   Kahan hassas toplaması korunur.
2. **`devre.QFT` → tayf mertebesi.** `KUME_9`: *"kuantum/devre
   (QFT = tayf)"*. Silsilenin **nokta** mertebesi Laplace–Beltrami
   tayf öz-durumlarıydı (Karar 12/4); QFT o tayfın taşıyıcısıdır.
   `devre._uexp` ise Karar 29(2) ile matchgate'e gider.

**KABUL EDİLMEYEN İKİ ŞIK:** `eniyileme.tayf_araligi`nın STA şartı
olması ve `parametre_kaydirma`nın kesilmesi. İkisi de **hükümsüz
kalır**; `kuantum/eniyileme.py` bugünkü hâlinde durur (fakat
`tayf_araligi`nın 41 kere `eigvalsh` çağırması ferman 2-J listesine
Karar 22 ile zaten girdi ve **aynı turda tercüme edilecektir**).

## 34. FORMUL.md ve SERH.md -- KOD DEĞİŞTİKÇE GÜNCELLENİR

> *"Kod değiştikçe güncellensin."*

Ferman 2-K'nın harfi: `FORMUL.md`ye **ancak fiilen koşan ameliye**
girer -- *"yazılmayan koşmaz, koşmayan yazılmaz."*

**Bu otuz dört karar henüz NİYETTİR, FORMÜL DEĞİLDİR.** Şimdi bir
"borç babı" açılmaz; her uzuv vidalandığı **turda** `FORMUL.md` ve
`SERH.md` beraber güncellenir. Ferman 5'in *"yapılmayan yapıldı diye
yazılmaz"* hükmü böylece en dar manasıyla tutulmuş olur:
yazılmamış olan, borç diye bile yazılmaz.

---

# ▓▓▓ İCRA CETVELİ -- OTUZ DÖRT KARARIN HÜLÂSASI ▓▓▓

**USUL (ferman 1, istisnasız):** evvelâ taht (`main/egitim.py`,
`main/cikarim.py`), sonra ara kat, en son hususi. Hiçbir dosya,
çağrısı tahta yazılmadan yazılmaz.

## A. KESİLECEKLER (padişah bizzat emretti)

    nefs/gor.py                     Karar 2, 5
    musahede.kaide                  Karar 9
    musahede.Gorev · ayir · genlige_gom   Karar 13 (ferman 1-N-C)
    idrak/kubit.py                  Karar 20 (Tuzak A)
    main/kaggle_egitim.py · kaggle_cikarim.py
      · ogrenme/kaggle_donanim.py   Karar 7 (tahta katlanır)
    ogrenme/izgara.py:artis_gradyani     Karar 15
    kulli_kayip.py:gorev_ozellikleri     Karar 31
    35 dosyada `if __name__ == "__main__"`  Karar 30
    17 çıplak `except` → `assert`        Karar 31

## B. MENFEZİNE VİDALANACAKLAR

    kuantum/surekli.py  → belirteç kodlamasının ASLI        Karar 6
    nefs/lif.py         → sadakat kefesi + münasebet haritası Karar 3
    nefs/mantik.py      → 3. mantıksızlık taşması + Gray     Karar 4
    nefs/ara.py         → NAKİL memuru + dizi araması        Karar 1
    idrak/kategori.py   → silsilenin UZAY mertebesi          Karar 12
    kuantum/stabilizer.py → Tableau'nun motoru               Karar 17
    kuantum/topolojik.py  → lifler arası morfizm             (kabul)
    nefs/hizli.py       → SEKTOR tek kaynak + Lie-Chebyshev  Karar 10
    nefs/qudit.py       → durum üreteci + GT sızıntı huddu   Karar 17
    kuantum/kapilar.py  → matchgate + meleke tuğla havuzu    Karar 17
    kuantum/tda.py      → dörtlü zırhın motoru               Karar 33
    kuantum/devre.py    → tayf mertebesi                     Karar 33
    nefs/hamiltonyen.py → 20 uzayın Hamiltonyeni + Cayley    Karar 32
    nefs/ttkan.py       → dizi zinciri (sıkıştırıcı DEĞİL)   Karar 20
    matematik/ dörtlüsü → tip/mizan/fitrat/geometri          Karar 12
    ogrenme/optimize.py → _durgunluk ÇUKUR, _yon_asgarisi    Karar 14
    ogrenme/izgara.py   → bukulme_dizeyi adım boyu           Karar 11
                        → sembolik_kapanis vekil türevi      Karar 15
    idrak/veri/soyutlamalar/ → 41 899 satır sözlü çözüm verisi Karar 8

## C. SIFIRDAN YAZILACAKLAR (Karar 28)

    HAD · ALTUZAY · VEKİL · KODLAMA · DALGA · TÜNEL · DENGE
    (+ BÜTÇE tamamlanır)

## D. KURULACAK BÜYÜK YAPILAR

    Tabakalı mizan: 4 kefe + Π_Kategori/Π_Uzay/Π_Nokta   Karar 18
    Üç faz: Sükût · Teemmül · İfşa + soru sorma kapısı   Karar 19
    Ayrık topolojik motor: Postnikov · tersine tavlama
      · kalıcı homoloji barkodu                          Karar 25
    20 uzay: F_m fırlatım + F_m† geri çevrim,
      uzaya mahsus zırh, hudutsuz dinamik mertebe        Karar 26
    Özerk döngü: Tenakuz → Gaye → Mutasarrıfa → Teemmül  Karar 27
    Harita hazineye · duraklar+j fiilen kullanılır       Karar 23
    Ferman 2-J'nin 14 aşkın çağrısı aynı turda tercüme   Karar 22
    24 çift başlı ad, CEBRÎ ispatla terkip               Karar 29
    omega_kategori git tarihçesinden terkip              Karar 16
