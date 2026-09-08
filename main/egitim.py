from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import json
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

from nefs.musahede import gorevleri_getir
from ogrenme.optimize import OptimizeAyari
from ogrenme.optimize import hoca_egit, optimize_beyani
from main import hazine
from nefs.kulli_mizan import (MizanAyari, kulli_mizan,
                              mizan_cetveli)
from nefs.hafiza import Hafiza
from main.cikarim import (hazineden_yukle, hafizayi_yukle, padisah,
                          hazineden_devam, devam_agirligi)
from nefs.galois import (GaloisAyari, tableau_kur,
                         sbox_bukme, sbox_olcu, palmer_olcu)
from nefs.tdd import TddAyari, kanonik_adres
from nefs.matchgate import MatchgateAyari, flo_evrimi
from nefs.ayna import AynaAyari
from nefs.mihenk import MIHENK, nobet_kur
from nefs.faz_polinomu import FazAyari, faz_oturt
from nefs.siklotomik import (SiklotomikAyari,
                             koset_indirge, iz_esitligi)
from nefs.qcekirdek import cekirdek_beyani
from tanilama.hizolcer import (Hizolcer, hizolcer_bagla,
                               hizolcer_beyani)
from nefs.gpu_akis import GpuAyari, gpu_akisi
from nefs.kararname import kararname
from nefs.golge import (GolgeAyari, golge_al,
                        kestir)
from nefs.sadakat import (SadakatAyari, sadakat_uygula,
                          sadakat_beyani)
from nefs.olcek import Kok, olcek, denge, olcek_beyani
from nefs.belirtec import (belirtec_kapisi, belirtec_sozlugu,
                           belirtec_beyani)
from nefs.keyfiyet import (KeyfiyetAyari, keyfiyet,
                           keyfiyet_beyani)
from nefs.munasebet import (MunasebetAyari, munasebet_kos,
                            munasebet_beyani)
from main.kulliyat import (kulliyat_verisi,
                           kulliyat_dokumu, kulliyat_beyani)
from nefs.mukayese import (hata_payi, kiplik, mukayese_beyani,
                           vecih_kur)
from nefs.usul import usul_beyani
from nefs.suphe import suphe_beyani
from tanilama.beyan import (talim_beyani,
                            kaggle_beyani, sifir_beyani)

HAZINE_DIZINI = os.environ.get("MUCIT_HAZINE", "depo/hazine")

HAZINE_ADI = "dimag"


def hazineden_hiz(dizin: Optional[str] = None) -> float:
    from main import hazine as _h
    y = hazine_yolu(dizin) + _h.UZANTI
    if not os.path.isfile(y):
        return 0.0
    try:
        ust = _h.ust_coz(_h.beyan(y).get("__metadata__", {}) or {})
    except Exception as e:
        raise AssertionError(
            "hazine üst verisi okunamadı (%s): hız ölçüsü sessizce "
            "yoklanamaz -- ferman 5" % e)
    return float(ust.get("ölçülen_hız", 0.0) or 0.0)


def hazine_yolu(dizin: Optional[str] = None) -> str:
    return os.path.join(dizin or HAZINE_DIZINI, HAZINE_ADI)


def hazine_sifirla(dizin: Optional[str] = None) -> Dict[str, object]:
    from main import hazine as _h
    y = hazine_yolu(dizin) + _h.UZANTI
    vardi = os.path.isfile(y)
    b = os.path.getsize(y) if vardi else 0
    if vardi:
        os.remove(y)
    return {"yol": y, "vardı": vardi, "bayt": int(b)}

__all__ = ["EgitimAyari", "DAR", "ORTA", "AZAMI",
           "KISA_CPU", "AZAMI_KAGGLE",
           "tek_iplik_zorla", "gecit", "ogreniyor_mu",
           "kulli_kayip_talimi", "muhurle", "kos", "HAZINE_DIZINI"]


def tek_iplik_zorla() -> Dict[str, str]:
    ad = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
          "NUMEXPR_NUM_THREADS")
    for a in ad:
        os.environ[a] = "1"
    return {"değişken": ",".join(ad), "geç": "numpy" in sys.modules}


