
from __future__ import annotations

import numpy as np

__all__ = ["qft_dizeyi", "iqft_dizeyi", "trotter", "suzuki2"]


def qft_dizeyi(n: int) -> np.ndarray:
    N = 2 ** n
    j = np.arange(N)
    return np.exp(2j * np.pi * np.outer(j, j) / N) / np.sqrt(N)


def iqft_dizeyi(n: int) -> np.ndarray:
    return qft_dizeyi(n).conj().T


def _uexp(M: np.ndarray, t: float) -> np.ndarray:
    oz, V = np.linalg.eigh(M)
    return V @ np.diag(np.exp(-1j * t * oz)) @ V.conj().T


def trotter(A: np.ndarray, B: np.ndarray, t: float, n: int) -> np.ndarray:
    if n < 1:
        raise ValueError("n ≥ 1 olmalı")
    adim = _uexp(A, t / n) @ _uexp(B, t / n)
    return np.linalg.matrix_power(adim, n)


def suzuki2(A: np.ndarray, B: np.ndarray, t: float, n: int) -> np.ndarray:
    if n < 1:
        raise ValueError("n ≥ 1 olmalı")
    yari = _uexp(A, t / (2 * n))
    adim = yari @ _uexp(B, t / n) @ yari
    return np.linalg.matrix_power(adim, n)
