
from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "I2", "X", "Y", "Z", "H", "S_", "Sdg", "T_", "Tdg",
    "Rx", "Ry", "Rz", "U1", "U2", "U3", "faz",
    "CNOT", "CZ", "SWAP", "iSWAP", "CRx", "CRz", "kontrollu",
    "RXX", "RYY", "RZZ", "TOFFOLI", "FREDKIN", "molmer_sorensen",
    "uniter_mi", "esdeger_mi", "yerlestir", "kron", "chebyshev",
    "PAULI", "komutator", "antikomutator",
]

TOL = 1e-10


I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S_ = np.diag([1, 1j]).astype(complex)
Sdg = S_.conj().T
T_ = np.diag([1, np.exp(1j * np.pi / 4)]).astype(complex)
Tdg = T_.conj().T

PAULI: Dict[str, np.ndarray] = {"I": I2, "X": X, "Y": Y, "Z": Z}


def _donme(P: np.ndarray, teta: float) -> np.ndarray:
    return np.cos(teta / 2) * np.eye(P.shape[0], dtype=complex) \
        - 1j * np.sin(teta / 2) * P


def Rx(teta: float) -> np.ndarray:
    return _donme(X, teta)


def Ry(teta: float) -> np.ndarray:
    return _donme(Y, teta)


def Rz(teta: float) -> np.ndarray:
    return _donme(Z, teta)


def U1(lam: float) -> np.ndarray:
    return np.diag([1.0 + 0j, np.exp(1j * lam)])


def U2(fi: float, lam: float) -> np.ndarray:
    return np.array([[1, -np.exp(1j * lam)],
                     [np.exp(1j * fi), np.exp(1j * (fi + lam))]],
                    dtype=complex) / np.sqrt(2)


def U3(teta: float, fi: float, lam: float) -> np.ndarray:
    c, s = np.cos(teta / 2), np.sin(teta / 2)
    return np.array([[c, -np.exp(1j * lam) * s],
                     [np.exp(1j * fi) * s, np.exp(1j * (fi + lam)) * c]],
                    dtype=complex)


def faz(a: float) -> complex:
    return complex(np.exp(1j * a))


def kron(*dizeyler: np.ndarray) -> np.ndarray:
    sonuc = np.array([[1.0 + 0j]])
    for d in dizeyler:
        sonuc = np.kron(sonuc, d)
    return sonuc


def kontrollu(U: np.ndarray, n_kontrol: int = 1) -> np.ndarray:
    d = U.shape[0]
    K = 2 ** n_kontrol
    C = np.eye(K * d, dtype=complex)
    C[(K - 1) * d:, (K - 1) * d:] = U
    return C


CNOT = kontrollu(X)
CZ = kontrollu(Z)
SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0],
                 [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)
iSWAP = np.array([[1, 0, 0, 0], [0, 0, 1j, 0],
                  [0, 1j, 0, 0], [0, 0, 0, 1]], dtype=complex)
TOFFOLI = kontrollu(X, 2)
FREDKIN = kontrollu(SWAP, 1)


def CRx(teta: float) -> np.ndarray:
    return kontrollu(Rx(teta))


def CRz(teta: float) -> np.ndarray:
    return kontrollu(Rz(teta))


def _cift_donme(P: np.ndarray, teta: float) -> np.ndarray:
    PP = np.kron(P, P)
    return np.cos(teta / 2) * np.eye(4, dtype=complex) \
        - 1j * np.sin(teta / 2) * PP


def RXX(teta: float) -> np.ndarray:
    return _cift_donme(X, teta)


def RYY(teta: float) -> np.ndarray:
    return _cift_donme(Y, teta)


def RZZ(teta: float) -> np.ndarray:
    return _cift_donme(Z, teta)


def molmer_sorensen(n: int, teta: float, fi: float) -> np.ndarray:
    if n < 1:
        raise ValueError("n ≥ 1 olmalı")
    A = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n):
        A = A + yerlestir(np.cos(fi) * X + np.sin(fi) * Y, [i], n)
    M = A @ A
    oz, V = np.linalg.eigh(M)
    return V @ np.diag(np.exp(-1j * teta / 4 * oz)) @ V.conj().T


def yerlestir(U: np.ndarray, kubitler: Sequence[int], n: int) -> np.ndarray:
    k = len(kubitler)
    if U.shape != (2 ** k, 2 ** k):
        raise ValueError(f"U {2**k}×{2**k} olmalı, {U.shape} verildi")
    if len(set(kubitler)) != k:
        raise ValueError("kübitler tekrarsız olmalı")
    if any(not 0 <= q < n for q in kubitler):
        raise ValueError("kübit indisi kayıt dışında")

    kalan = [q for q in range(n) if q not in kubitler]
    sira = list(kubitler) + kalan
    tam = np.kron(U, np.eye(2 ** (n - k), dtype=complex))
    P = _permutasyon_dizeyi(sira, n)
    return P.conj().T @ tam @ P


