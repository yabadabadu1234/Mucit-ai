"""Lie — cebir, Jacobi özdeşliği ve grup üzerinde güncelleme.

Mutasarrıfa ``ℛ``nın üreteçleri bir Lie cebri teşkil eder.  Üç mesele:

**1. Jacobi özdeşliği.**  ``[X,[Y,Z]] + [Y,[Z,X]] + [Z,[X,Y]] = 0``.
Dizey komütatörü için bu bir **teoremdir**, sağlanması gereken bir
kısıt değil: açılınca 12 terim ikişer ikişer götürür.  Yani sayısal
bir "Jacobi onarımı" gerekmez; sağlanmıyorsa kod yanlıştır.  Burada
ölçülüyor.  Ama **yapı sabitleriyle** verilen bir cebirde Jacobi bir
kısıttır ve orada sınanması gerekir; ikisi ayrı ayrı ele alınıyor.

**2. Gruptan çıkmama.**  ``X ← X − η∇L`` yapılırsa netice ``SO(n)``
içinde kalmaz.  Doğrusu, cebirde adım atıp **üstel harita** ile gruba
dönmektir:

.. math::  A = -\\eta\\,\\Pi_{\\mathfrak{g}}(\\nabla L), \\qquad
           X_{t+1} = X_t \\exp(A)

``Π_𝔤`` cebire izdüşümdür (``so(n)`` için antisimetrik kısım).  Üstel
harita **kapalı formda** hesaplanır (Rodrigues / özayrışım), seri
kesmesiyle değil.  İki yol da ölçülüp karşılaştırılıyor.

**3. Kutup ayrışımıyla geri getirme.**  Sayısal sürüklenmeyle gruptan
azıcık çıkılırsa, en yakın dik dizey ``UV^T``dir (kutup ayrışımı).
Bu, Frobenius normunda **en iyi** yaklaşımdır; simetrikleştirme
değildir (K28 tashihi).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "braket", "jacobi_hatasi", "so_izdusumu", "uslu_harita",
    "so_n_mi", "en_yakin_dik", "grup_adimi", "yapi_sabitleri",
    "yapi_sabiti_jacobi_hatasi", "so3_uretecleri", "sun_uretecleri",
]

TOL = 1e-10


# ══════════════════════════════════════════════════════════════════════
#  Cebir
# ══════════════════════════════════════════════════════════════════════

def braket(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """``[A,B] = AB − BA``."""
    A, B = np.asarray(A), np.asarray(B)
    return A @ B - B @ A


def jacobi_hatasi(X: np.ndarray, Y: np.ndarray, Z: np.ndarray) -> float:
    """``‖[X,[Y,Z]] + [Y,[Z,X]] + [Z,[X,Y]]‖_F``.

    Dizey komütatörü için bu **sıfırdır** (teorem).  Ölçüm, kodun
    doğruluğunun sağlamasıdır; sıfırdan büyük çıkarsa braket yanlış
    kurulmuş demektir.
    """
    E = (braket(X, braket(Y, Z)) + braket(Y, braket(Z, X))
         + braket(Z, braket(X, Y)))
    return float(np.linalg.norm(E, "fro"))


def so_izdusumu(M: np.ndarray) -> np.ndarray:
    """``Π_{so(n)}(M) = (M − Mᵀ)/2`` — antisimetrik kısım.

    ``so(n)``, antisimetrik dizeylerin uzayıdır ve dik izdüşüm
    (Frobenius iç çarpımında) tam olarak antisimetrik kısımdır:
    simetrik ile antisimetrik parçalar diktir.
    """
    M = np.asarray(M, float)
    return (M - M.T) / 2.0


def uslu_harita(A: np.ndarray, yontem: str = "ozayrisim") -> np.ndarray:
    """``exp(A)`` — antisimetrik ``A`` için.

    ``yontem="ozayrisim"``: ``A`` antisimetrik ⟹ ``iA`` Hermitesel,
    özayrışım **tam** üsteli verir; seri kesmesi yok.

    ``yontem="seri"``: Taylor serisi (kıyas için).  Kaç terimle ne
    kadar yaklaştığı ölçülebilsin diye duruyor; ``‖A‖`` büyükken
    seri hem yavaş hem kararsızdır.
    """
    A = np.asarray(A, float)
    if yontem == "ozayrisim":
        oz, V = np.linalg.eigh(1j * A)          # iA Hermitesel
        return np.real(V @ np.diag(np.exp(-1j * oz)) @ V.conj().T)
    if yontem == "seri":
        sonuc = np.eye(A.shape[0])
        terim = np.eye(A.shape[0])
        for k in range(1, 40):
            terim = terim @ A / k
            sonuc = sonuc + terim
        return sonuc
    raise ValueError("yöntem: 'ozayrisim' veya 'seri'")


def so_n_mi(X: np.ndarray, tol: float = 1e-9) -> bool:
    """``XᵀX = I`` **ve** ``det X = +1``.

    Yalnız ``XᵀX = I`` bakmak ``O(n)``i verir; yansımalar (det = −1)
    da geçer.  ``SO(n)`` bağlantılı bileşen olduğundan üstel harita
    oraya asla götürmez, ama bir *denetim* olarak ikisi de aranmalıdır.
    """
    X = np.asarray(X, float)
    n = X.shape[0]
    if X.shape != (n, n):
        return False
    if np.max(np.abs(X.T @ X - np.eye(n))) > tol:
        return False
    return abs(float(np.linalg.det(X)) - 1.0) < tol


def en_yakin_dik(M: np.ndarray) -> np.ndarray:
    """Frobenius normunda en yakın dik dizey: ``UVᵀ`` (kutup ayrışımı).

    Simetrikleştirme (``(M+Mᵀ)/2``) bunu **vermez** ve dikliği geri
    getirmez (K28 tashihi).  Kutup ayrışımı ise ``argmin_{QᵀQ=I}
    ‖Q−M‖_F``in kapalı çözümüdür.
    """
    U, _, Vt = np.linalg.svd(np.asarray(M, float))
    return U @ Vt


def grup_adimi(X: np.ndarray, grad: np.ndarray, eta: float) -> np.ndarray:
    """``X ← X exp(−η Π_𝔤(grad))`` — grup içinde kalan güncelleme."""
    A = -eta * so_izdusumu(np.asarray(grad, float))
    return np.asarray(X, float) @ uslu_harita(A)


# ══════════════════════════════════════════════════════════════════════
#  Yapı sabitleri
# ══════════════════════════════════════════════════════════════════════

def so3_uretecleri() -> List[np.ndarray]:
    """``so(3)``ün standart tabanı: ``(L_a)_{bc} = −ε_{abc}``.

    Bu tabanda ``[L_a, L_b] = ε_{abc} L_c``, yani yapı sabitleri
    Levi-Civita sembolüdür.
    """
    L = []
    for a in range(3):
        M = np.zeros((3, 3))
        for b in range(3):
            for c in range(3):
                M[b, c] = -_levi_civita(a, b, c)
        L.append(M)
    return L


def _levi_civita(i: int, j: int, k: int) -> float:
    if len({i, j, k}) < 3:
        return 0.0
    perm = [i, j, k]
    isaret = 1.0
    for a in range(3):
        for b in range(a + 1, 3):
            if perm[a] > perm[b]:
                isaret = -isaret
    return isaret


def sun_uretecleri(n: int) -> List[np.ndarray]:
    """``su(n)``in bir tabanı: izsiz anti-Hermitesel dizeyler.

    Boyut ``n²−1``; kurulan taban sayısı bununla **karşılaştırılır**
    ve uyuşmazsa hata verilir -- eksik bir taban, yapı sabitlerini
    sessizce yanlış yapardı.
    """
    if n < 2:
        raise ValueError("n ≥ 2 olmalı")
    T: List[np.ndarray] = []
    for i in range(n):
        for j in range(i + 1, n):
            M = np.zeros((n, n), dtype=complex)
            M[i, j], M[j, i] = 1j, 1j          # anti-Hermitesel simetrik
            T.append(M)
            M2 = np.zeros((n, n), dtype=complex)
            M2[i, j], M2[j, i] = 1.0, -1.0
            T.append(M2)
    for k in range(1, n):
        kosegen = np.zeros(n, dtype=complex)
        kosegen[:k] = 1j
        kosegen[k] = -1j * k
        T.append(np.diag(kosegen) / math.sqrt(k * (k + 1)))
    if len(T) != n * n - 1:
        raise ValueError(f"taban eksik: {len(T)} ≠ {n*n-1}")
    return T


def yapi_sabitleri(taban: Sequence[np.ndarray]) -> np.ndarray:
    """``[T_a, T_b] = Σ_c f_{ab}^c T_c`` — ``f`` en küçük karelerle.

    Taban vektörleri Frobenius iç çarpımında dik olmayabilir; o yüzden
    ``f`` doğrudan iz alarak değil, **çözülerek** bulunur.  Sonra
    açılımın gerçekten tuttuğu ölçülür (kalan artık).
    """
    T = [np.asarray(t) for t in taban]
    d = len(T)
    A = np.stack([t.reshape(-1) for t in T], axis=1)     # (n², d)
    f = np.zeros((d, d, d), dtype=complex)
    artik = 0.0
    for a in range(d):
        for b in range(d):
            hedef = braket(T[a], T[b]).reshape(-1)
            c, *_ = np.linalg.lstsq(A, hedef, rcond=None)
            f[a, b] = c
            artik = max(artik, float(np.linalg.norm(A @ c - hedef)))
    if artik > 1e-8:
        raise ValueError(f"braket tabanın dışına çıkıyor (artık {artik:.2e}) "
                         "— verilen küme bir Lie cebri değil")
    return f


def yapi_sabiti_jacobi_hatasi(f: np.ndarray) -> float:
    """``Σ_e (f_{ab}^e f_{ec}^d + f_{bc}^e f_{ea}^d + f_{ca}^e f_{eb}^d)``.

    Yapı sabitleriyle verilen bir cebirde Jacobi **kısıttır**, teorem
    değil: keyfî ``f`` bunu sağlamaz.  Dizeylerden türetilmiş ``f``
    ise sağlamak zorundadır ve ölçüm bunu doğrular.
    """
    f = np.asarray(f)
    t1 = np.einsum("abe,ecd->abcd", f, f)
    t2 = np.einsum("bce,ead->abcd", f, f)
    t3 = np.einsum("cae,ebd->abcd", f, f)
    return float(np.max(np.abs(t1 + t2 + t3)))


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    import time
    s: List[str] = []
    rng = np.random.default_rng(0)

    s.append("=== Jacobi: dizey komütatöründe TEOREM ===")
    for n in (2, 3, 5, 8):
        en_buyuk = 0.0
        for _ in range(20):
            X, Y, Z = (rng.normal(size=(n, n)) for _ in range(3))
            olcek = max(np.linalg.norm(X) * np.linalg.norm(Y)
                        * np.linalg.norm(Z), 1e-300)
            en_buyuk = max(en_buyuk, jacobi_hatasi(X, Y, Z) / olcek)
        s.append(f"  n={n}: 20 rastgele üçlüde azamî bağıl hata = "
                 f"{en_buyuk:.2e}")
    s.append("  Yani 'sayısal Jacobi onarımı' diye bir ihtiyaç yok;")
    s.append("  sıfırdan sapma varsa braket yanlış kurulmuş demektir.")

    s.append("\n=== so(3): yapı sabitleri Levi-Civita ===")
    L = so3_uretecleri()
    f = yapi_sabitleri(L)
    hata = 0.0
    for a in range(3):
        for b in range(3):
            for c in range(3):
                hata = max(hata, abs(complex(f[a, b, c]).real
                                     - _levi_civita(a, b, c)))
    s.append(f"  |f_ab^c − ε_abc| azamî = {hata:.2e}")
    s.append(f"  yapı sabiti Jacobi hatası = "
             f"{yapi_sabiti_jacobi_hatasi(f):.2e}")

    s.append("\n=== su(n): boyut n²−1 ve Jacobi ===")
    for n in (2, 3, 4):
        T = sun_uretecleri(n)
        f = yapi_sabitleri(T)
        s.append(f"  su({n}): {len(T)} üreteç (beklenen {n*n-1})"
                 f"   Jacobi hatası = {yapi_sabiti_jacobi_hatasi(f):.2e}")

    s.append("\n  Keyfî f Jacobi'yi SAĞLAMAZ (kısıt olduğunun şahidi):")
    keyfi = rng.normal(size=(3, 3, 3))
    s.append(f"    rastgele f: Jacobi hatası = "
             f"{yapi_sabiti_jacobi_hatasi(keyfi):.4f}")

    s.append("\n=== Üstel harita: özayrışım v seri ===")
    for olcek in (0.1, 1.0, 5.0, 20.0):
        A = so_izdusumu(rng.normal(size=(5, 5))) * olcek
        E1 = uslu_harita(A, "ozayrisim")
        E2 = uslu_harita(A, "seri")
        s.append(f"  ‖A‖={np.linalg.norm(A):6.2f}: "
                 f"özayrışım SO(5)'te mi? {so_n_mi(E1)}"
                 f"   seri SO(5)'te mi? {so_n_mi(E2)}"
                 f"   fark={np.max(np.abs(E1-E2)):.2e}")
    s.append("  Seri, norm büyüdükçe hem yavaşlıyor hem gruptan çıkıyor;")
    s.append("  özayrışım her ölçekte TAM ve grupta kalıyor.")

    s.append("\n=== Gruptan çıkmama: naif adım v üstel adım ===")
    X = en_yakin_dik(rng.normal(size=(4, 4)))
    if np.linalg.det(X) < 0:
        X[:, 0] *= -1
    s.append(f"  başlangıç SO(4)'te mi? {so_n_mi(X)}")
    naif, uslu = X.copy(), X.copy()
    s.append("  adım   naif ‖XᵀX−I‖   naif det    üstel ‖XᵀX−I‖   üstel det")
    for adim in range(1, 6):
        g = rng.normal(size=(4, 4))
        naif = naif - 0.1 * g
        uslu = grup_adimi(uslu, g, 0.1)
        s.append(f"  {adim:4d}   {np.max(np.abs(naif.T@naif-np.eye(4))):.3e}"
                 f"    {np.linalg.det(naif):+.4f}"
                 f"    {np.max(np.abs(uslu.T@uslu-np.eye(4))):.3e}"
                 f"      {np.linalg.det(uslu):+.6f}")
    s.append("  Naif adım grubu terk ediyor; üstel adım makine")
    s.append("  hassasiyetinde içinde kalıyor.")

    s.append("\n=== K28: geri getirme kutup ayrışımıyla ===")
    Q = en_yakin_dik(rng.normal(size=(5, 5)))
    bozuk = Q + 0.08 * rng.normal(size=(5, 5))
    sim = (bozuk + bozuk.T) / 2
    kutup = en_yakin_dik(bozuk)
    s.append(f"  bozuk    ‖XᵀX−I‖ = {np.max(np.abs(bozuk.T@bozuk-np.eye(5))):.4f}")
    s.append(f"  simetrik ‖XᵀX−I‖ = {np.max(np.abs(sim.T@sim-np.eye(5))):.4f}"
             "   ← simetrikleştirme dikliği getirmiyor")
    s.append(f"  kutup    ‖XᵀX−I‖ = {np.max(np.abs(kutup.T@kutup-np.eye(5))):.2e}"
             "   ← tam dik")
    # En iyilik: rastgele başka dik dizeyler daha yakın olamaz
    d_kutup = np.linalg.norm(kutup - bozuk, "fro")
    daha_iyi = 0
    for _ in range(300):
        R = en_yakin_dik(rng.normal(size=(5, 5)))
        if np.linalg.norm(R - bozuk, "fro") < d_kutup - 1e-12:
            daha_iyi += 1
    s.append(f"  300 rastgele dik dizeyin {daha_iyi}'i daha yakın"
             f"  (kutup mesafesi {d_kutup:.4f})")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
