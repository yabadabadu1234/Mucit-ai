"""
Aradeğerleme: Kan genişletmesi ve onun ezber zaafı.

**Kan genişletmesi nedir, burada niçin geçiyor?** Lawvere'in okuyuşunda bir
metrik uzay, ``[0,∞]`` üzerinde zenginleştirilmiş bir kategoridir; nesneler
noktalar, ``hom(x,y) = d(x,y)``. Bir ``L``-Lipschitz fonksiyon böyle
kategoriler arası bir zenginleştirilmiş funktordur. Sonlu bir örnek kümesi
``S ⊂ X`` üzerinde tanımlı ``f``i bütün ``X``e genişletmek, ``S ↪ X``
katılımı boyunca **Kan genişletmesi** almaktır ve formül tam olarak
McShane--Whitney genişletmeleridir:

    (Lan f)(x) = supᵢ [ f(xᵢ) − L·d(x, xᵢ) ]      (en KÜÇÜK L-Lipschitz genişleme)
    (Ran f)(x) = infᵢ [ f(xᵢ) + L·d(x, xᵢ) ]      (en BÜYÜK L-Lipschitz genişleme)

ve her ``L``-Lipschitz genişleme ``g`` için ``Lan f ≤ g ≤ Ran f``. Bu bir
benzetme değil; sınanabilir bir özdeşliktir ve aşağıda sınanır.

**Zaafı**: Kan genişletmesi verilen noktalarda TAM oturur. Veri gürültülüyse
gürültüyü de ezberler. Çare, genişlemeyi zorlamak yerine cezalandırmaktır:
RKHS'de ``‖g‖²_H`` cezasıyla sırt bağlanımı (kernel ridge). Bedeli: artık
veriden geçmez; sapma (bias) ile varyans arasında bilerek takas yapılır.
"""
from __future__ import annotations

from typing import Callable, Dict, Tuple

import numpy as np


# =====================================================================
#  1. Kan genişletmesi = McShane--Whitney
# =====================================================================
def lan(x: np.ndarray, xs: np.ndarray, ys: np.ndarray, L: float) -> np.ndarray:
    """Sol Kan genişletmesi: ``supᵢ [yᵢ − L|x−xᵢ|]``."""
    return np.max(ys[None, :] - L * np.abs(x[:, None] - xs[None, :]), axis=1)


def ran(x: np.ndarray, xs: np.ndarray, ys: np.ndarray, L: float) -> np.ndarray:
    """Sağ Kan genişletmesi: ``infᵢ [yᵢ + L|x−xᵢ|]``."""
    return np.min(ys[None, :] + L * np.abs(x[:, None] - xs[None, :]), axis=1)


def kan_ozellikleri(
    n: int = 12, L: float = 3.0, tohum: int = 0
) -> Dict[str, object]:
    """Üç iddia sınanır:

    1. ``Lan f`` ve ``Ran f`` örnek noktalarında ``f`` ile aynıdır (birim eş).
    2. İkisi de ``L``-Lipschitz'tir.
    3. Her ``L``-Lipschitz genişleme ikisinin ARASINDADIR (evrensel hususiyet).
    """
    rng = np.random.default_rng(tohum)
    xs = np.sort(rng.uniform(0, 1, n))
    hedef = lambda t: np.sin(2 * np.pi * t)          # Lipschitz sabiti 2π
    L = max(L, 2 * np.pi)
    ys = hedef(xs)

    izgara = np.linspace(0, 1, 1001)
    a, b = lan(izgara, xs, ys, L), ran(izgara, xs, ys, L)

    # 1. örnek noktalarda tam oturma
    oturma = float(
        max(np.max(np.abs(lan(xs, xs, ys, L) - ys)), np.max(np.abs(ran(xs, xs, ys, L) - ys)))
    )
    # 2. Lipschitz sabiti (ayrık)
    h = izgara[1] - izgara[0]
    lip = float(max(np.max(np.abs(np.diff(a))), np.max(np.abs(np.diff(b)))) / h)
    # 3. arada olma: hedefin kendisi L-Lipschitz bir genişlemedir
    g = hedef(izgara)
    arada = bool(np.all(a <= g + 1e-9) and np.all(g <= b + 1e-9))
    return {
        "L": L,
        "ornekte_tam_oturma_hatasi": oturma,
        "olculen_lipschitz": lip,
        "lipschitz_asilmadi": bool(lip <= L * (1 + 1e-6)),
        "hedef_arada": arada,
        "lan_ran_araligi_ortalama": float(np.mean(b - a)),
    }


