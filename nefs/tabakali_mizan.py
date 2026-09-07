from __future__ import annotations

import math
from typing import Any, Dict, Optional, Sequence

import numpy as np

__all__ = ["kategori_kaybi", "nokta_kaybi"]


def kategori_kaybi(haller: Sequence[np.ndarray], azami: int = 32,
                   tohum: int = 0) -> Dict[str, Any]:
    from .kulli_mizan import givens
    m = len(haller)
    if m < 3:
        return {"kayıp": 0.0, "ihlâl": 0, "deneme": 0, "azamî": 0.0}
    H = np.stack([np.asarray(h, complex).reshape(-1) for h in haller])
    H = H / np.maximum(np.linalg.norm(H, axis=-1, keepdims=True), 1e-300)
    r = np.random.default_rng(int(tohum))
    k = int(min(int(azami), m))
    ucluler = np.stack([r.choice(m, size=3, replace=False)
                        for _ in range(k)])
    toplam = 0.0
    ihlal = 0
    azami_fark = 0.0
    for idx in ucluler:
        a, b, c = (H[int(idx[0])], H[int(idx[1])], H[int(idx[2])])
        M_f = givens(a, b)
        M_g = givens(b, c)
        M_gf = givens(a, c)
        fark = M_gf - (M_g @ M_f)
        d2 = float(np.sum(np.abs(fark) ** 2))
        toplam += d2
        azami_fark = max(azami_fark, d2)
        if d2 > 1e-9:
            ihlal += 1
    n = float(len(ucluler))
    kayip = toplam / n
    assert math.isfinite(kayip), "kategori kaybı sonlu değil"
    assert kayip >= 0.0, "Frobenius normunun karesi negatif çıkamaz"
    return {"kayıp": float(kayip), "ihlâl": int(ihlal),
            "deneme": int(len(ucluler)), "azamî": float(azami_fark)}


def nokta_kaybi(lifliler: Sequence[np.ndarray], hedefler: Sequence[int],
                n_v: int, eps: float = 1e-12,
                cinsler: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    assert len(lifliler) == len(hedefler), (
        "lifli sayısı %d, hedef sayısı %d -- örnek kayboldu"
        % (len(lifliler), len(hedefler)))
    if not lifliler:
        return {"kayıp": 0.0, "isabet": 0.0, "örnek": 0}
    M = np.stack([np.asarray(x, complex) for x in lifliler])
    guc = np.einsum('svh,svh->sv', M, M.conj()).real
    iz = np.maximum(guc.sum(axis=1), 1e-300)
    rho_kosegen = guc / iz[:, None]
    h = np.asarray(list(hedefler), np.int64) % int(n_v)
    p = rho_kosegen[np.arange(h.size), h]
    tekil = -np.log(np.maximum(p, float(eps)))
    tepe = np.argmax(rho_kosegen, axis=1) == h
    if cinsler is None:
        agirlik = np.ones(h.size, float)
        pay = {"arc": int(h.size), "sözlü": 0}
    else:
        c = np.asarray([str(x) for x in cinsler])
        arc = np.char.startswith(c, "arc")
        soz = ~arc
        nebze = float(tepe[soz].mean()) if bool(soz.any()) else 0.0
        agirlik = np.where(arc, 1.0, nebze)
        pay = {"arc": int(arc.sum()), "sözlü": int(soz.sum()),
               "sözlü_nebze": nebze,
               "arc_isabet": (float(tepe[arc].mean())
                              if bool(arc.any()) else 0.0),
               "sözlü_isabet": (float(tepe[soz].mean())
                                if bool(soz.any()) else 0.0)}
    top = float(agirlik.sum())
    kayip = float((tekil * agirlik).sum() / max(top, 1e-300))
    assert math.isfinite(kayip), "nokta kaybı sonlu değil"
    isabet = float(np.mean(tepe))
    return {"kayıp": kayip, "isabet": isabet, "örnek": int(h.size),
            "ortalama_born": float(np.mean(p)), "cins": pay}
