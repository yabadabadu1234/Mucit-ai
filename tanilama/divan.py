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

# ══ TEBAA -- ağaçtan ÜRETİLDİ, elle tutulmuyor ══
try:
    import idrak  # [uzuv] idrak — külliyatın mimarisinin fiilî hâli: ARC-AGI-2 üzerinde çalışan 
except Exception as _e:  # noqa: BLE001
    EKSIK['idrak'] = str(_e)
try:
    import idrak.kategori  # [uzuv] 20 ∞-kategori uzayı -- ``omega_kategori_nbe`` ile **fiilen** kurulur.
except Exception as _e:  # noqa: BLE001
    EKSIK['idrak.kategori'] = str(_e)
try:
    import idrak.test_sekil  # [şahit] ``idrak.sekil`` sınamaları — ispatlı şekil kestirimi ya da sükût.
except Exception as _e:  # noqa: BLE001
    EKSIK['idrak.test_sekil'] = str(_e)
try:
    import kuantum  # [uzuv] kuantum — kapılar, devreler, spektral işleçler ve topolojik mizan.
except Exception as _e:  # noqa: BLE001
    EKSIK['kuantum'] = str(_e)
try:
    import kuantum.devre  # [uzuv] Devre — durum vektörü simülatörü ve spektral işleçler.
except Exception as _e:  # noqa: BLE001
    EKSIK['kuantum.devre'] = str(_e)
try:
    import kuantum.eniyileme  # [uzuv] Adiyabatik geçiş, QAOA ve parametre-kaydırma kuralı.
except Exception as _e:  # noqa: BLE001
    EKSIK['kuantum.eniyileme'] = str(_e)
try:
    import kuantum.kapilar  # [uzuv] Kapılar — tek ve çok kübitli üniter operatörler.
except Exception as _e:  # noqa: BLE001
    EKSIK['kuantum.kapilar'] = str(_e)
try:
    import kuantum.kubit_taksimati  # [uzuv] 22 milyon kübitin Hilbert yazmaç taksimatı -- **tek zincirde**.
except Exception as _e:  # noqa: BLE001
    EKSIK['kuantum.kubit_taksimati'] = str(_e)
try:
    import kuantum.stabilizer  # [uzuv] Stabilizer rank ayrışımı (Bravyi–Gosset–Smith) -- Clifford çerçevesi +
except Exception as _e:  # noqa: BLE001
    EKSIK['kuantum.stabilizer'] = str(_e)
try:
    import kuantum.surekli  # [uzuv] Sürekli değişkenli (CV) fotonik operatörler — kesilmiş Fock uzayında.
except Exception as _e:  # noqa: BLE001
    EKSIK['kuantum.surekli'] = str(_e)
try:
    import kuantum.test_kuantum  # [şahit] kuantum test takımı.
except Exception as _e:  # noqa: BLE001
    EKSIK['kuantum.test_kuantum'] = str(_e)
try:
    import kuantum.test_kuantum_ileri  # [şahit] ``kuantum.surekli``, ``kuantum.topolojik``, ``kuantum.eniyileme`` sına
except Exception as _e:  # noqa: BLE001
    EKSIK['kuantum.test_kuantum_ileri'] = str(_e)
try:
    import kuantum.topolojik  # [uzuv] Topolojik anyon örgüsü ve hata düzeltme (QEC) kapıları.
except Exception as _e:  # noqa: BLE001
    EKSIK['kuantum.topolojik'] = str(_e)
try:
    import main  # [uzuv] Küllî Dimağ -- tecrit mimarisinin müstakil modeli (kütük H32).
except Exception as _e:  # noqa: BLE001
    EKSIK['main'] = str(_e)
try:
    import main.cikarim  # [taht] ÇIKARIM -- tahtın ikinci kapısı: **cevabı motor verir.**
except Exception as _e:  # noqa: BLE001
    EKSIK['main.cikarim'] = str(_e)
try:
    import main.egitim  # [taht] KÜLLÎ DİMAĞ -- YEREL VE GENEL TÂLİM MOTORU (PADİŞAH TÂLİM)