@dataclass
class EgitimAyari:
    ad: str = "kısa"
    kodlama: str = "o200k_base"
    sozluk: int = 0
    belirtec_basamak: int = 0
    comert: float = 0.5
    tohum: int = 0
    olculen_hiz: float = 0.0

    veri_lifi: int = 0
    hukum_lifi: int = 0
    karo: int = 0
    yerel_yuva: int = 1
    parametre_genisligi: int = 0
    yigin_dilimi: int = 0
    ornek_sayisi: int = 0
    pencere: int = 0
    talim_tur: int = 0
    altuzay_ornek: int = 0
    cevrim_sayisi: int = 0
    cevrim_boyu: int = 3
    degerlendirme_gorevi: int = 0
    dogrulama_sayisi: int = 0
    kademe_gorevi: int = 0
    azami_uret: int = 0
    yaricap: float = 0.0
    blok: int = 0
    azami_talim_saati: float = 0.0
    lam_cevrim: float = 0.0
    lam_monogami: float = 0.0
    lam_tip: float = 0.0
    lam_engel: float = 0.0
    lam_tenakuz: float = 0.0
    lam_kategori: float = 0.0
    lam_nokta: float = 0.0
    lam_meleke: float = 0.0
    lam_zirh: float = 0.0
    lam_kaide: float = 0.0
    lam_tasma: float = 0.0
    mihenk_arasi: float = 300.0
    galois_us: int = 0
    tableau_n: int = 0
    faz_mertebesi: int = 0
    flo_modu: int = 0
    flo_kapisi: int = 0
    siklotomik_us: int = 0
    siklotomik_taban: int = 3
    siklotomik_derece: int = 12
    faz_derecesi: int = 3
    tdd_cekirdek: int = 0
    tdd_tolerans: float = 1e-7
    stab_mertebe: int = 0
    golge_ornegi: int = 0
    golge_haddi: float = 0.05
    gpu_akis_haddi: float = 1000.0
    gpu_genlesmesi: int = 8
    hiz_geciti: int = 1
    canli_saniye: float = 20.0
    hal_kaynagi: str = "tutarlı"
    sadakat_acik: int = 1
    parite_lifi: int = 2
    usul_acik: int = 1
    usul_haddi: float = 0.0
    usul_seferi: int = 0
    keyfiyet_turu: int = 0
    suphe_acik: int = 1
    rust_muayene: int = 1
    sbox_acik: int = 1
    meleke_olcumu: int = 1
    mukayese_acik: int = 1
    hat: str = "c"
    hat_bandi: int = 0
    motor: str = "galois"
    genlik_tipi: str = "complex64"
    rust_t0: float = 0.5
    rust_tau: float = 0.15
    rust_kapanis: float = 0.5
    hafiza_kapasitesi: int = 0
    hafiza_yazma: float = 0.05
    hafiza_sonumu: float = 0.02
    suphe_sonumu: float = 0.05
    zeno_esigi: float = 0.35
    zeno_tepe: float = 0.9
    hafiza_ayniyet: float = 0.98
    hafiza_buhar: float = 1e-4
    tenakuz_eps: float = 1e-5
    dislama_tau: float = 8.0
    ayna_teta: float = 0.2617993877991494
    ayna_r: float = 0.35
    ayna_tur: int = 0
    qudit_qsvt: int = 0
    qudit_derece: int = 0
    qudit_yon: int = 0
    harman_kademesi: int = 0

    def __post_init__(self) -> None:
        if int(self.sozluk) <= 0:
            self.sozluk = int(belirtec_sozlugu(str(self.kodlama)))
        if float(self.olculen_hiz) <= 0.0:
            self.olculen_hiz = float(hazineden_hiz())
        o = olcek(Kok(sozluk=int(self.sozluk), comert=float(self.comert),
                      tohum=int(self.tohum), hiz=float(self.olculen_hiz)))
        self.olcek_dokumu = o
        self.elle = tuple(sorted(
            k for k in o if getattr(self, k, None) not in (0, 0.0, None)))
        for k, v in o.items():
            if getattr(self, k, None) in (0, 0.0):
                setattr(self, k, v)

    olcek_dokumu: Dict[str, object] = field(default_factory=dict)
    elle: Tuple[str, ...] = ()

    @property
    def lif_yapisi(self) -> Tuple[int, ...]:
        return (int(self.veri_lifi), int(self.karo), int(self.karo))

    @property
    def d(self) -> int:
        return int(self.veri_lifi) * int(self.karo) ** 2

    def qayar(self):
        from nefs.zihin_durumu import QAyar
        import numpy as _np
        tip = {"complex64": _np.complex64,
               "complex128": _np.complex128}[str(self.genlik_tipi)]
        return QAyar(veri_lifi=int(self.veri_lifi),
                     yerel_yuva=int(self.yerel_yuva),
                     harman_kademesi=int(self.harman_kademesi),
                     tohum=int(self.tohum),
                     yigin=self.yigin(), tip=tip,
                     motor=str(self.motor),
                     hukum_lifi=int(self.hukum_lifi),
                     lif_yapisi=self.lif_yapisi,
                     faz_mertebesi=int(self.faz_mertebesi),
                     hat=str(self.hat), hat_bandi=int(self.hat_bandi),
                     sadakat_acik=int(self.sadakat_acik),
                     parite_lifi=int(self.parite_lifi),
                     parametre_genisligi=int(self.parametre_genisligi),
                     meleke_olcumu=int(self.meleke_olcumu))

    def yigin(self) -> int:
        return max(1, min(int(self.yigin_dilimi), int(self.ornek_sayisi)))