def _permutasyon_dizeyi(sira: Sequence[int], n: int) -> np.ndarray:
    N = 2 ** n
    P = np.zeros((N, N), dtype=complex)
    for eski in range(N):
        bitler = [(eski >> (n - 1 - q)) & 1 for q in range(n)]
        yeni = 0
        for j, q in enumerate(sira):
            yeni |= bitler[q] << (n - 1 - j)
        P[yeni, eski] = 1.0
    return P


def uniter_mi(U: np.ndarray, tol: float = TOL) -> bool:
    U = np.asarray(U)
    if U.ndim != 2 or U.shape[0] != U.shape[1]:
        return False
    return bool(np.max(np.abs(U.conj().T @ U
                              - np.eye(U.shape[0]))) < tol)


def esdeger_mi(A: np.ndarray, B: np.ndarray,
               kuresel_faz_serbest: bool = False,
               tol: float = TOL) -> bool:
    A, B = np.asarray(A), np.asarray(B)
    if A.shape != B.shape:
        return False
    if not kuresel_faz_serbest:
        return bool(np.max(np.abs(A - B)) < tol)
    m = np.abs(B) > tol
    if not np.any(m):
        return bool(np.max(np.abs(A)) < tol)
    oran = A[m] / B[m]
    if abs(abs(oran[0]) - 1.0) > tol:
        return False
    return bool(np.max(np.abs(oran - oran[0])) < tol)


def komutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return A @ B - B @ A


def antikomutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return A @ B + B @ A


