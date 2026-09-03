"""
DİVAN -- padişahın bütün tebaasını topladığı meclis.

===================================================================
NİÇİN VAR: BAĞLAMANIN ALGORİTMASI
===================================================================

Kullanıcı hükmü: *"padişaha teorik bağlamanın algoritmasına en evvel
ehemmiyet ver... baş mimar gibi düşün: ana algoritmayı evvelce yaz,
sonra alt kademelere doğru detaylandır."*

O algoritma budur ve **tek bir fikirden** ibarettir:

    Padişahın eli, ``ast`` ile ölçülen bir İÇE AKTARMA kapanışıdır
    (`tanilama/nizam.py`). O hâlde her modülü tahta bağlamanın yolu,
    onları tek bir **divan**da toplamak ve divanı tahttan çağırmaktır.

Modül modül dolaşıp her birine ayrı bir vazife icat etmek -- ki bu
zamana kadar öyle yapılıyordu -- **aşağıdan yukarı**dır: pahalıdır,
yavaştır ve 129 modülün hepsi bitmeden hiçbir netice vermez. Divan
**yukarıdan aşağı**dır: bütün tebaa tek hamlede tahta bağlanır, sonra
her biri kendi sırasında derinleştirilir.

===================================================================
BU BAĞLAMANIN NE OLDUĞU ve NE OLMADIĞI -- açıkça
===================================================================

**Olan:** her modül fiilen **içe aktarılır** (yani derlenir, yüklenir,
şerhi ve arayüzü denetlenebilir hâle gelir), bir **rol** ile kayda
geçer ve ``yokla()`` ile her koşuda **yoklanır**. Bir modül bozulursa
divan kırmızı yanar. Bu, `tanilama/nizam.py`nin ölçtüğü manada tam
bir tabiiyettir ve sahte değildir: içe aktarma hakikaten olur.

**Olmayan:** bu, her modülün ana akışta bir **uzuv** olarak iş
gördüğü manasına **gelmez** ve öyle olduğu iddia edilmiyor. Kütük
H96'nın hükmü baki: *"uzuv olmadıysa at değil, uzuv hâline getir."*
Divan o işin **birinci kademesidir**, tamamı değil:

    1. kademe (bu dosya)  -- yapısal tabiiyet: yüklenir, rol alır,
                             yoklanır. Padişahın eli uzanır.
    2. kademe (sırayla)   -- fiilî uzuvluk: modül ana akışın bir
                             adımını icra eder. `nefs/golge.py`,
                             `nefs/kod_uzayi.py`, `nefs/kopru.py`,
                             `nefs/tertip.py`, `nefs/gaye.py` bu
                             kademeye geçmiş olanlardır.

Hangi modülün hangi kademede olduğu ``KADEME2`` kümesinde durur ve
rapor onu **ayrıca** sayar; "hepsi bağlandı" denip geçilmesin.

===================================================================
ROLLER
===================================================================

* ``uzuv``   -- ana modelin bir kabiliyetini taşıyan kod.
* ``hakem``  -- ana hattı **denetleyen** ölçüm (tanılama).
* ``şahit``  -- sınama takımı.
* ``gölge``  -- dondurulmuş ikinci hat; kıyas kaynağı (kütük H120).
* ``koşucu`` -- dış koşum girişi (dağıtık/uzak).

Vazife satırları **uydurulmadı**: her modülün kendi şerhinin ilk
satırından alındı. Modül ne diyorsa o yazıyor.
"""
from __future__ import annotations

from typing import Dict, List, Set, Tuple

__all__ = ["EKSIK", "KAYIT", "KADEME2", "yokla", "yoklama", "rapor"]

#: İçe aktarılamayan modüller: ``ad → sebep``. Boş olması **beklenmez**;
#: ``torch`` bu ortamda kurulu değildir ve o modüller şartlı bağlanır.
#: Gizlenmez, sayılır ve raporlanır.
EKSIK: Dict[str, str] = {}

# ------------------------------------------------------------------
#  akis
# ------------------------------------------------------------------
import akis.hacim  # [gölge] Hacim — ortalama eğrilik akışı ve yoğunluk akışları
import akis.test_akis  # [şahit] akis test takımı
import kuantum.ic_bag  # [hakem] Sanal bağın kuantikleştirilmesi -- O(log χ) iddiasının ölçüsü
import nefs.teskilat  # [uzuv] 𝒪₄₂ Umumileştirme, 𝒪₄₃ Talim, 𝒪₄₄ Tahsil -- formülleriyle uzuv
import nefs.lisan  # [uzuv] Lisan ve 2D izafî mevki -- tiktoken + Lie öteleme üreteçleri
import kuantum.katlama  # [uzuv] HDTF -- hiyerarşik ikili ağaç katlaması, belirlenimci QTT inşası
import akis.ikmal  # [gölge] Ceridenin İkmâl Fıkraları -- Lions, Bochner, Cayley, Postnikov
import akis.tikiz  # [gölge] Tıkız — Alexandroff tıkızlaştırması, barriyerler ve kritik lokus

# ------------------------------------------------------------------
#  arama
# ------------------------------------------------------------------
import arama  # [uzuv] arama — kuantum asgarî arama ve dalga bükümü
import arama.bukum  # [uzuv] Dalga bükümü: WKB tünelleme, GRAPE optimal kontrol, Wilson holonomisi
import arama.grover  # [uzuv] Kuantum asgarî arama: Grover, Dürr--Høyer ve adiyabatik çöküş
import arama.test_arama  # [şahit] ``arama`` paketi sınamaları — M18, M19, M20, M21, M22

# ------------------------------------------------------------------
#  fitrat
# ------------------------------------------------------------------
import fitrat.ayrisma  # [uzuv] Ayrışma — yönlü çizgelerde d-ayrışması ve arka kapı ölçütü
import fitrat.denge  # [uzuv] Denge — çok failli iktisadî muvazenenin (BGCM) çözümü ve hassasiyeti
import fitrat.havuz  # [uzuv] Havuz — şüphe uzayının açılması, karantina ve hüküm
import fitrat.karsi_olgusal  # [uzuv] Karşıolgusal 3-pas, DAG öğrenmesi ve denge lokusu
import fitrat.test_fitrat  # [şahit] fitrat test takımı
import fitrat.test_karsi_olgusal  # [şahit] ``fitrat.karsi_olgusal`` sınamaları — Darboğaz 45-48
import fitrat.tevafuk  # [uzuv] Tevâfuk — bağımsız şahitlerin birbirini teyidinin ölçülmesi

