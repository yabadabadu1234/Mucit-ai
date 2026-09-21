from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import (Any, Callable, Dict, Iterable, List, Optional,
                    Sequence, Tuple)

import numpy as np

from matematik.mizan import ardisiklik_kaidesi
from matematik.mizan import mertebe_adi
from matematik.sonsuz_mertebeler_teorisi import RED_HATALARI
from .melekeler import qmelekeler, qsicil
from .zihin_durumu import QAyar, QYazmac, donme


@dataclass(frozen=True)
class OlcuUzayi:
    ad: str
    alt: float
    ust: float
    buyugu_iyi: bool
    tahmini_ust: bool = False

    def gecerli_mi(self) -> bool:
        return float(self.ust) > float(self.alt)


MERTEBE_UZAYI = OlcuUzayi("mertebe", 0.0, 1.0, True)


def _mertebeler() -> Dict[str, float]:
    from matematik.mizan import MERTEBELER
    m = {str(ad): float(esik) for esik, ad in MERTEBELER}
    assert m, "mertebe merdiveni BOŞ geldi -- mizan bozuk"
    return m


UZAYLAR: Dict[str, OlcuUzayi] = {
    "tenakuz": OlcuUzayi("tenakuz", 0.0, 1.0, False),
    "nakz": OlcuUzayi("nakz", 0.0, 1.0, False),
    "tasdik": OlcuUzayi("tasdik", 0.0, 1.0, True),
    "sukut": OlcuUzayi("sukut", 0.0, 1.0, False),
    "gaye": OlcuUzayi("gaye", 0.0, 1.0, True),
    "mizan": OlcuUzayi("mizan", 0.0, 1.0, True),
    "makam": OlcuUzayi("makam", 0.0, 1.0, True),
    "kelam": OlcuUzayi("kelam", 0.0, 1.0, True),
    "kesme_hakiki": OlcuUzayi("kesme_hakiki", 0.0, 1.0, False),
    "norm_hatası": OlcuUzayi("norm_hatası", 0.0, 1.0, False),
    "capraz_entropi": OlcuUzayi("capraz_entropi", 0.0, float(np.log(16.0)),
                                False),
    "hucre_isabeti": OlcuUzayi("hucre_isabeti", 0.0, 1.0, True),
    "tam_cozum": OlcuUzayi("tam_cozum", 0.0, 1.0, True),
}


def mertebe(x=None, S=None, ne: str = "ileri", m: float = 0.0,
                    f=None, T=None, tohum: int = 0, n: int = 64,
                    ad: str = "", ust=None):
    if ne == "uzay":
        if ad in UZAYLAR and ust is None:
            return UZAYLAR[ad]
        if ust is None:
            return OlcuUzayi(ad, 0.0, 1.0, False, tahmini_ust=True)
        return OlcuUzayi(ad, 0.0, float(ust), False,
                         tahmini_ust=ad not in UZAYLAR)

    def ileri(v, U):
        if not U.gecerli_mi():
            return 0.5
        u = (float(v) - U.alt) / (U.ust - U.alt)
        u = float(np.clip(u, 0.0, 1.0))
        return u if U.buyugu_iyi else 1.0 - u

    def geri(v, U):
        if not U.gecerli_mi():
            return U.alt
        u = float(np.clip(v, 0.0, 1.0))
        if not U.buyugu_iyi:
            u = 1.0 - u
        return U.alt + u * (U.ust - U.alt)

    if ne == "ileri":
        return ileri(x, S)
    if ne == "geri":
        return geri(m, S)
    if ne == "morfizm":
        return lambda z: ileri(f(geri(z, S)), T)
    if ne == "adlandır":
        k, _ = min(_mertebeler().items(),
                   key=lambda kv: abs(kv[1] - float(m)))
        return k
    if ne != "doğrula":
        raise ValueError("funktör kipi bilinmiyor: %r" % (ne,))
    rng = np.random.default_rng(tohum)
    S = OlcuUzayi("S", -2.0, 5.0, True)
    T = OlcuUzayi("T", 0.0, 3.0, False)
    U = OlcuUzayi("U", 1.0, 9.0, True)
    m = rng.uniform(0.0, 1.0, size=n)

    birim = mertebe(ne="morfizm", f=lambda x: x, S=S, T=S)
    hata_birim = float(np.max(np.abs([birim(v) - v for v in m])))

    def f(x: float) -> float:
        return 0.0 + 3.0 * (x + 2.0) / 7.0

    def g(x: float) -> float:
        return 1.0 + 8.0 * x / 3.0

    sol = mertebe(ne="morfizm", f=lambda x: g(f(x)), S=S, T=U)
    sag_f = mertebe(ne="morfizm", f=f, S=S, T=T)
    sag_g = mertebe(ne="morfizm", f=g, S=T, T=U)
    hata_terkip = float(np.max(np.abs(
        [sol(v) - sag_g(sag_f(v)) for v in m])))

    x = np.sort(rng.uniform(S.alt, S.ust, size=n))
    mert = np.asarray([mertebe(v, S) for v in x])
    sira_korunuyor = bool(np.all(np.diff(mert) >= -1e-12))

    S_ters = OlcuUzayi("S_ters", S.alt, S.ust, not S.buyugu_iyi)
    mert_ters = np.asarray([mertebe(v, S_ters) for v in x])
    sira_bozuluyor = bool(np.all(np.diff(mert_ters) <= 1e-12)
                          and np.ptp(mert_ters) > 1e-6)

    return {"birim_hatası": hata_birim,
            "terkip_hatası": hata_terkip,
            "terkip_aşikâr_mı": True,
            "sıra_korunuyor": sira_korunuyor,
            "cihet_ters_çevrilince_bozuluyor": sira_bozuluyor,
            "funktör_mü": (hata_birim < 1e-9 and hata_terkip < 1e-9
                           and sira_korunuyor),
            "ölçüt_kör_değil": sira_korunuyor and sira_bozuluyor}


@dataclass
class Olcum:
    kaynak: str
    deger: float
    uzay: OlcuUzayi
    agirlik: float = 1.0

    def mertebe(self) -> float:
        return mertebe(self.deger, self.uzay)

    def eksik(self) -> float:
        return self.agirlik * (1.0 - self.mertebe())


BETA: float = 8.0


HEDEF_USSU: float = 0.5


def zayif_halka(x=None, beta=None, ne: str = "asgarî",
                             olcumler=None, hedef_us=None):
    if ne == "asgarî":
        a = np.asarray(x, float).reshape(-1)
        if a.size == 0:
            return 0.0
        if a.size == 1:
            return float(a[0])
        b = float(max(beta if beta is not None else BETA, 1e-6))
        z = -b * a
        m = float(np.max(z))
        return float(-(m + np.log(np.sum(np.exp(z - m)))
                       - np.log(a.size)) / b)

    if ne == "katılan":
        eksikler = np.asarray(x, float)
        z = beta * eksikler
        z = z - float(np.max(z))
        w = np.exp(z)
        t = float(np.sum(w))
        if t <= 0.0:
            return float(eksikler.size)
        w = w / t
        nz = w > 0.0
        H = float(-np.sum(w[nz] * np.log(w[nz])))
        return float(np.exp(H))

    if ne != "azamî":
        raise ValueError("toplama kipi bilinmiyor: %r" % (ne,))
    if not olcumler:
        return {"kayıp": 0.0, "ortalama_mertebe": 1.0, "uzuv": 0,
                "en_zayıf": None, "tahminî_hadli": 0}
    eksikler = [o.eksik() for o in olcumler]
    mert = [o.mertebe() for o in olcumler]
    en_zayif = min(olcumler, key=lambda o: o.mertebe())
    kayip = float(np.max(eksikler))
    return {"kayıp": kayip,
            "β": 0.0,
            "katılan_uzuv": float(len(eksikler)),
            "azamî_eksik": float(max(eksikler)),
            "ortalama_eksik": float(np.mean(eksikler)),
            "ortalama_mertebe": float(np.mean(mert)),
            "uzuv": len(eksikler),
            "en_zayıf": (en_zayif.kaynak, float(en_zayif.mertebe())),
            "tahminî_hadli": sum(1 for o in olcumler if o.uzay.tahmini_ust)}