def _gosterim() -> str:
    s: List[str] = []

    s.append("=== Pauli cebri ===")
    eps = {("X", "Y"): "Z", ("Y", "Z"): "X", ("Z", "X"): "Y"}
    for (a, b), c in eps.items():
        k = komutator(PAULI[a], PAULI[b])
        s.append(f"  [{a},{b}] = 2i·{c} mi? "
                 f"{np.max(np.abs(k - 2j * PAULI[c])):.2e}")
    for a in "XYZ":
        for b in "XYZ":
            ak = antikomutator(PAULI[a], PAULI[b])
            bekle = 2 * I2 if a == b else np.zeros((2, 2))
            if np.max(np.abs(ak - bekle)) > 1e-12:
                s.append(f"  {{{a},{b}}} BEKLENMEDİK")
    s.append("  {σ_a,σ_b} = 2δ_ab I: bütün 9 çiftte sağlandı")

    s.append("\n=== Üniterlik: bütün kapılar ===")
    kapilar = {
        "I": I2, "X": X, "Y": Y, "Z": Z, "H": H, "S": S_, "S†": Sdg,
        "T": T_, "T†": Tdg, "Rx(1.1)": Rx(1.1), "Ry(1.1)": Ry(1.1),
        "Rz(1.1)": Rz(1.1), "U1(0.7)": U1(0.7), "U2(.3,.9)": U2(.3, .9),
        "U3(.4,.5,.6)": U3(.4, .5, .6), "CNOT": CNOT, "CZ": CZ,
        "SWAP": SWAP, "iSWAP": iSWAP, "CRx(.8)": CRx(.8),
        "RXX(.6)": RXX(.6), "RYY(.6)": RYY(.6), "RZZ(.6)": RZZ(.6),
        "Toffoli": TOFFOLI, "Fredkin": FREDKIN,
        "MS(3,.7,.2)": molmer_sorensen(3, .7, .2),
    }
    bozuk = [ad for ad, U in kapilar.items() if not uniter_mi(U)]
    s.append(f"  {len(kapilar)} kapı denendi, üniter olmayan: "
             f"{bozuk if bozuk else 'yok'}")

    s.append("\n=== K7 tashihi: U₁(λ) ile R_z(λ) ===")
    for lam in (0.7, np.pi / 2, 2.4):
        u, r = U1(lam), Rz(lam)
        s.append(f"  λ={lam:.4f}: tam eşit mi? {esdeger_mi(u, r)}"
                 f"   küresel faz serbest? "
                 f"{esdeger_mi(u, r, kuresel_faz_serbest=True)}"
                 f"   U₁ = e^{{iλ/2}}R_z mi? "
                 f"{esdeger_mi(u, faz(lam / 2) * r)}")
    s.append("  KONTROL altında fark ölçülebilir hâle geliyor:")
    for lam in (0.7, 2.4):
        c1, c2 = kontrollu(U1(lam)), kontrollu(Rz(lam))
        s.append(f"    λ={lam:.2f}: CU₁ = CR_z mi? {esdeger_mi(c1, c2)}"
                 f"   küresel faz serbest bile mi? "
                 f"{esdeger_mi(c1, c2, kuresel_faz_serbest=True)}"
                 f"   ‖fark‖∞ = {np.max(np.abs(c1 - c2)):.4f}")

    s.append("\n=== Bilinen özdeşlikler ===")
    ozdeslikler = [
        ("H² = I", H @ H, I2, False),
        ("HXH = Z", H @ X @ H, Z, False),
        ("HZH = X", H @ Z @ H, X, False),
        ("S² = Z", S_ @ S_, Z, False),
        ("T² = S", T_ @ T_, S_, False),
        ("X = i·Rx(π)", X, 1j * Rx(np.pi), False),
        ("CNOT² = I", CNOT @ CNOT, np.eye(4), False),
        ("SWAP² = I", SWAP @ SWAP, np.eye(4), False),
        ("SWAP = CNOT·CNOT'·CNOT", SWAP,
         CNOT @ yerlestir(CNOT, [1, 0], 2) @ CNOT, False),
        ("Toffoli² = I", TOFFOLI @ TOFFOLI, np.eye(8), False),
        ("RZZ(θ)= e^{-iθ/2 Z⊗Z}", RZZ(0.9),
         np.diag(np.exp(-0.45j * np.array([1, -1, -1, 1]))), False),
    ]
    for ad, A, B, faz_serbest in ozdeslikler:
        ok = esdeger_mi(A, B, kuresel_faz_serbest=faz_serbest)
        s.append(f"  {ad:22s} {ok}"
                 + ("   (küresel faz serbest)" if faz_serbest else ""))

    s.append("\n=== Kübit sırası: q₀ en anlamlı bit ===")
    v01 = np.zeros(4, dtype=complex); v01[1] = 1
    v10 = np.zeros(4, dtype=complex); v10[2] = 1
    s.append(f"  CNOT|01⟩ = |01⟩ mi? "
             f"{np.allclose(CNOT @ v01, v01)}")
    s.append(f"  CNOT|10⟩ = |11⟩ mi? "
             f"{np.allclose(CNOT @ v10, np.eye(4)[3])}")
    ters = yerlestir(CNOT, [1, 0], 2)
    s.append(f"  kontrol/hedef takas edilince CNOT|01⟩ = |11⟩ mi? "
             f"{np.allclose(ters @ v01, np.eye(4)[3])}")
    s.append(f"  ve SWAP·CNOT·SWAP = takas edilmiş CNOT mi? "
             f"{esdeger_mi(SWAP @ CNOT @ SWAP, ters)}")

    s.append("\n=== Yerleştirme: 4 kübitlik kayıtta ===")
    n = 4
    for kubitler in ([0], [2], [0, 1], [1, 3], [3, 1], [0, 2, 3]):
        U = {1: H, 2: CNOT, 3: TOFFOLI}[len(kubitler)]
        G = yerlestir(U, kubitler, n)
        s.append(f"  {str(kubitler):10s} → şekil {G.shape}"
                 f"  üniter mi? {uniter_mi(G)}")

    s.append("\n=== Mølmer–Sørensen: |0…0⟩ nereye gidiyor? ===")
    for n in (2, 3, 4, 5, 6):
        U = molmer_sorensen(n, np.pi / 2, 0.0)
        sifir = np.zeros(2 ** n, dtype=complex); sifir[0] = 1
        c = U @ sifir
        dolu = int(np.count_nonzero(np.abs(c) > 1e-9))
        ghz = (abs(abs(c[0]) ** 2 - 0.5) < 1e-9
               and abs(abs(c[-1]) ** 2 - 0.5) < 1e-9 and dolu == 2)
        s.append(f"  n={n}: {dolu:2d}/{2**n:2d} temel durum dolu"
                 f"   GHZ mi? {ghz}")
    s.append("  Ölçülen kaide: ÇİFT n'de MS(π/2) tam olarak GHZ veriyor")
    s.append("  ((|0…0⟩+|1…1⟩)/√2); TEK n'de çift-parite alt uzayına")
    s.append("  yayılıyor. İkisi de doğru MS davranışıdır — kapı bütün")
    s.append("  çiftleri aynı anda bağladığı için netice n'in paritesine")
    s.append("  bağlıdır.")
    return "\n".join(s)


def chebyshev(x, derece: int):
    x = np.clip(np.asarray(x, float), -1.0, 1.0)
    T = np.empty(x.shape + (int(derece) + 1,), float)
    T[..., 0] = 1.0
    if int(derece) >= 1:
        T[..., 1] = x
    for d in range(2, int(derece) + 1):
        T[..., d] = 2.0 * x * T[..., d - 1] - T[..., d - 2]
    return T


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())


KAPI_USULU: str = "us"

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
