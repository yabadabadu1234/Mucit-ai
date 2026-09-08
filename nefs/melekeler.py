from __future__ import annotations

import math
import sys
import time
import zlib
from dataclasses import dataclass, field, replace
from functools import lru_cache
from typing import (TYPE_CHECKING, Any, Callable, Dict, List, Optional,
                    Sequence, Tuple)

import numpy as np

from matematik.fitrat import fazla_sayma, tevafuk_olcusu
from kuantum.kapilar import dik_iki_kubit
from matematik.mizan import ardisiklik_kaidesi, tam_istikra_mi
from matematik.mizan import (MERTEBELER, ZANN_I_GALIB_ESIGI, hukum_agirligi,
                            ikili_entropi, makam_tayin, mertebe_adi,
                            yakin_gazali, yakin_zinciri)
from matematik.tip_teorisi import (Baglam, Cember, Deg, Evren, Taban,
                                   denetle_t, dongu_uzayi_n, morfizm_tipi)


from .kule import ince, kaba
from .musahede import ortu
from .zihin_durumu import (MAKAM_ADLARI, QAyar, QYazmac, degil_x, donme, faz_z,
                      kontrollu_donme)
from .zirh import vicdan
from .musahede import (artiklar, delil_dizileri, kaide,
                    nakz_bul, ayir)


__all__ = ["MELEKE_SAYISI", "MERTEBE_SAYISI", "KANONIK_CETVEL",
           "EKSIK_MELEKELER", "UMUM", "TALIM", "TAHSIL",
           "talim_kademesi", "Lif", "lifleri_kur", "SABIT", "DINAMIK",
           "AZAMI_TAM_MERTEBE", "QMeleke", "qsicil", "qmelekeler",
           "QAKIS", "NIZAM_ACIK", "nizami_ac", "nizam_cetveli", "QNefs",
           "rapor_qakis", "bec_faz_kilidi", "QParametre",
           "dikkat", "ehlilestir", "tevafuk", "devirler",
           "KAN_TEMELI", "ALTIN_ORAN",
           "grape_gradyani", "tam_gradyan", "sonlu_fark_gradyani",
           "grape_kos", "sadakat"]


def ehlilestir(tarz: str, x: Any, payda: Any = None, *, eksen: int = -1,
               eps: Optional[float] = None) -> Any:
    if tarz == "bol":
        return float(x / (payda + (1e-9 if eps is None else eps)))
    if tarz == "sık":
        return float(x / (1.0 + x))
    if tarz == "sigmoid":
        return 1.0 / (1.0 + np.exp(-np.clip(x, -60, 60)))
    if tarz == "gelu":
        u = np.sqrt(2.0 / np.pi) * (x + 0.044715 * x ** 3)
        return x / (1.0 + np.exp(-np.clip(2.0 * u, -60, 60)))
    if tarz == "softmax":
        z = x - np.max(x, axis=eksen, keepdims=True)
        e = np.exp(z)
        return e / np.sum(e, axis=eksen, keepdims=True)
    if tarz == "kat_norm":
        mu = np.mean(x, axis=-1, keepdims=True)
        sd = np.std(x, axis=-1, keepdims=True)
        return (x - mu) / (sd + (1e-6 if eps is None else eps))
    if tarz == "nicele":
        return np.round(x / payda) * payda
    raise ValueError("ehlîleştirmenin tarzı bilinmiyor: %r" % (tarz,))


def tevafuk(tarz: str, a: np.ndarray, b: Optional[np.ndarray] = None,
            olcek: Optional[float] = None) -> float:
    def _ic(u: np.ndarray, v: np.ndarray) -> float:
        payda = float(np.linalg.norm(u) * np.linalg.norm(v))
        return float(u.ravel() @ v.ravel() / payda) if payda > 1e-12 else 0.0

    if tarz == "ham":
        return _ic(np.asarray(a), np.asarray(b))
    if tarz == "merkezli":
        u, v = np.asarray(a).ravel(), np.asarray(b).ravel()
        return _ic(u - u.mean(), v - v.mean())
    if tarz == "ayna":
        Y = np.asarray(a)
        if float(np.linalg.norm(Y)) < 1e-12:
            return 1.0
        return float(1.0 - np.sqrt(max(1.0 - _ic(Y, Y.T), 0.0) / 2.0))
    if tarz == "çekirdek":
        x, y = np.asarray(a), np.asarray(b)
        n = len(x)
        if n < 4:
            return 0.0
        TAVAN = 512
        if n > TAVAN:
            idx = np.linspace(0, n - 1, TAVAN).astype(int)
            x, y, n = x[idx], y[idx], TAVAN

        def gram(v: np.ndarray) -> np.ndarray:
            d2 = (v[:, None] - v[None, :]) ** 2
            s = (olcek if olcek is not None
                 else np.sqrt(0.5 * np.median(d2[d2 > 0])) if np.any(d2 > 0)
                 else 1.0)
            return np.exp(-0.5 * d2 / max(s * s, 1e-12))

        H = np.eye(n) - np.ones((n, n)) / n
        K, L = gram(x), gram(y)
        return float(np.trace(K @ H @ L @ H) / (n - 1) ** 2)
    raise ValueError("tevafukun tarzı bilinmiyor: %r" % (tarz,))


