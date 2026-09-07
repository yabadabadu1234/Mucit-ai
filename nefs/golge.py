from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["GolgeAyari", "golge_al", "kestir", "rapor"]


@dataclass
class GolgeAyari:

    ornek: int = 128
    had: float = 0.05
    tohum: int = 0


def golge_al(psi, ayar: Optional[GolgeAyari] = None) -> Dict[str, Any]:
    a = ayar or GolgeAyari()
    K = max(1, int(a.ornek))
    r = np.random.default_rng(int(a.tohum))
    if hasattr(psi, "havuz") and hasattr(psi, "kok"):
        d = int(psi.boy)
        h = psi.havuz
        b = np.empty(K, np.int64)
        for k in range(K):
            adres, indis, sev = psi.kok, 0, psi.seviye
            while sev > 0:
                _sv, sol, sag, ls, lg = h.dugum[adres]
                w0 = abs(ls) ** 2 * float(np.real(h.ic(sol, sol, sev - 1)))
                w1 = abs(lg) ** 2 * float(np.real(h.ic(sag, sag, sev - 1)))
                t = w0 + w1
                git = 1 if (t <= 0.0 or r.random() * t >= w0) else 0
                indis = (indis << 1) | git
                adres = sag if git else sol
                sev -= 1
            b[k] = indis
        return {"b": b, "K": int(K), "d": d, "had": float(a.had),
                "olasılık": None, "graf": True}
    v = np.asarray(psi, complex).reshape(-1)
    d = int(v.size)
    assert d >= 2, "gölge için en az iki genlik lâzım"
    P = np.abs(v) ** 2
    top = float(P.sum())
    assert top > 0.0, "BOŞ durumdan gölge alınamaz"
    P = P / top
    b = r.choice(d, size=K, p=P)
    return {"b": b, "K": int(K), "d": d, "had": float(a.had),
            "olasılık": P, "graf": False}


def kestir(golge: Dict[str, Any], gozlenebilirler: Sequence[Tuple[int, int]],
           tahkik: bool = True) -> Dict[str, Any]:
    b = np.asarray(golge["b"], int)
    K = int(golge["K"])
    P = golge.get("olasılık")
    P = None if P is None else np.asarray(P, float)
    kestirim: List[float] = []
    tam: List[float] = []
    for (i, j) in gozlenebilirler:
        kestirim.append(float(np.count_nonzero((b >= i) & (b < j))) / K)
        if tahkik and P is not None:
            tam.append(float(P[int(i):int(j)].sum()))
    kes = np.asarray(kestirim, float)
    o: Dict[str, Any] = {"kestirim": kes, "gözlenebilir": len(kestirim),
                         "örnek": K}
    if tahkik and tam:
        t = np.asarray(tam, float)
        o["tam"] = t
        o["azamî_hata"] = float(np.max(np.abs(kes - t))) if t.size else 0.0
        o["hadde_sığdı"] = bool(o["azamî_hata"] <= float(golge["had"]))
    return o


def rapor(d: int = 4096, tohum: int = 0) -> str:
    import time
    r = np.random.default_rng(int(tohum))
    v = r.normal(size=d) + 1j * r.normal(size=d)
    v /= np.linalg.norm(v)
    M = 64
    kenar = np.linspace(0, d, M + 1).astype(int)
    goz = [(int(kenar[k]), int(kenar[k + 1])) for k in range(M)]

    s = ["=== KLASİK GÖLGELER -- O(log M) ölçüm ===", "",
         "  d = %d   M = %d gözlenebilir" % (d, M), ""]
    for K in (32, 128, 512, 2048):
        t0 = time.perf_counter()
        G = golge_al(v, GolgeAyari(ornek=K, tohum=tohum))
        o = kestir(G, goz, tahkik=True)
        sure = time.perf_counter() - t0
        s.append("  K=%-5d azamî hata %.4f   %.4f sn   hadde sığdı: %s"
                 % (K, o["azamî_hata"], sure, o["hadde_sığdı"]))
    t0 = time.perf_counter()
    P = np.abs(v) ** 2
    for _ in range(10):
        _ = [float(P[i:j].sum()) for (i, j) in goz]
    tam_sure = (time.perf_counter() - t0) / 10
    t0 = time.perf_counter()
    for _ in range(10):
        G = golge_al(v, GolgeAyari(ornek=128, tohum=tohum))
        _ = kestir(G, goz, tahkik=False)
    golge_sure = (time.perf_counter() - t0) / 10
    s += ["",
          "  tam ölçüm  : %.5f sn  (%d aralık, durum M kere dolaşılır)"
          % (tam_sure, M),
          "  gölge (K=128): %.5f sn  → %.2f×"
          % (golge_sure, tam_sure / max(golge_sure, 1e-12)),
          "",
          "  Hata O(1/√K)dir ve İDDİA EDİLMİYOR, ölçülüyor: her",
          "  kestirim tam değerle karşılaştırılıp farkı dönüyor."]
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
