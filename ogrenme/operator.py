
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List

import numpy as np

__all__ = [
    "DeepONet", "fino_ayristir", "fino_uygula", "spektral_rutbe",
    "cozunurluk_bagimsizligi", "ornek_operator", "l2_norm",
]


def l2_norm(v: np.ndarray, alan: float = 1.0) -> float:
    v = np.asarray(v, float)
    N = v.shape[0]
    return float(np.sqrt(alan / N * np.sum(v * v)))


@dataclass
class DeepONet:
    m: int
    p: int = 16
    gizli: int = 32
    tohum: int = 0
    W_dal: np.ndarray = field(init=False, repr=False)
    W_govde: np.ndarray = field(init=False, repr=False)
    b0: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        if self.m < 1 or self.p < 1:
            raise ValueError("m, p ≥ 1 olmalı")
        r = np.random.default_rng(self.tohum)
        self._A_dal = r.normal(0, 1.0 / np.sqrt(self.m),
                               (self.m, self.gizli))
        self._c_dal = r.uniform(-1, 1, self.gizli)
        self.dal_boyu = self.gizli + self.m
        self._A_govde = r.normal(0, 1.0, (1, self.gizli))
        self._c_govde = r.uniform(-2, 2, self.gizli)
        self.W_dal = np.zeros((self.dal_boyu, self.p))
        self.W_govde = np.zeros((self.gizli, self.p))

    def _dal_ozn(self, U: np.ndarray) -> np.ndarray:
        U = np.atleast_2d(np.asarray(U, float))
        if U.shape[1] != self.m:
            raise ValueError(f"dal girdisi {self.m} sensörlü olmalı")
        return np.hstack([np.tanh(U @ self._A_dal + self._c_dal), U])

    def _govde_ozn(self, y: np.ndarray) -> np.ndarray:
        y = np.asarray(y, float).reshape(-1, 1)
        return np.tanh(y @ self._A_govde + self._c_govde)

    def uydur(self, U: np.ndarray, Y: np.ndarray, hedef: np.ndarray,
              lam: float = 1e-4, tur: int = 30) -> "DeepONet":
        Pd = self._dal_ozn(U)
        Pt = self._govde_ozn(Y)
        H = np.asarray(hedef, float)
        if H.shape != (Pd.shape[0], Pt.shape[0]):
            raise ValueError(f"hedef {(Pd.shape[0], Pt.shape[0])} olmalı")
        r = np.random.default_rng(self.tohum + 1)
        self.W_govde = r.normal(0, 0.5, (self.gizli, self.p))
        tarih: List[float] = []
        for _ in range(tur):
            T = Pt @ self.W_govde
            A = (np.kron(T.T @ T, Pd.T @ Pd)
                 + lam * np.eye(self.dal_boyu * self.p))
            b = (Pd.T @ H @ T).reshape(-1, order="F")
            self.W_dal = np.linalg.solve(A, b).reshape(
                self.dal_boyu, self.p, order="F")
            B = Pd @ self.W_dal
            A2 = np.kron(B.T @ B, Pt.T @ Pt) + lam * np.eye(self.gizli * self.p)
            b2 = (Pt.T @ H.T @ B).reshape(-1, order="F")
            self.W_govde = np.linalg.solve(A2, b2).reshape(
                self.gizli, self.p, order="F")
            nd = float(np.linalg.norm(self.W_dal))
            ng = float(np.linalg.norm(self.W_govde))
            if nd > 1e-300 and ng > 1e-300:
                c = math.sqrt(ng / nd)
                self.W_dal = self.W_dal * c
                self.W_govde = self.W_govde / c
            tarih.append(float(np.mean((self(U, Y) - H) ** 2)))
        self.tarih = tarih
        return self

    def __call__(self, U: np.ndarray, Y: np.ndarray) -> np.ndarray:
        B = self._dal_ozn(U) @ self.W_dal
        T = self._govde_ozn(Y) @ self.W_govde
        return B @ T.T + self.b0


def fino_ayristir(R: np.ndarray, rutbe: int) -> Dict[str, object]:
    R_ = np.asarray(R)
    if R_.ndim != 2:
        raise ValueError("R iki indisli olmalı")
    if not 1 <= rutbe <= min(R_.shape):
        raise ValueError(f"1 ≤ rütbe ≤ {min(R_.shape)} olmalı")
    U, s, Vh = np.linalg.svd(R_, full_matrices=False)
    Ur = U[:, :rutbe] * s[:rutbe]
    Vr = Vh[:rutbe]
    yaklasik = Ur @ Vr
    kalan = float(np.sqrt(np.sum(s[rutbe:] ** 2)))
    return {
        "U": Ur, "V": Vr, "yaklaşık": yaklasik,
        "hata_frobenius": float(np.linalg.norm(yaklasik - R_, "fro")),
        "kapalı_form_hata": kalan,
        "bağıl_hata": kalan / max(float(np.sqrt(np.sum(s ** 2))), 1e-300),
        "parametre_tam": R_.size,
        "parametre_fino": Ur.size + Vr.size,
        "tekil_değerler": s,
    }


def fino_uygula(U: np.ndarray, V: np.ndarray, vhat: np.ndarray
                ) -> np.ndarray:
    return np.asarray(U) @ (np.asarray(V) @ np.asarray(vhat))


def spektral_rutbe(R: np.ndarray, eps: float = 1e-3) -> int:
    s = np.linalg.svd(np.asarray(R), compute_uv=False)
    toplam = float(np.sum(s ** 2))
    if toplam <= 0:
        return 0
    kuyruk = toplam
    for r in range(s.size):
        kuyruk -= float(s[r] ** 2)
        if kuyruk < eps * toplam:
            return r + 1
    return s.size


def ornek_operator(u: np.ndarray, x: np.ndarray) -> np.ndarray:
    u = np.asarray(u, float)
    x = np.asarray(x, float)
    orta = np.concatenate([[0.0], (u[1:] + u[:-1]) / 2 * np.diff(x)])
    return np.cumsum(orta)


def cozunurluk_bagimsizligi(model: DeepONet,
                            u_uret: Callable[[np.ndarray], np.ndarray],
                            sensor: np.ndarray,
                            Y_kaba: np.ndarray,
                            Y_ince: np.ndarray) -> Dict[str, object]:
    ortak = np.intersect1d(Y_kaba, Y_ince)
    if ortak.size < Y_kaba.size:
        raise ValueError("ince ızgara kaba ızgarayı kapsamalı")
    U = np.atleast_2d(u_uret(sensor))
    yk = model(U, Y_kaba)
    yi = model(U, Y_ince)
    idx = np.searchsorted(Y_ince, Y_kaba)
    olcek = max(float(np.max(np.abs(yk))), 1e-300)
    return {
        "azamî_fark": float(np.max(np.abs(yk - yi[:, idx]))),
        "bağıl_fark": float(np.max(np.abs(yk - yi[:, idx]))) / olcek,
        "kaba_nokta": int(Y_kaba.size), "ince_nokta": int(Y_ince.size),
    }