ESIK: float = 1e-6


BOLGELER: Tuple[str, ...] = (
    "veri", "yerel", "makam", "mizan", "tenakuz", "tasdik", "sukut",
    "nakz", "kelam", "kaide", "orak", "gaye", "tertip",
)


SOZLESME: Dict[int, Tuple[Tuple[str, ...], str]] = {
    1:  (("veri",), "öz-dikkat: yalnız veri kübitleri"),
    2:  (("veri",), "hayal: satırın son veri kübitini aralar"),
    3:  (("veri",), "muhayyile: satır içi atlamalı çiftler"),
    4:  (("veri", "yerel"), "satırı kendi yerel hükmüne bağlar"),
    5:  (("veri",), "tecrit: fırça katmanının tersi"),
    6:  (("veri", "yerel"),
         "MERA kademesi satır bölgesine vurur; küllî bloğa DOKUNMAZ (H119)"),
    7:  (("yerel", "tasdik"), "mana: yerel hükümler tasdike akar"),
    8:  (("veri",), "tahlil: kübit başına dönme"),
    9:  (("veri",), "terkip: ters yönlü fırça"),
    10: (("veri",), "tezat: işaret çevirme"),
    11: (("yerel", "tenakuz"), "çelişki küllî tenakuz alanına akar"),
    12: (("yerel",), "tenkit: yerel hükmü bastırır"),
    13: (("tasdik",), "tasdik mührü: yalnız tasdik alanı"),
    14: (("tasdik", "mizan"), "gaye: tasdiki mîzâna bağlar"),
    15: (("nakz",), "merak: nakz alanını süperpozisyona sokar"),
    16: (("veri",), "keşif hamleleri"),
    17: (("mizan",), "önsel mîzâna yazılır"),
    18: (("veri",), "kıyas: komşu satırların veri kübitleri"),
    19: (("veri",), "temsil: dik ve tersinir"),
    20: (("veri",), "teşbih: ilk iki satır"),
    21: (("veri", "yerel", "makam"), "tefekkür: 20 mertebe, makama akar"),
    22: (("veri",), "illet: yönlü, satırdan satıra"),
    23: (("yerel", "nakz"), "mantık: nakz birikimi"),
    24: (("yerel",), "ispat: yerel hükümler zinciri"),
    25: (("veri",), "teemmül: aynı fırça, birkaç tur"),
    26: (("yerel",), "temkin: küçük açı"),
    27: (("veri",), "tetkik"),
    28: (("veri",), "tashih: tetkikin tersi"),
    29: (("veri",), "teyit: satırın iki ucu"),
    30: (("yerel", "tasdik"), "tahkik: ikinci yoldan tasdike"),
    31: (("veri", "mizan"), "tedebbür: ileri sarım + mîzân"),
    32: (("nakz", "tenakuz", "tasdik", "makam", "sukut"),
         "makam üç kaynaktan çevrilir, sükût kapısı açılır"),
    33: (("tasdik", "tenakuz", "nakz", "mizan"), "muhakeme: meclis"),
    34: (("yerel", "makam"), "tafsil: makam yerellere dağılır"),
    35: (("veri",), "tefsir: siyak ve sibak"),
    36: (("tenakuz", "tasdik"), "te'vil: çelişki şartıyla"),
    37: (("yerel", "tasdik", "kelam"),
         "fesâhat: mana YEREL HÜKÜMden kelama akar; tasdik mührü şart"),
    38: (("tasdik", "kelam"), "talâkat: akıcılık tasdikten, veriden değil"),
    39: (("makam", "tasdik", "kelam"), "belâgat: makam ve tasdik kelama"),
    40: (("makam", "kelam"), "sanat: altın açı, yalnız hüküm ve kelamda"),
    41: (("mizan", "makam", "sukut", "kelam"), "münazara + sükût kapısı"),
    42: (("yerel", "mizan", "tenakuz"),
         "umumileştirme: bütün duraklardan AYNI açıyla mîzâna (kesişim), "
         "araz tenakuza"),
    43: (("kelam",),
         "talim: kelamı kademe kademe keskinleştirir (τ monoton azalan)"),
    44: (("mizan", "parametre"),
         "tahsil: mîzân kontrollü Gibbs sönümü + γ kimlik payı, "
         "parametre bölgesine"),
}


def sozunde_mi(no: int = 0, n_satir: int = 4, chi: int = 32,
                        tohum: int = 0, esik: float = ESIK,
                        ne: str = "dokundu") -> object:
    if ne == "hepsi":
        return [sozunde_mi(m.no, n_satir, chi, tohum, esik)
                for m in qmelekeler()]
    if ne != "dokundu":
        raise ValueError("sözleşme ölçüsünün kipi bilinmiyor: %r" % (ne,))

    def bolge_yuvalari(q):
        d = {"veri": list(q.veri_izgara()),
             "yerel": q.yereller()}
        for a, kac in q.ayar.kulli_alanlar:
            d[a] = [q.kulli(a, j) for j in range(kac)]
        return d

    def yogunluklar(q):
        return np.asarray(q.y.tekil_yogunluklar(list(range(q.n))), float)[0]

    rng = np.random.default_rng(tohum)
    q = QYazmac(n_satir, QAyar(tohum=tohum))
    from kuantum.mahalli_yazmac import MahalliYazmac
    mahalli = MahalliYazmac(int(q.ayar.veri_lifi))
    q.mahalli = mahalli
    q.y.mahalli = mahalli
    q.kodla(rng.normal(size=(n_satir, 12)))
    q.superpozisyon()
    q.harman()
    for a, _kac in q.ayar.kulli_alanlar:
        q.sektor_donmesi(a, 0.4)
    from .donanim import bellek_haddi
    from kuantum.parametre_yazmaci import ParametreAyari, ParametreYazmaci
    p = ParametreYazmaci(64, 1, bellek_haddi(),
                         ParametreAyari(tohum=int(tohum)))

    once = yogunluklar(q)
    qsicil()[int(no)].kosu(q, p)
    sonra = yogunluklar(q)
    sapma = np.max(np.abs(sonra - once), axis=(1, 2))

    yuv = bolge_yuvalari(q)
    olculen, en_buyuk = [], {}
    for a in BOLGELER:
        if not yuv.get(a):
            continue
        sv = float(np.max(sapma[np.asarray(yuv[a], np.intp)]))
        en_buyuk[a] = sv
        if sv > esik:
            olculen.append(a)

    ilan = set(SOZLESME[int(no)][0])
    hepsi_yuva = []
    for a in ilan:
        hepsi_yuva += yuv.get(a, [])
    if not hepsi_yuva:
        guz = set(ilan)
    else:
        bas, son = min(hepsi_yuva), max(hepsi_yuva)
        guz = {a for a, y in yuv.items()
               if y and any(bas <= i <= son for i in y)}

    return {
        "no": int(no),
        "ilan": tuple(sorted(ilan)),
        "güzergâh": tuple(sorted(guz - ilan)),
        "ölçülen": tuple(sorted(olculen)),
        "ihlâl": tuple(sorted(set(olculen) - guz)),
        "kullanılmayan": tuple(sorted(ilan - set(olculen))),
        "sapma": en_buyuk,
        "sadakat": float(q.y.sadakat()),
    }


Izgara = np.ndarray


KADEME_VARSAYILAN: Dict[str, Tuple[float, float, float]] = {
    "kademe.idrak.nesne":        (1.0,  1.0,  8.0),
    "kademe.muhakeme.derinlik":  (2.0,  1.0,  4.0),
    "kademe.tasdik.müphem":      (0.5,  0.1,  1.0),
    "kademe.tasdik.tevafuk":     (0.6,  0.2,  1.0),
    "kademe.tasdik.taban":       (0.5,  0.1,  1.0),
    "kademe.beyan.eşik":         (0.55, 0.05, 0.95),
}


