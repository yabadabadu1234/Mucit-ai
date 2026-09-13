from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import numpy as np

__all__ = ["kararname", "rapor"]


def kararname(psi, mertebe: int = 8, esik: float = 1e-3,
              tohum: int = 0) -> Dict[str, Any]:
    v = np.asarray(psi, complex).reshape(-1)
    d = int(v.size)
    assert d >= 2, "karar verilecek durum en az iki genlikli olmalı"
    nrm = float(np.linalg.norm(v))
    assert nrm > 0.0, "BOŞ durum hakkında karar verilemez"
    v = v / nrm
    if int(mertebe) <= 0:
        return {"chi": 0, "örtüşme": 0.0, "üst_sınır": True,
                "clifforda_yakın": False, "kalıntı": 1.0,
                "aday": 0, "kapalı": True}

    kalinti = v.copy()
    secilen: List[int] = []
    kats: List[complex] = []
    jj = np.arange(d)
    for _ in range(int(mertebe)):
        iz = int(np.argmax(np.abs(kalinti)))
        c_z = complex(kalinti[iz])
        F = np.fft.fft(kalinti) / math.sqrt(d)
        ix = int(np.argmax(np.abs(F)))
        c_x = complex(np.conj(F[ix]))
        if abs(c_z) >= abs(c_x):
            if abs(c_z) < 1e-12:
                break
            taban = np.zeros(d, complex)
            taban[iz] = 1.0
            kat = c_z
        else:
            if abs(c_x) < 1e-12:
                break
            taban = np.exp(2j * math.pi * ix * jj / d) / math.sqrt(d)
            kat = complex(np.vdot(taban, kalinti))
        secilen.append(iz if abs(c_z) >= abs(c_x) else (d + ix))
        kats.append(kat)
        kalinti = kalinti - kat * taban
        if float(np.linalg.norm(kalinti)) < float(esik):
            break
    kal = float(np.linalg.norm(kalinti))
    ortusme = float(max(0.0, 1.0 - kal ** 2))
    return {"chi": len(secilen), "örtüşme": ortusme,
            "kalıntı": kal, "aday": 2 * d,
            "üst_sınır": True, "kapalı": False,
            "clifforda_yakın": bool(kal < float(esik)),
            "katsayı": np.asarray(kats, complex)}


def rapor(d: int = 256, tohum: int = 0) -> str:
    r = np.random.default_rng(int(tohum))
    j = np.arange(d)
    haller = {
        "taban |5⟩ (stabilizer)": np.eye(1, d, 5, dtype=complex).reshape(-1),
        "Fourier |+⟩ (stabilizer)": np.exp(2j * math.pi * 3 * j / d)
        / math.sqrt(d),
        "iki stabilizer toplamı": (np.eye(1, d, 5, dtype=complex).reshape(-1)
                                   + np.exp(2j * math.pi * 3 * j / d)
                                   / math.sqrt(d)),
        "gürültü (Haar)": r.normal(size=d) + 1j * r.normal(size=d),
    }
    s = ["=== KARARNAME -- stabilizer rank üst sınırı ===", "",
         "  d = %d   mertebe haddi = 8" % d, ""]
    for ad, v in haller.items():
        v = np.asarray(v, complex).reshape(-1)
        v = v / (np.linalg.norm(v) or 1.0)
        k = kararname(v, mertebe=8, tohum=tohum)
        s.append("  %-26s χ ≤ %2d   örtüşme %.6f   kalıntı %.2e   "
                 "Clifford'a yakın: %s"
                 % (ad, k["chi"], k["örtüşme"], k["kalıntı"],
                    k["clifforda_yakın"]))
    s += ["", "  Gürültüde χ küçük ÇIKMAZ ve bu gizlenmiyor: keyfî bir",
          "  durum Clifford çerçevesine oturmaz. χ bir vaat değil,",
          "  durumun yapısının neticesidir. Ayrıca dönen sayı χ'nin",
          "  kendisi değil ÜST SINIRIDIR (açgözlü seçim, sabit aile)."]
    return "\n".join(s)