def devirler(tarz: str, A: np.ndarray, esik: float = 0.35) -> Any:
    if tarz == "laplasyen":
        derece = A.sum(1)
        inv = np.where(derece > 0, 1.0 / np.sqrt(np.maximum(derece, 1e-12)), 0.0)
        return np.eye(len(A)) - (inv[:, None] * A * inv[None, :])
    if tarz == "betti":
        n = len(A)
        gorulen = np.zeros(n, dtype=bool)
        b0 = 0
        for s in range(n):
            if gorulen[s]:
                continue
            b0 += 1
            yigin = [s]
            gorulen[s] = True
            while yigin:
                u = yigin.pop()
                for v in np.nonzero(A[u])[0]:
                    if not gorulen[v]:
                        gorulen[v] = True
                        yigin.append(int(v))
        kenar = int(np.sum(A > 0) // 2)
        return b0, kenar - n + b0
    if tarz == "zincir_β0":
        v = A
        if len(v) < 2:
            return 1
        fark = np.abs(np.diff(v))
        olcek = float(np.median(fark)) + 1e-12
        return 1 + int(np.sum(fark > esik + 3.0 * olcek))
    if tarz == "ihlâl":
        d = len(A)
        M = A * A
        toplam = np.eye(d)
        terim = np.eye(d)
        for k in range(1, 60):
            terim = terim @ M / k
            toplam = toplam + terim
            if np.max(np.abs(terim)) < 1e-16:
                break
        return float(np.trace(toplam) - d)
    raise ValueError("devir tarzı bilinmiyor: %r" % (tarz,))


def dikkat(q: np.ndarray, k: np.ndarray, v: np.ndarray) -> np.ndarray:
    d = q.shape[-1]
    return ehlilestir("softmax", q @ k.T / np.sqrt(d)) @ v


MELEKE_SAYISI: int = 44
MERTEBE_SAYISI: int = 20

KANONIK_CETVEL: Dict[int, int] = {
    1: 0, 37: 0, 38: 0,
    4: 1, 34: 1,
    6: 2, 2: 2, 3: 2,
    7: 3, 35: 3,
    8: 4, 9: 4,
    5: 5,
    10: 6,
    23: 7, 18: 7,
    11: 8, 12: 8,
    13: 9, 32: 9,
    22: 10, 16: 10,
    15: 11, 14: 11,
    21: 12, 25: 12, 26: 12,
    27: 13, 28: 13,
    24: 14, 29: 14,
    30: 15, 36: 15,
    33: 16, 31: 16,
    19: 17, 20: 17,
    17: 18, 41: 18,
    40: 19, 39: 19, 42: 19, 43: 19, 44: 19,
}

EKSIK_MELEKELER: Dict[int, int] = {}


UMUM: int = 42
TALIM: int = 43
TAHSIL: int = 44


def talim_kademesi(S: np.ndarray, tau: Sequence[float]
                   ) -> Dict[str, object]:
    S = np.asarray(S, float).ravel()
    t = [float(x) for x in tau]
    if any(t[i] <= t[i + 1] for i in range(len(t) - 1)) is False and len(t) > 1:
        pass
    ent: List[float] = []
    dag: List[np.ndarray] = []
    for x in t:
        z = S / max(float(x), 1e-12)
        z = z - z.max()
        p = np.exp(z)
        p = p / max(float(p.sum()), 1e-300)
        dag.append(p)
        nz = p > 1e-15
        ent.append(float(-np.sum(p[nz] * np.log(p[nz]))))
    azalan = all(ent[i] >= ent[i + 1] - 1e-12 for i in range(len(ent) - 1))
    tau_azalan = all(t[i] > t[i + 1] for i in range(len(t) - 1))
    return {"τ": t, "entropi": ent, "dağılım": dag,
            "τ_azalan": bool(tau_azalan),
            "entropi_azalan": bool(azalan),
            "sahih": bool(tau_azalan and azalan)}


sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))

SABIT: Tuple[int, ...] = tuple(range(10))
DINAMIK: Tuple[int, ...] = (13, 17, 19, 20, 30, 55, 1000, 1009, 58383, 60000)

AZAMI_TAM_MERTEBE = 20

_U = Evren(0)
_D = Deg


@dataclass(frozen=True)
class Lif:
    yuva: int
    mertebe: int
    tam_kuruldu: bool
    denetlendi: bool
    tip_ozeti: str
    hata: str = ""

    @property
    def pencere(self) -> int:
        return min(self.mertebe + 1, 4)

    @property
    def adim(self) -> int:
        return 1 + int(math.log2(1 + self.mertebe))

    @property
    def olcek(self) -> float:
        return 1.0 / (1.0 + math.log1p(float(self.mertebe)))


def _tam_kur(m: int) -> Tuple[object, str]:
    return morfizm_tipi(_D("A"), m), "morfizm_tipi(A, %d)" % m


def _temsilci_kur(m: int) -> Tuple[object, str]:
    n = 1 + (m % AZAMI_TAM_MERTEBE)
    return (dongu_uzayi_n(Cember(), Taban(), n),
            "Ω^%d(S¹)  [mertebe %d için temsilci]" % (n, m))


@lru_cache(maxsize=4)
def lifleri_kur(dinamik: Tuple[int, ...] = DINAMIK) -> Tuple[Lif, ...]:
    if len(dinamik) != 10:
        raise ValueError("dinamik mertebe sayısı 10 olmalı (H22)")
    gA = Baglam.terimlerden({"A": _U, "a": _D("A"), "b": _D("A")})
    g0 = Baglam()

    lifler: List[Lif] = []
    for yuva, m in enumerate(tuple(SABIT) + tuple(int(x) for x in dinamik)):
        tam = m <= AZAMI_TAM_MERTEBE
        tip, ozet = _tam_kur(m) if tam else _temsilci_kur(m)
        baglam = gA if tam else g0
        hata = ""
        try:
            denetle_t(tip, _U, baglam)
            gecti = True
        except Exception as e:
            gecti = False
            hata = "%s: %s" % (type(e).__name__, str(e)[:120])
        lifler.append(Lif(yuva=yuva, mertebe=m, tam_kuruldu=tam,
                          denetlendi=gecti, tip_ozeti=ozet, hata=hata))
    return tuple(lifler)


KAN_TEMELI = "rbf"


ALTIN_ORAN = (1.0 + np.sqrt(5.0)) / 2.0

MERTEBE_SIRA: Dict[str, int] = {
    ad: i for i, (_, ad) in enumerate(reversed(MERTEBELER), start=1)
}


KULLI_SIRA: Tuple[Tuple[int, int], ...] = (
    (1, 5), (5, 6), (6, 7),
    (7, 21), (21, 22), (22, 23),
    (23, 25), (25, 26), (26, 27), (27, 30),
    (30, 33), (33, 13),
    (13, 37), (37, 38), (38, 39),
)

AKIS: Tuple[int, ...] = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24,
    25, 26, 27, 28, 29, 30, 31, 32,
    33, 13,
    34, 35, 36,
    37, 38, 39, 40, 41,
)


ALTIN = (1.0 + math.sqrt(5.0)) / 2.0

NIZAM_ACIK: bool = False


