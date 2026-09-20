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
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from nefs.musahede import gorevleri_getir
from ogrenme.mecz import MeczAyari, mecz_egit, mecz_beyani
from main import hazine
from nefs.kulli_mizan import (FockUzayi, Hamiltonyen, MizanAyari,
                              balyala, fock_beyani, hamiltonyen_beyani,
                              kulli_mizan, mizan_cetveli)
from nefs.hafiza import Hafiza, tertip_beyani
from main.cikarim import (hazineden_yukle, hafizayi_yukle, padisah,
                          hazineden_devam, devam_agirligi)
from nefs.tdd import TddAyari, kanonik_adres
from nefs.matchgate import MatchgateAyari, flo_evrimi
from nefs.ayna import AynaAyari
from nefs.mihenk import (MIHENK, nobet_kur, safha,
                         safha_beyani, safha_sifirla)
from nefs.veri_kapisi import (VeriKapisiAyari, veri_kapisi,
                              kapi_beyani, kapi_tertibi)
from nefs.qcekirdek import cekirdek_beyani
from nefs.parametre_yazmaci import (ParametreAyari, ParametreYazmaci,
                                    parametre_beyani, kenet_beyani)
from nefs.nqs import nqs_beyani, turun_genligi, tur_beyani
from nefs.mahalli_yazmac import (mahalli_beyani, uzunluk_beyani,
                                 uzunluk_genligi)
from tanilama.hizolcer import (Hizolcer, hizolcer_bagla,
                               hizolcer_beyani)
from nefs.kararname import kararname
from nefs.golge import (GolgeAyari, golge_al,
                        kestir)
from nefs.sadakat import (SadakatAyari, sadakat_uygula,
                          sadakat_beyani, sadakat_devresi,
                          sadakat_devre_beyani)
from nefs.olcek import Kok, olcek, denge, olcek_beyani
from nefs.belirtec import (belirtec_kapisi, belirtec_sozlugu,
                           belirtec_beyani)
from nefs.keyfiyet import (KeyfiyetAyari, keyfiyet,
                           keyfiyet_beyani)
from nefs.munasebet import (Harita, MunasebetAyari, munasebet_kos,
                            munasebet_beyani)
from main.kulliyat import (kulliyat_verisi,
                           kulliyat_dokumu, kulliyat_beyani)
from nefs.mukayese import (hata_payi, kiplik, mukayese_beyani,
                           mukayese_melekesi_beyani, omur_beyani,
                           vecih_beyani,
                           vecihleri_istihrac, yirtiklari_tertiple)
from kuantum.devre import devre_beyani
from nefs.qyazmac import sektor_beyani
from matematik.sonsuz_mertebeler_teorisi import (HendeseAyari, hendese_teshisi,
                                                 hendese_beyani, harita_kur,
                                                 lif_beyani)
