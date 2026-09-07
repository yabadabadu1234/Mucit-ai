from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["DEVRELER", "usul_sec", "usul_imzasi", "UsulAyari", "USULLER", "gedik_bul", "sefer", "usul_kos",
           "usul_beyani", "usul_sifirla"]


USULLER: Tuple[str, ...] = (
    "Barbara",
    "Celarent",
    "Cesare",
    "Darapti",
    "Baroco",
    "ModusPonens",
    "Munfasıla",
    "Temsil",
    "AksiMüstevî",
    "Sorites",
)


@dataclass
class UsulAyari:

    acik: int = 1
    had: float = 0.0
    sefer: int = 4
    lan_esigi: float = 1e-6


_SAYAC: Dict[str, float] = {
    "yoklama": 0.0, "sefer": 0.0, "istihrac": 0.0, "cerh": 0.0,
    "tahkik": 0.0, "uncompute": 0.0, "lan_k": 0.0, "artık": 0.0,
    "tasfiye": 0.0}
_USUL_SAYAC: Dict[str, int] = {}


def gedik_bul(omegalar: Sequence[float],
              ayar: Optional[UsulAyari] = None) -> List[int]:
    a = ayar or UsulAyari()
    _SAYAC["yoklama"] += 1.0
    if not int(a.acik):
        return []
    om = np.asarray(list(omegalar), float)
    if om.size == 0:
        return []
    if float(a.had) != 0.0:
        esik = float(a.had)
    else:
        eps = float(np.finfo(om.dtype).eps)
        cz = float(np.arccos(np.clip(1.0 - np.sqrt(eps), -1.0, 1.0)))
        esik = float(np.median(om)) - cz
    karanlik = np.nonzero(om < esik)[0]
    if karanlik.size == 0 and om.size >= 2:
        karanlik = np.asarray([int(np.argmin(om))])
    sira = karanlik[np.argsort(om[karanlik])]
    return [int(i) for i in sira[:max(0, int(a.sefer))]]