def nizami_ac(acik: bool = True) -> bool:
    global NIZAM_ACIK
    eski = NIZAM_ACIK
    NIZAM_ACIK = bool(acik)
    return eski


KANONIK_ACIK: bool = False


def kanoniklestir(acik: bool = True) -> bool:
    global KANONIK_ACIK
    eski = KANONIK_ACIK
    KANONIK_ACIK = bool(acik)
    return eski

_QSICIL: Dict[int, "QMeleke"] = {}


def qkaydet(sinif):
    ornek = sinif()
    if ornek.no in _QSICIL:
        raise ValueError("𝒪%d iki kere kaydedildi" % ornek.no)
    _QSICIL[ornek.no] = ornek
    return sinif


def qsicil() -> Dict[int, "QMeleke"]:
    return dict(_QSICIL)


def qmelekeler() -> List["QMeleke"]:
    return [_QSICIL[i] for i in sorted(_QSICIL)]


def nizam_cetveli() -> List[Tuple[int, str, str, Optional[int]]]:
    return [(m.no, m.ad, m.SINIF, m.CHI) for m in qmelekeler()]


class QParametre:

    def __init__(self, tohum: int = 0, genislik: int = 1) -> None:
        self.tohum = int(tohum)
        self.genislik = max(1, int(genislik))
        self._yer: Dict[str, Tuple[int, int]] = {}
        self._n = 0
        self._vek: Optional[np.ndarray] = None

    def al(self, anahtar: str, n: int) -> np.ndarray:
        if anahtar not in self._yer:
            self._yer[anahtar] = (self._n, int(n))
            self._n += int(n)
        bas, kac = self._yer[anahtar]
        if self._vek is None or len(self._vek) < self._n:
            self._buyut()
        return self._vek[bas:bas + kac]

    def _buyut(self) -> None:
        eski = self._vek
        rng = np.random.default_rng(self.tohum)
        yeni = rng.normal(scale=1.0, size=max(self._n, 1))
        if eski is not None:
            yeni[:len(eski)] = eski
        self._vek = yeni

    def __len__(self) -> int:
        return self._n

    def vektor(self) -> np.ndarray:
        if self._vek is None:
            self._buyut()
        return np.asarray(self._vek[:self._n], float).copy()

    def yukle(self, v: np.ndarray) -> None:
        v = np.asarray(v, float).reshape(-1)
        if self._vek is None:
            self._buyut()
        m = min(len(v), len(self._vek))
        self._vek[:m] = v[:m]

    def defter(self) -> Dict[str, Tuple[int, int]]:
        return dict(self._yer)


class QMeleke:

    no: int = 0
    ad: str = ""
    BIRIKIM_ACI: int = 8

    SINIF: str = "koruyucu"
    CHI: Optional[int] = None

    def aci(self, p, n: int, olcek: float = 0.6) -> np.ndarray:
        anahtar = "q%d.%s/%d" % (self.no, self.ad, int(n))
        if isinstance(p, QParametre):
            return olcek * p.al(anahtar, n)
        return olcek * p.v(anahtar, n)

    def yay(self, p, n_sabit: int, hedef: int, olcek: float = 0.6
            ) -> np.ndarray:
        g = max(1, int(getattr(p, "genislik", 1)))
        a = self.aci(p, int(n_sabit) * g, olcek)
        if hedef <= 0:
            return np.zeros(0)
        return np.resize(a, int(hedef))

    def birikim(self, p, n: int, olcek: float = 0.6) -> np.ndarray:
        return self.yay(p, self.BIRIKIM_ACI, n, olcek) / max(float(n), 1.0)

    def uygula(self, q: QYazmac, p: "QParametre") -> None:
        raise NotImplementedError

    def kosu(self, q: QYazmac, p: "QParametre") -> None:
        n0 = q.iz.kapi
        if KANONIK_ACIK:
            q.y.kanonikle()
        self.uygula(q, p)
        q.iz.not_dus("𝒪%d %s" % (self.no, self.ad),
                     "%d kapı" % (q.iz.kapi - n0))

    def tugla(self, q: QYazmac, p: "QParametre", ofset: int = 0,
              olcek: float = 0.5) -> None:
        a = self.aci(p, 6, olcek)
        G = dik_iki_kubit(a)
        k = q.veri_yuvasi
        sol = q.veri_izgara(range(ofset, k - 1, 2))
        q.cift_yigin(sol, G)

    def satir_donmesi(self, q: QYazmac, p: "QParametre",
                      olcek: float = 0.6) -> None:
        k = q.veri_yuvasi
        a = self.aci(p, k, olcek)
        Gk = np.stack([donme(float(t)) for t in a])
        yuv = q.veri_izgara()
        q.tek_yigin(yuv, np.tile(Gk, (q.n_satir, 1, 1)))


@qkaydet
class QMusahede(QMeleke):
    no, ad = 1, "Müşahede"
    SINIF, CHI = "kurucu", 8

    def uygula(self, q, p):
        self.satir_donmesi(q, p, 0.7)
        self.tugla(q, p, ofset=0, olcek=0.6)
        self.tugla(q, p, ofset=1, olcek=0.6)


@qkaydet
class QHayal(QMeleke):
    no, ad = 2, "Hayal"
    SINIF, CHI = "kurucu", 8

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.9)
        j = q.veri_yuvasi - 1
        q.tek_yigin([q.veri(i, j) for i in range(q.n_satir)],
                    np.stack([donme(0.25 * math.pi + float(t)) for t in a]))


@qkaydet
class QMuhayyile(QMeleke):
    no, ad = 3, "Muhayyile"
    SINIF, CHI = "kurucu", 16

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.8))
        k = q.veri_yuvasi
        for i in range(q.n_satir):
            for j in range(0, k - 2):
                q.uzak_cift(q.veri(i, j), q.veri(i, j + 2), G)


@qkaydet
class QTertip(QMeleke):
    no, ad = 4, "Tertip"
    SINIF, CHI = "koruyucu", 8

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.7)
        j = q.veri_yuvasi - 1
        q.cift_yigin([q.veri(i, j) for i in range(q.n_satir)],
                     np.stack([kontrollu_donme(float(t)) for t in a]))


