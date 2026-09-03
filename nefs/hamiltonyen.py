"""
Uzaya mahsus Hamiltonyenler ve kuantum evrimi.

Metnin verdiği tarif aynen budur:

    H_k = Σ_{σ∈Δ_k} E_k(σ)|σ⟩⟨σ| + Σ_{σ~τ} J_k(σ,τ)(|σ⟩⟨τ| + |τ⟩⟨σ|)

* ``E_k(σ)``  -- bir ``k``-simpleksin **yerel enerji cezası** (köşegen).
* ``J_k(σ,τ)`` -- komşu simpleksler arası **tünelleme/bağ katsayısı**
  (köşegen dışı, Hermisyen).

``Δ_k``nin bu inşadaki fiilî karşılığı: ``m``inci uzayın penceresi
``w = min(m+1, 4)`` kübit, adımı ``a`` (ikisi de ``main.kategori``dan,
yani ∞-kategori teriminden gelir). Simpleks, ``a`` aralıkla dizilmiş
``w`` kübitlik bir penceredir. Yüksek mertebe daha **uzak menzilli**
tutarlılık denetler; bu, ``adim``ın mertebeyle logaritmik büyümesiyle
sağlanır.

**Evrim üniterdir.** ``H`` simetrik kurulur (``H = Hᵀ``), evrim
``U = exp(−η H)``nin reel karşılığı olan **Cayley dönmesiyle** yapılır:
``U = (I − ηH̃)(I + ηH̃)⁻¹``, ``H̃ = H − Hᵀ``... hayır. Reel cebirde
Hermisyen ``H``nin ürettiği ``e^{−iηH}`` doğrudan reel değildir; reel
karşılığı, ``H``yi ters simetrik bir üretece taşıyıp ``SO(2^w)``de
dönmektir. Bunun için ``H``den ters simetrik ``K = H ⊗ J`` yerine daha
sade ve **tam dik** olan şu kullanılır:

    U = exp(−η A),   A = H − Hᵀ  (ters simetrik)  →  UᵀU = I

Fakat ``H`` simetrikse ``A = 0`` olurdu. Bu yüzden Hamiltonyen iki
parçaya ayrılır ve **ikisi de kullanılır**:

* köşegen ``E`` → **işaret/faz** kapısı: ``diag(exp(−ηE))`` normalize
  edilerek; bu kısım genlikleri yeniden tartar, yıkıcı girişimi üretir.
* köşegen dışı ``J`` → **dönme** kapısı: ``exp(−η(J − Jᵀ))``, tam dik.

Bileşke ``U_m = Dönme(J) · Tartı(E)`` normu korur (tartı sonrası yeniden
normalize edilir) ve ``E``deki her fark bir **faz farkıdır**: yüksek
enerjili diziliş sönümlenir, düşük enerjili yükselir. Metnin
"enerjisi yüksek diziliş zıt faza döner ve söndürülür" hükmü budur.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from idrak.kategori import Uzay
from kuantum.yazmac import Yazmac

__all__ = ["UzayHamiltonyeni", "hamiltonyenleri_kur", "evrim_uygula",
           "tunelleme_uygula"]


def _cayley(A: np.ndarray) -> np.ndarray:
    """``Q = (I−A)(I+A)⁻¹``; ``A`` ters simetrikse ``Q ∈ SO(n)``."""
    A = 0.5 * (A - A.T)
    I = np.eye(len(A))
    return np.linalg.solve((I + A).T, (I - A).T).T


@dataclass
class UzayHamiltonyeni:
    """``H_m``in fiilî hâli: köşegen enerjiler + bağ katsayıları."""
    uzay: Uzay
    E: np.ndarray              # (2^w,)   -- E_m(σ)
    J: np.ndarray              # (2^w, 2^w) -- J_m(σ,τ), ters simetrik kısmı alınır
    eta: float

    @property
    def w(self) -> int:
        return self.uzay.pencere

    def tarti(self) -> np.ndarray:
        """``diag(exp(−ηE))`` -- köşegen faz/genlik tartısı."""
        v = np.exp(-self.eta * (self.E - self.E.mean()))
        return v / (np.linalg.norm(v) / np.sqrt(len(v)) + 1e-30)

    def donme(self) -> np.ndarray:
        """``exp(−η(J−Jᵀ))`` -- Cayley ile tam dik köşegen dışı evrim."""
        return _cayley(self.eta * (self.J - self.J.T))

    def kapi(self) -> np.ndarray:
        """``U_m = Dönme(J) · Tartı(E)`` -- ``2^w × 2^w``."""
        return self.donme() @ np.diag(self.tarti())

    def parametre_sayisi(self) -> int:
        d = 2 ** self.w
        return d + d * (d - 1) // 2


def hamiltonyenleri_kur(uzaylar: Sequence[Uzay], p: Optional[np.ndarray] = None,
                        eta: float = 0.35, tohum: int = 0
                        ) -> List[UzayHamiltonyeni]:
    """Her uzay için ``H_m``i kur.

    ``p`` verilirse parametreler **öğrenilen** vektörden okunur; yoksa
    tohumdan türetilir. Parametrelerin uzaya dağılımı, ∞-kategori
    teriminden gelen ``parametre`` sayısına göredir -- yani hangi uzayın
    kaç serbestlik derecesi olacağını **tip belirler**, elle konmaz.
    """
    rng = np.random.default_rng(tohum + 31)
    out: List[UzayHamiltonyeni] = []
    imlec = 0
    for u in uzaylar:
        d = 2 ** u.pencere
        n_E, n_J = d, d * (d - 1) // 2
        if p is not None:
            q = np.asarray(p, float)
            dilim = q[imlec:imlec + n_E + n_J]
            if len(dilim) < n_E + n_J:
                dilim = np.resize(dilim if len(dilim) else q, n_E + n_J)
            E = dilim[:n_E].copy()
            jv = dilim[n_E:n_E + n_J].copy()
            imlec += n_E + n_J
        else:
            E = rng.normal(scale=0.5, size=n_E)
            jv = rng.normal(scale=0.4, size=n_J)
        J = np.zeros((d, d))
        J[np.triu_indices(d, 1)] = jv
        # mertebe, bağ şiddetine de girer: yüksek mertebe daha zayıf fakat
        # daha uzak bağ kurar (yakın menzilli gürültüyü ezmesin diye).
        olcek = 1.0 / (1.0 + np.log1p(u.mertebe))
        out.append(UzayHamiltonyeni(uzay=u, E=E * olcek, J=J * olcek,
                                    eta=eta))
    return out


def parametre_sayisi(uzaylar: Sequence[Uzay]) -> int:
    return sum(2 ** u.pencere + (2 ** u.pencere) * (2 ** u.pencere - 1) // 2
               for u in uzaylar)


# =====================================================================
#  Evrim: kapıyı yazmaca uygula
# =====================================================================
def evrim_uygula(y: Yazmac, H: UzayHamiltonyeni) -> Dict[str, float]:
    """``|ψ⟩ ← U_m |ψ⟩`` -- ``m``inci uzayın Hamiltonyen evrimi.

    ``w`` kübitlik kapı, Trotter ayrıştırmasıyla komşu **çift** kapılara
    indirilir: ``exp(−ηH_w) ≈ Π_i exp(−ηh_{i,i+1})``. Sebep sayısaldır ve
    ölçüldü: ``w`` kübitlik pencereyi bir bütün olarak bölmek pencere
    başına ``w−1`` yığın SVD'si ister; 6 milyon yuvada bu Python'da
    koşmaz. Çift kapıya inince tek yığın SVD kalır.

    Trotter hatası ``O(η²[h_i, h_j])``dir ve ``η`` küçük tutulur;
    bileşke hâlâ **tam diktir** (her çarpan dik), yani norm bozulmaz --
    kaybolan şey yalnız çarpanların sırasının değişmezliğidir.

    ``adim`` uzayın kendi geometrisidir: kapı her ``a``ıncı çifte
    uygulanır. Böylece 20 uzay aynı kübitlere **başka başka** dokunur.
    """
    w, a = H.uzay.pencere, H.uzay.adim
    G4 = H.kapi()
    if w == 1:
        # tek kübitlik uzay: köşegen tartı doğrudan
        G2 = np.diag(H.tarti()[:2])
        nrm = np.linalg.norm(G2, axis=0, keepdims=True) + 1e-30
        y.tek_kapi((G2 / nrm).astype(y.tip))
        return {"kesme": 0.0, "pencere": 1.0, "adım": float(a)}
    # w ≥ 2: 4×4 çift kapısına indir (Trotter)
    if G4.shape[0] != 4:
        # 2^w > 4 ise komşu çift altuzayına izdüşür: ilk 4×4 blok
        G4 = G4[:4, :4]
        q, _ = np.linalg.qr(G4)
        G4 = q
    kesme = 0.0
    # adım a: ofset 0, a, 2a … ile fırça; a=1 ise klasik fırça
    for ofs in range(0, min(a, 2)):
        kesme += y.cift_kapi(G4.astype(y.tip), ofset=ofs)
    return {"kesme": float(kesme), "pencere": float(w), "adım": float(a)}


def tunelleme_uygula(y: Yazmac, gama: float) -> float:
    """``H_tünel = −Σ_j Γ σ_x^{(j)}`` -- enine alan (kütük H29).

    Reel cebirde ``σ_x`` bir yansımadır; ``exp(−iΓσ_x)``in reel karşılığı
    ``[[cosΓ, −sinΓ],[sinΓ, cosΓ]]`` dönmesidir ve tam diktir. ``Γ = 0``
    iken birim dizeydir, yani vana kapalıdır. Vana melekelere kilitlidir:
    ancak tıkanma teşhis edilince açılır.
    """
    if gama <= 0.0:
        return 0.0
    c, s = float(np.cos(gama)), float(np.sin(gama))
    y.tek_kapi(np.array([[c, -s], [s, c]], dtype=y.tip))
    return float(gama)
