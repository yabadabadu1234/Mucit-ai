
from __future__ import annotations

import math

import numpy as np

__all__ = ["uniter_mi", "chebyshev", "dik_iki_kubit", "dik_iki_kubit_turevi"]

TOL = 1e-10


def uniter_mi(U: np.ndarray, tol: float = TOL) -> bool:
    U = np.asarray(U)
    if U.ndim != 2 or U.shape[0] != U.shape[1]:
        return False
    return bool(np.max(np.abs(U.conj().T @ U
                              - np.eye(U.shape[0]))) < tol)


def chebyshev(x, derece: int):
    x = np.clip(np.asarray(x, float), -1.0, 1.0)
    T = np.empty(x.shape + (int(derece) + 1,), float)
    T[..., 0] = 1.0
    if int(derece) >= 1:
        T[..., 1] = x
    for d in range(2, int(derece) + 1):
        T[..., d] = 2.0 * x * T[..., d - 1] - T[..., d - 2]
    return T


def dik_iki_kubit(teta: np.ndarray) -> np.ndarray:
    t = np.asarray(teta, float).reshape(-1)[:2]
    ca, sa = math.cos(float(t[0])), math.sin(float(t[0]))
    cb, sb = math.cos(float(t[1])), math.sin(float(t[1]))
    G = np.zeros((4, 4), np.float64)
    G[0, 0], G[0, 3] = ca, -sa
    G[3, 0], G[3, 3] = sa, ca
    G[1, 1], G[1, 2] = cb, -sb
    G[2, 1], G[2, 2] = sb, cb
    return G


def dik_iki_kubit_turevi(teta: np.ndarray) -> np.ndarray:
    t = np.asarray(teta, float).reshape(-1)[:2]
    ca, sa = math.cos(float(t[0])), math.sin(float(t[0]))
    cb, sb = math.cos(float(t[1])), math.sin(float(t[1]))
    dA = np.zeros((4, 4), np.float64)
    dA[0, 0], dA[0, 3] = -sa, -ca
    dA[3, 0], dA[3, 3] = ca, -sa
    dB = np.zeros((4, 4), np.float64)
    dB[1, 1], dB[1, 2] = -sb, -cb
    dB[2, 1], dB[2, 2] = cb, -sb
    return np.stack([dA, dB])