@qkaydet
class QTecrit(QMeleke):
    no, ad = 5, "Tecrit"
    SINIF, CHI = "çözücü", None

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        k = q.veri_yuvasi
        q.cift_yigin(q.veri_izgara(range(1, k - 1, 2)), G.T)


@qkaydet
class QTasavvur(QMeleke):
    no, ad = 6, "Tasavvur"
    SINIF, CHI = "kurucu", 16

    def uygula(self, q, p):
        q.harman(kademe=1, teta=self.aci(p, 24, 0.6))


@qkaydet
class QMana(QMeleke):
    no, ad = 7, "Mana"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        q.mpo_topla("tasdik", self.birikim(p, q.n_satir, 0.9))


@qkaydet
class QTahlil(QMeleke):
    no, ad = 8, "Tahlil"
    SINIF, CHI = "çözücü", 2

    def uygula(self, q, p):
        self.satir_donmesi(q, p, 0.8)


@qkaydet
class QTerkip(QMeleke):
    no, ad = 9, "Terkip"
    SINIF, CHI = "kurucu", 8

    def uygula(self, q, p):
        self.tugla(q, p, ofset=1, olcek=0.7)


@qkaydet
class QTezat(QMeleke):
    no, ad = 10, "Tezat"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        Z = faz_z()
        k = q.veri_yuvasi
        q.tek_yigin([q.veri(i, k - 1) for i in range(1, q.n_satir, 2)], Z)


@qkaydet
class QTenakuz(QMeleke):
    no, ad = 11, "Tenakuz Bulma"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        a = self.birikim(p, q.n_satir, 1.1)
        isaret = np.where(np.arange(q.n_satir) % 2 == 0, 1.0, -1.0)
        q.mpo_topla("tenakuz", a * isaret)


@qkaydet
class QTenkit(QMeleke):
    no, ad = 12, "Tenkit"
    SINIF, CHI = "çözücü", 2

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.4)
        q.tek_yigin(q.yereller(),
                    np.stack([donme(-abs(float(t))) for t in a]))


@qkaydet
class QTasdik(QMeleke):
    no, ad = 13, "Tasdik"
    SINIF, CHI = "çözücü", None

    def uygula(self, q, p):
        a = self.aci(p, 2, 0.5)
        q.cift(q.kulli("tasdik", 0), kontrollu_donme(float(a[0])))
        q.tek(q.kulli("tasdik", 1), donme(float(a[1])))


@qkaydet
class QGaye(QMeleke):
    no, ad = 14, "Gaye Belirleme"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        a = self.aci(p, 4, 0.5)
        for j in range(2):
            q.uzak_cift(q.kulli("tasdik", j), q.kulli("mizan", j),
                        kontrollu_donme(float(a[j])))


@qkaydet
class QMerak(QMeleke):
    no, ad = 15, "Merak ve Sual"
    SINIF, CHI = "kurucu", 8

    def uygula(self, q, p):
        a = self.aci(p, 2, 0.5)
        q.tek_yigin([q.kulli("nakz", j) for j in range(2)],
                    np.stack([donme(0.25 * math.pi + float(t))
                              for t in a[:2]]))


@qkaydet
class QDenemeYanilma(QMeleke):
    no, ad = 16, "Deneme-Yanılma"
    SINIF, CHI = "kurucu", 8

    def uygula(self, q, p):
        k = q.veri_yuvasi
        a = self.aci(p, k, 0.3)
        Gk = np.tile(np.stack([donme(float(t)) for t in a]),
                     (q.n_satir, 1, 1))
        q.tek_yigin(q.veri_izgara(), Gk)


@qkaydet
class QIhtimal(QMeleke):
    no, ad = 17, "İhtimal Hesabı"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        a = self.aci(p, 4, 0.4)
        q.tek_yigin([q.kulli("mizan", j) for j in range(4)],
                    np.stack([donme(float(t)) for t in a[:4]]))


@qkaydet
class QKiyas(QMeleke):
    no, ad = 18, "Kıyas"
    SINIF, CHI = "kurucu", 8

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        for i in range(q.n_satir - 1):
            q.uzak_cift(q.veri(i, 0), q.veri(i + 1, 0), G)


@qkaydet
class QTemsil(QMeleke):
    no, ad = 19, "Temsil"
    SINIF, CHI = "koruyucu", 8

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.6))
        k = q.veri_yuvasi
        sol = [q.veri(i, 0) for i in range(q.n_satir)]
        if k >= 4:
            sol += [q.veri(i, 2) for i in range(q.n_satir)]
        q.cift_yigin(sol, G)


@qkaydet
class QTesbih(QMeleke):
    no, ad = 20, "Teşbih"
    SINIF, CHI = "kurucu", 8

    def uygula(self, q, p):
        if q.n_satir < 2:
            return
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        k = q.veri_yuvasi
        for j in range(k):
            q.uzak_cift(q.veri(0, j), q.veri(1, j), G)


@qkaydet
class QTefekkur(QMeleke):
    no, ad = 21, "Tefekkür"
    SINIF, CHI = "kurucu", 16

    def uygula(self, q, p):
        lifler = lifleri_kur(DINAMIK)
        a = self.aci(p, len(lifler), 1.0)
        k = q.veri_yuvasi

        eksen_acisi: Dict[int, float] = {}
        for lif in lifler:
            teta = lif.olcek * (1.0 + 0.3 * float(a[lif.yuva]))
            eksen_acisi[lif.yuva % k] = eksen_acisi.get(lif.yuva % k, 0.0) + teta
        yuv, Gl = [], []
        for j, top in eksen_acisi.items():
            R = donme(top)
            for i in range(q.n_satir):
                yuv.append(q.veri(i, j))
                Gl.append(R)
        q.tek_yigin(yuv, np.stack(Gl))
        son = q.kulli("makam", 0)
        katki: Dict[int, float] = {}
        for lif in lifler:
            teta = lif.olcek * (1.0 + 0.3 * float(a[lif.yuva]))
            bas = q.veri(0, lif.yuva % k)
            duraklar = list(range(bas, son, lif.adim))
            if len(duraklar) < 2:
                continue
            pay = teta / len(duraklar)
            for d in duraklar:
                katki[d] = katki.get(d, 0.0) + pay
        if len(katki) >= 2:
            dur = sorted(katki)
            q.mpo_topla("makam", [katki[d] for d in dur], duraklar=dur)


