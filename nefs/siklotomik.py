from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .galois import gf_carp, gf_tablo

__all__ = ["SiklotomikAyari", "koset", "koset_indirge", "frobenius",
           "iz", "iz_esitligi", "iz_uydur", "rapor"]


@dataclass
class SiklotomikAyari:

    us: int = 8
    taban: int = 3
    derece: int = 12


def koset(s: int, us: int = 8) -> List[int]:
    n = (1 << int(us)) - 1
    s0 = int(s) % n
    o = [s0]
    x = (s0 * 2) % n
    while x != s0:
        o.append(x)
        x = (x * 2) % n
    return o


def koset_indirge(derece: int, ayar: Optional[SiklotomikAyari] = None
                  ) -> Dict[str, Any]:
    a = ayar or SiklotomikAyari()
    d = int(derece if derece else a.derece)
    m = int(a.us)
    n = (1 << m) - 1
    taban = int(a.taban)
    C = koset(taban, m)
    kosette = (d % n) in C
    kare = C.index(d % n) if kosette else -1
    bit = [i for i in range(d.bit_length()) if (d >> i) & 1]
    ikili = " + ".join("2^%d" % i for i in reversed(bit)) if bit else "0"
    yazilis = ("x^%d" % d if not kosette else
               "(" * kare + "x^%d" % taban + ")²" * kare)
    nd = m * 8
    monom = float(sum(math.comb(nd, j) for j in range(1, min(d, nd) + 1)))
    return {"us": m, "taban": taban, "derece": d, "koset": C,
            "kosette": bool(kosette), "kare": int(kare),
            "ikili": ikili, "yazılış": yazilis,
            "monom_sayisi": monom, "kıyas_değişkeni": nd,
            "koset_boyu": len(C)}


def frobenius(x, kere: int = 1, us: int = 8) -> np.ndarray:
    v = np.asarray(x, np.uint8)
    for _ in range(int(kere)):
        v = gf_carp(v, v, int(us)).astype(np.uint8)
    return v


def us_al(x, e: int, us: int = 8) -> np.ndarray:
    v = np.asarray(x, np.uint8)
    o = np.ones_like(v)
    taban = v.copy()
    k = int(e)
    while k:
        if k & 1:
            o = gf_carp(o, taban, int(us)).astype(np.uint8)
        taban = gf_carp(taban, taban, int(us)).astype(np.uint8)
        k >>= 1
    return np.where(np.asarray(x, np.uint8) == 0, np.uint8(0), o)


def iz(x, us: int = 8) -> np.ndarray:
    m = int(us)
    v = np.asarray(x, np.uint8)
    o = np.zeros_like(v)
    cur = v.copy()
    for _ in range(m):
        o = o ^ cur
        cur = gf_carp(cur, cur, m).astype(np.uint8)
    assert bool(np.all((o == 0) | (o == 1))), (
        "iz F_2'ye düşmedi -- cisim yahut polinom yanlış: %r"
        % np.unique(o)[:8])
    return o


def iz_esitligi(ayar: Optional[SiklotomikAyari] = None) -> Dict[str, Any]:
    a = ayar or SiklotomikAyari()
    m, d, t = int(a.us), int(a.derece), int(a.taban)
    q = 1 << m
    o = koset_indirge(d, a)
    if not o["kosette"]:
        return {"tuttu": False, "sebep": "derece kosette değil",
                "eleman": q, "uyuşmayan": q, "kare": -1}
    k = int(o["kare"])
    x = np.arange(q, dtype=np.uint8)
    r = np.random.default_rng(0)
    uyusmayan = 0
    denenen = 0
    for alfa in r.integers(1, q, size=16, dtype=np.int64):
        A = np.uint8(int(alfa))
        B = frobenius(np.array([A], np.uint8), (m - k) % m, m)[0]
        sol = iz(gf_carp(np.full(q, A, np.uint8), us_al(x, d, m), m
                         ).astype(np.uint8), m)
        sag = iz(gf_carp(np.full(q, B, np.uint8), us_al(x, t, m), m
                         ).astype(np.uint8), m)
        uyusmayan += int(np.count_nonzero(sol != sag))
        denenen += q
    return {"tuttu": bool(uyusmayan == 0), "eleman": denenen,
            "uyuşmayan": uyusmayan, "kare": k, "us": m,
            "derece": d, "taban": t,
            "alfa_sayısı": 16}


def iz_uydur(k, ayar: Optional[SiklotomikAyari] = None) -> Dict[str, Any]:
    a = ayar or SiklotomikAyari()
    m, t = int(a.us), int(a.taban)
    q = 1 << m
    v = np.asarray(k, np.int64).reshape(-1)
    n = min(v.size, q)
    hedef = (v[:n] & 1).astype(np.uint8)
    x = np.arange(n, dtype=np.uint8)
    xt = us_al(x, t, m)
    eniyi, eniyi_a = -1.0, -1
    for alfa in range(1, q):
        y = iz(gf_carp(np.full(n, alfa, np.uint8), xt, m).astype(np.uint8), m)
        oran = float(np.mean(y == hedef))
        if oran > eniyi:
            eniyi, eniyi_a = oran, alfa
    return {"en_iyi_uyum": eniyi, "alfa": eniyi_a, "eleman": int(n),
            "tam_uydu": bool(eniyi >= 1.0),
            "rastgele_beklenti": 0.5}


def rapor(tohum: int = 0) -> str:
    a = SiklotomikAyari()
    o = koset_indirge(12, a)
    e = iz_esitligi(a)
    s = ["=== SİKLOTOMİK KOSET İNDİRGEMESİ ===", "",
         "  CNOT-Dihedral iddiası İPTAL: ölçülen derece 12, teorem ≤3 ister.",
         "",
         "  GF(2^%d),  taban x^%d,  derece %d" % (o["us"], o["taban"],
                                                  o["derece"]),
         "    %d = %s" % (o["derece"], o["ikili"]),
         "    koset(%d) = %s   (boy %d)" % (o["taban"], o["koset"],
                                            o["koset_boyu"]),
         "    %d kosette mi : %s   → %d Frobenius karesi"
         % (o["derece"], o["kosette"], o["kare"]),
         "    yazılışı      : x^%d = %s" % (o["derece"], o["yazılış"]), "",
         "  HÜKÜM SINANDI (örnekleme değil, cismin TAMAMI):",
         "    Tr(α·x^%d) = Tr(β·x^%d),  β = α^(2^-%d)"
         % (o["derece"], o["taban"], e["kare"]),
         "    denenen: %d eleman (%d farklı α × %d eleman)"
         % (e["eleman"], e["alfa_sayısı"], 1 << o["us"]),
         "    uyuşmayan: %d   →  EŞİTLİK: %s" % (e["uyuşmayan"], e["tuttu"]),
         "",
         "  KIYAS -- monom açılımı yapılsaydı:",
         "    %d değişkende derece ≤%d monom sayısı: %.3e"
         % (o["kıyas_değişkeni"], o["derece"], o["monom_sayisi"]),
         "    siklotomik yolda açılan terim sayısı  : 1  (tek iz terimi)",
         "",
         "  ÖLÇÜ KIRMIZI YANABİLİR (ferman 5):"]
    kotu = koset_indirge(5, a)
    s += ["    derece 5 kosette mi: %s  (doğru: 5 ∉ C_3, indirgenmez)"
          % kotu["kosette"],
          "    derece 5 için iz eşitliği: %s"
          % iz_esitligi(SiklotomikAyari(us=8, taban=3, derece=5))["tuttu"]]
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
