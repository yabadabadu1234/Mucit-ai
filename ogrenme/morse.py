from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

__all__ = ["euler_karakteristigi", "morse_indisleri",
           "morse_euler_denklik_tahkiki", "tahkik_cetveli"]


def euler_karakteristigi(g: np.ndarray) -> int:
    g = np.atleast_2d(np.asarray(g, int))
    H, W = g.shape
    toplam = 0
    for renk in np.unique(g):
        M = (g == renk)
        V = int(M.sum())
        E = int((M[:, :-1] & M[:, 1:]).sum()) + int((M[:-1] & M[1:]).sum())
        F = int((M[:-1, :-1] & M[:-1, 1:] & M[1:, :-1] & M[1:, 1:]).sum())
        toplam += V - E + F
    return int(toplam)


_HALKA: Tuple[Tuple[int, int], ...] = (
    (-1, 0), (-1, 1), (0, 1), (1, 1),
    (1, 0), (1, -1), (0, -1), (-1, -1),
)


def _alt_bag_chi(ped: np.ndarray, i: int, j: int,
                 f: Dict[Tuple[int, int], float]) -> Tuple[int, int]:
    fv = f[(i, j)]
    var = []
    for t, (dy, dx) in enumerate(_HALKA):
        y, x = i + dy, j + dx
        if not ped[y, x]:
            var.append(False)
            continue
        if dy and dx:
            tam = (ped[i, x] and ped[y, j] and ped[y, x])
            var.append(bool(tam) and f[(y, x)] < fv)
        else:
            var.append(f[(y, x)] < fv)
    kose = sum(1 for v in var if v)
    kenar = 0
    for t in range(8):
        u = (t + 1) % 8
        if not (var[t] and var[u]):
            continue
        dy1, dx1 = _HALKA[t]
        dy2, dx2 = _HALKA[u]
        cy, cx = (dy1 or dy2), (dx1 or dx2)
        if ped[i + cy, j + cx] and ped[i + cy, j] and ped[i, j + cx]:
            kenar += 1
    return int(kose - kenar), int(kose)


def morse_indisleri(g: np.ndarray) -> Dict[int, int]:
    g = np.atleast_2d(np.asarray(g, int))
    M = {0: 0, 1: 0, 2: 0}
    for renk in np.unique(g):
        A = (g == renk)
        H, W = A.shape
        ped = np.zeros((H + 2, W + 2), bool)
        ped[1:-1, 1:-1] = A
        eps = 1.0 / (W + 2.0)
        f = {(y, x): y + eps * x
             for y in range(H + 2) for x in range(W + 2)}
        for y in range(1, H + 1):
            for x in range(1, W + 1):
                if not ped[y, x]:
                    continue
                chi_l, kose = _alt_bag_chi(ped, y, x, f)
                i_v = 1 - chi_l
                if kose == 0:
                    M[0] += 1
                elif i_v == 1:
                    M[2] += 1
                elif i_v < 0:
                    M[1] += (-i_v)
    return M


def morse_euler_denklik_tahkiki(g: np.ndarray, bozarak: int = 0
                                ) -> Tuple[bool, Dict[str, int]]:
    g = np.atleast_2d(np.asarray(g, int))
    M = morse_indisleri(g)
    M[1] += int(bozarak)
    morse = M[0] - M[1] + M[2]
    chi = euler_karakteristigi(g)
    return bool(morse == chi), {"M0": M[0], "M1": M[1], "M2": M[2],
                                "morse_toplam": int(morse), "chi": int(chi)}


def tahkik_cetveli() -> Dict[str, object]:
    dolu = np.ones((5, 6), int)
    delikli = np.ones((5, 6), int)
    delikli[2, 2] = 2
    satir = []
    for ad, g, bozuk in (("dolu dikdörtgen", dolu, 0),
                         ("delikli", delikli, 0),
                         ("dolu (KASTEN BOZUK)", dolu, 3)):
        ok, r = morse_euler_denklik_tahkiki(g, bozarak=bozuk)
        satir.append({"ad": ad, "tahkik": ok, **r})
    return {"satır": satir}


def rapor() -> str:
    c = tahkik_cetveli()
    s = ["MORSE-EULER TOPOLOJİK MUHASEBE   Σ(−1)^k M_k == χ", "",
         "  %-22s %6s %6s %6s %8s %6s %8s"
         % ("hâl", "M0", "M1", "M2", "Σ(−1)^k", "χ", "tahkik")]
    for r in c["satır"]:
        s.append("  %-22s %6d %6d %6d %8d %6d %8s"
                 % (r["ad"], r["M0"], r["M1"], r["M2"],
                    r["morse_toplam"], r["chi"], r["tahkik"]))
    s.append("")
    s.append("  Son satır KASTEN bozuktur ve False çıkmalıdır;")
    s.append("  çıkmazsa ölçü kırmızı yanamıyor demektir (H90).")
    return "\n".join(s)
