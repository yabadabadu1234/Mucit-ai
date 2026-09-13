from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["HendeseAyari", "gecis_dizeyi", "karsilikli_haber",
           "gromov_delta", "mertebe_sec", "dikey_asansor",
           "hendese_teshisi", "hendese_beyani", "hendese_yukle",
           "hendese_sifirla"]


_HENDESE: Dict[str, float] = {}


def hendese_sifirla() -> None:
    _HENDESE.clear()
    _HENDESE.update({"çağrı": 0.0, "mertebe": -1.0, "δ": 0.0,
                     "haber": 0.0, "sapma": 0.0, "nilpotent": -1.0,
                     "denklik": 0.0, "üçgen_ihlâli": 0.0,
                     "eğrilik": 0.0, "asansör_katı": 0.0})


hendese_sifirla()


@dataclass
class HendeseAyari:
    azami_alfabe: int = 256
    dortlu_ornek: int = 64
    tohum: int = 0


def gecis_dizeyi(w: Sequence[int], n: int) -> np.ndarray:
    y = np.asarray(list(w), np.int64).reshape(-1) % int(n)
    if y.size < 2:
        return np.zeros((int(n), int(n)), float)
    T = np.zeros((int(n), int(n)), float)
    np.add.at(T, (y[:-1], y[1:]), 1.0)
    sat = T.sum(axis=1, keepdims=True)
    return T / np.maximum(sat, 1.0)


def karsilikli_haber(w: Sequence[int], n: int) -> Dict[str, float]:
    y = np.asarray(list(w), np.int64).reshape(-1) % int(n)
    if y.size < 2:
        return {"haber": 0.0, "şart_sapması": 0.0}
    ortak = np.zeros((int(n), int(n)), float)
    np.add.at(ortak, (y[:-1], y[1:]), 1.0)
    top = max(float(ortak.sum()), 1.0)
    P = ortak / top
    Pi = P.sum(axis=1, keepdims=True)
    Pj = P.sum(axis=0, keepdims=True)
    payda = np.maximum(Pi * Pj, 1e-300)
    sec = P > 0.0
    haber = float(np.sum(P[sec] * np.log(P[sec] / payda[sec])))
    sart = P / np.maximum(Pi, 1e-300)
    dolu = np.asarray(Pi).reshape(-1) > 0.0
    sapma = (float(np.mean(np.var(sart[dolu], axis=1)))
             if bool(dolu.any()) else 0.0)
    return {"haber": haber, "şart_sapması": sapma}


def _mesafe(w: Sequence[int], n: int) -> np.ndarray:
    T = gecis_dizeyi(w, n)
    S = T + T.T
    ic = -np.log(np.maximum(S, 1e-12))
    np.fill_diagonal(ic, 0.0)
    m = int(n)
    D = ic.copy()
    for k in range(m):
        D = np.minimum(D, D[:, k:k + 1] + D[k:k + 1, :])
    return D


def gromov_delta(w: Sequence[int], ayar: Optional[HendeseAyari] = None
                 ) -> Dict[str, float]:
    a = ayar or HendeseAyari()
    y = np.asarray(list(w), np.int64).reshape(-1)
    n = int(min(int(a.azami_alfabe), max(2, int(y.max()) + 1)))
    D = _mesafe(y, n)
    r = np.random.default_rng(int(a.tohum))
    en_buyuk = 0.0
    ihlal = 0
    kac = int(a.dortlu_ornek)
    for _ in range(kac):
        i, j, k, l = (int(x) for x in r.choice(n, size=4, replace=False))
        s1 = D[i, j] + D[k, l]
        s2 = D[i, k] + D[j, l]
        s3 = D[i, l] + D[j, k]
        d = float(s1 - max(s2, s3))
        en_buyuk = max(en_buyuk, abs(d))
        if D[i, k] > D[i, j] + D[j, k] + 1e-9:
            ihlal += 1
    _HENDESE["δ"] = float(en_buyuk)
    _HENDESE["üçgen_ihlâli"] = float(ihlal) / max(1, kac)
    return {"δ": float(en_buyuk), "üçgen_ihlâli": float(ihlal) / max(1, kac),
            "dörtlü": kac, "alfabe": n}