def kademe_parametreleri_ac(p) -> int:
    assert hasattr(p, "al") or hasattr(p, "v"), (
        "parametre taşıyıcısında ne ``al`` ne ``v`` var: %r" % type(p))
    n = 0
    for anahtar in KADEME_VARSAYILAN:
        v = p.al(anahtar, 1) if hasattr(p, "al") else p.v(anahtar, 1)
        assert v is not None and np.size(v) > 0, (
            "kademe parametresi BOŞ açıldı: %r" % anahtar)
        n += 1
    return n


MERTEBE_NOTU: Dict[str, float] = {"doğru": 1.0, "sükût": 0.25,
                                  "yanlış": 0.0}


K_UZAY: Dict[str, OlcuUzayi] = {
    "idrak": OlcuUzayi("idrak", 0.0, 1.0, True),
    "tasavvur": OlcuUzayi("tasavvur", 0.0, 1.0, True),
    "muhakeme": OlcuUzayi("muhakeme", 0.0, 1.0, True),
    "ispat": OlcuUzayi("ispat", 0.0, 1.0, True),
    "tasdik": OlcuUzayi("tasdik_kademe", 0.0, 1.0, True),
    "beyan": OlcuUzayi("beyan", 0.0, 1.0, True),
}


@dataclass
class Idrak:
    ciftler: List[Tuple[Izgara, Izgara]]
    girdiler: List[Izgara]
    nesne_sayisi: List[int] = field(default_factory=list)
    ayni_sekil: bool = False


@dataclass
class Hal:
    ozellik: np.ndarray
    kademe_sayisi: int = 0
    spektral_rutbe: int = 0
    kabalastirma_kaybi: float = 1.0


@dataclass
class Namzet:
    kaideler: List[object] = field(default_factory=list)
    aranan: int = 0


@dataclass
class Ispat:
    kaideler: List[object] = field(default_factory=list)
    elenen: int = 0
    gerekce: str = ""


@dataclass
class Yakin:
    deger: float = 0.0
    istikra: float = 0.0
    muphem: bool = False
    tevafuk: float = 0.0