except Exception as _e:  # noqa: BLE001
    EKSIK['main.egitim'] = str(_e)
try:
    import main.kaggle_cikarim  # [taht] KÜLLÎ DİMAĞ -- KAGGLE ÇIKARIM VE TESLİMAT NAZIRI
except Exception as _e:  # noqa: BLE001
    EKSIK['main.kaggle_cikarim'] = str(_e)
try:
    import main.kaggle_egitim  # [taht] KÜLLÎ DİMAĞ -- KAGGLE ÇOKLU GPU TÂLİM NAZIRI
except Exception as _e:  # noqa: BLE001
    EKSIK['main.kaggle_egitim'] = str(_e)
try:
    import main.veri  # [taht] VERİ -- belirteçleri diske dizen ve Kaggle'a gönderen tek kapı.
except Exception as _e:  # noqa: BLE001
    EKSIK['main.veri'] = str(_e)
try:
    import matematik  # [uzuv] matematik -- sistemin bastığı değişmez analitik zemin.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik'] = str(_e)
try:
    import matematik.fitrat  # [uzuv] FITRAT ÇİPİ -- nedensellik, illiyet ve oyun dengesi.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.fitrat'] = str(_e)
try:
    import matematik.geometri  # [uzuv] HENDESE ÇİPİ -- Riemann manifoldu, Lie cebri, akışlar ve tam aritmetik
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.geometri'] = str(_e)
try:
    import matematik.mizan  # [uzuv] MÎZÂN ÇİPİ -- mantık, cedel ve epistemik hüküm.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.mizan'] = str(_e)
try:
    import matematik.test_akis  # [şahit] akis test takımı.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.test_akis'] = str(_e)
try:
    import matematik.test_fitrat  # [şahit] fitrat test takımı.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.test_fitrat'] = str(_e)
try:
    import matematik.test_hesap  # [şahit] ``hesap`` paketi sınamaları — M23, M24, M25/M26, M27.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.test_hesap'] = str(_e)
try:
    import matematik.test_karsi_olgusal  # [şahit] ``fitrat.karsi_olgusal`` sınamaları — Darboğaz 45-48.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.test_karsi_olgusal'] = str(_e)
try:
    import matematik.test_mizan  # [şahit] mizan test takımı.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.test_mizan'] = str(_e)
try:
    import matematik.test_palmer  # [şahit] ``hesap.palmer`` sınamaları — dört itirazın tartılması ve geri almalar
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.test_palmer'] = str(_e)
try:
    import matematik.test_reel  # [şahit] ``reel`` paketi sınamaları — M9-M16, M28-M30.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.test_reel'] = str(_e)
try:
    import matematik.test_tip_teorisi  # [şahit] omega_kategori_nbe sınama takımı.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.test_tip_teorisi'] = str(_e)
try:
    import matematik.test_token_uzaylari  # [şahit] token_uzaylari test takımı.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.test_token_uzaylari'] = str(_e)
try:
    import matematik.tip_teorisi  # [uzuv] TİP TEORİSİ ÇİPİ -- kübik tip teorisi, NbE ve HoTT.
except Exception as _e:  # noqa: BLE001
    EKSIK['matematik.tip_teorisi'] = str(_e)
try:
    import nefs  # [uzuv] nefs -- Nefs-i Müdrike mimarisi: 41 idrak melekesinin koşabilir hâli.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs'] = str(_e)
try:
    import nefs.akit  # [uzuv] Kademe 1 -- **envanter ve arayüz akdi**.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.akit'] = str(_e)
try:
    import nefs.ara  # [uzuv] ARAMAK -- en iyiyi bulmak, kuyuya düşersen çıkmak.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.ara'] = str(_e)
try:
    import nefs.dusun  # [uzuv] DÜŞÜNMEK -- manzarayı yazmaca alıp melekelerden geçirmek.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.dusun'] = str(_e)
try:
    import nefs.gor  # [uzuv] GÖRMEK -- dış âlemden tek nesne.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.gor'] = str(_e)
try:
    import nefs.hizli  # [uzuv] HIZLI -- boyut patlamasının dört tedbiri, GPU dahil.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.hizli'] = str(_e)
