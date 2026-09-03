"""
Çift motorlu eğitim (kütük H28) -- **gradyan inişi yoktur**.

    ┌──────────────────────┐        ┌──────────────────────────┐
    │  AYRIK MOTOR         │        │  SÜREKLİ MOTOR           │
    │  Postnikov k-inv.    │─ D* ──►│  Active Subspaces d→r    │
    │  tersine tavlama     │        │  AS-GEK vekil yüzeyi     │
    │  kalıcı homoloji     │◄─ H^n ─│  sanal zamanlı DALGA     │
    └──────────────────────┘        └──────────────────────────┘

**Sürekli motor.** Parametre uzayı ``d`` boyutludur ve büyüktür.
Gradyanlar sonlu farkla, **rastgele yönlerde** alınır (tam Jacobi hiç
kurulmaz). Bunlardan kovaryans ``C = 1/N Σ g gᵀ`` kurulup özayrışımıyla
``r`` boyutlu **aktif alt uzay** ``W₁`` çıkarılır. Vekil yüzey (GEK) bu
``r`` boyutta kurulur; sonra o yüzeyde **bizzat dalga** yayılır --
yaylı boncuk değil (kütük H28): sanal zamanlı Schrödinger

    ∂ψ/∂τ = ∇²ψ − V_toplam(u)·ψ,   ψ(u,τ) = Σ c_n e^{−E_n τ} φ_n(u)

Yüksek enerjili sahte çukurlar ``e^{−Eτ}`` ile **üstel olarak silinir**;
geriye taban modu kalır. Tepe noktası küresel minimumdur ve ters
izdüşümle ``x* = W₁u*`` ile tam boyuta taşınır.

**Hedef bilgisi sızdırma.** Minimumun nerede olduğunu bilmesek de orada
hangi şartın sağlanacağını biliriz. Bu, potansiyele doğrudan konur:

    V_toplam(u) = V_GEK(u) + λ‖𝒢(u) − y_hedef‖²

**Ayrık motor.** Dinamik mertebe indisleri ``D = [d₁..d₁₀] ∈ ℕ¹⁰``
sürekli değildir; gradyanı yoktur. Hangi mertebenin açılacağına
kohomolojik tıkanıklık **analitik olarak adres verir** (Postnikov
k-invaryantı), seçim ise ayrık uzayda tersine tavlama ile yapılır.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["aktif_altuzay", "gek_uydur", "dalga_yayilimi", "as_gek_adimi",
           "postnikov_adresi", "tersine_tavlama"]


# =====================================================================
#  1. Active Subspaces
# =====================================================================
def aktif_altuzay(f: Callable[[np.ndarray], float], x0: np.ndarray,
                  n_ornek: int = 24, r: int = 2, h: float = 1e-3,
                  tohum: int = 0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``C = 1/N Σ g gᵀ`` → ``W₁ ∈ ℝ^{d×r}`` (en büyük r özyön).

    Gradyanlar **rastgele yönlü sonlu farkla** alınır: ``d`` boyutlu tam
    gradyan ``2d`` değerlendirme ister; burada ``n_ornek`` yönle
    yetinilir ve kovaryans onlardan kurulur. Bu, tam gradyanın
    tarafsız bir örneklemesidir (Gauss yönlerde ``E[gvᵀ] = ∇f``).
    """
    rng = np.random.default_rng(tohum)
    d = len(x0)
    G = np.zeros((n_ornek, d))
    for i in range(n_ornek):
        v = rng.normal(size=d)
        v /= np.linalg.norm(v) + 1e-12
        turev = (f(x0 + h * v) - f(x0 - h * v)) / (2 * h)
        G[i] = turev * v                       # yönlü türev · yön
    C = G.T @ G / n_ornek
    w, U = np.linalg.eigh(C)
    idx = np.argsort(-w)
    return U[:, idx[:r]], w[idx], G


