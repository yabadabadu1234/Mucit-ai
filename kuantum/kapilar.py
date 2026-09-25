
from __future__ import annotations

import numpy as np

__all__ = ["uniter_mi", "chebyshev", "dik_iki_kubit", "dik_iki_kubit_yigin",
           "dik_iki_kubit_turevi"]

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


def _so4_ureteci(teta: np.ndarray) -> np.ndarray:
    t = np.asarray(teta, float)
    A = np.zeros(t.shape[:-1] + (4, 4))
    iu = np.triu_indices(4, 1)
    A[..., iu[0], iu[1]] = t[..., :6]
    return A - np.swapaxes(A, -1, -2)


def dik_iki_kubit_yigin(teta: np.ndarray) -> np.ndarray:
    A = -2.0 * _so4_ureteci(teta)
    oz, V = np.linalg.eigh(1j * A)
    E = np.matmul(V * np.exp(-1j * oz)[..., None, :],
                  np.conjugate(np.swapaxes(V, -1, -2)))
    return np.real(E).astype(np.float64)


def dik_iki_kubit(teta: np.ndarray) -> np.ndarray:
    return dik_iki_kubit_yigin(np.asarray(teta, float).reshape(-1)[:6])


def _so4_temeli() -> np.ndarray:
    iu = np.triu_indices(4, 1)
    T = np.zeros((6, 4, 4))
    for k in range(6):
        T[k, iu[0][k], iu[1][k]] = 1.0
        T[k, iu[1][k], iu[0][k]] = -1.0
    return -2.0 * T


def dik_iki_kubit_turevi(teta: np.ndarray) -> np.ndarray:
    t = np.asarray(teta, float).reshape(-1)[:6]
    A = -2.0 * _so4_ureteci(t)
    oz, V = np.linalg.eigh(1j * A)
    lam = -1j * oz
    e = np.exp(lam)
    fark = lam[:, None] - lam[None, :]
    bol = np.where(np.abs(fark) < 1e-12,
                   e[:, None],
                   (e[:, None] - e[None, :]) / np.where(
                       np.abs(fark) < 1e-12, 1.0, fark))
    Vd = np.conjugate(V.T)
    out = np.zeros((6, 4, 4), complex)
    for k in range(6):
        Mk = Vd @ _SO4_TEMELI[k] @ V
        out[k] = V @ (Mk * bol) @ Vd
    return out


_SO4_TEMELI = _so4_temeli()
