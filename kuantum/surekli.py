"""Sürekli değişkenli (CV) fotonik operatörler — kesilmiş Fock uzayında.

Kaynak: ``docs/kaynak/kuantum_kapi_kulliyati.tex`` §"Sürekli Değişkenli
(CV) Optik Fotonik Operatörleri".

.. math::

   [\\hat a, \\hat a^\\dagger] = I, \\quad
   \\hat x = \\sqrt{\\hbar/2}\\,(\\hat a + \\hat a^\\dagger), \\quad
   \\hat p = -i\\sqrt{\\hbar/2}\\,(\\hat a - \\hat a^\\dagger)

**Bu uzay sonsuz boyutludur; bilgisayarda değildir.**  Her şey ``N``
boyutlu bir kesmede yapılır ve kesmenin bedeli burada *gizlenmez,
ölçülür*:

* ``[a, a†] = I`` kesmede **sağlanmaz**.  Sapma yalnız son köşegen
  girdisindedir ve ölçülen değeri ``−N``dir (``a``nın son satırı
  sıfır olduğu için ``0 − (N−1) − 1``).  Yuvarlama değil **yapısal**
  bir sapmadır.
* Buna rağmen ``D(α)``, ``S(z)``, ``BS(θ,φ)`` kesmede **tam
  üniterdir**: üreteçleri ters-Hermityendir ve ters-Hermityen bir
  dizeyin üsteli her boyutta üniter çıkar (ölçüldü: ``‖U†U−I‖`` her
  ``N``de ~1e-15).  *Yanlış yazmıştım; ölçüm düzeltti.*  Kesmenin
  bedeli üniterliği bozmak değil, **başka bir operatör** vermektir.
* O bedel :func:`kesme_hatasi` ile iki kesme kıyaslanarak ölçülür ve
  kapıya göre çok değişir.  Sıkıştırmada ``N``, ``r`` ile hızla
  büyümek zorundadır (ölçülen: ``r=0.5``te ``N=80`` yeter, ``r=1.5``te
  ``N=320`` gerekir, ``r=2.0``de ``N=320`` bile yetmez).
* Kerr kapısı ``K(κ) = exp(iκ n̂²)`` ve kesirsel Fourier ``F^a``
  **köşegendir**: kesmeden hiç etkilenmezler.  Kesme hatası
  operatörün *biçimine* bağlıdır, tek bir sayıya değil.

Ölçüm ölçütü olarak her yerde, düşük foton sayılı alt blokta
(``n < N/2``) hata verilir: fiziksel olarak anlamlı olan orasıdır.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

import numpy as np

__all__ = [
    "yok_et", "yarat", "sayi", "konum", "momentum",
    "yer_degistirme", "sikistirma", "isik_bolucu", "kerr", "kubik_faz",
    "kesirsel_fourier", "tutarli_durum", "vakum", "fock",
    "foton_dagilimi", "kuadratur_belirsizligi",
    "komutator_sapmasi", "uniterlik_sapmasi", "kesme_hatasi",
]

HBAR = 1.0


def expm(A: np.ndarray) -> np.ndarray:
    """``exp(A)`` — buradaki bütün üreteçler **ters-Hermityen** olduğu için
    ``A = −iH`` ile ``H`` Hermityen alınıp özayrışımla hesaplanır.

    Bu, seriye göre hem tam hem hızlıdır ve sonucu **kesin üniter**
    kılar (bkz. ``akis.lie``da ölçülen seri/özayrışım farkı).
    Ters-Hermityen olmayan bir girdi burada kabul EDİLMEZ: sessizce
    yanlış sonuç vermektense hata atmak yeğdir.
    """
    A = np.asarray(A, complex)
    H = 1j * A
    sapma = float(np.abs(H - H.conj().T).max())
    if sapma > 1e-9 * max(1.0, float(np.abs(H).max())):
        raise ValueError("üreteç ters-Hermityen değil (sapma %.3e)" % sapma)
    H = 0.5 * (H + H.conj().T)
    lam, V = np.linalg.eigh(H)
    return (V * np.exp(-1j * lam)) @ V.conj().T


# ══════════════════════════════════════════════════════════════════════
#  1. Temel operatörler
# ══════════════════════════════════════════════════════════════════════

def yok_et(N: int) -> np.ndarray:
    """``â``: ``a|n⟩ = √n |n−1⟩`` — üst köşegen."""
    return np.diag(np.sqrt(np.arange(1, N)), 1).astype(complex)


def yarat(N: int) -> np.ndarray:
    """``â†`` — ``yok_et``in eşleniği."""
    return yok_et(N).conj().T


def sayi(N: int) -> np.ndarray:
    """``n̂ = â†â = diag(0,1,…,N−1)`` — kesmede **tam**."""
    return np.diag(np.arange(N)).astype(complex)


def konum(N: int, hbar: float = HBAR) -> np.ndarray:
    a = yok_et(N)
    return math.sqrt(hbar / 2.0) * (a + a.conj().T)


def momentum(N: int, hbar: float = HBAR) -> np.ndarray:
    a = yok_et(N)
    return -1j * math.sqrt(hbar / 2.0) * (a - a.conj().T)


def komutator_sapmasi(N: int) -> Dict[str, object]:
    """``[a,a†] − I`` kesmede sıfır DEĞİLDİR — nerede ve ne kadar.

    Tam uzayda ``[a,a†] = I``.  Kesmede ``a†``nin son satırı yok
    edildiği için son köşegen girdi ``−N`` olur (``a``nın son satırı
    sıfır: ``0 − (N−1) − 1``); başka her yerde sapma makine
    hassasiyetindedir.
    """
    a = yok_et(N)
    C = a @ a.conj().T - a.conj().T @ a - np.eye(N)
    return {
        "boyut": N,
        "alt_blok_azamî_sapma": float(np.abs(C[:N - 1, :N - 1]).max()),
        "son_köşegen": complex(C[N - 1, N - 1]),
        "beklenen_son_köşegen": complex(-N),
        "not": "kesme hatası son satırda toplanır; alt blok temizdir",
    }


# ══════════════════════════════════════════════════════════════════════
#  2. Gauss kapıları
# ══════════════════════════════════════════════════════════════════════

def yer_degistirme(alpha: complex, N: int) -> np.ndarray:
    """``D(α) = exp(α â† − α* â)``.

    Heisenberg'de ``D†(α) â D(α) = â + α I``.
    """
    a = yok_et(N)
    return expm(alpha * a.conj().T - np.conj(alpha) * a)


def sikistirma(z: complex, N: int) -> np.ndarray:
    """``S(z) = exp(½(z* â² − z â†²))``, ``z = r e^{iφ}``.

    ``φ = 0`` için ``S†(r) x̂ S(r) = e^{−r} x̂``.
    """
    a = yok_et(N)
    return expm(0.5 * (np.conj(z) * (a @ a)
                       - z * (a.conj().T @ a.conj().T)))


def isik_bolucu(theta: float, phi: float, N: int) -> np.ndarray:
    """``BS(θ,φ) = exp(θ(e^{iφ} â₁†â₂ − e^{−iφ} â₁â₂†))`` — iki kip.

    Heisenberg'de çıkış kipleri

    .. math::

       \\begin{pmatrix}\\cos θ & -e^{-iφ}\\sin θ\\\\
       e^{iφ}\\sin θ & \\cos θ\\end{pmatrix}

    dizeyiyle karışır; toplam foton sayısı **korunur** (üreteç
    ``n̂₁+n̂₂`` ile sıfır komutatörlüdür).
    """
    a = yok_et(N)
    I = np.eye(N, dtype=complex)
    a1, a2 = np.kron(a, I), np.kron(I, a)
    G = (np.exp(1j * phi) * (a1.conj().T @ a2)
         - np.exp(-1j * phi) * (a1 @ a2.conj().T))
    return expm(theta * G)


def kesirsel_fourier(a_kuvvet: float, N: int) -> np.ndarray:
    """``F^a = exp(−i a (π/2)(n̂ + ½))`` — köşegen, kesmeden etkilenmez.

    Grup özelliği ``F^a F^b = F^{a+b}`` **tam** sağlanır (köşegen
    olduğu için).  ``a = 1``de ``F† x̂ F = p̂`` çıkar: alışıldık
    Fourier dönüşümü.
    """
    n = np.arange(N)
    return np.diag(np.exp(-1j * a_kuvvet * (math.pi / 2) * (n + 0.5)))


# ══════════════════════════════════════════════════════════════════════
#  3. Gauss olmayan kapılar
# ══════════════════════════════════════════════════════════════════════

def kerr(kappa: float, N: int) -> np.ndarray:
    """``K(κ) = exp(i κ n̂²)`` — köşegen; kesmede **tam üniter**."""
    n = np.arange(N)
    return np.diag(np.exp(1j * kappa * n * n))


def kubik_faz(gamma: float, N: int, hbar: float = HBAR) -> np.ndarray:
    """``V(γ) = exp(i γ x̂³ / (3ħ))`` — evrensellik için gereken kapı.

    Kesilmiş ``x̂`` Hermityen olduğundan ``V`` her ``N``de üniterdir.
    Yakınsaması ``γ``ya bağlıdır (ölçüldü, ilk 6×6 blokta):
    ``γ=0.1``de ``N=40`` ile 8e-16, ``γ=0.5``te ``N=80`` ile 1e-11,
    ``γ=2.0``de ``N=160`` ile ancak 6e-02.  Yani küçük ``γ`` ucuz,
    büyük ``γ`` pahalıdır -- ``x̂³`` yüksek Fock bileşenlerini güçlü
    karıştırır.
    """
    x = konum(N, hbar)
    return expm(1j * gamma / (3.0 * hbar) * (x @ x @ x))


# ══════════════════════════════════════════════════════════════════════
#  4. Durumlar ve ölçümler
# ══════════════════════════════════════════════════════════════════════

def vakum(N: int) -> np.ndarray:
    v = np.zeros(N, dtype=complex)
    v[0] = 1.0
    return v


def fock(n: int, N: int) -> np.ndarray:
    v = np.zeros(N, dtype=complex)
    v[n] = 1.0
    return v


def tutarli_durum(alpha: complex, N: int) -> np.ndarray:
    """``|α⟩ = e^{−|α|²/2} Σ αⁿ/√n! |n⟩`` — kapalı biçim.

    ``D(α)|0⟩`` ile kıyaslamak, ``D``nin kesme hatasının bağımsız bir
    ölçüsüdür: iki yol aynı duruma varmalı.
    """
    n = np.arange(N)
    # log-uzayda: |α|^n / √(n!) taşma yapmasın
    log_c = n * np.log(abs(alpha) + 1e-300) - 0.5 * _log_faktoriyel(n)
    faz = np.exp(1j * np.angle(alpha) * n)
    v = np.exp(log_c - abs(alpha) ** 2 / 2.0) * faz
    if abs(alpha) == 0:
        v = vakum(N)
    return v.astype(complex)


def _log_faktoriyel(n: np.ndarray) -> np.ndarray:
    return np.array([math.lgamma(float(k) + 1.0) for k in n])


def foton_dagilimi(psi: np.ndarray) -> np.ndarray:
    return np.abs(psi) ** 2


def kuadratur_belirsizligi(psi: np.ndarray, hbar: float = HBAR
                           ) -> Dict[str, float]:
    """``Δx``, ``Δp`` ve çarpımları — Heisenberg ``ΔxΔp ≥ ħ/2``."""
    N = len(psi)
    x, p = konum(N, hbar), momentum(N, hbar)

    def mom(A):
        o1 = complex(psi.conj() @ (A @ psi)).real
        o2 = complex(psi.conj() @ (A @ A @ psi)).real
        return math.sqrt(max(o2 - o1 * o1, 0.0))

    dx, dp = mom(x), mom(p)
    return {"Δx": dx, "Δp": dp, "çarpım": dx * dp,
            "alt_sınır": hbar / 2.0, "sağlanıyor": dx * dp >= hbar / 2 - 1e-9}


# ══════════════════════════════════════════════════════════════════════
#  5. Kesme bedelinin ölçülmesi
# ══════════════════════════════════════════════════════════════════════

def uniterlik_sapmasi(U: np.ndarray, alt: Optional[int] = None) -> float:
    """``‖U†U − I‖_∞`` — istenirse yalnız alt blokta."""
    V = U if alt is None else U[:alt, :alt]
    W = U.conj().T @ U
    W = W if alt is None else W[:alt, :alt]
    return float(np.abs(W - np.eye(W.shape[0])).max())


def kesme_hatasi(uret, N: int, kat: int = 2, alt: Optional[int] = None
                 ) -> Dict[str, float]:
    """``uret(N)`` ile ``uret(kat·N)``ı düşük Fock bloğunda kıyasla.

    Tam operatörü bilmediğimiz hâlde kesmenin yakınsayıp
    yakınsamadığını söyleyen dürüst ölçüt budur.
    """
    k = alt if alt is not None else N // 2
    A = np.asarray(uret(N))[:k, :k]
    B = np.asarray(uret(kat * N))[:k, :k]
    return {
        "alt_blok": k, "N": N, "büyük_N": kat * N,
        "azamî_fark": float(np.abs(A - B).max()),
        "bağıl_fark": float(np.abs(A - B).max()
                            / max(np.abs(B).max(), 1e-300)),
    }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s = []
    s.append("=== [a,a†] = I kesmede SAĞLANMAZ ===")
    for N in (8, 16, 64):
        r = komutator_sapmasi(N)
        s.append("  N=%3d  alt blok sapma=%.2e   son köşegen=%+.1f "
                 "(beklenen %+.1f)"
                 % (N, r["alt_blok_azamî_sapma"], r["son_köşegen"].real,
                    r["beklenen_son_köşegen"].real))
    s.append("  Kesme hatası son satırda toplanıyor; hüküm hep")
    s.append("  düşük foton bloğunda veriliyor.")

    s.append("\n=== D(α)|0⟩ kapalı tutarlı durumla uyuşuyor mu? ===")
    N = 60
    for al in (0.5, 1.0, 2.0, 4.0):
        psi = yer_degistirme(al, N) @ vakum(N)
        fark = float(np.abs(psi - tutarli_durum(al, N)).max())
        pd = foton_dagilimi(psi)
        s.append("  α=%.1f  azamî fark=%.2e   ⟨n⟩=%.4f (|α|²=%.4f)"
                 % (al, fark, float(pd @ np.arange(N)), al * al))
    s.append("  Foton sayısı Poisson: ⟨n⟩ = |α|², iki yol da aynı yere varıyor.")

    s.append("\n=== Üniterlik kesmede BOZULMUYOR (yanlış yazmıştım) ===")
    for N in (20, 40, 80):
        U = yer_degistirme(3.0, N)
        s.append("  α=3, N=%3d  ‖U†U−I‖=%.2e" % (N, uniterlik_sapmasi(U)))
    s.append("  Üreteç ters-Hermityen olduğundan üsteli her boyutta")
    s.append("  üniterdir. Kesmenin bedeli üniterlik değil, operatörün")
    s.append("  kendisidir; o da aşağıda iki kesme kıyaslanarak ölçülüyor.")

    s.append("\n=== Sıkıştırma: S†(r) x̂ S(r) = e^{−r} x̂ ===")
    k = 12
    s.append("  (bağıl hata, ilk %d×%d blokta; N yeterli değilse BOZULUR)" % (k, k))
    s.append("  r      N=40      N=80     N=160     N=320   Δx(N=320)  e^{−r}/√2")
    for r in (0.5, 1.0, 1.5, 2.0):
        hat = []
        for N in (40, 80, 160, 320):
            S = sikistirma(r, N)
            sol = (S.conj().T @ konum(N) @ S)[:k, :k]
            sag = (math.exp(-r) * konum(N))[:k, :k]
            hat.append(float(np.abs(sol - sag).max() / np.abs(sag).max()))
        b = kuadratur_belirsizligi(sikistirma(r, 320) @ vakum(320))
        s.append("  %.1f  %8.1e  %8.1e  %8.1e  %8.1e   %.6f   %.6f"
                 % (r, hat[0], hat[1], hat[2], hat[3], b["Δx"],
                    math.exp(-r) / math.sqrt(2)))
    s.append("  Gereken N, r ile hızla büyüyor: r=0.5'te 80 yeter,")
    s.append("  r=1.5'te 320 gerekir, r=2.0'de 320 bile yetmez.")
    b = kuadratur_belirsizligi(sikistirma(1.0, 320) @ vakum(320))
    s.append("  Sıkıştırma belirsizlik ÇARPIMINI değiştirmiyor:")
    s.append("  r=1.0, N=320: ΔxΔp=%.6f (alt sınır ħ/2=%.6f)"
             % (b["çarpım"], b["alt_sınır"]))

    s.append("\n=== Işık bölücü: foton sayısı korunuyor ===")
    N = 12
    a = yok_et(N)
    I = np.eye(N, dtype=complex)
    Ntop = np.kron(a.conj().T @ a, I) + np.kron(I, a.conj().T @ a)
    for th in (0.3, math.pi / 4, 1.2):
        B = isik_bolucu(th, 0.4, N)
        # tek foton her iki kipte: |1,0⟩
        psi = np.kron(fock(1, N), fock(0, N))
        out = B @ psi
        n_once = complex(psi.conj() @ (Ntop @ psi)).real
        n_sonra = complex(out.conj() @ (Ntop @ out)).real
        p2 = abs(out[np.ravel_multi_index((0, 1), (N, N))]) ** 2
        s.append("  θ=%.3f  ⟨n⟩ %.6f → %.6f   |⟨0,1|out⟩|²=%.6f "
                 "(sin²θ=%.6f)"
                 % (th, n_once, n_sonra, p2, math.sin(th) ** 2))

    s.append("\n=== Kerr KÖŞEGEN: kesme hatası YOK ===")
    for N in (8, 32, 128):
        s.append("  N=%3d  ‖K†K−I‖=%.2e" % (N, uniterlik_sapmasi(kerr(0.7, N))))
    s.append("  Kesme hatası operatörün BİÇİMİNE bağlı, tek bir sayıya değil.")

    s.append("\n=== Kübik faz: yakınsama γ'ya bağlı (ölçülerek) ===")
    s.append("  γ      N=20→40   N=40→80  N=80→160   (ilk 6×6 blok)")
    for g in (0.1, 0.5, 2.0):
        h = [kesme_hatasi(lambda n, g=g: kubik_faz(g, n), N, alt=6)["azamî_fark"]
             for N in (20, 40, 80)]
        s.append("  %.1f  %8.1e  %8.1e  %8.1e" % (g, h[0], h[1], h[2]))
    s.append("  Küçük γ ucuz, büyük γ pahalı: γ=2'de N=160 bile yetmiyor.")
    s.append("  Kıyas için D(1.0) aynı ölçütle:")
    h = [kesme_hatasi(lambda n: yer_degistirme(1.0, n), N, alt=6)["azamî_fark"]
         for N in (20, 40, 80)]
    s.append("       %8.1e  %8.1e  %8.1e" % (h[0], h[1], h[2]))

    s.append("\n=== Kesirsel Fourier: grup özelliği TAM ===")
    N = 64
    for a1, b1 in ((0.3, 0.7), (1.0, 1.0), (2.5, -0.5)):
        L = kesirsel_fourier(a1, N) @ kesirsel_fourier(b1, N)
        R = kesirsel_fourier(a1 + b1, N)
        s.append("  F^%.1f F^%.1f vs F^%.1f : azamî fark=%.2e"
                 % (a1, b1, a1 + b1, float(np.abs(L - R).max())))
    F = kesirsel_fourier(1.0, N)
    k = 32
    sol = (F.conj().T @ konum(N) @ F)[:k, :k]
    s.append("  a=1'de F† x̂ F = p̂ mi? azamî fark=%.2e"
             % float(np.abs(sol - momentum(N)[:k, :k]).max()))
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
