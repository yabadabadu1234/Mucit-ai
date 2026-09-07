from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

import numpy as np

__all__ = ["TenakuzAyari", "birlikte_gorulme", "dislama_dizeyi",
           "log_bariyer", "tenakuz_tavani"]


@dataclass
class TenakuzAyari:

    lam: float = 0.4
    eps: float = 1e-5
    tau: float = 8.0

    def __post_init__(self) -> None:
        assert float(self.eps) > 0.0, (
            "ε sıfır olamaz: log-bariyerin tavanı sonsuza gider ve tek "
            "bir çevrim bütün mizanı yutar -- ıraksamayı önlemek için "
            "konmuştu")
        assert float(self.tau) > 0.0, (
            "τ_pencere sıfır olamaz: sıfıra bölme")


def birlikte_gorulme(baglamlar: Sequence[Sequence[int]], n: int
                     ) -> np.ndarray:
    n = int(n)
    C = np.zeros((n, n), np.int64)
    for bag in baglamlar:
        t = np.unique(np.asarray(list(bag), np.int64) % n)
        if t.size < 2:
            continue
        C[np.ix_(t, t)] += 1
    np.fill_diagonal(C, 0)
    return C


def dislama_dizeyi(baglamlar: Sequence[Sequence[int]], n: int,
                   ayar: Optional[TenakuzAyari] = None) -> np.ndarray:
    a = ayar or TenakuzAyari()
    C = birlikte_gorulme(baglamlar, n).astype(float)
    S = np.exp(-(C + 1e-4) / float(a.tau))
    assert np.all(np.isfinite(S)), "dışlama dizeyi sonlu değil"
    assert float(S.max()) < 1.0, (
        "S_dışlama tam 1 çıktı -- 10⁻⁴ payı düşmüş demektir; sınır hâli "
        "o pay olmadan ölçülemez")
    return S


def tenakuz_tavani(d: int, ayar: Optional[TenakuzAyari] = None) -> float:
    a = ayar or TenakuzAyari()
    e = float(a.eps)
    return float(math.log((2.0 * float(d) + e) / e))


def log_bariyer(U: np.ndarray, S_cifti: np.ndarray,
                ayar: Optional[TenakuzAyari] = None) -> Dict[str, Any]:
    a = ayar or TenakuzAyari()
    U = np.asarray(U, complex)
    assert U.ndim == 3 and U.shape[1] == U.shape[2], (
        "holonomi bloğu (C, n, n) olmalı; verilen %r" % (U.shape,))
    C, n, _ = U.shape
    e = float(a.eps)
    iz = float(n) + np.real(np.einsum('cii->c', U))
    iz = np.maximum(iz, 0.0)
    arg = (iz + e) / (2.0 * float(n) + e)
    assert np.all(arg > 0.0) and np.all(arg <= 1.0 + 1e-12), (
        "log-bariyerin argümanı (0,1] dışına çıktı -- normalizasyon "
        "bozuk demektir; ceza ödüle dönerdi")
    ham = np.maximum(-np.log(np.minimum(arg, 1.0)), 0.0)
    S = np.asarray(S_cifti, float).reshape(-1)
    assert S.size == C, "dışlama vektörü %d, çevrim %d" % (S.size, C)
    ceza = ham * S
    tavan = tenakuz_tavani(n, a)
    assert np.all(np.isfinite(ceza)), "L_Tenakuz sonlu değil -- IRAKSADI"
    assert float(np.max(ham, initial=0.0)) <= tavan + 1e-9, (
        "ham bariyer tavanı aştı (%.6f > %.6f) -- ε freni tutmuyor"
        % (float(np.max(ham, initial=0.0)), tavan))
    return {"ceza": float(np.mean(ceza)) if C else 0.0,
            "azamî": float(np.max(ceza)) if C else 0.0,
            "ham_azamî": float(np.max(ham)) if C else 0.0,
            "tavan": tavan,
            "dışlama_ortalama": float(np.mean(S)) if C else 0.0,
            "çevrim": int(C)}
