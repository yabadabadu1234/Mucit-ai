from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["RustAyari", "gf2_rank", "sinir_operatorleri",
           "topolojik_yirtik", "rust_kilidi"]


@dataclass
class RustAyari:

    t0: float = 0.5
    tau: float = 0.15
    kapanis: float = 0.5
    muayene: int = 1
    toplam_adim: int = 200

    def __post_init__(self) -> None:
        assert float(self.tau) > 0.0, "takvim genişliği sıfır olamaz"
        assert float(self.kapanis) > 0.0, (
            "σ_kapanış sıfır olamaz: sıfıra bölme. Muayeneyi kapatmak "
            "için ``muayene=0`` denir")


def gf2_rank(M: np.ndarray) -> int:
    A = (np.asarray(M) & 1).astype(np.uint8).copy()
    if A.size == 0:
        return 0
    satir, sutun = A.shape
    r = 0
    for c in range(sutun):
        pivot = -1
        for i in range(r, satir):
            if A[i, c]:
                pivot = i
                break
        if pivot < 0:
            continue
        if pivot != r:
            A[[r, pivot]] = A[[pivot, r]]
        vur = A[:, c].astype(bool).copy()
        vur[r] = False
        A[vur] ^= A[r]
        r += 1
        if r == satir:
            break
    return int(r)


def sinir_operatorleri(baglamlar: Sequence[Sequence[int]], n: int
                       ) -> Tuple[np.ndarray, np.ndarray,
                                  List[Tuple[int, int]],
                                  List[Tuple[int, int, int]]]:
    n = int(n)
    kenar_no: Dict[Tuple[int, int], int] = {}
    ucgen: List[Tuple[int, int, int]] = []
    gorulen = set()
    kumeler = {tuple(sorted(set(int(x) % n for x in bag)))
               for bag in baglamlar}
    for t in kumeler:
        for i in range(len(t)):
            for j in range(i + 1, len(t)):
                kenar_no.setdefault((t[i], t[j]), len(kenar_no))
        for i in range(len(t)):
            for j in range(i + 1, len(t)):
                for k in range(j + 1, len(t)):
                    u = (t[i], t[j], t[k])
                    if u not in gorulen:
                        gorulen.add(u)
                        ucgen.append(u)
    kenarlar = [k for k, _ in sorted(kenar_no.items(), key=lambda x: x[1])]
    d1 = np.zeros((len(kenarlar), n), np.uint8)
    for e, (a, b) in enumerate(kenarlar):
        d1[e, a] = 1
        d1[e, b] = 1
    d2 = np.zeros((len(ucgen), len(kenarlar)), np.uint8)
    for f, (a, b, c) in enumerate(ucgen):
        for kenar in ((a, b), (b, c), (a, c)):
            d2[f, kenar_no[kenar]] = 1
    return d1, d2, kenarlar, ucgen


def topolojik_yirtik(baglamlar: Sequence[Sequence[int]], n: int,
                     morfizm: Optional[np.ndarray] = None
                     ) -> Dict[str, Any]:
    n = int(n)
    d1, d2, kenarlar, ucgen = sinir_operatorleri(baglamlar, n)
    n_kenar = len(kenarlar)
    if n_kenar == 0:
        return {"h1": 0, "dF_dec": 0.0, "kenar": 0, "üçgen": 0,
                "rank_d1": 0, "rank_d2": 0, "kopuk": 0}
    r1 = gf2_rank(d1)
    r2 = gf2_rank(d2) if len(ucgen) else 0
    h1 = max(0, (n_kenar - r1) - r2)

    if morfizm is None:
        onde = np.zeros((n, n), np.int64)
        for bag in baglamlar:
            t = np.asarray(list(bag), np.int64) % n
            if t.size < 2:
                continue
            M = np.zeros((t.size, n), np.int64)
            M[np.arange(t.size), t] = 1
            onceki = np.cumsum(M, axis=0) - M
            onde += onceki.T @ M
        np.fill_diagonal(onde, 0)
        F = (onde > onde.T).astype(np.uint8)
    else:
        F = (np.asarray(morfizm) & 1).astype(np.uint8)
        assert F.shape == (n, n), "morfizm alanı (n, n) olmalı"

    acik = 0
    for (a, b, c) in ucgen:
        if (int(F[a, b]) ^ int(F[b, c]) ^ int(F[c, a])) & 1:
            acik += 1
    dF = float(acik) / float(max(1, len(ucgen)))
    return {"h1": int(h1), "dF_dec": float(dF * dF), "kenar": n_kenar,
            "üçgen": len(ucgen), "rank_d1": r1, "rank_d2": r2,
            "kopuk": int(n - r1)}


def rust_kilidi(adim: int, dF_dec: float, h1: int,
                ayar: Optional[RustAyari] = None) -> Dict[str, float]:
    a = ayar or RustAyari()
    T = max(1, int(a.toplam_adim))
    u = (float(adim) / T - float(a.t0)) / float(a.tau)
    u = float(np.clip(u, -60.0, 60.0))
    takvim = float(1.0 / (1.0 + math.exp(-u)))

    if not int(a.muayene):
        return {"takvim": takvim, "muayene": 1.0, "α": takvim,
                "dF_dec": float(dF_dec), "h1": float(int(h1))}

    yirtik = float(dF_dec) + float(int(h1)) ** 2
    us = -yirtik / (float(a.kapanis) ** 2)
    muayene = float(math.exp(max(us, -700.0)))
    return {"takvim": takvim, "muayene": muayene,
            "α": float(takvim * muayene),
            "dF_dec": float(dF_dec), "h1": float(int(h1))}
