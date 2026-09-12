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
