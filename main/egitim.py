"""
KÜLLÎ DİMAĞ -- YEREL VE GENEL TÂLİM MOTORU (PADİŞAH TÂLİM)
Dosya: main/egitim.py

`nefs/kulli_egitim.py`nin meşru uzuvları buraya zerk edilmiştir ve o
dosya ilga edilmiştir. Zerk tablosu ve **divanın tablosundaki üç
yanlış** aşağıda, "İNTİKAL MUHASEBESİ" başlığındadır.

Vazifesi:
  2D izafî ``tiktoken`` gömmesi, HDTF ağaç katlaması, 44 meleke Lie
  cebri, dörtlü topolojik zırh, QSVT dinamik Gibbs soğutması, STA
  karşıt-adiyabatik sürüş ve GCL/FCT kapalı formunda tâlim; **ve**
  41 melekeyi fiilen eniyileyen küllî kayıp hattı.

===================================================================
İNTİKAL MUHASEBESİ -- NE ALINDI, NE ALINMADI, DİVAN NEREDE YANILDI
===================================================================

**ALINANLAR (fiilen orada vardı ve buraya taşındı):**

    kaynak uzuv                     buradaki mevkii
    ------------------------------  ----------------------------------
    EgitimAyari + üç profil         ``EgitimAyari``, ``KISA_CPU``,
    (ölçülmüş şerhleriyle)          ``ORTA``, ``AZAMI_KAGGLE``
    arc.bol ile imtihan bölümü      ``KulliDalgaTalimMotoru.__init__``
    V_ilk/V_son/seyir telemetrisi   ``kulli_kayip_talimi``
    düşen_uzuv, kayıp_çağrısı       aynı yerde
    kulli_kayip hattı               ``kulli_kayip_talimi``  ← ASIL UZUV
    süreç havuzu (fork + _isci)     ``_isci_kur``, ``_isci_kayip``

**DİVANIN TABLOSUNDAKİ ÜÇ YANLIŞ -- ölçtüm, kabul etmedim:**

1. *"Tek-iplik BLAS intizamı (`tek_iplik_zorla`) zerk edildi."*
   **O dosyada böyle bir şey YOKTU.** Tarandı: ``OMP_NUM_THREADS``,
   ``tek_iplik`` -- ikisi de yok. Fikir doğrudur ve buraya **yeni
   olarak** kondu; fakat "oradan alındı" demek yanlış olurdu. Üstelik
   gerekçesi ölçülmüştür: bu turda ``np.linalg.solve``un döngü içinde
   BLAS iş parçacığı maliyeti hesabı gömdüğü ve 11,96 sn → 0,0029 sn
   (4100×) fark çıktığı ölçüldü.

2. *"Metropolis MCMC zincirleri (`zincir`, `ornek`) ilga edildi."*
   **O dosyada Metropolis YOKTU.** ``zincir`` ve ``ornek`` orada yalnız
   ayar dataclass'ında birer **tam sayıdır** ve `nefs/talim.py`ye
   geçirilir. Hakikî Metropolis `nefs/talim.py`dedir; bu dosyayı
   silmek onu kaldırmaz. Kaldırdım demek, yapmadığım bir işi yaptım
   demek olurdu.

3. *"Gri kodlama MCMC kalıntısıdır, ilga edilsin."*
   **Gri kod MCMC kalıntısı değil, parametrenin kübite kodlanmasıdır.**
   Yeni motor sürekli uzayda çalıştığı için eğitim hattında artık
   kullanılmıyor; fakat kütüğün **H75 denetimi** onu kullanır. Onun
   için silinmedi, son kullanıcısına (`nefs/hukum_denetimi.py`)
   nakledildi ve H75 hâlâ yeşil. Silmek, kayıtlı bir hükmü açık nakz
   olmadan düşürmek olurdu.

**ALINMAYANLAR (hakikaten oradaydı ve ilga edildi):**

    as_gek_mukayesesi   -- AS-GEK vekil mukayese döngüsü
    uygunluk çağrısı    -- belirteç kestirimli eski skaler kayıp

===================================================================
İKİ TÂLİM VARDIR VE İKİSİ AYRI ŞEYDİR
===================================================================

1. ``kulli_kayip_talimi``  -- 41 melekeyi ``kulli_kayip`` ile ölçüp
   `ogrenme/optimize.py`nin küllî motoruyla eniyiler. **Fiilen bir
   kaybı düşüren hat budur.**
2. ``dalga_talimi_kos``    -- HDTF + Ĥ_Dimağ + QSVT + STA + FCT.
   Şemanın bablarını koşturur.

**Ölçülmüş had, saklamıyorum:** ikinci hattın zırh kaybı üç çevrimde
``104,653426``da sabit kaldı; yani o hat şu anda **öğrenmiyor**. ARC
görevlerini fiilen çözen ise üçüncü bir hattır: `main/cikarim.py`nin
görev tâlimi (``3618c87e``, sırf ağırlıktan, birebir).
"""
from __future__ import annotations

# --- BLAS ÇEKİRDEK İNTİZAMI: ``numpy``dan ÖNCE tek ipliğe sabitlenir.
#
# **Bu, `kulli_egitim.py`den alınmadı -- orada yoktu; buraya yeni
# kondu.** Gerekçesi bu turda ölçüldü: küçük matrislerde BLAS iş
# parçacığı maliyeti hesabın kendisini gömüyor (72×100'lük bir mesele
# için 60 devir 11,96 sn; tek iplikte ve ters ön-hesapla 0,0029 sn).
# Çoklu süreçte ise iplikler birbirinin çekirdeğini kırar.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import json                                              # noqa: E402
import sys                                               # noqa: E402
import time                                              # noqa: E402
from dataclasses import dataclass, field                 # noqa: E402
from typing import Dict, List, Optional, Sequence, Tuple  # noqa: E402

import numpy as np                                       # noqa: E402

from nefs.musahede import gorevleri_getir                                    # noqa: E402
# HDTF ağaç katlaması ``kuantum/yazmac.py``daydı ve **MPS/QTT
# çekirdeği** üretiyordu -- yâni iptal edilen usulün ta kendisi.
# Motor silinince o da gitti; veri hazırlığı artık qudit
# kodlamasıdır (``nefs/qyazmac.py``).                    # noqa: E402
from ogrenme.optimize import (qsvt_gibbs_sogutma,        # noqa: E402
                          statik_faz_tablosu_oku)
from nefs.musahede import IzafiMevki2D, tiktoken_2d_kodla   # noqa: E402
from nefs.melekeler import melekeleri_kur                # noqa: E402
from ogrenme.optimize import OptimizeAyari               # noqa: E402
from ogrenme.optimize import hoca_egit                   # noqa: E402
from ogrenme.optimize import (chebyshev_tasarimi,        # noqa: E402
                              kestirmeden_sur)
from nefs.zirh import zirhla                        # noqa: E402
from main import hazine                             # noqa: E402
# ── MÎZÂN-I KÜLLÎ VE KUANTUM HAFIZASI ──────────────────────────────
# **USUL FERMANI (docs/zabit/USUL_UMUMIDEN_HUSUSIYE.md):** bu iki satır
# modüller HENÜZ YOKKEN yazıldı. Çağrı evvel yazılır, uzuv sonra; böylece
# bağlanmamış bir dosya yazmak imkânsız olur.
from nefs.kulli_mizan import (MizanAyari, kulli_mizan,   # noqa: E402
                              mizan_cetveli, rust)
from nefs.hafiza import Hafiza                           # noqa: E402

#: Ağırlıkların yattığı dizin. ``main/cikarim.py`` buradan okur.
HAZINE_DIZINI = os.environ.get("MUCIT_HAZINE", "depo/hazine")

__all__ = ["EgitimAyari", "KISA_CPU", "ORTA", "AZAMI_KAGGLE",
           "tek_iplik_zorla", "KulliDalgaTalimMotoru", "gecit",
           "ogreniyor_mu", "kulli_kayip_talimi", "gorev_talimi", "kos",
           "HAZINE_DIZINI"]


def tek_iplik_zorla() -> Dict[str, str]:
    """BLAS ipliğini 1'e sabitle; **hangi değişkenlerin konduğunu döndür**.

    ``numpy`` yüklendikten sonra çağrılırsa **geç kalmıştır** ve bu
    sessizce geçilmez: dönen sözlükte ``geç`` alanı doğru olur. Modül
    başındaki ayar asıl olandır; bu fonksiyon alt süreçler içindir.
    """
    ad = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
          "NUMEXPR_NUM_THREADS")
    for a in ad:
        os.environ[a] = "1"
    return {"değişken": ",".join(ad), "geç": "numpy" in sys.modules}


