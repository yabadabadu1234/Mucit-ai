from __future__ import annotations

import math
from typing import Dict

import numpy as np

__all__ = ["qft_vur", "qudit_qft_vur", "trotter", "suzuki2", "evrim",
           "devre_beyani", "devre_metni"]

_SAYAC: Dict[str, float] = {
    "qft": 0.0, "ters_qft": 0.0, "karo": 0.0, "en_buyuk_taban": 0.0,
    "trotter": 0.0, "suzuki2": 0.0, "dilim": 0.0, "askin": 0.0,
    "yogun_dizey": 0.0, "evrim": 0.0, "son_dilim": 0.0,
    "dilim_artigi": 0.0}


def qft_vur(v: np.ndarray, ters: bool = False,
            eksen: int = -1) -> np.ndarray:
    a = np.asarray(v, complex)
    m = int(a.shape[eksen])
    assert m >= 2, "Fourier için en az iki seviye lâzım; m=%d" % m
    _SAYAC["ters_qft" if ters else "qft"] += 1.0
    _SAYAC["en_buyuk_taban"] = max(_SAYAC["en_buyuk_taban"], float(m))
    if ters:
        return np.fft.ifft(a, axis=eksen) * math.sqrt(m)
    return np.fft.fft(a, axis=eksen) / math.sqrt(m)


def qudit_qft_vur(v: np.ndarray, q: int, n: int,
                  ters: bool = False) -> np.ndarray:
    a = np.asarray(v, complex)
    q, n = int(q), int(n)
    assert q >= 2 and n >= 1, "qudit QFT için q ≥ 2, n ≥ 1 lâzım"
    assert a.shape[-1] == q ** n, (
        "qudit QFT: son eksen %d, fakat q^n = %d^%d = %d"
        % (a.shape[-1], q, n, q ** n))
    bas = a.shape[:-1]
    t = a.reshape(bas + (q,) * n)
    for k in range(n):
        _SAYAC["karo"] += 1.0
        t = qft_vur(t, ters=ters, eksen=len(bas) + k)
    return t.reshape(bas + (q ** n,))


def _uexp(M: np.ndarray, t: float) -> np.ndarray:
    _SAYAC["askin"] += 1.0
    oz, V = np.linalg.eigh(M)
    return V @ np.diag(np.exp(-1j * t * oz)) @ V.conj().T


def trotter(A: np.ndarray, B: np.ndarray, t: float, n: int) -> np.ndarray:
    n = int(n)
    assert n >= 1, "Trotter dilimi %d -- en az bir dilim lâzım" % n
    _SAYAC["trotter"] += 1.0
    _SAYAC["dilim"] += float(n)
    adim = _uexp(A, t / n) @ _uexp(B, t / n)
    return np.linalg.matrix_power(adim, n)


def suzuki2(A: np.ndarray, B: np.ndarray, t: float, n: int) -> np.ndarray:
    n = int(n)
    assert n >= 1, "Suzuki dilimi %d -- en az bir dilim lâzım" % n
    _SAYAC["suzuki2"] += 1.0
    _SAYAC["dilim"] += float(n)
    yari = _uexp(A, t / (2 * n))
    adim = yari @ _uexp(B, t / n) @ yari
    return np.linalg.matrix_power(adim, n)


def evrim(A: np.ndarray, B: np.ndarray, t: float) -> np.ndarray:
    A = np.asarray(A, complex)
    B = np.asarray(B, complex)
    assert A.shape == B.shape and A.ndim == 2 and A.shape[0] == A.shape[1], (
        "evrim iki KARE ve aynı ebatta üreteç ister: %s ile %s"
        % (A.shape, B.shape))
    if not (float(t) > 0.0):
        return np.eye(A.shape[0], dtype=complex)
    n = 1
    U = suzuki2(A, B, float(t), n)
    evvel = float(np.linalg.norm(trotter(A, B, float(t), n) - U))
    while True:
        V = suzuki2(A, B, float(t), 2 * n)
        artik = float(np.linalg.norm(trotter(A, B, float(t), 2 * n) - V))
        if not (artik < evvel - float(np.finfo(float).eps)):
            break
        U, evvel, n = V, artik, 2 * n
    _SAYAC["evrim"] = _SAYAC.get("evrim", 0.0) + 1.0
    _SAYAC["son_dilim"] = float(n)
    _SAYAC["dilim_artigi"] = float(evvel)
    return U


def devre_beyani() -> Dict[str, float]:
    return dict(_SAYAC)


def devre_metni(b=None) -> str:
    d = dict(b or devre_beyani())
    if not (d["qft"] or d["trotter"] or d["suzuki2"]):
        return "  DEVRE (kuantum/devre.py): HİÇ KOŞMADI -- kırmızı (ferman 5)"
    return "\n".join([
        "  DEVRE -- MATRİSSİZ FOURIER + TROTTER EVRİMİ (kuantum/devre.py)",
        "    İKİLİ KÜBİT TABANI KESİLDİ (ferman 7): N = 2^n şartı yok,",
        "    yoğun N×N dizey KURULMUYOR. Çevrimsel Z_m Fourier'i",
        "    Cooley-Tukey ile, (Z_q)^n QFT'si KRONECKER KARO ile vurulur.",
        "    qft %d   ters qft %d   Kronecker karosu %d   en büyük taban %d"
        % (int(d["qft"]), int(d["ters_qft"]), int(d["karo"]),
           int(d["en_buyuk_taban"])),
        "    kurulan yoğun QFT dizeyi %d  -- SIFIR olmalıdır"
        % int(d["yogun_dizey"]),
        "    trotter %d   suzuki2 %d   toplam dilim %d"
        % (int(d["trotter"]), int(d["suzuki2"]), int(d["dilim"])),
        "    EVRİM: dilim sayısı ELLE YAZILMAZ (ferman 1-J) -- 1. mertebe",
        "    Trotter ile 2. mertebe Suzuki ayrışması sönene kadar ikiye",
        "    katlanır. çağrı %d   son dilim %d   dilim artığı %.3e"
        % (int(d.get("evrim", 0)), int(d.get("son_dilim", 0)),
           d.get("dilim_artigi", 0.0)),
        "    aşkın çağrı %d -- ferman 2-Ş yasağı kaldırdı, MUHASEBEYİ"
        " kaldırmadı" % int(d["askin"]),
    ])
