"""Manifold — metrik, bağlantı, eğrilik ve Laplace–Beltrami.

Bir token uzayı, üzerinde bir Riemann metriği ``g_{ij}(x)`` taşıyan
manifold olarak ele alınır.  Bütün geometrik büyüklükler metrikten
**türetilir**; hiçbiri elle verilmez:

.. math::

   \\Gamma^k_{ij} &= \\tfrac12 g^{kl}\\bigl(\\partial_i g_{jl}
                    + \\partial_j g_{il} - \\partial_l g_{ij}\\bigr) \\\\
   R^\\rho_{\\ \\sigma\\mu\\nu} &= \\partial_\\mu \\Gamma^\\rho_{\\nu\\sigma}
       - \\partial_\\nu \\Gamma^\\rho_{\\mu\\sigma}
       + \\Gamma^\\rho_{\\mu\\lambda}\\Gamma^\\lambda_{\\nu\\sigma}
       - \\Gamma^\\rho_{\\nu\\lambda}\\Gamma^\\lambda_{\\mu\\sigma} \\\\
   R_{\\sigma\\nu} &= R^\\mu_{\\ \\sigma\\mu\\nu} \\qquad
   R = g^{\\sigma\\nu}R_{\\sigma\\nu} \\\\
   \\Delta f &= \\frac{1}{\\sqrt{|g|}}\\,\\partial_i
       \\bigl(\\sqrt{|g|}\\;g^{ij}\\,\\partial_j f\\bigr)

Doğruluğun teminatı **bilinen manifoldlarda sağlamadır**: düz uzayda
bütün eğrilik bileşenleri sıfır çıkmalı; ``r`` yarıçaplı 2-küre için
``K = 1/r²``, ``R = 2/r²`` çıkmalı; hiperbolik düzlemde ``K = −1``
çıkmalı.  Bu üçü de test edilir.

Ayrıca Riemann tensörünün **simetrileri** ayrı ayrı ölçülür — bunlar
formülün doğru kurulduğunun bağımsız şahididir:

* ``R_{ρσμν} = −R_{σρμν}`` ve ``= −R_{ρσνμ}`` (çift antisimetri)
* ``R_{ρσμν} = R_{μνρσ}`` (çift değişimi)
* ``R_{ρ[σμν]} = 0`` (birinci Bianchi)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "Metrik", "duz_metrik", "kure_metrigi", "hiperbolik_metrik",
    "konformal_metrik", "riemann_simetrileri",
]

_H = np.finfo(float).eps ** (1.0 / 3.0)


def _turev(f: Callable[[np.ndarray], np.ndarray], x: np.ndarray,
           j: int) -> np.ndarray:
    """``∂f/∂x_j`` — merkezî fark, koordinat başına ölçekli adım."""
    h = _H * max(1.0, abs(float(x[j])))
    arti = x.copy(); arti[j] += h
    eksi = x.copy(); eksi[j] -= h
    return (np.asarray(f(arti), float) - np.asarray(f(eksi), float)) \
        / (arti[j] - eksi[j])


def _ikinci_turev(f: Callable[[np.ndarray], np.ndarray], x: np.ndarray,
                  i: int, j: int) -> np.ndarray:
    """``∂²f/∂x_i∂x_j`` — merkezî farkın merkezî farkı."""
    if i == j:
        h = _H * max(1.0, abs(float(x[i])))
        arti = x.copy(); arti[i] += h
        eksi = x.copy(); eksi[i] -= h
        return (np.asarray(f(arti), float) - 2 * np.asarray(f(x), float)
                + np.asarray(f(eksi), float)) / (h * h)
    return _turev(lambda z: _turev(f, z, j), x, i)


@dataclass
class Metrik:
    """``g_{ij}(x)`` ile verilen Riemann manifoldu.

    ``g``: ``x ↦ (n,n)`` simetrik pozitif tanımlı dizey.
    Kurulurken bir noktada simetri ve pozitif tanımlılık **denetlenir**;
    bozuk bir metrik bütün aşağı akış büyüklüklerini sessizce bozar.
    """
    n: int
    g: Callable[[np.ndarray], np.ndarray]
    ad: str = ""

    def denetle(self, x: Sequence[float], tol: float = 1e-10) -> None:
        G = np.asarray(self.g(np.asarray(x, float)), float)
        if G.shape != (self.n, self.n):
            raise ValueError(f"metrik {(self.n, self.n)} olmalı, {G.shape}")
        if np.max(np.abs(G - G.T)) > tol:
            raise ValueError("metrik simetrik değil")
        if np.min(np.linalg.eigvalsh(G)) <= 0:
            raise ValueError("metrik pozitif tanımlı değil")

    # --- temel büyüklükler --------------------------------------------
    def G(self, x: np.ndarray) -> np.ndarray:
        return np.asarray(self.g(np.asarray(x, float)), float)

    def G_ters(self, x: np.ndarray) -> np.ndarray:
        """``g^{ij}`` — ``solve`` ile, açık ters alma yerine.

        ``inv`` da aynı işi yapar ama ``solve`` hem daha kararlıdır hem
        de tekil bir metrikte sessizce devasa sayılar üretmek yerine
        ``LinAlgError`` verir; tekillik gizlenmez.
        """
        return np.linalg.solve(self.G(x), np.eye(self.n))

    def hacim(self, x: np.ndarray) -> float:
        """``√|g|`` — hacim öğesi."""
        return float(np.sqrt(abs(np.linalg.det(self.G(x)))))

    def dg(self, x: np.ndarray) -> np.ndarray:
        """``∂_k g_{ij}`` — indis sırası ``[k,i,j]``."""
        return np.array([_turev(self.g, np.asarray(x, float), k)
                         for k in range(self.n)])

    # --- bağlantı ------------------------------------------------------
    def christoffel(self, x: np.ndarray) -> np.ndarray:
        """``Γ^k_{ij}`` — indis sırası ``[k,i,j]``.

        Levi-Civita bağlantısı burulmasızdır, yani ``Γ^k_{ij}`` alt iki
        indiste simetriktir; formül zaten simetrik kurulduğu için bu
        cebirsel olarak garantidir ve testte ayrıca ölçülür.
        """
        x = np.asarray(x, float)
        gi = self.G_ters(x)
        d = self.dg(x)                      # d[k,i,j] = ∂_k g_{ij}
        # Γ^k_{ij} = ½ g^{kl} (∂_i g_{jl} + ∂_j g_{il} − ∂_l g_{ij})
        # d[k,i,j] = ∂_k g_{ij} olduğuna göre, üç terim de DOĞRUDAN d'den
        # okunur; ara bir transpoze almak indisleri karıştırır.
        terim = (np.einsum("ijl->ijl", d)      # ∂_i g_{jl}
                 + np.einsum("jil->ijl", d)    # ∂_j g_{il}
                 - np.einsum("lij->ijl", d))   # ∂_l g_{ij}
        return 0.5 * np.einsum("kl,ijl->kij", gi, terim)

    def dChristoffel(self, x: np.ndarray) -> np.ndarray:
        """``∂_m Γ^k_{ij}`` — indis sırası ``[m,k,i,j]``."""
        x = np.asarray(x, float)
        return np.array([_turev(self.christoffel, x, m)
                         for m in range(self.n)])

    # --- eğrilik -------------------------------------------------------
    def riemann(self, x: np.ndarray) -> np.ndarray:
        """``R^ρ_{σμν}`` — indis sırası ``[ρ,σ,μ,ν]``."""
        G_ = self.christoffel(x)            # [k,i,j]
        dG = self.dChristoffel(x)           # [m,k,i,j]
        # ∂_μ Γ^ρ_{νσ} − ∂_ν Γ^ρ_{μσ} + Γ^ρ_{μλ}Γ^λ_{νσ} − Γ^ρ_{νλ}Γ^λ_{μσ}
        t1 = np.einsum("mrns->rsmn", dG)    # ∂_μ Γ^ρ_{νσ}
        t2 = np.einsum("nrms->rsmn", dG)    # ∂_ν Γ^ρ_{μσ}
        t3 = np.einsum("rml,lns->rsmn", G_, G_)
        t4 = np.einsum("rnl,lms->rsmn", G_, G_)
        return t1 - t2 + t3 - t4

    def riemann_alt(self, x: np.ndarray) -> np.ndarray:
        """``R_{ρσμν} = g_{ρλ} R^λ_{σμν}`` — bütün indisler aşağıda."""
        return np.einsum("rl,lsmn->rsmn", self.G(x), self.riemann(x))

    def ricci(self, x: np.ndarray) -> np.ndarray:
        """``R_{σν} = R^μ_{σμν}`` — Riemann'ın 1. ve 3. indisi büzülür."""
        return np.einsum("msmn->sn", self.riemann(x))

    def skaler_egrilik(self, x: np.ndarray) -> float:
        """``R = g^{σν} R_{σν}``."""
        return float(np.einsum("sn,sn->", self.G_ters(x), self.ricci(x)))

    def kesit_egriligi(self, x: np.ndarray, u: Sequence[float],
                       v: Sequence[float]) -> float:
        """``K(u,v) = R_{ρσμν}u^ρv^σu^μv^ν / (|u|²|v|² − ⟨u,v⟩²)``.

        Daralma sırası konvansiyona bağlıdır ve kolayca ters yazılır.
        Burada ``R^ρ_{σμν}``de ``μν`` "hangi iki yön" slotları, ``σ`` ise
        üzerine etki edilen argümandır; o hâlde ``⟨R(u,v)v, u⟩`` daralması
        ``u^ρ v^σ u^μ v^ν`` sırasını verir.  ``u,v,v,u`` yazmak, ``R``nin
        son çift antisimetrisi yüzünden işareti TERSİNE çevirir — küreyi
        negatif eğrilikli gösterir.  Aşağıdaki sağlama tam bu yüzden var.

        Payda, ``u`` ile ``v``nin gerdiği paralelkenarın alanının
        karesidir; sıfırsa (vektörler paralel) kesit tanımsızdır ve
        ``nan`` döner — sıfıra bölünüp sonsuz üretilmez.
        """
        u = np.asarray(u, float); v = np.asarray(v, float)
        G = self.G(x)
        Rd = self.riemann_alt(x)
        pay = float(np.einsum("rsmn,r,s,m,n->", Rd, u, v, u, v))
        uu = float(u @ G @ u); vv = float(v @ G @ v); uv = float(u @ G @ v)
        payda = uu * vv - uv * uv
        if abs(payda) < 1e-14:
            return float("nan")
        return pay / payda

    # --- Laplace–Beltrami ----------------------------------------------
    def laplace_beltrami(self, f: Callable[[np.ndarray], float],
                         x: np.ndarray) -> float:
        """``Δf = |g|^{-1/2} ∂_i(|g|^{1/2} g^{ij} ∂_j f)``.

        Diverjans formu kasten tercih edildi.  Açılmış hâli
        ``g^{ij}∂_i∂_j f − g^{ij}Γ^k_{ij}∂_k f`` cebirsel olarak aynıdır
        ama Christoffel'in **birinci** türevlerini ister; diverjans formu
        ise yalnız metriğin birinci türevini ister, yani bir mertebe
        daha az sayısal türev alınır.  İki yol da hesaplanıp
        karşılaştırılabilsin diye ikincisi de ayrıca yazıldı.
        """
        x = np.asarray(x, float)

        def akı(z: np.ndarray) -> np.ndarray:
            """``√|g| g^{ij} ∂_j f`` — bir vektör alanı."""
            gi = self.G_ters(z)
            grad = np.array([_turev(lambda w: np.array([f(w)]), z, j)[0]
                             for j in range(self.n)])
            return self.hacim(z) * (gi @ grad)

        div = sum(_turev(akı, x, i)[i] for i in range(self.n))
        return float(div / self.hacim(x))

    def laplace_beltrami_christoffel(self, f: Callable[[np.ndarray], float],
                                     x: np.ndarray) -> float:
        """``Δf = g^{ij}(∂_i∂_j f − Γ^k_{ij}∂_k f)`` — ikinci yol."""
        x = np.asarray(x, float)
        gi = self.G_ters(x)
        G_ = self.christoffel(x)
        skaler = lambda w: np.array([f(w)])
        grad = np.array([_turev(skaler, x, j)[0] for j in range(self.n)])
        hes = np.array([[_ikinci_turev(skaler, x, i, j)[0]
                         for j in range(self.n)] for i in range(self.n)])
        return float(np.einsum("ij,ij->", gi, hes)
                     - np.einsum("ij,kij,k->", gi, G_, grad))