@qkaydet
class QIllet(QMeleke):
    no, ad = 22, "İllet Keşfi"
    SINIF, CHI = "koruyucu", 8

    def uygula(self, q, p):
        a = self.yay(p, 4, max(q.n_satir - 1, 1), 0.5)
        for i in range(q.n_satir - 1):
            q.uzak_cift(q.veri(i, 0), q.veri(i + 1, 0),
                        kontrollu_donme(float(a[i])))


@qkaydet
class QMantik(QMeleke):
    no, ad = 23, "Mantık Yürütme"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        q.mpo_topla("nakz", -np.abs(self.birikim(p, q.n_satir, 0.8)))


@qkaydet
class QIspat(QMeleke):
    no, ad = 24, "İspat"
    SINIF, CHI = "çözücü", None

    def uygula(self, q, p):
        a = self.yay(p, 4, max(q.n_satir - 1, 1), 0.5)
        for i in range(q.n_satir - 1):
            teta = float(a[i]) / (1.0 + 0.1 * i)
            q.uzak_cift(q.yerel(i), q.yerel(i + 1), kontrollu_donme(teta))


@qkaydet
class QTeemmul(QMeleke):
    no, ad = 25, "Teemmül"
    SINIF, CHI = "koruyucu", 8
    TUR = 3

    def uygula(self, q, p):
        for t in range(self.TUR):
            self.tugla(q, p, ofset=t % 2, olcek=0.3)


@qkaydet
class QTemkin(QMeleke):
    no, ad = 26, "Temkin"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.12)
        q.tek_yigin(q.yereller(),
                    np.stack([donme(float(t)) for t in a]))


@qkaydet
class QTetkik(QMeleke):
    no, ad = 27, "Tetkik"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        self.satir_donmesi(q, p, 0.2)


@qkaydet
class QTashih(QMeleke):
    no, ad = 28, "Tashih"
    SINIF, CHI = "çözücü", 2

    def uygula(self, q, p):
        k = q.veri_yuvasi
        tetkik = QTetkik().aci(p, k, 0.2)
        lam = float(np.tanh(self.aci(p, 1, 1.0)[0]))
        Gk = np.tile(np.stack([donme(-lam * float(t)) for t in tetkik]),
                     (q.n_satir, 1, 1))
        q.tek_yigin(q.veri_izgara(), Gk)


@qkaydet
class QTeyit(QMeleke):
    no, ad = 29, "Teyit"
    SINIF, CHI = "koruyucu", 8

    def uygula(self, q, p):
        k = q.veri_yuvasi
        if k < 2:
            return
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        for i in range(q.n_satir):
            q.uzak_cift(q.veri(i, 0), q.yerel(i), G)


@qkaydet
class QTahkik(QMeleke):
    no, ad = 30, "Tahkik"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        q.mpo_topla("tasdik", self.birikim(p, q.n_satir, 1.0), j=1)


@qkaydet
class QTedebbur(QMeleke):
    no, ad = 31, "Tedebbür"
    SINIF, CHI = "kurucu", 8
    UFUK = 4

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.25))
        GU = np.linalg.matrix_power(np.asarray(G, float), self.UFUK)
        q.cift_yigin([q.veri(i, 0) for i in range(q.n_satir)], GU)
        a = self.aci(p, 2, 0.3)
        q.tek_yigin([q.kulli("mizan", 2 + j) for j in range(2)],
                    np.stack([donme(float(t)) for t in a[:2]]))


@qkaydet
class QSekZanYakin(QMeleke):
    no, ad = 32, "Şek-Zan-Yakîn"
    SINIF, CHI = "çözücü", 2

    def uygula(self, q, p):
        a = self.aci(p, 5, 0.6)
        mk = q._alan["makam"][1]
        q.uzak_cift(q.kulli("tasdik", 0), q.kulli("makam", 0),
                    kontrollu_donme(abs(float(a[0]))))
        q.uzak_cift(q.kulli("nakz", 0), q.kulli("makam", 0),
                    kontrollu_donme(-abs(float(a[1]))))
        if mk >= 2:
            q.uzak_cift(q.kulli("tenakuz", 0), q.kulli("makam", 1),
                        kontrollu_donme(abs(float(a[2]))))
        if mk >= 3:
            q.uzak_cift(q.kulli("tasdik", 1), q.kulli("makam", 2),
                        kontrollu_donme(float(a[3])))
        q.uzak_cift(q.kulli("makam", 1 if mk >= 2 else 0),
                    q.kulli("sukut", 0),
                    kontrollu_donme(abs(float(a[4]))))


@qkaydet
class QMuhakeme(QMeleke):
    no, ad = 33, "Muhakeme"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        a = self.aci(p, 6, 0.5)
        for j in range(2):
            q.uzak_cift(q.kulli("tasdik", j), q.kulli("mizan", j),
                        kontrollu_donme(abs(float(a[j]))))
        for j in range(2):
            q.uzak_cift(q.kulli("tenakuz", j), q.kulli("mizan", 2 + j),
                        kontrollu_donme(-abs(float(a[2 + j]))))
        for j in range(2):
            q.uzak_cift(q.kulli("nakz", j), q.kulli("mizan", j),
                        kontrollu_donme(-abs(float(a[4 + j]))))


@qkaydet
class QTafsil(QMeleke):
    no, ad = 34, "Tafsil"
    SINIF, CHI = "koruyucu", 8

    def uygula(self, q, p):
        q.mpo_dagit("makam", self.birikim(p, q.n_satir, 0.7))


@qkaydet
class QTefsir(QMeleke):
    no, ad = 35, "Tefsir"
    SINIF, CHI = "koruyucu", 8

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.4))
        k = q.veri_yuvasi
        for i in range(1, q.n_satir):
            q.uzak_cift(q.veri(i - 1, k - 1), q.veri(i, 0), G)


@qkaydet
class QTevil(QMeleke):
    no, ad = 36, "Tevil"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        a = self.aci(p, 2, 0.5)
        for j in range(2):
            q.uzak_cift(q.kulli("tenakuz", j), q.kulli("tasdik", j),
                        kontrollu_donme(float(a[j])))