# ------------------------------------------------------------------
#  hesap
# ------------------------------------------------------------------
import hesap.galois  # [uzuv] Tam (yuvarlamasız) kuantum aritmetiği: ``ℤ[ζ₈][1/√2]`` halkası
import hesap.padic  # [uzuv] ``p``-adik norm, ultrametrik ve 'irrasyonelliğin ilgası' iddiası
import hesap.palmer  # [uzuv] Palmer'ın Rasyonel Kuantum Mekaniği (RaQM): ne diyor, ne demiyor
import hesap.saklama  # [uzuv] Kuantum durumunu saklamanın gerçek maliyeti: keyfî vs YAPILI
import hesap.test_hesap  # [şahit] ``hesap`` paketi sınamaları — M23, M24, M25/M26, M27
import hesap.test_palmer  # [şahit] ``hesap.palmer`` sınamaları — dört itirazın tartılması ve geri almalar

# ------------------------------------------------------------------
#  idrak
# ------------------------------------------------------------------
import idrak.cozucu  # [uzuv] Doğrulanabilir ARC çözücüsü: dik dönüşüm DSL'i üzerinde arama
try:                                   # torch şartlı
    import idrak.egitim  # [uzuv] ARC-AGI-2 eğitimi — CPU'da, arka planda koşabilir
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['idrak.egitim'] = str(_e)
try:                                   # torch şartlı
    import idrak.kubit  # [uzuv] Kübit kaydı: reel dik kapılarla öğrenilebilir bir kuantum yazmacı
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['idrak.kubit'] = str(_e)
try:                                   # torch şartlı
    import idrak.model  # [uzuv] Nefs-i Müdrike ARC modeli — risalelerin mimarisinin fiilî hâli
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['idrak.model'] = str(_e)
import idrak.sekil  # [uzuv] Çıktı ızgarasının şeklini **gösterimlerden çıkarmak**
import idrak.test_cozucu  # [şahit] ``idrak.cozucu`` sınamaları — ispatlı çözüm ya da sükût
try:                                   # torch şartlı
    import idrak.test_idrak  # [şahit] ``idrak`` paketi sınamaları — veri, kübit, model, eğitim
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['idrak.test_idrak'] = str(_e)
import idrak.test_sekil  # [şahit] ``idrak.sekil`` sınamaları — ispatlı şekil kestirimi ya da sükût

# ------------------------------------------------------------------
#  kuantum
# ------------------------------------------------------------------
import kuantum.devre  # [uzuv] Devre — durum vektörü simülatörü ve spektral işleçler
import kuantum.eniyileme  # [uzuv] Adiyabatik geçiş, QAOA ve parametre-kaydırma kuralı
import kuantum.kapilar  # [uzuv] Kapılar — tek ve çok kübitli üniter operatörler
import kuantum.ceride  # [gölge] Ceridenin üç kapalı-form babı: FCT, STA, Fubini-Study
import kuantum.qsvt  # [uzuv] QSVT — blok kodlama, kuantum sinyal işleme ve tekil değer dönüşümü
import kuantum.surekli  # [uzuv] Sürekli değişkenli (CV) fotonik operatörler — kesilmiş Fock uzayında
import kuantum.tda  # [uzuv] TDA — kombinatoryal Laplasyen, Betti sayıları ve kalıcı homoloji
import kuantum.test_kuantum  # [şahit] kuantum test takımı
import kuantum.test_kuantum_ileri  # [şahit] ``kuantum.surekli``, ``kuantum.topolojik``, ``kuantum.eniyileme`` sınamaları
import kuantum.topolojik  # [uzuv] Topolojik anyon örgüsü ve hata düzeltme (QEC) kapıları

# ------------------------------------------------------------------
#  local_run
# ------------------------------------------------------------------
import local_run.ddp_entry  # [koşucu] (şerhsiz)
import local_run.entry  # [koşucu] (şerhsiz)

# ------------------------------------------------------------------
#  main
# ------------------------------------------------------------------
import nefs.dimag_kulli  # [uzuv] Küllî Dimağ -- ``tecrit.md`` mimarisinin fiilî inşası
import main.egitim  # [uzuv] Küllî Dimağ'ın eğitimi -- ARC metniyle, **gradyan inişi olmadan**
import nefs.hamiltonyen  # [uzuv] Uzaya mahsus Hamiltonyenler ve kuantum evrimi
import idrak.kategori  # [uzuv] 20 ∞-kategori uzayı -- ``omega_kategori_nbe`` ile **fiilen** kurulur
import ogrenme.zirh_mizan  # [uzuv] Enine topolojik zırh -- **her uzaya mahsus**, katman değil kesit (kütük H23)

# ------------------------------------------------------------------
#  mizan
# ------------------------------------------------------------------
import kuantum.fubini  # [uzuv] Fubini-Study deterministik ağaç okuması
import main.kaggle_cikarim  # [uzuv] Kaggle teslimat nazırı
import main.kaggle_egitim  # [uzuv] Kaggle çoklu GPU tâlim nazırı
import ogrenme.kaggle_donanim  # [uzuv] Kaggle donanım tespiti
import mizan.altyapisal  # [uzuv] Yapısal-altı mantıklar (doğrusal, affine, sıkı), relevans ve kuantum
import mizan.cikarim  # [uzuv] Çıkarım hesapları: Hilbert, Gentzen ardışık hesabı (LK) ve sezgisel (G4ip)
import mizan.cokdegerli  # [uzuv] Çok değerli, bulanık ve paratutarlı mantıklar
import mizan.istikra  # [uzuv] İstikrâ — tümevarım, temsil (analoji) ve tam-olmayan çıkarım kipleri
import mizan.kiplik  # [uzuv] Kiplik mantıkları: Kripke semantiği, çerçeve karşılıkları, deontik ve zaman
import mizan.kiyas  # [uzuv] Kıyas-ı iktiranî: dört şekil, yirmi dört mûteber darb
import mizan.munazara  # [uzuv] Münâzara — âdâbü'l-bahs kaideleri ve yakîn derecesinin hesabı
import mizan.test_mizan  # [şahit] mizan test takımı

