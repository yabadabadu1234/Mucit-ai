
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
    A = np.asarray(A, complex)
    H = 1j * A
    sapma = float(np.abs(H - H.conj().T).max())
    if sapma > 1e-9 * max(1.0, float(np.abs(H).max())):
        raise ValueError("üreteç ters-Hermityen değil (sapma %.3e)" % sapma)
    H = 0.5 * (H + H.conj().T)
    lam, V = np.linalg.eigh(H)
    return (V * np.exp(-1j * lam)) @ V.conj().T


def yok_et(N: int) -> np.ndarray:
    return np.diag(np.sqrt(np.arange(1, N)), 1).astype(complex)


def yarat(N: int) -> np.ndarray:
    return yok_et(N).conj().T


def sayi(N: int) -> np.ndarray:
    return np.diag(np.arange(N)).astype(complex)


def konum(N: int, hbar: float = HBAR) -> np.ndarray:
    a = yok_et(N)
    return math.sqrt(hbar / 2.0) * (a + a.conj().T)


def momentum(N: int, hbar: float = HBAR) -> np.ndarray:
    a = yok_et(N)
    return -1j * math.sqrt(hbar / 2.0) * (a - a.conj().T)


def komutator_sapmasi(N: int) -> Dict[str, object]:
    a = yok_et(N)
    C = a @ a.conj().T - a.conj().T @ a - np.eye(N)
    return {
        "boyut": N,
        "alt_blok_azamî_sapma": float(np.abs(C[:N - 1, :N - 1]).max()),
        "son_köşegen": complex(C[N - 1, N - 1]),
        "beklenen_son_köşegen": complex(-N),
        "not": "kesme hatası son satırda toplanır; alt blok temizdir",
    }


def yer_degistirme(alpha: complex, N: int) -> np.ndarray:
    a = yok_et(N)
    return expm(alpha * a.conj().T - np.conj(alpha) * a)


def sikistirma(z: complex, N: int) -> np.ndarray:
    a = yok_et(N)
    return expm(0.5 * (np.conj(z) * (a @ a)
                       - z * (a.conj().T @ a.conj().T)))


def isik_bolucu(theta: float, phi: float, N: int) -> np.ndarray:
    a = yok_et(N)
    I = np.eye(N, dtype=complex)
    a1, a2 = np.kron(a, I), np.kron(I, a)
    G = (np.exp(1j * phi) * (a1.conj().T @ a2)
         - np.exp(-1j * phi) * (a1 @ a2.conj().T))
    return expm(theta * G)


def kesirsel_fourier(a_kuvvet: float, N: int) -> np.ndarray:
    n = np.arange(N)
    return np.diag(np.exp(-1j * a_kuvvet * (math.pi / 2) * (n + 0.5)))


def kerr(kappa: float, N: int) -> np.ndarray:
    n = np.arange(N)
    return np.diag(np.exp(1j * kappa * n * n))


def kubik_faz(gamma: float, N: int, hbar: float = HBAR) -> np.ndarray:
    x = konum(N, hbar)
    return expm(1j * gamma / (3.0 * hbar) * (x @ x @ x))


def vakum(N: int) -> np.ndarray:
    v = np.zeros(N, dtype=complex)
    v[0] = 1.0
    return v


def fock(n: int, N: int) -> np.ndarray:
    v = np.zeros(N, dtype=complex)
    v[n] = 1.0
    return v


def tutarli_durum(alpha: complex, N: int) -> np.ndarray:
    n = np.arange(N)
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
    N = len(psi)
    x, p = konum(N, hbar), momentum(N, hbar)

    def mom(A):
        o1 = complex(psi.conj() @ (A @ psi)).real
        o2 = complex(psi.conj() @ (A @ A @ psi)).real
        return math.sqrt(max(o2 - o1 * o1, 0.0))

    dx, dp = mom(x), mom(p)
    return {"Δx": dx, "Δp": dp, "çarpım": dx * dp,
            "alt_sınır": hbar / 2.0, "sağlanıyor": dx * dp >= hbar / 2 - 1e-9}


def uniterlik_sapmasi(U: np.ndarray, alt: Optional[int] = None) -> float:
    V = U if alt is None else U[:alt, :alt]
    W = U.conj().T @ U
    W = W if alt is None else W[:alt, :alt]
    return float(np.abs(W - np.eye(W.shape[0])).max())


def kesme_hatasi(uret, N: int, kat: int = 2, alt: Optional[int] = None
                 ) -> Dict[str, float]:
    k = alt if alt is not None else N // 2
    A = np.asarray(uret(N))[:k, :k]
    B = np.asarray(uret(kat * N))[:k, :k]
    return {
        "alt_blok": k, "N": N, "büyük_N": kat * N,
        "azamî_fark": float(np.abs(A - B).max()),
        "bağıl_fark": float(np.abs(A - B).max()
                            / max(np.abs(B).max(), 1e-300)),
    }


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


if __name__ == "__main__":
    print(_gosterim())
