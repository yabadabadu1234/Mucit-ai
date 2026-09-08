from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import (Callable, Dict, Iterable, List, Mapping, Optional,
                    Sequence, Tuple)

import numpy as np

from idrak.kategori import Uzay
from kuantum.stabilizer import StabilizerDurum
from nefs.qyazmac import QuditYazmac as Yazmac
from matematik.mizan import Onerme, Tablo, deg, degil, ise, ve
from nefs.zihin_durumu import QYazmac, degil_x, donme

__all__ = [
    "yama", "delik", "iz",
    "vietoris_rips", "dogum_olum_cetveli", "cetveller_arasi_mesafe",
    "kahan_toplam",
    "ZirhAyari", "ZirhIzi", "zirhla", "dalgayi_yokla",
    "Usul", "USULLER", "ALANLAR", "isaret_vur",
    "vicdan",
    "SINIF_CIHETI", "NIZAM_BANDI", "SADAKAT_SIDDETI",
    "taahhude_yuzlestir", "muhru_stabilizerle_yuzlestir",
    "zirh_kaybi", "rapor",
]


def yama(res_a: np.ndarray, res_b: np.ndarray,
                       eps: float = 1e-9) -> Dict[str, object]:
    a = np.asarray(res_a, float)
    b = np.asarray(res_b, float)
    if a.shape != b.shape:
        raise ValueError("iki kısıtlama aynı şekilde olmalı")
    d = (a - b).ravel()
    kare = float(d @ d)
    return {"uyumsuzluk": kare,
            "izdüşüm": np.eye(d.size) - np.outer(d, d) / (kare + float(eps)),
            "fark": d}


def delik(K: Dict[int, List[Tuple[int, ...]]], k: int = 1,
                  ne: str = "delik", esik: Optional[float] = None):
    if ne == "euler":
        return int(sum((-1) ** kk * len(v) for kk, v in K.items()))

    def sinir(kk: int) -> np.ndarray:
        if kk <= 0:
            return np.zeros((0, len(K.get(0, []))))
        ust = K.get(kk, [])
        alt = K.get(kk - 1, [])
        yer = {x: i for i, x in enumerate(alt)}
        B = np.zeros((len(alt), len(ust)))
        for j, x in enumerate(ust):
            for i in range(len(x)):
                yuz = x[:i] + x[i + 1:]
                if yuz in yer:
                    B[yer[yuz], j] = (-1.0) ** i
        return B

    if ne == "sınır":
        return sinir(int(k))

    Bk = sinir(int(k))
    Bk1 = sinir(int(k) + 1)
    n = len(K.get(int(k), []))
    D = np.zeros((n, n))
    if Bk1.size:
        D = D + Bk1 @ Bk1.T
    if Bk.size:
        D = D + Bk.T @ Bk
    if ne == "laplasyen":
        return D

    if D.size == 0:
        if ne == "betti":
            return 0
        return {"betti": 0.0, "betti0": 0.0, "boşluk": 0.0, "kayıp": 0.0,
                "delik_cezası": 0.0, "ada_cezası": 0.0}
    oz = np.linalg.eigvalsh((D + D.T) / 2.0)
    olcek = max(float(abs(oz).max()), 1e-30)
    e = esik
    if ne == "betti":
        if e is None:
            e = D.shape[0] * np.finfo(float).eps * max(1.0, olcek)
        return int(np.sum(oz <= e))
    if ne != "delik":
        raise ValueError("delik sayımının kipi bilinmiyor: %r" % (ne,))

    sifir = oz <= (1e-9 if e is None else e) * olcek
    kalan = oz[~sifir]
    b = int(sifir.sum())
    bosluk = float(kalan.min()) if kalan.size else 0.0
    delik_sayisi = float(b)
    ada = float(max(b - 1, 0))
    return {"betti": float(b), "betti0": float(b), "boşluk": bosluk,
            "delik_cezası": delik_sayisi, "ada_cezası": ada,
            "kayıp": ada if int(k) == 0 else delik_sayisi}


def iz(baglanti: Sequence[np.ndarray]) -> Dict[str, object]:
    W = None
    for U in baglanti:
        A = np.asarray(U, float)
        W = A if W is None else A @ W
    if W is None:
        W = np.eye(1)
    n = W.shape[0]
    sapma = float(np.linalg.norm(W - np.eye(n)) / math.sqrt(max(n, 1)))
    return {"W": W, "sapma": sapma, "kayıp": sapma}