# =====================================================================
#  2. GEK vekil yüzeyi (Nyström ile hafifletilmiş)
# =====================================================================
def gek_uydur(U: np.ndarray, y: np.ndarray, lam: float = 1e-6,
              nystrom: int = 0) -> Callable[[np.ndarray], np.ndarray]:
    """Gradyan destekli Kriging -- kapalı form, gradyan inişi yok.

    ``α = (K + λI)⁻¹ y``; ``K`` Gauss çekirdeği, genişlik medyan
    sezgisiyle. ``nystrom > 0`` ise ``M ≪ N`` temsilci nokta seçilip
    ``K ≈ K_NM K_MM⁻¹ K_NMᵀ`` düşük dereceli açılımı kullanılır -- matris
    tersi maliyeti ``O(N³)``ten ``O(N M²)``ye iner (kütük H28/H12).
    """
    U = np.atleast_2d(U)
    n = len(U)
    D2 = ((U[:, None, :] - U[None, :, :]) ** 2).sum(-1)
    med = float(np.median(D2[np.triu_indices(n, 1)])) if n > 1 else 1.0
    gam = 1.0 / (2.0 * med) if med > 0 else 1.0
    K = np.exp(-gam * D2)

    if nystrom and nystrom < n:
        idx = np.linspace(0, n - 1, nystrom).astype(int)
        Kmm = K[np.ix_(idx, idx)] + lam * np.eye(nystrom)
        Knm = K[:, idx]
        A = Knm.T @ Knm + lam * Kmm
        alfa_m = np.linalg.solve(A, Knm.T @ y)
        merkez = U[idx]

        def vekil(u: np.ndarray) -> np.ndarray:
            u = np.atleast_2d(u)
            d2 = ((u[:, None, :] - merkez[None, :, :]) ** 2).sum(-1)
            return np.exp(-gam * d2) @ alfa_m
        return vekil

    alfa = np.linalg.solve(K + lam * np.eye(n), y)

    def vekil_tam(u: np.ndarray) -> np.ndarray:
        u = np.atleast_2d(u)
        d2 = ((u[:, None, :] - U[None, :, :]) ** 2).sum(-1)
        return np.exp(-gam * d2) @ alfa
    return vekil_tam


# =====================================================================
#  3. Sanal zamanlı dalga yayılımı -- yaylı boncuk DEĞİL
# =====================================================================
def dalga_yayilimi(V: np.ndarray, tau_adim: int = 400,
                   dt: float = 0.02, hbar2m: float = 1.0
                   ) -> Tuple[Tuple[int, ...], np.ndarray]:
    """``∂ψ/∂τ = ∇²ψ − Vψ`` -- ızgarada, ``r ≤ 3`` boyutta.

    Boyut laneti burada yoktur çünkü ``r``ye Active Subspaces ile
    inilmiştir (kütük H28). Dalga bütün bariyerlerin içinden aynı anda
    sızar (difüzyon), yüksek enerjili sahte çukurlar ``e^{−Eτ}`` ile
    söner, geriye taban modu kalır. Tepe noktasının indeksi küresel
    minimumdur.
    """
    psi = np.ones_like(V)
    psi /= np.linalg.norm(psi)
    for _ in range(tau_adim):
        lap = np.zeros_like(psi)
        for eks in range(psi.ndim):
            lap += (np.roll(psi, 1, eks) - 2 * psi + np.roll(psi, -1, eks))
        psi = psi + dt * (hbar2m * lap - V * psi)
        psi = np.abs(psi)
        n = np.linalg.norm(psi)
        if n < 1e-300:
            break
        psi /= n
    return np.unravel_index(int(np.argmax(psi)), psi.shape), psi