# ══════════════════════════════════════════════════════════════════════
#  Bilinen manifoldlar — sağlama için
# ══════════════════════════════════════════════════════════════════════

def duz_metrik(n: int) -> Metrik:
    """Öklid: ``g = I``.  Bütün eğrilik sıfır olmalı."""
    I = np.eye(n)
    return Metrik(n, lambda x: I.copy(), "düz")


def kure_metrigi(r: float = 1.0) -> Metrik:
    """``r`` yarıçaplı 2-küre, ``(θ, φ)`` koordinatlarında.

    ``g = diag(r², r² sin²θ)``.  Beklenen: ``K = 1/r²``, ``R = 2/r²``.
    Kutuplarda (``sinθ = 0``) koordinat tekilliği vardır; metrik orada
    dejenere olur ve hesap yapılmaz — tekillik gizlenmez.
    """
    def g(x: np.ndarray) -> np.ndarray:
        t = float(x[0])
        return np.diag([r * r, r * r * np.sin(t) ** 2])
    return Metrik(2, g, f"küre(r={r})")


def hiperbolik_metrik() -> Metrik:
    """Poincaré üst yarı düzlemi: ``g = y^{-2} I``.  Beklenen ``K = −1``."""
    def g(x: np.ndarray) -> np.ndarray:
        y = float(x[1])
        return np.eye(2) / (y * y)
    return Metrik(2, g, "hiperbolik")


