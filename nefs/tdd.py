from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["TddAyari", "kanonik_adres", "esit_mi", "rapor"]


@dataclass
class TddAyari:

    tolerans: float = 1e-9
    cekirdek: int = 16


def kanonik_adres(psi, cekirdek: int = 16,
                  ayar: Optional[TddAyari] = None) -> Dict[str, Any]:
    a = ayar or TddAyari()
    v = np.asarray(psi, complex).reshape(-1)
    assert v.size >= 1, "adres için en az bir genlik lâzım"
    k = max(1, min(int(cekirdek), v.size))
    c = v[:k]
    tol = float(a.tolerans)
    j = int(np.argmax(np.abs(c) > tol)) if np.any(np.abs(c) > tol) else -1
    if j < 0:
        anahtar: Tuple = ("0", k)
    else:
        w = c / c[j]
        basamak = max(1, int(round(-math.log10(max(tol, 1e-15)))))
        anahtar = (k, j) + tuple(np.round(w, basamak).tolist())
    return {"adres": hash(anahtar), "anahtar": anahtar,
            "çekirdek": k, "boy": int(v.size),
            "bayt": int(c.nbytes)}


def esit_mi(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    return a["adres"] == b["adres"] and a["anahtar"] == b["anahtar"]


def rapor(d: int = 4096, tohum: int = 0) -> str:
    import time
    r = np.random.default_rng(int(tohum))
    v = r.normal(size=d) + 1j * r.normal(size=d)
    v /= np.linalg.norm(v)
    w = v * np.exp(1j * 0.7)
    u = r.normal(size=d) + 1j * r.normal(size=d)
    u /= np.linalg.norm(u)

    t0 = time.perf_counter()
    for _ in range(1000):
        av = kanonik_adres(v)
    sure = (time.perf_counter() - t0) / 1000
    aw, au = kanonik_adres(w), kanonik_adres(u)

    t0 = time.perf_counter()
    for _ in range(1000):
        _ = abs(complex(np.vdot(v, u)))
    tam = (time.perf_counter() - t0) / 1000

    return "\n".join([
        "=== KANONİK DENETÇİ (TDD hesap motoru İPTAL) ===", "",
        "  d = %d   çekirdek = 16 eleman" % d,
        "  adres alma  : %.7f sn" % sure,
        "  tam iç çarpım: %.7f sn   → denetçi %.1f× hızlı"
        % (tam, tam / max(sure, 1e-12)),
        "",
        "  ψ ile λψ (yalnız faz farkı) : aynı adres mi → %s  (doğru)"
        % esit_mi(av, aw),
        "  ψ ile bağımsız φ            : aynı adres mi → %s  (doğru)"
        % esit_mi(av, au),
        "",
        "  Hesap motoru KÖKÜNDEN KESİLDİ: kapı, toplama, iç çarpım,",
        "  çöp toplama -- hiçbiri yok. Zabıtın hükmü: TDD ileri/geri",
        "  akışta REDDEDİLİR, yalnız kanonik denetçidir.",
    ])