DAR = EgitimAyari(ad="dar", comert=0.15, hiz_geciti=0)

ORTA = EgitimAyari(ad="orta", comert=0.5)

AZAMI = EgitimAyari(ad="azamî", comert=1.0)

KISA_CPU = DAR
AZAMI_KAGGLE = AZAMI

PROFILLER: Dict[str, EgitimAyari] = {
    "dar": DAR, "kısa": DAR, "kisa": DAR, "orta": ORTA,
    "azamî": AZAMI, "azami": AZAMI}


def gecit(sert: bool = True, hiz_ayari=None) -> Dict[str, object]:
    from nefs.illet import (alan_cizgesi, cevrimler, kelam_ayrismasi,
                            zaman_cizgesi)

    dug, ken, kabul = alan_cizgesi()
    assert dug, "sebep çizgesi BOŞ -- illet ölçüsü bir şey ölçmüyor"
    alan_cevrimi = cevrimler(dug, ken)
    zg, _yer = zaman_cizgesi()
    zaman_cevrimi = cevrimler(list(zg.dugumler), list(zg.kenarlar))
    ayrisma = kelam_ayrismasi()

    o: Dict[str, object] = {
        "alan": len(dug), "kenar": len(ken),
        "alan_çevrimi": len(alan_cevrimi),
        "zaman_düğümü": len(zg.dugumler),
        "zaman_çevrimi": [list(c) for c in zaman_cevrimi],
        "kelam_ayrıştı": bool(ayrisma.get("hüküm_şartıyla_ayrık", False)),
        "kelam_dökümü": ayrisma,
    }
    if hiz_ayari is not None:
        from tanilama.hiz_teftisi import BUTCE_SANIYESI, HAD, olc
        h = olc(hiz_ayari)
        o["belirteç_sn"] = float(h["belirteç_sn"])
        o["hız_haddi"] = float(HAD)
        o["hız_geçti"] = bool(h["belirteç_sn"] >= HAD)
        o["kayıp_süresi"] = float(h["kayıp_süresi"])
        o["en_pahalı_uzuv"] = (h["tek_meleke"][0][0]
                               if h["tek_meleke"] else "?")
        cagri = max(1, int(hiz_ayari.talim_tur)
                    * max(1, int(hiz_ayari.altuzay_ornek)))
        o["kestirilen_saniye"] = float(h["kayıp_süresi"]) * cagri
        o["bütçe_saniyesi"] = float(BUTCE_SANIYESI)
    if sert:
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
    y = np.asarray(list(seyir), float).reshape(-1)
    assert y.size >= 2, "seyir eğrisi için en az iki nokta lâzım"
    assert np.all(np.isfinite(y)), "seyirde NaN/Inf var"
    from ogrenme.izgara import bagintili_olcut, duzenli_uydur

    t = np.linspace(-1.0, 1.0, y.size)
    G = max(2, min(8, y.size // 3))
    k = 3 if y.size > 5 else 1
    u = duzenli_uydur(t, y, G, k, lam=float(lam))
    tahmin = np.asarray(u["B"], float) @ np.asarray(u["c"], float)
    n = max(1, min(y.size - 1, y.size // 4))
    egim = float((tahmin[-1] - tahmin[-1 - n]) / (t[-1] - t[-1 - n]))
    bag = float(bagintili_olcut(t, y))
    return {"eğim": egim, "artık": float(u["artık"]),
            "bükülme": float(u["bükülme"]), "bağıntı": bag,
            "öğreniyor": bool(egim < 0.0 and bag < 0.0),
            "toplam_düşüş": float(y[0] - y[-1])}


def mizan_ayari(a: EgitimAyari) -> "MizanAyari":
    return MizanAyari(
        zeno_tepe=float(a.zeno_tepe), lam_engel=float(a.lam_engel),
        ayna_tur=int(a.ayna_tur), ayna_teta=float(a.ayna_teta),
        ayna_r=float(a.ayna_r),
        lam_cevrim=float(a.lam_cevrim), lam_monogami=float(a.lam_monogami),
        lam_tip=float(a.lam_tip), cevrim_boyu=int(a.cevrim_boyu),
        tdd_cekirdek=int(a.tdd_cekirdek),
        golge_ornegi=int(a.golge_ornegi), golge_haddi=float(a.golge_haddi),
        qsvt=int(a.qudit_qsvt), qudit_derece=int(a.qudit_derece),
        qudit_yon=int(a.qudit_yon),
        cevrim_sayisi=int(a.cevrim_sayisi),
        hal_kaynagi=str(a.hal_kaynagi),
        sadakat_acik=int(a.sadakat_acik), parite_lifi=int(a.parite_lifi),
        lam_tenakuz=float(a.lam_tenakuz), tenakuz_eps=float(a.tenakuz_eps),
        dislama_tau=float(a.dislama_tau),
        lam_kategori=float(a.lam_kategori), lam_nokta=float(a.lam_nokta),
        lam_meleke=float(a.lam_meleke), lam_zirh=float(a.lam_zirh),
        lam_kaide=float(a.lam_kaide),
        lam_tasma=float(a.lam_tasma), basamak=int(a.belirtec_basamak),
        meleke_olcumu=int(a.meleke_olcumu),
        usul_acik=int(a.usul_acik), usul_haddi=float(a.usul_haddi),
        usul_seferi=int(a.usul_seferi),
        suphe_acik=int(a.suphe_acik), suphe_sonumu=float(a.suphe_sonumu),
        rust_t0=float(a.rust_t0),
        rust_tau=float(a.rust_tau), rust_kapanis=float(a.rust_kapanis),
        rust_muayene=int(a.rust_muayene), zeno_esigi=float(a.zeno_esigi),
        toplam_adim=max(1, int(a.talim_tur) * max(1, int(a.altuzay_ornek))),
        tohum=int(a.tohum))


def kulli_kayip_talimi(ayar: EgitimAyari = KISA_CPU,
                       gorevler: Optional[Sequence] = None) -> Dict[str, object]:
    from nefs.kulli_kayip import kademe_parametreleri_ac
    from nefs.melekeler import QNefs
    from nefs.qegitim import degerlendir, ornekler

    t0 = time.perf_counter()
    kapi_bel = belirtec_kapisi(str(ayar.kodlama))
    assert int(kapi_bel.n_vocab) == int(ayar.sozluk), (
        "sözlük ile kodlama tutmuyor: ayar %d, %s %d -- sözlük elle "
        "yazılmış olabilir (ferman 1-N)"
        % (ayar.sozluk, ayar.kodlama, kapi_bel.n_vocab))
    kapi = gecit(sert=bool(int(ayar.hiz_geciti)), hiz_ayari=ayar)
    hepsi = list(gorevler) if gorevler is not None else \
        gorevleri_getir("training")
    egitim_gorevleri, dogrulama = gorevleri_getir(ne="böl", gorevler=
        hepsi, dogrulama=int(ayar.dogrulama_sayisi), tohum=ayar.tohum)
    arc_veri = ornekler(egitim_gorevleri,
                        azami=max(1, int(ayar.ornek_sayisi) // 2),
                        pencere=ayar.pencere, sozluk=ayar.sozluk,
                        tohum=ayar.tohum, taban=int(ayar.veri_lifi),
                        basamak=int(ayar.belirtec_basamak))
    devam = hazineden_devam(hazine_yolu())
    kul_veri, imlec = kulliyat_verisi(
        sozluk=int(ayar.sozluk), pencere=int(ayar.pencere),
        azami=max(0, int(ayar.ornek_sayisi) - len(arc_veri)),
        tohum=int(ayar.tohum), kodlama=str(ayar.kodlama),
        taban=int(ayar.veri_lifi),
        basamak=int(ayar.belirtec_basamak),
        imlec=devam.get("imleç"), ne="imleçli")
    veri = list(arc_veri) + list(kul_veri)
    assert veri, "tâlim verisi BOŞ"

    nefs = QNefs(ayar.tohum, ayar.qayar())
    nefs.idrak_et(np.zeros((2, ayar.veri_lifi)))
    kademe_parametresi = kademe_parametreleri_ac(nefs.p)
    d = len(nefs)
    p0 = devam_agirligi(devam, nefs, d)
    kademe_gorevleri = list(egitim_gorevleri)[:int(ayar.kademe_gorevi)]

    mzn = mizan_ayari(ayar)
    LAM_ADLARI = ("lam_cevrim", "lam_monogami", "lam_tip", "lam_engel",
                  "lam_tenakuz", "lam_kategori", "lam_nokta",
                  "lam_meleke", "lam_zirh", "lam_kaide",
                  "lam_tasma")
    _elle_lam = tuple(a for a in LAM_ADLARI
                      if float(getattr(ayar, a, 0.0)) != 0.0)
    _mzn = {"a": mzn}

    def _dengele(dokum) -> Dict[str, float]:
        _a = dokum.get("artık")
        _n = dokum.get("artık_adı")
        lam = denge(dokum,
                    artik=(list(_a) if _a is not None else None),
                    adlar=(list(_n) if _n is not None else None))
        for ad, deger in lam.items():
            if ad == "frenlenen" or ad in _elle_lam:
                continue
            setattr(ayar, ad, float(deger))
        _mzn["a"] = mizan_ayari(ayar)
        return lam

    ilk_kefeler = kulli_mizan(nefs, veri, p0, ayar.sozluk, ayar=mzn,
                              kademe_gorevleri=kademe_gorevleri,
                              ne="döküm")
    olculen_lam = _dengele(ilk_kefeler)
    mzn = _mzn["a"]
    hafiza = Hafiza(kapasite=int(ayar.hafiza_kapasitesi),
                    yazma=float(ayar.hafiza_yazma),
                    sonum=float(ayar.hafiza_sonumu),
                    zeno_esigi=float(ayar.zeno_esigi),
                    zeno_tepe=float(ayar.zeno_tepe),
                    ayniyet=float(ayar.hafiza_ayniyet),
                    buhar=float(ayar.hafiza_buhar), tohum=int(ayar.tohum))
    _sayac = {"çağrı": 0}
    from tanilama.hiz_teftisi import HAD as _HIZ_HADDI
    olcer = Hizolcer(belirtec_basina=len(veri) * int(ayar.pencere),
                     had=float(_HIZ_HADDI), ad="küllî mizan",
                     canli_saniye=float(ayar.canli_saniye))
    hizolcer_bagla(olcer)

    _kume: Dict[str, Sequence] = {"v": list(veri)}
    _seyir: List[Dict[str, float]] = []
    nobet = nobet_kur(nefs, ara_saniye=float(ayar.mihenk_arasi),
                      pencere=int(ayar.pencere), sozluk=int(ayar.sozluk),
                      taban=int(ayar.veri_lifi),
                      basamak=int(ayar.belirtec_basamak),
                      kodlama=str(ayar.kodlama),
                      azami_uret=int(ayar.azami_uret),
                      ayna=AynaAyari(teta=float(ayar.ayna_teta),
                                     r=float(ayar.ayna_r),
                                     tur=int(ayar.ayna_tur),
                                     tohum=int(ayar.tohum)))

    def kayip_p(P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, float))
        out = np.empty(P.shape[0], float)
        kume = list(_kume["v"])
        for i, p in enumerate(P):
            _sayac["çağrı"] += 1
            with olcer.saat(len(kume) * int(ayar.pencere)):
                t = kulli_mizan(nefs, kume, p, ayar.sozluk, ayar=_mzn["a"],
                                hafiza=hafiza, adim=_sayac["çağrı"],
                                kademe_gorevleri=kademe_gorevleri)
            out[i] = float(t["kayıp"])
            _seyir.append({"V": float(t["kayıp"])})
            nobet.yokla(p, kayip=float(t["kayıp"]),
                        adim=_sayac["çağrı"])
        return out

    def _eniyile(p_, kume):
        o = OptimizeAyari(
            ad=ayar.ad, tur=1, yaricap=float(ayar.yaricap),
            gcl_nokta_sayisi=max(8, int(ayar.altuzay_ornek)),
            yon_sayisi=int(ayar.altuzay_ornek), blok=int(ayar.blok),
            sesli=False, tohum=ayar.tohum)
        o.tunel_acik = True
        o.vekil_acik = False
        n0 = _sayac["çağrı"]
        _kume["v"] = list(kume)
        rr = hoca_egit(kayip_p, np.asarray(p_, float), o)
        return np.asarray(rr["p"], float), _sayac["çağrı"] - n0

    def _olc(p_, kume):
        return kulli_mizan(nefs, list(kume), np.asarray(p_, float),
                           ayar.sozluk, ayar=_mzn["a"], hafiza=hafiza,
                           adim=_sayac["çağrı"],
                           kademe_gorevleri=kademe_gorevleri, ne="döküm")

    mun = munasebet_kos(
        veri, p0, _eniyile, _olc,
        dengele=_dengele,
        ayar=MunasebetAyari(
            acik=1,
            obek=int(ayar.yigin()),
                            azami_tur=int(ayar.keyfiyet_turu),
                            n_v=int(ayar.veri_lifi),
            azami_saniye=float(ayar.azami_talim_saati) * 3600.0),
        keyfiyet_ayari=KeyfiyetAyari(acik=1,
                                     azami_tur=int(ayar.keyfiyet_turu)))
    _kume["v"] = list(veri)
    p_son = np.asarray(mun["p"], float)
    _ilk = kulli_mizan(nefs, veri, p0, ayar.sozluk, ayar=_mzn["a"],
                       hafiza=hafiza, adim=_sayac["çağrı"],
                       kademe_gorevleri=kademe_gorevleri)
    _son = kulli_mizan(nefs, veri, p_son, ayar.sozluk, ayar=_mzn["a"],
                       hafiza=hafiza, adim=_sayac["çağrı"],
                       kademe_gorevleri=kademe_gorevleri)
    mzn = _mzn["a"]
    r = {"p": p_son, "V_ilk": float(_ilk["kayıp"]),
         "V_son": float(_son["kayıp"]),
         "kayıp_çağrısı": int(_sayac["çağrı"]), "seyir": _seyir,
         "günlük": [], "düşen_uzuv": {}}

    p_yildiz = np.asarray(r["p"], float)
    assert p_yildiz.size == d, (
        "tâlim %d parametre aldı, %d döndürdü" % (d, p_yildiz.size))
    assert np.all(np.isfinite(p_yildiz)), "tâlim NaN/Inf parametre döndürdü"
    nefs.yukle(p_yildiz)
    ayna = AynaAyari(teta=float(ayar.ayna_teta), r=float(ayar.ayna_r),
                     tur=int(ayar.ayna_tur), tohum=int(ayar.tohum))
    deg = degerlendir(nefs, dogrulama, azami=ayar.degerlendirme_gorevi,
                      pencere=ayar.pencere, sozluk=ayar.sozluk,
                      azami_uret=ayar.azami_uret, ayna=ayna)
    assert not deg.get("ölçüt_boş"), (
        "ARC ÖLÇÜTÜ BOŞ -- hiçbir görev denenmedi.\n"
        "  atlanan (hedef üretim haddinden uzun): %d\n"
        "  üretim haddi: %d basamak   basamak/belirteç: %d\n"
        "  Had belirteç cinsinden kalmış olabilir (ferman 1-N)."
        % (int(deg.get("atlanan_uzun", 0)), int(ayar.azami_uret),
           int(ayar.belirtec_basamak)))

    ham_seyir = [float(x["V"]) for x in (r.get("seyir") or [])
                 if isinstance(x, dict) and "V" in x]
    ders = (ogreniyor_mu([float(r["V_ilk"])] + ham_seyir)
            if ham_seyir else
            {"öğreniyor": bool(r["V_son"] < r["V_ilk"]), "eğim": 0.0,
             "bağıntı": 0.0, "artık": 0.0, "bükülme": 0.0,
             "toplam_düşüş": float(r["V_ilk"] - r["V_son"])})

    q_son = nefs.idrak_et(np.zeros((ayar.yigin(), 2, ayar.veri_lifi)))
    psi_son = np.asarray(q_son.y.psi[0], complex)
    ga = GaloisAyari(us=int(ayar.galois_us), n=int(ayar.tableau_n),
                     tohum=int(ayar.tohum))
    tab = tableau_kur(psi_son, ga)
    tdd = kanonik_adres(psi_son, cekirdek=int(ayar.tdd_cekirdek),
                        ayar=TddAyari(tolerans=float(ayar.tdd_tolerans)))
    stab = kararname(psi_son, mertebe=int(ayar.stab_mertebe))
    goz = [q_son.y.sektor(ad) for ad, _ in q_son.ayar.kulli_alanlar]
    K = int(ayar.golge_ornegi)
    t_g = time.perf_counter()
    if K > 0:
        golge_ham = golge_al(psi_son, GolgeAyari(
            ornek=K, had=float(ayar.golge_haddi), tohum=int(ayar.tohum)))
        golge = kestir(golge_ham, goz, tahkik=True)
        golge["açık"] = True
    else:
        golge = {"kestirim": np.zeros(len(goz)), "gözlenebilir": len(goz),
                 "örnek": 0, "açık": False}
    golge["gölge_sn"] = time.perf_counter() - t_g
    t_t = time.perf_counter()
    _P = np.abs(psi_son) ** 2
    _P = _P / max(float(_P.sum()), 1e-300)
    _tam = np.array([float(_P[i:j].sum()) for (i, j) in goz])
    golge["tam_sn"] = time.perf_counter() - t_t
    golge["hız"] = float(golge["tam_sn"] / max(golge["gölge_sn"], 1e-12))
    golge.setdefault("azamî_hata",
                     float(np.max(np.abs(golge["kestirim"] - _tam)))
                     if _tam.size else 0.0)
    flo = flo_evrimi(p_yildiz, MatchgateAyari(
        mod=int(ayar.flo_modu), kapi=int(ayar.flo_kapisi),
        tohum=int(ayar.tohum)))
    sb = sbox_bukme(tab, acik=bool(int(ayar.sbox_acik)))
    sb_olcu = sbox_olcu(us=int(ayar.galois_us))
    palmer = palmer_olcu(n=int(psi_son.size), tohum=int(ayar.tohum))
    fazp = faz_oturt(q_son.y.faz_birikimi(),
                     FazAyari(mertebe=int(ayar.faz_mertebesi),
                              derece=int(ayar.faz_derecesi)))
    sik = koset_indirge(int(fazp["derece"]), SiklotomikAyari(
        us=int(ayar.siklotomik_us), taban=int(ayar.siklotomik_taban),
        derece=int(ayar.siklotomik_derece)))
    sik["iz_eşitliği"] = iz_esitligi(SiklotomikAyari(
        us=int(ayar.siklotomik_us), taban=int(ayar.siklotomik_taban),
        derece=int(ayar.siklotomik_derece)))
    akis = gpu_akisi(psi_son, tab, GpuAyari(
        had=float(ayar.gpu_akis_haddi),
        genlesme=int(ayar.gpu_genlesmesi), tohum=int(ayar.tohum)))
    sad = sadakat_beyani()
    usl = usul_beyani()
    sup = suphe_beyani()
    assert int(sad["çağrı"]) > 0, (
        "MANTIĞA SADAKAT HİÇ KOŞMADI -- ``nefs/sadakat.py`` ana akışta "
        "çağrılmıyor demektir. Sadakat 7/24 koşmalıdır; koşmuyorsa "
        "sistem mantık dışına taşabiliyor.")
    assert int(sup["çağrı"]) > 0, (
        "ŞÜPHE MANİFOLDU HİÇ KOŞMADI -- ``nefs/suphe.py`` bağlanmamış.")
    assert int(usl["yoklama"]) > 0, (
        "MANTIK YÜRÜTME KAPISI HİÇ YOKLANMADI -- ``nefs/usul.py`` "
        "bağlanmamış. Sefer açılmayabilir; yoklanmaması başka şeydir.")
    son_sadakat = sadakat_uygula(psi_son.copy(), SadakatAyari(
        acik=int(ayar.sadakat_acik), parite_lifi=int(ayar.parite_lifi),
        lif_yapisi=tuple(ayar.lif_yapisi)))

    nefs.yukle(p_yildiz)
    _konusma = [padisah(g, nefs=nefs, ayar=ayar, hafiza=hafiza)
                for g in list(dogrulama)[:int(ayar.kademe_gorevi)]]
    konusma = {
        "görev": len(_konusma),
        "konuşan": sum(1 for c in _konusma if not c["sükût"]),
        "susan": sum(1 for c in _konusma if c["sükût"]),
        "budanan": sum(int(c.get("budanan", 0)) for c in _konusma),
        "sebep": [c["sebep"] for c in _konusma if c["sükût"]][:3],
        "belirteç": [list(c["belirteç"] or [])[:12] for c in _konusma][:2],
        "güven": (float(np.mean([c["güven"] for c in _konusma]))
                  if _konusma else 0.0)}

    kefeler = kulli_mizan(nefs, veri, p_yildiz, ayar.sozluk, ayar=mzn,
                          hafiza=hafiza, adim=_sayac["çağrı"],
                          kademe_gorevleri=kademe_gorevleri, ne="döküm")
    cetvel = mizan_cetveli(nefs, veri, p_yildiz, ayar.sozluk, ayar=mzn)
    if int(ayar.mukayese_acik):
        _sek = [q_son.y.sektor(ad) for ad, _ in q_son.ayar.kulli_alanlar]
        _vec = vecih_kur([(ad, s) for (ad, _n), s
                          in zip(q_son.ayar.kulli_alanlar, _sek)])
        mukayese = mukayese_beyani(
            kefeler.get("spektrum"),
            hata_payi(list(kefeler["artık_adı"]),
                      list(np.asarray(kefeler["artık"], float))))
        _dun = [np.asarray(h, complex) for h in
                np.asarray(q_son.y.psi, complex)[:4]]
        mukayese["kiplik"] = kiplik(np.asarray(psi_son, complex), _dun,
                                    _vec)
    else:
        mukayese = mukayese_beyani(None, None)

    kayit = hazine.koy(
        hazine_yolu(),
        dict({"p": p_yildiz}, **hafiza.hazineye()),
        {"tur": int(devam.get("tur", 0)) + 1,
         "imleç": imlec,
         "devam_etti": bool(devam.get("yüklendi")),
         "ölçülen_hız": float(
             (hizolcer_beyani() or {}).get("belirteç_sn", 0.0)),
         "ayar": ayar.ad, "parametre": d, "V_ilk": float(r["V_ilk"]),
         "V_son": float(r["V_son"]), "veri_lifi": int(ayar.veri_lifi),
         "sözlük": int(ayar.sozluk), "pencere": int(ayar.pencere),
         "yerel_yuva": int(ayar.yerel_yuva), "karo": int(ayar.karo),
         "hüküm_lifi": int(ayar.hukum_lifi), "d": int(ayar.d),
         "cömert": float(ayar.comert),
         "harman_kademesi": int(ayar.harman_kademesi),
         "tohum": int(ayar.tohum),
         "öğreniyor": bool(ders["öğreniyor"]),
         "mizan": {k: v for k, v in kefeler.items()
                   if isinstance(v, (int, float))},
         "veri_cetveli": cetvel,
         "hafıza_kapasitesi": int(ayar.hafiza_kapasitesi),
         "hafıza_yazma": float(ayar.hafiza_yazma),
         "hafıza_sönümü": float(ayar.hafiza_sonumu),
         "zeno_eşiği": float(ayar.zeno_esigi)})

    return {"ayar": ayar.ad, "parametre": d,
            "devam": devam, "imleç": imlec,
            "geçit": kapi, "ders": ders, "hazine": kayit,
            "tdd": tdd, "stabilizer": stab, "gölge": golge,
            "galois": tab.beyan(),
            "flo": flo, "sbox": sb, "sbox_ölçü": sb_olcu,
            "palmer": palmer,
            "faz_polinomu": fazp, "gpu_akışı": akis, "siklotomik": sik,
            "sadakat": sad, "son_sadakat": son_sadakat,
            "mukayese": mukayese,
            "mihenk": nobet.beyan(p_yildiz),
            "eniyileme": optimize_beyani(),
            "faz_borcu": q_son.y.faz_borcu(),
            "konuşma": konusma, "münasebet": munasebet_beyani(),
            "keyfiyet": keyfiyet_beyani(),
            "külliyat": {"arc": len(arc_veri), "külliyat": len(kul_veri),
                         "döküm": kulliyat_dokumu()},
            "belirteç": belirtec_beyani(str(ayar.kodlama)),
            "ölçek": ayar.olcek_dokumu, "elle_verilen": ayar.elle,
            "denge": olculen_lam, "ilk_kefeler": ilk_kefeler,
            "usul": usl, "şüphe": sup,
            "hızölçer": hizolcer_beyani(),
            "çekirdek": cekirdek_beyani(),
            "mizan": kefeler, "veri_cetveli": cetvel,
            "hafıza": hafiza.beyan(), "rüşt": float(kefeler["α_rüşt"]),
            "veri": len(veri),
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


def muhurle(cikti_yolu: str, netice: Dict[str, object]) -> None:
    dizin = os.path.dirname(cikti_yolu)
    if dizin:
        os.makedirs(dizin, exist_ok=True)
    def _yaz(o):
        import numpy as _np
        if isinstance(o, (complex, _np.complexfloating)):
            return {"re": float(o.real), "im": float(o.imag)}
        if isinstance(o, _np.ndarray):
            return o.tolist()
        if isinstance(o, (_np.integer,)):
            return int(o)
        if isinstance(o, (_np.floating,)):
            return float(o)
        if isinstance(o, (set, tuple)):
            return list(o)
        if isinstance(o, (bytes, bytearray)):
            return o.decode("utf-8", "replace")
        return str(o)

    with open(cikti_yolu + ".olcum.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in netice.items() if k != "p"},
                  f, ensure_ascii=False, indent=2, default=_yaz)
    print("  [MÜHÜR] Ölçümler kaydedildi: %s.olcum.json" % cikti_yolu,
          flush=True)


def kos(ayar_adi: str = "kısa", cikti: Optional[str] = None,
        kulli_kayip_ile: bool = True) -> str:
    ayar = PROFILLER.get(ayar_adi, KISA_CPU)
    tek_iplik_zorla()
    kulli: Optional[Dict[str, object]] = None
    if kulli_kayip_ile:
        kulli = kulli_kayip_talimi(ayar)
        assert kulli and kulli.get("hazine"), (
            "küllî kayıp hattı BOŞ döndü -- hazineye bir şey yazılmadı")
    if cikti and kulli:
        muhurle(cikti, kulli)
    return talim_beyani(ayar, kulli)


KIPLER: Tuple[str, ...] = ("tâlim", "sıfırla", "mizan", "sabit",
                           "kaggle", "veri")


def taht(ne: str = "tâlim", *arg: str) -> str:
    ne = str(ne)
    if ne == "sıfırla":
        return sifir_beyani(hazine_sifirla())
    if ne == "kaggle":
        from main.kaggle_egitim import kaggle_talimini_baslat
        from main.kaggle_cikarim import kaggle_teslimat_dosyasi_uret
        from ogrenme.kaggle_donanim import ayar_sec
        veri = arg[0] if arg else "/kaggle/input"
        prof = ayar_sec()
        t = kaggle_talimini_baslat(veri)
        return kaggle_beyani(prof, t, kaggle_teslimat_dosyasi_uret)
    if ne == "sabit":
        from tanilama.sabit_teftisi import rapor as sabit_raporu
        return sabit_raporu(*(arg[:1] or ()))
    if ne == "mizan":
        from nefs.kulli_mizan import rapor as mizan_raporu
        return mizan_raporu(arg[0] if arg else "kısa")
    if ne == "veri":
        from main.veri import rapor as veri_raporu
        return veri_raporu(*(arg[:1] or ("training",)))
    if ne == "tâlim":
        ad = arg[0] if arg else "kısa"
        yol = arg[1] if len(arg) > 1 else "depo/kulli_dimag_talim"
        return kos(ad, yol)
    raise ValueError("bilinmeyen kip %r; kipler: %s" % (ne, ", ".join(KIPLER)))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in KIPLER:
        print(taht(sys.argv[1], *sys.argv[2:]))
    else:
        print(taht("tâlim", *sys.argv[1:]))