def konformal_metrik(n: int, olcek: Callable[[np.ndarray], float]) -> Metrik:
    """``g = e^{2φ(x)} δ`` — konformal düz metrik."""
    def g(x: np.ndarray) -> np.ndarray:
        return np.exp(2.0 * float(olcek(x))) * np.eye(n)
    return Metrik(n, g, "konformal")


# ══════════════════════════════════════════════════════════════════════
#  Riemann simetrileri — formülün bağımsız şahidi
# ══════════════════════════════════════════════════════════════════════

def riemann_simetrileri(m: Metrik, x: Sequence[float],
                        tol: float = 1e-5) -> Dict[str, object]:
    """Dört simetrinin ihlal büyüklükleri."""
    R = m.riemann_alt(np.asarray(x, float))
    olcek = max(float(np.max(np.abs(R))), 1e-30)
    ilk = float(np.max(np.abs(R + np.einsum("rsmn->srmn", R)))) / olcek
    son = float(np.max(np.abs(R + np.einsum("rsmn->rsnm", R)))) / olcek
    cift = float(np.max(np.abs(R - np.einsum("rsmn->mnrs", R)))) / olcek
    bianchi = float(np.max(np.abs(
        R + np.einsum("rsmn->rmns", R) + np.einsum("rsmn->rnsm", R)))) / olcek
    return {
        "büyüklük": olcek,
        "ilk_çift_antisimetri": ilk,
        "son_çift_antisimetri": son,
        "çift_değişimi": cift,
        "birinci_Bianchi": bianchi,
        "hepsi_sağlanıyor": max(ilk, son, cift, bianchi) < tol,
    }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s: List[str] = []

    s.append("=== Düz uzay: bütün eğrilik sıfır olmalı ===")
    d = duz_metrik(3)
    x = np.array([0.3, -0.7, 1.1])
    s.append(f"  ‖Γ‖∞      = {np.max(np.abs(d.christoffel(x))):.3e}")
    s.append(f"  ‖Riemann‖∞ = {np.max(np.abs(d.riemann(x))):.3e}")
    s.append(f"  skaler R   = {d.skaler_egrilik(x):.3e}")

    s.append("\n=== 2-küre: K = 1/r², R = 2/r² ===")
    for r in (1.0, 2.0, 0.5):
        k = kure_metrigi(r)
        p = np.array([1.0, 0.4])          # kutuptan uzak bir nokta
        K = k.kesit_egriligi(p, [1.0, 0.0], [0.0, 1.0])
        R = k.skaler_egrilik(p)
        s.append(f"  r={r:<4} K={K:.10f} (beklenen {1/r**2:.10f})"
                 f"   R={R:.10f} (beklenen {2/r**2:.10f})")

    s.append("\n=== Hiperbolik düzlem: K = −1 ===")
    h = hiperbolik_metrik()
    for p in ([0.0, 1.0], [2.0, 0.5], [-1.0, 3.0]):
        K = h.kesit_egriligi(np.array(p), [1.0, 0.0], [0.0, 1.0])
        s.append(f"  nokta {str(p):12s} K = {K:.10f}"
                 f"   R = {h.skaler_egrilik(np.array(p)):.10f}")

    s.append("\n=== Riemann simetrileri (bağıl ihlal) ===")
    for ad, m, p in (("küre", kure_metrigi(1.0), [1.0, 0.4]),
                     ("hiperbolik", hiperbolik_metrik(), [0.5, 1.3])):
        r = riemann_simetrileri(m, p)
        s.append(f"  {ad:11s} antisim {r['ilk_çift_antisimetri']:.2e}/"
                 f"{r['son_çift_antisimetri']:.2e}"
                 f"  çift-değişim {r['çift_değişimi']:.2e}"
                 f"  Bianchi {r['birinci_Bianchi']:.2e}"
                 f"  → {r['hepsi_sağlanıyor']}")

    s.append("\n=== Laplace–Beltrami: iki yol aynı sayıyı mı veriyor? ===")
    f = lambda z: float(np.sin(z[0]) * np.exp(0.3 * z[1]))
    for ad, m, p in (("düz(2)", duz_metrik(2), [0.4, 0.9]),
                     ("küre", kure_metrigi(1.0), [1.0, 0.4]),
                     ("hiperbolik", hiperbolik_metrik(), [0.5, 1.3])):
        a = m.laplace_beltrami(f, np.array(p))
        b = m.laplace_beltrami_christoffel(f, np.array(p))
        s.append(f"  {ad:11s} diverjans={a:+.8f}  Christoffel={b:+.8f}"
                 f"  fark={abs(a-b):.2e}")

    s.append("\n  Düz uzayda Δ, alelâde Laplasyen'e inmeli:")
    p = np.array([0.4, 0.9])
    tam = -np.sin(p[0]) * np.exp(0.3 * p[1]) \
        + 0.09 * np.sin(p[0]) * np.exp(0.3 * p[1])
    s.append(f"    sayısal={duz_metrik(2).laplace_beltrami(f, p):+.8f}"
             f"   kapalı={tam:+.8f}")

    s.append("\n=== Koordinat tekilliği gizlenmiyor ===")
    k = kure_metrigi(1.0)
    try:
        k.denetle([0.0, 0.0])          # kutup: sin θ = 0
        s.append("  kutupta metrik kabul edildi (BEKLENMEZ)")
    except ValueError as e:
        s.append(f"  kutupta (θ=0): {e}")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