@qkaydet
class QFesahat(QMeleke):
    no, ad = 37, "Fesâhat"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        _, kk = q._alan["kelam"]
        a = self.birikim(p, q.n_satir * kk, 1.2) * kk
        duraklar = q.yereller()
        for j in range(kk):
            q.mpo_topla("kelam", a[j * q.n_satir:(j + 1) * q.n_satir],
                        duraklar=duraklar, j=j)
        b = self.aci(p, 2, 0.6)
        tas = q.kulli("tasdik", 0)
        q.tek(tas, degil_x())
        for j in range(min(kk, 2)):
            q.uzak_cift(tas, q.kulli("kelam", j),
                        kontrollu_donme(-abs(float(b[j]))))
        q.tek(tas, degil_x())


@qkaydet
class QTalakat(QMeleke):
    no, ad = 38, "Talâkat"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        _, kk = q._alan["kelam"]
        G = dik_iki_kubit(self.aci(p, 6, 0.4))
        for j in range(kk - 1):
            q.cift(q.kulli("kelam", j), G)
        a = self.aci(p, 2, 0.35)
        for j in range(2):
            q.uzak_cift(q.kulli("tasdik", j), q.kulli("kelam", j),
                        kontrollu_donme(float(a[j])))


@qkaydet
class QBelagat(QMeleke):
    no, ad = 39, "Belâgat"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        _, kk = q._alan["kelam"]
        _, tk = q._alan["tasdik"]
        a = np.concatenate([self.aci(p, kk, 0.45),
                            self.birikim(p, tk, 0.7)])
        mk = q._alan["makam"][1]
        for j in range(kk):
            q.uzak_cift(q.kulli("makam", j % mk), q.kulli("kelam", j),
                        kontrollu_donme(float(a[j])))
        for j in range(min(tk, kk)):
            q.uzak_cift(q.kulli("tasdik", j),
                        q.kulli("kelam", (j + 2) % kk),
                        kontrollu_donme(float(a[kk + j])))


@qkaydet
class QSanat(QMeleke):
    no, ad = 40, "Sanat"
    SINIF, CHI = "koruyucu", None

    def uygula(self, q, p):
        altin_aci = 2.0 * math.pi / (ALTIN ** 2)
        _, kk = q._alan["kelam"]
        mk = q._alan["makam"][1]
        q.tek_yigin([q.kulli("makam", j) for j in range(mk)],
                    np.stack([donme((altin_aci * (j + 1)) % (2 * math.pi))
                              for j in range(mk)]))
        q.tek_yigin([q.kulli("kelam", j) for j in range(kk)],
                    np.stack([donme((altin_aci * (j + 1)) % (2 * math.pi))
                              for j in range(kk)]))


@qkaydet
class QMunazara(QMeleke):
    no, ad = 41, "Münazara"
    SINIF, CHI = "çözücü", 2

    def uygula(self, q, p):
        _, kk = q._alan["kelam"]
        a = self.aci(p, 4 + kk, 0.5)
        for j in range(2):
            q.uzak_cift(q.kulli("mizan", j), q.kulli("makam", j),
                        kontrollu_donme(float(a[j])))
        for j in range(kk):
            q.uzak_cift(q.kulli("sukut", 0), q.kulli("kelam", j),
                        kontrollu_donme(-abs(float(a[4 + j]))))
        q.tek(q.kulli("sukut", 0), donme(float(a[2]) * 0.5))


@qkaydet
class QUmumilestirme(QMeleke):
    no, ad = 42, "Umumileştirme"
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        n = max(1, q.n_satir)
        a = self.aci(p, 2, 0.5)
        ortak = np.full(n, float(a[0]) / float(n))
        q.iz.kesme += q.mpo_topla("mizan", ortak)
        q.iz.kesme += q.mpo_topla("tenakuz", -0.25 * ortak)


@qkaydet
class QTalim(QMeleke):
    no, ad = 43, "Talim"
    SINIF, CHI = "koruyucu", 4
    TAU: Tuple[float, ...] = (4.0, 2.0, 1.0, 0.5)
    OLCU: Tuple[float, ...] = (3.0, 1.0, 0.5, -1.0, 2.0)

    def uygula(self, q, p):
        r = talim_kademesi(np.asarray(self.OLCU, float), self.TAU)
        if not r["sahih"]:
            return
        _, kk = q._alan["kelam"]
        a = self.aci(p, len(self.TAU), 0.4)
        for l, tau in enumerate(self.TAU):
            teta = float(a[l]) / float(tau)
            q.tek_yigin([q.kulli("kelam", j) for j in range(kk)],
                        np.stack([donme(teta) for _ in range(kk)]))


@qkaydet
class QTahsil(QMeleke):
    no, ad = 44, "Tahsil"
    SINIF, CHI = "çözücü", 2
    ETA: float = 0.1
    GAMA: float = 0.05

    def uygula(self, q, p):
        if not q.bolge_var("parametre"):
            return
        npar = q.taksimat.bolge["parametre"][1]
        kac = min(int(npar), 8)
        a = self.aci(p, 2, 0.5)
        for j in range(kac):
            q.uzak_cift(q.kulli("mizan", j % 4), q.parametre(j),
                        kontrollu_donme(-abs(float(a[0])) * float(self.ETA)))
        q.tek_yigin([q.parametre(j) for j in range(kac)],
                    np.stack([donme(float(self.GAMA) * float(a[1]))
                              for _ in range(kac)]))


QAKIS: Tuple[int, ...] = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24,
    25, 26, 27, 28, 29, 30, 31, 32,
    33, 13,
    34, 35, 36,
    37, 38, 39, 40, 41,
    42, 43, 44,
)


YOGUSAN: Tuple[str, ...] = ("makam", "mizan", "tasdik", "kelam")


def bec_faz_kilidi(q: QYazmac, tur: int = 6, g: float = 0.35) -> None:
    alanlar = [(ad, kac) for ad, kac in q.ayar.kulli_alanlar
               if ad in YOGUSAN]
    for t in range(tur):
        for ad, kac in alanlar:
            for j in range(kac - 1):
                q.cift(q.kulli(ad, j), _kinetik(0.12))
        faz = g / (1.0 + t)
        for ad, kac in alanlar:
            for j in range(kac):
                q.tek(q.kulli(ad, j), donme(faz))