# =====================================================================
#  HİYERARŞİK TÂLİM AYARLARI -- `kulli_egitim.py`den zerk edildi
# =====================================================================
@dataclass
class EgitimAyari:
    """Yazmaç, veri, dalga ve donanım ölçüleri **tek yerde**.

    Kullanıcı hükmü: *"modelin tüm parametrelerini en genel eğitim için
    mümkün olan hududun en sonuna kadar açmanı istiyorum."* Hiçbiri
    koda gömülü değildir.
    """
    ad: str = "kısa"
    # --- yazmaç (nefsin kendisi)
    #: **FERMANLA DEĞİŞTİ: 4 → 16.** İkili kodlama dalı imha edilince
    #: (``nefs/qegitim.py``) kategorik kodlama ``kubit ≥ sozluk``
    #: ŞARTINA bağlandı: 16 belirteci 4 boyutta eşit uzaklıkta dizmek
    #: imkânsızdır ve o imkânsızlığı ikili kodlamayla örtmek tam da
    #: yasaklanan şeydi. 16'da bütün ikili mesafeler eşittir (5,657;
    #: değişke 0,0000) -- yâni fiilen bir qudit tabanı.
    #:
    #: **BEDELİ SAKLANMIYOR:** yazmaç genişler ve eski MPS motoru
    #: yavaşlar. O motor zaten fermanla iptaldir; bedel onun tasfiyesini
    #: geciktirmenin bedelidir, bu şartın değil.
    satir_kubiti: int = 16
    yerel_kubit: int = 1
    bag: int = 16                    # χ
    mera_kademe: int = 3
    # --- veri
    gorev: int = 24
    ornek_sayisi: int = 4
    pencere: int = 8
    sozluk: int = 16
    degerlendirme_gorevi: int = 4
    dogrulama_sayisi: int = 100
    kademe_gorevi: int = 2
    azami_uret: int = 32
    #: Eski kübit kodlaması ölçüsü. Yeni motor (`ogrenme/optimize.py`)
    #: sürekli uzayda çalışır ve parametreyi kübite açmaz; ``bit``
    #: yalnız eski ölçümlerin tekrarlanabilirliği için duruyor.
    bit: int = 6
    yaricap: float = 2.5
    # --- arama (FCT kapalı formu + blok koordinat inişi)
    nqs_gizli: Tuple[int, ...] = (48,)
    nqs_derece: int = 5
    cevrim: int = 6
    ornek: int = 24
    zincir: int = 8
    oran: float = 0.20
    kademe: float = 0.6
    lam: float = 1e-2
    talim_tur: int = 3
    altuzay_ornek: int = 24
    #: Blok koordinat inişi: 0 = kapalı (bütün yönler her turda).
    blok: int = 0
    #: Kesit boyutu ``r``yi bağlayan kübit haddi. **Ölçüldü** (d=262,
    #: aynı bütçe, yarıçap 2,5)::
    #:
    #:     V(p₀)                       0,5758
    #:     "etkin" altuzay r=8         yayılım 0,0026  (rastgeleden kötü)
    #:     Walsh kesiti r=32  en iyi   0,4443
    #:     TAM UZAY  d=262    en iyi   0,3215
    #:
    #: Kesit ulaşılabilir iyileşmenin yarısını yiyor; had ``d·bit``i
    #: aşacak kadar açıldı ki kesit kurulmasın ve arama tam uzayda koşsun.
    azami_kubit: int = 4096
    # --- şemanın QSVT/FCT ölçüleri
    sanal_kubit_sayisi: int = 22_000_000
    qsvt_derecesi: int = 32          # cetveldeki derece; arama YASAK
    beta_maksimum: float = 4.0       # cetvelde mühürlü β
    gcl_nokta_sayisi: int = 128
    lambda_mizan: float = 0.035
    ogrenme_orani: float = 0.01
    # --- MÎZÂN-I KÜLLÎ (nefs/kulli_mizan.py) -- dört kefenin ağırlıkları
    #: ``ℒ_Küllî = ℒ_Rezonans + λ₁ℒ_Çevrim + λ₂ℒ_Monogami + λ₃ℒ_Hodge``
    #:
    #: **KÖR NLL BURADA YOKTUR VE OLMAYACAKTIR.** Padişahın hükmü:
    #: *"loss = CrossEntropyLoss() satırı modelin katilidir."* Veriye
    #: bağlanma tek yerdedir ve o da kör değildir: Uhlmann kuantum
    #: sadakati (``ℒ_Rezonans``). Veri bir kural değil, dışarıdan gelen
    #: **zayıf bir uyarımdır**; modelden verinin faz gürültüsünü taklit
    #: etmesi değil, ana frekansıyla rezonansa girmesi istenir.
    lam_cevrim: float = 1.0        # λ₁ Wilson holonomisi (tenakuz)
    lam_monogami: float = 0.5      # λ₂ CKW dolanıklık monogamisi
    lam_hodge: float = 0.75        # λ₃ Hodge tenakuzsuzluğu
    #: Muhakeme çevrimi kaç adımlıdır (``X → Y → Z → X``).
    cevrim_boyu: int = 3
    #: Taranacak azamî kapalı çevrim sayısı.
    cevrim_sayisi: int = 8
    # --- RÜŞT ÇİZELGESİ (Tabula Rasa zabıtı)
    #: ``α(t) = σ((t − t₀)/τ)``. ``α → 0`` bebeklik: hata doğrudan
    #: **fıtrata** (ağırlıklara) akar, terazi kalibre edilir.
    #: ``α → 1`` rüşt: fıtrat kilitlenir, hata **hafızaya** fatura edilir.
    #: Kör terazide hüküm verilemez; onun için bu bir aç-kapa anahtarı
    #: değil, adyabatik bir faz geçişidir.
    rust_t0: float = 0.5           # geçişin ortası (tur nispetiyle)
    rust_tau: float = 0.15         # geçişin genişliği
    # --- KUANTUM ASOSİYATİF HAFIZA (nefs/hafiza.py)
    #: **AĞIRLIK HAFIZA DEĞİLDİR.** Ağırlık fıtrattır, gramerdir,
    #: reflekstir. Tecrübe edilen safsatalar ve meşru teemmüller ayrı
    #: bir yoğunluk operatöründe (``ρ_Hafıza``) saklanır.
    hafiza_kapasitesi: int = 256
    #: Kraus yazma oranı ``ε``: ``ρ ← (1−ε)ρ + ε|Φ⟩⟨Φ|``.
    hafiza_yazma: float = 0.05
    #: Liouville sönümü ``γ``: delilsiz kuru zan zamanla buharlaşır.
    hafiza_sonumu: float = 0.02
    #: Zeno budaması eşiği: hafızada cerhedilmiş bir yolla örtüşme bunu
    #: aşarsa döngü **tamamlanmadan** kesilir.
    zeno_esigi: float = 0.35
    # --- donanım
    surec: int = 0                   # 0 = donanımdan tayin et
    tohum: int = 0
    #: **TÂLİM SAAT HADDİ (kütük H212).** ``ogrenme/hoca.py``nin bütçe
    #: freni bu haddi okur: ``tur × d × düğüm`` çağrısının kestirilen
    #: süresi bunu aşarsa koşu **başlamaz**, ``RuntimeError`` verir.
    #:
    #: Sessiz bir sabit değil, profilde **ilan edilen** bir ölçüdür ve
    #: sebebi ölçümdür: aynı fren ``AZAMI_KAGGLE``ı 1 saatlik varsayılan
    #: hadde reddediyordu (d=264, tur=3, düğüm=4097 → 3,24 milyon çağrı
    #: ≈ 18 saat). O profil zaten kasten uzun koşudur; haddi profilin
    #: kendisi söylemelidir, fren değil.
    azami_talim_saati: float = 1.0

    def qayar(self):
        from nefs.zihin_durumu import QAyar
        # **YIĞIN YAZMACA GEÇER.** Evvelce geçmiyordu ve yazmaç daima
        # ``B=1`` kuruluyordu: 41 melekenin 300 000 kapısı her örnek
        # için baştan vuruluyordu. Hız teftişi bunu ölçtü.
        return QAyar(satir_kubiti=self.satir_kubiti,
                     yerel_kubit=self.yerel_kubit, bag=self.bag,
                     mera_kademe=self.mera_kademe, tohum=self.tohum,
                     yigin=int(self.ornek_sayisi))


#: **CPU'da koşan kısa hâl.** ``B = ornek_sayisi`` bu ortam için
#: ölçülerek seçildi (kütük H151)::
#:
#:      B    kayıp sn   parametre yayılımı   veri gürültüsü
#:      2      1,73          0,0191               —
#:      4      2,96          0,0066            0,0013
#:      8      5,51          0,0045            0,0019
#:     16     10,55          0,0058            0,0007
#:     32     20,35          0,0051            0,0018
#:
#: B büyüdükçe parametre yayılımı **düşüyor** (σ/√B). B=4'ten sonra
#: ölçülebilir kazanç yok, maliyet doğrusal artıyor. Delil budur: B=4.
#: **ÖLÇÜLEREK DEĞİŞTİ (hız teftişi).** ``ornek_sayisi`` artık yazmacın
#: **yığın boyudur** ve 4 değil 64'tür; ``pencere`` 8 değil 512'dir.
#: Sebebi ölçümdür -- aynı kayıp, aynı netice, farklı hız::
#:
#:      B    L      belirteç/sn
#:      4    8            215
#:     64  512         43 859
#:    128  512         61 660      ← seçilen (tavan)
#:    256  512         58 248
#:    512  512         32 646      (bellek doyumu)
#:
#: Kayıp değişti çünkü veri değişti (daha uzun bağlam, daha çok örnek),
#: hesabın kendisi değil: B=4/L=8'de iki hat **birebir** aynı sayıyı
#: veriyor (2,888511).
KISA_CPU = EgitimAyari(ad="kısa-CPU", ornek_sayisi=128, pencere=512,
                       cevrim=1, ornek=3, zincir=2, talim_tur=1,
                       altuzay_ornek=6, degerlendirme_gorevi=8,
                       dogrulama_sayisi=20,
                       sanal_kubit_sayisi=1_000_000, bag=8)

#: Orta hâl -- tek makinede saatler.
ORTA = EgitimAyari(ad="orta", satir_kubiti=6, bag=32, gorev=120,
                   ornek_sayisi=24, degerlendirme_gorevi=40,
                   azami_uret=120, dogrulama_sayisi=100,
                   nqs_gizli=(96, 64), nqs_derece=6, cevrim=40,
                   ornek=128, zincir=32, bit=8,
                   azami_talim_saati=6.0)

#: **Kaggle azamî hâli.** 4 cihaz, ~84 GB VRAM. Ceridenin taksimatı::
#:
#:     Veri yazmacı : B = 2048 dizi × L_bağlam = 4096 belirteç
#:                  = 8.388.608 belirteç / adım
#:
#: **HUDUT -- açıkça:** bu ayar bu ortamda KOŞMAMIŞTIR ve koştuğu iddia
#: edilmiyor. Burada GPU yoktur (``torch`` kurulu değil); 8,4 milyon
#: belirteçlik yığın bu makinenin belleğine sığmaz.
AZAMI_KAGGLE = EgitimAyari(
    ad="azamî-Kaggle", satir_kubiti=12, yerel_kubit=1, bag=256,
    mera_kademe=5, gorev=1000, ornek_sayisi=2048, pencere=4096,
    sozluk=16, degerlendirme_gorevi=120, dogrulama_sayisi=100,
    azami_uret=0, bit=10, yaricap=3.0, nqs_gizli=(512, 256, 128),
    nqs_derece=8, cevrim=400, ornek=4096, zincir=256, oran=0.10,
    kademe=0.4, lam=1e-3, sanal_kubit_sayisi=88_000_000,
    qsvt_derecesi=32, beta_maksimum=4.0, azami_talim_saati=24.0)