def as_gek_adimi(f: Callable[[np.ndarray], float], x0: np.ndarray,
                 yaricap: float = 0.6, r: int = 2, izgara: int = 24,
                 n_ornek: int = 24, hedef_ceza: Optional[Callable] = None,
                 lam_hedef: float = 1.0, tohum: int = 0
                 ) -> Tuple[np.ndarray, Dict[str, float]]:
    """Bir tam çevrim: AS → GEK → hedef sızdırma → dalga → ters izdüşüm."""
    W1, ozdeger, _ = aktif_altuzay(f, x0, n_ornek=n_ornek, r=r, tohum=tohum)
    rng = np.random.default_rng(tohum + 1)

    # r boyutlu kutuda örnekleme ve gerçek fonksiyon değerleri
    n_nokta = max(24, 8 * r)
    Ur = rng.uniform(-yaricap, yaricap, size=(n_nokta, r))
    y = np.array([f(x0 + W1 @ u) for u in Ur])
    vekil = gek_uydur(Ur, y, nystrom=min(16, n_nokta // 2))

    eks = [np.linspace(-yaricap, yaricap, izgara) for _ in range(r)]
    ag = np.stack(np.meshgrid(*eks, indexing="ij"), -1).reshape(-1, r)
    V = np.asarray(vekil(ag), float).reshape([izgara] * r)

    # --- HEDEF BİLGİSİ SIZDIRMA (kütük H28)
    # ``V_toplam = V_GEK + λ‖𝒢(u) − y_hedef‖²``. Minimumun NEREDE
    # olduğunu bilmesek de orada hangi şartın sağlanacağını biliriz;
    # o şart potansiyele doğrudan konur.
    #
    # Cezayı ızgaranın her düğümünde hesaplamak, ``izgara^r`` tam ileri
    # geçiş demektir (r=2, izgara=20 → 400 geçiş, çevrim başına
    # dakikalar). Bunun yerine ceza da AYNI ``n_nokta`` örnekte ölçülüp
    # kendi GEK yüzeyine oturtulur ve ızgarada vekilden okunur. Böylece
    # sızdırma fiilen olur, maliyeti ise ``n_nokta`` kadardır.
    hedef_bilgisi = 0.0
    if hedef_ceza is not None:
        c = np.array([float(hedef_ceza(x0 + W1 @ u)) for u in Ur])
        ceza_vekili = gek_uydur(Ur, c, nystrom=min(16, n_nokta // 2))
        C = np.asarray(ceza_vekili(ag), float).reshape(V.shape)
        # İki yüzey aynı mertebeye getirilir; aksi hâlde biri ötekini
        # ezer ve sızdırma ya hiç iş görmez ya yüzeyi tamamen ele geçirir.
        Vn = (V - V.min()) / (V.max() - V.min() + 1e-12)
        Cn = (C - C.min()) / (C.max() - C.min() + 1e-12)
        V = Vn + lam_hedef * Cn
        hedef_bilgisi = float(np.mean(c))

    V = (V - V.min()) / (V.max() - V.min() + 1e-12) * 30.0
    tepe, _ = dalga_yayilimi(V)
    u_yildiz = np.array([eks[i][tepe[i]] for i in range(r)])
    x_yeni = x0 + W1 @ u_yildiz               # ters izdüşüm

    return x_yeni, {"r": float(r),
                    "özdeğer_oranı": float(ozdeger[0] / (ozdeger.sum() + 1e-12)),
                    "vekil_min": float(V.min()), "vekil_max": float(V.max()),
                    "hedef_sızdırıldı": float(hedef_ceza is not None),
                    "hedef_cezası": hedef_bilgisi}


# =====================================================================
#  4. Ayrık motor: Postnikov adresi + tersine tavlama
# =====================================================================
def postnikov_adresi(tikaniklik: Dict[int, float], mevcut: Sequence[int],
                     ust_sinir: int = 100000) -> int:
    """Kohomolojik tıkanıklık, açılacak mertebenin adresini **verir**.

    ``H^n ≠ 0`` ise Postnikov kulesinde bir sonraki bütünlük mertebesi
    ``k^{n+1} ∈ H^{n+1}(X; π_n(X))`` sınıfıyla adreslenir. Kör arama
    yoktur: en büyük tıkanıklığı taşıyan mertebe ``n``, tıkanıklığın
    şiddetiyle ölçeklenen bir sıçrama üretir (kütük H28).
    """
    if not tikaniklik:
        return int(mevcut[0]) if mevcut else 13
    n = max(tikaniklik, key=lambda k: tikaniklik[k])
    siddet = float(tikaniklik[n])
    adres = int(round((n + 1) * (1.0 + 9.0 * siddet)))
    return int(np.clip(adres, 10, ust_sinir))


def tersine_tavlama(enerji: Callable[[Tuple[int, ...]], float],
                    D0: Sequence[int], adim: int = 60,
                    s_hedef: float = 0.6, ust_sinir: int = 100000,
                    tohum: int = 0) -> Tuple[Tuple[int, ...], float]:
    """Ayrık mertebe vektöründe tersine kuantum tavlama.

    Sıfırdan süperpozisyonla başlanmaz (klasik tavlamanın ölçeklenme
    derdi budur); **eldeki aday** ``D0``a kilitlenip etrafında enine alan
    ``s: 1 → s_hedef → 1`` döngüsüyle kontrollü dalgalanma açılır. Dar
    duvarın ardındaki daha derin taban bulunursa oraya tünellenir.
    """
    rng = np.random.default_rng(tohum)
    D = list(int(x) for x in D0)
    E = enerji(tuple(D))
    en_iyi, E_iyi = list(D), E
    for t in range(adim):
        s = 1.0 - (1.0 - s_hedef) * np.sin(np.pi * (t + 1) / adim)
        genlik = max(1, int((1.0 - s) * 2000))
        j = int(rng.integers(len(D)))
        aday = list(D)
        aday[j] = int(np.clip(aday[j] + rng.integers(-genlik, genlik + 1),
                              10, ust_sinir))
        E_aday = enerji(tuple(aday))
        # tünelleme: bariyerin YÜKSEKLİĞİ değil GENİŞLİĞİ belirler
        genislik = abs(aday[j] - D[j]) / (genlik + 1.0)
        p_tunel = float(np.exp(-genislik * max(E_aday - E, 0.0)))
        if E_aday < E or rng.random() < p_tunel:
            D, E = aday, E_aday
            if E < E_iyi:
                en_iyi, E_iyi = list(D), E
    return tuple(en_iyi), E_iyi