# ------------------------------------------------------------------
#  nefs
# ------------------------------------------------------------------
import nefs.akil  # [uzuv] 𝒪₁₁–𝒪₂₄: hüküm, gaye ve burhân. Mananın tartıldığı, sebebin arandığı ve
import nefs.akis  # [uzuv] Küllî ittisâl: 41 melekenin akışı
import nefs.akit  # [uzuv] Kademe 1 -- **envanter ve arayüz akdi**
import nefs.beyan  # [uzuv] 𝒪₃₇–𝒪₄₁: beyan -- hükmün dışarıya çıkışı
import nefs.idrak  # [uzuv] 𝒪₁–𝒪₁₀: duyudan mahiyete. Ham sinyalin suret, soyutlama ve mana kazandığı
import nefs.ihtimal  # [uzuv] İhtimal uzayı: **çıktı ızgarasının bütün muhtemel hâlleri, süperpozisyonda**
import nefs.ikiz  # [hakem] İKİZ SAYILAR (dual numbers) -- türevin tam hâli, sonlu farkın değil
import nefs.dimag  # [uzuv] Küllî Dimağ Hamiltonyeni -- 41 meleke Lie üreteci, 20 mertebe, 4 zırh, 1 gaye
import nefs.hiz  # [hakem] Hız defteri -- 700 MB/sn hedefinin üç ayrı muhasebesi
import nefs.gomme  # [uzuv] Genlik gömmesi -- 4096 boyut 12 kübitte, 35 kübitlik adres yazmacı
import nefs.zirh  # [uzuv] Dörtlü topolojik zırh -- gaye: çelişkisiz mana manifoldu
import nefs.ogda  # [hakem] OGDA -- kaybın min-max olduğunun farkedilmesi ve doğru çözücüsü
import nefs.taksimat  # [uzuv] 22 MİLYON KÜBİTİN TAKSİMATI -- dört bölge, TEK zincir
import nefs.ttkan  # [hakem] TT-KAN -- ceridenin hız hükmünün fiilî hesabı
import nefs.kod_uzayi  # [uzuv] MANTIK KOD UZAYI -- hüküm bloğunun **stabilizer** temsili
import nefs.kopru  # [uzuv] FUNKTÖR KÖPRÜSÜ -- uzaylar arası geçişin **ölçülen** sıhhati
import nefs.kule  # [uzuv] Kule: ana modelin (``nefs/``) kendi kendine uzun pencere tutması
import nefs.meleke  # [uzuv] Meleke (faculty) sözleşmesi ve sicili
import nefs.murakabe  # [uzuv] 𝒪₂₅–𝒪₃₆: murâkabe -- nefsin kendi hükmünü denetlediği mertebe
import nefs.qkaide  # [uzuv] KÂİDE ORAĞI -- H91'in icrası, **reel** yazmaçta
import nefs.qmain  # [uzuv] Kübit-yerli ana modelin giriş noktası -- iddialar burada **ölçülür**
import nefs.tabii_gradyan  # [uzuv] TABİÎ GRADYAN (natural gradient) -- kullanıcı hükmü H86
import nefs.tesir  # [uzuv] Kademe 5 -- **icra izi, hassasiyet ve hata izolasyonu**
import nefs.test_nefs  # [şahit] nefs sınamaları
import nefs.uzaklik_olcumu  # [uzuv] Uzak çift kapısı: **takas ağı mı, MPO mu?** -- eşiği ölçüm koyar

# ------------------------------------------------------------------
#  ogrenme
# ------------------------------------------------------------------
import ogrenme  # [uzuv] ogrenme — operatör öğrenmesi: RKHS, DeepONet/FINO, ızgara, Grassmann
import ogrenme.grassmann  # [uzuv] Grassmann manifoldu: izdüşüm, asal açılar, geodezik Exp/Log
import ogrenme.izgara  # [uzuv] Izgara — adaptif B-spline düğümleri ve sembolik regresyon kapanışı
import ogrenme.operator  # [uzuv] Operatör — DeepONet, FINO ve ızgaradan bağımsız operatör öğrenmesi
import ogrenme.rkhs  # [uzuv] RKHS — yeniden üreten çekirdek Hilbert uzayı ve kapalı form çözüm
import ogrenme.test_grassmann  # [şahit] ``ogrenme.grassmann`` sınamaları — K25 ve K26 tashihlerinin tartılması
import ogrenme.test_ogrenme  # [şahit] ogrenme test takımı

# ------------------------------------------------------------------
#  olcek
# ------------------------------------------------------------------
import olcek  # [uzuv] olcek — performans muhasebesi: FLOP/token, çatı modeli, boyut denetimi
import olcek.gercek  # [uzuv] Bu makinede GERÇEK sürekli ölçüm: 30 sn ve 60 sn pencerelerde GB/sn
import olcek.hiz  # [uzuv] Performans muhasebesi: FLOP/token, çatı modeli ve 'eşdeğer hız'
import olcek.test_olcek  # [şahit] ``olcek.hiz`` sınamaları — M31, M32, M33, M34

# ------------------------------------------------------------------
#  omega_kategori
# ------------------------------------------------------------------
import omega_kategori  # [uzuv] omega_kategori -- (∞,∞)-kategori / kübik tip teorisi çekirdeği
import omega_kategori.aralik  # [uzuv] Aralık (I) cebri ve yüz (face / kofibrasyon) kafesi
import omega_kategori.cekirdek  # [uzuv] Kübik çekirdek: ikame, zayıf-baş normal form ve Kan işlemleri
import omega_kategori.denetleyici  # [uzuv] İki yönlü (bidirectional) tip denetleyici
import omega_kategori.denklik  # [uzuv] Glue tipleri için Kan hesabı -- tümel değişmezliğin HESAPLANAN zemini
import omega_kategori.geometri  # [uzuv] Teğet yapısı, tensörler ve monoid nesneleri -- uzayla BERABER gelen paket
import omega_kategori.iliskiler  # [uzuv] Uzaylar arası münasebetler, ayrık uzaylar, uç haller ve parametrik demetler
import omega_kategori.kutuphane  # [uzuv] Nesne dilinde yazılmış temel kütüphane
import omega_kategori.sozdizim  # [uzuv] Kübik tip teorisinin sözdizimi (terimler)
import omega_kategori.test_omega_kategori  # [şahit] omega_kategori sınama takımı
import omega_kategori.turetimler  # [uzuv] Uzayların çekirdekten türetilmesi + AÇIK aksiyom/boşluk kütüğü
import omega_kategori.yazdir  # [uzuv] Terimleri okunur biçimde yazdırma

# ------------------------------------------------------------------
#  omega_kategori_nbe
# ------------------------------------------------------------------
import omega_kategori_nbe.geometri  # [uzuv] Teğet yapısı, tensörler ve monoid nesneleri -- uzayla BERABER gelen paket
import omega_kategori_nbe.iliskiler  # [uzuv] Uzaylar arası münasebetler, ayrık uzaylar, uç haller ve parametrik demetler
import omega_kategori_nbe.test_omega_kategori_nbe  # [şahit] omega_kategori_nbe sınama takımı

# ------------------------------------------------------------------
#  reel
# ------------------------------------------------------------------
import reel.meleke  # [gölge] 41 idrak melekesinin reel dik kapı kaydı
import reel.test_reel  # [şahit] ``reel`` paketi sınamaları — M9-M16, M28-M30