#: Ayar adından profile -- komut satırı için.
PROFILLER: Dict[str, EgitimAyari] = {
    "kısa": KISA_CPU, "kisa": KISA_CPU, "orta": ORTA,
    "azamî": AZAMI_KAGGLE, "azami": AZAMI_KAGGLE}


# =====================================================================
#  TÂLİM GEÇİDİ -- koşmadan EVVEL dimağın akdi ve illeti denetlenir
# =====================================================================
def gecit(sert: bool = True, hiz_ayari=None) -> Dict[str, object]:
    """TÂLİME GİRMEDEN EVVEL İKİ ŞART -- akit ve illet.

    Bir tâlim koşusu saatler sürer. Koşunun sonunda "sebep çizgesinde
    çevrim varmış" yahut "sözleşmedeki meleke kodda yokmuş" demek,
    saatleri çöpe atmak demektir. Bu geçit ikisini de **koşudan evvel**
    ve **saniyeler içinde** ölçer:

    1. ``nefs/akit.py`` -- SÖZLEŞME İLE KOD UYUŞUYOR MU?
       Uzuv sofrasında yazan her melekenin kodda karşılığı var mı,
       hangileri hâlâ vekil formülle çalışıyor, hangileri veri yoluna
       hiçbir şey **yazmıyor** (koşar, hesaplar, tesirsizdir).

    2. ``nefs/illet.py`` -- SEBEP ÇİZGESİ SAĞLAM MI?

       (a) **ZAMAN AÇILIMLI** çizge çevrimsiz olmalı. Alan seviyesindeki
           çizgede çevrim beklenir ve kusur değildir (``makam`` ile
           ``mizan`` birbirini besler; akış devridaimlidir) -- ölçüldü:
           10 alan, 58 kenar, 6 çevrim. Orada çevrim aramak yanlış
           soruydu. Doğru soru zaman açılımındadır: ``alan@t`` bir
           **sonraki** adımı etkiler, o hâlde orada çevrim çıkarsa bir
           adım kendi geleceğine bağlı demektir ve bu imkânsızdır.
       (b) ``kelam``, ``veri``den **yalnız hüküm üzerinden** beslenmeli.
           Ölçünün adı ``hüküm_şartıyla_ayrık``tır. ``şartsız_ayrık``
           DEĞİLDİR ve olmamalıdır: kelamın veriden hiç etkilenmemesi
           modelin girdiyi hiç görmemesi demek olurdu.

    3. ``tanilama/hiz_teftisi.py`` -- **BELİRTEÇ/SN HADDİ TUTUYOR MU?**
       Ferman: *"hız konusunda garanti elde etmeden umumi eğitim
       başlatma."* Bir tâlim koşusunun ne kadar süreceği, koşmadan
       evvel tek bir kayıp çağrısı ölçülerek bilinir. Had
       ``tanilama/hiz_teftisi.py:HAD``dır ve orada yazılıdır.

    ``sert`` doğruysa ihlâl ``assert`` ile koşuyu **durdurur**. Yumuşak
    kipte yalnız raporlanır; o kip ölçüyü görmek içindir, geçmek için
    değil.
    """
    from nefs.akit import akdi_denetle, vekil_kalanlar, yazmayanlar
    from nefs.illet import (alan_cizgesi, cevrimler, kelam_ayrismasi,
                            zaman_cizgesi)

    uydu, sikayet = akdi_denetle()
    vekil = vekil_kalanlar()
    sessiz = yazmayanlar()

    dug, ken, kabul = alan_cizgesi()
    assert dug, "sebep çizgesi BOŞ -- illet ölçüsü bir şey ölçmüyor"
    alan_cevrimi = cevrimler(dug, ken)
    zg, _yer = zaman_cizgesi()
    zaman_cevrimi = cevrimler(list(zg.dugumler), list(zg.kenarlar))
    ayrisma = kelam_ayrismasi()

    o: Dict[str, object] = {
        "akit_uydu": bool(uydu), "akit_şikâyeti": list(sikayet),
        "vekil_meleke": len(vekil), "yazmayan_meleke": len(sessiz),
        "alan": len(dug), "kenar": len(ken),
        "alan_çevrimi": len(alan_cevrimi),
        "zaman_düğümü": len(zg.dugumler),
        "zaman_çevrimi": [list(c) for c in zaman_cevrimi],
        "kelam_ayrıştı": bool(ayrisma.get("hüküm_şartıyla_ayrık", False)),
        "kelam_dökümü": ayrisma,
    }
    if hiz_ayari is not None:
        from tanilama.hiz_teftisi import AZAMI_SANIYE, HAD, olc
        h = olc(hiz_ayari)
        o["belirteç_sn"] = float(h["belirteç_sn"])
        o["hız_haddi"] = float(HAD)
        o["hız_geçti"] = bool(h["belirteç_sn"] >= HAD)
        o["kayıp_süresi"] = float(h["kayıp_süresi"])
        o["en_pahalı_uzuv"] = (h["tek_meleke"][0][0]
                               if h["tek_meleke"] else "?")
    if sert:
        assert uydu, ("AKİT TUTMUYOR -- sözleşme ile kod uyuşmuyor:\n  %s"
                      % "\n  ".join(sikayet[:8]))
        assert not zaman_cevrimi, (
            "ZAMAN AÇILIMLI SEBEP ÇİZGESİNDE ÇEVRİM VAR -- bir adım "
            "kendi geleceğine bağlı: %r" % (zaman_cevrimi[:3],))
        assert ayrisma.get("kurulabilir", False), (
            "zaman çizgesi kurulamadı -- illet ölçüsü boş: %r" % (ayrisma,))
        assert ayrisma.get("hüküm_şartıyla_ayrık", False), (
            "KELAM VERİDEN DOĞRUDAN BESLENİYOR -- hüküm atlanabiliyor. "
            "Bu, ezberin açık kapısıdır. Döküm: %r" % (ayrisma,))
        if "belirteç_sn" in o:
            from tanilama.hiz_teftisi import HAD
            assert o["hız_geçti"], (
                "HIZ HADDİ TUTMUYOR -- TÂLİM BAŞLAMAZ.\n"
                "  ölçülen : %.1f belirteç/sn\n"
                "  had     : %.0f belirteç/sn  (%.0f kat eksik)\n"
                "  bir kayıp çağrısı: %.4f sn   en pahalı uzuv: %s\n"
                "  Ferman: hız garantisi elde etmeden umumi tâlim "
                "başlatılmaz." % (o["belirteç_sn"], HAD,
                                  HAD / max(1e-9, o["belirteç_sn"]),
                                  o["kayıp_süresi"], o["en_pahalı_uzuv"]))
    return o


