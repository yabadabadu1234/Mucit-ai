from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

__all__ = ["FazAyari", "mobius", "zeta", "faz_oturt", "faz_uygula", "rapor"]

BRAVYI_GOSSET_ALFA = 0.468


@dataclass
class FazAyari:

    mertebe: int = 8
    derece: int = 3


def mobius(k: np.ndarray, m: int) -> np.ndarray:
    c = np.asarray(k, np.int64).copy() % int(m)
    d = c.size
    n = int(round(math.log2(d)))
    assert 1 << n == d, "boy ikinin kuvveti olmalı: %d" % d
    idx = np.arange(d)
    for i in range(n):
        bit = 1 << i
        ust = idx[(idx & bit) != 0]
        c[ust] = (c[ust] - c[ust ^ bit]) % int(m)
    return c


def zeta(c: np.ndarray, m: int) -> np.ndarray:
    k = np.asarray(c, np.int64).copy() % int(m)
    d = k.size
    n = int(round(math.log2(d)))
    idx = np.arange(d)
    for i in range(n):
        bit = 1 << i
        ust = idx[(idx & bit) != 0]
        k[ust] = (k[ust] + k[ust ^ bit]) % int(m)
    return k


def faz_oturt(k, ayar: Optional[FazAyari] = None) -> Dict[str, Any]:
    a = ayar or FazAyari()
    m = max(4, int(a.mertebe))
    v = np.asarray(k, np.int64).reshape(-1) % m
    d = v.size
    assert d >= 2, "faz vektörü en az iki elemanlı olmalı"
    n = int(round(math.log2(d)))
    assert 1 << n == d, "faz vektörü boyu ikinin kuvveti olmalı: %d" % d

    c = mobius(v, m)
    geri = zeta(c, m)
    geri_hata = int(np.count_nonzero(geri != v))

    nz = np.nonzero(c)[0]
    if nz.size:
        agirlik = np.array([int(bin(int(i)).count("1")) for i in nz])
        derece = int(agirlik.max())
        artik = int(np.count_nonzero(agirlik > int(a.derece)))
    else:
        derece, artik = 0, 0

    ceyrek = max(1, m // 4)
    t_sayisi = int(np.count_nonzero(c[nz] % ceyrek)) if nz.size else 0
    return {
        "mertebe": m, "boy": int(d), "değişken": n,
        "derece": derece, "terim": int(nz.size),
        "azamî_derece": int(a.derece),
        "tam": bool(derece <= int(a.derece)),
        "artık": artik,
        "geri_hata": geri_hata,
        "katsayı_baytı": int(c.astype(np.int16).nbytes),
        "yoğun_baytı": int(d * 16),
        "dallanma": 1,
        "t_kapısı": t_sayisi,
        "dallanma_kubit": float(2.0 ** min(BRAVYI_GOSSET_ALFA * t_sayisi,
                                           1023.0)),
        "katsayı": c,
    }


def faz_uygula(psi, k, mertebe: int = 8) -> np.ndarray:
    from .galois import palmer_indir
    m = int(mertebe)
    e = np.asarray(k, np.int64).reshape(-1) % m
    return palmer_indir(psi, e, m)[0]


def rapor(n: int = 12, tohum: int = 0) -> str:
    m = 8
    d = 1 << n
    r = np.random.default_rng(int(tohum))
    x = np.arange(d)
    s = ["=== FAZ POLİNOMU -- AMY-MASLOV-MOSCA (2014) ===", "",
         "  Z_%d,  n = %d değişken,  d = %d taban durumu" % (m, n, d), "",
         "  hâl                         derece  terim   tam?   geri hata",
         "  " + "-" * 62]
    a = r.integers(0, m, size=n)
    dogrusal = np.zeros(d, np.int64)
    for i in range(n):
        dogrusal += a[i] * ((x >> i) & 1)
    o1 = faz_oturt(dogrusal % m, FazAyari(mertebe=m))
    s.append("  doğrusal (Σaᵢxᵢ)            %6d  %5d   %-5s  %d"
             % (o1["derece"], o1["terim"], o1["tam"], o1["geri_hata"]))
    ikinci = dogrusal.copy()
    for i in range(n):
        for j in range(i + 1, n):
            ikinci += int(r.integers(0, m)) * (((x >> i) & 1)
                                               * ((x >> j) & 1))
    o2 = faz_oturt(ikinci % m, FazAyari(mertebe=m))
    s.append("  ikinci derece (CZ)          %6d  %5d   %-5s  %d"
             % (o2["derece"], o2["terim"], o2["tam"], o2["geri_hata"]))
    ucuncu = ikinci.copy()
    for i in range(0, n - 2, 3):
        ucuncu += 1 * (((x >> i) & 1) * ((x >> (i + 1)) & 1)
                       * ((x >> (i + 2)) & 1))
    o3 = faz_oturt(ucuncu % m, FazAyari(mertebe=m))
    s.append("  üçüncü derece (CCZ)         %6d  %5d   %-5s  %d"
             % (o3["derece"], o3["terim"], o3["tam"], o3["geri_hata"]))
    keyfi = r.integers(0, m, size=d)
    o4 = faz_oturt(keyfi, FazAyari(mertebe=m))
    s.append("  keyfî (rastgele)            %6d  %5d   %-5s  %d"
             % (o4["derece"], o4["terim"], o4["tam"], o4["geri_hata"]))
    s += ["",
          "  ÖLÇÜ KIRMIZI YANABİLİYOR: keyfî faz derece %d verdi ve"
          % o4["derece"],
          "  CNOT-Dihedral sınıfına GİRMEDİ (tam: %s). Yanamayan bir"
          % o4["tam"],
          "  ölçü hiçbir şey ölçmüyor demektir.", "",
          "  DALLANMA:",
          "    faz polinomu yolunda        : %d tablo" % o3["dallanma"],
          "    kübit tabanında (t=%d)      : %.3e stabilizer"
          % (o3["t_kapısı"], o3["dallanma_kubit"]),
          "",
          "  BELLEK (üçüncü derece hâli):",
          "    katsayı dizisi : %d bayt" % o3["katsayı_baytı"],
          "    yoğun faz      : %d bayt" % o3["yoğun_baytı"],
          "",
          "  GERİ DÖNÜŞ HATASI DÖRT HÂLDE DE SIFIR: oturtma bir",
          "  uydurma değil, tam Möbius açılımıdır."]
    return "\n".join(s)
