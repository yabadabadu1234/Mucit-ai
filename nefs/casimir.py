from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["CasimirAyari", "casimir_yukleri", "dhr_ayrismasi",
           "gelfand_tsetlin_araya_girme", "kartan_fazi",
           "casimir_beyani", "casimir_sifirla"]


_CASIMIR: Dict[str, float] = {}


def casimir_sifirla() -> None:
    _CASIMIR.clear()
    _CASIMIR.update({"çağrı": 0.0, "sektör": 0.0, "azamî_sektör_payı": 0.0,
                     "sızıntı": 0.0, "araya_girme_ihlâli": 0.0,
                     "blok_köşegen_artığı": 0.0, "kartan_çağrısı": 0.0})


casimir_sifirla()


@dataclass
class CasimirAyari:
    acik: int = 1
    esik_payi: float = 0.0


def casimir_yukleri(lif: Sequence[int]) -> np.ndarray:
    lif = tuple(int(x) for x in lif)
    d = int(np.prod(lif))
    yuk = np.zeros(d, np.int64)
    ard = d
    for n in lif:
        ard //= int(n)
        eksen = (np.arange(d) // ard) % int(n)
        yuk += np.array([bin(int(v)).count("1") for v in range(int(n))],
                        np.int64)[eksen]
    return yuk


def dhr_ayrismasi(psi: np.ndarray, lif: Sequence[int],
                  ayar: Optional[CasimirAyari] = None) -> Dict[str, Any]:
    a = ayar or CasimirAyari()
    yuk = casimir_yukleri(lif)
    P = np.abs(np.asarray(psi, complex)) ** 2
    P = P / np.maximum(P.sum(axis=1, keepdims=True), 1e-300)
    q = np.unique(yuk)
    pay = np.stack([P[:, yuk == int(v)].sum(axis=1) for v in q], axis=1)
    ort = pay.mean(axis=0)
    _CASIMIR["çağrı"] += 1.0
    _CASIMIR["sektör"] = float(q.size)
    _CASIMIR["azamî_sektör_payı"] = float(ort.max()) if ort.size else 0.0
    sizinti = float(1.0 - ort.sum())
    _CASIMIR["sızıntı"] = abs(sizinti)
    return {"yük": q, "pay": pay, "ortalama_pay": ort,
            "sektör": int(q.size), "sızıntı": float(abs(sizinti)),
            "açık": bool(int(a.acik))}


def gelfand_tsetlin_araya_girme(pay: np.ndarray) -> Dict[str, Any]:
    m = np.asarray(pay, float)
    if m.ndim == 1:
        m = m[None, :]
    if m.shape[1] < 2:
        return {"ihlâl": 0, "denenen": 0, "nispet": 0.0}
    sirali = -np.sort(-m, axis=1)
    ihlal = 0
    denenen = 0
    for b in range(sirali.shape[0]):
        s = sirali[b]
        for i in range(s.size - 1):
            denenen += 1
            if s[i] + 1e-15 < s[i + 1]:
                ihlal += 1
    n = float(max(1, denenen))
    _CASIMIR["araya_girme_ihlâli"] = float(ihlal) / n
    return {"ihlâl": int(ihlal), "denenen": int(denenen),
            "nispet": float(ihlal) / n}


def kartan_fazi(lif: Sequence[int], acilar: Sequence[float]) -> np.ndarray:
    yuk = casimir_yukleri(lif)
    a = np.asarray(list(acilar), float).reshape(-1)
    if a.size == 0:
        return np.zeros(yuk.size, float)
    q = np.unique(yuk)
    tablo = np.zeros(int(q.max()) + 1, float)
    for i, v in enumerate(q):
        tablo[int(v)] = float(a[i % a.size])
    _CASIMIR["kartan_çağrısı"] += 1.0
    return -tablo[yuk]


def blok_kosegen_artigi(psi: np.ndarray, lif: Sequence[int]) -> float:
    yuk = casimir_yukleri(lif)
    v = np.asarray(psi, complex)
    q = np.unique(yuk)
    rho_ic = 0.0
    for s in q:
        m = yuk == int(s)
        rho_ic += float(np.sum(np.abs(v[:, m]) ** 2) ** 2)
    top = float(np.sum(np.abs(v) ** 2) ** 2)
    art = float(max(0.0, 1.0 - rho_ic / max(top, 1e-300)))
    _CASIMIR["blok_köşegen_artığı"] = art
    return art


def casimir_beyani() -> Dict[str, float]:
    return dict(_CASIMIR)
