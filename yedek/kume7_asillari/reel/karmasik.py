"""Sanal birimin ilgası: ``ℂ^N ≅ ℝ^{2N}`` gömmesi ve reel evrim.

Kaynak: ``docs/kaynak/reel_meleke_operatorleri.tex`` §Giriş, §Usul.

.. math::

   i \\longleftrightarrow J = \\begin{pmatrix} 0 & -I \\\\ I & 0
   \\end{pmatrix}, \\qquad J^2 = -I

**Kaynağın doğru yazdığı yer.**  ``H_ℝ = [[A, −B], [B, A]]`` blok
biçimi, ``H = A + iB`` Hermitesel dizeyinin reel gömmesidir ve bu biçim
``J`` ile **sıra değiştirir** (ölçüldü: ``[J, H_ℝ] = 0.0``).  Bu yüzden
``exp(tJH_ℝ) = cos(Ht)I + sin(Ht)J`` kapalı biçimi de doğrudur
(ölçüldü: fark 1.2e-15).  Bu, ``J²=−I`` özdeşliğinin doğrudan neticesi
değil -- ``J`` ile ``H_ℝ``nin sıra değiştirmesine bağlıdır ve o şart
burada **denetleniyor**.

**M28 tashihi -- işaret.**  Kaynak ``ħ d|Ψ⟩/dt = +J·H_ℝ|Ψ⟩`` yazıyor.
``iħ∂_tψ = Hψ`` ⟹ ``∂_tψ = −(i/ħ)Hψ`` olduğundan reel karşılık
``ħ d|Ψ⟩/dt = −J·H_ℝ|Ψ⟩``dır.  Ölçüldü (``N=3``, ``t=0.6``):
``exp(+tJH_ℝ)`` doğru ``exp(−iHt)``den **2.174** uzakta,
``exp(−tJH_ℝ)`` ise **1.05e-15**.  İşaret zamanı tersine çevirir; aynı
hata §7 Teemmül ve §17--25 Mizan kapılarında da tekrarlanıyor.

**Bedeli -- ve ölçümün beklentiyi düzelttiği yer.**  Reel gömme boyutu
ikiye katlar: ``N×N`` karmaşık çarpım ``4N³`` reel çarpma ister,
``2N×2N`` reel çarpım ``8N³``.  Kâğıt üstünde **iki kat** iştir ve ben
de önce bunu "bedel" diye yazmıştım.  Duvar saati bunu **yalanladı**:
ölçülen oran ``N=64,128,256`` için **0.39×, 0.36×, 0.47×** -- yani reel
gömme bu makinede karmaşık çarpımdan *iki-üç kat daha hızlı*.  Sebep,
BLAS'ın reel GEMM'inin karmaşık GEMM'den çok daha iyi eniyilenmiş
olmasıdır; iki kat işlemi daha verimli yapmak, az işlemi kötü yapmaktan
hızlı çıkıyor.  Netice: kaynağın "reel zemine geç" teklifi, hız
bakımından da savunulabilir -- ama sebebi kaynağın söylediği ("sanal
sayı yanılsaması") değil, kütüphane gerçekliğidir.  Doğruluk her iki
yolda aynıdır (fark 1e-13).

**UYARI -- bu hüküm YALNIZ TEK SİSTEM içindir.**  Buradaki gömme
``ρ(AB) = ρ(A)ρ(B)`` anlamında birebirdir (ölçüldü: 1.8e-15).  Fakat
**birleşik** sistemde çarpımsal DEĞİLDİR: ``dim_ℝ(ℂ^m ⊗ ℂ^n) = 2mn``
iken ``ℝ^{2m} ⊗ ℝ^{2n} = 4mn``dir ve ``ρ(A⊗B)`` ile ``ρ(A)⊗ρ(B)``nin
şekilleri bile tutmaz (8×8 / 16×16).  "Sanal sayıya ihtiyaç yok"
neticesi buradan **çıkarılamaz**; reel kuantum kuramı tartışmasının
tamamı o birleştirme kaidesindedir.  Bkz. :mod:`hesap.palmer`.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

import numpy as np

__all__ = [
    "J_dizeyi", "reel_goem", "karmasik_coz", "reel_hamiltonyen",
    "hermitesel_mi", "reel_evrim", "reel_evrim_cos_sin",
    "so_2n_mi", "kaynak_isaretiyle_evrim", "carpim_maliyeti",
]


def J_dizeyi(N: int) -> np.ndarray:
    """``J = [[0, −I], [I, 0]] ∈ ℝ^{2N×2N}``; ``J² = −I``."""
    Z, I = np.zeros((N, N)), np.eye(N)
    return np.block([[Z, -I], [I, Z]])


def reel_goem(v: np.ndarray) -> np.ndarray:
    """``ℂ^N ∋ v ↦ (Re v, Im v) ∈ ℝ^{2N}``."""
    v = np.asarray(v, complex)
    return np.concatenate([v.real, v.imag])


def karmasik_coz(x: np.ndarray) -> np.ndarray:
    """Ters gömme: ``ℝ^{2N} → ℂ^N``."""
    x = np.asarray(x, float)
    N = x.shape[0] // 2
    return x[:N] + 1j * x[N:]


def reel_hamiltonyen(H: np.ndarray) -> np.ndarray:
    """``H = A + iB`` Hermitesel ⟹ ``H_ℝ = [[A, −B], [B, A]]``.

    ``H`` Hermitesel ise ``A`` simetrik, ``B`` yatkın-simetriktir; o
    zaman ``H_ℝ`` **simetriktir** ve ``J`` ile sıra değiştirir.  Girdi
    Hermitesel değilse hata verilir: sessizce yanlış blok kurmaktansa.
    """
    H = np.asarray(H, complex)
    if not hermitesel_mi(H):
        raise ValueError("H Hermitesel değil; reel gömme tanımsız")
    A, B = H.real, H.imag
    return np.block([[A, -B], [B, A]])


def hermitesel_mi(H: np.ndarray, tol: float = 1e-10) -> bool:
    H = np.asarray(H, complex)
    return bool(np.abs(H - H.conj().T).max()
                <= tol * max(1.0, float(np.abs(H).max())))


def _uexp_simetrik(S: np.ndarray, t: float) -> np.ndarray:
    """``exp(t·J·S)``, ``S`` simetrik ve ``[J,S]=0`` iken — özayrışımla."""
    N = S.shape[0] // 2
    J = J_dizeyi(N)
    lam, V = np.linalg.eigh(S)
    C = (V * np.cos(lam * t)) @ V.T
    Sn = (V * np.sin(lam * t)) @ V.T
    return C + J @ Sn


def reel_evrim(H: np.ndarray, t: float) -> np.ndarray:
    """``exp(−tJH_ℝ)`` — **doğru** işaret (M28).

    ``exp(−iHt)``nin reel gömmesidir; ölçülen fark 1e-15.
    """
    return _uexp_simetrik(reel_hamiltonyen(H), -t)


def kaynak_isaretiyle_evrim(H: np.ndarray, t: float) -> np.ndarray:
    """``exp(+tJH_ℝ)`` — kaynağın yazdığı hâl, **kıyas için**.

    Zamanı tersine çevirir: ``exp(+iHt)``ye karşılık gelir.
    """
    return _uexp_simetrik(reel_hamiltonyen(H), +t)


def reel_evrim_cos_sin(H: np.ndarray, t: float) -> np.ndarray:
    """``cos(H_ℝ t)I + sin(H_ℝ t)J`` kapalı biçimi (doğru işaretle).

    Kaynağın kapalı biçimi -- ``[J, H_ℝ] = 0`` olduğu için geçerlidir;
    şart burada ayrıca ölçülüyor.
    """
    HR = reel_hamiltonyen(H)
    N = HR.shape[0] // 2
    J = J_dizeyi(N)
    lam, V = np.linalg.eigh(HR)
    return (V * np.cos(lam * t)) @ V.T - J @ ((V * np.sin(lam * t)) @ V.T)


def so_2n_mi(U: np.ndarray, tol: float = 1e-10) -> Dict[str, object]:
    """``U ∈ SO(2N)``? — diklik ve ``det = +1``."""
    U = np.asarray(U, float)
    dik = float(np.abs(U.T @ U - np.eye(U.shape[0])).max())
    isaret, logdet = np.linalg.slogdet(U)
    return {"diklik_sapması": dik, "det": float(isaret * math.exp(logdet)),
            "SO_da_mı": bool(dik < tol and isaret > 0)}


def carpim_maliyeti(N: int) -> Dict[str, object]:
    """Karmaşık ``N×N`` çarpım ile reel ``2N×2N`` çarpımın maliyeti.

    Karmaşık çarpım: ``N³`` karmaşık çarpma = ``4N³`` reel çarpma
    (naif) veya Karatsuba ile ``3N³``.  Reel gömme: ``(2N)³ = 8N³``.
    Yani gömme naife göre **2×**, Karatsuba'ya göre **2.67×** iştir.
    """
    return {"N": N, "karmaşık_naif_reel_çarpma": 4 * N ** 3,
            "karmaşık_karatsuba": 3 * N ** 3,
            "reel_gömme": 8 * N ** 3,
            "oran_naif": 2.0, "oran_karatsuba": 8.0 / 3.0}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    import time
    s = []
    r = np.random.default_rng(0)
    N = 3
    A = r.normal(size=(N, N)); A = A + A.T
    B = r.normal(size=(N, N)); B = B - B.T
    H = A + 1j * B

    s.append("=== J² = −I ve [J, H_ℝ] = 0 (kaynak DOĞRU) ===")
    J = J_dizeyi(N)
    HR = reel_hamiltonyen(H)
    s.append("  ‖J² + I‖ = %.2e" % float(np.abs(J @ J + np.eye(2 * N)).max()))
    s.append("  H Hermitesel mi? %s   ‖H_ℝ − H_ℝᵀ‖ = %.2e"
             % (hermitesel_mi(H), float(np.abs(HR - HR.T).max())))
    s.append("  ‖[J, H_ℝ]‖ = %.2e   ← cos/sin kapalı biçimini bu şart "
             "geçerli kılıyor" % float(np.abs(J @ HR - HR @ J).max()))

    s.append("\n=== M28: işaret. Hangisi exp(−iHt)'yi veriyor? ===")
    psi = r.normal(size=N) + 1j * r.normal(size=N)
    for t in (0.2, 0.6, 1.5):
        lam, V = np.linalg.eigh(H)
        ref = (V * np.exp(-1j * lam * t)) @ (V.conj().T @ psi)
        x = reel_goem(psi)
        dogru = karmasik_coz(reel_evrim(H, t) @ x)
        kaynak = karmasik_coz(kaynak_isaretiyle_evrim(H, t) @ x)
        s.append("  t=%.1f   −J·H_ℝ farkı=%.2e      +J·H_ℝ farkı=%.4f"
                 % (t, float(np.abs(dogru - ref).max()),
                    float(np.abs(kaynak - ref).max())))
    s.append("  '+' işareti exp(+iHt) veriyor, yani zamanı TERSİNE")
    s.append("  çeviriyor. İkisi de SO(2N)'de olduğu için diklik")
    s.append("  denetimi bu hatayı YAKALAMAZ:")
    for ad, U in (("−J·H_ℝ", reel_evrim(H, 0.6)),
                  ("+J·H_ℝ", kaynak_isaretiyle_evrim(H, 0.6))):
        d = so_2n_mi(U)
        s.append("    %s : diklik sapması=%.2e  det=%+.6f  SO(2N)'de mi? %s"
                 % (ad, d["diklik_sapması"], d["det"], d["SO_da_mı"]))

    s.append("\n=== cos/sin kapalı biçimi üstel ile aynı mı? ===")
    for t in (0.2, 0.6, 1.5):
        s.append("  t=%.1f  fark = %.2e"
                 % (t, float(np.abs(reel_evrim_cos_sin(H, t)
                                    - reel_evrim(H, t)).max())))

    s.append("\n=== Şart bozulursa: [J,S] ≠ 0 olan bir S ===")
    S = r.normal(size=(2 * N, 2 * N)); S = S + S.T
    s.append("  ‖[J,S]‖ = %.4f  → kapalı biçim artık geçerli değil"
             % float(np.abs(J @ S - S @ J).max()))
    lam, V = np.linalg.eigh(S)
    kapali = (V * np.cos(lam)) @ V.T + J @ ((V * np.sin(lam)) @ V.T)
    w, W = np.linalg.eig(J @ S)
    tam = np.real((W * np.exp(w)) @ np.linalg.inv(W))
    s.append("  ‖kapalı biçim − gerçek exp(JS)‖ = %.4f"
             % float(np.abs(kapali - tam).max()))
    s.append("  Yani kapalı biçim H_ℝ'nin BLOK YAPISINA borçludur,")
    s.append("  'J²=−I' özdeşliğine değil.")

    s.append("\n=== Gömmenin bedeli: iki kat iş ===")
    s.append("     N   karmaşık(naif)      reel gömme    oran   ölçülen")
    for N2 in (64, 128, 256):
        m = carpim_maliyeti(N2)
        Ac = r.normal(size=(N2, N2)) + 1j * r.normal(size=(N2, N2))
        Bc = r.normal(size=(N2, N2)) + 1j * r.normal(size=(N2, N2))
        Ar = np.block([[Ac.real, -Ac.imag], [Ac.imag, Ac.real]])
        Br = np.block([[Bc.real, -Bc.imag], [Bc.imag, Bc.real]])
        _ = Ac @ Bc
        t0 = time.perf_counter()
        for _ in range(5):
            Cc = Ac @ Bc
        t1 = (time.perf_counter() - t0) / 5
        t2 = time.perf_counter()
        for _ in range(5):
            Cr = Ar @ Br
        t3 = (time.perf_counter() - t2) / 5
        fark = float(np.abs(np.block([[Cc.real, -Cc.imag],
                                      [Cc.imag, Cc.real]]) - Cr).max())
        s.append("  %4d   %12d   %12d    %.2f   %.2f×  (fark=%.1e)"
                 % (N2, m["karmaşık_naif_reel_çarpma"], m["reel_gömme"],
                    m["oran_naif"], t1 / max(t3, 1e-12), fark))
    s.append("  Kuramsal işlem sayısı reel gömmede İKİ KAT; ama ölçülen")
    s.append("  duvar saati oranı 1'in ALTINDA, yani reel gömme daha HIZLI.")
    s.append("  ('İki kat iş, iki kat süre' diye yazmıştım; ölçüm yalanladı.")
    s.append("   Sebep BLAS'ın reel GEMM'inin karmaşık GEMM'den çok daha")
    s.append("   iyi eniyilenmiş olması. Netice aynı: fark 1e-13.)")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