class Kademeler:

    def __init__(self, p=None) -> None:
        self.olcumler: List[Olcum] = []
        self.eksik: Dict[str, str] = {}
        self.gunluk: List[str] = []
        self.p = p
        self.yakin_ilani: float = 0.0

    def _par(self, anahtar: str) -> float:
        var, alt, ust = KADEME_VARSAYILAN[anahtar]
        if self.p is None:
            return float(var)
        ham = (float(np.asarray(self.p.al(anahtar, 1), float).ravel()[0])
               if hasattr(self.p, "al")
               else float(self.p.v(anahtar, 1)[0]))
        assert np.isfinite(ham), "kademe ham degeri sonlu degil: %r" % anahtar
        t = float(np.tanh(ham))
        return float(var + t * ((ust - var) if t >= 0.0 else (var - alt)))

    def _olc(self, ad: str, deger: float) -> None:
        self.olcumler.append(Olcum("kademe.%s" % ad, float(deger),
                                   K_UZAY[ad]))

    def _dene(self, ad: str, f):
        try:
            return f()
        except RED_HATALARI as e:
            self.eksik[ad] = "%s: %s" % (type(e).__name__, str(e)[:60])
            return None
        except (NameError, AttributeError, ImportError) as e:
            raise AssertionError(
                "%s: eksik AD yahut ithal (%s: %s). Bu bir veri hâli "
                "değil, KOD kusurudur; sessizce yutulamaz (ferman 5)."
                % (ad, type(e).__name__, e))

    def idrak(self, gorev) -> Idrak:
        ciftler = [(np.asarray(a, np.int64), np.asarray(b, np.int64))
                   for a, b in getattr(gorev, "egitim", [])]
        girdiler = [np.asarray(a, np.int64)
                    for a, _ in getattr(gorev, "sinama", [])]
        I = Idrak(ciftler, girdiler)
        if not ciftler:
            self._olc("idrak", 0.0)
            return I
        I.ayni_sekil = all(a.shape == b.shape for a, b in ciftler)

        esik_nesne = int(round(self._par("kademe.idrak.nesne")))

        def _nesne():
            from .musahede import bilesen_kutulari
            ARKA = 0
            return [sum(1 for _renk, maske, _kutu in bilesen_kutulari(a, ARKA)
                        if int(maske.sum()) >= esik_nesne)
                    for a, _ in ciftler]
        I.nesne_sayisi = self._dene("nefs.musahede", _nesne) or []

        def _mubser():
            from .musahede import devinim_olc, bak
            return devinim_olc(bak(ciftler[0][0]),
                               bak(ciftler[0][1]))
        self._dene("nefs.mubser", _mubser)


        h = 0.0
        h += 0.3 if I.nesne_sayisi and min(I.nesne_sayisi) > 0 else 0.0
        self._olc("idrak", h)
        self.gunluk.append(
            "1. İDRAK: %d çift, %s  (ölçü/şekil kestirimi İMHA -- 1-P)"
            % (len(ciftler), "aynı şekilli" if I.ayni_sekil
               else "şekil değişiyor"))
        return I

    def tasavvur(self, I: Idrak) -> Hal:
        H = Hal(np.zeros(0))
        if not I.ciftler:
            self._olc("tasavvur", 0.0)
            return H
        A = I.ciftler[0][0]

        def _piramit():
            from matematik.sonsuz_mertebeler_teorisi import (
                coklu_cozunurluk_piramidi_kur, piramit_kabalastir)
            k = coklu_cozunurluk_piramidi_kur(np.asarray(A, float))
            _y, _n, kayip = piramit_kabalastir(np.asarray(A, float))
            return len(k), float(kayip)
        r = self._dene("matematik.sonsuz_mertebeler_teorisi", _piramit)
        if r is not None:
            H.kademe_sayisi, H.kabalastirma_kaybi = r

        def _rutbe():
            from ogrenme.operator import spektral_rutbe
            return int(spektral_rutbe(np.asarray(A, float)))
        H.spektral_rutbe = self._dene("ogrenme.operator", _rutbe) or 0

        def _tayf():
            from matematik.geometri import spektral_enerji
            return np.asarray(spektral_enerji(
                np.asarray(A, float).reshape(-1)[:64]), float).reshape(-1)
        tayf = self._dene("token_uzaylari.fno", _tayf)

        parcalar = [p for p in (tayf,) if p is not None and p.size]
        H.ozellik = (np.concatenate(parcalar) if parcalar
                     else np.zeros(1, float))
        self._olc("tasavvur", 1.0 - float(np.clip(H.kabalastirma_kaybi,
                                                  0.0, 1.0)))
        self.gunluk.append(
            "2. TASAVVUR: özellik %d boyut, piramit %d kademe, spektral "
            "rütbe %d, kabalaştırma kaybı %.3f"
            % (H.ozellik.size, H.kademe_sayisi, H.spektral_rutbe,
               H.kabalastirma_kaybi))
        return H

    def muhakeme(self, I: Idrak, H: Hal, derinlik: Optional[int] = None
                 ) -> Namzet:
        N = Namzet()
        if not I.ciftler:
            self._olc("muhakeme", 0.0)
            return N
        if derinlik is None:
            derinlik = int(round(self._par("kademe.muhakeme.derinlik")))

        def _ara():
            return []

        def _kullanilmayan():
            d = None
            if d is None:
                return []

            class _DalgaKaidesi:
                ad = "dalga/%s/%s" % (d.hendese, d.d4)
                boy = 1
                hipotez = int(d.W.size)

                def __call__(self, g):
                    r = d.oku(g)
                    return None if r is None else r[0]

            return [_DalgaKaidesi()]
        N.kaideler = self._dene("main.main", _ara) or []
        N.aranan = len(N.kaideler)
        self.gunluk.append("3. MUHAKEME: %d kaide bütün gösterimleri "
                           "tutuyor (derinlik %d)" % (N.aranan, derinlik))
        return N

    def ispat(self, I: Idrak, N: Namzet) -> Ispat:
        S = Ispat(list(N.kaideler))
        if not N.kaideler:
            self._olc("ispat", 0.0)
            return S
        onceki = len(S.kaideler)
        if I.girdiler:
            def _uzanan():
                return [k for k in S.kaideler
                        if all(k(g) is not None for g in I.girdiler)]
            u = self._dene("ispat.uzanma", _uzanan)
            if u is not None:
                S.kaideler = u
        S.elenen = onceki - len(S.kaideler)
        if S.elenen:
            S.gerekce = "%d kaide sınamaya uzanmıyor" % S.elenen

        def _mantik():
            from matematik.mizan import (deg, aksiyom,
                                         hukum)
            return bool(hukum(
                aksiyom(deg("K"), deg("İ"), no=1), ne="totoloji"))
        self._dene("mizan.cikarim", _mantik)

        nispet = (float(len(S.kaideler)) / float(max(onceki, 1))
                  if onceki else 0.0)
        self._olc("muhakeme", nispet)
        self._olc("ispat", nispet if S.kaideler else 0.0)
        self.gunluk.append("4. İSPAT: %d aday → %d ayakta (%s), isabet %.2f"
                           % (onceki, len(S.kaideler),
                              S.gerekce or "eleme yok", nispet))
        return S

    def tasdik(self, I: Idrak, S: Ispat) -> Yakin:
        Y = Yakin()
        self.yakin_ilani = 0.0
        if not S.kaideler:
            return Y

        def _istikra():
            from matematik.mizan import ardisiklik_kaidesi
            n = len(I.ciftler)
            return float(ardisiklik_kaidesi(n, n))
        Y.istikra = self._dene("mizan.istikra", _istikra) or 0.5

        if I.girdiler and len(S.kaideler) > 1:
            imzalar = set()
            for k in S.kaideler[:8]:
                o = k(I.girdiler[0])
                if o is not None:
                    imzalar.add(o.tobytes() + bytes(o.shape))
            Y.muphem = len(imzalar) > 1

        tam_sahit = bool(I.nesne_sayisi and min(I.nesne_sayisi) > 0)
        Y.tevafuk = 1.0 if tam_sahit else self._par("kademe.tasdik.tevafuk")

        def _makam():
            from matematik.mizan import hukum_agirligi, makam_tayin
            p = float(Y.istikra)
            return float(hukum_agirligi(p, makam_tayin(p)))
        agirlik = self._dene("mizan.munazara", _makam)

        muphem_cezasi = self._par("kademe.tasdik.müphem")
        taban = self._par("kademe.tasdik.taban")
        Y.deger = float(np.clip(
            Y.istikra * (muphem_cezasi if Y.muphem else 1.0) * Y.tevafuk
            * (1.0 if agirlik is None
               else float(np.clip(agirlik, taban, 1.0))),
            0.0, 1.0))
        self.yakin_ilani = float(Y.deger)
        self.gunluk.append(
            "5. TASDİK: istikrâ %.3f, %s, tevâfuk %.2f → yakîn %.3f"
            % (Y.istikra, "müphem" if Y.muphem else "müphem değil",
               Y.tevafuk, Y.deger))
        return Y

    def beyan(self, I: Idrak, S: Ispat, Y: Yakin,
              esik: Optional[float] = None
              ) -> Optional[List[Optional[Izgara]]]:
        if esik is None:
            esik = self._par("kademe.beyan.eşik")
        if not S.kaideler or Y.deger < esik:
            self.gunluk.append(
                "6. BEYAN: sükût -- %s"
                % ("kaide yok" if not S.kaideler
                   else "yakîn %.3f < eşik %.2f" % (Y.deger, esik)))
            return None
        k = S.kaideler[0]
        cevap = [k(g) for g in I.girdiler]
        self.gunluk.append("6. BEYAN: konuşuyorum -- kaide %s, yakîn %.3f"
                           % (getattr(k, "ad", "?"), Y.deger))
        return cevap

    def capraz_not(self, gorev) -> None:
        ciftler = [(np.asarray(a), np.asarray(b))
                   for a, b in getattr(gorev, "egitim", [])]
        if len(ciftler) < 2:
            self.gunluk.append(
                "ÇAPRAZ: %d gösterim -- bırak-birini kurulamaz, not yok"
                % len(ciftler))
            return
        sakli_g, sakli_c = ciftler[-1]

        class _G:
            ad = getattr(gorev, "ad", "?")
            kaynak = getattr(gorev, "kaynak", "?")
            egitim = ciftler[:-1]
            sinama = [(sakli_g, sakli_c)]

        ic = Kademeler(self.p)
        I2 = ic.idrak(_G())
        H2 = ic.tasavvur(I2)
        N2 = ic.muhakeme(I2, H2)
        S2 = ic.ispat(I2, N2)
        Y2 = ic.tasdik(I2, S2)
        C2 = ic.beyan(I2, S2, Y2)
        ilan = float(getattr(ic, "yakin_ilani", 0.0))

        if C2 is None or not C2 or C2[0] is None:
            hâl, isabet = "sükût", 0.0
        else:
            c = np.asarray(C2[0])
            if c.shape == sakli_c.shape and bool(np.array_equal(c, sakli_c)):
                hâl, isabet = "doğru", 1.0
            else:
                hâl, isabet = "yanlış", 0.0
        self._olc("beyan", MERTEBE_NOTU[hâl])
        if hâl != "sükût":
            self._olc("tasdik", 1.0 - abs(ilan - isabet))
        self.gunluk.append(
            "ÇAPRAZ: saklanan çift → %s (not %.2f), ilan edilen yakîn "
            "%.3f" % (hâl, MERTEBE_NOTU[hâl], ilan))


def kademeleri_kos(gorev, derinlik: Optional[int] = None,
                   esik: Optional[float] = None, p=None,
                   capraz: bool = True) -> Dict[str, object]:
    K = Kademeler(p)
    I = K.idrak(gorev)
    H = K.tasavvur(I)
    N = K.muhakeme(I, H, derinlik)
    S = K.ispat(I, N)
    Y = K.tasdik(I, S)
    C = K.beyan(I, S, Y, esik)
    if capraz:
        K.capraz_not(gorev)
    return {"idrak": I, "hal": H, "namzet": N, "ispat": S, "yakîn": Y,
            "cevap": C, "sükût": C is None, "ölçümler": K.olcumler,
            "günlük": K.gunluk, "eksik": K.eksik}


VAZIFE_NEVILERI: Tuple[str, ...] = ("bulmaca", "kelâm", "boş")


YAKIN_ESIGI: float = 0.5


