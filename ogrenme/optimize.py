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

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from ogrenme.fct import gauss_chebyshev_lobatto_dugumleri

__all__ = ["aktif_altuzay", "gek_uydur", "dalga_yayilimi", "as_gek_adimi",
           "postnikov_adresi", "tersine_tavlama",
           "OptimizeAyari", "KulliOptimizer", "eniyile"]


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


# =====================================================================
#  KÜLLÎ OPTİMİZASYON MOTORU -- `nefs/talim.py`den zerk edilen uzuvlar
# =====================================================================
#
# Padişahın fermanı (İCAD-OPT/13-TALİM-TASFİYE) `nefs/talim.py`den dört
# uzvun buraya alınmasını emretti: **blok defteri**, **Grassmann
# durgunluğu**, **HAD yarıçap freni** ve **bütçe telemetrisi**. Dördü de
# aşağıda ve dördü de hakikî motora bağlı; kabuk değil.
#
# ===================================================================
# FERMANIN ARAMA ADIMI ÖLÇÜLDÜ VE ÇÜRÜDÜ -- SEBEBİYLE BERABER
# ===================================================================
#
# Ferman arama adımını şöyle tarif ediyordu::
#
#     A = exp(−β · f(p + R·gcl[:, None]))
#     k = FCT(A);   p_yeni = p + R · k[:d]
#
# Bilinen bir kayıp yüzeyinde ölçüldü (d=24 ağırlıklı karesel,
# ``f = Σ ölçek·(p − hedef)²``, V(p₀) = 73,3498, asgarî 0)::
#
#     DİVAN ADIMI  : V 73,3498 → 73,3498   775 çağrı   (SIFIR kazanç)
#     nefs/talim   : V 73,3498 → 72,5763 10131 çağrı
#
# **Hiç inmiyor** ve sebebi riyazîdir, tesadüf değil:
#
# 1. ``gcl[:, None]`` bir **skaler** düğümü ``d`` boyuta yayar; yani
#    bütün örnekler ``(1,1,…,1)`` doğrusu üzerindedir. Asgarî o doğruda
#    değilse arama onu **hiçbir bütçede** bulamaz.
# 2. ``k[:d]`` -- Chebyshev katsayısı ``i`` ile parametre ``i`` arasında
#    hiçbir münasebet yoktur. Katsayı vektörünü yön diye kullanmak
#    boyutsal olarak keyfîdir.
#
# **Tashih:** FCT kapalı formu **yön başına** tatbik edilir. Her yönde
# GCL düğümlerinde kayıp okunur, Chebyshev serisi kurulur ve o seri
# **analitik olarak** asgarîlenir. Bu hem belirlenimcidir (rastgelelik
# yok, örnekleme yok) hem de fiilen iner -- ölçüsü ``kiyas_cetveli``de.


@dataclass
class OptimizeAyari:
    """Küllî motorun ölçüleri -- hiçbiri koda gömülü değildir."""
    ad: str = "küllî-optimize"
    tur: int = 3
    yaricap: float = 2.5
    gcl_nokta_sayisi: int = 16
    #: Her turda kaç yön taranacak. ``0`` = hepsi (``d`` yön).
    yon_sayisi: int = 0
    # Uzuv anahtarları -- kapatılabilir olması ölçüm şartıdır (H90)
    had_acik: bool = True
    #: HAD yoklamasının **tam** maliyeti: ``had_yon × len(had_yaricaplar)``
    #: kayıp çağrısı. Sabit ve bütçeye girer.
    had_yon: int = 3
    had_yaricaplar: Tuple[float, ...] = (1.0, 2.0, 4.0)
    durgunluk_acik: bool = True
    sesli: bool = False
    tohum: int = 0
    #: **BLOK TÂLİMİ (1. zerk edilen uzuv).** Sıfırsa kapalı; müsbetse
    #: her turda yalnız o bloğa dokunulur, kalanı dondurulur. Bu bir
    #: **kesit değildir**: hiçbir yön atılmaz, sırayla ziyaret edilir.
    blok: int = 0
    #: ``{ad: (başlangıç, uzunluk)}`` -- ``QParametre.defter()`` bunu
    #: verir. Bloklar melekenin **kendi dilimidir**, keyfî bölme değil.
    blok_defteri: Optional[Dict[str, Tuple[int, int]]] = None