def _kinetik(teta: float) -> np.ndarray:
    c, s = math.cos(teta), math.sin(teta)
    G = np.eye(4)
    G[1, 1] = c
    G[1, 2] = -s
    G[2, 1] = s
    G[2, 2] = c
    return G


class QNefs:

    def __init__(self, tohum: int = 0, ayar: Optional[QAyar] = None,
                 sira: Sequence[int] = QAKIS, sadakat: bool = True,
                 gaye: bool = True) -> None:
        self.ayar = ayar or QAyar(tohum=tohum)
        self.p = QParametre(tohum, genislik=int(
            getattr(self.ayar, "parametre_genisligi", 1)))
        self.sira = tuple(sira)
        self.s = qsicil()
        self.gaye = bool(gaye)
        self.sadakat = bool(sadakat)

    HARMAN_OLCEGI = 0.6

    def harman_acilari(self, q) -> np.ndarray:
        lif = tuple(int(x) for x in q.y.ayar.lif)
        kademe = max(1, int(getattr(self.ayar, "harman_kademesi", 1)))
        n = kademe * sum(max(1, int(x).bit_length() - 1) for x in lif)
        anahtar = "harman/%d" % int(n)
        ham = (self.p.al(anahtar, n) if isinstance(self.p, QParametre)
               else self.p.v(anahtar, n))
        return self.HARMAN_OLCEGI * np.asarray(ham, float)

    def idrak_et(self, E: np.ndarray, bec: bool = True,
                 yigin: int = 0, tikaniklik: float = 0.0,
                 olcum: Optional[bool] = None) -> QYazmac:
        E = np.asarray(E, float)
        if olcum is None:
            olcum = bool(int(getattr(self.ayar, "meleke_olcumu", 1)))
        B = E.shape[0] if E.ndim == 3 else max(1, int(yigin))
        n_satir = E.shape[-2]
        ayar = self.ayar
        if B != ayar.yigin:
            ayar = replace(ayar, yigin=B)
        q = QYazmac(n_satir, ayar)
        q.kodla(E)
        if tikaniklik:
            ortu(ne="kapı", q=q, h1=float(tikaniklik))
        q.harman(teta=self.harman_acilari(q))
        okumalar: Dict[int, Dict[str, float]] = {}
        dS: Dict[int, float] = {}
        if olcum:
            from .kulli_kayip import (SOZLESME, _TAKSIMAT_ARTIGI,
                                      bolge_degeri)

            def _entropi() -> float:
                e = q.y.dolasiklik_entropisi()
                v = e.get("entropi_yigin", None)
                if v is None:
                    return float(e["entropi"])
                return float(np.asarray(v, float).reshape(-1)[0])

        S_tasinan = _entropi() if olcum else 0.0
        for no in self.sira:
            onceki_sadakat = float(q.y.sadakat_log()) if olcum else 0.0
            S_once = S_tasinan
            self.s[no].kosu(q, self.p)
            if self.sadakat:
                vicdan(q, self.p, ne="işaret")
            if olcum:
                S_tasinan = _entropi()
                fark = S_tasinan - S_once
                dS[int(no)] = dS.get(int(no), 0.0) + (
                    0.0 if fark != fark else fark)
                ilan = SOZLESME.get(int(no), ((), ""))[0]
                d: Dict[str, float] = {}
                for ad in ilan:
                    if ad in _TAKSIMAT_ARTIGI or ad in ("veri", "yerel"):
                        continue
                    d[ad] = bolge_degeri(q, ad)
                dus = max(0.0, onceki_sadakat - float(q.y.sadakat_log()))
                d["kesme"] = float(np.exp(-dus))
                eski = okumalar.get(int(no))
                okumalar[int(no)] = d if eski is None else {
                    k: min(v, eski.get(k, v)) for k, v in d.items()}
        if self.sadakat:
            q.iz.kesme += vicdan(q, ne="usul")
        if self.gaye:
            from ogrenme.optimize import gaye_kos
            q.iz.kesme += gaye_kos(q, self.p)
        if self.sadakat:
            vicdan(q, ne="intaç")
            from .sadakat import SadakatAyari, sadakat_uygula
            lif = tuple(int(x) for x in q.y.ayar.lif)
            sadakat_uygula(q.y, SadakatAyari(
                acik=int(getattr(self.ayar, "sadakat_acik", 1)),
                parite_lifi=min(int(getattr(self.ayar, "parite_lifi", 2)),
                                len(lif) - 1),
                lif_yapisi=lif))
        if bec:
            bec_faz_kilidi(q)
        q.iz.kesme_hakiki = float(max(0.0, 1.0 - q.y.sadakat()))
        q.y.normalize()
        q.okumalar = okumalar
        q.dS = dS
        return q

    def __len__(self) -> int:
        return len(self.p)

    def vektor(self) -> np.ndarray:
        return self.p.vektor()

    def yukle(self, v: np.ndarray) -> None:
        self.p.yukle(v)


def rapor_qakis(tohum: int = 0, n: int = 20, d_in: int = 12,
          ayar: Optional[QAyar] = None) -> str:
    rng = np.random.default_rng(tohum)
    E = rng.normal(size=(n, d_in))
    nefs = QNefs(tohum, ayar)
    t0 = time.perf_counter()
    q = nefs.idrak_et(E)
    dt = time.perf_counter() - t0
    o = q.olcumler()

    s = ["=== nefs (KÜBİT): 41 meleke, tek dalga, tek ölçüm ===",
         "",
         "kübit=%d  (satır=%d × %d + küllî %d)   χ=%d   durum=%.1f KB"
         % (q.n, q.n_satir, q.oge, q.ayar.kulli_yuva, q.ayar.bag,
            q.y.bayt / 1024.0),
         "kapı=%d  takas=%d  MPO=%d  toplam kesme=%.3e  %.2f sn"
         % (q.iz.kapi, q.iz.takas, q.iz.supurme, q.iz.kesme, dt),
         "",
         "SÜPERPOZİSYON → DOLAŞIKLIK (ölçülen, iddia edilen değil):",
         "  MERA öncesi entropi = %.6f  (Schmidt = %d)"
         % (q.iz.entropi_once, q.iz.schmidt_once),
         "  MERA sonrası entropi = %.6f  (Schmidt = %d)"
         % (q.iz.entropi_sonra, q.iz.schmidt),
         "  akış sonu entropi    = %.6f" % o["entropi"],
         "  norm hatası          = %.2e" % o["norm_hatası"],
         "",
         "MAKAM DAĞILIMI (POVM zayıf ölçüm -- ÇÖKÜŞ YOK):"]
    for ad in MAKAM_ADLARI:
        p = o["P_" + ad]
        s.append("  %-6s %.4f  %s" % (ad, p, "█" * int(round(40 * p))))
    s += ["",
          "KÜLLÎ HÜKÜMLER (zayıf okuma, [0,1]):"]
    for ad, _ in q.ayar.kulli_alanlar:
        s.append("  %-9s %.4f" % (ad, o[ad]))
    s += ["", "MELEKELERİN İCRA İZİ:"]
    s += ["  " + x for x in q.iz.gunluk]
    return "\n".join(s)