def zirhla(hedef, ayar: Optional[ZirhAyari] = None,
                esik: float = 1e-9, S: Optional[np.ndarray] = None,
                Pi_betti: Optional[np.ndarray] = None,
                Pi_koho: Optional[np.ndarray] = None,
                u: Optional[Uzay] = None, okuma: Optional[np.ndarray] = None,
                onceki: Optional[np.ndarray] = None):
    if isinstance(hedef, np.ndarray) or not hasattr(hedef, "n"):
        H = np.atleast_2d(np.asarray(hedef, float))
        if S is not None or Pi_betti is not None or Pi_koho is not None:
            A = H
            for P in (S, Pi_betti, Pi_koho):
                if P is not None:
                    P = np.asarray(P, float)
                    A = P @ A @ P.T
            return A
        a = ayar or ZirhAyari()
        H = np.atleast_2d(np.asarray(H, float))
        n = int(H.shape[0])

        ust = np.triu(H)
        alt = np.tril(H).T
        ek = yama(ust, alt)
        s_hata = float(ek["uyumsuzluk"])
        S = ek["izdüşüm"]

        A = np.abs(H)
        dis = A[~np.eye(n, dtype=bool)]
        olcek = float(dis.max()) if dis.size else 0.0
        e_kompleks = max(float(esik), a.betti_kat * olcek)
        K = {0: [(i,) for i in range(n)],
             1: [(i, j) for i in range(n) for j in range(i + 1, n)
                 if A[i, j] > e_kompleks or A[j, i] > e_kompleks]}
        b1 = delik(K, k=1)
        b0 = delik(K, k=0)
        azami_b1 = max(1, n * (n - 1) // 2 - n + 1)

        adim = max(2, min(8, n))
        m = max(1, n // adim)
        baglanti = []
        for i in range(adim):
            b = i * m
            blok = H[b:b + m, b:b + m]
            if blok.shape != (m, m):
                blok = np.zeros((m, m))
            baglanti.append(np.eye(m) + 1e-3 * blok)
        h = iz(baglanti)

        toplam = zirh_kaybi(sheaf=s_hata,
                            betti=float(b1["delik_cezası"]) / azami_b1,
                            koho=float(b0["ada_cezası"]) / max(n, 1),
                            homotopi=float(h["sapma"]), ayar=a)

        H_zirhli = (S @ H @ S.T
                    if getattr(S, "shape", None) == H.shape else H)
        return H_zirhli, {
            "sheaf_uyumsuzluk": s_hata,
            "betti_delik_sayisi": float(b1["betti"]),
            "kohomoloji_tikaniklik": float(b0["ada_cezası"]),
            "homotopi_burulma": float(h["sapma"]),
            "sheaf_ceza": float(s_hata),
            "betti_ceza": float(b1["delik_cezası"]) / azami_b1,
            "koho_ceza": float(b0["ada_cezası"]) / max(n, 1),
            "homotopi_ceza": float(h["sapma"]),
            "toplam_kayip": float(toplam["kayıp"]),
            "mizan_dengesi": float(np.abs(np.mean(H_zirhli))),
        }
    y = hedef
    v = np.asarray(okuma, float).copy()
    k = len(v) // 2
    z = v[:k]

    if k >= 2:
        fark = np.diff(z)
        d = np.zeros_like(z)
        d[:-1] += 0.5 * fark
        d[1:] -= 0.5 * fark
        agirlik = 1.0 / (1.0 + float(np.mean(np.abs(fark))))
        z_yeni = z + (1.0 - agirlik) * d
        sheaf_d = float(np.linalg.norm(z_yeni - z))
        z = z_yeni
    else:
        sheaf_d = 0.0

    i = int(np.argmax(np.abs(z))) if k else 0
    isaret = 1.0 if (k == 0 or z[i] >= 0) else -1.0
    z = z * isaret

    from nefs.melekeler import devirler
    b0 = devirler("zincir_β0", z)
    ceza = float(np.exp(-0.25 * (b0 - 1) ** 2))
    z = z * ceza

    tik = 0.0
    if onceki is not None and len(onceki) == len(v):
        o = np.asarray(onceki, float)
        no = np.linalg.norm(o) + 1e-12
        oh = o / no
        tam = np.concatenate([z, v[k:]])
        paralel = oh * float(oh @ tam)
        dik = tam - paralel
        nd, nt = float(np.linalg.norm(dik)), float(np.linalg.norm(tam)) + 1e-12
        tik = nd / nt
        if tik > 0.9:
            tam = paralel + 0.1 * dik
        z, v = tam[:k], tam
    v = np.concatenate([z, v[k:]])

    if abs(isaret + 1.0) < 1e-9:
        y.tek_kapi(np.array([[1.0, 0.0], [0.0, -1.0]], dtype=y.tip))
    if ceza < 0.999:
        g = np.array([[1.0, 0.0], [0.0, ceza]], dtype=np.float64)
        g = g / (np.linalg.norm(g, axis=0, keepdims=True) + 1e-30)
        y.tek_kapi(g.astype(y.tip))

    return v, ZirhIzi(mertebe=u.mertebe, sheaf_duzeltme=sheaf_d,
                      homotopi_isaret=isaret, betti0=b0,
                      betti_ceza=ceza, tikaniklik=tik)


@dataclass
class ZirhAyari:
    w_sheaf: float = 1.0
    w_betti: float = 1.0
    w_koho: float = 1.0
    w_homotopi: float = 1.0
    w_nizam: float = 1.0
    tau: float = 4.0
    betti_kat: float = 0.3


def zirh_kaybi(sheaf: float = 0.0, betti: float = 0.0, koho: float = 0.0,
               homotopi: float = 0.0, nizam: float = 0.0,
               ayar: Optional[ZirhAyari] = None,
               q=None) -> Dict[str, object]:
    a = ayar or ZirhAyari()
    l = np.array([float(sheaf), float(betti), float(koho),
                  float(homotopi), float(nizam)])
    w = np.array([a.w_sheaf, a.w_betti, a.w_koho, a.w_homotopi,
                  a.w_nizam])
    t = float(a.tau)
    m = float(np.max(t * l))
    ls = m + math.log(float(np.sum(w * np.exp(t * l - m))))
    L = (ls - math.log(float(np.sum(w)))) / t
    out: Dict[str, object] = {
        "sheaf": float(l[0]), "betti": float(l[1]), "koho": float(l[2]),
        "homotopi": float(l[3]), "nizam": float(l[4]),
        "kayıp": float(L), "çelişkisiz": bool(L <= 1e-12)}
    if q is not None:
        try:
            out["mühür_tvd"] = float(
                muhru_stabilizerle_yuzlestir(q)["tvd"])
        except Exception as e:
            out["mühür_tvd"] = float("nan")
            out["mühür_hatası"] = str(e)
    return out


@dataclass
class ZirhIzi:
    mertebe: int
    sheaf_duzeltme: float
    homotopi_isaret: float
    betti0: int
    betti_ceza: float
    tikaniklik: float


def dalgayi_yokla(y: Yazmac, ornek: int = 256) -> np.ndarray:
    n = y.n
    idx = np.linspace(0, n - 1, min(ornek, n)).astype(int)
    R = y.tekil_yogunluklar(idx)
    z = R[:, 0, 0] - R[:, 1, 1]
    x = 2.0 * R[:, 0, 1]
    return np.concatenate([z, x])


def vietoris_rips(D: np.ndarray, eps: float, azami_boyut: int = 2
                  ) -> Dict[int, List[Tuple[int, ...]]]:
    D = np.asarray(D, float)
    N = D.shape[0]
    if D.shape != (N, N):
        raise ValueError("D kare olmalı")
    K: Dict[int, List[Tuple[int, ...]]] = {0: [(i,) for i in range(N)]}
    onceki = K[0]
    for k in range(1, azami_boyut + 1):
        simpleksler = []
        for s in itertools.combinations(range(N), k + 1):
            if all(D[a, b] <= eps for a, b in itertools.combinations(s, 2)):
                simpleksler.append(s)
        K[k] = simpleksler
        if not simpleksler:
            for kk in range(k + 1, azami_boyut + 1):
                K[kk] = []
            break
        onceki = simpleksler
    return K


def dogum_olum_cetveli(D: np.ndarray, esikler: Sequence[float],
                       k: int = 0, azami_boyut: int = 2,
                       tau: float = 0.0):
    egri = [delik(vietoris_rips(D, e, azami_boyut), k, "betti")
            for e in esikler]
    dogumlar: List[float] = []
    cubuklar: List[Tuple[float, float]] = []
    onceki = 0
    for e, b in zip(esikler, egri):
        if b > onceki:
            dogumlar.extend([e] * (b - onceki))
        elif b < onceki:
            for _ in range(onceki - b):
                if dogumlar:
                    cubuklar.append((dogumlar.pop(), e))
        onceki = b
    sonsuz = float(esikler[-1])
    for d in dogumlar:
        cubuklar.append((d, sonsuz))
    if tau > 0.0:
        cubuklar = [(b, d) for b, d in cubuklar if d - b >= tau]
    return {"eğri": egri, "çubuklar": cubuklar}


def cetveller_arasi_mesafe(B1: Sequence[Tuple[float, float]],
                           B2: Sequence[Tuple[float, float]],
                           kip: str = "bottleneck", p: float = 2.0) -> float:
    def kupsuz(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def kosegene(a):
        return abs(a[1] - a[0]) / 2.0

    B1, B2 = list(B1), list(B2)

    if kip == "wasserstein":
        kalan = list(B2)
        toplam = 0.0
        for x in B1:
            if kalan:
                i = int(np.argmin([kupsuz(x, y) for y in kalan]))
                d = kupsuz(x, kalan[i])
                if d <= kosegene(x):
                    kalan.pop(i)
                else:
                    d = kosegene(x)
            else:
                d = kosegene(x)
            toplam += d ** p
        for y in kalan:
            toplam += kosegene(y) ** p
        return toplam ** (1.0 / p)

    if kip != "bottleneck":
        raise ValueError("cetvel mesafesinin kipi bilinmiyor: %r" % (kip,))

    if not B1 and not B2:
        return 0.0

    def eslesme_var_mi(d: float) -> bool:
        tol = 1e-12
        n1, n2 = len(B1), len(B2)
        if n1 == 0 and n2 == 0:
            return True
        sol_n = n1 + n2
        komsu: List[List[int]] = [[] for _ in range(sol_n)]
        for i, a in enumerate(B1):
            for j, b in enumerate(B2):
                if kupsuz(a, b) <= d + tol:
                    komsu[i].append(j)
            if kosegene(a) <= d + tol:
                komsu[i].append(n2 + i)
        for j, b in enumerate(B2):
            if kosegene(b) <= d + tol:
                komsu[n1 + j].append(j)
            for i in range(n1):
                komsu[n1 + j].append(n2 + i)

        esles_sag: Dict[int, int] = {}

        def artir(u: int, gorulen: set) -> bool:
            for v in komsu[u]:
                if v in gorulen:
                    continue
                gorulen.add(v)
                if v not in esles_sag or artir(esles_sag[v], gorulen):
                    esles_sag[v] = u
                    return True
            return False

        return sum(1 for u in range(sol_n) if artir(u, set())) == sol_n

    adaylar = sorted({kupsuz(a, b) for a in B1 for b in B2}
                     | {kosegene(a) for a in B1}
                     | {kosegene(b) for b in B2} | {0.0})
    alt, ust = 0, len(adaylar) - 1
    if not eslesme_var_mi(adaylar[ust]):
        return float("inf")
    while alt < ust:
        orta = (alt + ust) // 2
        if eslesme_var_mi(adaylar[orta]):
            ust = orta
        else:
            alt = orta + 1
    return adaylar[alt]


def kahan_toplam(xs: Iterable[float]) -> float:
    s = 0.0
    c = 0.0
    for x in xs:
        y = float(x) - c
        t = s + y
        c = (t - s) - y
        s = t
    return s


def _mesafe(P: np.ndarray) -> np.ndarray:
    d = P[:, None, :] - P[None, :, :]
    return np.sqrt(np.sum(d * d, axis=2))


def _cember(n: int, r: float = 1.0) -> np.ndarray:
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack([r * np.cos(t), r * np.sin(t)], axis=1)


def _iki_cember(n: int) -> np.ndarray:
    a = _cember(n)
    b = _cember(n) + np.array([10.0, 0.0])
    return np.vstack([a, b])


SADAKAT_SIDDETI: Tuple[float, float, float] = (0.35, 0.25, 0.20)


HUKUM_ALANLARI: Tuple[str, ...] = ("mizan", "tasdik", "sukut", "nakz",
                                   "kelam", "gaye")

ALANLAR: Tuple[Tuple[str, int], ...] = (
    ("tasdik", 0), ("nakz", 0), ("mizan", 0), ("kelam", 0), ("sukut", 0),
)


class Usul:

    def __init__(self, ad: str, kur: Callable[[Dict[str, Onerme]], Onerme],
                 izah: str = "") -> None:
        self.ad = ad
        self.izah = izah
        self.formul = kur({a: deg(a) for a, _ in ALANLAR})


USULLER: Tuple[Usul, ...] = (
    Usul("tenakuzsuzluk",
         lambda v: degil(ve(v["tasdik"], v["nakz"])),
         "Bir hüküm hem mühürlenip hem nakzedilemez."),
    Usul("kâfi_sebep",
         lambda v: ise(v["tasdik"], v["mizan"]),
         "Mühür ancak delille olur: tasdik varsa mîzân da uyanık olmalı."),
    Usul("kelâm_şartı",
         lambda v: ise(v["kelam"], v["tasdik"]),
         "Mühürlenmemiş hükümle konuşulmaz."),
    Usul("sükût_şartı",
         lambda v: degil(ve(v["sukut"], v["tasdik"])),
         "Susarken mühürlemek olmaz (kütük H10)."),
)


SINIF_CIHETI: Dict[str, int] = {
    "kurucu": +1,
    "çözücü": -1,
    "koruyucu": 0,
}


NIZAM_BANDI: float = 0.05


KORUYUCU_BANDI: float = NIZAM_BANDI


_YASAK_CETVELI: Optional[Dict[str, List[Dict[str, int]]]] = None


def _yasak_cetveli() -> Dict[str, List[Dict[str, int]]]:
    global _YASAK_CETVELI
    if _YASAK_CETVELI is None:
        c: Dict[str, List[Dict[str, int]]] = {}
        for u in USULLER:
            adlar = sorted(u.formul.degiskenler())
            if not adlar:
                c[u.ad] = []
                continue
            t = Tablo(adlar)
            sutun = t.sutun(u.formul)
            c[u.ad] = [{ad: (i >> t.yer[ad]) & 1 for ad in adlar}
                       for i in range(1 << t.n) if not ((sutun >> i) & 1)]
        _YASAK_CETVELI = c
    return _YASAK_CETVELI


def vicdan(q=None, p=None, usuller=None, tur: int = 1,
                                   ne: str = "hepsi", orutu=None):
    if ne == "yasaklar":
        return _yasak_cetveli()

    def isaret(orutu_: Mapping[int, int]) -> float:
        if not orutu_:
            return 0.0
        yuv = sorted(int(k) for k in orutu_)
        bas, son = yuv[0], yuv[-1] + 1
        W: Dict[int, np.ndarray] = {}
        for j in yuv:
            T = np.zeros((2, 2, 2, 2))
            T[0, 0, 0, 0] = T[0, 1, 1, 0] = 1.0
            b = int(orutu_[j]) & 1
            T[1, b, b, 1] = 1.0
            W[j] = T
        return q.y.mpo_uygula(W, 2, bas=bas, son=son,
                              sol_sinir=np.array([1.0, -2.0]),
                              sag_sinir=np.array([1.0, 1.0]))

    if orutu is not None or ne == "örüntü":
        return isaret(orutu or {})

    kesme = 0.0

    if ne in ("işaret", "hepsi"):
        CZ = np.eye(4, dtype=np.float64)
        CZ[3, 3] = -1.0
        tas0 = q.kulli("tasdik", 0)
        tas1 = q.kulli("tasdik", 1)
        nak0 = q.kulli("nakz", 0)
        miz0 = q.kulli("mizan", 0)
        kel0 = q.kulli("kelam", 0)
        gay0 = q.kulli("gaye", 0)
        q.uzak_cift(tas0, nak0, CZ)
        q.tek(tas1, degil_x())
        q.cift(tas0, CZ)
        q.tek(tas1, degil_x())
        q.tek(miz0, degil_x())
        q.uzak_cift(tas0, miz0, CZ)
        q.tek(miz0, degil_x())
        q.tek(tas0, degil_x())
        q.uzak_cift(kel0, tas0, CZ)
        q.tek(tas0, degil_x())
        q.uzak_cift(q.kulli("sukut", 0), tas0, CZ)
        q.tek(gay0, degil_x())
        q.uzak_cift(tas0, gay0, CZ)
        q.tek(gay0, degil_x())
        q.tek(tas0, degil_x())
        q.uzak_cift(tas0, gay0, CZ)
        q.tek(tas0, degil_x())

    if ne in ("usul", "hepsi"):
        us = USULLER if usuller is None else usuller
        _, kac = q._alan["tertip"]
        yuv = [q.kulli("tertip", j) for j in range(kac)]
        q.tek_yigin(yuv, np.stack([donme(0.25 * math.pi)] * len(yuv)))
        cetvel = _yasak_cetveli()
        yer = dict(ALANLAR)
        for i, u in enumerate(us[:kac]):
            for yasak in cetvel.get(u.ad, []):
                o = {q.kulli(ad, yer[ad]): b for ad, b in yasak.items()}
                o[yuv[i]] = 1
                kesme += isaret(o)

    if ne in ("intaç", "hepsi"):
        yuv = sorted({q.kulli(ad, j) for ad in HUKUM_ALANLARI
                      for j in range(q._alan[ad][1])})
        for _ in range(max(1, int(tur))):
            q.tek_yigin(yuv, np.stack([donme(-0.25 * math.pi)] * len(yuv)))
            kesme += isaret({int(j): 0 for j in
                             range(min(yuv), max(yuv) + 1)})
            q.tek_yigin(yuv, np.stack([donme(0.25 * math.pi)] * len(yuv)))

    return float(kesme)


def taahhude_yuzlestir(sinif=None, dS=None, nefs=None,
                       E=None, ayar=None):
    def ihlal(sn: str, d: float) -> float:
        c = SINIF_CIHETI.get(str(sn), 0)
        d = float(d)
        eksik = (abs(d) - NIZAM_BANDI) if c == 0 else (NIZAM_BANDI - c * d)
        return float(np.tanh(max(0.0, eksik)))

    if sinif is not None and dS is not None:
        return ihlal(sinif, dS)

    from .melekeler import qsicil

    if nefs is None:
        from .musahede import gorevleri_getir

        from main.egitim import KISA_CPU
        from .melekeler import QNefs
        from .qegitim import belirtecleri_kodla, ornekler
        a = ayar or KISA_CPU
        nefs = QNefs(a.tohum, a.qayar())
        nefs.idrak_et(np.zeros((2, a.veri_lifi)))
        veri = ornekler(gorevleri_getir("training")[:6], azami=2,
                        pencere=a.pencere, sozluk=a.sozluk,
                        taban=int(a.veri_lifi),
                        basamak=int(a.belirtec_basamak))
        from .qegitim import ornek_bol
        E = np.stack([belirtecleri_kodla(b, a.veri_lifi, a.veri_lifi)
                      for b, _h, _c, _m in (ornek_bol(o) for o in veri)])
    _q = nefs.idrak_et(E, olcum=True)
    dSler = dict(getattr(_q, "dS", {}) or {})
    assert dSler, (
        "ΔS BOŞ -- meleke ölçümü kapalı olmalı (``meleke_olcumu=0``); "
        "nizam taahhüdü ölçüsüz yüzleştirilemez")
    sic = qsicil()
    out: List[Dict[str, object]] = []
    for no in sorted(dSler):
        m = sic[no]
        d = float(dSler[no])
        ih = ihlal(m.SINIF, d)
        out.append({"no": no, "ad": m.ad, "sınıf": m.SINIF,
                    "ΔS": d, "ihlâl": ih, "uydu_mu": ih <= 1e-9})
    return out


def muhru_stabilizerle_yuzlestir(q, alanlar: Sequence[str] = ("tasdik", "nakz"),
                                 n: int = 0,
                                 cz_ciftleri: Sequence[Tuple[int, int]] = (),
                                 z_yuvalari: Sequence[int] = ()
                                 ) -> Dict[str, object]:
    def kur(nn: int, cz, zy) -> StabilizerDurum:
        d = StabilizerDurum.arti(int(nn))
        for a in zy:
            d.z(int(a))
        for a, b in cz:
            d.cz(int(a), int(b))
        return d

    def dagilim(d: StabilizerDurum) -> np.ndarray:
        m = d.n
        if m > 14:
            raise ValueError("yüzleştirme için n ≤ 14 (2^n açılıyor)")
        Y = np.array([[(i >> j) & 1 for j in range(m)] for i in range(1 << m)],
                     dtype=np.int64)
        P = np.abs(np.asarray(d.genlik(Y))) ** 2
        t = float(P.sum())
        return P / t if t > 1e-30 else np.full(1 << m, 1.0 / (1 << m))

    if q is None:
        d = kur(n, cz_ciftleri, z_yuvalari)
        return {"kübit": int(n), "kod": d, "P_stab": dagilim(d)}

    yuv: List[int] = []
    for ad in alanlar:
        _, kac = q._alan[ad]
        yuv += [q.kulli(ad, j) for j in range(kac)]
    yuv = sorted(set(yuv))
    m = len(yuv)
    bas = min(yuv)
    if max(yuv) - bas + 1 != m:
        raise ValueError("yüzleştirme için alanlar bitişik olmalı")

    P_mps = np.asarray(q.blok_dagilimi(bas, m), float).ravel()

    yerel = {j: i for i, j in enumerate(yuv)}
    ilk, son = alanlar[0], alanlar[-1]
    cz = [(yerel[q.kulli(ilk, 0)], yerel[q.kulli(son, 0)])]
    P_stab = dagilim(kur(m, cz, ()))

    idx = np.array([int("".join(str((i >> j) & 1)
                               for j in range(m - 1, -1, -1)), 2)
                    for i in range(1 << m)])
    P_stab = P_stab[idx]

    return {"kübit": m, "P_mps": P_mps, "P_stab": P_stab,
            "tvd": 0.5 * float(np.sum(np.abs(P_mps - P_stab))),
            "kapsanan_şart": len(cz),
            "kapsanmayan": "menfî kontrollü ve üç kontrollü şartlar"}


def holonomi(kenar_fazlari: Sequence[float]) -> complex:
    return complex(np.exp(1j * float(np.sum(kenar_fazlari))))


def cevrim_egriligi(kenar_fazlari: Sequence[float],
                    yuz_var_mi: bool = False) -> Dict[str, object]:
    W = holonomi(kenar_fazlari)
    return {"F_yerel_sıfır_mı": True, "yüz_var_mı": yuz_var_mi,
            "holonomi": W, "holonomi_trivial_mi": bool(abs(W - 1) < 1e-12),
            "faz": float(np.angle(W)),
            "toplam_akı_bölü_2pi": float(np.sum(kenar_fazlari)
                                         / (2 * math.pi))}


def duz_mu(kenar_fazlari: Sequence[float]) -> bool:
    return True


def aharonov_bohm(N: int = 8, aki_bolu_2pi: float = 0.37
                  ) -> Dict[str, object]:
    a = np.full(N, 2 * math.pi * aki_bolu_2pi / N)
    d = cevrim_egriligi(a, yuz_var_mi=False)
    d["disk_olsaydı_F"] = 2 * math.pi * aki_bolu_2pi
    d["|W−1|"] = float(abs(d["holonomi"] - 1))
    return d


def _rapor_bukum() -> str:
    s = []
    s.append("=== M20: tünelleme O(1) DEĞİL, üstel pahalı ===")
    s.append("  genişlik      γ          T = e^{−γ}     beklenen deneme")
    for d in tunel_maliyet_cetveli((1, 2, 4, 8, 16)):
        s.append("  %8.0f   %8.4f      %.3e      %.3e"
                 % (d["genişlik"], d["γ"], d["T"], d["beklenen_deneme"]))
    s.append("  Risalenin kendi formülü T = e^{−γ} diyor; aynı sayfada")
    s.append("  'O(1) mertebesinde geçilir' demek onunla çelişiyor.")
    s.append("  Doğru kazanç: klasikte SIFIR olan olasılık POZİTİF oluyor.")

    s.append("\n=== M21: düz bağlantı, trivial OLMAYAN holonomi ===")
    for aki in (0.0, 0.25, 0.37, 0.5, 1.0):
        d = aharonov_bohm(8, aki)
        s.append("  akı/2π=%.2f   yerel F=0 mı? %s   yüz var mı? %s   "
                 "W=%+.4f%+.4fi   |W−1|=%.4f   trivial mi? %s"
                 % (aki, d["F_yerel_sıfır_mı"], d["yüz_var_mı"],
                    d["holonomi"].real, d["holonomi"].imag, d["|W−1|"],
                    d["holonomi_trivial_mi"]))
    s.append("  akı tam sayı olduğunda holonomi trivial oluyor; arada")
    s.append("  DEĞİL. F her hâlde sıfır. Yani 'F=0 ⟹ ΔΦ=0' yanlış;")
    s.append("  doğru ölçüt W(γ)=1'dir. (Aharonov–Bohm.)")

    s.append("\n=== M22: GRAPE gradyanı O(Δt²) yaklaşımı ===")
    r = np.random.default_rng(1)
    n = 4

    def herm(sd):
        A = (np.random.default_rng(sd).normal(size=(n, n))
             + 1j * np.random.default_rng(sd + 99).normal(size=(n, n)))
        return A + A.conj().T

    H0, Hk = herm(1), [herm(2), herm(3)]
    psi0 = np.zeros(n, complex); psi0[0] = 1
    hedef = np.zeros(n, complex); hedef[n - 1] = 1
    s.append("     M      Δt      sonlu fark      GRAPE        fark      "
             "fark/Δt²")
    for M in (10, 20, 40, 80, 160):
        om = [np.full(M, 0.3), np.full(M, -0.2)]
        dt = 1.0 / M
        j, k = M // 3, 0
        sf = sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        g = grape_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        s.append("  %5d  %.5f  %+.8f  %+.8f  %.2e  %.4f"
                 % (M, dt, sf, g, abs(g - sf), abs(g - sf) / dt ** 2))
    s.append("  'fark/Δt²' sütunu sabitleniyor: hata tam olarak O(Δt²).")
    s.append("  Kaynak bunu EŞİTLİK olarak yazıyor; yaklaşımdır.")

    s.append("\n=== Tam (Fréchet) gradyan sonlu farkla uyuşuyor mu? ===")
    for M in (10, 20, 40):
        om = [np.full(M, 0.3), np.full(M, -0.2)]
        j, k = M // 3, 0
        sf = sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        tam = tam_gradyan(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        yak = grape_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        s.append("  M=%3d  sonlu fark=%+.10f   tam=%+.10f (fark %.2e)   "
                 "GRAPE=%+.10f (fark %.2e)"
                 % (M, sf, tam, abs(tam - sf), yak, abs(yak - sf)))

    s.append("\n=== GRAPE gerçekten çalışıyor mu? ===")
    d = grape_kos(H0, Hk, psi0, hedef, 1.0, M=40, tur=300)
    s.append("  başlangıç sadakat = %.6f   son sadakat = %.6f"
             % (d["seyir"][0], d["sadakat"]))
    s.append("  tekdüze artıyor mu? %s   (tur sayısı %d)"
             % (d["tekdüze_mi"], len(d["seyir"])))
    s.append("  Yaklaşık gradyan eniyilemeyi bozmuyor: adım kabul ölçütü")
    s.append("  sadakati doğrudan sınadığı için yanlış yöne gidilmiyor.")
    return "\n".join(s)

def rapor() -> str:
    s: List[str] = ["ZIRH ÇİPİ -- Küme 3 tevhidi"]
    s.append("")
    s.append("=" * 70)
    s.append("  DÖRTLÜ TOPOLOJİK SÜZGEÇ -- gayenin kendisi")
    s.append("=" * 70)
    s += ["DÖRTLÜ TOPOLOJİK ZIRH -- gayenin kendisi", ""]

    s.append("=== Betti: delik VAR mı? (kırmızı/yeşil) ===")
    aci = np.linspace(0, 2 * math.pi, 8, endpoint=False)
    cember = np.stack([np.cos(aci), np.sin(aci)], axis=1)
    Dc = np.sqrt(((cember[:, None] - cember[None]) ** 2).sum(2))
    Kc = vietoris_rips(Dc, 0.9, azami_boyut=2)
    r1 = delik(Kc, 1)
    s.append("  çember (delik)  : b₁=%.0f  boşluk=%.4f  kayıp=%.1f"
             % (r1["betti"], r1["boşluk"], r1["kayıp"]))
    rng = np.random.default_rng(0)
    disk = rng.normal(size=(14, 2))
    disk = disk / np.maximum(np.linalg.norm(disk, axis=1, keepdims=True), 1)
    disk = disk * rng.uniform(0, 1, (14, 1)) ** 0.5
    Dd = np.sqrt(((disk[:, None] - disk[None]) ** 2).sum(2))
    Kd = vietoris_rips(Dd, 1.2, azami_boyut=2)
    r2 = delik(Kd, 1)
    s.append("  dolu disk       : b₁=%.0f  boşluk=%.4f  kayıp=%.1f"
             % (r2["betti"], r2["boşluk"], r2["kayıp"]))

    s.append("")
    s.append("=== Kohomoloji: mana adaları (b₀ − 1) ===")
    iki = np.vstack([rng.normal(size=(6, 2)) * 0.2,
                     rng.normal(size=(6, 2)) * 0.2 + 10.0])
    Di = np.sqrt(((iki[:, None] - iki[None]) ** 2).sum(2))
    Ki = vietoris_rips(Di, 0.8, azami_boyut=1)
    k1 = delik(Ki, 0)
    s.append("  iki kopuk ada   : b₀=%.0f  kayıp=%.1f   ← KIRMIZI"
             % (k1["betti0"], k1["kayıp"]))
    Kb = vietoris_rips(Di, 16.0, azami_boyut=1)
    k2 = delik(Kb, 0)
    s.append("  bağlanmış       : b₀=%.0f  kayıp=%.1f"
             % (k2["betti0"], k2["kayıp"]))

    s.append("")
    s.append("=== Sheaf ve Homotopi ===")
    a = np.array([1.0, 2.0, 3.0])
    s.append("  uyumlu ek yeri  : ‖ΔRes‖² = %.3e"
             % yama(a, a)["uyumsuzluk"])
    s.append("  uyumsuz ek yeri : ‖ΔRes‖² = %.3f   ← KIRMIZI"
             % yama(a, a + np.array([0.0, 0.5, -0.3]))["uyumsuzluk"])
    from nefs.zihin_durumu import donme
    kapali = [donme(0.4), donme(-0.4)]
    acik = [donme(0.4), donme(0.1)]
    s.append("  kapanan çevrim  : |W−I| = %.3e"
             % iz(kapali)["sapma"])
    s.append("  kapanmayan      : |W−I| = %.4f   ← KIRMIZI"
             % iz(acik)["sapma"])

    s.append("")
    s.append("=== Küllî zırh kaybı (yumuşak âzamî) ===")
    s.append("  dördü de sıfır      : L = %.3e"
             % zirh_kaybi()["kayıp"])
    s.append("  yalnız biri bozuk   : L = %.4f   (düz ortalama %.4f olurdu)"
             % (zirh_kaybi(betti=1.0)["kayıp"], 1.0 / 4.0))
    s.append("  dördü de bozuk      : L = %.4f"
             % zirh_kaybi(1.0, 1.0, 1.0, 1.0)["kayıp"])
    s.append("")
    s.append("=" * 70)
    s.append("  OPERATÖRE ZIRH GİYDİRME")
    s.append("=" * 70)
    rng = np.random.default_rng(0)
    s += ["OPERATÖRE ZIRH GİYDİRME", ""]
    for ad, H in (("rastgele", rng.normal(size=(12, 12))),
                  ("birim (temiz)", np.eye(12)),
                  ("tam bağlı", np.ones((12, 12)))):
        _Hz, r = zirhla(H)
        s.append("  %-14s sheaf=%.4f betti=%.0f koho=%.4f homotopi=%.4f "
                 "toplam=%.4f"
                 % (ad, r["sheaf_uyumsuzluk"], r["betti_delik_sayisi"],
                    r["kohomoloji_tikaniklik"], r["homotopi_burulma"],
                    r["toplam_kayip"]))
    s.append("")
    s.append("  Satırlar birbirinden AYRI çıkmalı; hepsi aynı çıkarsa")
    s.append("  zırh ölçmüyor demektir.")
    s.append("")
    s.append("=" * 70)
    s.append("  DALGAYA ZIRH GİYDİRME")
    s.append("=" * 70)
    from idrak.kategori import Uzay

    s += ["ENİNE TOPOLOJİK ZIRH -- dört süzgeç, dördü de ısırıyor mu?", ""]
    n = 24
    k = n

    def kos(z: np.ndarray, onceki=None) -> ZirhIzi:
        y = Yazmac(8, bag=4, tohum=0)
        v = np.concatenate([z, np.zeros_like(z)])
        u = Uzay(yuva=0, mertebe=1, tam_kuruldu=True, denetlendi=True,
                 baglayici=0, tip_ozeti="sınama")
        return zirhla(y, u=u, okuma=v, onceki=onceki)[1]

    duz = np.linspace(-0.2, 0.2, k)
    kopuk = duz.copy()
    kopuk[k // 2:] += 3.0
    dalgali = np.sin(np.linspace(0, 12, k))
    menfi = -np.abs(duz) - 0.5

    s.append("  %-14s %-12s %-8s %-10s %s"
             % ("okuma", "sheaf", "işaret", "β₀", "betti cezası"))
    for ad, z in (("düz", duz), ("kopuk", kopuk),
                  ("dalgalı", dalgali), ("menfî", menfi)):
        zi = kos(z)
        s.append("  %-14s %-12.4f %-8.0f %-10d %.4f"
                 % (ad, zi.sheaf_duzeltme, zi.homotopi_isaret,
                    zi.betti0, zi.betti_ceza))

    s.append("")
    s.append("  Kohomoloji: **önceki okumaya dik** bileşen yutuluyor mu?")
    onc = np.concatenate([duz, np.zeros_like(duz)])
    for ad, z in (("aynı yön", duz), ("dik yön", dalgali)):
        zi = kos(z, onceki=onc)
        s.append("    %-10s tıkanıklık = %.4f" % (ad, zi.tikaniklik))
    s.append("    (dik yönde tıkanıklık 1'e yaklaşmalı; yaklaşmıyorsa")
    s.append("     dördüncü süzgeç ölüdür.)")
    s.append("")
    s.append("=" * 70)
    s.append("  TOPOLOJİ: kompleks, Betti, barkod, mesafe")
    s.append("=" * 70)
    from fractions import Fraction
    s += []

    s.append("=== ∂∘∂ = 0 ölçülüyor ===")
    rng = np.random.default_rng(0)
    P = rng.normal(size=(9, 3))
    K = vietoris_rips(_mesafe(P), 2.2, azami_boyut=3)
    s.append("  simpleks sayıları: "
             + ", ".join(f"|C_{k}|={len(v)}" for k, v in sorted(K.items())))
    for k in (1, 2, 3):
        B1 = delik(K, k, "sınır")
        B2 = delik(K, k + 1, "sınır")
        if B1.size and B2.size:
            s.append(f"  ‖∂_{k}∘∂_{k+1}‖∞ = "
                     f"{np.max(np.abs(B1 @ B2)):.2e}")

    s.append("\n=== Bilinen şekillerde Betti sayıları ===")
    ornekler = [
        ("3 ayrık nokta", np.array([[0., 0.], [10., 0.], [0., 10.]]),
         0.5, (3, 0)),
        ("çember (16 nokta)", _cember(16), 0.5, (1, 1)),
        ("iki çember", _iki_cember(12), 0.6, (2, 2)),
        ("dolu üçgen", np.array([[0., 0.], [1., 0.], [0.5, 0.87]]),
         1.5, (1, 0)),
    ]
    for ad, P_, eps, (b0, b1) in ornekler:
        Kx = vietoris_rips(_mesafe(P_), eps, azami_boyut=2)
        o0, o1 = delik(Kx, 0, "betti"), delik(Kx, 1, "betti")
        s.append(f"  {ad:20s} ε={eps:.2f}  β₀={o0} (bekl. {b0})"
                 f"   β₁={o1} (bekl. {b1})"
                 f"   χ={delik(Kx, 0, chr(101)+chr(117)+chr(108)+chr(101)+chr(114))}")

    s.append("\n=== K25: Tikhonov çekirdeği yok ediyor ===")
    Kc = vietoris_rips(_mesafe(_cember(16)), 0.5, azami_boyut=2)
    D0 = delik(Kc, 0, "laplasyen")
    oz = np.linalg.eigvalsh(D0)
    s.append(f"  ker Δ₀ boyutu = {int(np.sum(np.abs(oz) < 1e-9))}  (β₀)")
    for eps in (1e-6, 1e-3):
        oz_e = np.linalg.eigvalsh(D0 + eps * np.eye(D0.shape[0]))
        s.append(f"  ε={eps:.0e}: ker(Δ₀+εI) boyutu = "
                 f"{int(np.sum(np.abs(oz_e) < 1e-9))}"
                 f"   ε-eşikli sayım = {int(np.sum(oz_e <= eps + 1e-9))}")
    s.append("  Düzenleme çekirdeği siliyor; Betti eşikli SAYIMLA okunmalı.")

    s.append("\n=== Kalıcılık: gürültü ile hakiki delik ===")
    r = np.random.default_rng(3)
    P2 = _cember(24) + 0.03 * r.normal(size=(24, 2))
    esikler = np.linspace(0.05, 2.2, 40)
    cub0 = dogum_olum_cetveli(_mesafe(P2), esikler, k=0)["çubuklar"]
    cub1 = dogum_olum_cetveli(_mesafe(P2), esikler, k=1)["çubuklar"]
    s.append(f"  β₀ barkodu: {len(cub0)} çubuk, "
             f"en uzun {max(d - b for b, d in cub0):.3f}")
    s.append(f"  β₁ barkodu: {len(cub1)} çubuk, "
             f"en uzun {max((d - b for b, d in cub1), default=0):.3f}")
    for tau in (0.0, 0.1, 0.5, 1.0):
        s.append(f"    τ={tau:.1f} süzgecinden geçen: "
                 f"β₀ {len([c for c in cub0 if c[1] - c[0] >= tau])}, "
                 f"β₁ {len([c for c in cub1 if c[1] - c[0] >= tau])}")

    s.append("\n=== Bottleneck mesafesi ===")
    A = [(0.0, 1.0), (0.2, 0.9)]
    B = [(0.0, 1.0), (0.2, 0.9)]
    s.append(f"  aynı barkod: {cetveller_arasi_mesafe(A, B):.6f}  (0 olmalı)")
    C = [(0.0, 1.0), (0.2, 0.9), (0.5, 0.52)]
    s.append(f"  kısa bir çubuk eklendi: {cetveller_arasi_mesafe(A, C):.6f}"
             f"   (o çubuğun köşegene mesafesi = {(0.52-0.5)/2:.3f})")
    Dd = [(0.0, 1.3), (0.2, 0.9)]
    s.append(f"  bir çubuk 0.3 uzadı: {cetveller_arasi_mesafe(A, Dd):.6f}")
    s.append(f"  boş barkodla: {cetveller_arasi_mesafe(A, []):.6f}"
             f"   (en uzun çubuğun yarısı = {1.0/2:.3f})")

    s.append("\n=== Kahan toplaması: hata N'den bağımsız (K32) ===")
    s.append("        N     naif hata     Kahan hata    naif/Kahan")
    for N in (1_000, 10_000, 100_000):
        rr = np.random.default_rng(N)
        xs = rr.normal(0, 1, N) * 10.0 ** rr.integers(-8, 8, N)
        tam = float(sum(Fraction(float(x)) for x in xs))
        olcek = float(np.sum(np.abs(xs)))
        naif = 0.0
        for x in xs:
            naif += float(x)
        h_naif = abs(naif - tam) / olcek
        h_kahan = abs(kahan_toplam(xs) - tam) / olcek
        oran = h_naif / h_kahan if h_kahan > 0 else float("inf")
        s.append(f"  {N:9d}   {h_naif:.3e}    {h_kahan:.3e}"
                 f"    {oran:>8.1f}×")
    eps = np.finfo(float).eps
    s.append(f"  makine epsilon = {eps:.3e}; Kahan hatası birkaç eps")
    s.append("  mertebesinde ve N ile BÜYÜMÜYOR — kaidenin söylediği bu.")
    s.append("")
    s.append("=" * 70)
    s.append("  DOLAŞIKLIK NİZAMI -- ilan ile ölçümün yüzleşmesi")
    s.append("=" * 70)
    s += ["=== DOLAŞIKLIK NİZAMI -- ilan ile ölçümün yüzleştirilmesi ===",
         "",
         "Her meleke bir SINIF ilan eder; taahhüdü ΔS'in bölgesidir:",
         "  kurucu ΔS≥+%.2f   çözücü ΔS≤−%.2f   koruyucu |ΔS|≤%.2f"
         % (NIZAM_BANDI, NIZAM_BANDI, NIZAM_BANDI),
         "",
         "  𝒪   meleke               sınıf      ΔS       ihlâl"]
    satir = taahhude_yuzlestir()
    uyan = 0
    for r in satir:
        uyan += bool(r["uydu_mu"])
        s.append("  %-3d %-20s %-10s %+8.4f  %.4f%s"
                 % (r["no"], r["ad"], r["sınıf"], r["ΔS"], r["ihlâl"],
                    "" if r["uydu_mu"] else "   ← İHLÂL"))
    s += ["",
          "%d/%d meleke ilanına uyuyor." % (uyan, len(satir)),
          "",
          "İhlâl bir kusur değil bir **eğitim işareti**dir: ölçü",
          "`nefs/kulli_kayip.py`nin öğrenilebilir kaybına girer, yani",
          "meleke 'çözücüyüm' dediği için değil FİİLEN çözdüğü için",
          "çözücü olur. 𝒪₅ Tecrit'in H148'de açık kalan borcu budur:",
          "sabit bir üniter keyfî bir durumu çözemez; çözücülük ancak",
          "eğitilerek kazanılır, iddia edilerek değil."]
    s.append("")
    s.append("=" * 70)
    s.append("  STABILIZER MÜHRÜ")
    s.append("=" * 70)
    s += ["MANTIK KOD UZAYI -- stabilizer ile MPS'in yüzleştirilmesi", ""]

    s.append("  1) Clifford devresinde dağılım TAM mı?")
    for n, cz in ((4, [(0, 1)]), (6, [(0, 1), (2, 3), (4, 5)]),
                  (8, [(i, i + 1) for i in range(7)])):
        r = muhru_stabilizerle_yuzlestir(None, n=n, cz_ciftleri=cz)
        d, P = r["kod"], r["P_stab"]
        s.append("    n=%d, %d CZ → Σ P = %.15f, sıfır olmayan hâl %d/%d"
                 % (n, len(cz), float(P.sum()),
                    int(np.sum(P > 1e-15)), 1 << n))
    s.append("    (Σ P tam 1; hiçbir bağ boyutu, hiçbir kesme yok.)")

    s.append("")
    s.append("  2) MPS ile yüzleştirme (tasdik ⊗ nakz bloğu)")
    from nefs.zihin_durumu import QAyar, QYazmac
    rng = np.random.default_rng(0)
    for bag in (4, 8, 16):
        q = QYazmac(4, QAyar())
        q.kodla(rng.normal(size=(4, 8)))
        q.superpozisyon()
        q.harman()
        r = muhru_stabilizerle_yuzlestir(q, alanlar=("tenakuz", "tasdik"))
        s.append("    χ=%-3d kübit=%d  TVD(MPS, stabilizer) = %.4f"
                 % (bag, r["kübit"], r["tvd"]))
    s.append("    Kapsanmayan: %s" % r["kapsanmayan"])
    s.append("    (TVD büyük çıkması bir kusur DEĞİL bir teşhistir: iki")
    s.append("     temsil aynı devreyi taşımıyor -- MPS akışın tamamını,")
    s.append("     stabilizer yalnız iki-kontrollü müsbet şartı görüyor.)")
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