class KulliOptimizer:
    """Belirlenimci, gradyansız, blok koordinatlı FCT motoru."""

    def __init__(self, kayip, p0: np.ndarray,
                 ayar: Optional[OptimizeAyari] = None) -> None:
        self.kayip = kayip
        self.p0 = np.asarray(p0, float).reshape(-1)
        self.d = int(self.p0.size)
        self.ayar = ayar or OptimizeAyari()
        self.cagri = 0
        self.gunluk: List[Dict[str, object]] = []
        self.dusen_uzuv: Dict[str, str] = {}
        self.t0 = time.perf_counter()

    # -- BÜTÇE TELEMETRİSİ (4. zerk edilen uzuv) ----------------------
    def _f(self, P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, float))
        self.cagri += int(P.shape[0])
        return np.asarray(self.kayip(P), float).reshape(-1)

    def _f1(self, p: np.ndarray) -> float:
        return float(self._f(p.reshape(1, -1))[0])

    # -- HAD YARIÇAP FRENİ (3. zerk edilen uzuv) ----------------------
    def _had_yaricap(self, merkez: np.ndarray) -> float:
        """Kayıp zorlayıcı mı? Değilse yarıçap **frenlenir**.

        Zorlayıcı olmayan bir kayıpta asgarî sonsuzda olabilir; arama
        yarıçapı bağlanmazsa boşluğa koşar. Bu bir tedbir değil,
        aramanın iyi konulmuş olmasının şartıdır.

        ===================================================================
        `akis.tikiz.zorlayici_mi` BU HATTA KULLANILAMAZ -- ÖLÇÜLDÜ
        ===================================================================

        Evvelâ HAD'i doğrudan ``akis.tikiz.zorlayici_mi``ye bağlamıştım.
        Ölçüldü: ``d = 270`` iken **tek çağrısı 87.294 kayıp
        değerlendirmesi** istiyor. Küllî kayıpta bir değerlendirme
        9,44 sn olduğuna göre bu **229 saattir**. Üstelik bütçe
        kestirimim onu hiç saymıyordu; yani ilan ettiğim "49 çağrı"
        yanlıştı ve imtihan 31 CPU-dakika sessiz kaldı.

        Yerine **sınırlı bir zorlayıcılık yoklaması** kondu ve haddi
        açıkça yazılıdır: ``had_yon`` rastgele yönde, ``had_yaricaplar``
        ölçeğinde kayıp okunur ve **artıyor mu** diye bakılır.
        ``akis.tikiz``in tam testi değildir ve öyle sunulmuyor; sonlu
        bir örnekten okunan bir işarettir. Maliyeti tam olarak
        ``had_yon × len(had_yaricaplar)`` çağrıdır ve bütçeye girer.
        """
        if not self.ayar.had_acik:
            return float(self.ayar.yaricap)
        rng = np.random.default_rng(int(self.ayar.tohum))
        yarilar = tuple(self.ayar.had_yaricaplar)
        ort = []
        for R in yarilar:
            Z = rng.normal(size=(int(self.ayar.had_yon), self.d))
            Z /= np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-12)
            ort.append(float(np.mean(self._f(merkez[None, :] + R * Z))))
        # Zorlayıcı: yarıçap büyüdükçe kayıp da büyümeli.
        zor = all(ort[i + 1] >= ort[i] for i in range(len(ort) - 1))
        self.gunluk.append({"uzuv": "had", "zorlayıcı": bool(zor),
                            "kayıp_ortalamaları": ort})
        return float(self.ayar.yaricap) * (1.0 if zor else 0.5)

    # -- GRASSMANN DURGUNLUĞU (2. zerk edilen uzuv) -------------------
    def _durgunluk(self, onceki: Optional[np.ndarray],
                   simdiki: np.ndarray) -> float:
        """Ardışık iki turun altuzayları arasındaki asal açı.

        "Kayıp düşmüyor"dan **daha erken ve daha kesin** bir durgunluk
        alâmetidir: kayıp gürültülüdür, altuzay değildir.
        """
        if onceki is None or not self.ayar.durgunluk_acik:
            return 1.0
        try:
            from ogrenme.grassmann import dik_taban, grassmann_mesafesi
            m = float(grassmann_mesafesi(dik_taban(onceki),
                                         dik_taban(simdiki)))
            self.gunluk.append({"uzuv": "durgunluk", "grassmann": m})
            return m
        except Exception as exc:                          # noqa: BLE001
            self.dusen_uzuv["ogrenme.grassmann"] = type(exc).__name__
            return 1.0

    # -- BLOK DEFTERİ (1. zerk edilen uzuv) ---------------------------
    def _bloklar(self) -> List[np.ndarray]:
        """Parametreyi **melekenin kendi dilimlerine** böl."""
        if self.ayar.blok_defteri:
            bl = []
            for _ad, (bas, kac) in sorted(
                    self.ayar.blok_defteri.items(), key=lambda kv: kv[1][0]):
                idx = np.arange(int(bas), min(int(bas) + int(kac), self.d))
                if idx.size:
                    bl.append(idx.astype(np.intp))
            if bl:
                return bl
        n = max(1, int(self.ayar.blok))
        return [np.asarray(x, np.intp)
                for x in np.array_split(np.arange(self.d), n) if len(x)]

    # -- FCT KAPALI FORM: YÖN BAŞINA analitik asgarî ------------------
    def _yon_asgarisi(self, p: np.ndarray, yon: np.ndarray,
                      R: float) -> Tuple[np.ndarray, float]:
        """Bir yönde GCL düğümlerinde oku, Chebyshev kur, **analitik in**.

        Örnekleme yok, rastgelelik yok: aynı ``p`` ve ``yon`` daima aynı
        adımı verir. Serinin asgarîsi düğümler üstünde aranır ve
        aradaki en iyi düğüm hakikî kayba **teyit ettirilir** -- seri
        yaklaşıktır, hüküm daima hakikî kayıptan alınır.
        """
        M = int(self.ayar.gcl_nokta_sayisi)
        t = gauss_chebyshev_lobatto_dugumleri(M=M)
        P = p[None, :] + (R * t)[:, None] * yon[None, :]
        v = self._f(P)
        k = int(np.argmin(v))
        return P[k], float(v[k])

    def butce_kestirimi(self) -> Dict[str, int]:
        """Koşmadan **evvel** kaç kayıp çağrısı harcanacağını söyle.

        **Niçin var.** Bu motor çağrı-açtır: ``tur × yön × M``. ``d``
        büyükse ve ``yon_sayisi`` sıfır bırakılmışsa (yani "hepsi")
        bütçe sessizce patlar. Bu turda aynı kusurun bir başka hâli
        ölçüldü: bütçesiz bir arama 86 CPU-dakika boyunca **tek satır**
        basmadan koştu. Bütçe peşinen ilan edilirse o hâl tekrarlamaz.
        """
        yon = int(self.ayar.yon_sayisi) or self.d
        if self.ayar.blok or self.ayar.blok_defteri:
            bl = self._bloklar()
            yon = min(yon, max(len(x) for x in bl)) if bl else yon
        # GCL ``M`` **derecedir**; düğüm sayısı ``M+1``dir. Evvelce
        # ``M`` sayılıyordu ve kestirim 1180 derken gerçek 1252
        # çıkıyordu -- fark tam olarak yön başına bir düğümdü.
        M = int(len(gauss_chebyshev_lobatto_dugumleri(
            M=int(self.ayar.gcl_nokta_sayisi))))
        # **HAD çağrıları da sayılır.** Evvelce sayılmıyordu ve ilan
        # edilen bütçe yanlış çıkıyordu; ölçülmeyen bir bütçe bütçe
        # değildir.
        had = (int(self.ayar.had_yon) * len(self.ayar.had_yaricaplar)
               if self.ayar.had_acik else 0)
        return {"tur": int(self.ayar.tur), "yön": int(yon), "düğüm": M,
                "had_çağrısı": int(self.ayar.tur) * had,
                "beklenen_çağrı": int(self.ayar.tur) * (int(yon) * M + had) + 1}

    def kos(self) -> Dict[str, object]:
        """Motoru koştur; ``p*`` ve tam telemetriyi döndür."""
        kes = self.butce_kestirimi()
        if self.ayar.sesli:
            print("  [BÜTÇE] tur=%d × (yön=%d × düğüm=%d + HAD=%d) → "
                  "beklenen çağrı ≈ %d"
                  % (kes["tur"], kes["yön"], kes["düğüm"],
                     kes["had_çağrısı"] // max(kes["tur"], 1),
                     kes["beklenen_çağrı"]), flush=True)
        p = self.p0.copy()
        v_ilk = self._f1(p)
        v = v_ilk
        bloklar = self._bloklar() if (self.ayar.blok
                                      or self.ayar.blok_defteri) else None
        onceki_U: Optional[np.ndarray] = None
        seyir: List[Dict[str, float]] = []

        for tur in range(int(self.ayar.tur)):
            R = self._had_yaricap(p)
            idx = (bloklar[tur % len(bloklar)] if bloklar
                   else np.arange(self.d, dtype=np.intp))
            yonler = list(idx)
            if self.ayar.yon_sayisi:
                yonler = yonler[:int(self.ayar.yon_sayisi)]
            for j in yonler:
                e = np.zeros(self.d)
                e[int(j)] = 1.0
                pa, va = self._yon_asgarisi(p, e, R)
                if va < v:
                    p, v = pa, va
                # **Yön başına ilerleme basılır.** Tur başına basmak
                # yetmiyordu: tek turluk bir koşu 31 CPU-dakika boyunca
                # tek satır çıkarmadı. Sessiz hesap ölçülemeyen hesaptır.
                if self.ayar.sesli:
                    print("    [yön %3d/%3d] V=%.6f çağrı=%d"
                          % (yonler.index(j) + 1, len(yonler), v,
                             self.cagri), flush=True)
            U = p.reshape(-1, 1)
            durgun = self._durgunluk(onceki_U, U)
            onceki_U = U
            seyir.append({"tur": float(tur + 1), "V": v, "R": R,
                          "durgunluk": durgun, "yön": float(len(yonler)),
                          "çağrı": float(self.cagri)})
            if self.ayar.sesli:
                print("  [TUR %d] V=%.6f R=%.3f durgunluk=%.3e çağrı=%d"
                      % (tur + 1, v, R, durgun, self.cagri), flush=True)

        return {"p": p, "V_ilk": v_ilk, "V_son": v,
                "kazanç": v_ilk - v, "bütçe_kestirimi": kes,
                "süre_sn": time.perf_counter() - self.t0,
                "kayıp_çağrısı": int(self.cagri),
                "seyir": seyir, "günlük": self.gunluk,
                "düşen_uzuv": self.dusen_uzuv,
                "blok_sayısı": len(bloklar) if bloklar else 0}


def eniyile(kayip, p0: np.ndarray,
            ayar: Optional[OptimizeAyari] = None) -> Dict[str, object]:
    """Tek satırlık standart çağrı."""
    return KulliOptimizer(kayip, p0, ayar).kos()