try:
    import nefs.illet  # [uzuv] İLLET -- akışın **sebep çizgesi** kurulur ve `fitrat/ayrisma.py` ile t
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.illet'] = str(_e)
try:
    import nefs.kule  # [uzuv] Kule: ana modelin (``nefs/``) kendi kendine uzun pencere tutması.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.kule'] = str(_e)
try:
    import nefs.kulli_kayip  # [uzuv] KÜLLÎ KAYIP ÇİPİ -- ölçü funktörü, kademe hiyerarşisi ve küllî kayıp.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.kulli_kayip'] = str(_e)
try:
    import nefs.lif  # [uzuv] LİF -- kelimenin nereye takıldığı: tip → kategori → uzay → nokta.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.lif'] = str(_e)
try:
    import nefs.mantik  # [uzuv] MANTIK -- `mizan/` külliyatının ana akışa **uzuv** olarak bağlanması.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.mantik'] = str(_e)
try:
    import nefs.melekeler  # [uzuv] KÜLLÎ MELEKE ÇİPİ -- 44 meleke, 20 mertebe, iki hat, tek dosya (KÜME 2
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.melekeler'] = str(_e)
try:
    import nefs.musahede  # [uzuv] MÜŞAHEDE ÇİPİ -- izafî lisan, mübser duyu, şahitlik ve ARC verisi.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.musahede'] = str(_e)
try:
    import nefs.ogren  # [uzuv] ÖĞRENMEK -- mîzâna göre düzelt, ve haddini bil.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.ogren'] = str(_e)
try:
    import nefs.qegitim  # [uzuv] Ana modelin eğitimi -- **gradyan inişi yoktur** (kütük H3/H28).
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.qegitim'] = str(_e)
try:
    import nefs.qudit  # [uzuv] QUDİT -- dimağın yeni çekirdeği: SVD yok, MPS yok, ikili kübit yok.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.qudit'] = str(_e)
try:
    import nefs.qyazmac  # [uzuv] QYAZMAÇ -- qudit yazmacı: MPS'in yerine geçen durum kabı.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.qyazmac'] = str(_e)
try:
    import nefs.soyle  # [uzuv] SÖYLEMEK -- ya motorun ürettiği, ya sükût.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.soyle'] = str(_e)
try:
    import nefs.tart  # [uzuv] TARTMAK -- hâl ne kadar doğru, kim sözünde durmadı.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.tart'] = str(_e)
try:
    import nefs.test_nefs  # [şahit] nefs sınamaları.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.test_nefs'] = str(_e)
try:
    import nefs.zihin_durumu  # [uzuv] ZİHİN DURUMU -- qudit yazmacı üstünde. **MPS SİLİNDİ.**
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.zihin_durumu'] = str(_e)
try:
    import nefs.zirh  # [uzuv] ZIRH ÇİPİ -- dörtlü topolojik zırh, mantık sadakati ve MPO işareti.
except Exception as _e:  # noqa: BLE001
    EKSIK['nefs.zirh'] = str(_e)
try:
    import ogrenme  # [uzuv] ogrenme — operatör öğrenmesi: RKHS, DeepONet/FINO, ızgara, Grassmann.
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme'] = str(_e)
try:
    import ogrenme.grassmann  # [uzuv] Grassmann manifoldu: izdüşüm, asal açılar, geodezik Exp/Log.
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.grassmann'] = str(_e)
try:
    import ogrenme.izgara  # [uzuv] Izgara — adaptif B-spline düğümleri ve sembolik regresyon kapanışı.
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.izgara'] = str(_e)
try:
    import ogrenme.kaggle_donanim  # [koşucu] Kaggle koşucusu: tek hücrelik başlangıç, çok cihazlı eğitim.
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.kaggle_donanim'] = str(_e)
try:
    import ogrenme.morse  # [uzuv] MORSE-EULER TOPOLOJİK MUHASEBE (K27 katı sağlaması)
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.morse'] = str(_e)
try:
    import ogrenme.operator  # [uzuv] Operatör — DeepONet, FINO ve ızgaradan bağımsız operatör öğrenmesi.
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.operator'] = str(_e)
try:
    import ogrenme.optimize  # [uzuv] TÂLİM VE ENİYİLEME ÇİPİ -- deterministik dalga tâliminin icra çekirdeğ
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.optimize'] = str(_e)
try:
    import ogrenme.rkhs  # [uzuv] RKHS — yeniden üreten çekirdek Hilbert uzayı ve kapalı form çözüm.
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.rkhs'] = str(_e)
try:
    import ogrenme.test_arama  # [şahit] ``arama`` paketi sınamaları — M18, M19, M20, M21, M22.
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.test_arama'] = str(_e)
try:
    import ogrenme.test_grassmann  # [şahit] ``ogrenme.grassmann`` sınamaları — K25 ve K26 tashihlerinin tartılması
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.test_grassmann'] = str(_e)
try:
    import ogrenme.test_ogrenme  # [şahit] ogrenme test takımı.
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.test_ogrenme'] = str(_e)
try:
    import ogrenme.test_yaklasim  # [şahit] yaklasim sınamaları.