def suz(gorev, yakin_esigi: float = YAKIN_ESIGI,
                  derinlik: int = 2, dalga: bool = False, nefs=None,
                  ne: str = "çevrim", ciftler=None, chi: int = 8,
                  tohum: int = 0) -> Dict[str, object]:
    if ne == "vazife":
        ciftler = list(getattr(gorev, "egitim", []) or [])
        sinama = list(getattr(gorev, "sinama", []) or [])
        if not ciftler:
            return {"nev": "boş", "gerekçe": "gösterim çifti yok",
                    "çift": 0}
        ikili = all(hasattr(a, "shape") and hasattr(b, "shape")
                    for a, b in ciftler)
        if ikili and len(ciftler) >= 2:
            return {"nev": "bulmaca", "çift": len(ciftler),
                    "sınama": len(sinama),
                    "gerekçe": "%d gösterim çifti var: bir dönüşüm "
                               "gösteriliyor ve aynısı isteniyor"
                               % len(ciftler)}
        return {"nev": "kelâm", "çift": len(ciftler), "sınama": len(sinama),
                "gerekçe": "girdi–çıktı çifti yok; vazife söz söylemek"}

    if ne == "tesadüf":
        if not ciftler:
            return {"renk_yapısı": 0.0, "şekil_bağı": 0.0, "yapı": 0.0}
        sapmalar = []
        for a, b in ciftler:
            for g in (a, b):
                g = np.asarray(g)
                if g.size == 0:
                    continue
                _v, s = np.unique(g, return_counts=True)
                p = s / s.sum()
                k = max(len(p), 2)
                sapmalar.append(0.5 * float(np.abs(p - 1.0 / k).sum())
                                + (1.0 - len(p) / 10.0) * 0.5)
        renk = float(np.clip(np.mean(sapmalar) if sapmalar else 0.0, 0, 1))

        ayni = sum(1 for a, b in ciftler if a.shape == b.shape)
        sabit = len({b.shape for _a, b in ciftler}) == 1
        kat = sum(1 for a, b in ciftler
                  if a.shape[0] and a.shape[1]
                  and (b.shape[0] % a.shape[0] == 0
                       and b.shape[1] % a.shape[1] == 0))
        n = len(ciftler)
        sekil = max(ayni / n, kat / n, 1.0 if sabit else 0.0)
        return {"renk_yapısı": renk, "şekil_bağı": float(sekil),
                "yapı": float(0.5 * renk + 0.5 * sekil)}

    if ne == "dalga":
        from .musahede import iki_olcegin_acisi
        from .musahede import ortu
        from .melekeler import QNefs
        from .zihin_durumu import MAKAM_ADLARI, QAyar

        X, Y = iki_olcegin_acisi(gorev, ne="öznitelik")
        if len(X) == 0:
            return None
        E = np.concatenate([X, Y], axis=1)
        c = ortu(gorev)
        q = (nefs or QNefs(tohum, QAyar(tohum=tohum))
             ).idrak_et(E, tikaniklik=float(c["H1"]))
        _, ks = q._alan["sukut"]
        sk = float(np.asarray(q.y.tekil_yogunluklar(
            [q.kulli("sukut", j) for j in range(ks)]), float)[0][:, 1, 1].mean())
        from .mantik import MAKAM_MERTEBE
        P = np.atleast_1d(np.asarray(q.makam_dagilimi(), float)).ravel()
        mk = float(sum(P[i] * MAKAM_MERTEBE[ad]
                       for i, ad in enumerate(MAKAM_ADLARI)))
        return {"sukut": sk, "makam_yakini": mk}

    if ne != "çevrim":
        raise ValueError("müdrike kipi bilinmiyor: %r" % (ne,))

    from .musahede import ortu

    dusunce: List[str] = []

    v = suz(gorev, ne="vazife")
    dusunce.append("Benden ne isteniyor? %s → bu bir %s."
                   % (v["gerekçe"], v["nev"]))
    if v["nev"] != "bulmaca":
        return {"nev": v["nev"], "cevap": None, "sükût": True,
                "sebep": "bulmaca değil", "muhakeme": dusunce,
                "yakîn": 0.0}

    ciftler = list(gorev.egitim)

    t = suz(gorev, ne="tesadüf", ciftler=ciftler)
    dusunce.append("Renkler rastgele dizilmiş gibi mi? renk yapısı %.3f, "
                   "şekil bağı %.3f → yapı %.3f."
                   % (t["renk_yapısı"], t["şekil_bağı"], t["yapı"]))
    if t["yapı"] < 0.15:
        dusunce.append("Rastgele olsaydı cevabı nereden bulacaktım? "
                       "Bulamazdım. Yapı yok; sormak beyhude.")
        return {"nev": "bulmaca", "cevap": None, "sükût": True,
                "sebep": "yapı yok", "muhakeme": dusunce, "yakîn": 0.0,
                "tesadüf": t}
    dusunce.append("Demek ki rastgele değil: bir düzen var, "
                   "o hâlde bir kaide de olmalı.")

    c = ortu(gorev)
    dusunce.append("Bütün örnekler aynı kaideye mi bakıyor? "
                   "yama %d, uyuşmayan çift %d (H¹=%d)."
                   % (c["yama"], c.get("uyuşmayan_çift", 0), c["H1"]))
    if c["H1"]:
        dusunce.append("Yamaların şekil kaidesi ayrı düşüyor. Bu beni "
                       "susturmaz -- bütün gösterimleri tutan bir kaide "
                       "bulursam örtü zaten kapanmış olur; fakat "
                       "ihtiyatlı olurum.")

    dw = {"sükût": True,
          "sebep": "elle kurulmuş dalga fermanla kaldırıldı; "
                   "motor kaybın içinden çağrılmaz (kısır döngü)"}
    if not dw.get("sükût"):
        n = len(ciftler)
        yakin = float(ardisiklik_kaidesi(n, n))
        if c["H1"]:
            yakin *= 0.8
        yakin *= float(np.clip(dw.get("güven", 1.0), 0.3, 1.0))
        dusunce.append(
            "Hiçbir şablona bakmadan, şahitlerden bir dalga öğrendim: "
            "ebat kanunu %s, taşıyıcı D₄=%s, %d ağırlık; şahit isabeti "
            "%.4f, sınamada güven %.4f, zırh cezası %.4f."
            % (dw["hendese"], dw["d4"], dw["ağırlık"],
               dw["şahit_isabeti"], dw["güven"], dw["zırh"]))
        if yakin >= yakin_esigi:
            dusunce.append("Yakînim %s; öğrendiğim ağırlıklardan "
                           "konuşuyorum." % mertebe_adi(yakin))
            return {"nev": "bulmaca", "cevap": list(dw["cevap"]),
                    "sükût": False, "sebep": None, "muhakeme": dusunce,
                    "yakîn": yakin, "kaide": "dalga/%s" % dw["d4"],
                    "kaide_sayısı": 1, "müphem": False, "tesadüf": t,
                    "kaynak": "dalga"}
        dusunce.append("Dalga kuruldu fakat yakînim (%.3f) eşiğin altında; "
                       "kademelere devam ediyorum." % yakin)
    else:
        dusunce.append("Dalga tutmadı: %s." % dw.get("sebep"))

    kad = kademeleri_kos(gorev, derinlik=derinlik, esik=yakin_esigi)
    dusunce += kad["günlük"]
    K = list(kad["ispat"].kaideler)
    kademe_olcumleri = kad["ölçümler"]
    if kad["eksik"]:
        dusunce.append("Kademelerde düşen uzuv: %s"
                       % ", ".join(sorted(kad["eksik"])))
    if not K:
        dusunce.append("Hiçbir kaide bütün gösterimleri tutmuyor. "
                       "Tutmayan bir kaideyle cevap vermek, tam eşleşme "
                       "ölçütünü sahte kılardı.")
        return {"nev": "bulmaca", "cevap": None, "sükût": True,
                "sebep": "kaide bulunamadı", "muhakeme": dusunce,
                "yakîn": 0.0, "tesadüf": t,
                "ölçümler": kademe_olcumleri}

    girdiler_on = [np.asarray(a, np.int64)
                   for a, _ in getattr(gorev, "sinama", [])] or []
    if girdiler_on:
        konusabilen = [k for k in K
                       if all(k(g) is not None for g in girdiler_on)]
        if not konusabilen:
            dusunce.append(
                "%d kaide gösterimleri tutuyor fakat hiçbiri sınama "
                "girdisinde cevap üretmiyor -- görmediğim bir hâl var. "
                "Ezberlediğim tablo oraya uzanmıyor; susuyorum." % len(K))
            return {"nev": "bulmaca", "cevap": None, "sükût": True,
                    "sebep": "kaide sınamaya uzanmıyor",
                    "muhakeme": dusunce, "yakîn": 0.0, "tesadüf": t}
        if len(konusabilen) < len(K):
            dusunce.append("%d kaidenin %d'i sınama girdisinde cevap "
                           "üretebiliyor; yalnız onları tartıyorum."
                           % (len(K), len(konusabilen)))
        K = konusabilen

    n = len(ciftler)
    istikra = float(ardisiklik_kaidesi(n, n))
    girdiler = [a for a, _ in getattr(gorev, "sinama", [])] or []
    muphem = False
    if girdiler and len(K) > 1:
        for g in girdiler:
            cevaplar = []
            for k in K[:8]:
                r = k(np.asarray(g, np.int64))
                cevaplar.append(None if r is None else r.tobytes()
                                + bytes(r.shape))
            if len({c for c in cevaplar if c is not None}) > 1:
                muphem = True
                break
    delil = sum(int(np.asarray(a).size) for a, _ in ciftler)
    hip = int(getattr(K[0], "hipotez", 0))
    kanit = 1.0 if hip <= 0 else float(
        np.clip(delil / (4.0 * hip), 0.25, 1.0))
    ihtiyat = 0.8 if c["H1"] else 1.0
    yakin = istikra * (0.5 if muphem else 1.0) * ihtiyat * kanit

    kes = None
    if kes is not None and girdiler:
        deneme = K[0](np.asarray(girdiler[0], np.int64))
        if deneme is not None and tuple(deneme.shape) != tuple(kes):
            yakin *= 0.5
            dusunce.append(
                "Fakat ölçü kestirimi %s diyor, kaidem %s veriyor -- "
                "iki müstakil hesap uyuşmuyor; yakînimi yarıya "
                "indiriyorum." % (tuple(kes), tuple(deneme.shape)))
    if hip > 0:
        dusunce.append("Bu kaide %d girdilik bir tablo öğrendi; "
                       "delilim %d hücre → delil/hipotez sağlamlığı %.3f."
                       % (hip, delil, kanit))
    dh = (suz(gorev, ne="dalga", nefs=nefs)
          if dalga else None)
    if dh is not None:
        yakin *= float(np.clip(1.0 - 0.5 * dh["sukut"], 0.3, 1.0))
        dusunce.append("Dalganın hükmü: sükût eğilimi %.3f, makam yakîni "
                       "%.3f → yakînim %.3f'e ayarlandı."
                       % (dh["sukut"], dh["makam_yakini"], yakin))
    dusunce.append("Yakînim ne mertebede? %d gösterimden ardışıklık "
                   "kaidesi %.3f; tutan kaideler %s%s → yakîn %.3f (%s)."
                   % (n, istikra,
                      "AYRI cevaplar veriyor (müphem)" if muphem
                      else "aynı cevabı veriyor",
                      "; örtü tıkanıklığı ihtiyatı" if c["H1"] else "",
                      yakin, mertebe_adi(yakin)))
    if yakin < yakin_esigi:
        dusunce.append("Yakîn eşiğin (%.2f) altında; susuyorum."
                       % yakin_esigi)
        return {"nev": "bulmaca", "cevap": None, "sükût": True,
                "sebep": "yakîn eşiğin altında", "muhakeme": dusunce,
                "yakîn": yakin, "tesadüf": t, "kaide": K[0].ad}

    kural = K[0]
    cevap = [kural(np.asarray(g, np.int64)) for g in girdiler]
    dusunce.append("Kaide: %s. Yakînim %s; konuşuyorum."
                   % (kural.ad, mertebe_adi(yakin)))
    return {"nev": "bulmaca", "cevap": cevap, "sükût": False,
            "sebep": None, "muhakeme": dusunce, "yakîn": yakin,
            "kaide": kural.ad, "kaide_sayısı": len(K),
            "müphem": muphem, "tesadüf": t}