def _bir(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-300 else v


def _householder(v: np.ndarray, x: np.ndarray) -> np.ndarray:
    v = _bir(v)
    return x - 2.0 * complex(np.vdot(v, x)) * v


def _dikleştir(v: np.ndarray, x: np.ndarray) -> np.ndarray:
    v = _bir(v)
    return x - complex(np.vdot(v, x)) * v


def _barbara(K, G):
    a, b, c = K[0], K[1], K[-1]
    return G(b, c) @ (G(a, b) @ a), b


def _celarent(K, G):
    a, b, c = K[0], K[1], K[-1]
    return _householder(c, G(a, b) @ a), b


def _cesare(K, G):
    a, b, c = K[0], K[1], K[-1]
    return _dikleştir(c, a), b


def _darapti(K, G):
    a, b, c = K[0], K[1], K[-1]
    return _bir(b + c), b


def _baroco(K, G):
    a, b, c = K[0], K[1], K[-1]
    return _householder(b, a), b


def _modus_ponens(K, G):
    a, b, c = K[0], K[1], K[-1]
    return G(a, c) @ a, b


def _munfasila(K, G):
    a, b, c = K[0], K[1], K[-1]
    return _householder(a, c), b


def _temsil(K, G):
    a, b, c = K[0], K[1], K[-1]
    illet = complex(np.vdot(a, b))
    return _bir(illet * c + (1.0 - abs(illet)) * b), b


def _aksi_mustevi(K, G):
    a, b, c = K[0], K[1], K[-1]
    faz = complex(np.vdot(a, c))
    faz = faz / abs(faz) if abs(faz) > 1e-300 else 1.0 + 0j
    return _bir(faz * c), b


def _sorites(K, G):
    x = K[0]
    for i in range(len(K) - 1):
        x = G(K[i], K[i + 1]) @ x
    return x, K[len(K) // 2]


DEVRELER: Dict[str, Any] = {
    "Barbara": _barbara,
    "Celarent": _celarent,
    "Cesare": _cesare,
    "Darapti": _darapti,
    "Baroco": _baroco,
    "ModusPonens": _modus_ponens,
    "Munfasıla": _munfasila,
    "Temsil": _temsil,
    "AksiMüstevî": _aksi_mustevi,
    "Sorites": _sorites,
}

_IMZA: Dict[str, np.ndarray] = {}


def usul_imzasi(boy: int = 8) -> Dict[str, np.ndarray]:
    from .kulli_mizan import givens
    from .mukayese import nesnelestir, bargmann
    anahtar = "%d" % int(boy)
    if _IMZA.get("__boy__") is not None and str(
            _IMZA["__boy__"]) == anahtar:
        return {k: v for k, v in _IMZA.items() if k != "__boy__"}
    _IMZA.clear()
    E = np.eye(int(boy), dtype=complex)
    kanon = [E[0], _bir(E[0] + E[1]), _bir(E[1] + 1j * E[2]),
             _bir(E[2] - E[0])]
    for ad, dev in DEVRELER.items():
        netice, orta = dev(kanon, givens)
        o = bargmann([kanon[0], _bir(np.asarray(netice)), kanon[-1]])
        _IMZA[ad] = nesnelestir(o, int(boy))
    _IMZA["__boy__"] = anahtar
    return {k: v for k, v in _IMZA.items() if k != "__boy__"}


def usul_sec(koseler: Sequence[np.ndarray]) -> Dict[str, Any]:
    from .kulli_mizan import givens
    from .mukayese import bargmann, nesnelestir, swap_testi
    K = [_bir(np.asarray(k, complex).reshape(-1)) for k in koseler]
    boy = int(K[0].size)
    imza = usul_imzasi(min(boy, 8))
    o = bargmann([K[0], K[1], K[-1]])
    parmak = nesnelestir(o, min(boy, 8))
    en, ad_en = -1.0, "Barbara"
    olcu: Dict[str, float] = {}
    for ad, im in imza.items():
        v = float(swap_testi(parmak, im)["örtüşme"])
        olcu[ad] = v
        if v > en:
            en, ad_en = v, ad
    return {"usul": ad_en, "örtüşme": float(en), "ölçü": olcu,
            "r": float(o["r"]), "Φ": float(o["Φ"])}


def _gaye(omega: float) -> str:
    if omega < -0.5:
        return "cerh"
    if omega < 0.0:
        return "tahkik"
    return "istihrac"


def sefer(koseler: Sequence[np.ndarray], omega: float,
          mudrike: np.ndarray, ayar: Optional[UsulAyari] = None
          ) -> Dict[str, Any]:
    from .kulli_mizan import givens
    from .mukayese import swap_testi
    a = ayar or UsulAyari()
    K = [np.asarray(k, complex).reshape(-1) for k in koseler]
    assert len(K) >= 3, "sefer en az üç köşe ister (hadd-i evsat lâzım)"
    K = [_bir(k) for k in K]
    _sec = usul_sec(K)
    usul = str(_sec["usul"])
    gaye = _gaye(float(omega))
    _SAYAC["sefer"] += 1.0
    _SAYAC[gaye] += 1.0
    _USUL_SAYAC[usul] = _USUL_SAYAC.get(usul, 0) + 1

    netice, orta = DEVRELER[usul](K, givens)
    netice = np.asarray(netice, complex).reshape(-1)
    orta = np.asarray(orta, complex).reshape(-1)

    ic = complex(np.vdot(orta, netice))
    temiz = netice - ic * _bir(orta)
    artik = float(abs(ic))
    _SAYAC["artık"] += artik
    if artik < 0.5:
        _SAYAC["uncompute"] += 1.0
    sifir = np.zeros_like(temiz)
    sifir[0] = 1.0
    _tasfiye = float(swap_testi(
        orta, temiz)["örtüşme"]) if float(np.linalg.norm(temiz)) > 0 else 1.0
    _SAYAC["tasfiye"] = _SAYAC.get("tasfiye", 0.0) + _tasfiye

    nrm = float(np.linalg.norm(temiz))
    if nrm <= 1e-300:
        return {"usul": usul, "gaye": gaye, "artık": artik,
                "tasfiye": _tasfiye, "seçim": _sec,
                "lan_k": False, "kazanç": 0.0, "netice": None}
    temiz = temiz / nrm

    M = _bir(np.asarray(mudrike, complex).reshape(-1))
    once = float(abs(complex(np.vdot(M, K[0]))))
    sonra = float(abs(complex(np.vdot(M, temiz))))
    kazanc = sonra - once
    tasindi = bool(kazanc > float(a.lan_esigi))
    if tasindi:
        _SAYAC["lan_k"] += 1.0
    return {"usul": usul, "gaye": gaye, "artık": artik,
            "tasfiye": _tasfiye, "seçim": _sec,
            "lan_k": tasindi, "kazanç": float(kazanc), "netice": temiz}


def usul_kos(haller: Sequence[np.ndarray],
             cevrim_indisleri: Sequence[Sequence[int]],
             omegalar: Sequence[float],
             ayar: Optional[UsulAyari] = None) -> Dict[str, Any]:
    a = ayar or UsulAyari()
    gedikler = gedik_bul(omegalar, a)
    if not gedikler:
        return {"sefer": 0, "gedik": 0, "kapanan": 0,
                "kazanç": 0.0, "borç": 0.0, "netice": []}
    H = np.stack([np.asarray(h, complex).reshape(-1) for h in haller])
    mudrike = H.sum(axis=0)
    toplam = 0.0
    acilan = 0
    kapanan = 0
    neticeler: List[Tuple[int, np.ndarray]] = []
    for c in gedikler:
        idx = [int(i) for i in cevrim_indisleri[c]]
        r = sefer([haller[i] for i in idx], float(omegalar[c]), mudrike, a)
        toplam += float(r["kazanç"])
        acilan += 1
        if r["lan_k"] and r["netice"] is not None:
            kapanan += 1
            neticeler.append((idx[0], np.asarray(r["netice"], complex)))
    borc = (float(len(gedikler) - kapanan) / float(len(gedikler))
            if gedikler else 0.0)
    return {"sefer": acilan, "gedik": len(gedikler), "kapanan": kapanan,
            "kazanç": float(toplam), "borç": float(borc),
            "netice": neticeler}


def usul_beyani() -> Dict[str, Any]:
    y = max(1.0, _SAYAC["yoklama"])
    s = max(1.0, _SAYAC["sefer"])
    return {"yoklama": int(_SAYAC["yoklama"]),
            "sefer": int(_SAYAC["sefer"]),
            "sefer_nispeti": float(_SAYAC["sefer"] / y),
            "istihrac": int(_SAYAC["istihrac"]),
            "cerh": int(_SAYAC["cerh"]),
            "tahkik": int(_SAYAC["tahkik"]),
            "uncompute": int(_SAYAC["uncompute"]),
            "lan_k": int(_SAYAC["lan_k"]),
            "artık_dolanıklık": float(_SAYAC["artık"] / s),
            "hadd_tasfiyesi": float(_SAYAC.get("tasfiye", 0.0) / s),
            "devre": len(DEVRELER),
            "ayrı_koşan_usul": len(_USUL_SAYAC),
            "usul": dict(_USUL_SAYAC)}


def usul_sifirla() -> None:
    for k in _SAYAC:
        _SAYAC[k] = 0.0
    _USUL_SAYAC.clear()