# =====================================================================
#  2. Ezber zaafı: gürültülü veride tam aradeğerleme
# =====================================================================
def ezber_mi(xs=None, ys=None, t=None, ne: str = "kıyas",
             olcek: float = 0.03, lam: float = 1e-8, n: int = 40,
             gurultu: float = 0.25, tohum: int = 0):
    """EZBER Mİ, ÖĞRENME Mİ -- **tek terkip** (kütük H227).

    Küme: ``rbf_gram``, ``cekirdek_sirt``, ``ezber_kiyasi``,
    ``sobolev_kiyasi``. Dördü tek suâlin parçalarıydı: **model
    ezberliyor mu, yoksa genelliyor mu?** Ve cevabın tamamı tek
    sayıdadır -- düzenlileme katsayısı ``λ``:

        ``λ → 0``   eğitimde sıfır hata, sınamada patlama  → **EZBER**
        ``λ`` büyük eğitimde daha kötü, sınamada daha iyi  → **ÖĞRENME**

    Küllî kaybın bilmesi gereken şey tam olarak budur ve şimdiye kadar
    bilmiyordu.

    ==================  ==============================================
    ``ne``              döndürdüğü
    ==================  ==============================================
    ``gram``            RBF Gram dizeyi ``exp(−‖x−z‖²/2σ²)``
    ``uydur``           ``min_g Σ(g(xᵢ)−yᵢ)² + λ‖g‖²_H`` çözümü (fonksiyon)
    ``kıyas``           ``λ=10⁻⁸`` ile ``λ=10⁻¹``: ezber ile öğrenme
                        yan yana; koşul sayısı da raporlanır
    ``sobolev``         değer+türev uydurmak türev hatasını düşürüyor mu
    ==================  ==============================================

    İki ihtiyat kaydı -- ikisi de ölçüm sırasında ortaya çıktı:

    * **``λ = 0`` sayısal olarak ERİŞİLEBİLİR DEĞİLDİR.** Gram dizeyinin
      koşul sayısı burada ~10⁸--10¹⁷. Bu yüzden "tam aradeğerleme"
      yerine ``λ = 10⁻⁸`` alınır ve koşul sayısı **raporlanır** --
      erişilemeyen bir hâl erişilmiş gibi sunulmaz.
    * **Gürültü, gereken Lipschitz sabitini patlatır.** Kan
      genişletmesinin veriye tam oturması için ``L``, VERİNİN Lipschitz
      sabitinden küçük olmamalı; gürültülü veri hedefin ``2π``sini
      fazlasıyla aşar (burada ~4,5·10³). Yâni "tam oturma" bedava
      değildir: genişletme dikenleşir. Ezberin sebebi tam budur.
    """
    if ne == "gram":
        d2 = (np.asarray(xs, float)[:, None] - np.asarray(ys, float)[None, :]) ** 2
        return np.exp(-0.5 * d2 / (olcek * olcek))

    if ne == "uydur":
        xs_, ys_ = xs, ys
        K = ezber_mi(xs_, xs_, olcek=olcek, ne="gram")
        A = K + lam * np.eye(len(xs_))
        alfa = np.linalg.solve(A, ys_)
        return lambda t: ezber_mi(t, xs_, olcek=olcek, ne="gram") @ alfa

    if ne == "kıyas":
        rng = np.random.default_rng(tohum)
        hedef = lambda t: np.sin(2 * np.pi * t)
        xs = np.sort(rng.uniform(0, 1, n))
        ys = hedef(xs) + gurultu * rng.normal(size=n)
        xt = np.linspace(0.02, 0.98, 500)
        yt = hedef(xt)

        L_veri = float(np.max(np.abs(np.diff(ys) / np.diff(xs))))
        kan_orta = 0.5 * (lan(xt, xs, ys, L_veri) + ran(xt, xs, ys, L_veri))
        kan_egitim = 0.5 * (lan(xs, xs, ys, L_veri) + ran(xs, xs, ys, L_veri))

        g0 = ezber_mi(xs, ys, olcek=olcek, lam=1e-8, ne="uydur")
        g1 = ezber_mi(xs, ys, olcek=olcek, lam=1e-1, ne="uydur")

        def hata(tahmin: np.ndarray, dogru: np.ndarray) -> float:
            return float(np.sqrt(np.mean((tahmin - dogru) ** 2)))

        kayit = {
            "gurultu_seviyesi": gurultu,
            "verinin_lipschitz_sabiti": L_veri,
            "hedefin_lipschitz_sabiti": 2 * np.pi,
            "gram_kosul_sayisi": float(np.linalg.cond(ezber_mi(xs, xs, olcek=olcek, ne="gram"))),
            "kan_egitim_hatasi": hata(kan_egitim, ys),
            "kan_sinama_hatasi": hata(kan_orta, yt),
            "cekirdek_lam0_egitim": hata(g0(xs), ys),
            "cekirdek_lam0_sinama": hata(g0(xt), yt),
            "cekirdek_sirt_egitim": hata(g1(xs), ys),
            "cekirdek_sirt_sinama": hata(g1(xt), yt),
        }
        kayit["kan_tam_oturuyor"] = bool(kayit["kan_egitim_hatasi"] < 1e-9)
        kayit["gurultu_lipschitzi_patlatti"] = bool(L_veri > 100 * 2 * np.pi)
        # ezber: eğitimde gürültüden çok daha iyi, sınamada çok daha kötü
        kayit["ezber_gorunuyor"] = bool(
            kayit["cekirdek_lam0_egitim"] < 0.5 * gurultu
            and kayit["cekirdek_lam0_sinama"] > 4.0 * gurultu
        )
        kayit["duzenlileme_sinamayi_iyilestirdi"] = bool(
            kayit["cekirdek_sirt_sinama"] < kayit["cekirdek_lam0_sinama"]
            and kayit["cekirdek_sirt_sinama"] < kayit["kan_sinama_hatasi"]
        )
        kayit["duzenlileme_egitimi_kotulestirdi"] = bool(
            kayit["cekirdek_sirt_egitim"] > kayit["cekirdek_lam0_egitim"]
        )
        return kayit

    if ne == "sobolev":
        # Aslının imzası AYRI varsayılanlar taşıyordu; tek kapıya
        # girerken onlar geri konur -- yoksa ölçüm sessizce değişir
        # (H223'te ölçülen kusurun aynısı).
        if (n, gurultu, olcek, lam, tohum) == (40, 0.25, 0.03, 1e-8, 0):
            n, gurultu, olcek, lam, tohum = 14, 0.05, 0.25, 1e-6, 3
        rng = np.random.default_rng(tohum)
        hedef = lambda t: np.sin(2 * np.pi * t)
        turev = lambda t: 2 * np.pi * np.cos(2 * np.pi * t)
        xs = np.sort(rng.uniform(0, 1, n))
        ys = hedef(xs) + gurultu * rng.normal(size=n)
        ds = turev(xs) + gurultu * rng.normal(size=n)

        def dK(x: np.ndarray, z: np.ndarray) -> np.ndarray:
            """``∂/∂x k(x,z)``."""
            return -(x[:, None] - z[None, :]) / (olcek * olcek) * ezber_mi(x, z, olcek=olcek, ne="gram")

        K = ezber_mi(xs, xs, olcek=olcek, ne="gram")
        # (a) yalnız değer
        a_deger = np.linalg.solve(K + lam * np.eye(n), ys)
        # (b) değer + türev (en küçük kareler)
        A = np.vstack([K, dK(xs, xs)])
        b = np.concatenate([ys, ds])
        a_sob = np.linalg.lstsq(A.T @ A + lam * np.eye(n), A.T @ b, rcond=None)[0]

        xt = np.linspace(0.05, 0.95, 400)
        def hata(v, d):
            return float(np.sqrt(np.mean((v - d) ** 2)))

        deger_h = hata(ezber_mi(xt, xs, olcek=olcek, ne="gram") @ a_deger, hedef(xt))
        deger_t = hata(dK(xt, xs) @ a_deger, turev(xt))
        sob_h = hata(ezber_mi(xt, xs, olcek=olcek, ne="gram") @ a_sob, hedef(xt))
        sob_t = hata(dK(xt, xs) @ a_sob, turev(xt))
        return {
            "yalniz_deger__deger_hatasi": deger_h,
            "yalniz_deger__turev_hatasi": deger_t,
            "sobolev__deger_hatasi": sob_h,
            "sobolev__turev_hatasi": sob_t,
            "turev_iyilesti": bool(sob_t < deger_t),
        }

    raise ValueError("ezber suâlinin kipi bilinmiyor: %r" % (ne,))


