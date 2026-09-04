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
from kuantum.yazmac import hiyerarsik_ikili_agac_katlama  # noqa: E402
from ogrenme.optimize import (qsvt_gibbs_sogutma,        # noqa: E402
                          statik_faz_tablosu_oku)
from nefs.musahede import IzafiMevki2D, tiktoken_2d_kodla   # noqa: E402
from nefs.melekeler import melekeleri_kur                # noqa: E402
from ogrenme.optimize import OptimizeAyari               # noqa: E402
from ogrenme.optimize import hoca_egit                   # noqa: E402
from ogrenme.optimize import (chebyshev_tasarimi,        # noqa: E402
                              kestirmeden_sur)
from nefs.zirh import zirh_giydir                        # noqa: E402

__all__ = ["EgitimAyari", "KISA_CPU", "ORTA", "AZAMI_KAGGLE",
           "tek_iplik_zorla", "KulliDalgaTalimMotoru",
           "kulli_kayip_talimi", "gorev_talimi", "kos"]


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
    satir_kubiti: int = 4
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
        return QAyar(satir_kubiti=self.satir_kubiti,
                     yerel_kubit=self.yerel_kubit, bag=self.bag,
                     mera_kademe=self.mera_kademe, tohum=self.tohum)


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
KISA_CPU = EgitimAyari(ad="kısa-CPU", ornek_sayisi=4, cevrim=1,
                       ornek=3, zincir=2, talim_tur=1,
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
    """İşçi de **aynı** kaybı hesaplar; ayrı kayıp mukayeseyi bozardı."""
    from nefs.kulli_kayip import kulli_kayip
    a: EgitimAyari = _ISCI["ayar"]        # type: ignore[assignment]
    t = kulli_kayip(_ISCI["nefs"], _ISCI["veri"], p,   # type: ignore
                    a.sozluk, kademe_gorevleri=_ISCI.get("kademe"))
    return float(t["kayıp"])


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
    from nefs.kulli_kayip import kulli_kayip
    from nefs.melekeler import QNefs
    from nefs.qegitim import degerlendir, ornekler

    t0 = time.perf_counter()
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

    def kayip_p(P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, float))
        if havuz is not None:
            return np.array(list(havuz.map(_isci_kayip, list(P))))
        out = np.empty(P.shape[0], float)
        for i, p in enumerate(P):
            t = kulli_kayip(nefs, veri, p, ayar.sozluk,
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
    nefs.yukle(p_yildiz)
    deg = degerlendir(nefs, dogrulama, azami=ayar.degerlendirme_gorevi,
                      pencere=ayar.pencere, sozluk=ayar.sozluk,
                      azami_uret=ayar.azami_uret)
    return {"ayar": ayar.ad, "parametre": d,
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

        cek, kesme, kademe = hiyerarsik_ikili_agac_katlama(
            vektorler, bag_boyutu=self.ayar.bag,
            sanal_kubit=self.ayar.sanal_kubit_sayisi)
        sure = time.perf_counter() - t0
        print("  [HDTF] %d veri parçası %.3f sn'de QTT'ye katlandı "
              "(kademe %d, kesme %.4e)."
              % (len(vektorler), sure, kademe, kesme), flush=True)
        return {"cekirdek": cek, "kesme": float(kesme),
                "kademe": int(kademe), "süre_sn": sure,
                "parca": len(vektorler)}

    def talim_adimi_icra_et(self, durum: Dict[str, object]
                            ) -> Dict[str, float]:
        """Bab III, IV, V, VI gereğince tek makro QSVT dalga adımı."""
        t0 = time.perf_counter()
        H_dimag = self.meleke_manifoldu.hamiltonyen_uret()
        H_zirhli, zirh = zirh_giydir(H_dimag)
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
        try:
            kulli = kulli_kayip_talimi(ayar)
        except Exception as exc:                         # noqa: BLE001
            print("  [DÜŞTÜ] küllî kayıp hattı: %s: %s"
                  % (type(exc).__name__, str(exc)[:120]), flush=True)

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
        if kulli.get("düşen_uzuv"):
            s.append("    DÜŞEN UZUV: %s"
                     % ", ".join(sorted(kulli["düşen_uzuv"])))
    s += ["", "  HAD: ARC'de fiilen çözen hat bu ikisi DEĞİL, üçüncüsüdür:",
          "  `gorev_talimi` (bkz. main/cikarim.py). İkisinin ARC çözümüne",
          "  katkısı ÖLÇÜLMEMİŞTİR ve ölçülmüş gibi gösterilmiyor."]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    ad = sys.argv[1] if len(sys.argv) > 1 else "kısa"
    yol = sys.argv[2] if len(sys.argv) > 2 else "depo/kulli_dimag_talim"
    print(kos(ad, yol))