def ogreniyor_mu(seyir: Sequence[float], lam: float = 1e-3
                 ) -> Dict[str, object]:
    """SEYİR EĞRİSİ DÜŞÜYOR MU -- gürültüye bakmadan (``ogrenme/izgara.py``).

    Kaybın son iki adımına bakıp "düştü" demek gürültüyü hüküm
    sanmaktır. Doğru soru eğrinin **eğilimidir** ve eğilim, gürültülü
    bir örneklemden ancak düzenlenmiş bir uydurmayla çıkarılır::

        min_c ‖Bc − y‖² + λ·cᵀSc

    ``S`` bükülme dizeyidir (``∫B''B''``); ``λ`` eğriyi yumuşatır. Bu
    tam olarak ``ogrenme/izgara.py``nin ``duzenli_uydur``udur ve
    burada süs değil hükümdür: ``eğim ≥ 0`` ise **tâlim öğrenmiyor**
    ve netice öyle yazılır.

    Bağıntı ölçütü (``bagintili_olcut``) ikinci şahittir: sabit bir
    eğri hiçbir zaman kazanamaz (payda sıfırsa 0 döner).
    """
    y = np.asarray(list(seyir), float).reshape(-1)
    assert y.size >= 2, "seyir eğrisi için en az iki nokta lâzım"
    assert np.all(np.isfinite(y)), "seyirde NaN/Inf var"
    from ogrenme.izgara import bagintili_olcut, duzenli_uydur

    t = np.linspace(-1.0, 1.0, y.size)
    G = max(2, min(8, y.size // 3))
    k = 3 if y.size > 5 else 1
    u = duzenli_uydur(t, y, G, k, lam=float(lam))
    tahmin = np.asarray(u["B"], float) @ np.asarray(u["c"], float)
    n = max(2, y.size // 4)
    egim = float((tahmin[-1] - tahmin[-1 - n]) / (t[-1] - t[-1 - n]))
    bag = float(bagintili_olcut(t, y))
    # İKİ ŞAHİT BİRDEN. Yalnız eğime bakmak yetmez: sabit bir seyirde
    # eğim ``−2,5e−16`` çıkıyor (ölçüldü) ve kayan nokta gürültüsünü
    # "öğreniyor" diye okumak tam da örtmek olurdu. ``bagintili_olcut``
    # sabit eğride paydası sıfır olduğu için **tam 0** döner ve o kapıyı
    # kapatır.
    return {"eğim": egim, "artık": float(u["artık"]),
            "bükülme": float(u["bükülme"]), "bağıntı": bag,
            "öğreniyor": bool(egim < 0.0 and bag < 0.0),
            "toplam_düşüş": float(y[0] - y[-1])}


# =====================================================================
#  SÜREÇ HAVUZU -- kübit ileri geçişi paraleldir
# =====================================================================
_ISCI: Dict[str, object] = {}


def _isci_kur(ayar: EgitimAyari, veri, kademe=None) -> None:
    from nefs.melekeler import QNefs
    tek_iplik_zorla()
    _ISCI["nefs"] = QNefs(ayar.tohum, ayar.qayar())
    _ISCI["veri"] = veri
    _ISCI["ayar"] = ayar
    _ISCI["kademe"] = list(kademe or [])
    _ISCI["nefs"].idrak_et(np.zeros((2, ayar.satir_kubiti)))


def _isci_kayip(p: np.ndarray) -> float:
    """İşçi de **aynı** mizanı hesaplar; ayrı kayıp mukayeseyi bozardı."""
    a: EgitimAyari = _ISCI["ayar"]        # type: ignore[assignment]
    t = kulli_mizan(_ISCI["nefs"], _ISCI["veri"], p,   # type: ignore
                    a.sozluk, ayar=mizan_ayari(a),
                    hafiza=_ISCI.get("hafıza"),
                    kademe_gorevleri=_ISCI.get("kademe"))
    return float(t["kayıp"])


def mizan_ayari(a: EgitimAyari) -> "MizanAyari":
    """Tâlim ayarından mizan ayarı -- **tek kaynak**, iki nüsha değil."""
    return MizanAyari(
        lam_cevrim=float(a.lam_cevrim), lam_monogami=float(a.lam_monogami),
        lam_hodge=float(a.lam_hodge), cevrim_boyu=int(a.cevrim_boyu),
        cevrim_sayisi=int(a.cevrim_sayisi), rust_t0=float(a.rust_t0),
        rust_tau=float(a.rust_tau), zeno_esigi=float(a.zeno_esigi),
        # Rüşt çizelgesinin paydası tâlimin kendi bütçesidir; elle
        # yazılmış bir sabit değildir. Bütçe değişince geçiş de kayar.
        toplam_adim=max(1, int(a.talim_tur) * max(1, int(a.altuzay_ornek))),
        tohum=int(a.tohum))


# =====================================================================
#  1. HAT -- KÜLLÎ KAYIP TÂLİMİ (41 meleke fiilen eniyilenir)
# =====================================================================
def kulli_kayip_talimi(ayar: EgitimAyari = KISA_CPU,
                       gorevler: Optional[Sequence] = None,
                       paralel: bool = True) -> Dict[str, object]:
    """41 melekeyi ``kulli_kayip`` ile ölçüp ``Talim`` ile eniyile.

    **Bu, `kulli_egitim.py`nin ASIL uzvudur ve divanın tablosunda
    hiç geçmiyordu.** Onsuz silmek, bir kaybı fiilen düşüren tek
    tâlim hattını yok etmek olurdu; ölçüldü: şemanın QSVT/FCT hattı
    zırh kaybını üç çevrimde hiç kıpırdatmıyor.

    Adam/SGD yoktur: ``Talim`` dokuz uzuvlu usuldür (dalga, had
    ölçümü, vekil yüzey, durgunluk, tünelleme, denge...).
    """
    from nefs.kulli_kayip import kademe_parametreleri_ac
    from nefs.melekeler import QNefs
    from nefs.qegitim import degerlendir, ornekler

    t0 = time.perf_counter()
    # **GEÇİT KOŞUDAN EVVEL.** Saatler süren bir tâlimin sonunda
    # "akit tutmuyormuş" demek saatleri çöpe atmaktır.
    kapi = gecit(sert=True, hiz_ayari=ayar)
    hepsi = list(gorevler) if gorevler is not None else \
        gorevleri_getir("training")
    # **İMTİHAN BÖLÜMLEMESİ** -- ezberi ve sızıntıyı engeller.
    egitim_gorevleri, dogrulama = gorevleri_getir(ne="böl", gorevler=
        hepsi, dogrulama=int(ayar.dogrulama_sayisi), tohum=ayar.tohum)
    veri = ornekler(egitim_gorevleri, azami=ayar.ornek_sayisi,
                    pencere=ayar.pencere, sozluk=ayar.sozluk,
                    tohum=ayar.tohum)

    nefs = QNefs(ayar.tohum, ayar.qayar())
    nefs.idrak_et(np.zeros((2, ayar.satir_kubiti)))
    # Kademe parametreleri ``d`` sabitlenmeden EVVEL açılmalıdır; boyut
    # ortada değişirse tâlim kendi öğrendiğini siler (H39).
    kademe_parametresi = kademe_parametreleri_ac(nefs.p)
    d = len(nefs)
    p0 = nefs.vektor()
    kademe_gorevleri = list(egitim_gorevleri)[:int(ayar.kademe_gorevi)]

    havuz = None
    surec = ayar.surec or 1
    if paralel and surec > 1:
        import multiprocessing as mp
        havuz = mp.get_context("fork").Pool(
            surec, initializer=_isci_kur,
            initargs=(ayar, veri, kademe_gorevleri))
        _ISCI["hafıza"] = None      # her işçi kendi hafızasını kurar

    # **HATA FONKSİYONU MÎZÂN-I KÜLLÎ'DİR** (nefs/kulli_mizan.py).
    #
    #     ℒ_Küllî = ℒ_Rezonans + λ₁ℒ_Çevrim + λ₂ℒ_Monogami + λ₃ℒ_Hodge
    #
    # Dördü de kuantumun kendi hadiselerinden mülhemdir ve hiçbiri
    # veriye kör teslimiyet değildir:
    #   Rezonans  -- Uhlmann sadakati (kör NLL DEĞİL)
    #   Çevrim    -- Wilson holonomisi; manayı bilmeden tenakuz bulur
    #   Monogami  -- CKW eşitsizliği; sahte illetleri budar
    #   Hodge     -- Δ|Ψ⟩ = 0; harmonik hüküm
    mzn = mizan_ayari(ayar)
    hafiza = Hafiza(kapasite=int(ayar.hafiza_kapasitesi),
                    yazma=float(ayar.hafiza_yazma),
                    sonum=float(ayar.hafiza_sonumu), tohum=int(ayar.tohum))
    _sayac = {"çağrı": 0}

    def kayip_p(P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, float))
        if havuz is not None:
            return np.array(list(havuz.map(_isci_kayip, list(P))))
        out = np.empty(P.shape[0], float)
        for i, p in enumerate(P):
            _sayac["çağrı"] += 1
            t = kulli_mizan(nefs, veri, p, ayar.sozluk, ayar=mzn,
                            hafiza=hafiza, adim=_sayac["çağrı"],
                            kademe_gorevleri=kademe_gorevleri)
            out[i] = float(t["kayıp"])
        return out

    # **`nefs/talim.py` ilga edildi; motor `ogrenme/optimize.py`dir.**
    # Bilinen bir yüzeyde ölçülerek karşılaştırıldı (d=24 ağırlıklı
    # karesel, V(p₀)=73,3498, asgarî 0)::
    #
    #     divanın taslak adımı   73,3498 → 73,3498   (SIFIR kazanç)
    #     eski nefs/talim        73,3498 → 72,5763
    #     ogrenme/optimize       73,3498 →  0,5410   ← seçilen
    #
    # Eski tâlimin kazancı %1; yeni motorunki 135 kat. Kübit kodlaması
    # (Gri kod) da kalktı: yeni motor sürekli uzayda çalışır.
    opt = OptimizeAyari(
        ad=ayar.ad, tur=ayar.talim_tur, yaricap=ayar.yaricap,
        gcl_nokta_sayisi=max(8, int(ayar.ornek)),
        yon_sayisi=int(ayar.altuzay_ornek), blok=int(ayar.blok),
        sesli=True, tohum=ayar.tohum)
    # **HOCA (kütük H212, H223'te motora eridi).** Üç uzuv da bu hatta
    # lâzımdır ve artık motorun kendi ayarındadır:
    #   TÜNEL  -- durgunluk düşüp HAD zorlayıcı bulamadığında STA
    #             karşıt-adiyabatik sürüşü (H29'un çift şartı).
    #   VEKİL  -- kapalı (varsayılan): küllî kayıp çağrısı pahalıdır,
    #             RKHS yüzeyi ancak aday çoğaldığında değer.
    #   BÜTÇE  -- ``d`` büyürse koşu SESSİZCE günlere yayılmasın diye
    #             peşinen reddeder (idrak/model.py dersi, H209).
    opt.tunel_acik = True
    opt.vekil_acik = False
    opt.bütçe_denetimi = True
    opt.azami_saniye = float(ayar.azami_talim_saati) * 3600.0
    try:
        r = hoca_egit(kayip_p, p0, opt)
    finally:
        if havuz is not None:
            havuz.close()
            havuz.join()

    p_yildiz = np.asarray(r["p"], float)
    assert p_yildiz.size == d, (
        "tâlim %d parametre aldı, %d döndürdü" % (d, p_yildiz.size))
    assert np.all(np.isfinite(p_yildiz)), "tâlim NaN/Inf parametre döndürdü"
    nefs.yukle(p_yildiz)
    deg = degerlendir(nefs, dogrulama, azami=ayar.degerlendirme_gorevi,
                      pencere=ayar.pencere, sozluk=ayar.sozluk,
                      azami_uret=ayar.azami_uret)

    # --- ÖĞRENİYOR MU? (ogrenme/izgara.py -- düzenli uydurma)
    ham_seyir = [float(x["V"]) for x in (r.get("seyir") or [])
                 if isinstance(x, dict) and "V" in x]
    ders = (ogreniyor_mu([float(r["V_ilk"])] + ham_seyir)
            if ham_seyir else
            {"öğreniyor": bool(r["V_son"] < r["V_ilk"]), "eğim": 0.0,
             "bağıntı": 0.0, "artık": 0.0, "bükülme": 0.0,
             "toplam_düşüş": float(r["V_ilk"] - r["V_son"])})

    # --- MİZANIN DÖRT KEFESİ AYRI AYRI (hangisi kırmızı, görünsün)
    kefeler = kulli_mizan(nefs, veri, p_yildiz, ayar.sozluk, ayar=mzn,
                          hafiza=hafiza, adim=_sayac["çağrı"],
                          kademe_gorevleri=kademe_gorevleri, ne="döküm")
    # --- VERİ KENDİ KENDİNİ DÖRDE AYIRDI MI? (zabıt V. fasıl)
    #     Hakikat / Yanlış / Şüpheli / Kuru gürültü -- etiketsiz.
    cetvel = mizan_cetveli(nefs, veri, p_yildiz, ayar.sozluk, ayar=mzn)

    # --- HAZİNE: ağırlıklar safetensors olarak kaydedilir (main/hazine.py)
    # **FITRAT İLE HADİSE AYNI DOSYADA, AYRI TENSÖRLERDE.** ``p``
    # ağırlıktır (fıtrat); ``hafıza$*`` tecrübedir (hadise). İkisini
    # ayrı tensörlerde tutmak, ayrı şeyler olduklarını dosyanın
    # kendisinde görünür kılar.
    kayit = hazine.koy(
        os.path.join(HAZINE_DIZINI, "dimag_%s" % ayar.ad),
        dict({"p": p_yildiz}, **hafiza.hazineye()),
        {"ayar": ayar.ad, "parametre": d, "V_ilk": float(r["V_ilk"]),
         "V_son": float(r["V_son"]), "satır_kübiti": int(ayar.satir_kubiti),
         "sözlük": int(ayar.sozluk), "pencere": int(ayar.pencere),
         "yerel_kübit": int(ayar.yerel_kubit), "bağ": int(ayar.bag),
         "mera_kademe": int(ayar.mera_kademe), "tohum": int(ayar.tohum),
         "öğreniyor": bool(ders["öğreniyor"]),
         "mizan": {k: v for k, v in kefeler.items()
                   if isinstance(v, (int, float))},
         "veri_cetveli": cetvel,
         "hafıza_kapasitesi": int(ayar.hafiza_kapasitesi),
         "hafıza_yazma": float(ayar.hafiza_yazma),
         "hafıza_sönümü": float(ayar.hafiza_sonumu),
         "zeno_eşiği": float(ayar.zeno_esigi)})

    return {"ayar": ayar.ad, "parametre": d,
            "geçit": kapi, "ders": ders, "hazine": kayit,
            "mizan": kefeler, "veri_cetveli": cetvel,
            "hafıza": hafiza.beyan(), "rüşt": float(kefeler["α_rüşt"]),
            "veri": len(veri), "süreç": surec,
            "V_ilk": float(r["V_ilk"]), "V_son": float(r["V_son"]),
            "süre_sn": time.perf_counter() - t0,
            "kayıp_çağrısı": int(r.get("kayıp_çağrısı", 0)),
            "seyir": r.get("seyir", []),
            "değerlendirme": deg,
            "tâlim_günlüğü": r.get("günlük", []),
            "düşen_uzuv": r.get("düşen_uzuv", {}),
            "kademe_görevi": len(kademe_gorevleri),
            "kademe_parametresi": kademe_parametresi,
            "p": p_yildiz}


# =====================================================================
#  2. HAT -- ŞEMANIN DALGA TÂLİMİ (HDTF + Ĥ_Dimağ + QSVT + STA + FCT)
# =====================================================================
class KulliDalgaTalimMotoru:
    """Tek akış: belirlenimci kuantum dalga tâlimi."""

    def __init__(self, ayar: Optional[EgitimAyari] = None) -> None:
        self.ayar = ayar or KISA_CPU
        self.meleke_manifoldu = melekeleri_kur(meleke_sayisi=44)
        self.izafi_mevki = IzafiMevki2D()
        self.faz_tablosu = statik_faz_tablosu_oku(
            derece=self.ayar.qsvt_derecesi, beta=self.ayar.beta_maksimum)
        self.gcl_dugumleri = chebyshev_tasarimi(
            self.ayar.gcl_nokta_sayisi, "düğüm")
        self.seyir: List[Dict[str, float]] = []

    def veri_durumu_hazirla(self, ham_veriler: Sequence
                            ) -> Dict[str, object]:
        """HDTF ikili ağaç katlamasıyla QTT süperpozisyonuna al."""
        t0 = time.perf_counter()
        vektorler: List[np.ndarray] = []
        for v in ham_veriler:
            if hasattr(v, "egitim") and getattr(v, "egitim", None):
                for cift in v.egitim:
                    vektorler.append(self.izafi_mevki.durum_vektoru_kur(
                        np.asarray(cift[0], dtype=int)))
            elif isinstance(v, dict) and "izgara" in v:
                vektorler.append(self.izafi_mevki.durum_vektoru_kur(
                    np.asarray(v["izgara"], dtype=int)))
            elif isinstance(v, dict) and "metin" in v:
                vektorler.append(np.asarray(
                    tiktoken_2d_kodla(str(v["metin"])), float))
        vektorler = [np.asarray(x, float).reshape(-1)
                     for x in vektorler if np.asarray(x).size]
        if not vektorler:
            raise ValueError("katlanacak veri yok")

        # ==============================================================
        # HDTF/QTT KATLAMASI YERİNE QUDİT KODLAMASI
        # ==============================================================
        #
        # Evvelce ``hiyerarsik_ikili_agac_katlama`` çağrılıyordu ve o,
        # veriyi **MPS/QTT çekirdeklerine** katlıyordu -- ``bag_boyutu``
        # ile kesip. İptal edilen usul tam olarak budur; motorla
        # beraber silindi.
        #
        # Yerine gelen: vektörler tek bir qudit durumuna kodlanır.
        # **Kesme yoktur**, dolayısıyla ``kesme = 0,0``dır ve bu bir
        # iyimserlik değil, atılan hiçbir şey olmadığının ifadesidir.
        from nefs.qyazmac import QuditYazmac, QuditAyar
        v = np.concatenate(vektorler)
        d = 1 << int(np.ceil(np.log2(max(v.size, 2))))
        d = int(min(max(d, 16), 1 << 16))
        lif = (d,)
        q = QuditYazmac(QuditAyar(d=d, lif=lif), n_satir=1,
                        satir_kubiti=int(np.log2(d)))
        w = np.resize(v, d).astype(complex)
        n = float(np.linalg.norm(w)) or 1.0
        q.psi = (w / n).reshape(1, d)
        sure = time.perf_counter() - t0
        print("  [QUDİT] %d veri parçası %.3f sn'de d=%d qudite kodlandı "
              "(kesme 0,0 -- kesme YOK)."
              % (len(vektorler), sure, d), flush=True)
        return {"cekirdek": [np.asarray(q.psi[0])], "kesme": 0.0,
                "kademe": 1, "süre_sn": sure,
                "parca": len(vektorler), "qudit": q}

    def talim_adimi_icra_et(self, durum: Dict[str, object]
                            ) -> Dict[str, float]:
        """Bab III, IV, V, VI gereğince tek makro QSVT dalga adımı."""
        t0 = time.perf_counter()
        H_dimag = self.meleke_manifoldu.hamiltonyen_uret()
        H_zirhli, zirh = zirhla(H_dimag)
        mizan = self.meleke_manifoldu.bgcm_mizan_enerjisi()
        H_toplam = H_zirhli + self.ayar.lambda_mizan * mizan * np.eye(
            H_zirhli.shape[0])

        cek = durum["cekirdek"]
        v = np.asarray(cek[0], float).reshape(-1)
        n = H_toplam.shape[0]
        v = v[:n] if v.size >= n else np.pad(v, (0, n - v.size))
        sogutulmus = qsvt_gibbs_sogutma(v, H_toplam, self.faz_tablosu,
                                        beta_maks=self.ayar.beta_maksimum)

        surus = False
        if float(zirh.get("kohomoloji_tikaniklik", 0.0)) > 0.35:
            sogutulmus = kestirmeden_sur(ne="sürüş_uygula",
                                         durum=sogutulmus,
                                         hamiltonyen=H_toplam,
                                                 sure_tau=1.0)
            surus = True

        ornek = np.interp(self.gcl_dugumleri,
                          np.linspace(-1.0, 1.0, len(sogutulmus)),
                          np.asarray(sogutulmus, float).reshape(-1))
        self.meleke_manifoldu.katsayilari_guncelle(
            chebyshev_tasarimi(int(np.size(ornek)) - 1, "katsayı", f=ornek),
            oran=self.ayar.ogrenme_orani)

        kayit = {"adim_suresi_sn": time.perf_counter() - t0,
                 "topolojik_kayip": float(zirh.get("toplam_kayip", 0.0)),
                 "sheaf": float(zirh.get("sheaf_uyumsuzluk", 0.0)),
                 "betti_delik": float(zirh.get("betti_delik_sayisi", 0.0)),
                 "kohomoloji_hata": float(
                     zirh.get("kohomoloji_tikaniklik", 0.0)),
                 "homotopi": float(zirh.get("homotopi_burulma", 0.0)),
                 "bgcm_mizan": float(mizan), "sta_surusu": float(surus),
                 "hdtf_kesme": float(durum.get("kesme", 0.0))}
        self.seyir.append(kayit)
        return kayit

    def kaydet(self, cikti_yolu: str, netice: Dict[str, object]) -> None:
        """Ağırlıkları ``.npy``, telemetriyi ``.olcum.json`` olarak mühürle."""
        dizin = os.path.dirname(cikti_yolu)
        if dizin:
            os.makedirs(dizin, exist_ok=True)
        np.save(cikti_yolu + ".parametre.npy",
                self.meleke_manifoldu.parametreler_vektoru())
        telemetri = {k: v for k, v in netice.items()
                     if k not in ("p", "agirliklar")}
        with open(cikti_yolu + ".olcum.json", "w", encoding="utf-8") as f:
            json.dump(telemetri, f, ensure_ascii=False, indent=2,
                      default=float)
        print("  [MÜHÜR] Parametre ve ölçümler kaydedildi: %s.{parametre.npy,"
              "olcum.json}" % cikti_yolu, flush=True)


def dalga_talimi_kos(ayar: EgitimAyari = KISA_CPU,
                     kume: str = "training") -> Dict[str, object]:
    """Şemanın dalga hattını koştur ve telemetrisini döndür."""
    motor = KulliDalgaTalimMotoru(ayar)
    hepsi = gorevleri_getir(kume)
    egitim_gorevleri, _dog = gorevleri_getir(ne="böl", gorevler=
        hepsi, dogrulama=int(ayar.dogrulama_sayisi), tohum=ayar.tohum)
    durum = motor.veri_durumu_hazirla(
        list(egitim_gorevleri)[:int(ayar.gorev)])
    t0 = time.perf_counter()
    for c in range(int(ayar.cevrim)):
        n = motor.talim_adimi_icra_et(durum)
        print("  [ÇEVRİM %02d/%02d] %.4f sn | zırh %.6f | sheaf %.4f | "
              "betti %.0f | koho %.4f | mizan %.6f"
              % (c + 1, ayar.cevrim, n["adim_suresi_sn"],
                 n["topolojik_kayip"], n["sheaf"], n["betti_delik"],
                 n["kohomoloji_hata"], n["bgcm_mizan"]), flush=True)
    ilk = motor.seyir[0] if motor.seyir else {}
    son = motor.seyir[-1] if motor.seyir else {}
    return {"motor": motor, "ayar": ayar.ad,
            "parca": durum["parca"], "hdtf_kademe": durum["kademe"],
            "hdtf_kesme": durum["kesme"],
            "V_ilk": float(ilk.get("topolojik_kayip", 0.0)),
            "V_son": float(son.get("topolojik_kayip", 0.0)),
            "toplam_sure_sn": time.perf_counter() - t0,
            "seyir": motor.seyir}


# =====================================================================
#  3. HAT -- GÖREV TÂLİMİ (ARC'de fiilen çözen hat)
# =====================================================================
def gorev_talimi(gorev, devir: int = 120):
    """Tek görevin şahitlerinden o göreve mahsus dalgayı çıkar."""
    from main.cikarim import dalga_kur
    cift = [(np.asarray(a, int), np.asarray(b, int))
            for a, b in getattr(gorev, "egitim", [])]
    return dalga_kur(cift, devir=int(devir))



# =====================================================================
#  TEK HAT -- dört hattın terkibi (kütük H230)
# =====================================================================
def _bol(P, n_teta: int):
    """Müşterek vektörü iki yüze ayır: ``θ`` (dönme) ve ``p`` (kapı)."""
    P = np.asarray(P, float).reshape(-1)
    return P[:n_teta], P[n_teta:]


def tek_hattin_kaybi(P, motor, nefs, veri, ayar, kademe_gorevleri,
                     ne: str = "kayıp"):
    """DÖRT HATTIN TEK KAYBI -- **terkip** (kütük H230).

    Dört hattı birleştirmenin önündeki asıl engel isim yahut dosya
    değildi; **iki ayrı parametre taşıyıcısıydı**:

    ==============  ==================  ==========================
    hat             taşıyıcı            ne öğreniyordu
    ==============  ==================  ==========================
    HAT 1 (dalga)   ``KulliMelekeManifoldu.teta``  44 sayı: her
                                        melekenin ``so(D)`` dönme
                                        açısı -- meleke NE KADAR
                                        döner
    HAT 2 (küllî)   ``QNefs.p``         272 sayı: her melekenin MPS
                                        kapısı -- meleke NE YAPAR
    ==============  ==================  ==========================

    İkisi **aynı 44 melekenin iki yüzüdür** ve birbirini hiç
    görmüyordu: dalga hattı θ'yı eğitiyor, küllî hat p'yi eğitiyor,
    ne biri ötekinin neticesini okuyor ne de ortak bir mîzâna
    giriyorlardı. Terkip budur: **tek vektör ``[θ | p]``, tek kayıp,
    tek hoca.**

    Kayıp iki yüzü **zayıf halkaya göre** birleştirir, düz toplamla
    değil::

        L = yumuşak_asgarî_tersi(ℓ_zırh, ℓ_küllî)

    Sebep proje kaidesidir: zincir en zayıf halkası kadardır. Düz
    toplam, zırhı temiz bir dalgayı küllî kaybı berbat iken aklardı;
    yumuşak âzamî **en kötü yüzü** öne çıkarır. (Aynı usul zırhın
    kendi beş süzgecinde de kullanılıyor.)

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``kayıp``       tek sayı -- hocanın gördüğü
    ``döküm``       iki yüz ayrı ayrı; hangisi zayıf halka
    ==============  ==================================================
    """
    from nefs.kulli_kayip import kulli_kayip, zayif_halka
    from nefs.zirh import zirhla

    teta, pp = _bol(P, int(np.asarray(motor.meleke_manifoldu.teta).size))

    # --- YÜZ 1: dönme yüzü (HAT 1'in cevheri) ---------------------
    mm = motor.meleke_manifoldu
    eski = np.array(mm.teta, float).copy()
    mm.teta = np.asarray(teta, float).copy()
    try:
        H = mm.hamiltonyen_uret()
        _, z = zirhla(H)
        l_zirh = float(z.get("toplam_kayip", 0.0))
    finally:
        mm.teta = eski                      # kayıp saf olmalı: yan tesir yok

    # --- YÜZ 2: kapı yüzü (HAT 2'nin cevheri) ---------------------
    t = kulli_kayip(nefs, veri, np.asarray(pp, float), ayar.sozluk,
                    kademe_gorevleri=kademe_gorevleri)
    l_kulli = float(t["kayıp"])

    # --- ZAYIF HALKA: en kötü yüz hükmü verir --------------------
    # Yumuşak ÂZAMÎ, aynı çekirdekle: ``max(x) = −min(−x)``. Kapı
    # ``asgarî`` kipinde yumuşak asgarîdir; işareti çevirmek onu tam
    # olarak yumuşak âzamî yapar -- ikinci bir çekirdek yazılmaz.
    # (``ne="azamî"`` kipi ``Olcu`` nesneleri içindir, düz sayı için
    # değil.)
    L = -float(zayif_halka([-l_zirh, -l_kulli], beta=8.0, ne="asgarî"))
    if ne == "kayıp":
        return L
    if ne != "döküm":
        raise ValueError("tek hat kaybının kipi bilinmiyor: %r" % (ne,))
    return {"kayıp": L, "zırh": l_zirh, "küllî": l_kulli,
            "zayıf_halka": ("zırh" if l_zirh >= l_kulli else "küllî"),
            "θ": int(teta.size), "p": int(np.asarray(pp).size)}


def dimag(gorevler=None, tur: int = 2, n_gorev: int = 24,
          tohum: int = 0, ayar: Optional[EgitimAyari] = None,
          egit: bool = True, ne: str = "kos", **opt_kw):
    """KÜLLÎ DİMAĞ -- **dört hat tek hatta terkip** (kütük H230).

    Evvelce dört ayrı hat vardı ve hiçbiri ötekinin neticesini
    okumuyordu::

        HAT 1  dalga_talimi_kos      θ'yı eğitir      (öğrenmiyordu -- H229)
        HAT 2  kulli_kayip_talimi    p'yi eğitir      (θ'yı görmez)
        HAT 3  idrak.cozucu          ispatla çözer    (ikisini de görmez)
        HAT 4  nazırlık zinciri      gor→dusun→söyle  (ogren'i çağırmıyordu)

    Terkipte tek hat kalır ve dört cevher yerini bulur::

        manzara = gor(gorev)              # görmek
        hal     = dusun(manzara)          # 44 meleke + dörtlü zırh
        mizan   = tart(hal)               # zayıf halka + sözleşme
        ogren(tek_hattin_kaybi, [θ|p])    # HAT 1 + HAT 2, TEK vektör
        cevap   = soyle(gorev, nefs=nefs) # HAT 3 -- MOTOR üretir

    **Öğrenilen ile söylenen nasıl bağlanır.** Bu, hattın en ince
    yeridir ve kaidesi şudur: **ispat öğrenmeyi ezer.** Çözücü aday
    dönüşümleri gösterim çiftlerinde doğrular; tutan tek aday varsa
    öğrenilenin söyleyecek sözü yoktur -- ispat kesindir. Fakat
    **birden çok aday tutuyorsa** "ilkini al" keyfîdir, ve keyfî
    olan yerde öğrenilen hüküm verebilir. Ölçüldü (200 eğitim
    görevi): cevap verilen altı görevin **üçünde** birden çok aday
    tutuyor. Köprü işte o üç görevdedir; ötekilerde yoktur ve
    olmaması doğrudur.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``kos``         bütün akış: görülen, düşünülen, tartılan, öğrenilen,
                    söylenen
    ``gor``         yalnız manzaralar
    ``soyle``       yalnız cevaplar (çıkarım hattı; tâlim yok)
    ``kayıp``       tek hattın kaybının dökümü (iki yüz yan yana)
    ==============  ==================================================
    """
    from nefs.gor import gor
    from nefs.dusun import dusun
    from nefs.tart import tart
    from nefs.ogren import ogren
    from nefs.soyle import soyle
    from nefs.melekeler import QNefs
    from nefs.qegitim import ornekler

    a = ayar or KISA_CPU
    if gorevler is None:
        gorevler = gorevleri_getir("training")
    gorevler = list(gorevler)[:int(n_gorev)]

    if ne == "gor":
        return [gor(g) for g in gorevler]
    if ne == "soyle":
        # Motorsuz söylemek yasak: kâide cebri tasfiye edildi.
        nefs = QNefs(a.tohum, a.qayar())
        nefs.idrak_et(np.zeros((2, a.satir_kubiti)))
        return [soyle(g, nefs=nefs) for g in gorevler]

    # --- tek taşıyıcı: iki yüz tek vektörde ----------------------
    motor = KulliDalgaTalimMotoru(a)
    nefs = QNefs(a.tohum, a.qayar())
    nefs.idrak_et(np.zeros((2, a.satir_kubiti)))
    teta0 = np.asarray(motor.meleke_manifoldu.teta, float).reshape(-1)
    p0 = np.asarray(nefs.vektor(), float).reshape(-1)
    P0 = np.concatenate([teta0, p0])
    veri = ornekler(gorevler, azami=a.ornek_sayisi, pencere=a.pencere,
                    sozluk=a.sozluk, tohum=a.tohum)
    kademe = list(gorevler)[:int(a.kademe_gorevi)]

    def kayip(M):
        M = np.atleast_2d(np.asarray(M, float))
        return np.array([tek_hattin_kaybi(m, motor, nefs, veri, a, kademe)
                         for m in M])

    if ne == "kayıp":
        return tek_hattin_kaybi(P0, motor, nefs, veri, a, kademe,
                                ne="döküm")
    if ne != "kos":
        raise ValueError("dimağ kipi bilinmiyor: %r" % (ne,))

    ilk = tek_hattin_kaybi(P0, motor, nefs, veri, a, kademe, ne="döküm")
    P = P0
    talim = None
    if egit and veri:
        # Müşterek kaybın bedeli ÖLÇÜLDÜ: tek çağrı 30,8 sn, bunun
        # 25,8'i kademe görevlerinden geliyor (``kademe_gorevi=2``).
        # Bütçe çağırana bırakılır; gizlice kısılmaz.
        talim = ogren(kayip, P0, tur=int(tur), tunel=True, **opt_kw)
        P = np.asarray(talim["p"], float).reshape(-1)
    son = tek_hattin_kaybi(P, motor, nefs, veri, a, kademe, ne="döküm")

    # --- HANGİ YÜZ KIPIRDADI -- ve niçin.
    #
    #     Müşterek vektör kurmak yetmez; hangi yüze fiilen dokunulduğu
    #     ÖLÇÜLMELİDİR, yoksa "birleştirdim" demek tabeladır.
    #
    #     Fakat tek yüzün kıpırdaması körlük DEĞİLDİR: kayıp zayıf
    #     halkaya göre kurulduğu için hoca bütçesini **en kötü yüze**
    #     harcar ve öteki yüzü oynatmak L'yi düşürmez. Ölçüldü:
    #     hoca 316 eksenin HEPSİNİ yokluyor (sayıldı), fakat yalnız
    #     zayıf halkadakiler kabul ediliyor. İki yüz de sırası gelince
    #     kıpırdar -- zayıf halka el değiştirince.
    #     (Bunun kırmızısı da ölçüldü: eksen kesme kusuru varken
    #     yalnız θ erişilebilirdi ve o zaman θ 1,25 oynayıp zırh
    #     %97 düşmüştü. Yâni iki yüz de oynatılabilir.)
    teta, pp = _bol(P, teta0.size)
    d_teta = float(np.linalg.norm(np.asarray(teta, float) - teta0))
    d_p = float(np.linalg.norm(np.asarray(pp, float) - p0))

    # --- öğrenileni yazmaca yükle: söylenen artık onu görebilsin --
    motor.meleke_manifoldu.teta = np.asarray(teta, float).copy()
    # ``except pass`` KALDIRILDI (ferman). Burası tâlimin öğrendiğini
    # yazmaca **yükleyen** satırdı; düşerse söylenen eski parametreyi
    # görürdü ve netice "öğrenmedi" diye okunurdu. Sessizce geçilecek
    # bir yer değil, hattın can damarıdır.
    assert hasattr(nefs.p, "vektorden"), (
        "parametre taşıyıcısında ``vektorden`` yok: %r" % type(nefs.p))
    nefs.p.vektorden(np.asarray(pp, float))

    manzaralar, mizanlar, cevaplar = [], [], []
    for g in gorevler:
        manzara = gor(g)
        hal = dusun(manzara, nefs=nefs)
        mizanlar.append(tart(hal, sozlesme=False))
        cevaplar.append(soyle(g, manzara=manzara, nefs=nefs,
                              sozluk=a.sozluk))
        manzaralar.append(manzara)

    konusan = [c for c in cevaplar if not c.sukut]
    return {
        "görev": len(gorevler),
        "parametre": int(P0.size), "θ": int(teta0.size), "p": int(p0.size),
        "V_ilk": ilk["kayıp"], "V_son": son["kayıp"],
        "kazanç": ilk["kayıp"] - son["kayıp"],
        "ilk_döküm": ilk, "son_döküm": son,
        "kayıp_çağrısı": int((talim or {}).get("kayıp_çağrısı", 0)),
        "Δθ": d_teta, "Δp": d_p,
        "iki_yüze_de_dokundu": bool(d_teta > 1e-12 and d_p > 1e-12),
        "kalıbı_bilinen": sum(1 for m in manzaralar if not m.sukut),
        "konuşan": len(konusan), "susan": len(cevaplar) - len(konusan),
        "ortalama_kayıp": (float(np.mean([m.kayip for m in mizanlar]))
                           if mizanlar else 0.0),
        "manzara": manzaralar, "mizan": mizanlar, "cevap": cevaplar,
    }


def dimag_raporu(n_gorev: int = 24, tur: int = 2,
                 **kw) -> str:              # pragma: no cover
    """Tek hattın ölçümü -- dört cevher de ısırıyor mu?"""
    d = dimag(n_gorev=n_gorev, tur=tur, **kw)
    s = ["=== TEK HAT: dört hattın terkibi ===", ""]
    s.append("  parametre         : %d  (θ=%d dönme + p=%d kapı)"
             % (d["parametre"], d["θ"], d["p"]))
    s.append("  görev             : %d" % d["görev"])
    s.append("")
    s.append("  KAYIP (zayıf halkaya göre)")
    for ad, k in (("ilk", d["ilk_döküm"]), ("son", d["son_döküm"])):
        s.append("    %-4s L=%.6f  |  zırh=%.6f  küllî=%.6f  zayıf halka: %s"
                 % (ad, k["kayıp"], k["zırh"], k["küllî"], k["zayıf_halka"]))
    s.append("    kazanç %.6f   kayıp çağrısı %d"
             % (d["kazanç"], d["kayıp_çağrısı"]))
    s.append("    ‖Δθ‖=%.6f  ‖Δp‖=%.6f   (hoca zayıf halkaya harcar:"
             " %s)" % (d["Δθ"], d["Δp"], d["son_döküm"]["zayıf_halka"]))
    s.append("")
    s.append("  NAZIRLIK ZİNCİRİ")
    s.append("    kalıbı bilinen  : %d  (gor)" % d["kalıbı_bilinen"])
    s.append("    konuşan         : %d  (soyle -- ispatla)" % d["konuşan"])
    s.append("    susan           : %d  (H10)" % d["susan"])
    s.append("    ortalama mîzân  : %.6f  (tart)" % d["ortalama_kayıp"])
    return "\n".join(s)


# =====================================================================
def kos(ayar_adi: str = "kısa", cikti: Optional[str] = None,
        kulli_kayip_ile: bool = True) -> str:
    """Her iki tâlim hattını da koştur ve **ikisini yan yana** raporla."""
    ayar = PROFILLER.get(ayar_adi, KISA_CPU)
    ip = tek_iplik_zorla()
    print("=== KÜLLÎ DİMAĞ TÂLİMİ (%s) ===" % ayar.ad, flush=True)
    print("  [BLAS] tek iplik: %s (geç mi: %s)"
          % (ip["değişken"], ip["geç"]), flush=True)

    print("", flush=True)
    print("--- 1. HAT: ŞEMA DALGASI (HDTF + Ĥ_Dimağ + QSVT + STA + FCT) ---",
          flush=True)
    dalga = dalga_talimi_kos(ayar)

    kulli: Optional[Dict[str, object]] = None
    if kulli_kayip_ile:
        print("", flush=True)
        print("--- 2. HAT: KÜLLÎ KAYIP TÂLİMİ (41 meleke + Talim) ---",
              flush=True)
        # ``except`` KALDIRILDI (ferman). Evvelce bu hat düşerse
        # bir satır basılıp koşu devam ediyordu: yâni tâlimin ASIL
        # hattı çökmüşken netice yine de basılıyordu. Bir hattın
        # çöküşünü rapora "başarı" diye yazdıran şey buydu.
        kulli = kulli_kayip_talimi(ayar)
        assert kulli and kulli.get("hazine"), (
            "küllî kayıp hattı BOŞ döndü -- hazineye bir şey yazılmadı")

    if cikti:
        netice = dict(dalga)
        netice.pop("motor", None)
        if kulli:
            netice["kulli_kayip"] = {
                k: v for k, v in kulli.items() if k != "p"}
        dalga["motor"].kaydet(cikti, netice)

    s = ["", "=== TÂLİM NETİCESİ (%s) ===" % ayar.ad, "",
         "  1. HAT -- ŞEMA DALGASI",
         "    veri parçası   : %d" % dalga["parca"],
         "    HDTF kademe    : %d" % dalga["hdtf_kademe"],
         "    HDTF kesme     : %.4e  (χ=%d'de kayıp -- saklanmıyor)"
         % (dalga["hdtf_kesme"], ayar.bag),
         "    zırh kaybı     : %.6f → %.6f"
         % (dalga["V_ilk"], dalga["V_son"]),
         "    süre           : %.2f sn" % dalga["toplam_sure_sn"]]
    if dalga["V_ilk"] == dalga["V_son"]:
        s.append("    ⚠ KAYIP HİÇ KIPIRDAMADI: bu hat şu anda ÖĞRENMİYOR.")
    if kulli:
        d = kulli["değerlendirme"]
        s += ["", "  2. HAT -- KÜLLÎ KAYIP TÂLİMİ",
              "    parametre      : %d" % kulli["parametre"],
              "    veri örneği    : %d" % kulli["veri"],
              "    kayıp çağrısı  : %d" % kulli["kayıp_çağrısı"],
              "    V_ilk → V_son  : %.4f → %.4f  (fark %.4f)"
              % (kulli["V_ilk"], kulli["V_son"],
                 kulli["V_ilk"] - kulli["V_son"]),
              "    süre           : %.1f sn" % kulli["süre_sn"],
              "", "    İKİ ÖLÇÜT BERABER (H47):",
              "      tam çözülen          : %d / %d"
              % (d["tam_çözülen"], d["deneme"]),
              "      ortalama hücre isabeti: %.4f"
              % d["ortalama_hücre_isabeti"],
              "      sükût                 : %d" % d["sükût"]]
        m = kulli["mizan"]
        s += ["", "    MÎZÂN-I KÜLLÎ (nefs/kulli_mizan.py) -- DÖRT KEFE:",
              "      ℒ_Rezonans (Uhlmann) : %.6f" % m["rezonans"],
              "      ℒ_Çevrim   (Wilson)  : %.6f   "
              "(meşru %d / kısır %d / tenakuz %d)"
              % (m["çevrim"], m["meşru"], m["kısır"], m["tenakuz"]),
              "      ℒ_Monogami (CKW)     : %.6f   ihlâl: %d"
              % (m["monogami"], m["ihlâl"]),
              "      ℒ_Hodge    (Δ|Ψ⟩=0)  : %.6f" % m["hodge"],
              "      ─────────────────────────────────",
              "      ℒ_Küllî              : %.6f" % m["kayıp"],
              "      rüşt α               : %.4f   (0=bebeklik → "
              "fıtrat terbiye; 1=rüşt → hafızaya fatura)" % kulli["rüşt"],
              "",
              "    VERİ KENDİNİ DÖRDE AYIRDI MI? (etiketsiz, zabıt V):",
              "      hakikat %d | tenakuz %d | şüpheli %d | gürültü %d"
              % (kulli["veri_cetveli"]["hakikat"],
                 kulli["veri_cetveli"]["tenakuz"],
                 kulli["veri_cetveli"]["şüpheli"],
                 kulli["veri_cetveli"]["gürültü"]),
              "",
              "    KUANTUM ASOSİYATİF HAFIZA (nefs/hafiza.py):",
              "      kayıt %d | tasdik %d | tevakkuf %d | cerh %d | "
              "Zeno budaması %d"
              % (kulli["hafıza"]["kayıt"], kulli["hafıza"]["tasdik"],
                 kulli["hafıza"]["tevakkuf"], kulli["hafıza"]["cerh"],
                 kulli["hafıza"]["budama"])]
        ders = kulli["ders"]
        s += ["",
              "    ÖĞRENİYOR MU (ogrenme/izgara.py, düzenli uydurma):",
              "      eğim      : %+.6f   %s" % (
                  ders["eğim"],
                  "DÜŞÜYOR" if ders["öğreniyor"] else "⚠ ÖĞRENMİYOR"),
              "      bağıntı   : %+.4f   (sabit eğride tam 0)"
              % ders["bağıntı"],
              "      artık     : %.6f  bükülme: %.6f"
              % (ders["artık"], ders["bükülme"]),
              "",
              "    HAZİNE (main/hazine.py -- safetensors):",
              "      %s  (%d bayt, sha256 %s…)"
              % (kulli["hazine"]["yol"], kulli["hazine"]["bayt"],
                 kulli["hazine"]["sha256"][:16]),
              "",
              "    GEÇİT (nefs/akit.py + nefs/illet.py):",
              "      akit uydu : %s   vekil meleke: %d   yazmayan: %d"
              % (kulli["geçit"]["akit_uydu"],
                 kulli["geçit"]["vekil_meleke"],
                 kulli["geçit"]["yazmayan_meleke"]),
              "      zaman çizgesi: %d düğüm, %d çevrim   kelam ayrıştı: %s"
              % (kulli["geçit"]["zaman_düğümü"],
                 len(kulli["geçit"]["zaman_çevrimi"]),
                 kulli["geçit"]["kelam_ayrıştı"])]
        if kulli.get("düşen_uzuv"):
            s.append("    DÜŞEN UZUV: %s"
                     % ", ".join(sorted(kulli["düşen_uzuv"])))
    s += ["", "  HAD: ARC'de fiilen çözen hat bu ikisi DEĞİL, üçüncüsüdür:",
          "  `gorev_talimi` (bkz. main/cikarim.py). İkisinin ARC çözümüne",
          "  katkısı ÖLÇÜLMEMİŞTİR ve ölçülmüş gibi gösterilmiyor."]
    return "\n".join(s)


#: ``taht`` kipleri. Padişahın **tek** girişi budur; yanında ikinci bir
#: ``__main__`` bırakmak paralel devlettir. KÜME 9'a kadar dört ayrı taht
#: vardı (``main.egitim``, ``main.cikarim``, ``main.kaggle_egitim``,
#: ``main.kaggle_cikarim``) ve ``tanilama/nizam.py:GIRISLER`` dördünü de
#: "giriş" sayıyordu; bu, o dört ağaçtan erişilen her şeyi **sessizce**
#: tebaa gösteriyor, yetimliği ölçüden gizliyordu.
KIPLER: Tuple[str, ...] = ("tâlim", "mizan", "sabit", "kaggle", "teftiş",
                           "veri")


def taht(ne: str = "tâlim", *arg: str) -> str:
    """Tek hâkimin tek kapısı: bütün icra buradan dağıtılır.

    ``ne`` kipi:

    * ``"tâlim"``  -- ``kos``: iki hattın tek hatta terkibi (H230).
    * ``"sabit"``  -- ``tanilama/sabit_teftisi.py``: elle tayin edilmiş
      bütün sabitlerin listesi. Hangisi ayara bağlı, hangisi koda gömülü,
      hangisi hiç okunmuyor -- ``ast`` ile çıkarılır.
    * ``"mizan"``  -- ``nefs/kulli_mizan.py``: hata fonksiyonunun kendisi.
      Dört kefe (Rezonans, Çevrim, Monogami, Hodge) ayrı ayrı ölçülür ve
      verinin etiketsiz dört kampa ayrılması gösterilir. **Kök budur.**
    * ``"kaggle"`` -- ``main/kaggle_egitim.py`` + ``main/kaggle_cikarim.py``.
      Bunlar ayrı birer taht DEĞİL, tahtın koşum kipidir.
    * ``"veri"``   -- ``main/veri.py``: belirteçleri 500 MB'lık,
      64 bayta hizalı, mmap'lenebilir parçalara dizer ve Kaggle'a
      umumi veri kümesi olarak gönderir. Hem Kaggle'da hem burada.
    * ``"teftiş"`` -- ``tanilama/divan.py``: dimağı **muayene eden**
      hekim. Hekim uzuv değildir; ama yetim de değildir -- padişah onu
      çağırır, o padişahı değil.

    Buradaki hiçbir dal yeni matematik yazmaz; hepsi mevcut uzuvların
    çağrısıdır. Yeni bir formül yazarsa bu kapı nazırlık olmaktan çıkar,
    çip olur.
    """
    ne = str(ne)
    if ne == "kaggle":
        from main.kaggle_egitim import kaggle_talimini_baslat
        from main.kaggle_cikarim import kaggle_teslimat_dosyasi_uret
        from ogrenme.kaggle_donanim import ayar_sec
        veri = arg[0] if arg else "/kaggle/input"
        # Profil elle yazılmaz: **donanımdan okunur.** ``ayar_sec``
        # bu oturuma kadar hiçbir yerden çağrılmıyordu (yetim ölçüldü),
        # dolayısıyla 84 GB'lık makinede de "kısa" profil koşuyordu.
        prof = ayar_sec()
        t = kaggle_talimini_baslat(veri)
        return ("=== KAGGLE KİPİ ===\n  donanım profili: %r\n"
                "  tâlim: %r\n  teslimat: %s"
                % (prof, t, kaggle_teslimat_dosyasi_uret.__name__))
    if ne == "sabit":
        # **ELLE TAYİN EDİLEN HER SABİT GÖRÜNÜR OLMALI.** Padişahın
        # hükmü: *"elle tayin ettiğin tüm sabit değişkenleri mutlaka bir
        # fonksiyona bağlamak ya da değerini değiştirmek üzere evvela
        # bana liste halinde sunmak."* Bu kip o listeyi koddan **ast**
        # ile çıkarır; hafızadan yazılmaz, dolayısıyla eksik olamaz.
        from tanilama.sabit_teftisi import rapor as sabit_raporu
        return sabit_raporu(*(arg[:1] or ()))
    if ne == "mizan":
        # Mîzân-ı Küllî'yi **tâlim koşturmadan** ölç: dört kefe ayrı ayrı,
        # ve verinin kendini dörde ayırması (hakikat/tenakuz/şüpheli/
        # gürültü). Kök burasıdır; kök tutmadan ağacı büyütmenin manası
        # yoktur.
        from nefs.kulli_mizan import rapor as mizan_raporu
        return mizan_raporu(arg[0] if arg else "kısa")
    if ne == "veri":
        # Veri dönüştürücü: hem Kaggle hem burası. Ayrı bir taht
        # değil, tahtın kipi.
        from main.veri import rapor as veri_raporu
        return veri_raporu(*(arg[:1] or ("training",)))
    if ne == "teftiş":
        from tanilama.divan import rapor as divan_raporu
        return divan_raporu(kos=bool(arg and arg[0] == "koş"))
    if ne == "tâlim":
        ad = arg[0] if arg else "kısa"
        yol = arg[1] if len(arg) > 1 else "depo/kulli_dimag_talim"
        return kos(ad, yol)
    raise ValueError("bilinmeyen kip %r; kipler: %s" % (ne, ", ".join(KIPLER)))


if __name__ == "__main__":                               # pragma: no cover
    if len(sys.argv) > 1 and sys.argv[1] in KIPLER:
        print(taht(sys.argv[1], *sys.argv[2:]))
    else:
        print(taht("tâlim", *sys.argv[1:]))