def mertebe_sec(w: Sequence[int], ayar: Optional[HendeseAyari] = None
                ) -> Dict[str, Any]:
    a = ayar or HendeseAyari()
    y = np.asarray(list(w), np.int64).reshape(-1)
    n = int(min(int(a.azami_alfabe), max(2, int(y.max()) + 1)))
    hb = karsilikli_haber(y, n)
    T = gecis_dizeyi(y, n)
    sapma = float(np.linalg.norm(T - T.T))
    kuvvet = T.copy()
    nilpotent = -1
    for k in range(1, min(8, n) + 1):
        kuvvet = kuvvet @ T
        if float(np.max(np.abs(kuvvet))) < 1e-12:
            nilpotent = k
            break
    yari = max(1, y.size // 2)
    A = gecis_dizeyi(y[:yari], n)
    B = gecis_dizeyi(y[yari:], n)
    pay = float(np.linalg.norm(A) * np.linalg.norm(B))
    denklik = (float(np.sum(A * B) / pay) if pay > 1e-12 else 0.0)
    gr = gromov_delta(y, a)

    puan = np.zeros(4, float)
    puan[0] = 1.0 / (1.0 + hb["haber"] + hb["şart_sapması"])
    puan[1] = (1.0 - gr["üçgen_ihlâli"]) / (1.0 + sapma)
    puan[2] = sapma * (1.0 if nilpotent > 0 else 0.25)
    puan[3] = max(0.0, denklik) * (1.0 + hb["haber"])
    top = float(puan.sum())
    nispet = puan / max(top, 1e-300)
    l = int(np.argmax(nispet))
    egrilik = ("hiperbolik" if gr["δ"] > 1e-9 and gr["üçgen_ihlâli"] < 0.5
               else ("düz" if gr["δ"] <= 1e-9 else "pozitif"))
    _HENDESE["çağrı"] += 1.0
    _HENDESE["mertebe"] = float(l)
    _HENDESE["haber"] = float(hb["haber"])
    _HENDESE["sapma"] = sapma
    _HENDESE["nilpotent"] = float(nilpotent)
    _HENDESE["denklik"] = float(denklik)
    _HENDESE["eğrilik"] = float({"düz": 0, "hiperbolik": 1,
                                 "pozitif": 2}[egrilik])
    return {"ℓ*": l, "nispet": nispet, "haber": hb["haber"],
            "şart_sapması": hb["şart_sapması"], "sapma": sapma,
            "nilpotent": nilpotent, "denklik": denklik,
            "δ_Gromov": gr["δ"], "üçgen_ihlâli": gr["üçgen_ihlâli"],
            "eğrilik": egrilik, "alfabe": n}


def dikey_asansor(mertebe: int, lif: Sequence[int]) -> Dict[str, Any]:
    lif = tuple(int(x) for x in lif)
    kat = int(min(max(int(mertebe), 0), len(lif) - 1))
    _HENDESE["asansör_katı"] = float(kat)
    return {"kat": kat, "eksen": kat, "lif": lif,
            "taban_boyu": int(lif[kat]),
            "yukarı": tuple(lif[kat:]), "aşağı": tuple(lif[:kat + 1])}


def hendese_teshisi(baglamlar: Sequence[Sequence[int]], lif: Sequence[int],
                    ayar: Optional[HendeseAyari] = None) -> Dict[str, Any]:
    assert baglamlar, "hendese teşhisi için bağlam BOŞ olamaz"
    duz: List[int] = []
    for b in baglamlar:
        duz.extend(int(x) for x in np.asarray(list(b), np.int64).reshape(-1)
                   if int(x) >= 0)
    assert duz, "bağlamların hepsi boş -- teşhis edilecek dizi yok"
    m = mertebe_sec(duz, ayar)
    m["asansör"] = dikey_asansor(int(m["ℓ*"]), lif)
    m["basamak"] = len(duz)
    return m


def hendese_beyani() -> Dict[str, float]:
    return dict(_HENDESE)


def hendese_yukle(d: Dict[str, float]) -> None:
    _HENDESE.clear()
    _HENDESE.update({str(k): float(v) for k, v in dict(d).items()})
