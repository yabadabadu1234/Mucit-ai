"""Morfizm — token uzayları arasındaki eşlemeler ve funktoryel yapı.

Bir morfizm ``φ: M → N`` üç şey taşır:

* **İtme (pushforward)** ``dφ_x: T_xM → T_{φ(x)}N`` — Jacobi dizeyi.
* **Çekme (pullback)** ``φ^*: T^*_{φ(x)}N → T^*_xM`` — Jacobi'nin
  devriği; ko-vektörler ters yöne gider.
* **Metrik çekme** ``(φ^*h)_{ij} = h_{ab}\\,∂_iφ^a\\,∂_jφ^b``.

Bunların **funktoryel** olması, yani

.. math::  d(\\psi\\circ\\varphi)_x = d\\psi_{\\varphi(x)}\\cdot d\\varphi_x,
           \\qquad (\\psi\\circ\\varphi)^* = \\varphi^*\\circ\\psi^*

zincir kaidesinin ta kendisidir.  Bu modül onu iddia etmez, **ölçer**:
rastgele eşlemelerde bileşke Jacobi'si ile Jacobi'lerin çarpımı
karşılaştırılır.  Çekmenin **sırasının tersine dönmesi** (kontravaryans)
ayrıca sınanır — burası işaret/sıra hatasının en sık girdiği yerdir.

Ayrıca:

* **İzometri denetimi** — ``φ^*h = g`` ise ``φ`` mesafeleri korur.
* **Konformal denetimi** — ``φ^*h = λ(x)g`` ise açıları korur, mesafeleri
  korumaz.  Bu ikisi karıştırılır; ölçüt ayrı ayrı hesaplanır.
* **Monoidal yapı** — çarpım uzaylarında ``φ×ψ``nin Jacobi'si blok
  köşegendir; bu da ölçülür.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .manifold import Metrik

__all__ = [
    "Morfizm", "bileske", "carpim_morfizmi", "jakobi",
    "izometri_mi", "konformal_mi", "funktoryellik_olc",
]

_H = np.finfo(float).eps ** (1.0 / 3.0)


def jakobi(f: Callable[[np.ndarray], np.ndarray], x: np.ndarray,
           cikti_boyu: Optional[int] = None) -> np.ndarray:
    """``(∂f^a/∂x^i)`` — merkezî fark, satır ``a``, sütun ``i``."""
    x = np.asarray(x, float)
    m = cikti_boyu if cikti_boyu is not None else np.asarray(f(x)).size
    J = np.empty((m, x.size))
    for i in range(x.size):
        h = _H * max(1.0, abs(float(x[i])))
        arti = x.copy(); arti[i] += h
        eksi = x.copy(); eksi[i] -= h
        J[:, i] = (np.asarray(f(arti), float).ravel()
                   - np.asarray(f(eksi), float).ravel()) / (arti[i] - eksi[i])
    return J


@dataclass
class Morfizm:
    """``φ: ℝⁿ → ℝᵐ`` — token uzayları arası eşleme."""
    n: int
    m: int
    phi: Callable[[np.ndarray], np.ndarray]
    ad: str = ""

    def __call__(self, x: Sequence[float]) -> np.ndarray:
        y = np.asarray(self.phi(np.asarray(x, float)), float).ravel()
        if y.size != self.m:
            raise ValueError(f"çıktı boyu {self.m} olmalı, {y.size} geldi")
        return y

    # --- itme / çekme --------------------------------------------------
    def dphi(self, x: Sequence[float]) -> np.ndarray:
        """``dφ_x`` — ``(m, n)`` Jacobi."""
        return jakobi(self.phi, np.asarray(x, float), self.m)

    def itme(self, x: Sequence[float], v: Sequence[float]) -> np.ndarray:
        """Teğet vektörü ileri taşı: ``v ↦ dφ_x·v``."""
        v = np.asarray(v, float)
        if v.size != self.n:
            raise ValueError(f"teğet vektör boyu {self.n} olmalı")
        return self.dphi(x) @ v

    def cekme(self, x: Sequence[float], w: Sequence[float]) -> np.ndarray:
        """Ko-vektörü GERİ taşı: ``w ↦ (dφ_x)ᵀ·w``.

        Yön kasten terstir: bir ko-vektör (1-form) hedeften kaynağa
        çekilir.  Vektörlerle aynı yönde taşımaya çalışmak, hedef
        uzayın boyutu farklıysa şekil hatası verir — ki bu, hatanın
        sessizce geçmemesi bakımından iyidir.
        """
        w = np.asarray(w, float)
        if w.size != self.m:
            raise ValueError(f"ko-vektör boyu {self.m} olmalı")
        return self.dphi(x).T @ w

    def metrik_cek(self, hedef: Metrik, x: Sequence[float]) -> np.ndarray:
        """``(φ^*h)_{ij} = h_{ab} ∂_iφ^a ∂_jφ^b``."""
        if hedef.n != self.m:
            raise ValueError("hedef metriğin boyutu φ'nin çıktısıyla uyuşmalı")
        J = self.dphi(x)
        H = hedef.G(self(x))
        return J.T @ H @ J

    def cekilmis_metrik(self, hedef: Metrik) -> Metrik:
        """Çekilmiş metriği bir ``Metrik`` nesnesi olarak ver."""
        return Metrik(self.n, lambda z: self.metrik_cek(hedef, z),
                      f"{self.ad}^*{hedef.ad}")


def bileske(psi: Morfizm, phi: Morfizm) -> Morfizm:
    """``ψ∘φ`` — önce ``φ``, sonra ``ψ``."""
    if phi.m != psi.n:
        raise ValueError(f"boyutlar uyuşmuyor: {phi.m} ≠ {psi.n}")
    return Morfizm(phi.n, psi.m,
                   lambda x: psi.phi(np.asarray(phi.phi(x), float)),
                   f"{psi.ad}∘{phi.ad}")


def carpim_morfizmi(phi: Morfizm, psi: Morfizm) -> Morfizm:
    """``φ×ψ`` — çarpım uzayında bileşen bazında etki."""
    def f(x: np.ndarray) -> np.ndarray:
        a = np.asarray(phi.phi(x[:phi.n]), float).ravel()
        b = np.asarray(psi.phi(x[phi.n:]), float).ravel()
        return np.concatenate([a, b])
    return Morfizm(phi.n + psi.n, phi.m + psi.m, f,
                   f"{phi.ad}×{psi.ad}")


# ══════════════════════════════════════════════════════════════════════
#  Ölçümler
# ══════════════════════════════════════════════════════════════════════

def funktoryellik_olc(psi: Morfizm, phi: Morfizm,
                      x: Sequence[float]) -> Dict[str, float]:
    """Zincir kaidesi ve çekmenin ters sırası — ölçülerek.

    İki iddia:

    1. ``d(ψ∘φ)_x = dψ_{φ(x)} · dφ_x`` (kovaryant, sıra korunur)
    2. ``(ψ∘φ)^* = φ^* ∘ ψ^*`` (kontravaryant, sıra **tersine döner**)

    İkincisinde sırayı korumak yaygın bir hatadır.  Yanlış sıra ayrıca
    denenir; ``n ≠ m`` iken bu sayısal bir sapma değil doğrudan **tip
    hatası** verir — yani hata sessizce yanlış bir sayı üretemez.
    """
    x = np.asarray(x, float)
    bil = bileske(psi, phi)
    sol = bil.dphi(x)
    sag = psi.dphi(phi(x)) @ phi.dphi(x)
    olcek = max(float(np.max(np.abs(sol))), 1e-30)

    w = np.linspace(0.3, 1.1, psi.m)
    cekme_dogru = phi.cekme(x, psi.cekme(phi(x), w))
    cekme_bilesik = bil.cekme(x, w)

    # Yanlış sıra (``ψ^* ∘ φ^*``) denenirse ne olur?  Boyutlar
    # ``n ≠ m`` iken bu daha kurulurken çöker — yani hata sayısal bir
    # sapma olarak değil, doğrudan TİP hatası olarak görünür.  Bu iyi
    # bir haberdir: sessizce yanlış sayı üretmez.
    try:
        psi.cekme(phi(x), phi.cekme(x, w))
        yanlis_sira: object = "kurulabildi (boyutlar tesadüfen uydu)"
    except ValueError as e:
        yanlis_sira = f"tip hatası: {e}"

    return {
        "zincir_kaidesi_sapması": float(np.max(np.abs(sol - sag))) / olcek,
        "çekme_sapması": float(np.max(np.abs(cekme_dogru - cekme_bilesik))),
        "çekme_büyüklüğü": float(np.max(np.abs(cekme_bilesik))),
        "ters_sıra": yanlis_sira,
    }


def izometri_mi(phi: Morfizm, kaynak: Metrik, hedef: Metrik,
                noktalar: Sequence[Sequence[float]],
                tol: float = 1e-7) -> Dict[str, object]:
    """``φ^*h = g`` her noktada mı?"""
    sapmalar = []
    for x in noktalar:
        fark = phi.metrik_cek(hedef, x) - kaynak.G(np.asarray(x, float))
        sapmalar.append(float(np.max(np.abs(fark))))
    return {"azamî_sapma": max(sapmalar), "izometri": max(sapmalar) < tol,
            "sapmalar": sapmalar}


def konformal_mi(phi: Morfizm, kaynak: Metrik, hedef: Metrik,
                 noktalar: Sequence[Sequence[float]],
                 tol: float = 1e-7) -> Dict[str, object]:
    """``φ^*h = λ(x)·g`` — λ noktadan noktaya değişebilir.

    λ, her noktada ``tr(g^{-1}φ^*h)/n`` ile tahmin edilir (en küçük
    kareler anlamında en iyi skaler); sonra kalan sapma ölçülür.
    İzometri, ``λ ≡ 1`` olan özel hâldir — o yüzden her izometri
    konformaldir ama tersi doğru değildir.
    """
    sapmalar, lambdalar = [], []
    for x in noktalar:
        x = np.asarray(x, float)
        A = phi.metrik_cek(hedef, x)
        G = kaynak.G(x)
        lam = float(np.trace(np.linalg.solve(G, A)) / kaynak.n)
        lambdalar.append(lam)
        sapmalar.append(float(np.max(np.abs(A - lam * G))))
    return {
        "azamî_sapma": max(sapmalar),
        "konformal": max(sapmalar) < tol,
        "λ_değerleri": lambdalar,
        "λ_sabit_mi": (max(lambdalar) - min(lambdalar)) < tol,
    }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    from .manifold import duz_metrik, konformal_metrik
    s: List[str] = []

    phi = Morfizm(2, 3, lambda x: np.array([x[0] ** 2 + x[1],
                                            np.sin(x[0]) * x[1],
                                            np.exp(0.3 * x[0])]), "φ")
    psi = Morfizm(3, 2, lambda y: np.array([y[0] * y[2],
                                            np.tanh(y[1] + y[0])]), "ψ")
    x = np.array([0.7, -0.4])

    s.append("=== Funktoryellik: zincir kaidesi ölçülüyor ===")
    f = funktoryellik_olc(psi, phi, x)
    s.append(f"  d(ψ∘φ) ile dψ·dφ arasındaki bağıl sapma:"
             f" {f['zincir_kaidesi_sapması']:.3e}")
    s.append(f"  (ψ∘φ)^*w ile φ^*(ψ^*w) arasındaki sapma:"
             f" {f['çekme_sapması']:.3e}"
             f"   (büyüklük {f['çekme_büyüklüğü']:.4f})")
    s.append("  → çekme sırası tersine dönüyor ve doğru netice veriyor.")
    s.append(f"  yanlış sıra (ψ^*∘φ^*) denenirse: {f['ters_sıra']}")

    s.append("\n=== Çekmenin yönü gerçekten ters mi? ===")
    s.append("  φ: ℝ²→ℝ³ ; vektör ileri gider (2→3), ko-vektör geri (3→2):")
    v = np.array([1.0, 0.5])
    w = np.array([0.2, -0.7, 1.3])
    s.append(f"    itme(v)  boyu = {phi.itme(x, v).size}  (hedefte)")
    s.append(f"    çekme(w) boyu = {phi.cekme(x, w).size}  (kaynakta)")
    try:
        phi.cekme(x, v)
        s.append("    yanlış boyda ko-vektör kabul edildi (BEKLENMEZ)")
    except ValueError as e:
        s.append(f"    yanlış boyda ko-vektör reddedildi: {e}")

    s.append("\n=== Metrik çekme ===")
    duz3 = duz_metrik(3)
    G = phi.metrik_cek(duz3, x)
    J = phi.dphi(x)
    s.append(f"  φ^*δ = JᵀJ mi? sapma = {np.max(np.abs(G - J.T @ J)):.3e}")
    s.append(f"  çekilmiş metrik simetrik mi? "
             f"{np.max(np.abs(G - G.T)):.3e}")
    s.append(f"  pozitif tanımlı mı? özdeğerler ="
             f" {np.array2string(np.linalg.eigvalsh(G), precision=5)}")

    s.append("\n=== İzometri v konformallik ===")
    noktalar = [[0.3, 0.5], [-0.8, 1.2], [1.5, -0.3]]
    donme = Morfizm(2, 2, lambda z: np.array([
        np.cos(0.7) * z[0] - np.sin(0.7) * z[1],
        np.sin(0.7) * z[0] + np.cos(0.7) * z[1]]), "dönme")
    olcekleme = Morfizm(2, 2, lambda z: 2.5 * z, "×2.5")
    egri = Morfizm(2, 2, lambda z: np.array([z[0] ** 2, z[1]]), "eğri")
    duz2 = duz_metrik(2)
    for ad, m in (("dönme", donme), ("×2.5", olcekleme), ("eğri", egri)):
        i = izometri_mi(m, duz2, duz2, noktalar)
        k = konformal_mi(m, duz2, duz2, noktalar)
        s.append(f"  {ad:8s} izometri={str(i['izometri']):5s}"
                 f" (sapma {i['azamî_sapma']:.2e})"
                 f"  konformal={str(k['konformal']):5s}"
                 f"  λ sabit mi={k['λ_sabit_mi']}"
                 f"  λ≈{np.mean(k['λ_değerleri']):.4f}")
    s.append("  → her izometri konformaldir; ×2.5 konformaldir ama izometri")
    s.append("    değildir; 'eğri' ikisi de değildir. Ölçüt ayırt ediyor.")

    s.append("\n=== Monoidal yapı: (φ×ψ)'nin Jacobi'si blok köşegen ===")
    a = Morfizm(2, 2, lambda z: np.array([z[0] ** 2, z[0] * z[1]]), "a")
    b = Morfizm(3, 2, lambda z: np.array([z[0] + z[2], np.sin(z[1])]), "b")
    c = carpim_morfizmi(a, b)
    p = np.array([0.4, -0.6, 1.1, 0.2, -0.9])
    Jc = c.dphi(p)
    Ja, Jb = a.dphi(p[:2]), b.dphi(p[2:])
    blok = np.zeros_like(Jc)
    blok[:2, :2] = Ja
    blok[2:, 2:] = Jb
    s.append(f"  Jacobi şekli = {Jc.shape}"
             f"   blok köşegenden sapma = {np.max(np.abs(Jc - blok)):.3e}")
    s.append(f"  köşegen dışı blokların büyüklüğü ="
             f" {max(np.max(np.abs(Jc[:2, 2:])), np.max(np.abs(Jc[2:, :2]))):.3e}")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