except Exception as _e:  # noqa: BLE001
    EKSIK['ogrenme.test_yaklasim'] = str(_e)
try:
    import tanilama.dogrula_pareto  # [hakem] (şerhsiz)
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.dogrula_pareto'] = str(_e)
try:
    import tanilama.graf_capasi  # [hakem] (şerhsiz)
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.graf_capasi'] = str(_e)
try:
    import tanilama.haraplama  # [hakem] HARAPLAMA (lezyon) ÇALIŞMASI -- "melekeler ârızasız bir vücut mü?"
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.haraplama'] = str(_e)
try:
    import tanilama.kok_avi  # [hakem] (şerhsiz)
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.kok_avi'] = str(_e)
try:
    import tanilama.kok_avi2  # [hakem] (şerhsiz)
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.kok_avi2'] = str(_e)
try:
    import tanilama.nizam  # [hakem] NİZAM -- kod tabanının **padişah bakışı**: kime kimin eli uzanıyor.
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.nizam'] = str(_e)
try:
    import tanilama.nizam_dolasiklik  # [hakem] DOLAŞIKLIK NİZAMI -- Dosya 1'in hükmü **ölçülür**, iddia edilmez.
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.nizam_dolasiklik'] = str(_e)
try:
    import tanilama.ram_repro  # [hakem] (şerhsiz)
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.ram_repro'] = str(_e)
try:
    import tanilama.referans_avi  # [hakem] (şerhsiz)
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.referans_avi'] = str(_e)
try:
    import tanilama.sadakat  # [hakem] MANTIĞA SADAKAT ÖLÇÜMÜ -- kütük H102'nin açık borcunun kapatılması.
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.sadakat'] = str(_e)
try:
    import tanilama.sahip_avi  # [hakem] (şerhsiz)
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.sahip_avi'] = str(_e)
try:
    import tanilama.sizinti_avi  # [hakem] (şerhsiz)
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.sizinti_avi'] = str(_e)
try:
    import tanilama.sizinti_gerileme_testi  # [hakem] (şerhsiz)
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.sizinti_gerileme_testi'] = str(_e)
try:
    import tanilama.tefti  # [hakem] TEFTİŞ -- padişahın **fiilen koşturduğu** her fonksiyon, dosyasıyla be
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.tefti'] = str(_e)
try:
    import tanilama.umumi_profil  # [hakem] (şerhsiz)
except Exception as _e:  # noqa: BLE001
    EKSIK['tanilama.umumi_profil'] = str(_e)