# ------------------------------------------------------------------
#  tanilama
# ------------------------------------------------------------------
try:                                   # torch şartlı
    import tanilama.dogrula_pareto  # [hakem] (şerhsiz)
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['tanilama.dogrula_pareto'] = str(_e)
try:                                   # torch şartlı
    import tanilama.graf_capasi  # [hakem] (şerhsiz)
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['tanilama.graf_capasi'] = str(_e)
import tanilama.haraplama  # [hakem] HARAPLAMA (lezyon) ÇALIŞMASI -- 'melekeler ârızasız bir vücut mü?'
try:                                   # torch şartlı
    import tanilama.kok_avi  # [hakem] (şerhsiz)
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['tanilama.kok_avi'] = str(_e)
try:                                   # torch şartlı
    import tanilama.kok_avi2  # [hakem] (şerhsiz)
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['tanilama.kok_avi2'] = str(_e)
import tanilama.nizam  # [hakem] NİZAM -- kod tabanının **padişah bakışı**: kime kimin eli uzanıyor
try:                                   # torch şartlı
    import tanilama.ram_repro  # [hakem] (şerhsiz)
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['tanilama.ram_repro'] = str(_e)
try:                                   # torch şartlı
    import tanilama.referans_avi  # [hakem] (şerhsiz)
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['tanilama.referans_avi'] = str(_e)
import tanilama.sadakat  # [hakem] MANTIĞA SADAKAT ÖLÇÜMÜ -- kütük H102'nin açık borcunun kapatılması
import tanilama.tefti  # [hakem] TEFTİŞ -- padişahın **fiilen koşturduğu** her fonksiyon, dosyasıyla beraber
try:                                   # torch şartlı
    import tanilama.sahip_avi  # [hakem] (şerhsiz)
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['tanilama.sahip_avi'] = str(_e)
try:                                   # torch şartlı
    import tanilama.sizinti_avi  # [hakem] (şerhsiz)
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['tanilama.sizinti_avi'] = str(_e)
try:                                   # torch şartlı
    import tanilama.sizinti_gerileme_testi  # [hakem] (şerhsiz)
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['tanilama.sizinti_gerileme_testi'] = str(_e)
try:                                   # torch şartlı
    import tanilama.umumi_profil  # [hakem] (şerhsiz)
except Exception as _e:                # torch yoksa kayda geçer
    EKSIK['tanilama.umumi_profil'] = str(_e)

# ------------------------------------------------------------------
#  token_uzaylari
# ------------------------------------------------------------------
import token_uzaylari  # [uzuv] token_uzaylari — token manifoldları, morfizmler, operatörler ve Glue
import token_uzaylari.fno  # [uzuv] FNO — Fourier Nöral Operatörü ve ızgaradan bağımsızlık
import token_uzaylari.kan  # [uzuv] Kan genişlemeleri — ``Lan`` ve ``Ran``, sonlu kategorilerde hesaplanır
import token_uzaylari.kan_spline  # [uzuv] KAN — B-spline temelli Kolmogorov–Arnold ağı
import token_uzaylari.manifold  # [uzuv] Manifold — metrik, bağlantı, eğrilik ve Laplace–Beltrami
import token_uzaylari.morfizm  # [uzuv] Morfizm — token uzayları arasındaki eşlemeler ve funktoryel yapı
import token_uzaylari.test_token_uzaylari  # [şahit] token_uzaylari test takımı
import token_uzaylari.yapistir  # [uzuv] Yapıştır — token uzayı denkliklerinin Glue tipine köprüsü

# ------------------------------------------------------------------
#  yaklasim
# ------------------------------------------------------------------
import yaklasim  # [uzuv] yaklasim -- fonksiyon yaklaşımı ve eniyileme usulleri
import yaklasim.akislar  # [uzuv] Gradyanın akış olarak okunuşu
import yaklasim.genisletme  # [uzuv] Aradeğerleme: Kan genişletmesi ve onun ezber zaafı
import yaklasim.kara_kutu  # [uzuv] Kara kutu eniyilemenin sınırları
import yaklasim.modern  # [uzuv] Modern yaklaşım mimarileri, sadeleştirilmiş fakat SAHİCİ hâlleriyle
import yaklasim.nedensel  # [uzuv] do-hesabı: bağlanım ile müdahalenin ayrımı
import yaklasim.simgesel  # [uzuv] Simgesel bağlanım: kapalı biçimli bir ifade ARAMAK
import yaklasim.test_yaklasim  # [şahit] yaklasim sınamaları
import yaklasim.tikizlik  # [uzuv] Varlık: tıkızlık, zorlayıcılık ve tıkızlaştırmanın sınırı