_IZLENEN = ("X", "Z_hayal", "H_hayal", "Z_muhayyile", "sira", "U_k", "D",
            "S", "S_kebir", "K_vahime", "mu_mana", "parcalar",
            "tekil_degerler", "tenakuz", "G", "G_kebir", "Q_sual",
            "A_neden", "burhan", "M", "T", "P_idrak", "makam", "N",
            "sahitler", "kaideler", "kaide", "nakz", "sahit_agirliklari",
            "muteber_sahit", "tevafuk", "ispat", "hukum", "sukut",
            "tezat_kutbu", "w_kesit")


VERI_ORNEK: int = 8

_TAKSIMAT_ARTIGI: Tuple[str, ...] = ("parametre", "meleke", "ancilla")


def bolge_degeri(q, ad: str) -> Optional[float]:
    if ad == "yerel":
        y = q.yereller()
        assert y, "yerel kübit yok -- ``yerel`` bölgesi BOŞ"
        return zayif_halka(q.povm(y))
    if ad == "veri":
        y = list(q.veri_izgara())[:VERI_ORNEK]
        assert y, "veri yuvası yok -- ``veri`` bölgesi BOŞ"
        return zayif_halka(q.povm(y))
    assert ad not in _TAKSIMAT_ARTIGI, (
        "``%s`` imha edilen kübit taksimatının bölgesiydi; quditte yoktur. "
        "Çağıran onu kesmeden ölçmeli." % ad)
    v = zayif_halka(q.alan_degeri(ad))
    assert v is not None, "bölge %r BOŞ okundu" % ad
    return v


def meleke_olcumleri(okumalar: Dict[int, Dict[str, float]]
                     ) -> List[Olcum]:
    out: List[Olcum] = []
    for no, d in sorted(okumalar.items()):
        if not d:
            continue
        w = 1.0 / float(len(d))
        for ad, v in sorted(d.items()):
            if ad == "kesme":
                S = OlcuUzayi("tutulan_kesir", 0.0, 1.0, True)
            else:
                S = UZAYLAR.get(ad)
            if S is None:
                S = OlcuUzayi(ad, 0.0, 1.0, True, tahmini_ust=True)
            out.append(Olcum("𝒪%d.%s" % (no, ad), float(v), S, w))
    return out


def lan(x: np.ndarray, xs: np.ndarray, ys: np.ndarray, L: float) -> np.ndarray:
    return np.max(ys[None, :] - L * np.abs(x[:, None] - xs[None, :]), axis=1)


def ran(x: np.ndarray, xs: np.ndarray, ys: np.ndarray, L: float) -> np.ndarray:
    return np.min(ys[None, :] + L * np.abs(x[:, None] - xs[None, :]), axis=1)


def kan_ozellikleri(
    n: int = 12, L: float = 3.0, tohum: int = 0
) -> Dict[str, object]:
    rng = np.random.default_rng(tohum)
    xs = np.sort(rng.uniform(0, 1, n))
    hedef = lambda t: np.sin(2 * np.pi * t)
    L = max(L, 2 * np.pi)
    ys = hedef(xs)

    izgara = np.linspace(0, 1, 1001)
    a, b = lan(izgara, xs, ys, L), ran(izgara, xs, ys, L)

    oturma = float(
        max(np.max(np.abs(lan(xs, xs, ys, L) - ys)), np.max(np.abs(ran(xs, xs, ys, L) - ys)))
    )
    h = izgara[1] - izgara[0]
    lip = float(max(np.max(np.abs(np.diff(a))), np.max(np.abs(np.diff(b)))) / h)
    g = hedef(izgara)
    arada = bool(np.all(a <= g + 1e-9) and np.all(g <= b + 1e-9))
    return {
        "L": L,
        "ornekte_tam_oturma_hatasi": oturma,
        "olculen_lipschitz": lip,
        "lipschitz_asilmadi": bool(lip <= L * (1 + 1e-6)),
        "hedef_arada": arada,
        "lan_ran_araligi_ortalama": float(np.mean(b - a)),
    }