def _uexp(H: np.ndarray, t: float) -> np.ndarray:
    lam, V = np.linalg.eigh(H)
    return (V * np.exp(-1j * lam * t)) @ V.conj().T


def _genel_expm(M: np.ndarray, tur: int = 60) -> np.ndarray:
    M = np.asarray(M, complex)
    nrm = float(np.abs(M).sum(axis=1).max())
    k = max(0, int(math.ceil(math.log2(max(nrm, 1e-300)))) + 2)
    A = M / (2.0 ** k)
    S = np.eye(A.shape[0], dtype=complex)
    T = np.eye(A.shape[0], dtype=complex)
    for i in range(1, tur):
        T = T @ A / i
        S = S + T
        if np.abs(T).max() < 1e-18:
            break
    for _ in range(k):
        S = S @ S
    return S


def sadakat(H0: np.ndarray, Hk: Sequence[np.ndarray],
            om: Sequence[np.ndarray], psi0: np.ndarray,
            hedef: np.ndarray, T: float) -> float:
    M = len(om[0])
    dt = T / M
    p = np.asarray(psi0, complex).copy()
    for j in range(M):
        H = H0 + sum(om[k][j] * Hk[k] for k in range(len(Hk)))
        p = _uexp(H, dt) @ p
    return float(abs(np.vdot(hedef, p)) ** 2)


def _ileri_geri(H0, Hk, om, psi0, hedef, T):
    M = len(om[0])
    dt = T / M
    Us, ileri = [], [np.asarray(psi0, complex).copy()]
    p = ileri[0]
    for j in range(M):
        H = H0 + sum(om[k][j] * Hk[k] for k in range(len(Hk)))
        U = _uexp(H, dt)
        Us.append(U)
        p = U @ p
        ileri.append(p.copy())
    geri = [None] * (M + 1)
    lam = np.asarray(hedef, complex).copy()
    geri[M] = lam.copy()
    for j in range(M - 1, -1, -1):
        lam = Us[j].conj().T @ lam
        geri[j] = lam.copy()
    return Us, ileri, geri, dt


def grape_gradyani(H0, Hk, om, psi0, hedef, T) -> List[np.ndarray]:
    Us, ileri, geri, dt = _ileri_geri(H0, Hk, om, psi0, hedef, T)
    M = len(om[0])
    G = [np.zeros(M) for _ in Hk]
    for k in range(len(Hk)):
        for j in range(M):
            P, PSI = geri[j + 1], ileri[j + 1]
            G[k][j] = 2.0 * np.real(np.vdot(P, PSI)
                                    * np.vdot(PSI, (1j * dt * Hk[k]) @ P))
    return G


def tam_gradyan(H0, Hk, om, psi0, hedef, T) -> List[np.ndarray]:
    M = len(om[0])
    dt = T / M
    n = H0.shape[0]
    Us, ileri, geri, _ = _ileri_geri(H0, Hk, om, psi0, hedef, T)
    G = [np.zeros(M) for _ in Hk]
    for k in range(len(Hk)):
        for j in range(M):
            H = H0 + sum(om[q][j] * Hk[q] for q in range(len(Hk)))
            A = -1j * dt * H
            E = -1j * dt * Hk[k]
            B = np.zeros((2 * n, 2 * n), dtype=complex)
            B[:n, :n] = A
            B[n:, n:] = A
            B[:n, n:] = E
            EB = _genel_expm(B)
            dU = EB[:n, n:]
            P, PSI = geri[j + 1], ileri[j]
            c = np.vdot(geri[0], ileri[0])
            G[k][j] = 2.0 * np.real(np.conj(c) * np.vdot(P, dU @ PSI))
    return G


def sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, T, h: float = 1e-6
                        ) -> List[np.ndarray]:
    M = len(om[0])
    G = [np.zeros(M) for _ in Hk]
    for k in range(len(Hk)):
        for j in range(M):
            o1 = [x.copy() for x in om]; o1[k][j] += h
            o2 = [x.copy() for x in om]; o2[k][j] -= h
            G[k][j] = (sadakat(H0, Hk, o1, psi0, hedef, T)
                       - sadakat(H0, Hk, o2, psi0, hedef, T)) / (2 * h)
    return G


def grape_kos(H0, Hk, psi0, hedef, T: float, M: int = 40,
              tur: int = 200, adim: float = 0.5, tohum: int = 0
              ) -> Dict[str, object]:
    r = np.random.default_rng(tohum)
    om = [r.normal(size=M) * 0.2 for _ in Hk]
    F = sadakat(H0, Hk, om, psi0, hedef, T)
    seyir = [F]
    t = adim
    for _ in range(tur):
        G = grape_gradyani(H0, Hk, om, psi0, hedef, T)
        n = math.sqrt(sum(float(np.sum(g * g)) for g in G))
        if n < 1e-14:
            break
        yeni = [om[k] + t * G[k] / n for k in range(len(Hk))]
        Fy = sadakat(H0, Hk, yeni, psi0, hedef, T)
        if Fy > F:
            om, F = yeni, Fy
        else:
            t *= 0.5
            if t < 1e-10:
                break
        seyir.append(F)
    return {"kontrol": om, "sadakat": F, "seyir": seyir,
            "tekdüze_mi": all(seyir[i] <= seyir[i + 1] + 1e-12
                              for i in range(len(seyir) - 1))}