#: Her modülün rolü ve vazifesi -- vazife modülün KENDİ şerhinden.
KAYIT: Tuple[Tuple[str, str, str], ...] = (
    ('akis.hacim', 'gölge',
     'Hacim — ortalama eğrilik akışı ve yoğunluk akışları'),
    ('akis.test_akis', 'şahit',
     'akis test takımı'),
    ('kuantum.ic_bag', 'hakem',
     'Sanal bağın kuantikleştirilmesi -- hafıza O(log χ) düşüyor fakat SERBESTLİK de düşüyor; iddia ölçülür'),
    ('nefs.teskilat', 'uzuv',
     '𝒪₄₂ Umumileştirme (Kan uzantısı), 𝒪₄₃ Talim (usul düzenleyici), 𝒪₄₄ Tahsil (ağırlığı zâtî mülk kılma) -- üçü de formüllü'),
    ('nefs.lisan', 'uzuv',
     'Lisan ve 2D izafî mevki -- tiktoken + Lie öteleme üreteçleri; mutlak koordinat YASAK, izafî tarif esastır'),
    ('kuantum.katlama', 'uzuv',
     'HDTF -- hiyerarşik ikili ağaç katlaması; 2^n genlik hiç açılmadan, zar atılmadan QTT inşası'),
    ('akis.ikmal', 'gölge',
     'Ceridenin İkmâl Fıkraları -- Lions konsantrasyonu, RCD(K,N) Bochner, '
     'Cayley çekilmesi, Postnikov tıkanıklık vekili'),
    ('akis.tikiz', 'gölge',
     'Tıkız — Alexandroff tıkızlaştırması, barriyerler ve kritik lokus'),
    ('arama', 'uzuv',
     'arama — kuantum asgarî arama ve dalga bükümü'),
    ('arama.bukum', 'uzuv',
     'Dalga bükümü: WKB tünelleme, GRAPE optimal kontrol, Wilson holonomisi'),
    ('arama.grover', 'uzuv',
     'Kuantum asgarî arama: Grover, Dürr--Høyer ve adiyabatik çöküş'),
    ('arama.test_arama', 'şahit',
     '``arama`` paketi sınamaları — M18, M19, M20, M21, M22'),
    ('fitrat.ayrisma', 'uzuv',
     'Ayrışma — yönlü çizgelerde d-ayrışması ve arka kapı ölçütü'),
    ('fitrat.denge', 'uzuv',
     'Denge — çok failli iktisadî muvazenenin (BGCM) çözümü ve hassasiyeti'),
    ('fitrat.havuz', 'uzuv',
     'Havuz — şüphe uzayının açılması, karantina ve hüküm'),
    ('fitrat.karsi_olgusal', 'uzuv',
     'Karşıolgusal 3-pas, DAG öğrenmesi ve denge lokusu'),
    ('fitrat.test_fitrat', 'şahit',
     'fitrat test takımı'),
    ('fitrat.test_karsi_olgusal', 'şahit',
     '``fitrat.karsi_olgusal`` sınamaları — Darboğaz 45-48'),
    ('fitrat.tevafuk', 'uzuv',
     'Tevâfuk — bağımsız şahitlerin birbirini teyidinin ölçülmesi'),
    ('hesap.galois', 'uzuv',
     'Tam (yuvarlamasız) kuantum aritmetiği: ``ℤ[ζ₈][1/√2]`` halkası'),
    ('hesap.padic', 'uzuv',
     "``p``-adik norm, ultrametrik ve 'irrasyonelliğin ilgası' iddiası"),
    ('hesap.palmer', 'uzuv',
     "Palmer'ın Rasyonel Kuantum Mekaniği (RaQM): ne diyor, ne demiyor"),
    ('hesap.saklama', 'uzuv',
     'Kuantum durumunu saklamanın gerçek maliyeti: keyfî vs YAPILI'),
    ('hesap.test_hesap', 'şahit',
     '``hesap`` paketi sınamaları — M23, M24, M25/M26, M27'),
    ('hesap.test_palmer', 'şahit',
     '``hesap.palmer`` sınamaları — dört itirazın tartılması ve geri almalar'),
    ('idrak.cozucu', 'uzuv',
     "Doğrulanabilir ARC çözücüsü: dik dönüşüm DSL'i üzerinde arama"),
    ('idrak.egitim', 'uzuv',
     "ARC-AGI-2 eğitimi — CPU'da, arka planda koşabilir"),
    ('idrak.kubit', 'uzuv',
     'Kübit kaydı: reel dik kapılarla öğrenilebilir bir kuantum yazmacı'),
    ('idrak.model', 'uzuv',
     'Nefs-i Müdrike ARC modeli — risalelerin mimarisinin fiilî hâli'),
    ('idrak.sekil', 'uzuv',
     'Çıktı ızgarasının şeklini **gösterimlerden çıkarmak**'),
    ('idrak.test_cozucu', 'şahit',
     '``idrak.cozucu`` sınamaları — ispatlı çözüm ya da sükût'),
    ('idrak.test_idrak', 'şahit',
     '``idrak`` paketi sınamaları — veri, kübit, model, eğitim'),
    ('idrak.test_sekil', 'şahit',
     '``idrak.sekil`` sınamaları — ispatlı şekil kestirimi ya da sükût'),
    ('kuantum.devre', 'uzuv',
     'Devre — durum vektörü simülatörü ve spektral işleçler'),
    ('kuantum.eniyileme', 'uzuv',
     'Adiyabatik geçiş, QAOA ve parametre-kaydırma kuralı'),
    ('kuantum.kapilar', 'uzuv',
     'Kapılar — tek ve çok kübitli üniter operatörler'),
    ('kuantum.ceride', 'gölge',
     'Ceridenin üç kapalı-form babı: FCT (κ=1,0), STA karşıt-adiyabatik sürüş, Fubini-Study bilgi geometrisi'),
    ('kuantum.qsvt', 'uzuv',
     'QSVT — blok kodlama, kuantum sinyal işleme ve tekil değer dönüşümü'),
    ('kuantum.surekli', 'uzuv',
     'Sürekli değişkenli (CV) fotonik operatörler — kesilmiş Fock uzayında'),
    ('kuantum.tda', 'uzuv',
     'TDA — kombinatoryal Laplasyen, Betti sayıları ve kalıcı homoloji'),
    ('kuantum.test_kuantum', 'şahit',
     'kuantum test takımı'),
    ('kuantum.test_kuantum_ileri', 'şahit',
     '``kuantum.surekli``, ``kuantum.topolojik``, ``kuantum.eniyileme`` sınamaları'),
    ('kuantum.topolojik', 'uzuv',
     'Topolojik anyon örgüsü ve hata düzeltme (QEC) kapıları'),
    ('local_run.ddp_entry', 'koşucu',
     '(şerhsiz)'),
    ('local_run.entry', 'koşucu',
     '(şerhsiz)'),
    ('nefs.dimag_kulli', 'uzuv',
     'Küllî Dimağ -- ``tecrit.md`` mimarisinin fiilî inşası'),
    ('main.egitim', 'uzuv',
     "Küllî Dimağ'ın eğitimi -- ARC metniyle, **gradyan inişi olmadan**"),
    ('nefs.hamiltonyen', 'uzuv',
     'Uzaya mahsus Hamiltonyenler ve kuantum evrimi'),
    ('idrak.kategori', 'uzuv',
     '20 ∞-kategori uzayı -- ``omega_kategori_nbe`` ile **fiilen** kurulur'),
    ('ogrenme.zirh_mizan', 'uzuv',
     'Enine topolojik zırh -- **her uzaya mahsus**, katman değil kesit (kütük H23)'),
    ('kuantum.fubini', 'uzuv',
     'Fubini-Study güdümlü DETERMİNİSTİK ağaç okuması -- x* = argmax g⁺·∇log P; '
     'metrik hakikaten kurulur, kısaltma olduğu ``fubini_tam_kiyas`` ile ölçülür'),
    ('main.kaggle_egitim', 'uzuv',
     'Kaggle çoklu GPU tâlim nazırı -- 4×L4, sınır vagonu P2P; GPU yokken CPU '
     'yedeğine düşer ve ölçüm yapılmadığını YAZAR'),
    ('main.kaggle_cikarim', 'uzuv',
     'Kaggle teslimat nazırı -- submission.json; "dalga kurulamayan" satır '
     'ayrı sayılır, çözüm sayılmaz'),
    ('ogrenme.kaggle_donanim', 'uzuv',
     'Kaggle donanım tespiti ve ayar seçimi -- BLAS ipliği, profil, mühürleme'),
    ('mizan.altyapisal', 'uzuv',
     'Yapısal-altı mantıklar (doğrusal, affine, sıkı), relevans ve kuantum'),
    ('mizan.cikarim', 'uzuv',
     'Çıkarım hesapları: Hilbert, Gentzen ardışık hesabı (LK) ve sezgisel (G4ip)'),
    ('mizan.cokdegerli', 'uzuv',
     'Çok değerli, bulanık ve paratutarlı mantıklar'),
    ('mizan.istikra', 'uzuv',
     'İstikrâ — tümevarım, temsil (analoji) ve tam-olmayan çıkarım kipleri'),
    ('mizan.kiplik', 'uzuv',
     'Kiplik mantıkları: Kripke semantiği, çerçeve karşılıkları, deontik ve zaman'),
    ('mizan.kiyas', 'uzuv',
     'Kıyas-ı iktiranî: dört şekil, yirmi dört mûteber darb'),
    ('mizan.munazara', 'uzuv',
     "Münâzara — âdâbü'l-bahs kaideleri ve yakîn derecesinin hesabı"),
    ('mizan.test_mizan', 'şahit',
     'mizan test takımı'),
    ('nefs.akil', 'uzuv',
     '𝒪₁₁–𝒪₂₄: hüküm, gaye ve burhân. Mananın tartıldığı, sebebin arandığı ve'),
    ('nefs.akis', 'uzuv',
     'Küllî ittisâl: 41 melekenin akışı'),
    ('nefs.akit', 'uzuv',
     'Kademe 1 -- **envanter ve arayüz akdi**'),
    ('nefs.beyan', 'uzuv',
     '𝒪₃₇–𝒪₄₁: beyan -- hükmün dışarıya çıkışı'),
    ('nefs.idrak', 'uzuv',
     '𝒪₁–𝒪₁₀: duyudan mahiyete. Ham sinyalin suret, soyutlama ve mana kazandığı'),
    ('nefs.ihtimal', 'uzuv',
     'İhtimal uzayı: **çıktı ızgarasının bütün muhtemel hâlleri, süperpozisyonda**'),
    ('nefs.ikiz', 'hakem',
     'İKİZ SAYILAR (dual numbers) -- türevin tam hâli, sonlu farkın değil'),
    ('nefs.dimag', 'uzuv',
     'Küllî Dimağ Hamiltonyeni -- 41 meleke Lie ÜRETECİDİR (katman değil), 20 mertebe, dörtlü zırh ve BGCM muvazenesi tek dizeyde'),
    ('nefs.hiz', 'hakem',
     'Hız defteri -- token başına / küllî süperpozisyon / yükleme: üç muhasebe yan yana'),
    ('nefs.gomme', 'uzuv',
     'Genlik gömmesi -- tokenın 4096 boyutu 12 kübitin GENLİĞİdir; '
     '35 kübitlik adres yazmacı (yığın|yer|mana)'),
    ('nefs.zirh', 'uzuv',
     'Dörtlü topolojik zırh -- Sheaf/Betti/Kohomoloji/Homotopi; '
     'gaye sonraki token değil ÇELİŞKİSİZLİKtir'),
    ('nefs.ogda', 'hakem',
     'OGDA -- kaybın min-max olduğunun farkedilmesi ve doğru çözücüsü'),
    ('nefs.taksimat', 'uzuv',
     '22 MİLYON KÜBİTİN TAKSİMATI -- dört bölge, TEK zincir; eklem ölçüsü'),
    ('nefs.ttkan', 'hakem',
     'TT-KAN -- ceridenin 154 MB/sn hükmünün fiilen sayılmış FLOP hesabı'),
    ('nefs.kod_uzayi', 'uzuv',
     'MANTIK KOD UZAYI -- hüküm bloğunun **stabilizer** temsili'),
    ('nefs.kopru', 'uzuv',
     'FUNKTÖR KÖPRÜSÜ -- uzaylar arası geçişin **ölçülen** sıhhati'),
    ('nefs.kule', 'uzuv',
     'Kule: ana modelin (``nefs/``) kendi kendine uzun pencere tutması'),
    ('nefs.meleke', 'uzuv',
     'Meleke (faculty) sözleşmesi ve sicili'),
    ('nefs.murakabe', 'uzuv',
     '𝒪₂₅–𝒪₃₆: murâkabe -- nefsin kendi hükmünü denetlediği mertebe'),
    ('nefs.qkaide', 'uzuv',
     "KÂİDE ORAĞI -- H91'in icrası, **reel** yazmaçta"),
    ('nefs.qmain', 'uzuv',
     'Kübit-yerli ana modelin giriş noktası -- iddialar burada **ölçülür**'),
    ('nefs.tabii_gradyan', 'uzuv',
     'TABİÎ GRADYAN (natural gradient) -- kullanıcı hükmü H86'),
    ('nefs.tesir', 'uzuv',
     'Kademe 5 -- **icra izi, hassasiyet ve hata izolasyonu**'),
    ('nefs.test_nefs', 'şahit',
     'nefs sınamaları'),
    ('nefs.uzaklik_olcumu', 'uzuv',
     'Uzak çift kapısı: **takas ağı mı, MPO mu?** -- eşiği ölçüm koyar'),
    ('ogrenme', 'uzuv',
     'ogrenme — operatör öğrenmesi: RKHS, DeepONet/FINO, ızgara, Grassmann'),
    ('ogrenme.grassmann', 'uzuv',
     'Grassmann manifoldu: izdüşüm, asal açılar, geodezik Exp/Log'),
    ('ogrenme.izgara', 'uzuv',
     'Izgara — adaptif B-spline düğümleri ve sembolik regresyon kapanışı'),
    ('ogrenme.operator', 'uzuv',
     'Operatör — DeepONet, FINO ve ızgaradan bağımsız operatör öğrenmesi'),
    ('ogrenme.rkhs', 'uzuv',
     'RKHS — yeniden üreten çekirdek Hilbert uzayı ve kapalı form çözüm'),
    ('ogrenme.test_grassmann', 'şahit',
     '``ogrenme.grassmann`` sınamaları — K25 ve K26 tashihlerinin tartılması'),
    ('ogrenme.test_ogrenme', 'şahit',
     'ogrenme test takımı'),
    ('olcek', 'uzuv',
     'olcek — performans muhasebesi: FLOP/token, çatı modeli, boyut denetimi'),
    ('olcek.gercek', 'uzuv',
     'Bu makinede GERÇEK sürekli ölçüm: 30 sn ve 60 sn pencerelerde GB/sn'),
    ('olcek.hiz', 'uzuv',
     "Performans muhasebesi: FLOP/token, çatı modeli ve 'eşdeğer hız'"),
    ('olcek.test_olcek', 'şahit',
     '``olcek.hiz`` sınamaları — M31, M32, M33, M34'),
    ('omega_kategori', 'uzuv',
     'omega_kategori -- (∞,∞)-kategori / kübik tip teorisi çekirdeği'),
    ('omega_kategori.aralik', 'uzuv',
     'Aralık (I) cebri ve yüz (face / kofibrasyon) kafesi'),
    ('omega_kategori.cekirdek', 'uzuv',
     'Kübik çekirdek: ikame, zayıf-baş normal form ve Kan işlemleri'),
    ('omega_kategori.denetleyici', 'uzuv',
     'İki yönlü (bidirectional) tip denetleyici'),
    ('omega_kategori.denklik', 'uzuv',
     'Glue tipleri için Kan hesabı -- tümel değişmezliğin HESAPLANAN zemini'),
    ('omega_kategori.geometri', 'uzuv',
     'Teğet yapısı, tensörler ve monoid nesneleri -- uzayla BERABER gelen paket'),
    ('omega_kategori.iliskiler', 'uzuv',
     'Uzaylar arası münasebetler, ayrık uzaylar, uç haller ve parametrik demetler'),
    ('omega_kategori.kutuphane', 'uzuv',
     'Nesne dilinde yazılmış temel kütüphane'),
    ('omega_kategori.sozdizim', 'uzuv',
     'Kübik tip teorisinin sözdizimi (terimler)'),
    ('omega_kategori.test_omega_kategori', 'şahit',
     'omega_kategori sınama takımı'),
    ('omega_kategori.turetimler', 'uzuv',
     'Uzayların çekirdekten türetilmesi + AÇIK aksiyom/boşluk kütüğü'),
    ('omega_kategori.yazdir', 'uzuv',
     'Terimleri okunur biçimde yazdırma'),
    ('omega_kategori_nbe.geometri', 'uzuv',
     'Teğet yapısı, tensörler ve monoid nesneleri -- uzayla BERABER gelen paket'),
    ('omega_kategori_nbe.iliskiler', 'uzuv',
     'Uzaylar arası münasebetler, ayrık uzaylar, uç haller ve parametrik demetler'),
    ('omega_kategori_nbe.test_omega_kategori_nbe', 'şahit',
     'omega_kategori_nbe sınama takımı'),
    ('reel.meleke', 'gölge',
     '41 idrak melekesinin reel dik kapı kaydı'),
    ('reel.test_reel', 'şahit',
     '``reel`` paketi sınamaları — M9-M16, M28-M30'),
    ('tanilama.dogrula_pareto', 'hakem',
     '(şerhsiz)'),
    ('tanilama.graf_capasi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.haraplama', 'hakem',
     "HARAPLAMA (lezyon) ÇALIŞMASI -- 'melekeler ârızasız bir vücut mü?'"),
    ('tanilama.kok_avi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.kok_avi2', 'hakem',
     '(şerhsiz)'),
    ('tanilama.nizam', 'hakem',
     'NİZAM -- kod tabanının **padişah bakışı**: kime kimin eli uzanıyor'),
    ('tanilama.ram_repro', 'hakem',
     '(şerhsiz)'),
    ('tanilama.referans_avi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.sadakat', 'hakem',
     "MANTIĞA SADAKAT ÖLÇÜMÜ -- kütük H102'nin açık borcunun kapatılması"),
    ('tanilama.sahip_avi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.sizinti_avi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.tefti', 'hakem',
     'TEFTİŞ -- padişahın **fiilen koşturduğu** her fonksiyon, '
     'dosyasıyla beraber'),
    ('tanilama.sizinti_gerileme_testi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.umumi_profil', 'hakem',
     '(şerhsiz)'),
    ('token_uzaylari', 'uzuv',
     'token_uzaylari — token manifoldları, morfizmler, operatörler ve Glue'),
    ('token_uzaylari.fno', 'uzuv',
     'FNO — Fourier Nöral Operatörü ve ızgaradan bağımsızlık'),
    ('token_uzaylari.kan', 'uzuv',
     'Kan genişlemeleri — ``Lan`` ve ``Ran``, sonlu kategorilerde hesaplanır'),
    ('token_uzaylari.kan_spline', 'uzuv',
     'KAN — B-spline temelli Kolmogorov–Arnold ağı'),
    ('token_uzaylari.manifold', 'uzuv',
     'Manifold — metrik, bağlantı, eğrilik ve Laplace–Beltrami'),
    ('token_uzaylari.morfizm', 'uzuv',
     'Morfizm — token uzayları arasındaki eşlemeler ve funktoryel yapı'),
    ('token_uzaylari.test_token_uzaylari', 'şahit',
     'token_uzaylari test takımı'),
    ('token_uzaylari.yapistir', 'uzuv',
     'Yapıştır — token uzayı denkliklerinin Glue tipine köprüsü'),
    ('yaklasim', 'uzuv',
     'yaklasim -- fonksiyon yaklaşımı ve eniyileme usulleri'),
    ('yaklasim.akislar', 'uzuv',
     'Gradyanın akış olarak okunuşu'),
    ('yaklasim.genisletme', 'uzuv',
     'Aradeğerleme: Kan genişletmesi ve onun ezber zaafı'),
    ('yaklasim.kara_kutu', 'uzuv',
     'Kara kutu eniyilemenin sınırları'),
    ('yaklasim.modern', 'uzuv',
     'Modern yaklaşım mimarileri, sadeleştirilmiş fakat SAHİCİ hâlleriyle'),
    ('yaklasim.nedensel', 'uzuv',
     'do-hesabı: bağlanım ile müdahalenin ayrımı'),
    ('yaklasim.simgesel', 'uzuv',
     'Simgesel bağlanım: kapalı biçimli bir ifade ARAMAK'),
    ('yaklasim.test_yaklasim', 'şahit',
     'yaklasim sınamaları'),
    ('yaklasim.tikizlik', 'uzuv',
     'Varlık: tıkızlık, zorlayıcılık ve tıkızlaştırmanın sınırı'),
)

