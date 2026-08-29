"""
Polinomial Tensör Halkası (PTR) -- çevrimli MPS + Chebyshev çekirdeği.

Vesikadaki hüküm: *"Çok boyutlu optimizasyon yüzeyini dairesel periyodik
sınır şartlarıyla bağlayan ve Schmidt rankını logaritmik tıkızlıkta
hapseden tensör çevrimleri."*

    ψ(x) = Tr( G₁[:,x₁,:] G₂[:,x₂,:] ⋯ G_N[:,x_N,:] ) ,  G_k ∈ ℂ^{χ×d×χ}

**Halka ile zincirin farkı.** Açık MPS'te uçlar ``1`` boyutludur; birinci
ile sonuncu değişken arasındaki münasebet ancak bütün zincirden geçerek
kurulur. Halkada uçlar **kapalıdır** (iz alınır): birinci ile sonuncu
doğrudan komşudur. Neticesi ölçülebilir bir şeydir -- *dönemli*
(periyodik) ve *döngüsel bakışımlı* fonksiyonlarda halka aynı ``χ`` ile
zincirden belirgin daha az hata verir. Aşağıda ölçülmüştür.

**Bedeli de gizlenmez:** halkada **çevrim vardır**. Çevrim, ``nefs/agac.py``
de kaçınılan şeyin ta kendisidir: kanonik hâl tanımsızlaşır, en iyi kesme
(optimal truncation) garantisi düşer. Onun için PTR burada **durum
temsili** olarak değil, **yüzey temsili** olarak kullanılır: kayıp
yüzeyinin kompakt bir tarifi. Dalganın kendisi ağaçtadır (H53), yüzey
halkadadır; ikisi karıştırılmaz.

**"Polinomial" nereden.** Sürekli bir parametre ``t ∈ [−1,1]`` için
çekirdek Chebyshev tabanında açılır::

    G_k(t) = Σ_{p=0}^{P} C[k,p] · T_p(t)

Böylece halka ayrık bir dizin üzerinde değil **sürekli bir yüzey**
üzerinde tanımlı olur; nefsin 250 açısı gibi sürekli parametreler
ayrıklaştırılmadan taşınabilir.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from .nqs import chebyshev

__all__ = ["TensorHalka", "PolinomHalka"]


class TensorHalka:
    """``ψ(x) = Tr(Π_k G_k[:, x_k, :])`` -- ayrık dizinli halka."""

    def __init__(self, n: int, d: int = 2, chi: int = 4,
                 tohum: int = 0, halka: bool = True) -> None:
        self.n, self.d, self.chi, self.halka = int(n), int(d), int(chi), halka
        rng = np.random.default_rng(tohum)
        self.G = [rng.normal(scale=1.0 / np.sqrt(chi),
                             size=(chi, d, chi))
                  for _ in range(n)]
        if not halka:
            # açık MPS: uçlar 1 boyutlu -- mukayese için
            self.G[0] = self.G[0][:1]
            self.G[-1] = self.G[-1][:, :, :1]

    # -----------------------------------------------------------------
    def __len__(self) -> int:
        return sum(g.size for g in self.G)

    def genlik(self, X: np.ndarray) -> np.ndarray:
        """``(B, n)`` dizinler → ``(B,)`` değer. Yığın hâlinde büzülür."""
        X = np.atleast_2d(np.asarray(X, int))
        B = len(X)
        M = self.G[0][:, X[:, 0], :]                 # (χ₀, B, χ)
        M = np.moveaxis(M, 1, 0)                     # (B, χ₀, χ)
        for k in range(1, self.n):
            Nk = np.moveaxis(self.G[k][:, X[:, k], :], 1, 0)
            M = np.einsum("bij,bjk->bik", M, Nk, optimize=True)
        return (np.einsum("bii->b", M) if self.halka
                else M[:, 0, 0])

    def durum(self) -> Dict[str, float]:
        return {"n": float(self.n), "d": float(self.d), "χ": float(self.chi),
                "halka": float(self.halka), "parametre": float(len(self)),
                "açık_tablo_olsaydı_log2": float(self.n
                                                 * np.log2(self.d))}


# =====================================================================
class PolinomHalka:
    """Sürekli parametrede halka: ``G_k(t) = Σ_p C[k,p] T_p(t)``.

    Ayrıklaştırma yoktur; ``t`` sürekli kalır. Bu, nefsin açıları gibi
    sürekli parametrelerde ``2^{bit}`` kaybını tamamen ortadan kaldırır.
    """

    def __init__(self, n: int, chi: int = 4, derece: int = 6,
                 tohum: int = 0, halka: bool = True) -> None:
        self.n, self.chi, self.derece = int(n), int(chi), int(derece)
        self.halka = halka
        rng = np.random.default_rng(tohum)
        self.C = rng.normal(scale=1.0 / np.sqrt(chi * (derece + 1)),
                            size=(n, derece + 1, chi, chi))

    def __len__(self) -> int:
        return int(self.C.size)

    def cekirdek(self, T: np.ndarray) -> np.ndarray:
        """``T``: ``(B, n, P+1)`` Chebyshev tabanı → ``(B, n, χ, χ)``."""
        return np.einsum("bnp,npij->bnij", T, self.C, optimize=True)

    def deger(self, t: np.ndarray) -> np.ndarray:
        """``t``: ``(B, n)`` ∈ ``[-1,1]`` → ``(B,)``."""
        t = np.atleast_2d(np.asarray(t, float))
        K = self.cekirdek(chebyshev(t, self.derece))
        M = K[:, 0]
        for k in range(1, self.n):
            M = np.einsum("bij,bjk->bik", M, K[:, k], optimize=True)
        return (np.einsum("bii->b", M) if self.halka else M[:, 0, 0])

    def oturt(self, t: np.ndarray, y: np.ndarray, tur: int = 30,
              lam: float = 1e-6) -> List[float]:
        """**Değişmeli en küçük kareler** (ALS) -- gradyan inişi yok.

        Halka, her bir ``G_k``da **doğrusaldır** (ötekiler sabitken).
        Onun için her çekirdek kapalı formda çözülür ve sırayla dolaşılır.
        Bu, kütük H3'ün "uydurma kapalı formdur" şartını halkada da
        karşılar; Adam/SGD hiç girmez.
        """
        t = np.atleast_2d(np.asarray(t, float))
        y = np.asarray(y, float)
        Tb = chebyshev(t, self.derece)                   # (B, n, P+1)
        seyir: List[float] = []
        for _ in range(tur):
            K = self.cekirdek(Tb)                        # (B, n, χ, χ)
            for k in range(self.n):
                # sol = Π_{j<k}, sag = Π_{j>k}
                sol = None
                for j in range(k):
                    sol = K[:, j] if sol is None else np.einsum(
                        "bij,bjk->bik", sol, K[:, j], optimize=True)
                sag = None
                for j in range(k + 1, self.n):
                    sag = K[:, j] if sag is None else np.einsum(
                        "bij,bjk->bik", sag, K[:, j], optimize=True)
                B = len(t)
                I = np.broadcast_to(np.eye(self.chi), (B, self.chi, self.chi))
                sol = I if sol is None else sol
                sag = I if sag is None else sag
                # ψ = Σ_{ij} G_k[i,j] · E[j,i] olacak şekilde çevre ``E``:
                #   halka  : ψ = Tr(sol·G·sag)      → E = sag·sol
                #   zincir : ψ = (sol·G·sag)[0,0]   → E[j,i] = sol[0,i]·sag[j,0]
                # İlk hâlde ikisi için de ``sag·sol`` yazmıştım; zincir kolu
                # bu yüzden yanlış çözülüyor ve mukayese geçersiz oluyordu
                # (halka 0,35'e karşı zincir 1,22 -- halkanın üstünlüğü
                # değil, zincirin bozukluğuydu).
                if self.halka:
                    E = np.einsum("bij,bjk->bik", sag, sol, optimize=True)
                else:
                    E = np.einsum("bj,bi->bji", sag[:, :, 0], sol[:, 0, :],
                                  optimize=True)
                # tasarım dizeyi: (B, (P+1)·χ·χ)
                A = np.einsum("bp,bji->bpij", Tb[:, k], E,
                              optimize=True).reshape(B, -1)
                M = A.T @ A + lam * np.eye(A.shape[1])
                c = np.linalg.solve(M, A.T @ y)
                self.C[k] = c.reshape(self.derece + 1, self.chi, self.chi)
                K[:, k] = np.einsum("bp,pij->bij", Tb[:, k], self.C[k],
                                    optimize=True)
            seyir.append(float(np.sqrt(np.mean((self.deger(t) - y) ** 2))))
        return seyir


# =====================================================================
def _gosterim() -> str:
    rng = np.random.default_rng(0)
    s = ["=== Polinomial Tensör Halkası (PTR) ==="]

    # --- 1. Halka mı zincir mi: DÖNGÜSEL bir hedefte mukayese
    n, chi, der = 6, 4, 6
    B = 900
    t = rng.uniform(-1, 1, size=(B, n))

    def hedef_donusel(t):
        # döngüsel bakışımlı: her değişken KOMŞUSUYLA çarpılır ve
        # SONUNCU ile BİRİNCİ de komşudur -- halkanın tam tarifi
        return sum(np.cos(2.0 * t[:, k]) * np.cos(2.0 * t[:, (k + 1) % n])
                   for k in range(n))

    def hedef_dogrusal(t):
        # uçları bağlı OLMAYAN hedef: zincir bunu da temsil edebilmeli
        return sum(np.cos(2.0 * t[:, k]) * np.cos(2.0 * t[:, k + 1])
                   for k in range(n - 1))

    s += ["", "1) Aynı χ ve derecede halka ile zincir (ALS, kapalı form):",
          "   hedef            temsil    parametre   RMSE (900 nokta)"]
    for ad, hf in (("döngüsel", hedef_donusel), ("uçları açık", hedef_dogrusal)):
        y = hf(t)
        y = (y - y.mean()) / (y.std() + 1e-12)
        for tur_ad, hlk in (("halka", True), ("zincir", False)):
            P = PolinomHalka(n, chi=chi, derece=der, tohum=1, halka=hlk)
            seyir = P.oturt(t, y, tur=12)
            s.append("   %-16s %-9s %-11d %.4f"
                     % (ad, tur_ad, len(P), seyir[-1]))

    # --- 2. Bellek: halka ne kadar sıkıştırıyor
    s += ["", "2) Bellek: açık tabloya karşı halka"]
    for n_ in (8, 16, 32, 64):
        H = TensorHalka(n_, d=2, chi=8, tohum=0)
        s.append("   n=%-3d  halka parametre = %-7d   açık tablo = 2^%d"
                 % (n_, len(H), n_))

    # --- 3. İz gerçekten çevrimi kapatıyor mu (sınama)
    H = TensorHalka(5, d=2, chi=3, tohum=2)
    X = rng.integers(0, 2, size=(7, 5))
    elle = []
    for x in X:
        M = np.eye(3)
        for k in range(5):
            M = M @ H.G[k][:, x[k], :]
        elle.append(np.trace(M))
    s += ["", "3) Yığın büzülmesi elle çarpımla aynı mı: âzamî fark %.2e"
          % float(np.abs(H.genlik(X) - np.array(elle)).max())]

    s += ["",
          "Hüküm ve KENDİ TAHMİNİMİN YANLIŞ ÇIKMASI: halkanın üstünlüğünü",
          "hedefin döngüselliğine bağlamıştım. Ölçüm bunu DOĞRULAMADI --",
          "halka her iki hedefte de (0,355 ve 0,341) zincirden (0,548 ve",
          "0,544) daha iyi. Demek ki kazanç dönemlilikten değil, uçların",
          "SERBESTLİĞİNDEN geliyor: zincirde uç vektörleri e₀'a sabitli,",
          "her iki uçta χ−1 boyut boşa gidiyor; halkada iz alındığı için",
          "öyle bir kayıp yok. Aynı parametre sayısında halkanın müessir",
          "sığası daha büyük. Dönemlilik faydası varsa bu ölçüm onu",
          "ayıramadı ve ayırdığı iddia edilmiyor.",
          "",
          "Çevrim bedeli duruyor: halkada kanonik hâl yoktur, onun için",
          "burası YÜZEY temsilidir; durum temsili ağaçtadır (H53)."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(_gosterim())
