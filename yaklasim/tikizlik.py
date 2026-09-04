"""
Varlık: tıkızlık, zorlayıcılık ve tıkızlaştırmanın sınırı.

Eniyilemede iki ayrı soru vardır ve karıştırılmaları en pahalı hatadır:

  * **Var mı?** -- asgarînin varlığı bir TOPOLOJİ meselesidir. Weierstrass:
    tıkız bir kümede sürekli fonksiyon asgarîsine ulaşır. Tıkız olmayan
    uzayda ise infimum var olsa bile ULAŞILMAYABİLİR.
  * **Bulunur mu?** -- bu ayrı bir mesele (bkz. ``kara_kutu``).

``ℝⁿ`` tıkız değildir; kurtarıcı kavram **zorlayıcılıktır** (coercivity):
``‖x‖ → ∞`` iken ``f(x) → ∞`` ise, alt seviye kümeleri ``{f ≤ c}``
kapalı ve SINIRLIDIR, yani tıkızdır; asgarî oradadır. Zorlayıcılık bir
"iyi davranış temennisi" değil, tıkızlığın yerine geçen KESİN şarttır.

Tıkızlaştırma (bir noktada ``+∞`` ekleyerek) her zaman kurtarmaz: bu
dosya, tıkızlaştırmanın **sürekli genişlemeye** izin vermediği iki
klasik karşı örneği sayısal olarak gösterir.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import numpy as np


# =====================================================================
#  1. Zorlayıcılık ⟹ asgarî var
# =====================================================================
def asgari_var_mi(f=None, boyut: int = 2, ne: str = "hüküm",
                  c: float = 0.0,
                  yaricaplar=(1.0, 10.0, 100.0, 1000.0),
                  yon_sayisi: int = 200, azami_yaricap: float = 1e4,
                  ornek: int = 5000, adim: int = 30,
                  yaklasim_sayisi: int = 40, tohum: int = 0):
    """ASGARÎ VAR MI -- **tek terkip** (kütük H227).

    Küme: ``zorlayici_mi``, ``alt_seviye_sinirli_mi``,
    ``ulasilmayan_infimum``, ``sin_bir_bolu_x``, ``yon_bagimli_limit``.
    Beş isim **tek teoremin hipotezleri ve nakızlarıydı** -- Weierstrass:

        ``f`` sürekli **ve** alt seviye kümesi tıkız  ⇒  asgarî **vardır**

    Ve her hipotezin şart olduğu birer karşı örnekle mühürlenir:

    ==================  ==============================================
    ``ne``              ne ölçer / neyi düşürür
    ==================  ==============================================
    ``zorlayıcı``       küre üstündeki asgarî yarıçapla artıyor mu
    ``seviye``          ``{f ≤ c}`` sınırlı görünüyor mu
    ``hüküm``           ikisi birden -- asgarînin **varlık delili**
    ``kaçış``           ``e^{−x}``: inf var, asgarî YOK (zorlayıcı değil)
    ``süreksiz``        ``sin(1/x)``: limit yok (sürekli değil)
    ``yönlü``           ``(x²−y²)/(x²+y²)``: limit yöne bağlı
    ==================  ==============================================

    **Bu bir ispat değil delildir** ve sınırı açıkça yazılıdır: yön
    sayısı sonludur, dolayısıyla dar bir "kaçış koridoru" gözden
    kaçabilir. Bu tuzağa yazarken bizzat düşüldü -- yalnız rastgele
    yönlerle ``f(x) = Σ_{i≥1} xᵢ²`` (``x₀`` ekseni boyunca sabit sıfır)
    ZORLAYICI göründü, çünkü rastgele bir yön eksene tam oturmaz. Bu
    yüzden **koordinat eksenleri her zaman yön kümesine katılır**;
    kaçış koridorları çoğu zaman eksenlerdedir.

    Eniyilemenin ``kaçış`` hâlindeki başarısızlığı **usulün kusuru
    değildir**: çözüm kümesi boştur. Hoca suçlu değil, suâl yanlıştır.
    """
    if ne == "zorlayıcı":
        rng = np.random.default_rng(tohum)
        eksenler = np.concatenate([np.eye(boyut), -np.eye(boyut)], axis=0)
        yonler = rng.normal(size=(yon_sayisi, boyut))
        yonler /= np.linalg.norm(yonler, axis=1, keepdims=True)
        yonler = np.concatenate([eksenler, yonler], axis=0)
        asgariler = []
        for R in yaricaplar:
            degerler = [f(R * u) for u in yonler]
            asgariler.append(float(min(degerler)))
        artiyor = all(asgariler[i] < asgariler[i + 1] for i in range(len(asgariler) - 1))
        return {
            "yaricaplar": list(yaricaplar),
            "kure_asgarileri": asgariler,
            "delil_artiyor": artiyor,
            "kayit": "sonlu yön örneklemesi; ispat değil delil",
        }

    if ne == "seviye":
        rng = np.random.default_rng(tohum)
        # logaritmik yarıçap taraması: uzakta hâlâ c'nin altına inen var mı?
        R = np.exp(rng.uniform(np.log(1e-2), np.log(azami_yaricap), size=ornek))
        U = rng.normal(size=(ornek, boyut))
        U /= np.linalg.norm(U, axis=1, keepdims=True)
        eksenler = np.concatenate([np.eye(boyut), -np.eye(boyut)], axis=0)
        U[: len(eksenler)] = eksenler
        R[: len(eksenler)] = azami_yaricap
        X = R[:, None] * U
        icinde = np.array([f(x) <= c for x in X])
        if not icinde.any():
            return {"c": c, "nokta_yok": True, "azami_norm": 0.0, "sinirli_gorunuyor": True}
        azami = float(np.max(np.linalg.norm(X[icinde], axis=1)))
        return {
            "c": c,
            "nokta_yok": False,
            "azami_norm": azami,
            "sinirli_gorunuyor": bool(azami < azami_yaricap * 0.5),
        }

    if ne == "hüküm":
        z = asgari_var_mi(f, boyut, "zorlayıcı", yaricaplar=yaricaplar,
                          yon_sayisi=yon_sayisi, tohum=tohum)
        s_ = asgari_var_mi(f, boyut, "seviye", c=c,
                           azami_yaricap=azami_yaricap, ornek=ornek,
                           tohum=tohum)
        return {"zorlayıcı": z, "seviye": s_,
                "asgarî_var_delili": bool(z["delil_artiyor"]
                                          and s_["sinirli_gorunuyor"]),
                "kayıt": "Weierstrass şartının sayısal delili; ispat değil"}

    if ne == "kaçış":
        x = 0.0
        yol = []
        for _ in range(adim):
            # f' = -e^{-x};  büyük adım ölçekli iniş
            x = x - 10.0 * (-np.exp(-x))
            yol.append((x, float(np.exp(-x))))
        return {
            "son_x": yol[-1][0],
            "son_f": yol[-1][1],
            "infimum": 0.0,
            "kaciyor": yol[-1][0] > yol[0][0] * 10 or yol[-1][0] > 10.0,
            "asgari_ulasilmadi": yol[-1][1] > 0.0,
        }

    if ne == "süreksiz":
        k = np.arange(1, yaklasim_sayisi + 1)
        x_arti = 1.0 / (2 * np.pi * k + np.pi / 2)     # sin(1/x) = +1
        x_eksi = 1.0 / (2 * np.pi * k - np.pi / 2)     # sin(1/x) = -1
        f_arti = np.sin(1.0 / x_arti)
        f_eksi = np.sin(1.0 / x_eksi)
        return {
            "x_arti_son": float(x_arti[-1]),
            "x_eksi_son": float(x_eksi[-1]),
            "limit_arti": float(np.max(np.abs(f_arti - 1.0))),
            "limit_eksi": float(np.max(np.abs(f_eksi + 1.0))),
            "iki_dizi_de_sifira_gidiyor": bool(x_arti[-1] < 1e-2 and x_eksi[-1] < 1e-2),
            "limitler_ayrisiyor": bool(
                np.allclose(f_arti, 1.0, atol=1e-12) and np.allclose(f_eksi, -1.0, atol=1e-12)
            ),
        }

    if ne == "yönlü":
        yaklasim_sayisi = min(yaklasim_sayisi, 12)
        r = 10.0 ** (-np.arange(1, yaklasim_sayisi + 1, dtype=float))
        aciler = [0.0, np.pi / 4, np.pi / 2, np.pi / 3]
        izler = {}
        for th in aciler:
            x, y = r * np.cos(th), r * np.sin(th)
            izler[round(th, 6)] = float(((x * x - y * y) / (x * x + y * y))[-1])
        degerler = list(izler.values())
        return {
            "yarıcap_son": float(r[-1]),
            "yone_gore_limitler": izler,
            "cos2theta_ile_uyusuyor": all(
                abs(izler[round(th, 6)] - np.cos(2 * th)) < 1e-12 for th in aciler
            ),
            "limit_yok": bool(max(degerler) - min(degerler) > 0.5),
        }

    raise ValueError("asgarî suâlinin kipi bilinmiyor: %r" % (ne,))


# =====================================================================
#  4. Örnek hedefler
# =====================================================================
def kare(x: np.ndarray) -> float:
    return float(np.sum(x * x))


def rosenbrock(x: np.ndarray) -> float:
    return float(np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2))


def zorlayici_olmayan(x: np.ndarray) -> float:
    """``x₀`` ekseni boyunca sabit: alt seviye kümesi sınırsız."""
    return float(np.sum(x[1:] ** 2))


def rapor() -> str:
    s = ["=== tikizlik ==="]
    z = asgari_var_mi(kare, 3, ne="zorlayıcı")
    s.append("zorlayıcı(‖x‖²)  küre asgarileri=%s  artıyor=%s"
             % ([round(v, 3) for v in z["kure_asgarileri"]], z["delil_artiyor"]))
    zn = asgari_var_mi(zorlayici_olmayan, 3, ne="zorlayıcı")
    s.append("zorlayıcı değil    küre asgarileri=%s  artıyor=%s"
             % ([round(v, 6) for v in zn["kure_asgarileri"]], zn["delil_artiyor"]))
    a = asgari_var_mi(kare, 3, c=4.0, ne="seviye")
    b = asgari_var_mi(zorlayici_olmayan, 3, c=4.0, ne="seviye")
    s.append("alt seviye {f≤4}  ‖x‖²: azami norm=%.3g sınırlı=%s   |   sınırsız hâl: azami norm=%.3g sınırlı=%s"
             % (a["azami_norm"], a["sinirli_gorunuyor"], b["azami_norm"], b["sinirli_gorunuyor"]))
    u = asgari_var_mi(ne="kaçış")
    s.append("ulaşılmayan inf   son f=%.3g > inf=0 → %s (x kaçıyor=%s)"
             % (u["son_f"], u["asgari_ulasilmadi"], u["kaciyor"]))
    p = asgari_var_mi(ne="süreksiz")
    s.append("sin(1/x)          iki dizi 0'a gidiyor=%s, limitler ±1'e ayrışıyor=%s"
             % (p["iki_dizi_de_sifira_gidiyor"], p["limitler_ayrisiyor"]))
    q = asgari_var_mi(ne="yönlü")
    s.append("(x²−y²)/(x²+y²)   cos2θ ile uyuşuyor=%s, limit yok=%s"
             % (q["cos2theta_ile_uyusuyor"], q["limit_yok"]))
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
