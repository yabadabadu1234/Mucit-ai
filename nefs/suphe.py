from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

import numpy as np

__all__ = ["SupheAyari", "tearuz", "modal_kip", "suphe_manifoldu",
           "suphe_beyani", "suphe_sifirla"]


@dataclass
class SupheAyari:

    acik: int = 1
    sonum: float = 0.05
    kip_kenari: float = 0.25
    tevakkuf_esigi: float = 0.35
    parite_lifi: int = 2
    lif_yapisi: tuple = (16, 16, 16)


_SAYAC: Dict[str, float] = {
    "çağrı": 0.0, "tearuz": 0.0, "dallanma": 0.0, "merak": 0.0,
    "buhar": 0.0, "tevakkuf": 0.0, "örnek": 0.0,
    "μ_önce": 0.0, "μ_sonra": 0.0}


def tearuz(psi_p: np.ndarray, psi_np: np.ndarray) -> float:
    a = np.asarray(psi_p, complex).reshape(-1)
    b = np.asarray(psi_np, complex).reshape(-1)
    na = max(float(np.linalg.norm(a)), 1e-300)
    nb = max(float(np.linalg.norm(b)), 1e-300)
    return float(abs(complex(np.vdot(a / na, b / nb))))


def modal_kip(omega: float, kenar: float = 0.25) -> str:
    if omega > 1.0 - kenar:
        return "zorunlu"
    if omega < -1.0 + kenar:
        return "muhâl"
    return "mümkün"


def suphe_manifoldu(haller: Sequence[np.ndarray],
                    omegalar: Sequence[float],
                    yakin: Optional[np.ndarray] = None,
                    ayar: Optional[SupheAyari] = None) -> Dict[str, Any]:
    from .sadakat import SadakatAyari
    a = ayar or SupheAyari()
    _SAYAC["çağrı"] += 1.0
    m = len(haller)
    if m == 0 or not int(a.acik):
        return {"μ": np.zeros(0), "tevakkuf": 0, "tearuz": 0,
                "dallanma": 0, "merak": [], "açık": bool(int(a.acik))}

    H = np.stack([np.asarray(h, complex).reshape(-1) for h in haller])
    H = H / np.maximum(np.linalg.norm(H, axis=-1, keepdims=True), 1e-300)
    mu = (np.ones(m, float) if yakin is None
          else np.asarray(yakin, float).reshape(-1).copy())
    assert mu.size == m, "yakîn vektörü %d, hâl %d" % (mu.size, m)
    _SAYAC["μ_önce"] += float(np.mean(mu))

    from .sadakat import mantiki_degil
    sa = SadakatAyari(acik=1, parite_lifi=int(a.parite_lifi),
                      lif_yapisi=tuple(a.lif_yapisi))
    d = H.shape[1]
    lif_carpim = 1
    for x in a.lif_yapisi:
        lif_carpim *= int(x)
    if d == lif_carpim:
        S = mantiki_degil(H, sa)
    else:
        maske = 3 if d >= 4 else 1
        S = H[:, np.arange(d) ^ maske]
    ortusme = np.abs(np.einsum('ij,ij->i', H.conj(), S))
    mu = mu * (1.0 - ortusme)
    t_say = int(np.count_nonzero(ortusme > 1.0 - float(a.kip_kenari)))
    _SAYAC["tearuz"] += float(t_say)

    om = np.asarray(list(omegalar), float)
    dal = 0
    if om.size:
        mumkun = np.array([modal_kip(float(o), float(a.kip_kenari))
                           == "mümkün" for o in om])
        dal = int(np.count_nonzero(mumkun))
        if dal:
            kir = 1.0 - float(dal) / float(om.size)
            mu = mu * max(kir, 0.0)
    _SAYAC["dallanma"] += float(dal)

    g = float(a.sonum)
    assert 0.0 <= g < 1.0, "sönüm γ [0,1) olmalı"
    mu = mu * (1.0 - g)
    _SAYAC["buhar"] += float(np.count_nonzero(mu < float(a.tevakkuf_esigi)))

    suphe = 1.0 - mu
    merak = [int(i) for i in np.nonzero(suphe > mu)[0]]
    _SAYAC["merak"] += float(len(merak))

    tevakkuf = int(np.count_nonzero(mu < float(a.tevakkuf_esigi)))
    _SAYAC["tevakkuf"] += float(tevakkuf)
    _SAYAC["örnek"] += float(m)
    _SAYAC["μ_sonra"] += float(np.mean(mu))
    assert np.all(np.isfinite(mu)), "yakîn sonlu değil"
    return {"μ": mu, "şüphe": suphe, "tevakkuf": tevakkuf,
            "tearuz": t_say, "dallanma": dal, "merak": merak,
            "açık": True}


def suphe_beyani() -> Dict[str, Any]:
    c = max(1.0, _SAYAC["çağrı"])
    return {"çağrı": int(_SAYAC["çağrı"]),
            "tearuz": int(_SAYAC["tearuz"]),
            "dallanma": int(_SAYAC["dallanma"]),
            "merak": int(_SAYAC["merak"]),
            "buhar": int(_SAYAC["buhar"]),
            "tevakkuf": int(_SAYAC["tevakkuf"]),
            "örnek": int(_SAYAC["örnek"]),
            "μ_önce": float(_SAYAC["μ_önce"] / c),
            "μ_sonra": float(_SAYAC["μ_sonra"] / c)}


def suphe_sifirla() -> None:
    for k in _SAYAC:
        _SAYAC[k] = 0.0