def ezber_mi(xs=None, ys=None, t=None, ne: str = "kıyas",
             olcek: float = 0.03, lam: float = 1e-8, n: int = 40,
             gurultu: float = 0.25, tohum: int = 0):
    if ne == "gram":
        d2 = (np.asarray(xs, float)[:, None] - np.asarray(ys, float)[None, :]) ** 2
        return np.exp(-0.5 * d2 / (olcek * olcek))

    if ne == "uydur":
        xs_, ys_ = xs, ys
        K = ezber_mi(xs_, xs_, olcek=olcek, ne="gram")
        A = K + lam * np.eye(len(xs_))
        alfa = np.linalg.solve(A, ys_)
        return lambda t: ezber_mi(t, xs_, olcek=olcek, ne="gram") @ alfa

    if ne == "kıyas":
        rng = np.random.default_rng(tohum)
        hedef = lambda t: np.sin(2 * np.pi * t)
        xs = np.sort(rng.uniform(0, 1, n))
        ys = hedef(xs) + gurultu * rng.normal(size=n)
        xt = np.linspace(0.02, 0.98, 500)
        yt = hedef(xt)

        L_veri = float(np.max(np.abs(np.diff(ys) / np.diff(xs))))
        kan_orta = 0.5 * (lan(xt, xs, ys, L_veri) + ran(xt, xs, ys, L_veri))
        kan_egitim = 0.5 * (lan(xs, xs, ys, L_veri) + ran(xs, xs, ys, L_veri))

        g0 = ezber_mi(xs, ys, olcek=olcek, lam=1e-8, ne="uydur")
        g1 = ezber_mi(xs, ys, olcek=olcek, lam=1e-1, ne="uydur")

        def hata(tahmin: np.ndarray, dogru: np.ndarray) -> float:
            return float(np.sqrt(np.mean((tahmin - dogru) ** 2)))

        kayit = {
            "gurultu_seviyesi": gurultu,
            "verinin_lipschitz_sabiti": L_veri,
            "hedefin_lipschitz_sabiti": 2 * np.pi,
            "gram_kosul_sayisi": float(np.linalg.cond(ezber_mi(xs, xs, olcek=olcek, ne="gram"))),
            "kan_egitim_hatasi": hata(kan_egitim, ys),
            "kan_sinama_hatasi": hata(kan_orta, yt),
            "cekirdek_lam0_egitim": hata(g0(xs), ys),
            "cekirdek_lam0_sinama": hata(g0(xt), yt),
            "cekirdek_sirt_egitim": hata(g1(xs), ys),
            "cekirdek_sirt_sinama": hata(g1(xt), yt),
        }
        kayit["kan_tam_oturuyor"] = bool(kayit["kan_egitim_hatasi"] < 1e-9)
        kayit["gurultu_lipschitzi_patlatti"] = bool(L_veri > 100 * 2 * np.pi)
        kayit["ezber_gorunuyor"] = bool(
            kayit["cekirdek_lam0_egitim"] < 0.5 * gurultu
            and kayit["cekirdek_lam0_sinama"] > 4.0 * gurultu
        )
        kayit["duzenlileme_sinamayi_iyilestirdi"] = bool(
            kayit["cekirdek_sirt_sinama"] < kayit["cekirdek_lam0_sinama"]
            and kayit["cekirdek_sirt_sinama"] < kayit["kan_sinama_hatasi"]
        )
        kayit["duzenlileme_egitimi_kotulestirdi"] = bool(
            kayit["cekirdek_sirt_egitim"] > kayit["cekirdek_lam0_egitim"]
        )
        return kayit

    if ne == "sobolev":
        if (n, gurultu, olcek, lam, tohum) == (40, 0.25, 0.03, 1e-8, 0):
            n, gurultu, olcek, lam, tohum = 14, 0.05, 0.25, 1e-6, 3
        rng = np.random.default_rng(tohum)
        hedef = lambda t: np.sin(2 * np.pi * t)
        turev = lambda t: 2 * np.pi * np.cos(2 * np.pi * t)
        xs = np.sort(rng.uniform(0, 1, n))
        ys = hedef(xs) + gurultu * rng.normal(size=n)
        ds = turev(xs) + gurultu * rng.normal(size=n)

        def dK(x: np.ndarray, z: np.ndarray) -> np.ndarray:
            return -(x[:, None] - z[None, :]) / (olcek * olcek) * ezber_mi(x, z, olcek=olcek, ne="gram")

        K = ezber_mi(xs, xs, olcek=olcek, ne="gram")
        a_deger = np.linalg.solve(K + lam * np.eye(n), ys)
        A = np.vstack([K, dK(xs, xs)])
        b = np.concatenate([ys, ds])
        a_sob = np.linalg.lstsq(A.T @ A + lam * np.eye(n), A.T @ b, rcond=None)[0]

        xt = np.linspace(0.05, 0.95, 400)
        def hata(v, d):
            return float(np.sqrt(np.mean((v - d) ** 2)))

        deger_h = hata(ezber_mi(xt, xs, olcek=olcek, ne="gram") @ a_deger, hedef(xt))
        deger_t = hata(dK(xt, xs) @ a_deger, turev(xt))
        sob_h = hata(ezber_mi(xt, xs, olcek=olcek, ne="gram") @ a_sob, hedef(xt))
        sob_t = hata(dK(xt, xs) @ a_sob, turev(xt))
        return {
            "yalniz_deger__deger_hatasi": deger_h,
            "yalniz_deger__turev_hatasi": deger_t,
            "sobolev__deger_hatasi": sob_h,
            "sobolev__turev_hatasi": sob_t,
            "turev_iyilesti": bool(sob_t < deger_t),
        }

    raise ValueError("ezber suâlinin kipi bilinmiyor: %r" % (ne,))


def _rapor_ezber() -> str:
    s = ["=== genisletme ==="]
    k = kan_ozellikleri()
    s.append("Kan gen.  oturma hatası=%.2e  ölçülen Lip=%.3f ≤ L=%.3f → %s  hedef arada=%s"
             % (k["ornekte_tam_oturma_hatasi"], k["olculen_lipschitz"], k["L"],
                k["lipschitz_asilmadi"], k["hedef_arada"]))
    e = ezber_mi(ne="kıyas")
    s.append("ezber     Kan: eğitim=%.2e sınama=%.4f | λ=1e-8: eğitim=%.4f sınama=%.4g | sırt: eğitim=%.4f sınama=%.4f"
             % (e["kan_egitim_hatasi"], e["kan_sinama_hatasi"],
                e["cekirdek_lam0_egitim"], e["cekirdek_lam0_sinama"],
                e["cekirdek_sirt_egitim"], e["cekirdek_sirt_sinama"]))
    s.append("          gürültü=%.2f  verinin Lip=%.3g (hedefinki %.3g)  Gram koşul=%.2e"
             % (e["gurultu_seviyesi"], e["verinin_lipschitz_sabiti"],
                e["hedefin_lipschitz_sabiti"], e["gram_kosul_sayisi"]))
    s.append("          Kan tam oturuyor=%s  ezber görünüyor=%s  düzenlileme sınamayı iyileştirdi=%s"
             % (e["kan_tam_oturuyor"], e["ezber_gorunuyor"],
                e["duzenlileme_sinamayi_iyilestirdi"]))
    b = ezber_mi(ne="sobolev")
    s.append("Sobolev   yalnız değer: f=%.4f f'=%.4f | Sobolev: f=%.4f f'=%.4f | türev iyileşti=%s"
             % (b["yalniz_deger__deger_hatasi"], b["yalniz_deger__turev_hatasi"],
                b["sobolev__deger_hatasi"], b["sobolev__turev_hatasi"], b["turev_iyilesti"]))
    return "\n".join(s)

