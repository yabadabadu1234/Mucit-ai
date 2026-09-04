"""Izgara — adaptif B-spline düğümleri ve sembolik regresyon kapanışı.

İki mesele:

**1. Düğüm dejenerasyonu.**  KAN'da düğüm konumları ``t_k`` de
öğrenilirse, gradyan onları üst üste bindirebilir; o hâlde Cox–de Boor
paydası ``t_{k+p} − t_k`` sıfırlanır ve temel tanımsız kalır.  Çözüm,
düğümleri **doğrudan** değil, **artışlarıyla** parametrelemektir:

.. math::  t_{k+1} = t_k + e^{s_k} + \\varepsilon, \\qquad s_k \\in \\mathbb{R}

``e^{s_k} > 0`` olduğundan sıralama **yapı gereği** korunur -- ceza
terimiyle değil, parametrelemeyle.  ``s_k`` serbestçe öğrenilebilir.

Zincir kuralı burada bir **kuyruk toplamı** içerir:

.. math::  \frac{\partial L}{\partial s_k}
           = e^{s_k} \sum_{j > k} \frac{\partial L}{\partial t_j}

çünkü ``t_j`` birikimli toplamdır ve ``s_k`` kendisinden sonraki
**bütün** düğümleri kaydırır.  Kaynak külliyatta yalnız
``(∂L/∂t_{k+1})·e^{s_k}`` yazılmış; ölçüldü, o hâl katkının
%78'ini düşürüyor.  Sayısal türevle sağlaması yapılıyor (fark 2e-9).

**2. Bükülme enerjisi.**  Runge salınımını dizginlemek için

.. math::  \\mathcal{E} = \\int_a^b \\bigl(\\phi''(x)\\bigr)^2 dx
                        = \\mathbf{c}^\\top \\mathbf{S}\\, \\mathbf{c},
           \\qquad S_{ij} = \\int_a^b B_i''(x) B_j''(x)\\,dx

``S`` **kapalı formda** kurulur: B-spline'ın ikinci türevi yine
B-spline'dır ve Gauss–Legendre kuralı parça parça **tam** integral
verir (integrand parça başına polinom olduğundan yeterli düğüm
sayısıyla hata sıfırdır).  Sayısal türev kullanılmaz.

**3. Sembolik kapanış.**  Öğrenilen bir kenar fonksiyonu ``φ``, küçük
bir kütüphaneden en iyi **sade** ifadeyle değiştirilmeye çalışılır:

.. math::  f^* = \\arg\\max_{f \\in \\mathrm{Lib}}
           \\bigl\\{ R(f,\\phi) - \\mu\\,\\mathrm{Uzunluk}(f) \\bigr\\}

``R`` normalize edilmiş bağıntıdır; sadelik cezası olmadan en karmaşık
aday hep kazanır.  Kapanış **ancak** artık hata eşiği altındaysa kabul
edilir; aksi hâlde spline olduğu gibi bırakılır -- yani sembolik
regresyon burada zorlanmıyor.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from itertools import combinations

import numpy as np

from matematik.geometri import (bspline_temeli, bspline_turev_temeli,
                                       dugum_dizisi)

__all__ = [
    "artislardan_dugum", "dugum_gecerli_mi", "artis_gradyani",
    "bukulme_dizeyi", "bukulme_enerjisi", "duzenli_uydur",
    "SEMBOL_KUTUPHANESI", "sembolik_kapanis", "bagintili_olcut",
]


# ══════════════════════════════════════════════════════════════════════
#  1. Adaptif düğümler
# ══════════════════════════════════════════════════════════════════════

def artislardan_dugum(t0: float, s: Sequence[float],
                      eps: float = 1e-6) -> np.ndarray:
    """``t_{k+1} = t_k + e^{s_k} + ε`` — sıralama YAPI GEREĞİ korunur.

    Sıralamayı bir ceza terimiyle *teşvik etmek* ile parametrelemeyle
    *garanti etmek* farklı şeylerdir: ceza ihlal edilebilir, yapı
    edilemez.  ``ε > 0`` alt sınırı, ``s_k → −∞`` iken bile paydanın
    sıfırlanmamasını sağlar.
    """
    s = np.asarray(s, float)
    if eps <= 0:
        raise ValueError("ε > 0 olmalı")
    artis = np.exp(np.clip(s, -700, 700)) + eps
    return np.concatenate([[float(t0)], float(t0) + np.cumsum(artis)])


def dugum_gecerli_mi(t: np.ndarray, eps: float = 0.0) -> bool:
    """``t_0 < t_1 < … < t_G`` ve her aralık ``> ε``."""
    t = np.asarray(t, float)
    return bool(np.all(np.diff(t) > eps))


def artis_gradyani(dL_dt: Sequence[float], s: Sequence[float],
                   eps: float = 1e-6) -> np.ndarray:
    """``∂L/∂s_k = e^{s_k} · Σ_{j>k} ∂L/∂t_j``.

    ``t_j`` birikimli toplam olduğundan ``s_k``, kendisinden **sonraki
    bütün** düğümleri kaydırır; zincir kuralı bu yüzden bir kuyruk
    toplamı içerir.  Yalnız ``∂L/∂t_{k+1}`` almak (kaynaktaki 21.3
    numaralı formülün yazılışı) katkının çoğunu düşürür.
    """
    dL_dt = np.asarray(dL_dt, float)
    s = np.asarray(s, float)
    if dL_dt.size != s.size + 1:
        raise ValueError("dL/dt, s'den bir uzun olmalı")
    kuyruk = np.cumsum(dL_dt[::-1])[::-1]          # Σ_{j≥k} ∂L/∂t_j
    return np.exp(np.clip(s, -700, 700)) * kuyruk[1:]


# ══════════════════════════════════════════════════════════════════════
#  2. Bükülme enerjisi
# ══════════════════════════════════════════════════════════════════════

def bukulme_dizeyi(G: int, k: int, alt: float = -1.0, ust: float = 1.0,
                   dugum_sayisi: int = 8) -> np.ndarray:
    """``S_ij = ∫ B_i''(x) B_j''(x) dx`` — parça parça Gauss–Legendre.

    ``B_i''`` her düğüm aralığında ``k−2`` dereceli bir polinomdur, o
    yüzden çarpım ``2(k−2)`` derecelidir.  ``n`` düğümlü Gauss–Legendre
    ``2n−1`` dereceye kadar **tam**tır; ``n ≥ k−1`` seçilirse integral
    yaklaşık değil, tamdır.  ``dugum_sayisi`` varsayılanı bunu bolca
    aşar.

    ``k < 2`` iken ikinci türev sıfırdır ve ``S = 0`` döner (hata
    değil: sabit ve doğrusal parçaların bükülmesi yoktur).
    """
    if k < 0:
        raise ValueError("derece negatif olamaz")
    n_temel = G + k
    if k < 2:
        return np.zeros((n_temel, n_temel))
    d = dugum_dizisi(G, k, alt, ust)
    dugum, agirlik = np.polynomial.legendre.leggauss(dugum_sayisi)
    S = np.zeros((n_temel, n_temel))
    # Yalnız TAM DESTEKLENEN aralıklar: [t_k, t_{n}]
    kenarlar = d[k:d.size - k]
    for a, b in zip(kenarlar[:-1], kenarlar[1:]):
        if b <= a:
            continue
        orta, yari = (a + b) / 2, (b - a) / 2
        x = orta + yari * dugum
        # İkinci türev: türev temelinin türevi (iki kere kapalı form)
        D2 = _ikinci_turev_temeli(x, d, k)
        S += (D2 * (agirlik * yari)[:, None]).T @ D2
    return S


def _ikinci_turev_temeli(t: np.ndarray, dugumler: np.ndarray,
                         k: int) -> np.ndarray:
    """``B''_{i,k}`` — türev kuralını iki kere uygulayarak.

    ``B'_{i,k} = k(B_{i,k-1}/(t_{i+k}−t_i) − B_{i+1,k-1}/(t_{i+k+1}−t_{i+1}))``
    özdeşliği ``k−1`` derecede tekrar uygulanır.  Sayısal türev
    alınmaz; netice kapalı formdur.
    """
    d = np.asarray(dugumler, float)
    t = np.atleast_1d(np.asarray(t, float))
    if k < 2:
        return np.zeros((t.size, d.size - k - 1))
    Bk2 = bspline_temeli(t, d, k - 2)
    n = d.size - k - 1
    T = np.zeros((t.size, n))
    for i in range(n):
        for (i0, isaret) in ((i, 1.0), (i + 1, -1.0)):
            p1 = d[i0 + k - 1] - d[i0]
            if p1 <= 0:
                continue
            kat = isaret * k * (k - 1) / p1
            for (i1, isaret2) in ((i0, 1.0), (i0 + 1, -1.0)):
                p2 = d[i1 + k - 1] - d[i1]
                if p2 <= 0 or i1 >= Bk2.shape[1]:
                    continue
                T[:, i] += kat * isaret2 * Bk2[:, i1] / p2
    return T


def bukulme_enerjisi(c: np.ndarray, S: np.ndarray) -> float:
    """``E = cᵀSc`` — skalerdir ve ``S`` PSD olduğundan negatif olamaz."""
    c = np.asarray(c, float).reshape(-1)
    return float(c @ (np.asarray(S, float) @ c))


def duzenli_uydur(t: np.ndarray, y: np.ndarray, G: int, k: int,
                  lam: float = 0.0, alt: float = -1.0,
                  ust: float = 1.0) -> Dict[str, object]:
    """``min_c ‖Bc − y‖² + λ·cᵀSc`` — kapalı form.

    Normal denklemler ``(BᵀB + λS)c = Bᵀy``.  ``λ = 0``da ve az veriyle
    ``BᵀB`` tekil olabilir; o hâlde en küçük norm çözümü alınır ve
    **öyle olduğu bildirilir**, sessizce bir şey uydurulmaz.
    """
    t = np.atleast_1d(np.asarray(t, float))
    y = np.asarray(y, float).reshape(-1)
    d = dugum_dizisi(G, k, alt, ust)
    B = bspline_temeli(t, d, k)
    S = bukulme_dizeyi(G, k, alt, ust)
    A = B.T @ B + lam * S
    b = B.T @ y
    tekil = bool(np.linalg.matrix_rank(A) < A.shape[0])
    c = (np.linalg.lstsq(A, b, rcond=None)[0] if tekil
         else np.linalg.solve(A, b))
    tahmin = B @ c
    return {
        "c": c, "artık": float(np.sqrt(np.mean((tahmin - y) ** 2))),
        "bükülme": bukulme_enerjisi(c, S),
        "tekil_sistem": tekil, "S": S, "B": B,
    }


# ══════════════════════════════════════════════════════════════════════
#  3. Sembolik kapanış
# ══════════════════════════════════════════════════════════════════════

#: ``(ad, fonksiyon, AST uzunluğu)`` — uzunluk sadelik cezasıdır.
SEMBOL_KUTUPHANESI: Tuple[Tuple[str, Callable[[np.ndarray], np.ndarray],
                                int], ...] = (
    ("0", lambda x: np.zeros_like(x), 1),
    ("x", lambda x: x, 1),
    ("x^2", lambda x: x ** 2, 2),
    ("x^3", lambda x: x ** 3, 2),
    ("|x|", lambda x: np.abs(x), 2),
    ("1/(1+x^2)", lambda x: 1.0 / (1.0 + x ** 2), 4),
    ("sin(x)", lambda x: np.sin(x), 2),
    ("sin(3x)", lambda x: np.sin(3 * x), 3),
    ("cos(x)", lambda x: np.cos(x), 2),
    ("exp(x)", lambda x: np.exp(x), 2),
    ("tanh(x)", lambda x: np.tanh(x), 2),
    ("ln(1+x^2)", lambda x: np.log1p(x ** 2), 4),
)


def bagintili_olcut(f: np.ndarray, g: np.ndarray) -> float:
    """``R = ⟨f,g⟩/(‖f‖‖g‖)`` — sabit fonksiyonda 0.

    Sabit bir aday her fonksiyonla "mükemmel uyumlu" görünebilir;
    ortalama çıkarılmadan bağıntı bunu ödüllendirir.  Burada
    ortalamalar çıkarılıp Pearson alınır, ve payda sıfırsa (sabit)
    **0** döner -- yani sabit aday hiçbir zaman kazanamaz.
    """
    f = np.asarray(f, float).reshape(-1)
    g = np.asarray(g, float).reshape(-1)
    df, dg = f - f.mean(), g - g.mean()
    payda = math.sqrt(float(df @ df) * float(dg @ dg))
    if payda < 1e-14:
        return 0.0
    return float(df @ dg / payda)


def sembolik_kapanis(x: np.ndarray, phi: np.ndarray, mu: float = 0.02,
                     esik: float = 0.02
                     ) -> Dict[str, object]:
    """En iyi **sade** sembolik adayı seç -- kabul şartıyla.

    Her aday için en iyi ``a·f(x) + b`` afin ölçek kapalı formda
    bulunur (aday ile ``φ`` arasındaki ölçek farkı adayın suçu
    değildir), sonra puan ``R − μ·uzunluk`` ile sıralanır.

    **Kabul şartı ayrıdır:** en iyi adayın bağıl artığı ``esik``in
    altındaysa kapanış yapılır, değilse ``kabul=False`` döner ve
    spline olduğu gibi kalır.  Sembolik regresyon zorlanmaz.
    """
    x = np.asarray(x, float).reshape(-1)
    phi = np.asarray(phi, float).reshape(-1)
    olcek = float(np.sqrt(np.mean((phi - phi.mean()) ** 2)))
    adaylar = []
    for ad, f, uzunluk in SEMBOL_KUTUPHANESI:
        with np.errstate(over="ignore", invalid="ignore"):
            v = np.asarray(f(x), float)
        if not np.all(np.isfinite(v)):
            continue
        A = np.stack([v, np.ones_like(v)], axis=1)
        kats, *_ = np.linalg.lstsq(A, phi, rcond=None)
        artik = float(np.sqrt(np.mean((A @ kats - phi) ** 2)))
        R = abs(bagintili_olcut(v, phi))
        adaylar.append({
            "ad": ad, "a": float(kats[0]), "b": float(kats[1]),
            "bağıntı": R, "artık": artik,
            "bağıl_artık": artik / max(olcek, 1e-300),
            "uzunluk": uzunluk, "puan": R - mu * uzunluk,
        })
    if not adaylar:
        return {"kabul": False, "sebep": "hiçbir aday sonlu değil"}
    adaylar.sort(key=lambda a: -a["puan"])
    en_iyi = adaylar[0]
    return {
        "kabul": bool(en_iyi["bağıl_artık"] <= esik),
        "en_iyi": en_iyi,
        "sıralama": adaylar[:5],
        "eşik": esik,
    }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s: List[str] = []
    rng = np.random.default_rng(0)

    s.append("=== Adaptif düğümler: sıralama YAPI GEREĞİ korunuyor ===")
    for tohum in range(4):
        r = np.random.default_rng(tohum)
        sv = r.normal(0, 3.0, 7)          # vahşi parametreler
        t = artislardan_dugum(-1.0, sv)
        s.append(f"  tohum {tohum}: s ∈ [{sv.min():+.2f},{sv.max():+.2f}]"
                 f"  → düğüm aralığı [{t.min():.3f},{t.max():.3f}]"
                 f"  geçerli mi? {dugum_gecerli_mi(t)}")
    s.append("  Aşırı negatif s'te bile:")
    t = artislardan_dugum(0.0, [-1000.0] * 5)
    s.append(f"    s=-1000 → asgarî aralık = {np.min(np.diff(t)):.3e}"
             f"   geçerli mi? {dugum_gecerli_mi(t)}")
    s.append("  (Ceza terimiyle olsaydı bu hâlde payda sıfırlanabilirdi.)")

    s.append("\n=== Zincir kuralı: s_k kendinden SONRAKİ her düğümü kaydırır")
    sv = np.array([0.1, -0.3, 0.5])
    dL_dt = np.array([1.0, 2.0, 3.0, 4.0])
    g = artis_gradyani(dL_dt, sv)
    naif = np.exp(sv) * dL_dt[1:]           # kaynaktaki yazılış
    s.append(f"  doğru  ∂L/∂s = {np.array2string(g, precision=4)}")
    s.append(f"  naif   ∂L/∂s = {np.array2string(naif, precision=4)}")
    s.append(f"  bağıl fark: {np.max(np.abs(g - naif) / np.abs(g)):.2%}"
             "  — kuyruk toplamı düşürülünce katkının çoğu kayboluyor")
    # Sayısal sağlama
    def L(sv_):
        return float(np.sum(dL_dt * artislardan_dugum(0.0, sv_)))
    h = 1e-6
    say = np.array([(L(sv + h * np.eye(3)[i]) - L(sv - h * np.eye(3)[i]))
                    / (2 * h) for i in range(3)])
    s.append(f"  sayısal ∂L/∂s = {np.array2string(say, precision=4)}"
             f"   doğruyla fark = {np.max(np.abs(say - g)):.2e}")

    s.append("\n=== Bükülme dizeyi kapalı formda ===")
    for G, k in ((5, 3), (8, 3), (10, 4)):
        S = bukulme_dizeyi(G, k)
        oz = np.linalg.eigvalsh(S)
        s.append(f"  G={G} k={k}: şekil {S.shape}"
                 f"  simetrik mi? {np.max(np.abs(S-S.T)) < 1e-10}"
                 f"  PSD mi? {oz.min() > -1e-9}"
                 f"  sıfır özdeğer sayısı = {int(np.sum(np.abs(oz) < 1e-9))}")
    s.append("  Sıfır özdeğerler DOĞRUSAL fonksiyonlara karşılık gelir:")
    s.append("  bükülme enerjisi doğrusalları cezalandırmaz (φ''=0).")
    G, k = 8, 3
    S = bukulme_dizeyi(G, k)
    d = dugum_dizisi(G, k)
    x = np.linspace(-1, 1, 400)
    B = bspline_temeli(x, d, k)
    for ad, hedef in (("sabit 1", np.ones_like(x)), ("doğrusal x", x),
                      ("x²", x ** 2)):
        c, *_ = np.linalg.lstsq(B, hedef, rcond=None)
        s.append(f"    {ad:12s} bükülme enerjisi = "
                 f"{bukulme_enerjisi(c, S):.3e}")

    s.append("\n=== Runge salınımı dizginleniyor mu? ===")
    s.append("  Runge fonksiyonu 1/(1+25x²); AZ veri, ÇOK düğüm — yani")
    s.append("  aşırı uydurmanın bol olduğu hâl (N=30 nokta, G=28 aralık):")
    xr = np.linspace(-1, 1, 30)
    yr = 1.0 / (1.0 + 25 * xr ** 2) + 0.08 * rng.normal(size=30)
    xt = np.linspace(-1, 1, 500)
    yt = 1.0 / (1.0 + 25 * xt ** 2)
    Bt = bspline_temeli(xt, dugum_dizisi(28, 3), 3)
    s.append("      λ      eğitim artığı   bükülme      sınama hatası")
    sinamalar = []
    for lam in (0.0, 1e-6, 1e-4, 1e-2, 1.0):
        r = duzenli_uydur(xr, yr, 28, 3, lam)
        sina = float(np.sqrt(np.mean((Bt @ r["c"] - yt) ** 2)))
        sinamalar.append((lam, sina))
        s.append(f"  {lam:7.0e}   {r['artık']:.3e}   {r['bükülme']:.3e}"
                 f"   {sina:.3e}"
                 + ("   (tekil sistem)" if r["tekil_sistem"] else ""))
    en_iyi = min(sinamalar, key=lambda t: t[1])
    en_kotu = max(sinamalar, key=lambda t: t[1])
    s.append(f"  En iyi λ={en_iyi[0]:.0e} (sınama {en_iyi[1]:.3f});"
             f" düzenlemesiz hâl {sinamalar[0][1]:.3f}")
    s.append(f"  → düzenleme sınama hatasını "
             f"{sinamalar[0][1]/en_iyi[1]:.0f}× iyileştiriyor.")
    s.append("  Aşırı λ ise (1.0) fonksiyonu düzleştirip yine bozuyor:")
    s.append(f"  sınama {sinamalar[-1][1]:.3f}. Yani en iyi λ ORTADADIR.")

    s.append("\n=== Sembolik kapanış ===")
    x = np.linspace(-1.5, 1.5, 300)
    ornekler = [
        ("tam sin(3x)", np.sin(3 * x)),
        ("2.5·x² − 1", 2.5 * x ** 2 - 1.0),
        ("gürültülü tanh", np.tanh(x) + 0.01 * rng.normal(size=x.size)),
        ("kütüphanede yok", np.sin(3 * x) * np.exp(-x ** 2) + 0.3 * x ** 3),
    ]
    for ad, phi in ornekler:
        r = sembolik_kapanis(x, phi)
        e = r["en_iyi"]
        s.append(f"  {ad:18s} → {e['ad']:10s} "
                 f"(a={e['a']:+.3f} b={e['b']:+.3f})"
                 f"  bağıl artık={e['bağıl_artık']:.3e}"
                 f"  KABUL={r['kabul']}")
    s.append("  Son satır kasten kütüphanede yok: kapanış REDDEDİLİYOR,")
    s.append("  yani spline olduğu gibi kalıyor. Zorlama yok.")

    s.append("\n=== Sadelik cezasının BEDELİ ===")
    s.append("  μ sadeliği ödüllendirir, ama bedeli vardır: birbirine")
    s.append("  çok yakın iki aday arasında SADE olanı seçer -- doğru")
    s.append("  olanı değil. [-1.5,1.5] üzerinde tanh(x) ile x neredeyse")
    s.append("  ayırt edilemez; ölçelim:")
    phi_t = np.tanh(x) + 0.01 * rng.normal(size=x.size)
    for mu in (0.0, 0.02, 0.2):
        r = sembolik_kapanis(x, phi_t, mu=mu)
        ilk = ", ".join(f"{a['ad']}(R={a['bağıntı']:.5f},"
                        f" puan={a['puan']:.4f})"
                        for a in r["sıralama"][:2])
        s.append(f"    μ={mu:.2f}: {ilk}")
    s.append("  μ=0'da DOĞRU cevap (tanh) kazanıyor; μ=0.02'de sadelik")
    s.append("  x'i öne alıyor. Kabul eşiği yine de bu seçimi REDDEDİYOR,")
    s.append("  yani yanlış kapanış yapılmıyor — ceza sıralamayı bozuyor,")
    s.append("  kabulü bozmuyor. İki mekanizmanın ayrı olmasının sebebi bu.")
    s.append("")
    s.append("  Kütüphanede TAM olan bir hedefte ceza zararsız:")
    phi_s = np.sin(3 * x)
    for mu in (0.0, 0.02, 0.2):
        r = sembolik_kapanis(x, phi_s, mu=mu)
        s.append(f"    μ={mu:.2f}: {r['sıralama'][0]['ad']}"
                 f" (puan {r['sıralama'][0]['puan']:.3f})")
    return "\n".join(s)



# ====================================================================
#  KÜME 8: simgesel bağlanım -- kapalı biçimli ifade aramak
# ====================================================================

Terim = Tuple[str, Callable[[np.ndarray], np.ndarray]]


def varsayilan_kutuphane() -> List[Terim]:
    return [
        ("1", lambda x: np.ones_like(x)),
        ("x", lambda x: x),
        ("x^2", lambda x: x * x),
        ("x^3", lambda x: x ** 3),
        ("sin x", lambda x: np.sin(x)),
        ("cos x", lambda x: np.cos(x)),
        ("exp x", lambda x: np.exp(x)),
        ("1/(1+x^2)", lambda x: 1.0 / (1.0 + x * x)),
    ]


def _uydur(
    x: np.ndarray, y: np.ndarray, terimler: Sequence[Terim]
) -> Tuple[np.ndarray, float]:
    A = np.stack([f(x) for _, f in terimler], axis=1)
    kat, *_ = np.linalg.lstsq(A, y, rcond=None)
    rss = float(np.sum((A @ kat - y) ** 2))
    return kat, rss


def bic(rss: float, m: int, k: int, taban: float = 1e-20) -> float:
    """BIC; ``taban`` sayısal gürültü zeminidir.

    Tabansız hâlde temiz veride iki farklı model ``RSS ≈ 10⁻²⁸`` ve
    ``10⁻²⁹`` verir; bu fark ANLAMSIZDIR (yuvarlama), fakat ``m·log RSS``
    onu ``m·log 10`` kadar büyütüp fazla terimli modeli seçtirir. Ölçüm
    sırasında tam olarak bu oldu: 2 terimli doğru model yerine 3 terimli
    bir model kazandı. Taban, kayan noktalı sıfırı sıfır saymaktır.
    """
    return m * np.log(max(rss, taban * m) / m) + k * np.log(m)


def ara(
    x: np.ndarray,
    y: np.ndarray,
    kutuphane: Sequence[Terim] | None = None,
    azami_terim: int = 3,
) -> Dict[str, object]:
    """Kütüphanenin ``≤ azami_terim`` boyutlu bütün alt kümelerini tarar."""
    kutuphane = list(kutuphane or varsayilan_kutuphane())
    m = len(x)
    en_iyi = None
    sirali: List[Tuple[float, Tuple[str, ...], np.ndarray, float]] = []
    for k in range(1, azami_terim + 1):
        for alt in combinations(range(len(kutuphane)), k):
            secilen = [kutuphane[i] for i in alt]
            kat, rss = _uydur(x, y, secilen)
            skor = bic(rss, m, k)
            adlar = tuple(ad for ad, _ in secilen)
            sirali.append((skor, adlar, kat, rss))
            if en_iyi is None or skor < en_iyi[0]:
                en_iyi = (skor, adlar, kat, rss)
    sirali.sort(key=lambda t: t[0])
    skor, adlar, kat, rss = en_iyi  # type: ignore[misc]
    return {
        "formul": " + ".join("%.4f·%s" % (c, a) for c, a in zip(kat, adlar)),
        "terimler": adlar,
        "katsayilar": kat,
        "rss": rss,
        "bic": skor,
        "ilk_bes": [(round(s, 2), a) for s, a, _, _ in sirali[:5]],
    }


def temiz_veride_bulunuyor_mu() -> Dict[str, object]:
    """``y = 2x² − 3sin x``: doğru terim kümesi tam olarak bulunmalı."""
    x = np.linspace(-2, 2, 200)
    y = 2.0 * x * x - 3.0 * np.sin(x)
    r = ara(x, y)
    return {
        "bulunan": r["formul"],
        "terimler": r["terimler"],
        "dogru_terimler": bool(set(r["terimler"]) == {"x^2", "sin x"}),
        "katsayilar_dogru": bool(
            np.allclose(sorted(r["katsayilar"]), sorted([2.0, -3.0]), atol=1e-8)
        ),
        "rss": r["rss"],
    }


def ceza_fazla_terimi_eliyor_mu(gurultu: float = 0.05, tohum: int = 0) -> Dict[str, object]:
    """Gürültülü veride: cezasız ölçüt (RSS) hep en büyük modeli seçer,
    BIC ise doğru boyutta durur."""
    rng = np.random.default_rng(tohum)
    x = np.linspace(-2, 2, 200)
    y = 2.0 * x * x - 3.0 * np.sin(x) + gurultu * rng.normal(size=x.size)
    kut = varsayilan_kutuphane()

    en_iyi_rss = None
    for k in range(1, 4):
        for alt in combinations(range(len(kut)), k):
            _, rss = _uydur(x, y, [kut[i] for i in alt])
            adlar = tuple(kut[i][0] for i in alt)
            if en_iyi_rss is None or rss < en_iyi_rss[0]:
                en_iyi_rss = (rss, adlar)

    r = ara(x, y)
    return {
        "rss_secimi": en_iyi_rss[1],
        "rss_secimi_boyut": len(en_iyi_rss[1]),
        "bic_secimi": r["terimler"],
        "bic_secimi_boyut": len(r["terimler"]),
        "bic_daha_sade": bool(len(r["terimler"]) < len(en_iyi_rss[1])),
        "bic_dogruyu_buldu": bool(set(r["terimler"]) == {"x^2", "sin x"}),
    }


def kutuphane_disinda_ne_oluyor() -> Dict[str, object]:
    """**Zaaf.** Hedef ``y = log(2+x)``; kütüphanede logaritma YOK.

    Usul yine de bir formül döndürür ve o formül ARALIKTA iyi görünür.
    Yanlışlık ancak DIŞARIDA ortaya çıkar. Yani simgesel bağlanımın
    çıktısı 'kanun' diye okunamaz; ancak kütüphane doğru kurulduysa
    kanundur.
    """
    x = np.linspace(-1, 1, 200)
    y = np.log(2.0 + x)
    r = ara(x, y)
    kut = dict(varsayilan_kutuphane())
    A_ic = np.stack([kut[a](x) for a in r["terimler"]], axis=1)
    ic_hata = float(np.sqrt(np.mean((A_ic @ r["katsayilar"] - y) ** 2)))

    xd = np.linspace(3, 8, 200)          # eğitim aralığının DIŞI
    yd = np.log(2.0 + xd)
    A_dis = np.stack([kut[a](xd) for a in r["terimler"]], axis=1)
    dis_hata = float(np.sqrt(np.mean((A_dis @ r["katsayilar"] - yd) ** 2)))
    return {
        "bulunan": r["formul"],
        "aralik_ici_hata": ic_hata,
        "aralik_disi_hata": dis_hata,
        # hedefin aralık içi salınımı ~1.1; %1'in altı "iyi görünüyor"dur
        "hedef_genligi": float(np.max(y) - np.min(y)),
        "icerde_iyi_gorunuyor": bool(ic_hata < 0.01 * (np.max(y) - np.min(y))),
        "disarida_bozuluyor": bool(dis_hata > 100 * max(ic_hata, 1e-12)),
        "usul_bilmedigini_soylemiyor": True,
    }


def _rapor_simgesel() -> str:
    s = ["=== simgesel ==="]
    a = temiz_veride_bulunuyor_mu()
    s.append("temiz veri   %s   (doğru terimler=%s, katsayılar=%s, rss=%.2e)"
             % (a["bulunan"], a["dogru_terimler"], a["katsayilar_dogru"], a["rss"]))
    b = ceza_fazla_terimi_eliyor_mu()
    s.append("Occam cezası RSS seçimi=%s (k=%d) | BIC seçimi=%s (k=%d) | BIC sade=%s doğru=%s"
             % (b["rss_secimi"], b["rss_secimi_boyut"], b["bic_secimi"],
                b["bic_secimi_boyut"], b["bic_daha_sade"], b["bic_dogruyu_buldu"]))
    c = kutuphane_disinda_ne_oluyor()
    s.append("zaaf         log(2+x) için bulunan: %s" % c["bulunan"])
    s.append("             aralık içi=%.2e  aralık dışı=%.4g  içerde iyi=%s dışarıda bozuk=%s"
             % (c["aralik_ici_hata"], c["aralik_disi_hata"],
                c["icerde_iyi_gorunuyor"], c["disarida_bozuluyor"]))
    return "\n".join(s)

def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