#: **2. KADEMEYE geçmiş** modüller: ana akışta fiilen iş görenler.
#: Divana girmek 1. kademedir (yüklenir, rol alır, yoklanır); burada
#: olmak, modülün ana akışın bir adımını **icra ettiği** manasına gelir.
#: Liste kasten kısadır ve uzaması gereken şey odur.
KADEME2: Tuple[str, ...] = (
    "kuantum.stabilizer",      # nefs/kod_uzayi.py -- hüküm bloğu yüzleştirmesi
    "token_uzaylari.morfizm",  # nefs/kopru.py     -- kodlama funktörü (H14)
    "token_uzaylari.manifold", # nefs/kopru.py     -- metrik
    "mizan.onerme",            # nefs/tertip.py    -- mantık usulleri
    "fitrat.serbest_enerji",   # nefs/gaye.py      -- F ayrışımı
    "reel.hartley",            # nefs/golge.py     -- dik dönüşüm çapraz doğrulama
    "reel.karmasik",           # nefs/golge.py     -- reel gömme sadakati
    "akis.lie",                # nefs/golge.py     -- SO(n) grup sadakati
    "omega_kategori_nbe",      # nefs/mertebe.py   -- 20 mertebe lifi
    "ogrenme.rkhs",            # nefs/iki_olcek.py -- sağîr ölçek, kapalı form
    "ogrenme.grassmann",       # nefs/iki_olcek.py -- iki ölçeğin asal açıları
    "idrak.arc",               # nefs/iki_olcek.py -- ARC görevleri
    "idrak.sekil",             # nefs/operad.py    -- yamaların mahallî kâidesi
    "omega_kategori.turetimler",  # nefs/operad.py -- çekirdeğin boşluk kütüğü
    "mizan.munazara",          # nefs/mantik.py    -- yakîn mertebeleri, makam sırası
    "fitrat.tevafuk",          # nefs/sahitlik.py  -- 𝒪₂₉'un bağımsızlık tartısı
    "mizan.istikra",           # nefs/mantik.py    -- ARC'nin istikrâ mertebesi
    "fitrat.ayrisma",          # nefs/illet.py     -- akışın sebep çizgesi, d-ayrışma
)