KAYIT: Tuple[Tuple[str, str, str], ...] = (
    ('idrak', 'uzuv',
     'idrak — külliyatın mimarisinin fiilî hâli: ARC-AGI-2 üzerinde çalışan model.'),
    ('idrak.kategori', 'uzuv',
     '20 ∞-kategori uzayı -- ``omega_kategori_nbe`` ile **fiilen** kurulur.'),
    ('idrak.test_sekil', 'şahit',
     '``idrak.sekil`` sınamaları — ispatlı şekil kestirimi ya da sükût.'),
    ('kuantum', 'uzuv',
     'kuantum — kapılar, devreler, spektral işleçler ve topolojik mizan.'),
    ('kuantum.devre', 'uzuv',
     'Devre — durum vektörü simülatörü ve spektral işleçler.'),
    ('kuantum.eniyileme', 'uzuv',
     'Adiyabatik geçiş, QAOA ve parametre-kaydırma kuralı.'),
    ('kuantum.kapilar', 'uzuv',
     'Kapılar — tek ve çok kübitli üniter operatörler.'),
    ('kuantum.kubit_taksimati', 'uzuv',
     '22 milyon kübitin Hilbert yazmaç taksimatı -- **tek zincirde**.'),
    ('kuantum.stabilizer', 'uzuv',
     'Stabilizer rank ayrışımı (Bravyi–Gosset–Smith) -- Clifford çerçevesi + T.'),
    ('kuantum.surekli', 'uzuv',
     'Sürekli değişkenli (CV) fotonik operatörler — kesilmiş Fock uzayında.'),
    ('kuantum.test_kuantum', 'şahit',
     'kuantum test takımı.'),
    ('kuantum.test_kuantum_ileri', 'şahit',
     '``kuantum.surekli``, ``kuantum.topolojik``, ``kuantum.eniyileme`` sınamaları.'),
    ('kuantum.topolojik', 'uzuv',
     'Topolojik anyon örgüsü ve hata düzeltme (QEC) kapıları.'),
    ('main', 'uzuv',
     'Küllî Dimağ -- tecrit mimarisinin müstakil modeli (kütük H32).'),
    ('main.cikarim', 'taht',
     'ÇIKARIM -- tahtın ikinci kapısı: **cevabı motor verir.**'),
    ('main.egitim', 'taht',
     'KÜLLÎ DİMAĞ -- YEREL VE GENEL TÂLİM MOTORU (PADİŞAH TÂLİM)'),
    ('main.kaggle_cikarim', 'taht',
     'KÜLLÎ DİMAĞ -- KAGGLE ÇIKARIM VE TESLİMAT NAZIRI'),
    ('main.kaggle_egitim', 'taht',
     'KÜLLÎ DİMAĞ -- KAGGLE ÇOKLU GPU TÂLİM NAZIRI'),
    ('main.veri', 'taht',
     'VERİ -- belirteçleri diske dizen ve Kaggle\'a gönderen tek kapı.'),
    ('matematik', 'uzuv',
     'matematik -- sistemin bastığı değişmez analitik zemin.'),
    ('matematik.fitrat', 'uzuv',
     'FITRAT ÇİPİ -- nedensellik, illiyet ve oyun dengesi.'),
    ('matematik.geometri', 'uzuv',
     'HENDESE ÇİPİ -- Riemann manifoldu, Lie cebri, akışlar ve tam aritmetik.'),
    ('matematik.mizan', 'uzuv',
     'MÎZÂN ÇİPİ -- mantık, cedel ve epistemik hüküm.'),
    ('matematik.test_akis', 'şahit',
     'akis test takımı.'),
    ('matematik.test_fitrat', 'şahit',
     'fitrat test takımı.'),
    ('matematik.test_hesap', 'şahit',
     '``hesap`` paketi sınamaları — M23, M24, M25/M26, M27.'),
    ('matematik.test_karsi_olgusal', 'şahit',
     '``fitrat.karsi_olgusal`` sınamaları — Darboğaz 45-48.'),
    ('matematik.test_mizan', 'şahit',
     'mizan test takımı.'),
    ('matematik.test_palmer', 'şahit',
     '``hesap.palmer`` sınamaları — dört itirazın tartılması ve geri almalar.'),
    ('matematik.test_reel', 'şahit',
     '``reel`` paketi sınamaları — M9-M16, M28-M30.'),
    ('matematik.test_tip_teorisi', 'şahit',
     'omega_kategori_nbe sınama takımı.'),
    ('matematik.test_token_uzaylari', 'şahit',
     'token_uzaylari test takımı.'),
    ('matematik.tip_teorisi', 'uzuv',
     'TİP TEORİSİ ÇİPİ -- kübik tip teorisi, NbE ve HoTT.'),
    ('nefs', 'uzuv',
     'nefs -- Nefs-i Müdrike mimarisi: 41 idrak melekesinin koşabilir hâli.'),
    ('nefs.akit', 'uzuv',
     'Kademe 1 -- **envanter ve arayüz akdi**.'),
    ('nefs.ara', 'uzuv',
     'ARAMAK -- en iyiyi bulmak, kuyuya düşersen çıkmak.'),
    ('nefs.dusun', 'uzuv',
     'DÜŞÜNMEK -- manzarayı yazmaca alıp melekelerden geçirmek.'),
    ('nefs.gor', 'uzuv',
     'GÖRMEK -- dış âlemden tek nesne.'),
    ('nefs.hizli', 'uzuv',
     'HIZLI -- boyut patlamasının dört tedbiri, GPU dahil.'),
    ('nefs.illet', 'uzuv',
     'İLLET -- akışın **sebep çizgesi** kurulur ve `fitrat/ayrisma.py` ile tartılır.'),
    ('nefs.kule', 'uzuv',
     'Kule: ana modelin (``nefs/``) kendi kendine uzun pencere tutması.'),
    ('nefs.kulli_kayip', 'uzuv',
     'KÜLLÎ KAYIP ÇİPİ -- ölçü funktörü, kademe hiyerarşisi ve küllî kayıp.'),
    ('nefs.lif', 'uzuv',
     'LİF -- kelimenin nereye takıldığı: tip → kategori → uzay → nokta.'),
    ('nefs.mantik', 'uzuv',
     'MANTIK -- `mizan/` külliyatının ana akışa **uzuv** olarak bağlanması.'),
    ('nefs.melekeler', 'uzuv',
     'KÜLLÎ MELEKE ÇİPİ -- 44 meleke, 20 mertebe, iki hat, tek dosya (KÜME 2)'),
    ('nefs.musahede', 'uzuv',
     'MÜŞAHEDE ÇİPİ -- izafî lisan, mübser duyu, şahitlik ve ARC verisi.'),
    ('nefs.ogren', 'uzuv',
     'ÖĞRENMEK -- mîzâna göre düzelt, ve haddini bil.'),
    ('nefs.qegitim', 'uzuv',
     'Ana modelin eğitimi -- **gradyan inişi yoktur** (kütük H3/H28).'),
    ('nefs.qudit', 'uzuv',
     'QUDİT -- dimağın yeni çekirdeği: SVD yok, MPS yok, ikili kübit yok.'),
    ('nefs.qyazmac', 'uzuv',
     'QYAZMAÇ -- qudit yazmacı: MPS\'in yerine geçen durum kabı.'),
    ('nefs.soyle', 'uzuv',
     'SÖYLEMEK -- ya motorun ürettiği, ya sükût.'),
    ('nefs.tart', 'uzuv',
     'TARTMAK -- hâl ne kadar doğru, kim sözünde durmadı.'),
    ('nefs.test_nefs', 'şahit',
     'nefs sınamaları.'),
    ('nefs.zihin_durumu', 'uzuv',
     'ZİHİN DURUMU -- qudit yazmacı üstünde. **MPS SİLİNDİ.**'),
    ('nefs.zirh', 'uzuv',
     'ZIRH ÇİPİ -- dörtlü topolojik zırh, mantık sadakati ve MPO işareti.'),
    ('ogrenme', 'uzuv',
     'ogrenme — operatör öğrenmesi: RKHS, DeepONet/FINO, ızgara, Grassmann.'),
    ('ogrenme.grassmann', 'uzuv',
     'Grassmann manifoldu: izdüşüm, asal açılar, geodezik Exp/Log.'),
    ('ogrenme.izgara', 'uzuv',
     'Izgara — adaptif B-spline düğümleri ve sembolik regresyon kapanışı.'),
    ('ogrenme.kaggle_donanim', 'koşucu',
     'Kaggle koşucusu: tek hücrelik başlangıç, çok cihazlı eğitim.'),
    ('ogrenme.morse', 'uzuv',
     'MORSE-EULER TOPOLOJİK MUHASEBE (K27 katı sağlaması)'),
    ('ogrenme.operator', 'uzuv',
     'Operatör — DeepONet, FINO ve ızgaradan bağımsız operatör öğrenmesi.'),
    ('ogrenme.optimize', 'uzuv',
     'TÂLİM VE ENİYİLEME ÇİPİ -- deterministik dalga tâliminin icra çekirdeği.'),
    ('ogrenme.rkhs', 'uzuv',
     'RKHS — yeniden üreten çekirdek Hilbert uzayı ve kapalı form çözüm.'),
    ('ogrenme.test_arama', 'şahit',
     '``arama`` paketi sınamaları — M18, M19, M20, M21, M22.'),
    ('ogrenme.test_grassmann', 'şahit',
     '``ogrenme.grassmann`` sınamaları — K25 ve K26 tashihlerinin tartılması.'),
    ('ogrenme.test_ogrenme', 'şahit',
     'ogrenme test takımı.'),
    ('ogrenme.test_yaklasim', 'şahit',
     'yaklasim sınamaları.'),
    ('tanilama.dogrula_pareto', 'hakem',
     '(şerhsiz)'),
    ('tanilama.graf_capasi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.haraplama', 'hakem',
     'HARAPLAMA (lezyon) ÇALIŞMASI -- "melekeler ârızasız bir vücut mü?"'),
    ('tanilama.kok_avi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.kok_avi2', 'hakem',
     '(şerhsiz)'),
    ('tanilama.nizam', 'hakem',
     'NİZAM -- kod tabanının **padişah bakışı**: kime kimin eli uzanıyor.'),
    ('tanilama.nizam_dolasiklik', 'hakem',
     'DOLAŞIKLIK NİZAMI -- Dosya 1\'in hükmü **ölçülür**, iddia edilmez.'),
    ('tanilama.ram_repro', 'hakem',
     '(şerhsiz)'),
    ('tanilama.referans_avi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.sadakat', 'hakem',
     'MANTIĞA SADAKAT ÖLÇÜMÜ -- kütük H102\'nin açık borcunun kapatılması.'),
    ('tanilama.sahip_avi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.sizinti_avi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.sizinti_gerileme_testi', 'hakem',
     '(şerhsiz)'),
    ('tanilama.tefti', 'hakem',
     'TEFTİŞ -- padişahın **fiilen koşturduğu** her fonksiyon, dosyasıyla beraber.'),
    ('tanilama.umumi_profil', 'hakem',
     '(şerhsiz)'),
)

