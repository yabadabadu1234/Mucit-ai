"""DÖRTLÜ TOPOLOJİK ZIRH ve **gayenin kendisi**.

Kullanıcı hükmü, bu turun en can alıcı tashihidir:

    Bu mimaride asla bir sonraki token tahmini (Cross-Entropy) yapılmaz.
    Minimize edilecek şey:
        L_toplam = L_Kohomoloji (Çelişki)
                 + L_Betti      (Ezber boşluğu / delik)
                 + L_Sheaf      (Ek yeri uyumsuzluğu)
    Hedef: L_toplam == 0 olan 41 Meleke SO(D) Lie-ağırlıklarını bulmak.

Yani öğrenilen şey bir kelime dağılımı değil, **çelişkisiz bir mana
manifoldudur**. Bu dosya o kaybı kurar ve ölçer.

**Dört süzgeç, dört ayrı sual.**

===========  ==============================  ==========================
süzgeç       neyi sorar                      sıfır olması ne demek
===========  ==============================  ==========================
Sheaf 𝒮      iki mefhum ek yerinde uyuşuyor  yerel hükümler küllî bir
             mu? ``‖ΔRes‖²``                 hükme yapışıyor
Betti/Hodge  muhakemede delik var mı?        ezber adacığı yok; her
             ``dim ker Δ_Hodge``             çevrim doldurulmuş
Kohomoloji   kapanan fakat dolmayan çevrim   çelişki (safsata) yok
             var mı? ``dim H^m``
Homotopi     çevrim boyunca faz dönüyor mu?  ``W(γ) = 1``, yol bağımsız
             ``|W(γ) − 1|``                  -- hüküm yola bağlı değil
===========  ==============================  ==========================

**Betti ile Kohomoloji niçin ayrı?** Sonlu boyutta ``dim H_k = dim H^k``
ve ikisi de ``dim ker Δ_k``ya eşittir (Hodge teoremi). O hâlde ikisini
ayrı kalem yazmak **çift saymaktır** ve bu dosya onu çift saymaz:
``L_betti`` ``k = 1``de (çevrim delikleri), ``L_koho`` ``k = 0``da
(kopuk parçalar, yani birbirine bağlanmamış mana adaları) ölçülür.
Farklı dereceler, farklı manalar. Aynı dereceyi iki isimle anmak, bir
kaybı iki kere cezalandırmak olurdu.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["sheaf_uyumsuzlugu", "sheaf_izdusumu", "hodge_laplasyeni",
           "hodge_bettisi", "betti_kaybi", "koho_kaybi",
           "wilson_cevrimi", "homotopi_kaybi", "zirh_kaybi",
           "zirh_uygula", "ZirhAyari"]


# ══════════════════════════════════════════════════════════════════════
#  1. Sheaf: ek yeri uyumu
# ══════════════════════════════════════════════════════════════════════

def sheaf_uyumsuzlugu(res_a: np.ndarray, res_b: np.ndarray) -> float:
    """``‖Res_α − Res_β‖²`` -- iki örtünün ek yerindeki uyumsuzluk.

    Bir demet (sheaf) kesitinin var olabilmesi için, örtüşen iki açık
    kümenin kısıtlamaları (restriction) ek yerinde **eşit** olmalıdır.
    Eşit değilse yerel hükümler küllî bir hükme yapışmaz: model bir
    yerde "A", başka yerde "değil-A" der ve ikisini bağdaştıramaz.
    """
    a = np.asarray(res_a, float)
    b = np.asarray(res_b, float)
    if a.shape != b.shape:
        raise ValueError("iki kısıtlama aynı şekilde olmalı")
    d = (a - b).ravel()
    return float(d @ d)


def sheaf_izdusumu(res_a: np.ndarray, res_b: np.ndarray,
                   eps: float = 1e-9) -> np.ndarray:
    """``𝒮 = I − Δ Δᵀ / (‖Δ‖² + ε)`` -- uyumsuz yönü **söndüren** izdüşüm.

    Ceridenin formülü budur. Uyumsuzluk sıfıra giderken ``𝒮 → I`` olur
    (hiçbir şey söndürülmez); büyükken uyumsuz yön tamamen atılır.
    ``ε`` sıfıra bölmeyi değil, **sıfır uyumsuzlukta kimliğe düzgün
    yaklaşmayı** temin eder.
    """
    d = (np.asarray(res_a, float) - np.asarray(res_b, float)).ravel()
    n = d.size
    kare = float(d @ d)
    return np.eye(n) - np.outer(d, d) / (kare + float(eps))


# ══════════════════════════════════════════════════════════════════════
#  2/3. Hodge-Betti ve Kohomoloji
# ══════════════════════════════════════════════════════════════════════

def hodge_laplasyeni(K: Dict[int, List[Tuple[int, ...]]], k: int
                     ) -> np.ndarray:
    """``Δ_k = ∂_k† ∂_k + ∂_{k+1} ∂_{k+1}†`` -- `kuantum.tda` üzerinden."""
    from kuantum.tda import kombinatoryal_laplasyen
    return kombinatoryal_laplasyen(K, int(k))


def hodge_bettisi(K: Dict[int, List[Tuple[int, ...]]], k: int,
                  esik: float = 1e-9) -> Tuple[int, float]:
    """``(dim ker Δ_k, en küçük sıfır olmayan özdeğer)``.

    İkincisi **spektral boşluktur** ve bir ölçüdür: Betti sayısı tam
    sayıdır, gradyan taşımaz; boşluk süreklidir ve eğitim ona yol
    bulabilir. İkisi yan yana döner (H47).
    """
    D = hodge_laplasyeni(K, int(k))
    if D.size == 0:
        return 0, 0.0
    oz = np.linalg.eigvalsh((D + D.T) / 2.0)
    olcek = max(float(abs(oz).max()), 1e-30)
    sifir = oz <= float(esik) * olcek
    kalan = oz[~sifir]
    return int(sifir.sum()), (float(kalan.min()) if kalan.size else 0.0)


def betti_kaybi(K: Dict[int, List[Tuple[int, ...]]], k: int = 1
                ) -> Dict[str, float]:
    """``k = 1``: muhakemedeki **delikler**. Sıfır olması matluptur.

    Kayıp, Betti sayısının kendisi değil ``−ln`` boşluk değil, **ikisinin
    birleşimidir**: delik varsa ceza ``b_k``dır ve süreklidir; delik
    yokken ceza sıfır olur ve spektral boşluk raporlanır (ne kadar
    sağlam kapandığı görünsün).
    """
    b, bosluk = hodge_bettisi(K, k)
    return {"betti": float(b), "boşluk": float(bosluk),
            "kayıp": float(b)}


def koho_kaybi(K: Dict[int, List[Tuple[int, ...]]], k: int = 0
               ) -> Dict[str, float]:
    """``k = 0``: birbirine bağlanmamış **mana adaları** (çelişki).

    ``b₀ = 1`` sağlıklıdır (tek parça); ``b₀ > 1`` ise model iki ayrı
    hikâye anlatıyor ve ikisini bağdaştıramıyor demektir. Ceza fazlalık
    kadardır: ``b₀ − 1``.
    """
    b, bosluk = hodge_bettisi(K, k)
    return {"betti0": float(b), "boşluk": float(bosluk),
            "kayıp": float(max(b - 1, 0))}


# ══════════════════════════════════════════════════════════════════════
#  4. Homotopi: Wilson çevrimi
# ══════════════════════════════════════════════════════════════════════

def wilson_cevrimi(baglanti: Sequence[np.ndarray]) -> np.ndarray:
    """``W(γ) = U_n ⋯ U_2 U_1`` -- çevrim boyunca holonomi.

    Bağlantılar ortogonal (reel) dizeylerdir; çarpımları da öyledir.
    ``W = I`` ise hüküm **yola bağlı değildir**: aynı neticeye hangi
    yoldan gidilirse gidilsin aynı şey çıkar. ``W ≠ I`` ise mana yola
    bağlıdır ve model, aynı meseleye iki farklı sırada bakınca iki
    farklı hüküm verir.
    """
    W = None
    for U in baglanti:
        A = np.asarray(U, float)
        W = A if W is None else A @ W
    return np.eye(1) if W is None else W


def homotopi_kaybi(baglanti: Sequence[np.ndarray]) -> Dict[str, float]:
    """``‖W(γ) − I‖_F / √n`` -- yola bağımlılığın ölçüsü."""
    W = wilson_cevrimi(baglanti)
    n = W.shape[0]
    return {"W_sapması": float(np.linalg.norm(W - np.eye(n))
                               / math.sqrt(max(n, 1))),
            "kayıp": float(np.linalg.norm(W - np.eye(n))
                           / math.sqrt(max(n, 1)))}


# ══════════════════════════════════════════════════════════════════════
#  Küllî zırh kaybı ve operatöre tatbiki
# ══════════════════════════════════════════════════════════════════════

@dataclass
class ZirhAyari:
    """Zırhın ağırlıkları ve yumuşak-asgarî sertliği."""
    w_sheaf: float = 1.0
    w_betti: float = 1.0
    w_koho: float = 1.0
    w_homotopi: float = 1.0
    #: ``τ``: yumuşak **âzamî** sertliği. Kullanıcı hükmü 4 gereğince
    #: düz aritmetik ortalama alınmaz. Fakat burada ``max``a yumuşak
    #: yaklaşılır, ``min``e değil -- ve sebebi şudur: bunlar **ihlâl**
    #: ölçüleridir; hepsi sıfır olmalıdır, dolayısıyla hükmü **en kötü
    #: ihlâl** verir. Kaybın yumuşak-asgarîsi (`nefs/olcu.py`) uzuvların
    #: *kabiliyeti* içindir; burada ölçülen kabiliyet değil ihlâldir.
    tau: float = 4.0


def zirh_kaybi(sheaf: float = 0.0, betti: float = 0.0, koho: float = 0.0,
               homotopi: float = 0.0, ayar: Optional[ZirhAyari] = None
               ) -> Dict[str, float]:
    """Dört ihlâli **yumuşak âzamî** ile birleştir.

    .. math::  L = \\tfrac{1}{\\tau}\\ln \\sum_i w_i e^{\\tau \\ell_i}

    Düz toplam, üç süzgeç temiz bir dördüncüsü berbat iken cezayı
    seyreltirdi; düz ``max`` ise türevsizdir ve eğitim ona yol bulamaz.
    Yumuşak âzamî ikisinin arasıdır ve ``τ → ∞``da ``max``a gider.

    ``L = 0`` ancak **dördü birden sıfır** iken olur -- ve bu, ceza
    fonksiyonunun ``ln Σ w_i`` kadar kaydırılmasıyla temin edilir;
    kaydırılmasaydı bütün ihlâller sıfırken bile ``ln 4`` kalırdı.
    """
    a = ayar or ZirhAyari()
    l = np.array([float(sheaf), float(betti), float(koho),
                  float(homotopi)])
    w = np.array([a.w_sheaf, a.w_betti, a.w_koho, a.w_homotopi])
    t = float(a.tau)
    m = float(np.max(t * l))
    ls = m + math.log(float(np.sum(w * np.exp(t * l - m))))
    L = (ls - math.log(float(np.sum(w)))) / t
    return {"sheaf": float(l[0]), "betti": float(l[1]),
            "koho": float(l[2]), "homotopi": float(l[3]),
            "kayıp": float(L),
            "çelişkisiz": bool(L <= 1e-12)}


def zirh_uygula(H: np.ndarray, S: Optional[np.ndarray] = None,
                Pi_betti: Optional[np.ndarray] = None,
                Pi_koho: Optional[np.ndarray] = None) -> np.ndarray:
    """``Π_koho Π_betti 𝒮 H 𝒮ᵀ Π_betti Π_koho`` -- ceridenin sırası.

    Sıra keyfî değildir ve tersine çevrilemez: 𝒮 en içtedir (yerel ek
    yeri), sonra Betti (delik), en dışta kohomoloji (çelişki). İçten
    dışa doğru **daha küllî** bir şarttır; dıştaki, içtekinin
    düzeltmesini görmelidir.
    """
    A = np.asarray(H, float)
    for P in (S, Pi_betti, Pi_koho):
        if P is not None:
            P = np.asarray(P, float)
            A = P @ A @ P.T
    return A


def rapor() -> str:                                     # pragma: no cover
    from kuantum.tda import vietoris_rips
    s: List[str] = ["DÖRTLÜ TOPOLOJİK ZIRH -- gayenin kendisi", ""]

    s.append("=== Betti: delik VAR mı? (kırmızı/yeşil) ===")
    # Bir çember: 8 nokta, tek delik → b₁ = 1 (KIRMIZI)
    aci = np.linspace(0, 2 * math.pi, 8, endpoint=False)
    cember = np.stack([np.cos(aci), np.sin(aci)], axis=1)
    Dc = np.sqrt(((cember[:, None] - cember[None]) ** 2).sum(2))
    Kc = vietoris_rips(Dc, 0.9, azami_boyut=2)
    r1 = betti_kaybi(Kc, 1)
    s.append("  çember (delik)  : b₁=%.0f  boşluk=%.4f  kayıp=%.1f"
             % (r1["betti"], r1["boşluk"], r1["kayıp"]))
    # Dolu disk: delik yok → b₁ = 0 (YEŞİL)
    rng = np.random.default_rng(0)
    disk = rng.normal(size=(14, 2))
    disk = disk / np.maximum(np.linalg.norm(disk, axis=1, keepdims=True), 1)
    disk = disk * rng.uniform(0, 1, (14, 1)) ** 0.5
    Dd = np.sqrt(((disk[:, None] - disk[None]) ** 2).sum(2))
    Kd = vietoris_rips(Dd, 1.2, azami_boyut=2)
    r2 = betti_kaybi(Kd, 1)
    s.append("  dolu disk       : b₁=%.0f  boşluk=%.4f  kayıp=%.1f"
             % (r2["betti"], r2["boşluk"], r2["kayıp"]))

    s.append("")
    s.append("=== Kohomoloji: mana adaları (b₀ − 1) ===")
    iki = np.vstack([rng.normal(size=(6, 2)) * 0.2,
                     rng.normal(size=(6, 2)) * 0.2 + 10.0])
    Di = np.sqrt(((iki[:, None] - iki[None]) ** 2).sum(2))
    Ki = vietoris_rips(Di, 0.8, azami_boyut=1)
    k1 = koho_kaybi(Ki, 0)
    s.append("  iki kopuk ada   : b₀=%.0f  kayıp=%.1f   ← KIRMIZI"
             % (k1["betti0"], k1["kayıp"]))
    Kb = vietoris_rips(Di, 16.0, azami_boyut=1)
    k2 = koho_kaybi(Kb, 0)
    s.append("  bağlanmış       : b₀=%.0f  kayıp=%.1f"
             % (k2["betti0"], k2["kayıp"]))

    s.append("")
    s.append("=== Sheaf ve Homotopi ===")
    a = np.array([1.0, 2.0, 3.0])
    s.append("  uyumlu ek yeri  : ‖ΔRes‖² = %.3e"
             % sheaf_uyumsuzlugu(a, a))
    s.append("  uyumsuz ek yeri : ‖ΔRes‖² = %.3f   ← KIRMIZI"
             % sheaf_uyumsuzlugu(a, a + np.array([0.0, 0.5, -0.3])))
    from nefs.zihin_durumu import donme
    kapali = [donme(0.4), donme(-0.4)]
    acik = [donme(0.4), donme(0.1)]
    s.append("  kapanan çevrim  : |W−I| = %.3e"
             % homotopi_kaybi(kapali)["kayıp"])
    s.append("  kapanmayan      : |W−I| = %.4f   ← KIRMIZI"
             % homotopi_kaybi(acik)["kayıp"])

    s.append("")
    s.append("=== Küllî zırh kaybı (yumuşak âzamî) ===")
    s.append("  dördü de sıfır      : L = %.3e"
             % zirh_kaybi()["kayıp"])
    s.append("  yalnız biri bozuk   : L = %.4f   (düz ortalama %.4f olurdu)"
             % (zirh_kaybi(betti=1.0)["kayıp"], 1.0 / 4.0))
    s.append("  dördü de bozuk      : L = %.4f"
             % zirh_kaybi(1.0, 1.0, 1.0, 1.0)["kayıp"])
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