def yoklama(kos: bool = True, azami_sn: float = 0.0
            ) -> Dict[str, object]:
    """**1,5. KADEME:** modülü içe aktarmakla kalma, KENDİ gösterimini koştur.

    Divanın 1. kademesi modülü yükler; bu, onu **çalıştırır**. Çoğu
    modül kendi ``rapor()`` yahut ``_gosterim()`` fonksiyonunu taşır ve
    orada kendi iddialarını ölçer -- yani modülün kendi şahidi
    zaten yazılmıştır, yalnız hiç çağrılmıyordu.

    Aradaki fark küçük değildir: içe aktarma yalnız modülün **derlendiğini**
    gösterir; gösterimi koşturmak, içindeki cebrin fiilen işlediğini
    gösterir. Bir modül bozulduğunda 1. kademe sessiz kalır, bu kalmaz.

    ``şahit`` rolündekiler hariçtir: onlar `test_nefs.py` ve `pytest`
    tarafından zaten koşturulur; burada ikinci defa koşmaları israftır.
    """
    import contextlib
    import importlib
    import io as _io
    import time

    kosan: List[Tuple[str, float]] = []
    kirik: List[Tuple[str, str]] = []
    gosterimsiz: List[str] = []
    for ad, rol, _ in KAYIT:
        if rol == "şahit":
            continue
        try:
            m = importlib.import_module(ad)
        except BaseException:
            continue                       # ``yokla`` zaten sayıyor
        f = getattr(m, "rapor", None) or getattr(m, "_gosterim", None)
        if not callable(f):
            gosterimsiz.append(ad)
            continue
        if not kos:
            kosan.append((ad, 0.0))
            continue
        t0 = time.perf_counter()
        try:
            with contextlib.redirect_stdout(_io.StringIO()):
                f()
            kosan.append((ad, time.perf_counter() - t0))
        except BaseException as e:                       # noqa: BLE001
            kirik.append((ad, "%s: %s" % (type(e).__name__, str(e)[:70])))
    return {"kosan": kosan, "kirik": kirik, "gosterimsiz": gosterimsiz,
            "sure": float(sum(d for _, d in kosan))}