def kademe2(girisler=None):
    """**2. KADEME ARTIK ÖLÇÜLÜR, ELLE YAZILMAZ.**

    Buraya kadar ``KADEME2`` on sekiz satırlık elle tutulan bir
    demetti ve içindeki on modül (``token_uzaylari.morfizm``,
    ``mizan.onerme``, ``fitrat.serbest_enerji``, ``reel.hartley`` …)
    KÜME 7/8'de dağıtıldığı için **artık mevcut değildi**. Elle
    tutulan bir liste, ölçtüğünü iddia ettiği şeyin bayatlamasını
    göremez.

    "Ana akışta fiilen iş görüyor" cümlesinin hakiki karşılığı zaten
    ``nizam.padisahin_eli``dir: tahttan başlayan içe-aktarma kapanışı.
    O hâlde kademe 2 = **tahttan erişilen modüller**. Bu ölçü
    kırmızıya dönebilir (H90): bir uzuv akıştan düşerse sayı düşer.

    ÖLÇÜLEN TUZAK: hekimin (``tanilama/``) üzerinden geçilmez. Divan
    bütün tebaayı içe aktardığı için, taht divanı çağırınca 94 modülün
    91'i "erişilir" görünüyordu. Muayene edilmek iş görmek değildir.
    """
    from tanilama.nizam import padisahin_eli, GIRISLER
    return {m for m in padisahin_eli(girisler or GIRISLER,
                                     gecilmez=("tanilama",))
            if not m.startswith("tanilama")}


#: Geriye dönük ad. Demet değil, **ölçülen** kümedir.
KADEME2 = ()


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
        "kademe2": len(kademe2()),
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
