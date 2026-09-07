from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["UsulAyari", "USULLER", "gedik_bul", "sefer", "usul_kos",
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
    "tahkik": 0.0, "uncompute": 0.0, "lan_k": 0.0, "artık": 0.0}
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
    karanlik = np.nonzero(om < float(a.had))[0]
    sira = karanlik[np.argsort(om[karanlik])]
    return [int(i) for i in sira[:max(0, int(a.sefer))]]


def _usul_sec(omega: float, kose: int) -> str:
    if omega < -0.75:
        return "Baroco"
    if kose > 3:
        return "Sorites"
    if omega < -0.25:
        return "Celarent"
    if omega < 0.0:
        return "AksiMüstevî"
    return "Barbara"


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
    a = ayar or UsulAyari()
    K = [np.asarray(k, complex).reshape(-1) for k in koseler]
    assert len(K) >= 3, "sefer en az üç köşe ister (hadd-i evsat lâzım)"
    K = [k / max(float(np.linalg.norm(k)), 1e-300) for k in K]
    usul = _usul_sec(float(omega), len(K))
    gaye = _gaye(float(omega))
    _SAYAC["sefer"] += 1.0
    _SAYAC[gaye] += 1.0
    _USUL_SAYAC[usul] = _USUL_SAYAC.get(usul, 0) + 1

    a0, b0, c0 = K[0], K[1], K[-1]
    U_f = givens(a0, b0)
    U_g = givens(b0, c0)
    netice = U_g @ (U_f @ a0)

    ic = complex(np.vdot(b0, netice))
    temiz = netice - ic * b0
    artik = float(abs(ic))
    _SAYAC["artık"] += artik
    if artik < 0.5:
        _SAYAC["uncompute"] += 1.0

    nrm = float(np.linalg.norm(temiz))
    if nrm <= 1e-300:
        return {"usul": usul, "gaye": gaye, "artık": artik,
                "lan_k": False, "kazanç": 0.0, "netice": None}
    temiz = temiz / nrm

    M = np.asarray(mudrike, complex).reshape(-1)
    M = M / max(float(np.linalg.norm(M)), 1e-300)
    once = float(abs(complex(np.vdot(M, a0))))
    sonra = float(abs(complex(np.vdot(M, temiz))))
    kazanc = sonra - once
    tasindi = bool(kazanc > float(a.lan_esigi))
    if tasindi:
        _SAYAC["lan_k"] += 1.0
    return {"usul": usul, "gaye": gaye, "artık": artik,
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
            "usul": dict(_USUL_SAYAC)}


def usul_sifirla() -> None:
    for k in _SAYAC:
        _SAYAC[k] = 0.0
    _USUL_SAYAC.clear()