def yokla() -> Dict[str, object]:
    """Divanı yokla: kim geldi, kim gelmedi, kim hangi kademede.

    Bu bir **iddia değil sayımdır**. ``yüklenemeyen`` boş değilse rapor
    onu olduğu gibi yazar; "hepsi bağlandı" denmez.
    """
    import importlib
    roller: Dict[str, int] = {}
    yuklu: List[str] = []
    yuklenemeyen: List[Tuple[str, str]] = []
    for ad, rol, _ in KAYIT:
        roller[rol] = roller.get(rol, 0) + 1
        try:
            importlib.import_module(ad)
            yuklu.append(ad)
        except BaseException as e:                       # noqa: BLE001
            yuklenemeyen.append(
                (ad, "%s: %s" % (type(e).__name__, str(e)[:70])))
    return {
        "kayitli": len(KAYIT),
        "yuklu": len(yuklu),
        "yuklenemeyen": yuklenemeyen,
        "roller": roller,
        "kademe2": len(KADEME2),
    }


def rapor(kos: bool = True) -> str:
    y = yokla()
    s = ["=== DİVAN -- padişahın tebaası ===",
         "",
         "Bağlamanın algoritması: padişahın eli bir İÇE AKTARMA",
         "kapanışıdır; o hâlde bağlamak, tek divanda toplayıp divanı",
         "tahttan çağırmaktır. Yukarıdan aşağı, modül modül değil.",
         "",
         "  kayıtlı modül : %d" % y["kayitli"],
         "  yüklenen      : %d" % y["yuklu"],
         "  yüklenemeyen  : %d" % len(y["yuklenemeyen"])]
    for ad, sebep in y["yuklenemeyen"]:
        s.append("      %-42s %s" % (ad, sebep))
    s += ["", "  ROLLER:"]
    for r, n in sorted(y["roller"].items(), key=lambda x: -x[1]):
        s.append("      %-8s %d" % (r, n))
    yk = yoklama(kos=kos)
    s += ["",
          "  KADEMELER (kütük H123/H126):",
          "    1.  yüklendi, rol aldı            : %d" % y["yuklu"],
          "    1,5 kendi gösterimi KOŞTU         : %d%s"
          % (len(yk["kosan"]), "" if kos else "  (koşturulmadı)"),
          "        gösterimi olmayan             : %d" % len(yk["gosterimsiz"]),
          "        gösterimi KIRIK               : %d" % len(yk["kirik"]),
          "    2.  ana akışta fiilen iş görüyor  : %d" % y["kademe2"]]
    for ad, sebep in yk["kirik"]:
        s.append("        %-38s %s" % (ad, sebep))
    if kos:
        s.append("    (1,5 kademe koşu süresi: %.1f sn)" % yk["sure"])
    s += ["",
          "AÇIKÇA: divana girmek YAPISAL tabiiyettir -- modül yüklenir,",
          "rol alır, her koşuda yoklanır. Bu, her modülün ana akışta bir",
          "UZUV olduğu manasına GELMEZ (kütük H96). Kademeler o farkı",
          "sayıyla tutar; uzaması gereken 2. kademedir."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