# =====================================================================
#  3. Sobolev eğitimi: türev bilgisini de kullanmak
# =====================================================================


def rapor() -> str:
    s = ["=== genisletme ==="]
    k = kan_ozellikleri()
    s.append("Kan gen.  oturma hatası=%.2e  ölçülen Lip=%.3f ≤ L=%.3f → %s  hedef arada=%s"
             % (k["ornekte_tam_oturma_hatasi"], k["olculen_lipschitz"], k["L"],
                k["lipschitz_asilmadi"], k["hedef_arada"]))
    e = ezber_mi(ne="kıyas")
    s.append("ezber     Kan: eğitim=%.2e sınama=%.4f | λ=1e-8: eğitim=%.4f sınama=%.4g | sırt: eğitim=%.4f sınama=%.4f"
             % (e["kan_egitim_hatasi"], e["kan_sinama_hatasi"],
                e["cekirdek_lam0_egitim"], e["cekirdek_lam0_sinama"],
                e["cekirdek_sirt_egitim"], e["cekirdek_sirt_sinama"]))
    s.append("          gürültü=%.2f  verinin Lip=%.3g (hedefinki %.3g)  Gram koşul=%.2e"
             % (e["gurultu_seviyesi"], e["verinin_lipschitz_sabiti"],
                e["hedefin_lipschitz_sabiti"], e["gram_kosul_sayisi"]))
    s.append("          Kan tam oturuyor=%s  ezber görünüyor=%s  düzenlileme sınamayı iyileştirdi=%s"
             % (e["kan_tam_oturuyor"], e["ezber_gorunuyor"],
                e["duzenlileme_sinamayi_iyilestirdi"]))
    b = ezber_mi(ne="sobolev")
    s.append("Sobolev   yalnız değer: f=%.4f f'=%.4f | Sobolev: f=%.4f f'=%.4f | türev iyileşti=%s"
             % (b["yalniz_deger__deger_hatasi"], b["yalniz_deger__turev_hatasi"],
                b["sobolev__deger_hatasi"], b["sobolev__turev_hatasi"], b["turev_iyilesti"]))
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