from nefs.casimir import (CasimirAyari, blok_kosegen_artigi,
                          casimir_beyani, dhr_ayrismasi,
                          gelfand_tsetlin_araya_girme, kartan_fazi)
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
    lam_lif: float = 0.0
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
    motor: str = "sürekli"
    genlik_tipi: str = ""
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
            if getattr(self, k, None) in (0, 0.0, ""):
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
        from tanilama.hiz_teftisi import BUTCE_SANIYESI, HEDEF, had, olc
        h = olc(hiz_ayari)
        o["belirteç_sn"] = float(h["belirteç_sn"])
        o["hız_haddi"] = float(had())
        o["hız_hedefi"] = float(HEDEF)
        o["hız_geçti"] = bool(h["belirteç_sn"] >= had())
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
            from tanilama.hiz_teftisi import had
            assert o["hız_geçti"], (
                "HIZ HADDİ TUTMUYOR -- TÂLİM BAŞLAMAZ.\n"
                "  ölçülen : %.1f belirteç/sn\n"
                "  had     : %.0f belirteç/sn  (%.0f kat eksik)\n"
                "  bir kayıp çağrısı: %.4f sn   en pahalı uzuv: %s\n"
                "  Ferman: hız garantisi elde etmeden umumi tâlim "
                "başlatılmaz." % (o["belirteç_sn"], had(),
                                  had() / max(1e-9, o["belirteç_sn"]),
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
        lam_tasma=float(a.lam_tasma), lam_lif=float(a.lam_lif),
        basamak=int(a.belirtec_basamak),
        meleke_olcumu=int(a.meleke_olcumu),
        usul_acik=int(a.usul_acik), usul_haddi=float(a.usul_haddi),
        usul_seferi=int(a.usul_seferi),
        suphe_acik=int(a.suphe_acik), suphe_sonumu=float(a.suphe_sonumu),
        rust_t0=float(a.rust_t0),
        rust_tau=float(a.rust_tau), rust_kapanis=float(a.rust_kapanis),
        rust_muayene=int(a.rust_muayene), zeno_esigi=float(a.zeno_esigi),
        toplam_adim=max(1, int(a.talim_tur) * max(1, int(a.altuzay_ornek))),
        tohum=int(a.tohum))


def d0_gecit(Z: Dict[str, Any]) -> Dict[str, Any]:
    ayar = Z["ayar"]
    t0 = time.perf_counter()
    kapi_bel = belirtec_kapisi(str(ayar.kodlama))
    assert int(kapi_bel.n_vocab) == int(ayar.sozluk), (
        "sözlük ile kodlama tutmuyor: ayar %d, %s %d -- sözlük elle "
        "yazılmış olabilir (ferman 1-N)"
        % (ayar.sozluk, ayar.kodlama, kapi_bel.n_vocab))
    safha_sifirla()
    safha("D0 GEÇİT · başlıyor", profil=str(ayar.ad))
    kapi = gecit(sert=bool(int(ayar.hiz_geciti)), hiz_ayari=ayar)
    safha("D0 GEÇİT", çevrim=int(kapi.get("alan_çevrimi", 0)),
          kelâm=bool(kapi.get("kelam_ayrıştı")))
    Z.update({"t0": t0, "kapi_bel": kapi_bel, "kapi": kapi})
    return Z


def d1_olcu(Z: Dict[str, Any]) -> Dict[str, Any]:
    from nefs.qegitim import ornekler
    ayar = Z["ayar"]
    gorevler = Z["gorevler"]
    hepsi = list(gorevler) if gorevler is not None else \
        gorevleri_getir("training")
    egitim_gorevleri, dogrulama = gorevleri_getir(ne="böl", gorevler=
        hepsi, dogrulama=int(ayar.dogrulama_sayisi), tohum=ayar.tohum)
    arc_veri = ornekler(egitim_gorevleri,
                        azami=max(1, int(ayar.ornek_sayisi) // 2),
                        pencere=ayar.pencere, sozluk=ayar.sozluk,
                        tohum=ayar.tohum, taban=int(ayar.veri_lifi),
                        basamak=int(ayar.belirtec_basamak))
    safha("D1 ÖLÇÜ · ARC", örnek=len(arc_veri))
    devam = hazineden_devam(hazine_yolu())
    kul_veri, imlec = kulliyat_verisi(
        sozluk=int(ayar.sozluk), pencere=int(ayar.pencere),
        azami=max(0, int(ayar.ornek_sayisi) - len(arc_veri)),
        tohum=int(ayar.tohum), kodlama=str(ayar.kodlama),
        taban=int(ayar.veri_lifi),
        basamak=int(ayar.belirtec_basamak),
        imlec=devam.get("imleç"), ne="imleçli")
    gelen = list(arc_veri) + list(kul_veri)

    safha("D1 ÖLÇÜ · külliyat", örnek=len(gelen))
    Z.update({"egitim_gorevleri": egitim_gorevleri,
              "dogrulama": dogrulama, "arc_veri": arc_veri,
              "devam": devam, "kul_veri": kul_veri, "imlec": imlec,
              "gelen": gelen})
    return Z


def d2_hendese(Z: Dict[str, Any]) -> Dict[str, Any]:
    from nefs.qegitim import ornek_bol as _bol
    ayar = Z["ayar"]
    gelen = Z["gelen"]
    hendese = hendese_teshisi(
        [_bol(o)[0] for o in gelen], ayar.lif_yapisi,
        HendeseAyari(azami_alfabe=int(ayar.veri_lifi),
                     tohum=int(ayar.tohum)))

    if "parite_lifi" not in ayar.elle:
        ayar.parite_lifi = int(hendese["asansör"]["kat"])

    safha("D2 HENDESE", kafes=len(hendese["kafes"]),
          tıkanma=int(hendese["şelale"]["tıkanma"]),
          büzülme="%.3f" % float(hendese["asansör"]["büzülme"]))
    Z.update({"hendese": hendese})
    return Z


def d3_kurulus(Z: Dict[str, Any]) -> Dict[str, Any]:
    from nefs.kulli_kayip import kademe_parametreleri_ac
    from nefs.melekeler import QNefs
    ayar = Z["ayar"]
    hendese = Z["hendese"]
    devam = Z["devam"]
    egitim_gorevleri = Z["egitim_gorevleri"]
    nefs = QNefs(ayar.tohum, ayar.qayar())
    _hodge = hendese["hodge"]
    nefs.izdusum = (hendese["Π"],
                    (float(_hodge["𝒮_simetrik"]), float(_hodge["𝒜_yönlü"]),
                     float(_hodge["Ω_yırtık"])))
    nefs.idrak_et(np.eye(2, ayar.veri_lifi))
    hafiza = Hafiza(kapasite=int(ayar.hafiza_kapasitesi),
                    yazma=float(ayar.hafiza_yazma),
                    sonum=float(ayar.hafiza_sonumu),
                    zeno_esigi=float(ayar.zeno_esigi),
                    zeno_tepe=float(ayar.zeno_tepe),
                    ayniyet=float(ayar.hafiza_ayniyet),
                    buhar=float(ayar.hafiza_buhar), tohum=int(ayar.tohum))
    kademe_parametresi = kademe_parametreleri_ac(nefs.p)
    d = len(nefs)
    p0 = devam_agirligi(devam, nefs, d)
    kademe_gorevleri = list(egitim_gorevleri)[:int(ayar.kademe_gorevi)]

    mzn = mizan_ayari(ayar)
    LAM_ADLARI = ("lam_cevrim", "lam_monogami", "lam_tip", "lam_engel",
                  "lam_tenakuz", "lam_kategori", "lam_nokta",
                  "lam_meleke", "lam_zirh", "lam_kaide",
                  "lam_tasma", "lam_lif")
    _elle_lam = tuple(a for a in LAM_ADLARI
                      if float(getattr(ayar, a, 0.0)) != 0.0)
    _mzn = {"a": mzn}
    fock = FockUzayi()
    _derece: List[str] = []
    for _dug, _ro in zip(hendese["kafes"], hendese["tayf"]):
        if float(_ro) <= 0.0:
            continue
        _ad = "mertebe·%s" % _dug["ad"]
        fock.yarat(_ad, entropi=float(-_ro * np.log(max(float(_ro), 1e-300))),
                   butce=float(_ro),
                   celiski=float(hendese["hodge"]["Ω_yırtık"]))
        _derece.append(_ad)
    assert _derece, (
        "DERECELİ FOCK DEVRİ BOŞ -- türetim kafesinin hiçbir katmanı mod "
        "doğurmadı; her katman kendi hendesesinde nefes almalı "
        "(ferman 2-Ā-B, 2-Þ)")
    hamiltonyen = Hamiltonyen(fock=fock)
    safha("D3 KURULUŞ", derece=len(_derece), parametre=int(d))
    Z.update({"nefs": nefs, "hafiza": hafiza, "d": d, "p0": p0,
              "kademe_parametresi": kademe_parametresi,
              "kademe_gorevleri": kademe_gorevleri, "mzn": mzn,
              "_elle_lam": _elle_lam, "_mzn": _mzn, "fock": fock,
              "_derece": _derece, "hamiltonyen": hamiltonyen})
    return Z


def d4_kapi(Z: Dict[str, Any]) -> Dict[str, Any]:
    ayar = Z["ayar"]
    gelen = Z["gelen"]
    nefs = Z["nefs"]
    hafiza = Z["hafiza"]
    kapi_hukmu = veri_kapisi(
        gelen, nefs=nefs, hafiza=hafiza,
        ayar=VeriKapisiAyari(acik=1, sozluk=int(ayar.sozluk),
                             taban=int(ayar.veri_lifi),
                             basamak=int(ayar.belirtec_basamak)))
    veri = list(kapi_hukmu["kabul"])
    assert veri, (
        "tâlim verisi BOŞ -- kapı %d örneğin hepsini reddetti: %r"
        % (int(kapi_hukmu["gelen"]), kapi_hukmu["sebep"]))
    safha("D4 KAPI", örnek=len(veri))
    Z.update({"kapi_hukmu": kapi_hukmu, "veri": veri})
    return Z


def d5_uzay(Z: Dict[str, Any]) -> Dict[str, Any]:
    from nefs.mukayese import (ana_superpozisyon, cozum_uzayi_ac,
                               cozum_uzayi_kapat,
                               mantik_filtresi, mukayese_filtresi)
    from nefs.qegitim import ornek_bol as _ornek_bol
    ayar = Z["ayar"]
    veri = Z["veri"]
    nefs = Z["nefs"]
    hafiza = Z["hafiza"]
    fock = Z["fock"]
    hamiltonyen = Z["hamiltonyen"]
    _derece = Z["_derece"]
    sual = ana_superpozisyon([_ornek_bol(o)[0] for o in veri],
                             nefs=nefs, hafiza=hafiza,
                             sozluk=int(ayar.sozluk),
                             pencere=int(ayar.pencere),
                             taban=int(ayar.veri_lifi),
                             basamak=int(ayar.belirtec_basamak))
    safha("D5 SUAL", derece=len(_derece))
    uzay = cozum_uzayi_ac(sual, nefs=nefs, hafiza=hafiza, fock=fock)
    uzay = mantik_filtresi(uzay)
    uzay = mukayese_filtresi(uzay, hafiza=hafiza,
                             mahalli=getattr(nefs, "mahalli", None))
    safha("D5 SÜZGEÇ")
    netice = cozum_uzayi_kapat(uzay, sual, hamiltonyen=hamiltonyen)
    netice["uzunluk_genliği"] = uzunluk_genligi(
        getattr(nefs, "mahalli", None), int(netice["pencere"]))
    Z.update({"sual": sual, "uzay": uzay, "netice": netice})
    return Z


def d5b_sadakat(Z: Dict[str, Any]) -> Dict[str, Any]:
    ayar = Z["ayar"]
    nefs = Z["nefs"]
    hafiza = Z["hafiza"]
    fock = Z["fock"]
    netice = Z["netice"]
    _mzn = Z["_mzn"]
    _sadakat_ayari = SadakatAyari(acik=int(ayar.sadakat_acik),
                                  parite_lifi=int(ayar.parite_lifi),
                                  lif_yapisi=tuple(ayar.lif_yapisi),
                                  sozluk=int(ayar.sozluk))
    sadakat_devresi(nefs=nefs, hafiza=hafiza, fock=fock, netice=netice,
                    ayar=_sadakat_ayari)
    ayar.pencere = int(netice["pencere"])
    hafiza.kapasite = int(netice["hafıza_kapasitesi"])
    mzn = mizan_ayari(ayar)
    _mzn["a"] = mzn
    safha("D5b SADAKAT", pencere=int(ayar.pencere))
    Z.update({"_sadakat_ayari": _sadakat_ayari, "mzn": mzn, "_mzn": _mzn})
    return Z


def d6_mizan(Z: Dict[str, Any]) -> Dict[str, Any]:
    ayar = Z["ayar"]
    nefs = Z["nefs"]
    hafiza = Z["hafiza"]
    fock = Z["fock"]
    netice = Z["netice"]
    veri = Z["veri"]
    p0 = Z["p0"]
    d = Z["d"]
    mzn = Z["mzn"]
    _mzn = Z["_mzn"]
    _elle_lam = Z["_elle_lam"]
    hamiltonyen = Z["hamiltonyen"]
    kapi_hukmu = Z["kapi_hukmu"]
    kademe_gorevleri = Z["kademe_gorevleri"]
    _sadakat_ayari = Z["_sadakat_ayari"]

    def _dengele(dokum) -> Dict[str, float]:
        lam = denge(dokum,
                    nispet=hamiltonyen.kefelerden(dokum).nispetler())
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
    _sayac = {"çağrı": 0}
    from tanilama.hiz_teftisi import had as _hiz_haddi
    olcer = Hizolcer(belirtec_basina=len(veri) * int(ayar.pencere),
                     had=float(_hiz_haddi(int(ayar.d), int(ayar.karo))),
                     ad="küllî mizan", sert=True,
                     canli_saniye=float(ayar.canli_saniye))
    hizolcer_bagla(olcer)

    _kume: Dict[str, Any] = {"v": list(veri), "adım": 0}
    _seyir: List[Dict[str, float]] = []
    safha("D6 MİZAN · nöbet")
    nobet = nobet_kur(nefs, ara_saniye=float(ayar.mihenk_arasi),
                      pencere=int(ayar.pencere), sozluk=int(ayar.sozluk),
                      taban=int(ayar.veri_lifi),
                      basamak=int(ayar.belirtec_basamak),
                      kodlama=str(ayar.kodlama))

    def _kume_kimlik(kume) -> str:
        import hashlib
        h = hashlib.blake2b(digest_size=3)
        for o in kume:
            h.update(np.asarray(o[0], np.int64).tobytes()[:64])
            h.update(bytes([int(o[1]) & 0xFF]))
        return h.hexdigest()

    def kayip_p(P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, float))
        out = np.empty(P.shape[0], float)
        kume = list(_kume["v"])
        for i, p in enumerate(P):
            _sayac["çağrı"] += 1
            sadakat_devresi(nefs=nefs, hafiza=hafiza, fock=fock,
                            netice=netice, ayar=_sadakat_ayari)
            with olcer.saat(len(kume) * int(ayar.pencere)):
                t = kulli_mizan(nefs, kume, p, ayar.sozluk, ayar=_mzn["a"],
                                hafiza=hafiza.klon(),
                                kapi_hukmu=kapi_hukmu,
                                adim=int(_kume["adım"]),
                                kademe_gorevleri=kademe_gorevleri)
            out[i] = float(t["kayıp"])
            _seyir.append({"V": float(t["kayıp"]),
                           "ham": float(t.get("kayıp_ham", 0.0))})
            nobet.yokla(p, kayip=float(t["kayıp"]),
                        ham=float(t.get("kayıp_ham", 0.0)),
                        kume=len(kume), kume_kimlik=_kume_kimlik(kume),
                        eniyileme=mecz_beyani(),
                        adim=_sayac["çağrı"])
        return out

    def _eniyile(p_, kume):
        n0 = _sayac["çağrı"]
        _kume["v"] = list(kume)
        _kume["adım"] = int(_sayac["çağrı"])
        rr = mecz_egit(nefs, kayip_p, np.asarray(p_, float),
                       kume=list(kume), sozluk=int(ayar.sozluk),
                       ayar=MeczAyari(ad=ayar.ad,
                                      tur=max(1, int(ayar.altuzay_ornek)),
                                      tohum=int(ayar.tohum)))
        return np.asarray(rr["p"], float), _sayac["çağrı"] - n0

    def _olc(p_, kume):
        return kulli_mizan(nefs, list(kume), np.asarray(p_, float),
                           ayar.sozluk, ayar=_mzn["a"], hafiza=hafiza,
                           adim=_sayac["çağrı"], kapi_hukmu=kapi_hukmu,
                           kademe_gorevleri=kademe_gorevleri, ne="döküm")

    Z.update({"ilk_kefeler": ilk_kefeler, "olculen_lam": olculen_lam,
              "_sayac": _sayac, "olcer": olcer, "_kume": _kume,
              "_seyir": _seyir, "nobet": nobet, "kayip_p": kayip_p,
              "_eniyile": _eniyile, "_olc": _olc, "_dengele": _dengele,
              "mzn": _mzn["a"]})
    return Z


def d8_dongu(Z: Dict[str, Any]) -> Dict[str, Any]:
    ayar = Z["ayar"]
    veri = Z["veri"]
    p0 = Z["p0"]
    devam = Z["devam"]
    _eniyile = Z["_eniyile"]
    _olc = Z["_olc"]
    _dengele = Z["_dengele"]
    mun = munasebet_kos(
        veri, p0, _eniyile, _olc,
        dengele=_dengele,
        harita=Harita.hazineden(
            {"münasebet.M": devam.get("müşterek")}
            if devam.get("müşterek") is not None else None,
            n_v=int(ayar.veri_lifi),
            islenen=int(devam.get("müşterek_işlenen", 0) or 0)),
        ayar=MunasebetAyari(
            acik=1,
            obek=int(ayar.yigin()),
                            azami_tur=int(ayar.keyfiyet_turu),
                            n_v=int(ayar.veri_lifi),
            azami_saniye=float(ayar.azami_talim_saati) * 3600.0),
        keyfiyet_ayari=KeyfiyetAyari(acik=1,
                                     azami_tur=int(ayar.keyfiyet_turu)))
    safha("D8 DÖNGÜ", temizlenen=int(mun.get("temizlenen", 0)))
    Z.update({"mun": mun})
    return Z


def d9_kapanis(Z: Dict[str, Any]) -> Dict[str, Any]:
    ayar = Z["ayar"]
    veri = Z["veri"]
    p0 = Z["p0"]
    d = Z["d"]
    nefs = Z["nefs"]
    hafiza = Z["hafiza"]
    fock = Z["fock"]
    mun = Z["mun"]
    _derece = Z["_derece"]
    _mzn = Z["_mzn"]
    _kume = Z["_kume"]
    _sayac = Z["_sayac"]
    _seyir = Z["_seyir"]
    kapi_hukmu = Z["kapi_hukmu"]
    kademe_gorevleri = Z["kademe_gorevleri"]
    _kume["v"] = list(veri)
    kume_kapanisi = {
        "yırtık": yirtiklari_tertiple(hafiza, getattr(nefs, "mahalli",
                                                     None)),
        "kapı": kapi_tertibi(kapi_hukmu, hafiza,
                             getattr(nefs, "mahalli", None)),
        "balya": balyala(hafiza, fock),
        "derece_kapandı": int(sum(1 for _a in _derece if fock.yok_et(_a)))}
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
    safha("D9 KÜME KAPANIŞI", V_ilk="%.4f" % r["V_ilk"],
          V_son="%.4f" % r["V_son"])
    Z.update({"kume_kapanisi": kume_kapanisi, "p_son": p_son, "r": r,
              "mzn": mzn})
    return Z


def d10_kelam(Z: Dict[str, Any]) -> Dict[str, Any]:
    from nefs.qegitim import degerlendir
    ayar = Z["ayar"]
    veri = Z["veri"]
    d = Z["d"]
    r = Z["r"]
    mzn = Z["mzn"]
    _mzn = Z["_mzn"]
    _sayac = Z["_sayac"]
    nefs = Z["nefs"]
    hafiza = Z["hafiza"]
    devam = Z["devam"]
    dogrulama = Z["dogrulama"]
    hendese = Z["hendese"]
    hamiltonyen = Z["hamiltonyen"]
    kademe_gorevleri = Z["kademe_gorevleri"]
    mun = Z["mun"]
    p_yildiz = np.asarray(r["p"], float)
    assert p_yildiz.size == d, (
        "tâlim %d parametre aldı, %d döndürdü" % (d, p_yildiz.size))
    assert np.all(np.isfinite(p_yildiz)), "tâlim NaN/Inf parametre döndürdü"
    nefs.yukle(p_yildiz)
    deg = degerlendir(nefs, dogrulama, azami=ayar.degerlendirme_gorevi,
                      pencere=ayar.pencere, sozluk=ayar.sozluk,
                      azami_uret=ayar.azami_uret)
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
    tur = turun_genligi(nefs, q_son)
    psi_son = tur.hal
    dhr = dhr_ayrismasi(tur.yigin, q_son.y.ayar.lif, CasimirAyari(acik=1))
    dhr["araya_girme"] = gelfand_tsetlin_araya_girme(dhr["pay"])
    dhr["blok_artığı"] = blok_kosegen_artigi(tur.yigin, q_son.y.ayar.lif)
    dhr["kartan_boyu"] = int(kartan_fazi(
        q_son.y.ayar.lif, [float(ayar.ayna_teta)]).size)

    tdd = kanonik_adres(psi_son, cekirdek=int(ayar.tdd_cekirdek),
                        ayar=TddAyari(tolerans=float(ayar.tdd_tolerans)))
    stab = kararname(psi_son, mertebe=int(ayar.stab_mertebe))
    goz = tur.sektor_araliklari()
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
    _tur = tur_beyani()
    assert int(_tur["tur_başına_kan"]) == 1, (
        "TURDA %s KAN ÇAĞRISI -- ferman 2-A turda BİR çağrı ister; "
        "genlik ne iki kere üretilir ne sözlük boyunda şişirilir."
        % _tur["tur_başına_kan"])
    _devre = sadakat_devre_beyani()
    assert int(_devre["çağrı"]) > 0, (
        "SADAKAT DEVRESİ HİÇ KOŞMADI -- ferman 2-Đ istisnasız bütün "
        "süperpozisyonlarda doğrulayıcı devre ister.")
    assert not _devre["muaf"], (
        "SADAKAT DEVRESİNDEN MUAF KALAN SÜPERPOZİSYON VAR: %r -- "
        "ferman 2-Đ 'istisnasız' der (invaryant I8)." % (_devre["muaf"],))
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
    taban_durumu = hamiltonyen.kefelerden(kefeler).taban_durumu()
    cetvel = mizan_cetveli(nefs, veri, p_yildiz, ayar.sozluk, ayar=mzn)
    if int(ayar.mukayese_acik):
        _dun_ilk = [np.asarray(h, complex) for h in tur.yigin[:4]]
        _vec = vecihleri_istihrac(_dun_ilk + [psi_son])
        mukayese = mukayese_beyani(
            kefeler.get("spektrum"),
            hata_payi(list(kefeler["artık_adı"]),
                      list(np.asarray(kefeler["artık"], float))))
        mukayese["kiplik"] = kiplik(np.asarray(psi_son, complex),
                                    _dun_ilk, _vec)
    else:
        mukayese = mukayese_beyani(None, None)

    harita = harita_kur(nefs, veri, sozluk=int(ayar.sozluk),
                        hendese=hendese, munasebet=mun["harita"],
                        onceki=devam.get("harita"))

    safha("D10 KELÂM", konuşan=int(konusma["konuşan"]),
          susan=int(konusma["susan"]))
    Z.update({"p_yildiz": p_yildiz, "deg": deg, "ders": ders,
              "q_son": q_son, "tur": tur, "psi_son": psi_son, "dhr": dhr,
              "tdd": tdd, "stab": stab, "goz": goz,
              "golge": golge, "flo": flo,
              "sad": sad, "usl": usl, "sup": sup, "_tur": _tur,
              "son_sadakat": son_sadakat, "konusma": konusma,
              "kefeler": kefeler, "taban_durumu": taban_durumu,
              "cetvel": cetvel, "mukayese": mukayese, "harita": harita})
    return Z


def d11_muhur(Z: Dict[str, Any]) -> Dict[str, Any]:
    ayar = Z["ayar"]
    d = Z["d"]
    r = Z["r"]
    mun = Z["mun"]
    devam = Z["devam"]
    imlec = Z["imlec"]
    fock = Z["fock"]
    hafiza = Z["hafiza"]
    ders = Z["ders"]
    kefeler = Z["kefeler"]
    cetvel = Z["cetvel"]
    harita = Z["harita"]
    p_yildiz = Z["p_yildiz"]
    taban_durumu = Z["taban_durumu"]
    _kapanan = int(mun.get("temizlenen", 0)) + int(mun.get("kirli_kalan", 0))
    kayit = hazine.muhurle(
        _kapanan,
        hazine_yolu(),
        dict({"p": p_yildiz}, **hafiza.hazineye(),
             **mun["harita"].hazineye()),
        {"tur": int(devam.get("tur", 0)) + 1,
         "imleç": imlec,
         "taban_durumu": taban_durumu,
         "fock": fock.beyan(),
         "harita": harita.hazineye(),
         "müşterek_işlenen": int(mun["harita"].islenen),
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
    safha("D11 MÜHÜR", bayt=int(kayit.get("bayt", 0) or 0))
    Z.update({"kayit": kayit})
    return Z


ZINCIR: Tuple[Any, ...] = (d0_gecit, d1_olcu, d2_hendese, d3_kurulus,
                           d4_kapi, d5_uzay, d5b_sadakat, d6_mizan,
                           d8_dongu, d9_kapanis, d10_kelam, d11_muhur)


def kulli_kayip_talimi(ayar: EgitimAyari = KISA_CPU,
                       gorevler: Optional[Sequence] = None
                       ) -> Dict[str, object]:
    from tanilama.beyan import netice_derle
    safha_sifirla()
    Z: Dict[str, Any] = {"ayar": ayar, "gorevler": gorevler}
    for durum in ZINCIR:
        Z = durum(Z)
    return netice_derle(Z)


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


def profil_sec() -> EgitimAyari:
    from nefs.donanim import gpu_var_mi
    g = gpu_var_mi()
    if not g.get("var"):
        return DAR
    kart = list(g.get("cihaz") or ())
    vram = 0.0
    for satir in kart:
        for parca in str(satir).split(","):
            p = parca.strip()
            if p.lower().endswith("mib"):
                vram += float(p[:-3].strip()) / 1024.0
    if len(kart) >= 2 and vram >= 40.0:
        return AZAMI
    return ORTA


def taht(ne: str = "tâlim", *arg: str) -> str:
    ne = str(ne)
    if ne == "sıfırla":
        return sifir_beyani(hazine_sifirla())
    if ne == "kaggle":
        from main.cikarim import teslimat_uret
        test = (arg[0] if arg else
                "/kaggle/input/arc-prize-2026/arc-agi_test_challenges.json")
        cikti = arg[1] if len(arg) > 1 else "/kaggle/working/submission.json"
        prof = profil_sec()
        return kaggle_beyani(prof, kulli_kayip_talimi(prof),
                             teslimat_uret(test, cikti, ayar=prof))
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
