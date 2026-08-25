"""Adiyabatik geçiş, QAOA ve parametre-kaydırma kuralı.

Kaynak: ``docs/kaynak/kuantum_kapi_kulliyati.tex`` §"Kuantum Annealing,
Adiabatik ve Hamiltonian Simülasyonu".

**Adiyabatik.**  ``H(t) = (1 − t/T) H_baş + (t/T) H_hedef``,
``H_baş = −Σ X_i``.  Adiyabatik kuram, ``T`` yeterince büyükse
başlangıç temel durumunun hedef temel durumuna taşındığını söyler.
"Yeterince büyük"ün alışıldık ölçüsü **asgarî tayf aralığıdır**:
``T ≳ 1/Δ_min²``.  Bu ölçüt burada olduğu gibi **kullanılamaz** ve
sebebi ölçülerek gösteriliyor: ``H₁``in temel öz-uzayı dejeneredir,
bu yüzden ``E₁(s) − E₀(s)`` ``s → 1``de sıfıra iner ve ``Δ_min``
nereden kestiğinize bağlı bir sayı olur (ölçüldü: ``s ≤ 0.95``te
4-döngüde 1e-04, ``s = 1``de tam 0).  Üstelik 4-döngünün ``Δ_min``i
``K₄``ünkinden **küçük** olduğu hâlde ``T = 128``de başarısı daha
**yüksektir** (1.0000'e karşı 0.9992).  Sebep: kapanan aralık,
hedefin dejenere temel öz-uzayının oluşmasıdır ve o alt uzayın
içinde kalmak geçişi bozmaz.  Onun için başarı, temel duruma değil
**temel alt uzaya** örtüşmeyle ölçülüyor.

**QAOA.**  ``|γ,β⟩ = U_B(β_p)U_C(γ_p)…U_B(β_1)U_C(γ_1)|+⟩^{⊗n}`` ile
``U_C(γ) = e^{−iγH_C}``, ``U_B(β) = e^{−iβΣX_i}``.  ``H_C`` köşegen
olduğundan ``U_C`` köşegen bir faz çarpımıdır: **tam dizey
kurulmaz**.  ``U_B`` çarpım hâlindedir, kubit kubit uygulanır.

**Parametre kaydırma.**

.. math::

   \\partial_{\\theta_k}\\langle H\\rangle =
   \\tfrac12\\big(\\langle H\\rangle_{\\theta_k+\\pi/2}
   - \\langle H\\rangle_{\\theta_k-\\pi/2}\\big)

Bu **tam** bir türevdir, sonlu fark yaklaşımı değil -- ama yalnız
üreteci ``G² = I`` olan kapılar için.  Burada iki şey ölçülüyor:
(1) ``R_z``, ``R_x`` gibi kapılarda sonuç makine hassasiyetinde
sonlu farkla uyuşuyor; (2) üreteci ``G² = I`` **olmayan** bir kapıda
(``e^{−iθ n̂}``, ``n̂ = diag(0,1,2)``) aynı formül **yanlış** cevap
veriyor.  Kuralın şartı süs değildir.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "kesitli_hamiltonyen", "tayf_araligi", "adiyabatik_kos",
    "maxcut_hamiltonyeni", "qaoa_durumu", "qaoa_beklenen",
    "qaoa_eniyile", "parametre_kaydirma", "kaydirma_sarti_ihlali",
]

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_I = np.eye(2, dtype=complex)


def _tensor(ops: Sequence[np.ndarray]) -> np.ndarray:
    M = ops[0]
    for o in ops[1:]:
        M = np.kron(M, o)
    return M


def _tek_kubit(P: np.ndarray, i: int, n: int) -> np.ndarray:
    return _tensor([P if k == i else _I for k in range(n)])


# ══════════════════════════════════════════════════════════════════════
#  1. Adiyabatik geçiş
# ══════════════════════════════════════════════════════════════════════

def baslangic_hamiltonyeni(n: int) -> np.ndarray:
    """``H_baş = −Σ_i X_i`` — temel durumu ``|+⟩^{⊗n}``."""
    H = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n):
        H -= _tek_kubit(_X, i, n)
    return H


def kesitli_hamiltonyen(H0: np.ndarray, H1: np.ndarray, s: float
                        ) -> np.ndarray:
    """``H(s) = (1−s) H₀ + s H₁``, ``s = t/T ∈ [0,1]``."""
    return (1.0 - s) * H0 + s * H1


def tayf_araligi(H0: np.ndarray, H1: np.ndarray, ornek: int = 201,
                 s_ust: float = 0.95) -> Dict[str, object]:
    """``Δ(s) = E₁(s) − E₀(s)`` ve ``[0, s_ust]``teki asgarîsi.

    Neden uç nokta dışarıda?  ``H₁`` (MaxCut) temel öz-uzayı Z₂
    bakışımı yüzünden **dejeneredir** -- ölçüldü: 4-döngüde 2 katlı,
    ``K₄``te 6 katlı.  Bu yüzden ``E₁(1) − E₀(1) = 0``dır ve ``s → 1``
    yaklaştıkça aralık sıfıra iner (ölçüldü: ``s=0.995``te 3e-09).
    Ama bu **zararsız** bir kapanmadır: dejenere temel öz-uzayın
    içinde kalmak adiyabatik geçişi bozmaz, başarı zaten o alt uzaya
    örtüşmeyle ölçülür.  ``E_k − E_{k−1}`` yazmak da işe yaramaz:
    ``H₀``ın tayfı da dejeneredir, o zaman aralık ``s=0``da kapanır
    (ölçüldü).  Dürüst ölçüt, kapanmanın nerede olduğunu söyleyip
    uç bölgeyi ayırmaktır.
    """
    e1s = np.linalg.eigvalsh(H1)
    kat = int(np.sum(e1s < e1s[0] + 1e-9))
    ss = np.linspace(0.0, 1.0, ornek)
    d = np.array([float(np.diff(np.linalg.eigvalsh(
        kesitli_hamiltonyen(H0, H1, float(s))))[0]) for s in ss])
    maske = ss <= s_ust
    i = int(np.argmin(np.where(maske, d, np.inf)))
    return {"s": ss, "aralık": d, "hedef_temel_katlılık": kat,
            "s_ust": s_ust, "Δ_min": float(d[i]), "s_min": float(ss[i]),
            "uç_aralık": float(d[-1]),
            "kaba_T_ölçüsü": 1.0 / max(d[i], 1e-12) ** 2}


def adiyabatik_kos(H0: np.ndarray, H1: np.ndarray, T: float,
                   adim: int = 400) -> Dict[str, object]:
    """``|ψ(T)⟩``ı ``H(t/T)`` ile taşı; hedef temel duruma örtüşme.

    Zaman dilimi başına **tam** üstel (özayrışım) kullanılır: adım
    hatası yalnız ``H``nin zamanla değişmesinden gelir, üstelden
    değil.  Böylece ölçülen şey gerçekten adiyabatik hata olur.
    """
    e0, V0 = np.linalg.eigh(H0)
    psi = V0[:, 0].astype(complex)
    dt = T / adim
    for k in range(adim):
        s = (k + 0.5) / adim
        H = kesitli_hamiltonyen(H0, H1, s)
        lam, V = np.linalg.eigh(H)
        psi = (V * np.exp(-1j * lam * dt)) @ (V.conj().T @ psi)
    e1, V1 = np.linalg.eigh(H1)
    # hedefin temel öz-uzayı dejenere olabilir: bütün alt uzaya örtüşme
    kat = int(np.sum(e1 < e1[0] + 1e-9))
    P = V1[:, :kat]
    ortusme = float(np.sum(np.abs(P.conj().T @ psi) ** 2))
    return {"T": T, "adım": adim, "başarı": ortusme,
            "temel_katlılık": kat,
            "enerji": float((psi.conj() @ (H1 @ psi)).real),
            "temel_enerji": float(e1[0])}


# ══════════════════════════════════════════════════════════════════════
#  2. QAOA
# ══════════════════════════════════════════════════════════════════════

def maxcut_hamiltonyeni(n: int, kenarlar: Sequence[Tuple[int, int]]
                        ) -> np.ndarray:
    """``H_C = Σ_{(i,j)} ½(Z_iZ_j − 1)`` — köşegen, **vektör** olarak.

    Tam dizey kurmak ``4^n`` yer ister; köşegen olduğu için ``2^n``
    uzunluğunda bir vektör yeter.  ``H_C``nin asgarîsi (en negatif)
    en büyük kesime karşılık gelir.
    """
    d = np.zeros(2 ** n)
    idx = np.arange(2 ** n)
    for i, j in kenarlar:
        zi = 1 - 2 * ((idx >> (n - 1 - i)) & 1)
        zj = 1 - 2 * ((idx >> (n - 1 - j)) & 1)
        d += 0.5 * (zi * zj - 1)
    return d


def _mixer_uygula(psi: np.ndarray, beta: float, n: int) -> np.ndarray:
    """``e^{−iβΣX_i}`` = kubit başına ``R_x(2β)`` — tam dizey YOK."""
    c, s = math.cos(beta), -1j * math.sin(beta)
    T = psi.reshape([2] * n)
    for i in range(n):
        T = np.moveaxis(T, i, 0)
        a, b = T[0].copy(), T[1].copy()
        T[0] = c * a + s * b
        T[1] = s * a + c * b
        T = np.moveaxis(T, 0, i)
    return T.reshape(-1)


def qaoa_durumu(n: int, hc: np.ndarray, gamma: Sequence[float],
                beta: Sequence[float]) -> np.ndarray:
    """``|γ,β⟩`` — ``U_C`` köşegen faz, ``U_B`` kubit kubit."""
    psi = np.full(2 ** n, 2 ** (-n / 2.0), dtype=complex)
    for g, b in zip(gamma, beta):
        psi = np.exp(-1j * g * hc) * psi
        psi = _mixer_uygula(psi, float(b), n)
    return psi


def qaoa_beklenen(n: int, hc: np.ndarray, gamma: Sequence[float],
                  beta: Sequence[float]) -> float:
    psi = qaoa_durumu(n, hc, gamma, beta)
    return float(np.sum(hc * np.abs(psi) ** 2))


def qaoa_eniyile(n: int, hc: np.ndarray, p: int, tohum: int = 0,
                 baslangic: int = 8, tur: int = 250, adim: float = 0.15
                 ) -> Dict[str, object]:
    """Çok başlangıçlı sonlu-fark inişiyle ``(γ,β)`` araması.

    QAOA'nın **iddiası**, ``p`` arttıkça oranın 1'e gitmesidir; burada
    iddia edilmiyor, ``p = 1…4`` için ölçülüyor.
    """
    r = np.random.default_rng(tohum)
    en_iyi, en_par = float("inf"), None
    for _ in range(baslangic):
        x = r.uniform(0, math.pi, size=2 * p)
        f = qaoa_beklenen(n, hc, x[:p], x[p:])
        h, t = 1e-4, adim
        for _k in range(tur):
            g = np.empty(2 * p)
            for j in range(2 * p):
                y = x.copy(); y[j] += h
                g[j] = (qaoa_beklenen(n, hc, y[:p], y[p:]) - f) / h
            nrm = np.linalg.norm(g)
            if nrm < 1e-12:
                break
            y = x - t * g / nrm
            fy = qaoa_beklenen(n, hc, y[:p], y[p:])
            if fy < f:
                x, f = y, fy
            else:
                t *= 0.5
                if t < 1e-10:
                    break
        if f < en_iyi:
            en_iyi, en_par = f, x
    en_alt = float(hc.min())
    return {"p": p, "beklenen": en_iyi, "en_iyi_mümkün": en_alt,
            "oran": en_iyi / en_alt if en_alt != 0 else float("nan"),
            "parametre": en_par}


# ══════════════════════════════════════════════════════════════════════
#  3. Parametre kaydırma
# ══════════════════════════════════════════════════════════════════════

def parametre_kaydirma(f: Callable[[np.ndarray], float], theta: np.ndarray,
                       k: int) -> float:
    """``½(f(θ+π/2 e_k) − f(θ−π/2 e_k))``.

    ``f(θ) = ⟨ψ(θ)|H|ψ(θ)⟩`` ve ``θ_k`` kapısının üreteci ``G² = I``
    ise bu **tam** türevdir.
    """
    a, b = theta.copy(), theta.copy()
    a[k] += math.pi / 2
    b[k] -= math.pi / 2
    return 0.5 * (f(a) - f(b))


def _sonlu_fark(f: Callable[[np.ndarray], float], theta: np.ndarray,
                k: int, h: float = 1e-6) -> float:
    a, b = theta.copy(), theta.copy()
    a[k] += h
    b[k] -= h
    return (f(a) - f(b)) / (2 * h)


def kaydirma_sarti_ihlali() -> Dict[str, object]:
    """``G² = I`` şartı bozulunca kaydırma kuralı **yanlış** cevap verir.

    Kutuplu hâl: ``U(θ) = e^{−iθn̂}``, ``n̂ = diag(0,1,2)``.  Burada
    ``n̂² ≠ I``dir; kaydırma kuralı sonlu farkla **uyuşmaz** ve fark
    yuvarlama düzeyinde değildir.
    """
    n_ = np.diag([0.0, 1.0, 2.0])
    # |0⟩↔|2⟩ bağı ŞART: yalnız komşu bağlarla (fark 1) ⟨H⟩ saf bir
    # 2π-periyotlu sinüs olur ve kaydırma kuralı tesadüfen doğru çıkar
    # (ölçüldü: fark 0.0000).  Fark-2 terimi π-periyotlu bir bileşen
    # katar ve kural o zaman bozulur.
    H = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=complex)
    psi0 = np.ones(3, dtype=complex) / math.sqrt(3)

    def f(t):
        psi = np.exp(-1j * t[0] * np.diag(n_)) * psi0
        return float((psi.conj() @ (H @ psi)).real)

    t = np.array([0.37])
    return {"kaydırma": parametre_kaydirma(f, t, 0),
            "sonlu_fark": _sonlu_fark(f, t, 0),
            "üreteç": "n̂ = diag(0,1,2), n̂² ≠ I"}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s = []
    n = 4
    kenar_kolay = [(0, 1), (1, 2), (2, 3), (3, 0)]
    kenar_zor = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)]
    H0 = baslangic_hamiltonyeni(n)

    s.append("=== Adiyabatik: başarı, tayf aralığına bağlı ===")
    for ad, ke in (("4-döngü", kenar_kolay), ("K₄ (tam)", kenar_zor)):
        H1 = np.diag(maxcut_hamiltonyeni(n, ke)).astype(complex)
        t = tayf_araligi(H0, H1)
        s.append("  %s: hedef temel katlılık=%d   Δ_min=%.4f (s=%.2f, "
                 "s≤%.2f)   1/Δ²=%.1f   uçta Δ(1)=%.2e"
                 % (ad, t["hedef_temel_katlılık"], t["Δ_min"], t["s_min"],
                    t["s_ust"], t["kaba_T_ölçüsü"], t["uç_aralık"]))
        satir = []
        for T in (0.5, 2.0, 8.0, 32.0, 128.0):
            r = adiyabatik_kos(H0, H1, T)
            satir.append("T=%5.1f→%.4f" % (T, r["başarı"]))
        s.append("     " + "  ".join(satir))
    s.append("  Δ_min her ikisinde de kesme noktasında (s=0.95) çıkıyor:")
    s.append("  aralık uca doğru TEKDÜZE iniyor, yani bu sayı kesmeye")
    s.append("  bağlı. Nitekim 4-döngünün Δ_min'i daha KÜÇÜK olduğu hâlde")
    s.append("  T=128'de başarısı daha YÜKSEK. 'T ≳ 1/Δ²' burada işlemiyor.")
    s.append("  Uçta aralık kapanıyor ama bu ZARARSIZ: kapanma dejenere")
    s.append("  temel öz-uzayın içinde. Başarı o alt uzaya örtüşmeyle")
    s.append("  ölçülüyor ve her iki halde de T ile 1'e gidiyor.")

    s.append("\n=== QAOA: p arttıkça oran ===")
    hc = maxcut_hamiltonyeni(n, kenar_zor)
    s.append("  K₄ MaxCut, en iyi kesim değeri = %.1f" % hc.min())
    for p in (1, 2, 3, 4):
        r = qaoa_eniyile(n, hc, p, tohum=3)
        s.append("  p=%d  ⟨H_C⟩=%.6f   oran=%.4f" % (p, r["beklenen"],
                                                     r["oran"]))
    s.append("  p=0 (salt |+⟩): ⟨H_C⟩=%.6f  oran=%.4f"
             % (float(hc.mean()), float(hc.mean()) / float(hc.min())))

    s.append("\n=== QAOA hız: köşegen faz vs tam dizey ===")
    import time
    for nq in (8, 10, 12):
        ke = [(i, (i + 1) % nq) for i in range(nq)]
        h = maxcut_hamiltonyeni(nq, ke)
        g = np.array([0.4] * 3); b = np.array([0.7] * 3)
        t0 = time.perf_counter()
        psi = qaoa_durumu(nq, h, g, b)
        t1 = time.perf_counter()
        # kıyas: tam dizeyle
        Hc = np.diag(h).astype(complex)
        # U_B(β) = e^{−iβΣX_i}: karıştırıcının Hamiltonyeni +ΣX'tir.
        # (Başlangıç Hamiltonyeni −ΣX; işareti karıştırmak iki yolu
        #  ayırıyordu — ölçüm 1.5e-01 fark verince yakalandı.)
        Hb = np.zeros((2 ** nq, 2 ** nq), dtype=complex)
        for i in range(nq):
            Hb += _tek_kubit(_X, i, nq)
        t2 = time.perf_counter()
        lam, V = np.linalg.eigh(Hb)
        ps = np.full(2 ** nq, 2 ** (-nq / 2.0), dtype=complex)
        for gg, bb in zip(g, b):
            ps = np.exp(-1j * gg * h) * ps
            ps = (V * np.exp(-1j * bb * lam)) @ (V.conj().T @ ps)
        t3 = time.perf_counter()
        s.append("  n=%2d  köşegen yol %.4f s   tam dizey yol %.4f s   "
                 "hızlanma %5.1f×   fark=%.2e"
                 % (nq, t1 - t0, t3 - t2, (t3 - t2) / max(t1 - t0, 1e-9),
                    float(np.abs(psi - ps).max())))
    s.append("  Fark makine hassasiyetinde: hız doğruluktan alınmadı.")

    s.append("\n=== Parametre kaydırma: G²=I iken TAM ===")
    nq = 3
    Hh = np.zeros((8, 8), dtype=complex)
    for i in range(nq):
        Hh += _tek_kubit(_Z, i, nq)

    def dev(theta):
        psi = np.zeros(8, dtype=complex); psi[0] = 1.0
        for i in range(nq):
            c, sn = math.cos(theta[i] / 2), -1j * math.sin(theta[i] / 2)
            R = np.array([[c, sn], [sn, c]], dtype=complex)
            psi = _tek_kubit(R, i, nq) @ psi
        for i in range(nq):
            c = math.cos(theta[nq + i] / 2)
            R = np.array([[np.exp(-1j * theta[nq + i] / 2), 0],
                          [0, np.exp(1j * theta[nq + i] / 2)]], dtype=complex)
            psi = _tek_kubit(R, i, nq) @ psi
        return float((psi.conj() @ (Hh @ psi)).real)

    th = np.array([0.3, 1.1, 2.2, 0.7, 1.9, 2.8])
    for k in range(6):
        a = parametre_kaydirma(dev, th, k)
        b = _sonlu_fark(dev, th, k)
        s.append("  θ_%d  kaydırma=%+.10f  sonlu fark=%+.10f  fark=%.2e"
                 % (k, a, b, abs(a - b)))
    s.append("  (R_x, R_z üreteçleri X/2, Z/2; X²=Z²=I olduğu için kural TAM.")
    s.append("   θ₃..θ₅ türevleri TAM SIFIR: H=ΣZ, R_z ile sıra")
    s.append("   değiştirdiğinden o parametreler ⟨H⟩'yi hiç oynatmıyor.)")

    s.append("\n=== Şart bozulunca: G² ≠ I ===")
    r = kaydirma_sarti_ihlali()
    s.append("  üreteç: %s" % r["üreteç"])
    s.append("  kaydırma=%+.10f   sonlu fark=%+.10f   fark=%.4f"
             % (r["kaydırma"], r["sonlu_fark"],
                abs(r["kaydırma"] - r["sonlu_fark"])))
    s.append("  Fark yuvarlama düzeyinde DEĞİL; kuralın şartı süs değildir.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