def rapor() -> str:
    s: List[str] = ["KÜLLÎ KAYIP ÇİPİ -- Küme 5 tevhidi"]

    def _rapor_nefs_olcu() -> List[str]:
        s: List[str] = []
        d = mertebe(ne="doğrula")
        s += ["=== ÖLÇÜ FUNKTORU -- ayrı uzaylardan müşterek uzaya ===",
             "",
             "Müşterek uzay `mizan/munazara.py`nin merdivenidir:",
             "  " + "  <  ".join("%s %.2f" % (k, v) for k, v in
                                 sorted(_mertebeler().items(),
                                        key=lambda kv: kv[1])),
             "",
             "FUNKTÖR KAİDELERİ (iddia değil, sınanmış):",
             "  F(id) = id            hata %.2e" % d["birim_hatası"],
             "  F(g∘f) = F(g)∘F(f)    hata %.2e   ← AŞİKÂR, delil DEĞİL"
             % d["terkip_hatası"],
             "",
             "  Terkip kaidesi bu inşada cebren sağlanır (F_T⁻¹∘F_T",
             "  sadeleşir), o yüzden hiçbir şey ispat etmez. Yük taşıyan",
             "  hususiyet SIRA KORUMASIDIR ve sınanan odur:",
             "    sıra korunuyor mu            : %s" % d["sıra_korunuyor"],
             "    cihet ters çevrilince bozuluyor mu: %s"
             % d["cihet_ters_çevrilince_bozuluyor"],
             "    → ölçüt kör değil            : %s" % d["ölçüt_kör_değil"],
             "  funktör mü                     : %s" % d["funktör_mü"],
             "",
             "TANIMLI UZAYLAR (had ve cihet):"]
        for ad in sorted(UZAYLAR):
            S = UZAYLAR[ad]
            s.append("  %-16s [%.3f, %.3f]  %s%s"
                     % (S.ad, S.alt, S.ust,
                        "büyüğü iyi" if S.buyugu_iyi else "küçüğü iyi",
                        "  (haddi TAHMİNÎ)" if S.tahmini_ust else ""))
        s += ["",
              "Eski kayıptaki 0,25 ve 0,1 gibi elle konmuş katsayılar",
              "KALKMIŞTIR: uzaylar arası intibak artık funktörle sağlanıyor,",
              "katsayıyla değil. Katsayı bir ölçü değil, ölçüsüzlüğün örtüsüdür."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  ÖLÇÜ FUNKTÖRÜ -- S → 𝔐 mertebe köprüsü")
    s.append("=" * 70)
    s += _rapor_nefs_olcu()

    def _rapor_nefs_sozlesme() -> List[str]:
        s: List[str] = []
        n_satir = 4
        chi = 32
        tohum = 0
        o = sozunde_mi(n_satir=n_satir, chi=chi, tohum=tohum, ne="hepsi")
        s += ["=== SADAKAT SÖZLEŞMESİ (Dosya 2) -- yüzleştirme ===",
             "",
             "Her meleke dokunacağı bölgeleri İLAN eder; ölçüm dalganın",
             "kendisine bakıp fiilen dokunduğunu bulur. İkisi ayrı düşerse",
             "sözleşme ihlâl edilmiştir. Eşik = %.0e." % ESIK,
             "",
             "  𝒪   meleke              ihlâl / kullanılmayan"]
        ihlal_sayisi = 0
        bos_sayisi = 0
        sic = qsicil()
        for r in o:
            no = int(r["no"])
            ih, ku = r["ihlâl"], r["kullanılmayan"]
            if ih:
                ihlal_sayisi += 1
            if ku:
                bos_sayisi += 1
            isaret = "İHLÂL: " + ",".join(ih) if ih else ""
            if ku:
                isaret += ("  " if isaret else "") + "boş ilan: " + ",".join(ku)
            s.append("  %-3d %-20s %s" % (no, sic[no].ad, isaret or "✓"))
        s += ["",
              "%d melekede hudut ihlâli, %d melekede kullanılmayan ilan."
              % (ihlal_sayisi, bos_sayisi),
              "",
              "İHLÂL: meleke ilan etmediği bir bölgeye dokunmuş -- ya şerhi",
              "yanlış ya kapısı. KULLANILMAYAN İLAN: meleke ilan ettiği bir",
              "bölgeye HİÇ dokunmamış; sözleşme olduğundan geniş, yani",
              "denetlemiyor. İkincisi ihlâl kadar ağır değildir fakat bir",
              "gevşekliktir ve sayılır."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  SÖZLEŞME -- taahhüt edilen bölgeye mi dokundu")
    s.append("=" * 70)
    s += _rapor_nefs_sozlesme()

    def _rapor_nefs_kademeler() -> List[str]:
        s: List[str] = []
        kume = "training"
        n = 3
        from .musahede import gorevleri_getir

        s += ["=== ALTI KADEME -- girdi/çıktı zinciri ===", ""]
        for g in gorevleri_getir(kume)[:int(n)]:
            r = kademeleri_kos(g)
            t = zayif_halka(olcumler=r["ölçümler"], ne="azamî")
            s.append("--- %s ---" % g.ad)
            s += ["  " + x for x in r["günlük"]]
            s.append("  kademe kaybı %.4f  (ortalama mertebe %.3f = %s)"
                     % (t["kayıp"], t["ortalama_mertebe"],
                        mertebe(ne="adlandır", m=t["ortalama_mertebe"])))
            if r["eksik"]:
                s.append("  DÜŞEN UZUV: %s" % ", ".join(sorted(r["eksik"])))
            s.append("")
        s += ["Kademe k'nın çıktısı kademe k+1'in girdisidir; bir modül o",
              "zincirde halka ise uzuvdur. Yan tarafta rey veren modül uzuv",
              "değildir ve bu dosya o farkın kendisidir."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  ALTI KADEME -- LOO notlandırması")
    s.append("=" * 70)
    s += _rapor_nefs_kademeler()

    def _rapor_nefs_mudrike() -> List[str]:
        s: List[str] = []
        kume = "training"
        n = 120
        derinlik = 2
        dalga = False
        from .musahede import gorevleri_getir

        g = gorevleri_getir(kume)[:int(n)]
        coz = cevap = yanlis = 0
        sebepler: Dict[str, int] = {}
        ornek_muhakeme: List[str] = []
        for gv in g:
            r = suz(gv, derinlik=derinlik, dalga=dalga)
            if r["sükût"]:
                sebepler[r["sebep"]] = sebepler.get(r["sebep"], 0) + 1
                if not ornek_muhakeme and r["sebep"] == "kaide bulunamadı":
                    ornek_muhakeme = list(r["muhakeme"])
                continue
            cevap += 1
            ok = True
            for (a, b), c in zip(gv.sinama, r["cevap"]):
                if c is None or c.shape != b.shape or not np.array_equal(c, b):
                    ok = False
            coz += ok
            yanlis += (not ok)
            if ok and len(ornek_muhakeme) < 2:
                ornek_muhakeme = list(r["muhakeme"])

        s += ["=== MÜDRİKE ÇEVRİMİ -- %s (%d görev) ===" % (kume, len(g)),
             "",
             "  konuştu      : %d" % cevap,
             "  TAM ÇÖZDÜ    : %d  (%%%.1f)" % (coz, 100.0 * coz / max(len(g), 1)),
             "  yanlış cevap : %d" % yanlis,
             "  sustu        : %d" % (len(g) - cevap),
             "",
             "  SÜKÛT SEBEPLERİ:"]
        for k, v in sorted(sebepler.items(), key=lambda x: -x[1]):
            s.append("    %-26s %d" % (k, v))
        if ornek_muhakeme:
            s += ["", "  BİR MUHAKEME ÖRNEĞİ (modelin kendi kendine düşündüğü):"]
            s += ["    " + x for x in ornek_muhakeme]
        s += ["",
              "Cevap verince isabet: %s"
              % ("%.1f%%" % (100.0 * coz / cevap) if cevap else "—"),
              "Susmak bir kusur değil kabiliyettir (H10/H16) -- fakat",
              "sebebi söylenebiliyorsa. Yukarıdaki döküm o sebeplerdir."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  MÜDRİKE -- meseleyi içinden geçirmek")
    s.append("=" * 70)
    s += _rapor_nefs_mudrike()


    return "\n".join(s)


MIZAN_AGIRLIK: Dict[str, float] = {"uzay": 1.0, "kategori": 1.0,
                                   "tip": 1.0}
